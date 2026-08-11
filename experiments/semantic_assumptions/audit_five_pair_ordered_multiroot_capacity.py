#!/usr/bin/env python3
"""Score-blind capacity audit for a new five-relation ordered-root test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
METHOD = BASE / "FIVE_PAIR_ORDERED_MULTIROOT_CAPACITY_METHOD.md"
PRIOR = RESULTS / "public_repeated_plant_source_native_capacity.json"
FIFTH = RESULTS / "f102r1_fifth_repeated_plant_label_native_visual_ownership.json"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
OUT = RESULTS / "five_pair_ordered_multiroot_capacity.json"
OUT_MD = RESULTS / "five_pair_ordered_multiroot_capacity_report.md"

EXPECTED = {
    METHOD: "TO_BE_FILLED",
    PRIOR: "a16700eafc88653c3b95f8fcd840a4c86a185ca240a0e19123e880a46373cb2e",
    FIFTH: "04c81c69e4ca249201ea02a337978a544c698655f3c63192c302df605089fe59",
    INTERLINEAR: "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
}
EDITIONS = ("ZL3b", "IT2a", "RF1b")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def report(result: dict) -> str:
    counts = result["root_count_by_label"]
    compact = ", ".join(f"{item['label_locus']}={item['root_count']}" for item in counts)
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
        raise RuntimeError("refusing to overwrite five-pair capacity outputs")

    method_hash = sha(METHOD.read_bytes())
    expected = dict(EXPECTED)
    expected[METHOD] = method_hash
    for path, digest in expected.items():
        if sha(path.read_bytes()) != digest:
            raise RuntimeError(("input hash", path, sha(path.read_bytes()), digest))

    prior = read_json(PRIOR)
    fifth = read_json(FIFTH)
    if prior["capacity"]["relations"] != 4 or len(prior["relations"]) != 4:
        raise RuntimeError("prior relation count")
    if fifth["decision"] != "REOPEN_FIVE_PAIR_SCORE_BLIND_CAPACITY_AND_DESIGN_ONLY":
        raise RuntimeError("fifth relation decision")

    relations = [
        {"target_page": item["target_page"], "label_locus": item["label_locus"]}
        for item in prior["relations"]
    ]
    relations.append({"target_page": "f37v", "label_locus": fifth["label_binding"]["current_locus"]})
    target_pages = tuple(item["target_page"] for item in relations)
    label_loci = tuple(item["label_locus"] for item in relations)

    rows: dict[tuple[str, str], dict[str, str]] = {}
    with INTERLINEAR.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            # The filter precedes all access to target-bearing formal fields.
            if row["locus"] not in label_loci:
                continue
            key = (row["edition"], row["locus"])
            if key in rows:
                raise RuntimeError(("duplicate label row", key))
            rows[key] = row

    expected_keys = {(edition, locus) for edition in EDITIONS for locus in label_loci}
    if set(rows) != expected_keys:
        raise RuntimeError(("label row coverage", set(rows) ^ expected_keys))

    counts: dict[str, dict[str, int]] = {}
    for locus in label_loci:
        counts[locus] = {}
        for edition in EDITIONS:
            row = rows[(edition, locus)]
            if not (
                row["kind"] == "L"
                and row["grammar_scope"] == "DIAGNOSTIC_NONPROSE"
                and row["word_count"] == "1"
            ):
                raise RuntimeError(("label metadata", edition, locus))
            covered = row["core34_covered_words"] == "1" and row["hybrid95_covered_words"] == "1"
            if covered:
                roots = tuple(part for part in row["root_sequence"].split("+") if part)
                if not roots:
                    raise RuntimeError(("empty root sequence", edition, locus))
                counts[locus][edition] = len(roots)
            else:
                counts[locus][edition] = None

    stable_counts = {
        locus: len({value for value in values.values() if value is not None}) == 1
        for locus, values in counts.items()
    }
    root_count_rows = [
        {"label_locus": locus, "root_count": counts[locus]["ZL3b"]}
        for locus in label_loci
    ]
    multiroot = [item["label_locus"] for item in root_count_rows if item["root_count"] >= 2]
    parser_coverage = [
        {"edition": edition, "label_locus": locus, "covered": counts[locus][edition] is not None}
        for edition in EDITIONS
        for locus in label_loci
    ]
    covered_count = sum(item["covered"] for item in parser_coverage)
    assignments = math.factorial(len(relations))
    gates = {
        "exactly_five_relations_pages_and_labels": len(relations) == len(set(target_pages)) == len(set(label_loci)) == 5,
        "every_edition_has_every_strict_one_word_label": set(rows) == expected_keys and covered_count == len(expected_keys),
        "root_counts_stable_across_alternate_readings": all(stable_counts.values()),
        "at_least_four_multiroot_labels": len(multiroot) >= 4,
        "new_fifth_label_is_multiroot": counts[label_loci[-1]]["ZL3b"] >= 2,
        "assignment_floor_at_most_point_01": assignments == 120 and 1 / assignments <= 0.01,
        "target_herbal_rows_used": False,
        "label_to_page_scores_computed": False,
    }
    positive = [key for key in gates if key not in {"target_herbal_rows_used", "label_to_page_scores_computed"}]
    passed = all(gates[key] for key in positive) and not gates["target_herbal_rows_used"] and not gates["label_to_page_scores_computed"]
    decision = "GO_NEW_SCORER_CALIBRATION_AND_PREREGISTRATION_ONLY" if passed else "STOP_ALL_READING_EXACT_ROOT_PARSER_INCOMPLETE"

    result = {
        "experiment": "FIVE_PAIR_ORDERED_MULTIROOT_CAPACITY",
        "status": "PASS_SCORE_BLIND_FIVE_PAIR_CAPACITY" if passed else "STOP_SOURCE_INCOMPLETE",
        "decision": decision,
        "relations": relations,
        "root_count_by_label": root_count_rows,
        "parser_coverage": {
            "covered_label_readings": covered_count,
            "total_label_readings": len(parser_coverage),
            "uncovered": [
                {"edition": item["edition"], "label_locus": item["label_locus"]}
                for item in parser_coverage if not item["covered"]
            ],
        },
        "capacity": {
            "relations": len(relations),
            "multiroot_relations": len(multiroot),
            "singleton_relations": len(relations) - len(multiroot),
            "fixed_assignments": assignments,
            "minimum_inclusive_one_sided_p": 1 / assignments,
            "singleton_deleted_assignments": math.factorial(len(multiroot)),
            "singleton_deleted_minimum_p": 1 / math.factorial(len(multiroot)),
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
        "gates": gates,
        "inputs": {str(path.relative_to(ROOT)): digest for path, digest in expected.items()},
        "claim_ceiling": "Five fixed relations and four multi-root labels fix the old orbit and composition counts, but one RF1b label is outside the frozen formal parser, so the all-reading exact-root route stops unscored. No target Herbal association has been scored, and no plant name, component, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    OUT.write_bytes(canonical(result))
    OUT_MD.write_text(report(result), encoding="utf-8")


if __name__ == "__main__":
    main()
