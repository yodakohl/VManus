#!/usr/bin/env python3
"""Independent integrity checks for the score-free GDT379 freeze."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt379_f1_orthogonal_behavior"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_content(obj: dict) -> bool:
    expected = obj["content_hash"]
    clone = dict(obj)
    clone.pop("content_hash")
    actual = hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return expected == actual


def main() -> None:
    checks = []
    def check(name, value):
        checks.append({"check": name, "pass": bool(value)})
        if not value:
            raise AssertionError(name)

    cand = json.loads((ART / "gdt379_f1_candidate_freeze.json").read_text())
    null = json.loads((ART / "gdt379_null_and_future_correction_freeze.json").read_text())
    result = json.loads((ART / "gdt379_freeze_result.json").read_text())
    with (ART / "gdt379_diagnostic_manifest.tsv").open(newline="") as h:
        rows = list(csv.DictReader(h, delimiter="\t"))
    check("candidate_content_hash", valid_content(cand))
    check("null_content_hash", valid_content(null))
    check("result_content_hash", valid_content(result))
    check("f1_atomic_exact", cand["candidate"]["atomic_joint_tuple_id"] == "2f1c5e56e8f0ff459065")
    check("f1_d_group_exact", cand["candidate"]["d_rendered_source_group_id"] == "c502a1edfafbe3e54262")
    check("one_linked_object", cand["candidate"]["linked_resolutions_are_independent"] is False)
    check("not_promoted", cand["gdt378_identity_lead_promoted"] is False)
    check("old_null_not_retuned", cand["gdt378_primary_null_retuned"] is False)
    check("comparator_label_not_inherited", cand["source_comparator_label_inherited"] is False)
    check("eleven_diagnostics", len(rows) == 11 and len({r["diagnostic_id"] for r in rows}) == 11)
    check("eight_f1", sum(r["route"] == "F1" for r in rows) == 8)
    check("three_separate_routes", {r["route"] for r in rows if r["route"] != "F1"} == {"CMP_FUNCTION_01", "CMP_FUNCTION_02", "CMP_FUNCTION_03"})
    check("joint_4096_maxT", null["worlds"] == 4096 and null["joint_maxT"] is True and null["charged_diagnostic_families"] == 11)
    check("f2_replayed", null["nested_F2_search_replayed_per_world"] is True)
    check("future_null_mobile", "MOBILE_CANDIDATE_MEMBERSHIP" in null["future_slot_null_correction"]["allowed"].upper())
    check("no_retroactive_fix", null["future_slot_null_correction"]["gdt378_retroactive_change_authorized"] is False)
    check("no_outcomes", result["outcomes_inspected"] == 0 and result["f1_contexts_enumerated"] == 0)
    check("source_f84_free", "\tf84" not in (ROOT / "gdt327_joint_tuple_interlinear.tsv").read_text(encoding="utf-8"))
    check("all_input_hashes", all(sha(ROOT / p) == d for p, d in result["inputs"].items()))
    check("all_output_hashes", all(sha(ROOT / p) == d for p, d in result["outputs"].items()))
    check("all_document_hashes", all(sha(ROOT / p) == d for p, d in result["documents"].items()))
    check("semantic_unassigned", cand["candidate"]["semantic_state"] == "UNASSIGNED" and all(r["semantic_state"] == "UNASSIGNED" for r in rows))
    check("f84_flags_false", all(v is False for v in result["f84"].values()))

    validation = {
        "schema": "GDT379_FREEZE_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "result_sha256": sha(ART / "gdt379_freeze_result.json"),
        "validator_sha256": sha(BASE / "src/validate_freeze.py"),
    }
    validation["content_hash"] = hashlib.sha256(json.dumps(validation, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (ART / "gdt379_freeze_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
