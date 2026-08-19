#!/usr/bin/env python3
"""Validate the GDT374 pre-score freeze without importing its builder."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt374_common_functional_operator_discovery"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    fp = ART / "gdt374_freeze.json"
    data = json.loads(fp.read_text())
    check("schema", data["schema"] == "GDT374_FREEZE_V1")
    check("not_run", data["candidate_forms_enumerated"] == data["scores_computed"] == 0)
    check("three_scopes", data["record_scopes"] == ["FIELD", "DRAWING_RESET_SEGMENT", "PHYSICAL_LINE"])
    check("rewrite_count", len(data["rewrite_library"]) == 10)
    check("atomic_only", all(x in data["forbidden_features"] for x in ("HOST_ID", "PAGE_HOST", "GLYPH", "SUBSTRING", "TARGET_STATE")))
    check("worlds", data["permutation_worlds"] == 4096)
    check("promotion_capacity", data["minimum_candidate_base_sequences"] == 3 and data["minimum_candidate_physical_folios"] == 2)
    check("raw_guard", data["f84_policy"] == "RAW_PAGE_GUARD_BEFORE_ROW_PARSE_REJECT_ALL_F84_PREFIXES")
    check("f84", data["f84_accessed"] is False)
    check("no_semantics", data["semantic_roles_assigned"] == 0)
    for rel, digest in data["inputs"].items():
        check("input_" + rel, sha(ROOT / rel) == digest)
    for rel, digest in data["documents"].items():
        check("document_" + rel, sha(ROOT / rel) == digest)
    for rel, digest in data["implementation"].items():
        check("implementation_" + rel, sha(ROOT / rel) == digest)
    payload = dict(data)
    stored = payload.pop("content_hash")
    check("content_hash", hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == stored)
    out = {
        "schema": "GDT374_FREEZE_VALIDATION_V1",
        "status": "PASS",
        "scope": "INDEPENDENT_PRE_SCORE_FREEZE_INTEGRITY",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "freeze_sha256": sha(fp),
        "validator_sha256": sha(BASE / "src/validate_freeze.py"),
        "f84_accessed": False,
    }
    (ART / "gdt374_freeze_validation.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
