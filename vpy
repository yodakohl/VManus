#!/usr/bin/env bash
set -euo pipefail

# Canonical VManus interpreter: vision models, CuPy, and the scientific stack
# live together here.  Use ./vpy instead of relying on the system `python`.
exec /home/anon/.venvs/voynich-vision/bin/python "$@"
