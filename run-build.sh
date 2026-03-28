#!/usr/bin/env bash

set -euo pipefail

INPUT_FILE="$1"
NIXPKGS_PATH="$2"

JOBS=$(nproc)
TIMEOUT=30

LOG_DIR="build-logs"

mkdir -p "$LOG_DIR"

build_package() {
  local name="$1"

  echo "Starting build: $name"
  out_log="$LOG_DIR/${name}.log"

  timeout "$TIMEOUT" \
    nix-build -E "(import $NIXPKGS_PATH {}).${name}" \
      --max-jobs 1 \
      --cores 1 \
      --no-link \
      2>&1 | tee $out_log

  status=${PIPESTATUS[0]}

  if [ $status -eq 0 ]; then
    echo "@@@ [SUCCESS] @@@" | tee -a "$out_log"
  elif [ $status -eq 124 ]; then
    echo "@@@ [TIMEOUT] @@@" | tee -a "$out_log"
  else
    echo "@@@ [FAIL] @@@" | tee -a "$out_log"
  fi
}

export -f build_package
export LOG_DIR TIMEOUT NIXPKGS_PATH

cat "$INPUT_FILE" | xargs -I{} -P "$JOBS" bash -c 'build_package "$@"' _ {}
