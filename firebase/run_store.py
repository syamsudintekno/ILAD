"""Store private pilot runs and their results."""

import gzip
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from google.api_core.exceptions import AlreadyExists, FailedPrecondition

LEASE_DURATION = timedelta(minutes=3)
RPC_TIMEOUT = 10
RESULT_CHUNK_BYTES = 256 * 1024
MAX_COMPRESSED_RESULT_BYTES = 7 * 1024 * 1024


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
        option = self._database.write_option(last_update_time=snapshot.update_time)
        if status == "succeeded" and self._bucket is None:
            self._publish_firestore(document, attempt, payload, update, option)
            return self._response(run | update, payload)
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

        document.update(update, option=option, timeout=RPC_TIMEOUT)
        return self._response(run | update, payload)

    def _publish_firestore(self, document, attempt: str, payload: dict, update: dict, option) -> None:
        """Write result chunks and status in one conditional Firestore batch."""
        compressed = gzip.compress(json.dumps(payload, allow_nan=False).encode("utf-8"))
        if len(compressed) > MAX_COMPRESSED_RESULT_BYTES:
            raise ValueError("Result exceeds the Firestore batch size allowance")
        chunks = document.collection(f"result_{attempt}")
        batch = self._database.batch()
        count = 0
        for offset in range(0, len(compressed), RESULT_CHUNK_BYTES):
            batch.create(chunks.document(f"{count:03d}"), {
                "data": compressed[offset:offset + RESULT_CHUNK_BYTES],
            })
            count += 1
        update["result_chunk_count"] = count
        batch.update(document, update, option=option)
        batch.commit(timeout=RPC_TIMEOUT)

    def _read_result(self, run: dict) -> dict:
        """Read a published Firestore or Cloud Storage result."""
        if "result_chunk_count" in run:
            chunks = self._runs.document(run["run_id"]).collection(f"result_{run['attempt']}")
            snapshots = list(chunks.stream(timeout=RPC_TIMEOUT))
            snapshots.sort(key=lambda snapshot: snapshot.id)
            if len(snapshots) != run["result_chunk_count"]:
                raise RuntimeError("Incomplete Firestore result")
            compressed = b"".join(snapshot.get("data") for snapshot in snapshots)
            return json.loads(gzip.decompress(compressed))
        if self._bucket is None:
            raise RuntimeError("Run requires its original Cloud Storage backend")
        blob = self._bucket.blob(run["result_object"])
        return json.loads(blob.download_as_bytes(timeout=RPC_TIMEOUT))

    def _response(self, run: dict, payload: dict | None = None, *, include_csv: bool = False) -> dict:
        if payload is None:
            if run["status"] == "succeeded":
                payload = self._read_result(run)
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
