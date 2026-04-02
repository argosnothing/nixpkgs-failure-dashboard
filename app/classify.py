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

DETECTORS = {
    "rust": {
        "markers": ["rustc", ".rs:"],
        "patterns": [r"error\[\w+\]:", r"error:"],
    },
    "c": {
        "markers": ["gcc", "g++"],
        "patterns": [r":\d+:\d+: error:"],
    },
    "python": {
        "markers": ["python", ".py:"],
        "patterns": [r"File.*line \d+", r"Error:", r"Traceback"],
    },
    "cmake": {
        "markers": ["cmake", "ninja"],
        "patterns": [r"FAILED:", r"error:"],
    },
}


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


def find_error_line(log: str) -> int | None:
    for name, config in DETECTORS.items():
        if any(marker in log for marker in config["markers"]):
            result = find_specialized_error(log, config["patterns"])
            if result is not None:
                return result
    return find_generic_error_from_end(log)


def find_specialized_error(log: str, patterns: list[str]) -> int | None:
    lines = log.split("\n")
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in patterns]

    for i in range(len(lines) - 1, -1, -1):
        line = lines[i]

        if any(
            skip in line.lower()
            for skip in ["warning", "deprecation", "note:", "license"]
        ):
            continue

        for pattern in compiled_patterns:
            if pattern.search(line):
                phase_found = False
                for j in range(i + 1, min(i + 20, len(lines))):
                    if "Running phase:" in lines[j] or "@@@" in lines[j]:
                        phase_found = True
                        break

                if not phase_found:
                    return i + 1

    return None


def find_generic_error_from_end(log: str) -> int | None:
    lines = log.split("\n")
    pattern = re.compile(
        r"(error:|Error:|ERROR|FAILED|fatal:|Failed)", re.IGNORECASE
    )

    # check starting from bottom of file and traverse backwards
    # until an error is found, then check the next 20 lines of that error
    # to confirm if the error was fatal or not
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i]
        if any(skip in line.lower() for skip in ["warning", "deprecation"]):
            continue

        if pattern.search(line):
            phase_found = False
            for j in range(i + 1, min(i + 20, len(lines))):
                if "Running phase:" in lines[j] or "@@@" in lines[j]:
                    phase_found = True
                    break

            if not phase_found:
                return i + 1

    return None


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
                or "note: build failure may have been caused by lack of free disk space" in log
                or "/root/nixpkgs-failure" in log
                or log == "@@@ [FAIL] @@@\n"
            ):
                continue

            matches = re.findall("error: attribute '.*' missing\n", log)
            if matches:
                continue

            error_line = find_error_line(log)

            build = Build(
                attrpath=attrpath,
                hydra_id=hydra_ids.get(attrpath),
                tag=classify_log(log),
                error_line_number=error_line,
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
