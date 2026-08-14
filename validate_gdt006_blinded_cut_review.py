#!/usr/bin/env python3
"""Independent integrity validator for the GDT006 capacity stop."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_tsv(name):
    with (ROOT / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def sha(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def main():
    checks = []
    def check(name, value):
        checks.append({"name": name, "pass": bool(value)})
        if not value:
            raise AssertionError(name)

    selection = read_tsv("gdt005_matched_cut_selection.tsv")
    rows = read_tsv("gdt006_cut_localizations.tsv")
    reviews = read_tsv("gdt006_blind_reviews.tsv")
    result = json.loads((ROOT / "gdt006_blinded_cut_result.json").read_text())
    expected = set()
    for s in selection:
        for arm, prefix in (("TARGET", "target"), ("CONTROL", "control")):
            for ordinal, offset in enumerate(s[f"{prefix}_cut_offsets_1based"].split(";"), 1):
                expected.add((s["pair_id"], arm, str(ordinal), s["locus"], s[f"{prefix}_group_index"], s[f"{prefix}_surface"], offset))
    actual = {(r["pair_id"], r["arm"], r["cut_ordinal"], r["locus"], r["group_index"], r["surface"], r["display_cut_offset"]) for r in rows}
    check("exact_registered_probe_set", len(selection) == 9 and len(rows) == 34 and actual == expected)
    check("unique_probes", len(actual) == 34)
    check("arm_counts", sum(r["arm"] == "TARGET" for r in rows) == 17 and sum(r["arm"] == "CONTROL" for r in rows) == 17)
    check("localization_counts", sum(r["localization_state"] == "LOCALIZED" for r in rows) == 3 and sum(r["localization_state"] == "LOCALIZATION_UNRESOLVED" for r in rows) == 31)
    check("localized_targets_only", sum(r["arm"] == "TARGET" and r["localization_state"] == "LOCALIZED" for r in rows) == 3 and not any(r["arm"] == "CONTROL" and r["localization_state"] == "LOCALIZED" for r in rows))
    check("intrinsic_inside_sta", sum("falls inside single STA" in r["neutral_note"] for r in rows) == 5)
    pair_states = {r["pair_id"]: r["legacy_target_box_contains_registered_group"] for r in rows if r["arm"] == "TARGET"}
    check("legacy_pair_states", list(pair_states.values()).count("YES") == 2 and list(pair_states.values()).count("NO") == 2 and list(pair_states.values()).count("UNRESOLVED") == 5)
    check("no_review_rows", reviews == [] and result["blind_review"]["review_rows"] == 0 and result["blind_review"]["score"] == "NOT_COMPUTED")
    check("invalid_packet_excluded", not result["blind_review"]["valid_final_matched_packet_delivered"] and result["blind_review"]["provisional_packet"] == "INVALIDATED_WITHDRAWN_AND_EXCLUDED")
    check("status", result["status"] == "STOP_LOCALIZATION_CAPACITY_3_OF_34_NO_BLIND_REVIEW")
    check("result_counts", result["localization"]["localized_target_cuts"] == 3 and result["localization"]["localized_control_cuts"] == 0 and result["localization"]["unresolved_total"] == 31)
    check("no_f84", all("f84" not in json.dumps(r) for r in rows) and not result["holdout"]["f84r_opened"])
    for name, digest in result["inputs"].items():
        check("input_hash_" + name, sha(name) == digest)
    check("claim_ceiling", "no spacing effect" in result["claim_ceiling"] and "translation" in result["claim_ceiling"])
    payload = {
        "status": "PASS_CAPACITY_AND_PROVENANCE_INTEGRITY",
        "checks_passed": len(checks),
        "checks": checks,
        "result_sha256": sha("gdt006_blinded_cut_result.json"),
        "report_sha256": sha("GDT006_BLINDED_CUT_REVIEW_REPORT.md"),
        "validator_sha256": sha("validate_gdt006_blinded_cut_review.py"),
        "branch_ledger_sha256": sha("GDT002_YOLO_LEDGER.tsv"),
        "scope": "Independently reconstructs the registered probe set, localization attrition, absent review, hashes, holdout exclusion, and claim ceiling; it does not repeat source-aware visual localization.",
    }
    (ROOT / "gdt006_blinded_cut_validation.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
