"""Replay retained informed observation; does not automate visual inspection."""
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
print(json.dumps(json.loads((p/'artifacts/OBSERVATION.json').read_text()),indent=2))
