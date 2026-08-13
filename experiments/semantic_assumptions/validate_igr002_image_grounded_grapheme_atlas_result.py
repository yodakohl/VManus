#!/usr/bin/env python3
"""Independently validate the mapping-invariant IGR002 conclusion."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
RES = BASE / "results"
METHOD = BASE / "IGR002_IMAGE_GROUNDED_GRAPHEME_ATLAS_METHOD.md"
REG = RES / "igr002_image_grounded_grapheme_atlas_registration.json"
SEL = RES / "igr002_image_grounded_grapheme_atlas_selection.json"
SELV = RES / "igr002_image_grounded_grapheme_atlas_selection_validation.json"
BLIND = BASE / "igr002_image_grounded_grapheme_blinded_worklist.tsv"
LOC = BASE / "igr002_image_grounded_grapheme_localizations.tsv"
JOIN = BASE / "igr002_image_grounded_grapheme_crop_review_join.tsv"
REV = BASE / "igr002_image_grounded_grapheme_crop_reviews.tsv"
OBS = BASE / "igr002_image_grounded_grapheme_atlas_observations.tsv"
RESULT = RES / "igr002_image_grounded_grapheme_atlas_result.json"
REPORT = RES / "igr002_image_grounded_grapheme_atlas_result_report.md"
OUT = RES / "igr002_image_grounded_grapheme_atlas_result_validation.json"
OUT_REPORT = RES / "igr002_image_grounded_grapheme_atlas_result_validation_report.md"
BUILDER = BASE / "build_igr002_image_grounded_grapheme_atlas_selection.py"
SEL_VALIDATOR = BASE / "validate_igr002_image_grounded_grapheme_atlas_selection.py"

FIELDS = [
    "main_vertical_stems", "closed_loops", "left_extension",
    "right_extension", "descender", "separated_dot",
]
ELIGIBLE = {"ONE_CLEAR_VISIBLE_UNIT", "LIGATED_OR_COMPOSITE_UNIT"}
INELIGIBLE = {"LOCALIZATION_UNRESOLVED", "DAMAGED_RETRACED_OR_AMBIGUOUS"}
PRIMARY_TYPES = (1, 2, 3, 4, 5, 7, 8)
REVIEW_HEADER = [
    "reviewer", "review_id", "localization_state", "confidence", *FIELDS,
    "visible_note",
]
LOC_HEADER = [
    "crop_id", "canvas_id", "full_image_sha256", "image_width", "image_height",
    "crop_x", "crop_y", "crop_w", "crop_h", "target_x", "target_y",
    "target_w", "target_h", "confidence", "note",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_json(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    def hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key: {key}")
            out[key] = value
        return out
    obj = json.loads(raw, object_pairs_hook=hook, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    return obj, raw


def tsv(path: Path, header: list[str]) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != header:
            raise ValueError(f"wrong header: {path}")
        rows = list(reader)
    if any(set(row) != set(header) or any(value is None for value in row.values()) for row in rows):
        raise ValueError(f"malformed TSV: {path}")
    return rows


def signature(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(row[field] for field in FIELDS)


def expected_report(status: str) -> str:
    return f"""# IGR002 held-folio image-grounded grapheme atlas

Status: **{status}**.

Across all 26 crop-review records, 14 reviews have a match-eligible localization state and 12 are unresolved, damaged, retraced, or ambiguous. Treated as an unordered signature multiset, only one match-eligible six-field review signature equals any of the frozen primary prototypes: the type-3 prototype. Every other frozen prototype signature occurs zero times.

Consequently, regardless of the unresolved target-to-crop and review mapping, the number of exact primary matches is at most 1/28, below the frozen 20/28 gate. Type 3 can have at most one of four exact matches, while every other primary type has zero compatible review signatures; therefore 0/7 primary types can reach the frozen three-of-four condition, below the 6/7 gate. These two mapping-invariant failures are independently sufficient to fail the conjunctive preregistered pass rule.

The target-to-crop binding and reviewer-delivery mapping were not preserved in contemporaneous sealed provenance artifacts. The primary-localization count is therefore not adjudicated: canvas-compatible mappings permit 23/28 or 24/28 localized primary targets, straddling the frozen 24/28 threshold. The bundle does not support an exact target-level 1/28 claim, an exact match at a named locus, assigned type-level match counts, or a claim that all three gates fail. Reviewer history, exact delivered inputs, and release chronology remain workflow assertions rather than independently reconstructed provenance.

