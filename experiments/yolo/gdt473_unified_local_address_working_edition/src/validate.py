#!/usr/bin/env python3
"""Validate GDT473 and check a deterministic rebuild."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt473_unified_local_address_working_edition"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
VALIDATION = OUT / "gdt473_validation.json"
G459 = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas/artifacts/gdt459_183_address_interlinear.tsv"
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake/artifacts/gdt466_107_intake_dictionary.tsv"
G472 = ROOT / "experiments/yolo/gdt472_complete_address_template_dictionary/artifacts/gdt472_107_complete_template_assignments.tsv"
EDITION = OUT / "gdt473_183_unified_address_working_edition.tsv"
SURFACES = OUT / "gdt473_162_surface_consistency.tsv"
PAGES = OUT / "gdt473_6_page_summary.tsv"
COVERAGE = OUT / "gdt473_4_coverage_class_summary.tsv"
READABLE = OUT / "GDT473_COMPLETE_WORKING_EDITION.md"
RESULT = OUT / "gdt473_result.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [EDITION, SURFACES, PAGES, COVERAGE, READABLE, RESULT]
    check("all_outputs_present", all(path.is_file() for path in generated), [path.name for path in generated])
    if not all(path.is_file() for path in generated):
        raise RuntimeError("Run GDT473 builder before validation")

    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    source = read_tsv(G459)
    dictionary = read_tsv(G466)
    assignments = read_tsv(G472)
    edition = read_tsv(EDITION)
    surfaces = read_tsv(SURFACES)
    pages = read_tsv(PAGES)
    coverage = read_tsv(COVERAGE)
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("source_count_183", len(source) == 183, len(source))
    check("edition_count_183", len(edition) == 183, len(edition))
    check("source_event_order_exact", [r["source_event_id"] for r in edition] == [r["source_event_id"] for r in source], "ordered source_event_id")
    check("source_order_exact", [r["source_order"] for r in edition] == [r["source_order"] for r in source], "source_order")
    check("source_surfaces_exact", [r["surface"] for r in edition] == [r["surface"] for r in source], "surface")
    check("edition_ids_unique", len({r["edition_id"] for r in edition}) == 183, len({r["edition_id"] for r in edition}))
    check("source_event_ids_unique", len({r["source_event_id"] for r in edition}) == 183, len({r["source_event_id"] for r in edition}))

    source_by_event = {r["source_event_id"]: r for r in source}
    dict_by_event = {r["source_event_id"]: r for r in dictionary}
    assignment_by_event = {r["source_event_id"]: r for r in assignments}
    formula = [r for r in edition if r["edition_route"] == "GDT459_FORMULA_SIDE"]
    labels = [r for r in edition if r["edition_route"] == "GDT472_COMPLETE_LABEL_DICTIONARY"]
    check("formula_side_count_76", len(formula) == 76, len(formula))
    check("label_side_count_107", len(labels) == 107, len(labels))
    check("label_input_decks_107", len(dict_by_event) == len(assignment_by_event) == 107, [len(dict_by_event), len(assignment_by_event)])
    check("label_event_join_exact", {r["source_event_id"] for r in labels} == set(dict_by_event) == set(assignment_by_event), len(labels))
    check("formula_recipes_unchanged", all(r["working_recipe"] == source_by_event[r["source_event_id"]]["selected_recipe_or_whole_class"] for r in formula), "76/76")
    check("formula_readings_unchanged", all(r["working_reading_de"] == source_by_event[r["source_event_id"]]["short_default_de"] for r in formula), "76/76")
    check("label_recipes_exact_gdt472", all(r["working_recipe"] == assignment_by_event[r["source_event_id"]]["source_recipe"] for r in labels), "107/107")
    check("label_readings_exact_gdt472", all(r["working_reading_de"] == assignment_by_event[r["source_event_id"]]["source_reading_de"] for r in labels), "107/107")
    check("label_surface_templates_exact", all(r["surface_template"] == assignment_by_event[r["source_event_id"]]["surface_template"] for r in labels), "107/107")
    check("label_character_counts_exact_gdt466", all(
        r["function_character_count"] == dict_by_event[r["source_event_id"]]["known_function_character_count"]
        and r["learned_character_count"] == dict_by_event[r["source_event_id"]]["remaining_learned_character_count"]
        and r["surface_character_count"] == dict_by_event[r["source_event_id"]]["surface_character_count"]
        for r in labels
    ), "107/107")
    check("all_formula_characters_functional", all(r["function_character_count"] == r["surface_character_count"] and r["learned_character_count"] == "0" for r in formula), "76/76")
    check("all_character_accounts_close", all(int(r["function_character_count"]) + int(r["learned_character_count"]) == int(r["surface_character_count"]) for r in edition), "183/183")
    check("all_readings_nonempty", all(r["working_reading_de"] and r["working_reading_de"] != "NONE" for r in edition), "183/183")
    check("all_recipes_bounded", all(r["working_recipe"] for r in edition), "183/183")

    tier_counts = Counter(r["gdt459_decision_tier"] for r in edition)
    check("original_tier_counts", tier_counts == Counter({
        "A_EXACT_RUNNING_FORMULA": 61,
        "B_ATTESTED_RECIPE_NEW_SURFACE": 7,
        "C_SHORT_OR_REPEATED_COMPOSITION": 8,
        "D_OWNER_LEARNED_WHOLE_LABEL": 107,
    }), dict(tier_counts))
    cover_counts = Counter(r["coverage_class"] for r in edition)
    expected_coverage = Counter({
        "FULL_FUNCTION_FORMULA": 94,
        "HYBRID_FUNCTION_AND_LEARNED_NAME": 87,
        "OWNER_FAMILY_STRUCTURED_LEARNED_NAME": 1,
        "WHOLE_LEARNED_NAME": 1,
    })
    check("final_coverage_counts", cover_counts == expected_coverage, dict(cover_counts))
    mode_counts = Counter(r["edition_semantic_mode"] for r in edition)
    check("full_label_modes_16_plus_2", mode_counts["CALIBRATED_FULL_FUNCTION_FORMULA"] == 16 and mode_counts["EXACT_PACKAGE_ONLY_FULL_FORMULA"] == 2, dict(mode_counts))
    check("learned_label_modes_87_plus_1_plus_1", mode_counts["FUNCTION_SHELL_PLUS_LEARNED_NAME"] == 87 and mode_counts["OWNER_FAMILY_PLUS_LEARNED_NAME"] == 1 and mode_counts["WHOLE_LEARNED_NAME"] == 1, dict(mode_counts))

    check("surface_count_162", len(surfaces) == 162, len(surfaces))
    check("surface_event_total_183", sum(int(r["event_count"]) for r in surfaces) == 183, sum(int(r["event_count"]) for r in surfaces))
    repeated = [r for r in surfaces if int(r["event_count"]) > 1]
    check("duplicate_surface_count_16", len(repeated) == 16, len(repeated))
    check("duplicate_surface_event_count_37", sum(int(r["event_count"]) for r in repeated) == 37, sum(int(r["event_count"]) for r in repeated))
    check("surface_conflict_count_zero", all(r["consistency_status"] == "INVARIANT" for r in surfaces), [r["surface"] for r in surfaces if r["consistency_status"] != "INVARIANT"])
    check("duplicate_event_flags_exact", all((int(r["local_surface_event_count"]) > 1) == (r["duplicate_surface_status"] == "REPEATED_INVARIANT") for r in edition), "183/183")

    expected_pages = {"f17r": 2, "f71v": 22, "f72r": 96, "f77r": 11, "f88v": 14, "f89r": 38}
    check("page_rows_6", len(pages) == 6, len(pages))
    check("page_event_counts", {r["physical_page"]: int(r["event_count"]) for r in pages} == expected_pages, {r["physical_page"]: r["event_count"] for r in pages})
    check("no_new_pages", {r["physical_page"] for r in edition} == set(expected_pages), sorted({r["physical_page"] for r in edition}))
    check("sealed_pages_absent", not any(r["physical_page"].startswith("f84") for r in edition), sorted({r["physical_page"] for r in edition}))
    check("coverage_summary_four", len(coverage) == 4, len(coverage))
    check("coverage_summary_counts", {r["coverage_class"]: int(r["event_count"]) for r in coverage} == dict(expected_coverage), {r["coverage_class"]: r["event_count"] for r in coverage})

    exact = [r for r in edition if r["edition_semantic_mode"] == "EXACT_PACKAGE_ONLY_FULL_FORMULA"]
    check("exact_packages_only_ykyd_yddy", {r["surface"] for r in exact} == {"ykyd", "yddy"}, [r["surface"] for r in exact])
    check("exact_packages_nontransferable", all(r["transfer_scope"] == "NONTRANSFERABLE_EXACT_PACKAGE" and r["transferable_template"] == "NO" for r in exact), "2/2")
    check("other_label_templates_transferable", all(r["transferable_template"] == "YES" for r in labels if r not in exact), "105/105")

    check("result_status", result["status"] == "COMPLETE_183_EVENT_LOCAL_ADDRESS_WORKING_EDITION__94_FULL_FORMULAS_87_HYBRIDS_2_LEARNED_ONLY", result["status"])
    check("result_counts_match", result["source_event_count"] == 183 and result["distinct_surface_count"] == 162 and result["surface_conflict_count"] == 0, result)
    check("result_no_new_claims", result["new_page_count"] == result["new_component_meaning_count"] == result["new_surface_spelling_count"] == 0, "all zero")
    readable = READABLE.read_text(encoding="utf-8")
    check("readable_has_all_pages", all(f"## {page}" in readable for page in expected_pages), sorted(expected_pages))
    check("readable_mentions_all_surfaces", all(f"`{r['surface']}`" in readable for r in edition), "183 event surfaces represented")

    passed = sum(bool(row["pass"]) for row in checks)
    validation = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "details": checks,
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: validation[key] for key in ("status", "checks", "passed", "failed")}, sort_keys=True))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
