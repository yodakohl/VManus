#!/usr/bin/env python3
"""Independent reconstruction of the five-pair ordered-root capacity stop."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
METHOD = BASE / "FIVE_PAIR_ORDERED_MULTIROOT_CAPACITY_METHOD.md"
PRODUCER = BASE / "audit_five_pair_ordered_multiroot_capacity.py"
PRIOR = RESULTS / "public_repeated_plant_source_native_capacity.json"
FIFTH = RESULTS / "f102r1_fifth_repeated_plant_label_native_visual_ownership.json"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
RESULT = RESULTS / "five_pair_ordered_multiroot_capacity.json"
REPORT = RESULTS / "five_pair_ordered_multiroot_capacity_report.md"
OUT = RESULTS / "five_pair_ordered_multiroot_capacity_validation.json"
OUT_MD = RESULTS / "five_pair_ordered_multiroot_capacity_validation_report.md"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
INPUT_HASHES = {
    PRIOR: "a16700eafc88653c3b95f8fcd840a4c86a185ca240a0e19123e880a46373cb2e",
    FIFTH: "04c81c69e4ca249201ea02a337978a544c698655f3c63192c302df605089fe59",
    INTERLINEAR: "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_report(result: dict) -> str:
    compact = ", ".join(
        f"{item['label_locus']}={item['root_count']}" for item in result["root_count_by_label"]
    )
    coverage = result["parser_coverage"]
    return (
        "# Five-pair ordered-multiroot capacity\n\n"
        f"Decision: **{result['decision']}**.\n\n"
        "The externally fixed panel contains five distinct Herbal pages and five distinct "
        "pharmaceutical label loci. Formal-root counts are stable across ZL3b, IT2a, and "
        f"RF1b: {compact}. Four labels are multi-root, including the new fifth label. "
        "The fixed assignment orbit is 120, so its minimum inclusive one-sided rank is "
        "1/120 = 0.008333. However, only "
        f"{coverage['covered_label_readings']}/{coverage['total_label_readings']} label-reading "
        "cells are covered by the frozen formal parser: RF1b f102r2.22 is uncovered. The "
        "predeclared all-reading completeness gate therefore fails before calibration or "
        "target scoring.\n\n"
        "The fifth label identity was accidentally exposed to the analyst only after the "
        "relation and ownership result were published; no f37v target prose or label-to-page "
        "association was opened. Do not rescue the stopped exact-root route by dropping RF1b, "
        "using the unresolved parser output, or changing the representation after inspection.\n\n"
        "No plant name, component, word, sound, language, cipher, plaintext, meaning, or "
        "translation follows.\n"
    )


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise RuntimeError("refusing to overwrite five-pair validation")
    checks: list[str] = []
    for path, digest in INPUT_HASHES.items():
        if sha(path.read_bytes()) != digest:
            raise RuntimeError(("input hash", path))
    checks.append("frozen_primary_inputs")

    producer_tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
    imports = {
        node.module
        for node in ast.walk(producer_tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    if any("validate_five_pair" in item for item in imports):
        raise RuntimeError("producer imports validator")
    checks.append("nonimporting_independence")

    prior = read_json(PRIOR)
    fifth = read_json(FIFTH)
    relations = [
        {"target_page": item["target_page"], "label_locus": item["label_locus"]}
        for item in prior["relations"]
    ] + [{"target_page": "f37v", "label_locus": fifth["label_binding"]["current_locus"]}]
    loci = tuple(item["label_locus"] for item in relations)
    pages = tuple(item["target_page"] for item in relations)
    if len(set(loci)) != 5 or len(set(pages)) != 5:
        raise RuntimeError("relation distinctness")
    checks.append("five_relation_panel")

    rows: dict[tuple[str, str], dict[str, str]] = {}
    with INTERLINEAR.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in loci:
                rows[(row["edition"], row["locus"])] = row
    expected_keys = {(edition, locus) for edition in EDITIONS for locus in loci}
    if set(rows) != expected_keys:
        raise RuntimeError("label row coverage")
    checks.append("all_label_rows")

    counts: dict[str, dict[str, int | None]] = {locus: {} for locus in loci}
    for locus in loci:
        for edition in EDITIONS:
            row = rows[(edition, locus)]
            if (row["kind"], row["grammar_scope"], row["word_count"]) != (
                "L", "DIAGNOSTIC_NONPROSE", "1"
            ):
                raise RuntimeError(("metadata", edition, locus))
            covered = row["core34_covered_words"] == row["hybrid95_covered_words"] == "1"
            counts[locus][edition] = (
                len([item for item in row["root_sequence"].split("+") if item]) if covered else None
            )
    root_rows = [{"label_locus": locus, "root_count": counts[locus]["ZL3b"]} for locus in loci]
    if [item["root_count"] for item in root_rows] != [1, 3, 2, 3, 5]:
        raise RuntimeError("root-count reconstruction")
    checks.append("root_counts_without_identity_output")

    uncovered = [
        {"edition": edition, "label_locus": locus}
        for edition in EDITIONS for locus in loci if counts[locus][edition] is None
    ]
    if uncovered != [{"edition": "RF1b", "label_locus": "f102r2.22"}]:
        raise RuntimeError(("uncovered", uncovered))
    checks.append("single_RF_parser_gap")

    method_hash = sha(METHOD.read_bytes())
    input_rows = {
        str(METHOD.relative_to(ROOT)): method_hash,
        str(PRIOR.relative_to(ROOT)): INPUT_HASHES[PRIOR],
        str(FIFTH.relative_to(ROOT)): INPUT_HASHES[FIFTH],
        str(INTERLINEAR.relative_to(ROOT)): INPUT_HASHES[INTERLINEAR],
    }
    assignments = math.factorial(5)
    expected = {
        "experiment": "FIVE_PAIR_ORDERED_MULTIROOT_CAPACITY",
        "status": "STOP_SOURCE_INCOMPLETE",
        "decision": "STOP_ALL_READING_EXACT_ROOT_PARSER_INCOMPLETE",
        "relations": relations,
        "root_count_by_label": root_rows,
        "parser_coverage": {
            "covered_label_readings": 14,
            "total_label_readings": 15,
            "uncovered": uncovered,
        },
        "capacity": {
            "relations": 5,
            "multiroot_relations": 4,
            "singleton_relations": 1,
            "fixed_assignments": assignments,
            "minimum_inclusive_one_sided_p": 1 / assignments,
            "singleton_deleted_assignments": 24,
            "singleton_deleted_minimum_p": 1 / 24,
        },
        "exposure_and_access": {
            "relation_and_ownership_published_before_label_exposure": True,
            "fifth_label_identity_exposed_to_analyst_after_ownership_freeze": True,
            "fifth_label_root_sequence_exposed_to_analyst_after_ownership_freeze": True,
            "target_herbal_prose_rows_used": False,
            "label_to_page_scores_computed": False,
            "label_or_root_identity_serialized_here": False,
        },
        "stop_rules": {
            "do_not_drop_RF1b": True,
            "do_not_use_uncovered_parser_output": True,
            "do_not_run_old_S100": True,
            "do_not_score_target_pages": True,
        },
        "gates": {
            "exactly_five_relations_pages_and_labels": True,
            "every_edition_has_every_strict_one_word_label": False,
            "root_counts_stable_across_alternate_readings": True,
            "at_least_four_multiroot_labels": True,
            "new_fifth_label_is_multiroot": True,
            "assignment_floor_at_most_point_01": True,
            "target_herbal_rows_used": False,
            "label_to_page_scores_computed": False,
        },
        "inputs": input_rows,
        "claim_ceiling": "Five fixed relations and four multi-root labels fix the old orbit and composition counts, but one RF1b label is outside the frozen formal parser, so the all-reading exact-root route stops unscored. No target Herbal association has been scored, and no plant name, component, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    result_bytes = RESULT.read_bytes()
    if result_bytes != canonical(expected):
        raise RuntimeError("canonical result mismatch")
    checks.append("canonical_result")
    if REPORT.read_text(encoding="utf-8") != expected_report(expected):
        raise RuntimeError("report mismatch")
    checks.append("exact_report")
    if expected["gates"]["every_edition_has_every_strict_one_word_label"]:
        raise RuntimeError("stop gate unexpectedly passes")
    checks.append("stop_decision")

    validation = {
        "experiment": "FIVE_PAIR_ORDERED_MULTIROOT_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_RECONSTRUCTION_OF_UNSCORED_SOURCE_STOP",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": sha(result_bytes),
        "producer_sha256": sha(PRODUCER.read_bytes()),
        "reconstructed": {
            "relations": 5,
            "assignments": 120,
            "multiroot_relations": 4,
            "covered_label_readings": 14,
            "total_label_readings": 15,
            "uncovered": uncovered,
            "target_scores_computed": 0,
        },
        "claim_ceiling": expected["claim_ceiling"],
    }
    OUT.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# Five-pair ordered-multiroot capacity validation\n\n"
        "Status: **PASS_INDEPENDENT_RECONSTRUCTION_OF_UNSCORED_SOURCE_STOP**.\n\n"
        f"All {len(checks)} checks pass. Independent code recovers five fixed relations, "
        "four multi-root labels, the 120-assignment orbit, and the single uncovered cell "
        "RF1b f102r2.22. The all-reading exact-root route correctly stops before scorer "
        "calibration or target-page access.\n\n"
        "No plant name, component, word, sound, language, cipher, plaintext, meaning, or "
        "translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
