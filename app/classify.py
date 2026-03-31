from collections import defaultdict
from contextlib import contextmanager

import csv
import io
import os
import pathlib
import re
import urllib.request

from .db import get_db, reset_db
from .models import Build
from .tagging import CHECKS

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
    return {row["name"]: int(row["id"]) for row in reader}


def get_status(log: str) -> str:
    if log.endswith("@@@ [SUCCESS] @@@\n"):
        return "success"
    if log.endswith("@@@ [TIMEOUT] @@@\n"):
        return "timeout"
    return "failed"


def is_hash_mismatch(log: str) -> bool:
    return "error: hash mismatch in fixed-output derivation" in log


def classify_log(log: str) -> str:
    for name, check in CHECKS:
        if check(log):
            return name

    return "unknown"


def main():
    builds = []
    logs = sorted(
        LOG_DIR / entry
        for entry in os.listdir(LOG_DIR)
        if entry.endswith(".log")
    )

    reset_db()
    hydra_ids = fetch_hydra_ids()
    count = 0

    per_tags = defaultdict(list)

    with contextmanager(get_db)() as session:
        for logfile in logs:
            attrpath = logfile.name.removesuffix(".log")
            print("processing", attrpath)

            log = logfile.read_bytes().decode(errors="ignore")
            if get_status(log) != "failed":
                continue

            if (
                "error: Refusing to evaluate package" in log
                or "No space left on device" in log
                or "/root/nixpkgs-failure" in log
                or log == "@@@ [FAIL] @@@\n"
            ):
                continue

            matches = re.findall("error: attribute '.*' missing\n", log)
            if matches:
                continue

            build = Build(
                attrpath=attrpath,
                hydra_id=hydra_ids.get(attrpath),
                tag=classify_log(log),
            )

            per_tags[build.tag].append(build)
            builds.append(build)
            count += 1

        print("Registered", count, "packages")
        session.add_all(builds)
        session.commit()

        print("\nTagged:")
        for tag, vals in per_tags.items():
            print(f"- {tag}:", len(vals))


if __name__ == "__main__":
    main()
