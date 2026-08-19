#!/usr/bin/env python3
"""Independent integrity checks for the score-free GDT380 comparator freeze."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt380_identity_free_functional_transfer"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj: dict) -> str:
    clone = dict(obj)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    checks: list[dict] = []

    def check(name: str, ok: bool) -> None:
        checks.append({"check": name, "pass": bool(ok)})
        if not ok:
            raise AssertionError(name)

    freeze = json.loads((ART / "gdt380_comparator_behavior_freeze.json").read_text())
    result = json.loads((ART / "gdt380_comparator_freeze_result.json").read_text())
    check("freeze_content_hash", freeze["content_hash"] == content(freeze))
    check("result_content_hash", result["content_hash"] == content(result))
    check("four_families", [x["id"] for x in freeze["anonymous_families"]] == [f"CMP_FUNCTION_0{i}" for i in range(1, 5)])
    check("identity_forbidden", freeze["identity_policy"]["exact_opaque_id_as_feature"] is False)
    check("f1_closed", freeze["f1"]["semantic_route_closed"] is True and freeze["f1"]["used_in_gdt380"] is False)
    check("f1_gate_not_lowered", freeze["f1"]["stability_gate_changed"] is False)
    check("fixed_horizons", freeze["horizons"] == [1, 2, 4, 8])
    check("joint_null", freeze["null"]["worlds"] == 1024 and "FOUR_FAMILIES" in freeze["null"]["joint_maxT"])
    check("mobile_target_rule", freeze["target_if_authorized"]["deterministic_conditioned_candidate"].startswith("UNIDENTIFIABLE"))
    check("not_scored", result["status"] == "FROZEN_NOT_RUN" and freeze["voynich_target_rows_read"] == 0)
    check("f84_false", all(v is False for v in freeze["f84"].values()) and all(v is False for v in result["f84"].values()))
    for path, digest in freeze["inputs"].items():
        check("input_" + path.replace("/", "_"), sha(ROOT / path) == digest)
    for section in ["documents", "implementation", "outputs"]:
        for path, digest in result[section].items():
            check(section + "_" + path.replace("/", "_"), sha(ROOT / path) == digest)
    out = {
        "schema": "GDT380_COMPARATOR_FREEZE_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "result_hash": sha(ART / "gdt380_comparator_freeze_result.json"),
        "f84": {"opened": False, "parsed": False, "retained": False, "scored": False},
    }
    out["content_hash"] = content(out)
    (ART / "gdt380_comparator_freeze_validation.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
