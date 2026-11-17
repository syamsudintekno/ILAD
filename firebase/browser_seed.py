"""Create synthetic browser test accounts only in the loopback Auth emulator."""

import os

import firebase_admin
from firebase_admin import auth


def seed() -> None:
    """Provision the Admin QA and viewer accounts used by browser tests."""
    if os.environ.get("FIREBASE_AUTH_EMULATOR_HOST") != "127.0.0.1:9099":
        raise SystemExit("Start the demo-ilad Auth emulator on 127.0.0.1:9099 first.")
    firebase_admin.initialize_app(options={"projectId": "demo-ilad"})
    for email, claims in (
        ("qa-browser@example.test", {"ilad_role": "admin_qa"}),
        ("viewer-browser@example.test", {}),
    ):
        try:
            user = auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            user = auth.create_user(email=email, password="EmulatorOnly-ILAD-2026")
        auth.set_custom_user_claims(user.uid, claims)


if __name__ == "__main__":
    seed()
