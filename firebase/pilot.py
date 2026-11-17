"""HTTP routes for authenticated ILAD pilot runs."""

from hashlib import sha256
import json
import re

from firebase_admin import auth
from flask import Flask, Response, g, jsonify, request
from flask_cors import CORS
from pandas.errors import ParserError

from application.controller import DatasetValidationError
from application.web_overview import build_web_overview
from config.schema import REQUIRED_COLUMNS
from core.loader import EmptyCsvFileError

MAX_UPLOAD_BYTES = 2 * 1024 * 1024
KEY_PATTERN = re.compile(r"[a-zA-Z0-9_-]{1,128}")
RUN_PATTERN = re.compile(r"[a-f0-9]{64}")
RESULT_STATUS = {"succeeded": 200, "processing": 202, "invalid": 422, "failed": 500}


def create_firebase_app(store, allowed_origins: str):
    """Use Firebase ID tokens and configured frontend origins."""
    def verify_token(token: str) -> dict | None:
        try:
            return auth.verify_id_token(token, check_revoked=True)
        except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, auth.RevokedIdTokenError,
                auth.UserDisabledError, auth.UserNotFoundError, ValueError):
            return None

    app = create_app(store, verify_token)
    CORS(
        app,
        resources={r"/v1/runs.*": {"origins": [
            origin.strip() for origin in allowed_origins.split(",") if origin.strip()
        ]}},
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    )
    return app


def _reply(body, status):
    response = jsonify(body)
    response.status_code = status
    response.headers["Cache-Control"] = "no-store"
    return response


def _error(code, message, status):
    return _reply({"error": {"code": code, "message": message}}, status)


def _validation(error):
    if isinstance(error, DatasetValidationError):
        findings = dict(error.validation_result.errors)
        if "missing_values" in findings:
            findings["missing_values"] = {
                column: count
                for column, count in findings["missing_values"].items()
                if column in REQUIRED_COLUMNS
            }
        return {
            "error": {"code": "invalid_csv", "message": "Data CSV gagal divalidasi."},
            "validation": {"findings": findings, "summary": error.validation_result.summary},
        }
    return {
        "error": {"code": "unreadable_csv", "message": "CSV kosong atau tidak dapat dibaca."},
        "validation": {"findings": {}, "summary": {}},
    }


def create_app(store, verify_token):
    """Create pilot HTTP routes with injectable storage and token verification."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

    @app.errorhandler(413)
    def too_large(_error_instance):
        return _error("upload_too_large", "Ukuran CSV melebihi batas.", 413)

    @app.before_request
    def authorize():
        if request.method == "OPTIONS" or request.endpoint == "health":
            return None
        scheme, _, token = request.headers.get("Authorization", "").partition(" ")
        try:
            claims = verify_token(token) if scheme.lower() == "bearer" and token else None
        except Exception:
            return _error("authentication_unavailable", "Autentikasi belum tersedia.", 500)
        if not claims or not claims.get("uid"):
            return _error("unauthenticated", "Silakan masuk kembali.", 401)
        if claims.get("ilad_role") != "admin_qa":
            return _error("forbidden", "Akun tidak memiliki akses pilot.", 403)
        g.owner = claims["uid"]

    @app.get("/health")
    def health():
        return _reply({"status": "ok"}, 200)

    @app.get("/v1/runs/<run_id>")
    def get_run(run_id):
        if not RUN_PATTERN.fullmatch(run_id):
            return _error("not_found", "Run tidak tersedia.", 404)
        try:
            run = store.get(run_id, g.owner)
        except Exception:
            return _error("processing_failed", "Run belum dapat dibaca.", 500)
        if run is None:
            return _error("not_found", "Run tidak tersedia.", 404)
        return _reply(run, 200)

    @app.get("/v1/runs/<run_id>/exports/<file_format>")
    def export_run(run_id, file_format):
        if not RUN_PATTERN.fullmatch(run_id) or file_format not in {"csv", "json"}:
            return _error("not_found", "Ekspor tidak tersedia.", 404)
        try:
            run = store.get(run_id, g.owner, include_csv=file_format == "csv")
        except Exception:
            return _error("processing_failed", "Ekspor belum dapat dibaca.", 500)
        if run is None or run["status"] != "succeeded":
            return _error("not_found", "Ekspor tidak tersedia.", 404)
        if file_format == "csv":
            csv = run.get("analytics_csv")
            if csv is None:
                return _error("not_found", "Proses ulang CSV untuk menyiapkan ekspor run ini.", 404)
            filename, content_type, content = "ilad_analytics.csv", "text/csv; charset=utf-8", csv
        else:
            filename = "ilad_kpi_summary.json"
            content_type = "application/json"
            content = json.dumps(run["overview"]["kpis"], indent=2)
        return Response(content, content_type=content_type, headers={
            "Cache-Control": "no-store",
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Content-Type-Options": "nosniff",
        })

    @app.post("/v1/runs")
    def create_run():
        key = request.headers.get("Idempotency-Key", "")
        if not KEY_PATTERN.fullmatch(key):
            return _error("invalid_key", "Idempotency-Key tidak valid.", 400)
        if request.mimetype != "text/csv":
            return _error("unsupported_type", "Unggah berkas CSV.", 415)
        content = request.get_data()
        run_id = sha256(f"{g.owner}\0{key}".encode()).hexdigest()
        digest = sha256(content).hexdigest()
        try:
            run, attempt = store.claim(run_id, g.owner, digest)
            if run is None:
                return _error("key_conflict", "Key sudah dipakai untuk CSV berbeda.", 409)
            if attempt is None:
                return _reply(run, RESULT_STATUS[run["status"]])
            return _process_run(store, run_id, attempt, content)
        except Exception:
            return _error("processing_failed", "Pemrosesan belum dapat diselesaikan.", 500)

    return app


def _process_run(store, run_id, attempt, content):
    try:
        payload = build_web_overview(content)
    except (EmptyCsvFileError, ParserError, DatasetValidationError) as error:
        return _reply(store.finish(run_id, attempt, "invalid", _validation(error)), 422)
    except Exception:
        failure = {"error": {"code": "processing_failed", "message": "Pemrosesan gagal."}}
        return _reply(store.finish(run_id, attempt, "failed", failure), 500)
    return _reply(store.finish(run_id, attempt, "succeeded", payload), 201)
