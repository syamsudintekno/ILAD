"""Exercise the Render API with Auth and Firestore emulators."""

import os
from unittest.mock import patch
from uuid import uuid4

import httpx

from firebase.emulator_smoke import AUTH_HOST, PROJECT, _account, _csv
from firebase.pilot import create_firebase_app
from firebase.run_store import FirestoreRunStore


def check() -> None:
    """Verify upload, restart recovery, exports, and server-only storage."""
    os.environ["ILAD_FIREBASE_PROJECT"] = PROJECT
    os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = AUTH_HOST
    os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"
    os.environ["ILAD_ALLOWED_ORIGINS"] = "http://localhost:5173"

    from render_api import app
    from google.cloud import firestore

    owner = {"Authorization": f"Bearer {_account('admin_qa')}"}
    other = {"Authorization": f"Bearer {_account('admin_qa')}"}
    client = app.test_client()
    assert client.get("/health").status_code == 200
    with patch("firebase.run_store.RESULT_CHUNK_BYTES", 128):
        response = client.post("/v1/runs", data=_csv(), headers={
            **owner, "Content-Type": "text/csv", "Idempotency-Key": uuid4().hex,
        })
    assert response.status_code == 201, response.json
    result = response.json
    route = f"/v1/runs/{result['run_id']}"
    assert result["csv_export_available"]

    database = firestore.Client(project=PROJECT)
    recovered = FirestoreRunStore(database, bucket=None, analytics_version="restarted")
    client = create_firebase_app(recovered, os.environ["ILAD_ALLOWED_ORIGINS"]).test_client()
    assert client.get(route, headers=owner).json == result
    assert "Dosen Sintetis" in client.get(f"{route}/exports/csv", headers=owner).text
    assert client.get(f"{route}/exports/json", headers=owner).json == result["overview"]["kpis"]
    for suffix in ("", "/exports/csv", "/exports/json"):
        assert client.get(route + suffix, headers=other).status_code == 404
        assert client.get(route + suffix).status_code == 401

    run = database.collection("ilad_runs").document(result["run_id"]).get().to_dict()
    assert run["result_chunk_count"] > 1 and "result_object" not in run
    base = f"http://127.0.0.1:8080/v1/projects/{PROJECT}/databases/(default)/documents"
    url = f"{base}/ilad_runs/{result['run_id']}/result_{run['attempt']}/000"
    assert httpx.get(url, headers=owner).status_code in (401, 403)
    assert httpx.get(url).status_code in (401, 403)
    print("Render API Firestore checks passed.")


if __name__ == "__main__":
    check()
