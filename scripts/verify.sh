#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/evidence/core-$RUN_ID"
mkdir -p "$OUT"
trap 'rc=$?; printf "%s\n" "$rc" > "$OUT/exit_code.txt"; echo "EXIT_CODE=$rc"; echo "EVIDENCE=$OUT"; exit "$rc"' EXIT
cd "$ROOT"
{
  uv run ruff format --check .
  uv run ruff check .
  uv run mypy src
  uv run pytest -q
  uv build
  uv run sr-studio models
  uv run sr-studio doctor
} 2>&1 | tee "$OUT/verify.log"
