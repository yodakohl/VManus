#!/usr/bin/env python3
"""Small proposal/receipt integrity check; no target data are read."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "vmanus-work").is_file())
checks = []
source_hashes = {}
for name, idea in [("K_01_AGE_EXCEPTION_SCOPE.json", "IDEA000764"),
                   ("K_02_INFLUENCE_RELATION.json", "IDEA000765")]:
    p = HERE / name
    data = json.loads(p.read_text())
    assert data["status"] == "RAW_UNREVIEWED_NOT_SELECTED_NOT_TESTED"
    for key in ["title", "summary", "scope"]:
        assert data[key]
    for key in ["mechanism", "unit", "contrast", "prediction",
                "actual_referents", "additional_assumption",
                "strongest_known_countercase", "smallest_next_test"]:
        assert data["design"][key]
    for rel in data["design"]["primaries"]:
        q = Path(rel)
        assert not q.is_absolute() and ".." not in q.parts
        source = ROOT / q
        assert source.is_file(), rel
        source_hashes[rel] = hashlib.sha256(source.read_bytes()).hexdigest()
    checks.append({"file": name, "id": idea, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
for p in HERE.glob("K_*RECEIPT*.json"):
    json.loads(p.read_text())
artifacts = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(HERE.glob("K_*"))
             if p.is_file() and p.name != "K_VALIDATION.json"}
result = {"status": "PASS_FILE_INTEGRITY_ONLY", "proposals": checks,
          "source_hashes": source_hashes, "artifact_hashes": artifacts,
          "no_semantic_test": True}
(HERE / "K_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"status": result["status"], "proposals": checks,
                  "source_count": len(source_hashes), "artifact_count": len(artifacts)}, indent=2))
