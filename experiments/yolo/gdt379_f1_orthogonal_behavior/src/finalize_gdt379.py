#!/usr/bin/env python3
"""Bind final GDT379 documents and implementation into the settled result."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt379_f1_orthogonal_behavior"
ART = BASE / "artifacts"
RESULT = ART / "gdt379_result.json"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

obj = json.loads(RESULT.read_text())
obj["documents"] = {str((BASE / name).relative_to(ROOT)): sha(BASE / name) for name in ["METHOD.md", "README.md", "REPORT.md", "experiment.json"]}
scripts = sorted((BASE / "src").glob("*.py"))
obj["implementation"] = {str(path.relative_to(ROOT)): sha(path) for path in scripts}
corrections = sorted(ART.glob("gdt379_*correction.json"))
obj["corrections"] = {str(path.relative_to(ROOT)): sha(path) for path in corrections}
obj.pop("content_hash", None)
obj["content_hash"] = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
RESULT.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
