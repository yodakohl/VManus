#!/usr/bin/env python3
"""Validate V76 R1 binding, competition, codebook ceiling and scope."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MATRIX = OUT / "V76_R1_14_UNIT_PURPOSE_MATRIX.tsv"
WORKFLOW = OUT / "V76_R1_PRODUCTION_WORKFLOW.tsv"
SCORE = OUT / "V76_R1_COMPETITION_SCORECARD.tsv"
CONTRA = OUT / "V76_R1_CONTRADICTION_LEDGER.tsv"
RESULT = OUT / "V76_R1_VALIDATION.json"
RULE = ROOT / "experiments/yolo/SIDEQUEST_CODEBOOK_ATTESTATION_RULE.md"

LEAD = "C1420_ILLUSTRATED_PRACTITIONER_BATH_AND_CELESTIAL_ELECTION_COMPENDIUM"
RIVAL = "C1420_NATURALIA_COSMOGRAPHIA_WORKSHOP_MODEL_AND_MEMORY_BOOK"
MNEMONIC_STATUS = "PROVISIONAL_UNATTESTED_MNEMONIC_OR_FORMAL_LABEL_NOT_WORD"
UNITS = [f"H{i}" for i in range(1, 6)] + [f"B{i}" for i in range(1, 7)] + [f"A{i}" for i in range(1, 4)]
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    matrix = read_tsv(MATRIX)
    workflow = read_tsv(WORKFLOW)
    scores = read_tsv(SCORE)
    contradictions = read_tsv(CONTRA)
    rule_text = RULE.read_text(encoding="utf-8")

    detail_cache: dict[str, list[dict[str, str]]] = {}
    for row in matrix:
        path = row["source_detail_file"]
        detail_cache.setdefault(path, read_tsv(ROOT / path))

    checks: dict[str, bool] = {}
    checks["exactly_14_units_in_frozen_order"] = len(matrix) == 14 and [r["unit_id"] for r in matrix] == UNITS
    checks["matrix_rows_exact_1_to_14"] = [int(r["matrix_row"]) for r in matrix] == list(range(1, 15))
    checks["section_unit_counts_exact"] = Counter(r["section"] for r in matrix) == {"HERBAL": 5, "BIOLOGICAL": 6, "ASTRO": 3}
    checks["same_ten_pages_exact"] = {r["page"] for r in matrix} == PAGES
    checks["bound_group_counts_exact_100_281_395"] = (
        sum(int(r["bound_group_count"]) for r in matrix if r["section"] == "HERBAL") == 100 and
        sum(int(r["bound_group_count"]) for r in matrix if r["section"] == "BIOLOGICAL") == 281 and
        sum(int(r["bound_group_count"]) for r in matrix if r["section"] == "ASTRO") == 395)
    checks["all_776_groups_bound"] = sum(int(r["bound_group_count"]) for r in matrix) == 776
    checks["source_files_exist_and_hashes_exact"] = all(
        (ROOT / r["source_summary_file"]).exists() and
        (ROOT / r["source_detail_file"]).exists() and
        r["source_detail_sha256"] == sha256(ROOT / r["source_detail_file"])
        for r in matrix)

    detailed_ok = True
    for row in matrix:
        rows = detail_cache[row["source_detail_file"]]
        key, value = row["source_unit_selector"].split("=", 1)
        selected = [r for r in rows if r[key] == value]
        detailed_ok &= len(selected) == int(row["bound_group_count"])
        detailed_ok &= selected and {r["page"] for r in selected} == {row["page"]}
        if row["section"] == "HERBAL":
            detailed_ok &= key == "record_unit_id" and row["bound_group_kind"] == "PROSE_EVENT"
        elif row["section"] == "BIOLOGICAL":
            detailed_ok &= key == "record_unit_id" and row["bound_group_kind"] == "PROSE_EVENT"
        else:
            detailed_ok &= key == "diagram_id" and row["bound_group_kind"] == "VISIBLE_ASTRO_GROUP"
    checks["every_unit_exactly_binds_selected_detail_rows"] = bool(detailed_ok)
    checks["no_row_level_retranslation_columns"] = not any(
        name in matrix[0] for name in ("surface_display_only", "joint_tuple_id", "concrete_german_meaning_in_context"))
    required = [
        "visible_owner_or_instrument_binding", "selected_v73_v75_content_binding",
        "lead_unit_role", "rival_unit_role", "practical_use_at_unit",
        "compilation_source_layer", "picture_first_production", "multiple_scribe_fit",
        "master_exemplar_dependency", "lead_intended_user", "rival_intended_user",
        "apprentice_lesson", "coexistence_explanation", "strongest_unit_contradiction",
    ]
    checks["all_purpose_fields_nonempty"] = all(all(r[k].strip() for k in required) for r in matrix)
    checks["same_lead_and_genuinely_different_rival_all_units"] = all(
        r["lead_book_purpose"] == LEAD and r["rival_book_purpose"] == RIVAL and
        r["lead_unit_role"] != r["rival_unit_role"] and
        r["lead_intended_user"] != r["rival_intended_user"] for r in matrix)
    checks["picture_first_multiple_scribe_master_exemplar_explicit"] = all(
        "VISIBLE_OWNER_OR_INSTRUMENT" in r["picture_first_production"] and
        "SECTION_TEMPLATE" in r["multiple_scribe_fit"] and
        r["master_exemplar_dependency"].startswith("HIGH__") for r in matrix)
    checks["codebook_rule_frozen_and_no_word_attested"] = (
        "Every admitted dictionary row must carry" in rule_text and
        "No surface resemblance" in rule_text and
        all(r["legacy_mnemonic_status"] == MNEMONIC_STATUS and
            r["qualifying_codebook_attestations"] == "0" for r in matrix))
    checks["semantic_ceiling_all_units"] = all(
        r["semantic_ceiling"] == "BOOK_PURPOSE_COMPETITION_NOT_WORD_MEANING_LANGUAGE_OR_TRANSLATION" for r in matrix)
    checks["workflow_exactly_12_ordered_steps"] = (
        len(workflow) == 12 and [int(r["step"]) for r in workflow] == list(range(1, 13)))
    checks["workflow_covers_sources_images_text_hands_exemplar_binding_apprentice"] = {
        r["production_phase"] for r in workflow
    } >= {"GATHER_INDEPENDENT_QUIRES", "PLAN_HERBAL_IMAGES", "ADD_HERBAL_TEXT",
          "PLAN_BIO_STATIONS", "ADD_BIO_TEXT", "PLAN_CELESTIAL_INSTRUMENTS",
          "ADD_CELESTIAL_LABELS", "SECTION_SPECIALIST_COPYING",
          "MASTER_EXEMPLAR_CHECK", "ASSEMBLE_OR_BIND", "APPRENTICE_USE"}
    checks["workflow_all_has_hard_reset_or_ceiling"] = all(r["hard_reset_or_ceiling"] for r in workflow)
    checks["scorecard_10_fixed_criteria_plus_total"] = (
        len(scores) == 11 and [r["score_id"] for r in scores[:-1]] == [f"S{i:02d}" for i in range(1, 11)] and
        scores[-1]["score_id"] == "TOTAL")
    lead_total = sum(int(r["lead_weighted"]) for r in scores[:-1])
    rival_total = sum(int(r["rival_weighted"]) for r in scores[:-1])
    max_total = 4 * sum(int(r["weight"]) for r in scores[:-1])
    checks["score_arithmetic_exact_and_rival_remains_live"] = (
        lead_total == int(scores[-1]["lead_weighted"]) == 96 and
        rival_total == int(scores[-1]["rival_weighted"]) == 92 and
        max_total == 108 and scores[-1]["score_status"] == "LEAD_SELECTED_NARROWLY; RIVAL_NOT_REJECTED")
    checks["score_explicitly_nonstatistical"] = all(
        r["score_status"] == "CREATIVE_COMPARISON_NOT_STATISTICAL_EVIDENCE" for r in scores[:-1])
    checks["contradiction_ledger_16_complete"] = (
        len(contradictions) == 16 and [r["contradiction_id"] for r in contradictions] == [f"C{i:02d}" for i in range(1, 17)])
    by_cid = {r["contradiction_id"]: r for r in contradictions}
    checks["hard_codebook_master_exemplar_coverage_pressures_retained"] = (
        by_cid["C12"]["remaining_status"] == "HARD_CEILING" and
        by_cid["C15"]["remaining_status"] == "OPEN_HIGH_COST" and
        by_cid["C16"]["remaining_status"] == "HARD_CEILING")
    checks["no_contradiction_promotes_dictionary_word"] = all(
        r["dictionary_effect"] in {MNEMONIC_STATUS, "NO_PORTABLE_WORD_LICENSE"} for r in contradictions)
    checks["no_exact_codebook_attestation_supplied_or_hunted"] = not any(
        key in matrix[0] for key in ("codebook_shelfmark", "codebook_entry", "codebook_sign", "codebook_folio"))

    status = "PASS" if all(checks.values()) else "FAIL"
    result = {
        "experiment": "V76_R1_HISTORICAL_BOOK_PURPOSE_COMPETITION",
        "status": status,
        "selection": {
            "lead": LEAD,
            "strongest_genuinely_different_rival": RIVAL,
            "lead_weighted_score": lead_total,
            "rival_weighted_score": rival_total,
            "maximum_weighted_score": max_total,
            "interpretation": "CREATIVE_C1420_BOOK_PURPOSE_COMPETITION_NOT_STATISTICAL_OR_TRANSLATION_EVIDENCE",
        },
        "counts": {
            "units": len(matrix),
            "bound_groups": sum(int(r["bound_group_count"]) for r in matrix),
            "herbal_groups": sum(int(r["bound_group_count"]) for r in matrix if r["section"] == "HERBAL"),
            "biological_groups": sum(int(r["bound_group_count"]) for r in matrix if r["section"] == "BIOLOGICAL"),
            "astro_groups": sum(int(r["bound_group_count"]) for r in matrix if r["section"] == "ASTRO"),
            "pages": len({r["page"] for r in matrix}),
            "workflow_steps": len(workflow),
            "score_criteria": len(scores) - 1,
            "contradictions": len(contradictions),
            "qualifying_codebook_attestations": 0,
        },
        "checks": checks,
        "constraints": {
            "new_card_stem_sound_language_or_dictionary_word": False,
            "legacy_mnemonic_promoted": False,
            "desired_codebook_word_hunt": False,
            "new_row_translation": False,
            "new_pages_read": False,
            "f84_or_f84r_opened": False,
            "active_v76_sibling_output_read": False,
            "commit_or_push": False,
        },
    }
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
