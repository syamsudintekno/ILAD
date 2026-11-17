"""Firebase HTTPS entry point for the ILAD pilot API."""

import os
from functools import lru_cache

import firebase_admin
from firebase_functions import https_fn
from firebase_functions.options import MemoryOption
from flask.ctx import RequestContext
from google.cloud import firestore, storage

from pilot import create_firebase_app
from run_store import FirestoreRunStore

firebase_app = firebase_admin.initialize_app()


@lru_cache(maxsize=1)
def pilot_app():
    """Configure the private storage and allowed frontend origins."""
    project = firebase_app.project_id
    store = FirestoreRunStore(
        firestore.Client(project=project),
        storage.Client(project=project).bucket(os.environ["ILAD_STORAGE_BUCKET"]),
        os.environ["ILAD_ANALYTICS_VERSION"],
    )
    return create_firebase_app(store, os.environ.get("ILAD_ALLOWED_ORIGINS", ""))


@https_fn.on_request(timeout_sec=120, memory=MemoryOption.MB_512, invoker="public")
def ilad_api(request: https_fn.Request) -> https_fn.Response:
    """Dispatch HTTP requests after the hosting platform resolves the function."""
    app = pilot_app()
    # Share the request body cache with Functions Framework's response hook.
    with RequestContext(app, request.environ, request=request):
        return app.full_dispatch_request()
