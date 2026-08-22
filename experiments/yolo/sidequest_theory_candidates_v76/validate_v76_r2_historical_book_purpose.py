#!/usr/bin/env python3
"""Validate V76 R2 counts, provenance, ceilings, and attestation guards."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v76"
VALIDATION = OUT / "V76_R2_VALIDATION.json"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check(condition: bool, label: str, checks: list[dict[str, object]]) -> None:
    checks.append({"check": label, "pass": bool(condition)})


def main() -> None:
    checks: list[dict[str, object]] = []
    required = [
        "V76_R2_HISTORICAL_BOOK_PURPOSE_REPORT.md",
        "V76_R2_776_GROUP_PURPOSE_BINDING.tsv",
        "V76_R2_14_UNIT_PURPOSE_SCORECARD.tsv",
        "V76_R2_BOOK_PURPOSE_COMPETITION.tsv",
        "V76_R2_HISTORICAL_SOURCE_AUDIT.tsv",
        "V76_R2_PRODUCTION_WORKFLOW.tsv",
        "V76_R2_CONTRADICTIONS.tsv",
        "V76_R2_BUILD_SUMMARY.json",
        "build_v76_r2_historical_book_purpose.py",
        "validate_v76_r2_historical_book_purpose.py",
    ]
    check(all((OUT / name).is_file() for name in required), "required_artifacts_exist", checks)

    bindings = read_tsv("V76_R2_776_GROUP_PURPOSE_BINDING.tsv")
    score = read_tsv("V76_R2_14_UNIT_PURPOSE_SCORECARD.tsv")
    purposes = read_tsv("V76_R2_BOOK_PURPOSE_COMPETITION.tsv")
    sources = read_tsv("V76_R2_HISTORICAL_SOURCE_AUDIT.tsv")
    workflow = read_tsv("V76_R2_PRODUCTION_WORKFLOW.tsv")
    contradictions = read_tsv("V76_R2_CONTRADICTIONS.tsv")
    report = (OUT / "V76_R2_HISTORICAL_BOOK_PURPOSE_REPORT.md").read_text(encoding="utf-8")
    summary = json.loads((OUT / "V76_R2_BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    check(len(bindings) == 776, "exactly_776_group_bindings", checks)
    check([int(r["binding_serial"]) for r in bindings] == list(range(1, 777)), "binding_serials_complete", checks)
    check(len({r["binding_id"] for r in bindings}) == 776, "binding_ids_unique", checks)
    check(all(r["opaque_identity"] and r["source_row_id"] for r in bindings), "all_bindings_have_opaque_identity_and_source_row", checks)

    expected_units = {
        "H1": 14, "H2": 24, "H3": 17, "H4": 18, "H5": 27,
        "B1": 66, "B2": 62, "B3": 86, "B4": 47, "B5": 11, "B6": 9,
        "A1": 190, "A2": 65, "A3": 140,
    }
    check(Counter(r["unit_id"] for r in bindings) == Counter(expected_units), "all_14_unit_counts_exact", checks)
    check(Counter(r["section"] for r in bindings) == Counter({"HERBAL": 100, "BIO": 281, "ASTRO": 395}), "section_counts_100_281_395", checks)

    fixed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
    check({r["page"] for r in bindings} == fixed_pages, "only_fixed_ten_pages", checks)
    allowed_sources = {
        "V73_SELECTED_100_EVENT_INTERLINEAR.tsv",
        "V74_SELECTED_281_EVENT_INTERLINEAR.tsv",
        "V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv",
    }
    check({r["source_artifact"] for r in bindings} == allowed_sources, "only_frozen_central_v73_v75_event_sources", checks)
    check(all(r["binding_status"] == "INHERITED_FROM_FROZEN_SELECTED_SECTION__NO_NEW_GROUP_VALUE" for r in bindings), "no_new_group_values", checks)
    check(all(r["codebook_attestation_status"] == "NO_DICTIONARY_GLOSS_ADDED" for r in bindings), "no_dictionary_gloss_added", checks)
    check(all("BOOK_PURPOSE_LEVEL_ONLY" in r["cross_unit_inference_status"] for r in bindings), "purpose_only_no_group_transfer", checks)

    literal_blob = "\n".join(r["inherited_literal_or_formal_layer"] for r in bindings)
    check(re.search(r"(?<!OPAQUE_)\[CARD:", literal_blob) is None, "old_word_mnemonics_redacted", checks)
    check("EXACT_WORKING_MNEMONIC" not in "\n".join(r["inherited_source_status"] for r in bindings), "old_mnemonic_statuses_downgraded", checks)
    check("EXACT_MNEMONIC_AND" not in "\n".join(r["inherited_source_status"] for r in bindings), "combined_mnemonic_statuses_downgraded", checks)

    check(len(score) == 14 and {r["unit_id"] for r in score} == set(expected_units), "fourteen_unit_scorecard_complete", checks)
    check(sum(int(r["group_count"]) for r in score) == 776, "scorecard_group_counts_sum_776", checks)
    check(sum(int(r["A_total_0_20"]) for r in score) == 236, "purpose_A_total_236", checks)
    check(sum(int(r["B_total_0_20"]) for r in score) == 235, "purpose_B_total_235", checks)
    component_cols = [
        "A_visual_fit_0_4", "A_selected_section_fit_0_4", "A_period_mechanism_support_0_4",
        "A_book_coexistence_fit_0_4", "A_production_fit_0_4",
        "B_visual_fit_0_4", "B_selected_section_fit_0_4", "B_period_mechanism_support_0_4",
        "B_book_coexistence_fit_0_4", "B_production_fit_0_4",
    ]
    check(all(0 <= int(r[c]) <= 4 for r in score for c in component_cols), "all_ordinal_components_in_0_4", checks)

    check(len(purposes) == 2, "exactly_two_genuinely_competing_purposes", checks)
    check({r["purpose_id"] for r in purposes} == {
        "A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM",
        "B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK",
    }, "purpose_ids_exact", checks)
    check({int(r["ordinal_total"]) for r in purposes} == {235, 236}, "purpose_totals_match_scorecard", checks)

    check(len(sources) == 12, "twelve_compact_historical_comparators", checks)
    check(len({r["source_id"] for r in sources}) == 12, "historical_source_ids_unique", checks)
    check(all(r["official_url"].startswith("https://") for r in sources), "all_sources_have_institutional_https_links", checks)
    check(all(r["codebook_or_lexical_use"] == "NONE__MECHANISM_CALIBRATION_ONLY" for r in sources), "sources_used_only_for_mechanisms", checks)
    check(all("NOT_DONOR" in r["audit_status"] for r in sources), "comparators_not_claimed_as_donors", checks)
    check(Counter(r["date_window_status"] for r in sources) == Counter({
        "WITHIN_OR_OVERLAPPING_C1370_1450": 11,
        "BROAD_14C_TRANSMISSION_BACKGROUND": 1,
    }), "source_date_window_explicit_11_period_plus_1_background", checks)

    check(len(workflow) == 7 and [int(r["stage"]) for r in workflow] == list(range(1, 8)), "seven_stage_production_comparison", checks)
    check(len(contradictions) == 16, "sixteen_explicit_contradictions", checks)
    check({r["model"] for r in contradictions} == {
        "A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM",
        "B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK",
        "SHARED",
    }, "contradictions_cover_both_models_and_shared_guards", checks)

    check("NEAR_TIE__A_PRACTICAL_COHERENCE__B_VISIBLE_PRODUCTION_ECONOMY" in report, "report_states_near_tie", checks)
    check("NO_DICTIONARY_GLOSS_ADDED" in report, "report_states_attestation_ceiling", checks)
    check("A 236 : B 235" in report, "report_states_totals", checks)
    check(all(unit in report for unit in expected_units), "report_mentions_all_14_units", checks)
    check(report.count("https://") >= 10, "report_has_compact_authoritative_source_links", checks)

    r2_files = list(OUT.glob("V76_R2_*")) + [OUT / "build_v76_r2_historical_book_purpose.py"]
    r2_blob = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in r2_files if path.is_file() and path != VALIDATION)
    check(not any(tag in r2_blob for tag in ("V76_R1_", "V76_R3_", "V76_R4_")), "no_active_v76_sibling_artifact_dependency", checks)
    check(summary.get("groups_bound") == 776 and summary.get("units") == 14, "build_summary_counts_match", checks)
    check(summary.get("dictionary_glosses_added") == 0 and summary.get("codebook_entries_claimed") == 0, "build_summary_attestation_zero", checks)
    check(summary.get("f84_access") is False and summary.get("f84r_access") is False, "f84_and_f84r_reported_sealed", checks)

    passed = all(item["pass"] for item in checks)
    result = {
        "status": "PASS" if passed else "FAIL",
        "checks_passed": sum(bool(item["pass"]) for item in checks),
        "checks_total": len(checks),
        "fixed_units": 14,
        "bound_groups": 776,
        "purpose_A_total": 236,
        "purpose_B_total": 235,
        "competition_result": "NEAR_TIE__A_PRACTICAL_COHERENCE__B_VISIBLE_PRODUCTION_ECONOMY",
        "dictionary_glosses_added": 0,
        "codebook_entries_claimed": 0,
        "f84_access": False,
        "f84r_access": False,
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "checks_passed", "checks_total", "bound_groups")}, ensure_ascii=False))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
