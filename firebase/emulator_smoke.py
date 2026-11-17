"""Run the ILAD HTTP and rules smoke tests against the demo-only Firebase emulators."""

import csv
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
import os
from urllib.parse import quote
from uuid import uuid4

import firebase_admin
from firebase_admin import auth
from google.cloud import firestore
import httpx

PROJECT = "demo-ilad"
AUTH_HOST = "127.0.0.1:9099"
API = f"http://127.0.0.1:5001/{PROJECT}/us-central1/ilad_api/v1/runs"
BUCKET = f"{PROJECT}.appspot.com"


def _account(role: str | None) -> str:
    credentials = {
        "email": f"{uuid4().hex}@example.test",
        "password": uuid4().hex,
        "returnSecureToken": True,
    }
    url = f"http://{AUTH_HOST}/identitytoolkit.googleapis.com/v1/accounts"
    signup = httpx.post(f"{url}:signUp?key=demo", json=credentials).raise_for_status().json()
    if role:
        auth.set_custom_user_claims(signup["localId"], {"ilad_role": role})
    session = httpx.post(
        f"{url}:signInWithPassword?key=demo", json=credentials
    ).raise_for_status().json()
    return session["idToken"]


def _csv() -> bytes:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["lecturer_name", "study_program", "faculty", *[f"P{i}" for i in range(1, 21)]])
    writer.writerow(["Dosen Sintetis", "Prodi Sintetis", "Fakultas Sintetis", *([5] * 20)])
    return buffer.getvalue().encode()


def _check() -> None:
    os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = AUTH_HOST
    os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"
    firebase_admin.initialize_app(options={"projectId": PROJECT})
    owner, other = (_account("admin_qa") for _ in range(2))
    user = _account(None)

    def bearer(token):
        return {"Authorization": f"Bearer {token}"}

    def upload(key, content):
        return httpx.post(
            API,
            content=content,
            headers=bearer(owner) | {"Content-Type": "text/csv", "Idempotency-Key": key},
            timeout=60,
        )

    assert httpx.get(f"{API}/{'0' * 64}").status_code == 401
    assert httpx.get(f"{API}/{'0' * 64}", headers=bearer(user)).status_code == 403
    assert httpx.get(f"{API}/{'0' * 64}", headers=bearer("invalid-token")).status_code == 401
    for origin, allowed in (("http://localhost:5173", True), ("https://other.example.test", False)):
        preflight = httpx.options(
            API,
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization, content-type, idempotency-key",
            },
        )
        assert (preflight.headers.get("Access-Control-Allow-Origin") == origin) is allowed
    body = _csv()
    key = uuid4().hex
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: upload(key, body), range(2)))
    status_codes = sorted(response.status_code for response in responses)
    assert status_codes in ([200, 201], [201, 202]), [(r.status_code, r.text) for r in responses]
    result = next(response.json() for response in responses if response.status_code == 201)
    run_id = result["run_id"]
    assert result["cohort_size"] == 1
    assert result["lecturer_profiles"][0]["lecturer_name"] == "Dosen Sintetis"
    assert result["overview"]["top_lecturers"][0]["rpi"] == 50.0
    assert upload(key, body).json() == result
    assert upload(key, b"changed").status_code == 409
    invalid = upload(uuid4().hex, b"lecturer_name\nDosen Sintetis\n")
    assert invalid.status_code == 422 and "validation" in invalid.json()

    assert httpx.get(f"{API}/{run_id}", headers=bearer(owner)).json() == result
    assert httpx.get(f"{API}/{run_id}", headers=bearer(other)).status_code == 404

    document = f"projects/{PROJECT}/databases/(default)/documents/ilad_runs/{run_id}"
    firestore_url = f"http://127.0.0.1:8080/v1/{document}"
    metadata = firestore.Client(project=PROJECT).collection("ilad_runs").document(run_id).get().to_dict()
    storage_url = f"http://127.0.0.1:9199/v0/b/{BUCKET}/o/{quote(metadata['result_object'], safe='')}"
    for headers in ({}, bearer(owner)):
        assert httpx.get(firestore_url, headers=headers).status_code in (401, 403)
        assert httpx.get(storage_url, headers=headers).status_code in (401, 403)
    print("Firebase emulator smoke test passed.")


if __name__ == "__main__":
    _check()
