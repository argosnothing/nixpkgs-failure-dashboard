import pathlib
import os

XDG_STATE_HOME = os.getenv("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))
RUNTIME_DIR = pathlib.Path(XDG_STATE_HOME) / "nixpkgs-failure-dashboard"

BUILD_LOGS_DIR = RUNTIME_DIR / "build-logs"
DIST_BUILD_DIR = pathlib.Path("dist")
