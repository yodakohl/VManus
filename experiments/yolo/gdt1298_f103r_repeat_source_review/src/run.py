#!/usr/bin/env python3
"""Replay the fixed human-readable observation record; does not automate vision."""
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
print(json.dumps(json.loads((p/'artifacts/OBSERVATION.json').read_text()),indent=2))