This provenance-qualified result closes only the frozen held-folio transfer test under the exact six-field rubric on two mapping-invariant gates. The disclosed observation table and join are retained for audit but are `DISCLOSED_UNVERIFIED_MAPPING_DO_NOT_CITE` as scored target assignments. No OCR, CLIP, embedding, or automated visual classifier entered. The reviews are machine-authored native-vision observations, not independent human annotations. No preferred reading, allography, sound, alphabet, word, language, cipher, plaintext, meaning, or translation follows.
"""


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing overwrite")
    selection, selection_raw = strict_json(SEL)
    registration, _ = strict_json(REG)
    selection_validation, _ = strict_json(SELV)
    result, result_raw = strict_json(RESULT)
    reviews = tsv(REV, REVIEW_HEADER)
    localizations = tsv(LOC, LOC_HEADER)
    checks: dict[str, bool] = {}

    commitments = registration["commitments"]
    checks["registered_private_commitments_match_disclosure"] = (
        hashlib.sha256(selection_raw).hexdigest() == commitments["private_selection_sha256"]
        and sha(BLIND) == commitments["blinded_worklist_sha256"]
        and sha(BUILDER) == commitments["private_builder_sha256"]
        and sha(SEL_VALIDATOR) == commitments["private_validator_sha256"]
        and sha(RES / "igr002_image_grounded_grapheme_atlas_selection_report.md") == commitments["private_selection_report_sha256"]
        and sha(SELV) == commitments["private_selection_validation_sha256"]
        and sha(METHOD) == commitments["method_sha256"]
    )
    checks["selection_validation_binding"] = (
        selection_validation["status"].startswith("PASS_")
        and selection_validation["result_sha256"] == sha(SEL)
    )
    targets = selection["targets"]
    nonce = selection["private_registration_nonce"]
    checks["selection_cardinality_and_ids"] = (
        len(targets) == 32
        and bool(re.fullmatch(r"[0-9a-f]{64}", nonce))
        and len({target["opaque_id"] for target in targets}) == 32
        and all(
            target["opaque_id"] == "IGR2" + hashlib.sha256(
                (nonce + "|" + target["locus"] + "|" + str(target["symbol_index_1based"])).encode()
            ).hexdigest()[:14].upper()
            for target in targets
        )
    )
    checks["selection_primary_structure"] = (
        sum(bool(target["primary_prediction_target"]) for target in targets) == 28
        and Counter(target["type_index"] for target in targets) == {index: 4 for index in range(1, 9)}
        and all(len({target["physical_folio"] for target in targets if target["type_index"] == index}) == 4 for index in range(1, 9))
    )

    checks["review_rows_exact_and_unique"] = (
        len(reviews) == 26
        and len({row["review_id"] for row in reviews}) == 26
        and all(row["confidence"] in {"LOW", "MEDIUM", "HIGH"} for row in reviews)
    )
    checks["review_rubric_domains"] = all(
        row["localization_state"] in ELIGIBLE | INELIGIBLE
        and row["main_vertical_stems"] in {"ZERO", "ONE", "TWO_PLUS"}
        and row["closed_loops"] in {"NONE", "ONE", "TWO_PLUS"}
        and all(row[field] in {"YES", "NO"} for field in FIELDS[2:])
        for row in reviews
    )
    eligible = [row for row in reviews if row["localization_state"] in ELIGIBLE]
    checks["eligible_ineligible_counts"] = len(eligible) == 14 and len(reviews) - len(eligible) == 12

    prototypes = {}
    for type_index in PRIMARY_TYPES:
        rows_for_type = [target for target in targets if target["type_index"] == type_index]
        values = {tuple(target["prototype_signature"][field] for field in FIELDS) for target in rows_for_type}
        if len(values) != 1:
            raise SystemExit(f"nonunique prototype for type {type_index}")
        prototypes[type_index] = next(iter(values))
    review_signatures = Counter(signature(row) for row in eligible)
    occurrences = {type_index: review_signatures[prototype] for type_index, prototype in prototypes.items()}
    checks["six_unique_primary_prototypes"] = len(set(prototypes.values())) == 6
    checks["mapping_invariant_prototype_occurrences"] = occurrences == {1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 7: 0, 8: 0}
    exact_upper = sum(review_signatures[sig] for sig in set(prototypes.values()))
    qualified_upper = sum(min(4, review_signatures[prototypes[index]]) >= 3 for index in PRIMARY_TYPES)
    checks["exact_match_gate_invariantly_fails"] = exact_upper == 1 and exact_upper < 20
    checks["type_recurrence_gate_invariantly_fails"] = qualified_upper == 0 and qualified_upper < 6

    checks["localization_rows_exact_and_unique"] = (
        len(localizations) == 32
        and len({row["crop_id"] for row in localizations}) == 32
        and all(bool(re.fullmatch(r"[0-9a-f]{64}", row["full_image_sha256"])) for row in localizations)
    )
    target_by_canvas: dict[str, list[dict]] = defaultdict(list)
    loc_by_canvas: dict[str, list[dict[str, str]]] = defaultdict(list)
    for target in targets:
        target_by_canvas[target["canvas_id"]].append(target)
    for row in localizations:
        loc_by_canvas[row["canvas_id"]].append(row)
    checks["canvas_multiplicities_match_without_target_join"] = {
        key: len(value) for key, value in target_by_canvas.items()
    } == {key: len(value) for key, value in loc_by_canvas.items()}
    minimum = maximum = 0
    for canvas_id, canvas_targets in target_by_canvas.items():
        primary_count = sum(bool(target["primary_prediction_target"]) for target in canvas_targets)
        resolved_count = sum(row["target_x"] != "NA" for row in loc_by_canvas[canvas_id])
        diagnostic_count = len(canvas_targets) - primary_count
        minimum += max(0, resolved_count - diagnostic_count)
        maximum += min(primary_count, resolved_count)
    checks["localization_interval_reconstructed_unverified"] = (minimum, maximum) == (23, 24)

    expected_bounds = {
        "exact_primary_matches": {"lower_bound": 0, "upper_bound": 1, "threshold": 20, "pass": False, "status": "MAPPING_INVARIANT_FAILURE"},
        "localized_primary_targets": {"lower_bound": 23, "upper_bound": 24, "threshold": 24, "pass": None, "status": "UNVERIFIED_TARGET_CROP_BINDING"},
        "qualified_primary_types": {"lower_bound": 0, "upper_bound": 0, "threshold": 6, "pass": False, "status": "MAPPING_INVARIANT_FAILURE"},
    }
    checks["result_bounds_and_decision"] = (
        result["bounds"] == expected_bounds
        and result["overall_pass"] is False
        and result["status"] == "FINAL_MAPPING_INVARIANT_VISIBLE_SHAPE_TRANSFER_FAILURE_PROVENANCE_QUALIFIED"
        and result["decision"] == "CLOSE_FROZEN_SIX_FIELD_TRANSFER_ON_TWO_MAPPING_INVARIANT_GATES"
    )
    checks["result_counts_and_occurrences"] = (
        result["counts"] == {
            "crop_review_records": 26, "diagnostic_targets": 4, "match_eligible_reviews": 14,
            "primary_targets": 28, "primary_types": 7, "targets": 32,
            "unique_primary_prototype_signatures": 6,
            "unresolved_damaged_or_ambiguous_reviews": 12,
        }
        and result["mapping_invariant_prototype_occurrences"] == {str(key): value for key, value in occurrences.items()}
    )
    checks["scored_inputs_bound"] = all((ROOT / path).is_file() and sha(ROOT / path) == digest for path, digest in result["scored_inputs"].items())
    checks["unverified_mapping_artifacts_disclosed_and_bound"] = (
        result["access_limitations"] == {
            "private_selection_released_after_reviews_reported": True,
            "review_crop_delivery_manifest_available": False,
            "reviewer_history_and_inputs_independently_proven": False,
            "target_crop_binding_sealed_artifact_available": False,
        }
        and all((ROOT / path).is_file() and sha(ROOT / path) == digest for path, digest in result["disclosed_unverified_mapping_artifacts"].items())
    )
    checks["canonical_result"] = result_raw == (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode()
    checks["report_byte_exact_and_no_overclaim"] = (
        REPORT.read_text() == expected_report(result["status"])
        and "All three gates fail" not in REPORT.read_text()
        and "f79v.8" not in REPORT.read_text()
        and "Exactly 1/28" not in REPORT.read_text()
    )
    checks["claim_ceiling"] = all(term in result["claim_ceiling"] for term in ("preferred reading", "plaintext", "meaning", "translation"))

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit({name: checks[name] for name in failed})
    validation = {
        "check_count": len(checks),
        "checks": list(checks),
        "claim_ceiling": "Validation establishes only two mapping-invariant failures and an unverified localization interval; it supplies no preferred reading, allography, sound, alphabet, word, language, cipher, plaintext, meaning, or translation.",
        "experiment": "IGR002_MAPPING_INVARIANT_RESULT_VALIDATION",
        "mapping_invariant_bounds": {"exact_primary_matches_upper": exact_upper, "qualified_primary_types_upper": qualified_upper},
        "provenance_limit": "No contemporaneous sealed target-to-crop or reviewer-delivery manifest exists; target-level mappings and workflow chronology are not validated.",
        "result_sha256": sha(RESULT),
        "status": f"PASS_{len(checks)}_CHECK_MAPPING_INVARIANT_RECONSTRUCTION",
        "unverified_localization_interval": [minimum, maximum],
    }
    OUT.write_text(json.dumps(validation, sort_keys=True, separators=(",", ":")) + "\n")
    OUT_REPORT.write_text(
        f"# IGR002 mapping-invariant result validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        "Independent code ignores the unsealed target-level join. It reconstructs the unordered review-signature multiset, an exact-match upper bound of 1/28, a qualified-type upper bound of 0/7, and the unverified canvas-compatible localization interval 23–24/28. The first two bounds independently fail the conjunctive preregistered rule.\n\n"
        "The validation does not establish reviewer history, delivered inputs, sealing chronology, or any target-level match identity. No preferred reading, allography, sound, alphabet, word, language, cipher, plaintext, meaning, or translation follows.\n"
    )
    print(json.dumps(validation, sort_keys=True))


if __name__ == "__main__":
    main()
