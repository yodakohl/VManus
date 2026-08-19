#!/usr/bin/env python3
"""Independent retained-output validator for the GDT378 target stage."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer"
ART = BASE / "artifacts"
SOURCE = ROOT / "gdt327_joint_tuple_interlinear.tsv"
DESIGN = ART / "gdt378_voynich_target_design_freeze.json"
SIGNATURES = ART / "gdt378_secondary_transfer_signature_freeze.json"
CORRECTION = ART / "gdt378_target_execution_correction.json"
EVENTS = ART / "gdt378_voynich_event_scores.tsv.gz"
CANDIDATES = ART / "gdt378_voynich_candidate_atlas.tsv"
SUMMARY = ART / "gdt378_voynich_resolution_summary.tsv"
NULL = ART / "gdt378_voynich_null.tsv.gz"
TARGET_RESULT = ART / "gdt378_voynich_target_result.json"
DIAGNOSTIC = ART / "gdt378_identity_only_diagnostic.tsv"
DIAGNOSTIC_NULL = ART / "gdt378_identity_only_null.tsv.gz"
DIAGNOSTIC_RESULT = ART / "gdt378_identity_only_diagnostic_result.json"
FINAL_RESULT = ART / "gdt378_result.json"
RUNNER = BASE / "src/run_voynich_target.py"


def read(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_content(obj):
    clone = dict(obj)
    expected = clone.pop("content_hash")
    actual = hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return actual == expected


def source_group_id(row):
    value = ["SOURCE_GROUP", row["joint_tuple_id"], row["observed_wrapper"]]
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:20]


def main():
    source = read(SOURCE)
    design = json.loads(DESIGN.read_text())
    signatures = json.loads(SIGNATURES.read_text())
    correction = json.loads(CORRECTION.read_text())
    events = read(EVENTS)
    candidates = read(CANDIDATES)
    summary = read(SUMMARY)
    null = read(NULL)
    target = json.loads(TARGET_RESULT.read_text())
    diagnostic = read(DIAGNOSTIC)
    diagnostic_null = read(DIAGNOSTIC_NULL)
    diagnostic_result = json.loads(DIAGNOSTIC_RESULT.read_text())
    final = json.loads(FINAL_RESULT.read_text())
    checks = {}

    checks["source_exact"] = len(source) == 8448 and len({(row["page"], row["record_ordinal"]) for row in source}) == 288 and len({row["physical_folio"] for row in source}) == 91
    checks["source_fields"] = len({(row["page"], row["record_ordinal"], row["locus"], row["field_ordinal"]) for row in source}) == target["field_spans"] == 2400
    checks["source_f84_free"] = not any(any(row[key].lower().startswith("f84") for key in ("page", "physical_folio", "locus")) for row in source)
    checks["design_hashes"] = all(sha(ROOT / path) == digest for part in ("inputs", "documents") for path, digest in design[part].items())
    design_clone = dict(design)
    design_expected = design_clone.pop("content_hash")
    checks["design_content"] = hashlib.sha256(json.dumps(design_clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == design_expected
    checks["signature_count"] = signatures["signature_count"] == 4 and len(signatures["signatures"]) == 4

    expected_events = 4 * (8448 + 8448 + 2400)
    checks["event_count"] = len(events) == expected_events == 77184
    checks["event_resolution_counts"] = Counter(row["base_resolution"] for row in events) == Counter({"ATOMIC_JOINT_TUPLE": 33792, "SOURCE_GROUP": 33792, "FIELD_CONSTRUCTION_SPAN": 9600})
    checks["event_signature_counts"] = set(Counter(row["signature_id"] for row in events).values()) == {19296}
    checks["event_score_math"] = all(0 <= float(row["score"]) <= 1 and abs(float(row["score"]) - float(row["placement_baseline"]) - float(row["placement_residual"])) < 2e-9 for row in events)
    checks["event_uniqueness"] = len({(row["signature_id"], row["base_resolution"], row["unit_id"]) for row in events}) == len(events)
    checks["event_unassigned"] = all(row["semantic_state"] == "UNASSIGNED" for row in events)
    checks["event_f84_free"] = not any(row["page"].lower().startswith("f84") or row["physical_folio"].lower().startswith("f84") or row["locus"].lower().startswith("f84") for row in events)

    checks["candidate_count"] = len(candidates) == target["candidate_rows"] == 24356
    checks["powered_count"] = sum(row["powered"] == "1" for row in candidates) == target["powered_candidates"] == 1064
    checks["no_primary_promotions"] = not any(row["candidate_gate"] == "PASS" for row in candidates) and target["promoted_candidates"] == 0
    checks["powered_primary_p_one"] = all(row["max_family_p"] == "1.000000000000" for row in candidates if row["powered"] == "1")
    checks["candidate_unassigned"] = all(row["anonymous_class"] == "UNASSIGNED" and row["semantic_state"] == "UNASSIGNED" for row in candidates)
    checks["summary_rows"] = len(summary) == 16 and sum(int(row["powered_candidates"]) for row in summary) == 1064 and sum(int(row["promoted_candidates"]) for row in summary) == 0
    checks["null_capacity"] = all(row["null_capacity_ok"] == "1" for row in summary)
    checks["null_mobility"] = target["null_mobility"] == {"ATOMIC_JOINT_TUPLE": 6539, "SOURCE_GROUP": 6612, "FIELD_CONSTRUCTION_SPAN": 1005}

    primary_values = [float(row["max_abs_residual_statistic"]) for row in null]
    checks["primary_null_worlds"] = len(primary_values) == 4096
    checks["primary_null_degenerate"] = len(set(primary_values)) == 1 and abs(primary_values[0] - 561.258338298071) < 1e-12
    invariant = next(row for row in candidates if row["signature_id"] == "CMP_FUNCTION_03" and row["resolution"] == "GRAMMAR_SLOT_POSITION" and row["candidate_family"] == "FROM_START_X_CLOSURE" and row["candidate_id"] == "1__LINE_END")
    checks["invariant_slot_rebuilt"] = abs(float(invariant["residual_statistic_abs"]) - 561.258338297445) < 1e-12 and invariant["max_family_p"] == "1.000000000000"

    # Independently reconstruct the linked formal lead from the source and event layer.
    atomic_id = "2f1c5e56e8f0ff459065"
    group_id = "c502a1edfafbe3e54262"
    atomic_source = [row for row in source if row["joint_tuple_id"] == atomic_id]
    group_source = [row for row in source if source_group_id(row) == group_id]
    checks["lead_source_relation"] = len(atomic_source) == 435 and len(group_source) == 249 and {row["joint_tuple_id"] for row in group_source} == {atomic_id} and {row["observed_wrapper"] for row in group_source} == {"d"}
    event_index = defaultdict(list)
    for row in events:
        event_index[(row["signature_id"], row["base_resolution"], row["unit_id"])].append(row)
    atomic_residuals = [float(event_index[("CMP_FUNCTION_04", "ATOMIC_JOINT_TUPLE", row["event_id_sha256"])][0]["placement_residual"]) for row in atomic_source]
    group_residuals = [float(event_index[("CMP_FUNCTION_04", "SOURCE_GROUP", row["event_id_sha256"])][0]["placement_residual"]) for row in group_source]
    checks["lead_residual_means"] = abs(sum(atomic_residuals) / len(atomic_residuals) - .109185315999) < 2e-12 and abs(sum(group_residuals) / len(group_residuals) - .174044817432) < 2e-12

    correction_clone = dict(correction)
    correction_expected = correction_clone.pop("content_hash")
    checks["correction_content"] = hashlib.sha256(json.dumps(correction_clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == correction_expected
    checks["correction_exact"] = correction["scientific_definition_changed"] is False and correction["frozen_scorer_sha256"] == design["implementation"][str(RUNNER.relative_to(ROOT))] and correction["corrected_scorer_sha256"] == sha(RUNNER)
    checks["correction_reproduction"] = all(sha(ART / name) == digest for name, digest in correction["scores_materialized_before_correction"].items())

    diagnostic_values = [float(row["identity_only_max_abs_statistic"]) for row in diagnostic_null]
    checks["diagnostic_null"] = len(diagnostic_values) == 4096 and len(set(diagnostic_values)) == diagnostic_result["identity_only_null_unique_maxima"] == 3393
    checks["diagnostic_counts"] = len(diagnostic) == diagnostic_result["powered_identity_candidates"] == 960 and sum(float(row["identity_only_max_family_p"]) <= .05 for row in diagnostic) == 24
    checks["diagnostic_min_p"] = abs(min(float(row["identity_only_max_family_p"]) for row in diagnostic) - diagnostic_result["minimum_identity_only_p"]) < 1e-15 and abs(diagnostic_result["minimum_identity_only_p"] - .000244081035) < 1e-15
    atlas = {(row["signature_id"], row["resolution"], row["candidate_family"], row["candidate_id"]): row for row in candidates}
    diagnostic_leads = []
    for row in diagnostic:
        original = atlas[(row["signature_id"], row["resolution"], row["candidate_family"], row["candidate_id"])]
        if float(row["identity_only_max_family_p"]) <= .05 and float(original["held_sse_gain_over_placement"]) > 0 and float(original["positive_gain_folio_fraction"]) >= .60 and float(original["mean_placement_residual"]) > 0 and float(original["positive_residual_folio_fraction"]) >= 2 / 3 and int(original["positive_residual_registers"]) >= 2:
            diagnostic_leads.append((row["signature_id"], row["resolution"], row["candidate_id"]))
    checks["two_linked_diagnostic_leads"] = diagnostic_leads == [("CMP_FUNCTION_04", "SOURCE_GROUP", group_id), ("CMP_FUNCTION_04", "ATOMIC_JOINT_TUPLE", atomic_id)]

    checks["target_hashes"] = all(sha(ROOT / path) == digest for part in ("inputs", "outputs", "implementation") for path, digest in target[part].items())
    checks["target_content"] = check_content(target)
    checks["diagnostic_hashes"] = all(sha(ROOT / path) == digest for part in ("inputs", "outputs", "implementation") for path, digest in diagnostic_result[part].items())
    checks["diagnostic_content"] = check_content(diagnostic_result)
    checks["final_hashes"] = all(sha(ROOT / path) == digest for part in ("inputs", "implementation") for path, digest in final[part].items())
    checks["final_content"] = check_content(final)
    checks["final_decision"] = final["status"] == "HEAD_FAILED_PRIMARY_TARGET_NULL_DEGENERATE_TWO_POSTHOC_IDENTITY_LEADS" and final["target_promoted_candidates"] == 0 and final["posthoc_identity_only_lead_count"] == 2 and final["semantic_assignments"] == 0
    checks["all_f84_flags"] = not any(target["f84"].values()) and not any(diagnostic_result["f84"].values()) and not any(final["f84"].values())

    validation = {
        "schema": "GDT378_TARGET_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "scope": "Independent source/event/candidate/null accounting, lead reconstruction, correction provenance, hashes and decisions; does not independently rerun the 91-fold scorer or 4096 permutations.",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "final_result_sha256": sha(FINAL_RESULT),
        "validator_sha256": sha(Path(__file__)),
    }
    (ART / "gdt378_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(validation["status"], f"{validation['checks_passed']}/{validation['checks_total']}")
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
