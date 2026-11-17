"""Build a Firebase source directory from an explicit list of Python sources."""

from pathlib import Path
from shutil import copyfile


def stage() -> None:
    """Copy function and analytics sources without copying workspace data."""
    source = Path(__file__).resolve().parent
    root = source.parent
    destination = root / ".ilad-functions"
    destination.mkdir(exist_ok=True)
    for filename in ("main.py", "pilot.py", "run_store.py", "requirements.txt"):
        copyfile(source / filename, destination / filename)
    for package in ("application", "analytics", "config", "core"):
        (destination / package).mkdir(exist_ok=True)
        for module in (root / package).glob("*.py"):
            copyfile(module, destination / package / module.name)


if __name__ == "__main__":
    stage()
