import re
from typing import Callable


def hunk_failed(log: str) -> bool:
    return (
        'hunk FAILED -- saving rejects' in log
        or 'hunks FAILED -- saving rejects' in log
        or 'Skipping patch.\n1 out of 1 hunk ignored\n' in log
    )


def substitute_error(log: str) -> bool:
    return bool(re.search(r'substitute\(\): ERROR:', log)) or (
        "substituteStream() in derivation" in log
        and "ERROR: pattern" in log
        and "doesn't match anything in file" in log
    )


def curl_fetch_error(log: str) -> bool:
    return (
        "curl: (22) The requested URL returned error: 404" in log
        and "error: cannot download source from any mirror" in log
    )


def hash_mismatch(log: str) -> bool:
    return "error: hash mismatch in fixed-output derivation" in log



CHECKS: tuple[tuple[str, Callable[[str], bool]], ...] = (
    ("fetch-error", curl_fetch_error),
    ("hash-mismatch", hash_mismatch),
    ("hunk-failed", hunk_failed),
    ("substitute-error", substitute_error),
)
