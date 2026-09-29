"""Recheck bound inputs; native image and semantic judgments are not automated."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def validate():
    receipt = json.loads((HERE / "AJ_INPUTS.json").read_text())
    checks = []
    for rec in receipt["files"]:
        path = ROOT / rec["path"]
        checks.append({"path": rec["path"], "matches": hashlib.sha256(path.read_bytes()).hexdigest() == rec["sha256"]})
    closure = json.loads((HERE / "AI_CLOSURE.json").read_text())
    for rec in closure["author_files"]:
        path = ROOT / rec["path"]
        checks.append({"path": rec["path"], "matches": hashlib.sha256(path.read_bytes()).hexdigest() == rec["sha256"]})
    result = {
        "status": "PASS" if all(c["matches"] for c in checks) else "FAIL",
        "kind": "source identity only; no image, transcription or meaning validation",
        "checks": len(checks),
        "details": checks,
        "semantic_tests": 0,
    }
    return result


if __name__ == "__main__":
    result = validate()
    (HERE / "AJ_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "details"}, indent=2))
    raise SystemExit(result["status"] != "PASS")
