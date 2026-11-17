"""Render WSGI entry point for the ILAD pilot using Firestore."""

import os

import firebase_admin
from google.cloud import firestore

from firebase.pilot import create_firebase_app
from firebase.run_store import FirestoreRunStore

project = os.environ["ILAD_FIREBASE_PROJECT"]
firebase_admin.initialize_app(options={"projectId": project})
store = FirestoreRunStore(
    firestore.Client(project=project),
    bucket=None,
    analytics_version=os.environ.get("RENDER_GIT_COMMIT", "local-render"),
)
app = create_firebase_app(store, os.environ["ILAD_ALLOWED_ORIGINS"])
