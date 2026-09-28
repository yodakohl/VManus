#!/usr/bin/env python3
"""Reproduce the source-image receipt; the registered visual call is manual."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
IMAGE = ROOT / "research_registry/work_batches/ten_hours_20260915/paired_root_cache/f18r.jpg"
EXPECTED = "01659aa94a6176b56c621f50c9cbe8c467836d6265a03d8edb1e97e236126e78"

def main():
    observed = hashlib.sha256(IMAGE.read_bytes()).hexdigest()
    if observed != EXPECTED:
        raise SystemExit(f"source hash mismatch: {observed}")
    result = json.loads((Path(__file__).resolve().parents[1] / "artifacts/RESULT.json").read_text())
    print(json.dumps({"image_sha256": observed, "manual_decision": result["decision"]}, indent=2))

if __name__ == "__main__":
    main()
