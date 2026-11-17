"""Store private pilot runs using Firestore metadata and Cloud Storage results."""

import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from google.api_core.exceptions import AlreadyExists, FailedPrecondition

LEASE_DURATION = timedelta(minutes=3)
RPC_TIMEOUT = 10


class FirestoreRunStore:
    """Persist run status and enforce ownership before reading result objects."""

    def __init__(self, database, bucket, analytics_version: str) -> None:
        self._runs = database.collection("ilad_runs")
        self._database = database
        self._bucket = bucket
        self._analytics_version = analytics_version

    def get(self, run_id: str, owner: str, *, include_csv: bool = False) -> dict | None:
        """Return the run payload for its owner."""
        run = self._runs.document(run_id).get(timeout=RPC_TIMEOUT).to_dict()
        if run is None or run["owner"] != owner:
            return None
        return self._response(run, include_csv=include_csv)

    def claim(self, run_id: str, owner: str, digest: str) -> tuple[dict | None, str | None]:
        """Claim a new or retryable run atomically, scoped to the same owner and CSV."""
        document = self._runs.document(run_id)
        now = datetime.now(timezone.utc)
        attempt = uuid4().hex

        run = {
            "run_id": run_id,
            "owner": owner,
            "digest": digest,
            "created_at": now,
            "analytics_version": self._analytics_version,
            "status": "processing",
            "attempt": attempt,
            "lease_until": now + LEASE_DURATION,
            "details": {},
        }
        try:
            document.create(run, timeout=RPC_TIMEOUT)
            return self._response(run), attempt
        except AlreadyExists:
            pass

        for _ in range(3):
            snapshot = document.get(timeout=RPC_TIMEOUT)
            existing = snapshot.to_dict()
            if existing is None or existing["owner"] != owner or existing["digest"] != digest:
                return None, None
            if existing["status"] in ("succeeded", "invalid") or (
                existing["status"] == "processing" and existing["lease_until"] > now
            ):
                return self._response(existing), None
            run["created_at"] = existing["created_at"]
            try:
                option = self._database.write_option(last_update_time=snapshot.update_time)
                document.update(run, option=option, timeout=RPC_TIMEOUT)
                return self._response(run), attempt
            except FailedPrecondition:
                continue
        raise RuntimeError("Run changed during each claim attempt")

    def finish(self, run_id: str, attempt: str, status: str, payload: dict) -> dict:
        """Publish only the active attempt, after its result object is durable."""
        document = self._runs.document(run_id)
        snapshot = document.get(timeout=RPC_TIMEOUT)
        run = snapshot.to_dict()
        if run is None or run["attempt"] != attempt or run["status"] != "processing":
            raise RuntimeError("Run attempt is no longer active")
        update = {"status": status}
        if status == "succeeded":
            object_name = f"ilad-runs/{run_id}/{attempt}.json"
            blob = self._bucket.blob(object_name)
            blob.upload_from_string(
                json.dumps(payload, allow_nan=False),
                content_type="application/json",
                if_generation_match=0,
                timeout=RPC_TIMEOUT,
            )
            update["result_object"] = object_name
        else:
            update["details"] = payload

        option = self._database.write_option(last_update_time=snapshot.update_time)
        document.update(update, option=option, timeout=RPC_TIMEOUT)
        return self._response(run | update, payload)

    def _response(self, run: dict, payload: dict | None = None, *, include_csv: bool = False) -> dict:
        if payload is None:
            if run["status"] == "succeeded":
                blob = self._bucket.blob(run["result_object"])
                payload = json.loads(blob.download_as_bytes(timeout=RPC_TIMEOUT))
            else:
                payload = run.get("details", {})
        response = {
            "schema_version": 1,
            "run_id": run["run_id"],
            "created_at": run["created_at"].isoformat(),
            "analytics_version": run["analytics_version"],
            "status": run["status"],
            "cohort_size": None,
            "overview": None,
            **payload,
        }
        response["csv_export_available"] = "analytics_csv" in payload
        if not include_csv:
            response.pop("analytics_csv", None)
        return response
