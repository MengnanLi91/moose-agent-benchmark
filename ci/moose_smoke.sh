#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${MOOSE_APP:-}" ]]; then
  echo "MOOSE_APP must name an available MOOSE application executable" >&2
  exit 2
fi

if [[ "$MOOSE_APP" != /* ]]; then
  resolved_app="$(command -v "$MOOSE_APP")"
else
  resolved_app="$MOOSE_APP"
fi

uv run python -m moose_benchmark run-check \
  --executable "$resolved_app" \
  --case-root ci/fixtures \
  --input minimal_valid.i \
  --wall-time 60 \
  --cpu-time 30 \
  --memory-mib 2048 \
  --output benchmark-results/moose-smoke.json
