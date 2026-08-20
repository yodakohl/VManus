#!/usr/bin/env python3
"""Independent integrity checks for the GDT395 interface freeze."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
FREEZE = EXP / "artifacts/gdt395_interface_freeze.json"
OUT = EXP / "artifacts/gdt395_interface_freeze_validation.json"


def main() -> None:
    d = json.loads(FREEZE.read_text())
    checks = {}
    checks["schema"] = d["schema"] == "GDT395_INTERFACE_FREEZE_V1"
    checks["status"] = d["status"] == "FROZEN_BEFORE_WORLD_DESIGN"
    checks["ten_worlds"] = len(d["world_assignments"]) == 10 and len({x["world_id"] for x in d["world_assignments"]}) == 10
    checks["ten_sol_designers"] = d["designer_policy"]["primary_model"] == "gpt-5.6-sol" and d["designer_policy"]["one_isolated_session_per_world"]
    checks["twenty_seeds"] = d["corpus_seeds"] == list(range(20))
    checks["voynich_scale"] = d["target_events_per_seed"] == 8448
    checks["six_representations"] = len(d["representations"]) == 6
    checks["property_panel"] = len(d["properties"]) >= 17
    checks["organic_majority"] = sum(bool(x["organic_required"]) for x in d["world_assignments"]) >= 6
    checks["two_adversarial_pairs"] = sorted({x["adversarial_pair_id"] for x in d["world_assignments"] if x["adversarial_pair_id"] != "NONE"}) == ["PAIR_CODEBOOK", "PAIR_SEMANTIC"]
    checks["semantics_light"] = sum(x["broad_family"] == "SEMANTICS_LIGHT_GENERATOR" for x in d["world_assignments"]) == 1
    checks["decoder_separation"] = d["decoder_policy"]["designers_excluded"] and d["decoder_policy"]["observation_only"]
    checks["f84_sealed"] = not any(d["f84"].values()) and d["voynich_rows"] == 0
    checks["inputs_empty"] = d["inputs"] == []
    checks["hashes"] = all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in d["hashes"].items())
    tmp = dict(d); expected = tmp.pop("content_sha256")
    actual = hashlib.sha256(json.dumps(tmp, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    checks["content_hash"] = expected == actual
    result = {
        "schema": "GDT395_INTERFACE_FREEZE_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "freeze_sha256": hashlib.sha256(FREEZE.read_bytes()).hexdigest(),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "checks": f"{result['checks_passed']}/{result['checks_total']}"}))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
