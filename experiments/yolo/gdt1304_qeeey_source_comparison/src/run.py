"""Replay the retained comparison; this is not an automated visual judgment."""
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
print(json.dumps(json.loads((p/'artifacts/RESULT.json').read_text()),indent=2))
