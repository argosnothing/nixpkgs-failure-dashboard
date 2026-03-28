import os
import pathlib
from contextlib import contextmanager

from .db import get_db, reset_db
from .models import Build

LOG_DIR = pathlib.Path("build-logs")


def get_status(log: str) -> str:
    if log.endswith("@@@ [SUCCESS] @@@\n"):
        return "success"
    if log.endswith("@@@ [TIMEOUT] @@@\n"):
        return "timeout"
    return "failed"


def main():
    builds = []
    logs = sorted(
        LOG_DIR / entry
        for entry in os.listdir(LOG_DIR)
        if entry.endswith(".log")
    )

    reset_db()

    with contextmanager(get_db)() as session:
        for logfile in logs:
            print("processing", logfile)
            log = logfile.read_bytes().decode(errors="ignore")

            build = Build(
                attrpath=logfile.name.removesuffix(".log"),
                status=get_status(log),
            )

            builds.append(build)

        session.add_all(builds)
        session.commit()


if __name__ == "__main__":
    main()
