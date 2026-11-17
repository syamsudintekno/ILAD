"""Firebase HTTPS entry point for the ILAD pilot API."""

import os
from functools import lru_cache

import firebase_admin
from firebase_admin import auth
from firebase_functions import https_fn
from firebase_functions.options import MemoryOption
from flask.ctx import RequestContext
from flask_cors import CORS
from google.cloud import firestore, storage

from pilot import create_app
from run_store import FirestoreRunStore

firebase_app = firebase_admin.initialize_app()


def verify_token(token: str) -> dict | None:
    """Accept current Firebase ID tokens issued for this project."""
    try:
        return auth.verify_id_token(token, check_revoked=True)
    except (auth.InvalidIdTokenError, auth.ExpiredIdTokenError, auth.RevokedIdTokenError,
            auth.UserDisabledError, auth.UserNotFoundError, ValueError):
        return None


@lru_cache(maxsize=1)
def pilot_app():
    """Configure the private storage and allowed frontend origins."""
    project = firebase_app.project_id
    store = FirestoreRunStore(
        firestore.Client(project=project),
        storage.Client(project=project).bucket(os.environ["ILAD_STORAGE_BUCKET"]),
        os.environ["ILAD_ANALYTICS_VERSION"],
    )
    app = create_app(store, verify_token)
    origins = os.environ.get("ILAD_ALLOWED_ORIGINS", "").split(",")
    CORS(
        app,
        resources={r"/v1/runs.*": {"origins": [origin.strip() for origin in origins if origin.strip()]}},
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    )
    return app


@https_fn.on_request(timeout_sec=120, memory=MemoryOption.MB_512, invoker="public")
def ilad_api(request: https_fn.Request) -> https_fn.Response:
    """Dispatch HTTP requests after the hosting platform resolves the function."""
    app = pilot_app()
    # Share the request body cache with Functions Framework's response hook.
    with RequestContext(app, request.environ, request=request):
        return app.full_dispatch_request()
