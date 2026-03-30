from contextlib import contextmanager
import csv
import io
import os
import pathlib
import urllib.request

from .db import get_db, reset_db
from .models import Build

LOG_DIR = pathlib.Path("build-logs")

CSV_URL = (
    "https://raw.githubusercontent.com/"
    "Sigmanificient/nixpkgs-failure-notify"
    "/refs/heads/results"
    "/results/3-failures-x86_64-linux.csv"
)


def fetch_hydra_ids() -> dict[str, int]:
    with urllib.request.urlopen(CSV_URL) as resp:
        content = resp.read().decode()

    reader = csv.DictReader(io.StringIO(content))
    return {
        row["name"]: int(row["id"])
        for row in reader
    }


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
    hydra_ids = fetch_hydra_ids()

    with contextmanager(get_db)() as session:
        for logfile in logs:
            attrpath = logfile.name.removesuffix(".log")
            print("processing", attrpath)

            log = logfile.read_bytes().decode(errors="ignore")
            if get_status(log) != "failed":
                continue

            build = Build(
                attrpath=attrpath,
                hydra_id=hydra_ids.get(attrpath)
            )

            builds.append(build)

        session.add_all(builds)
        session.commit()


if __name__ == "__main__":
    main()
