#!/usr/bin/env bash
set -euo pipefail

# Portable interpreter wrapper. Set VOYNICH_PYTHON to an explicit executable
# when a dedicated scientific environment is required.
if [[ -n "${VOYNICH_PYTHON:-}" ]]; then
  exec "$VOYNICH_PYTHON" "$@"
elif [[ -x .venv/bin/python ]]; then
  exec .venv/bin/python "$@"
else
  exec python3 "$@"
fi
