"""Check routing independently of the Firebase Emulator Suite."""

from unittest.mock import Mock

import pytest

from firebase.pilot import MAX_UPLOAD_BYTES, create_app

AUTH = {"Authorization": "Bearer admin"}
UPLOAD = AUTH | {"Idempotency-Key": "first-upload", "Content-Type": "text/csv"}
RUN_ID = "a" * 64


@pytest.fixture
def api():
    """Provide the HTTP client and a mock run store."""
    store = Mock()
    claims = {
        "admin": {"uid": "qa", "ilad_role": "admin_qa"},
        "viewer": {"uid": "viewer"},
    }
    return create_app(store, claims.get).test_client(), store


@pytest.mark.parametrize(
    ("headers", "status"),
    [({}, 401), ({"Authorization": "Bearer expired"}, 401),
     ({"Authorization": "Bearer viewer"}, 403)],
)
def test_access_is_checked_before_storage(api, headers, status):
    """Reject unauthorized requests before looking up any run."""
    client, store = api
    assert client.get(f"/v1/runs/{RUN_ID}", headers=headers).status_code == status
    assert not store.mock_calls


def test_lookup_uses_verified_owner(api):
    """Pass the verified uid, even if the caller supplies another owner."""
    client, store = api
    store.get.return_value = None
    response = client.get(f"/v1/runs/{RUN_ID}?owner=other", headers=AUTH)
    assert response.status_code == 404
    assert response.headers["Cache-Control"] == "no-store"
    store.get.assert_called_once_with(RUN_ID, "qa")


def test_invalid_csv_omits_unrecognized_headers_from_findings(api):
    """Expose only canonical names and aggregate findings in validation responses."""
    client, store = api
    store.claim.return_value = {"status": "processing"}, "attempt"
    store.finish.side_effect = lambda _run, _attempt, _status, details: details
    response = client.post(
        "/v1/runs", headers=UPLOAD, data=b"lecturer_name,Private value\nDosen sintetis,\n",
    )
    assert response.status_code == 422
    assert response.json["validation"]["summary"]["missing_value_count"] == 1
    assert b"Private value" not in response.data
    assert b"Dosen sintetis" not in response.data


@pytest.mark.parametrize(
    ("headers", "data", "status"),
    [(AUTH, b"x", 400), (UPLOAD | {"Content-Type": "text/plain"}, b"x", 415),
     (UPLOAD, b"x" * (MAX_UPLOAD_BYTES + 1), 413)],
    ids=["missing-key", "wrong-content-type", "oversized"],
)
def test_bad_requests_do_not_create_runs(api, headers, data, status):
    """Reject invalid request metadata or oversized data before claiming a run."""
    client, store = api
    assert client.post("/v1/runs", headers=headers, data=data).status_code == status
    assert not store.mock_calls


@pytest.mark.parametrize(("run", "status"), [(None, 409), ({"status": "processing"}, 202)])
def test_repeated_upload_does_not_process_twice(api, run, status):
    """Return conflict or pending status without writing another result."""
    client, store = api
    store.claim.return_value = run, None
    response = client.post("/v1/runs", headers=UPLOAD, data=b"csv")
    assert response.status_code == status
    store.finish.assert_not_called()
