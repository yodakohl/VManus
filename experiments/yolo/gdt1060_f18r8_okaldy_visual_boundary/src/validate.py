#!/usr/bin/env python3
"""Check the frozen scope, source receipt and bounded result contract."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
IMAGE = ROOT / "research_registry/work_batches/ten_hours_20260915/paired_root_cache/f18r.jpg"
EXPECTED = "01659aa94a6176b56c621f50c9cbe8c467836d6265a03d8edb1e97e236126e78"

def main():
    manifest = json.loads((HERE / "experiment.json").read_text())
    result = json.loads((HERE / "artifacts/RESULT.json").read_text())
    assert manifest["experiment_id"] == result["experiment_id"] == "GDT1060"
    assert manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}
    assert hashlib.sha256(IMAGE.read_bytes()).hexdigest() == EXPECTED
    assert result["source_image_sha256"] == EXPECTED
    assert result["locus"] == "f18r.8"
    assert result["decision"] == "UNRESOLVED"
    assert result["confirmed_words"] == 0
    assert result["independent_confirmation_capacity"] == 0
    print("PASS: frozen image, sealed scope, bounded unresolved result")

if __name__ == "__main__":
    main()
