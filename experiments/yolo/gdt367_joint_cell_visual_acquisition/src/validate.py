#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes, sha256_file  # noqa:E402

EXP = ROOT / "experiments/yolo/gdt367_joint_cell_visual_acquisition"; ART = EXP / "artifacts"


def read(path):
    with path.open(newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def main():
    targets = read(ART / "gdt367_target_manifest.tsv"); obs = read(ART / "gdt367_visual_observations.tsv"); result = json.loads((ART / "gdt367_result.json").read_text())
    t = {r["gdt367_target_id"]: r for r in targets}; o = {r["gdt367_target_id"]: r for r in obs}
    body = dict(result); digest = body.pop("content_hash")
    broad = Counter(r["broad_closed_form"] for r in obs); fork = Counter(r["fork_or_branch"] for r in obs); fill = Counter(r["colored_fill"] for r in obs)
    checks = [
        len(t) == len(o) == 27 and set(t) == set(o),
        broad == Counter({"PRESENT": 27}),
        fill == Counter({"PRESENT": 27}),
        fork == Counter({"PRESENT": 24, "ABSENT": 2, "UNCERTAIN": 1}),
        result["global_axis_counts"]["BROAD_CLOSED_FORM"] == dict(broad),
        result["global_axis_counts"]["FORK_OR_BRANCH"] == dict(fork),
        result["global_axis_counts"]["COLORED_FILL"] == dict(fill),
        result["new_axes_mobile_within_at_least_two_folios"] == ["FORK_OR_BRANCH"],
        result["status"] == "NEW_AXES_INSUFFICIENT_FOR_JOINT_FORMAL_SEARCH",
        result["formal_rows_loaded_or_joined"] is False and result["formal_search_run"] is False,
        result["historical_contact_gap_gates_rewritten"] is False,
        result["f84_accessed"] is False,
        all(not r["page"].startswith("f84") and not r["locus"].startswith("f84") for r in targets),
        all(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in obs),
        all(sha256_file(ROOT / p) == h for p, h in result["inputs"].items()),
        all(sha256_file(ROOT / p) == h for p, h in result["outputs"].items()),
        all(sha256_file(ROOT / p) == h for p, h in result["implementation"].items()),
        hashlib.sha256(canonical_json_bytes(body)).hexdigest() == digest,
    ]
    assert all(checks)
    payload = {"schema": "GDT367_VALIDATION_V1", "status": "PASS", "checks_passed": sum(checks), "checks_total": len(checks), "result_sha256": sha256_file(ART / "gdt367_result.json"), "scope": "INDEPENDENT_ROW_COUNTS_CAPACITY_ARITHMETIC_HASHES_AND_ACCESS_FLAGS"}
    (ART / "gdt367_validation.json").write_bytes(canonical_json_bytes(payload))
    print(f"PASS {sum(checks)}/{len(checks)}")


if __name__ == "__main__": main()
