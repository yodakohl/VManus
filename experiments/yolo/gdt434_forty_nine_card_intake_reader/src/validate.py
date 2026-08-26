#!/usr/bin/env python3
"""Validate the GDT434 exact-recipe intake reader and its tier boundaries."""

from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
PREDICTIONS = ROOT / "experiments/yolo/gdt430_nineteen_core_paradigm_prediction_deck/artifacts/gdt430_293_absent_multi_neighbor_predictions.tsv"
REGISTERS = {"SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt434_1563_recipe_intake_catalog.tsv",
        OUT / "gdt434_245_main_card_register_readings.tsv",
        OUT / "gdt434_246_narrow_lookup_appendix.tsv",
        OUT / "gdt434_8_matcher_test_cases.tsv",
        OUT / "FORTY_NINE_CARD_INTAKE_SHEET.md",
        OUT / "gdt434_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    catalog = read_tsv(tracked[0])
    main_readings = read_tsv(tracked[1])
    narrow = read_tsv(tracked[2])
    tests = read_tsv(tracked[3])
    clauses = read_tsv(CLAUSES)
    predictions = read_tsv(PREDICTIONS)
    result = json.loads((OUT / "gdt434_result.json").read_text(encoding="utf-8"))

    tier_counts = Counter(row["intake_tier"] for row in catalog)
    recipes_by_tier: dict[str, set[str]] = defaultdict(set)
    for row in catalog:
        recipes_by_tier[row["intake_tier"]].add(row["component_recipe"])
    catalog_recipes = [row["component_recipe"] for row in catalog]
    observed_recipes = {row["component_recipe"] for row in clauses}
    narrow_source = {row["candidate_recipe"] for row in predictions if row["prediction_rank"] == "AMBER_NARROW"}
    main_recipes = {row["component_recipe"] for row in main_readings}
    main_counts = Counter(row["component_recipe"] for row in main_readings)
    generic_main = {
        row["component_recipe"]: row["generic_workshop_phrase_de"]
        for row in catalog if row["intake_tier"] in {"T1_FUTURE_HIGH", "T2_FUTURE_STRONG", "T3_SECOND_RING_AMBER"}
    }
    local_phrase_keys = [(row["register"], row["owner_local_workshop_phrase_de"]) for row in main_readings]
    narrow_collisions = [row for row in narrow if int(row["generic_phrase_collision_count"]) > 0]
    narrow_collision_groups = {
        tuple(sorted(row["generic_phrase_collision_recipes"].split("|"))) for row in narrow_collisions
    }

    test_results: list[dict[str, object]] = []
    for test in tests:
        completed = subprocess.run(
            [
                "python3", str(BASE / "src/read_recipe.py"),
                "--recipe", test["component_recipe"],
                "--register", test["register"],
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        test_results.append({
            "test_id": test["test_id"],
            "expected": test["expected_tier"],
            "actual": payload["intake_tier"],
            "status": payload["match_status"],
            "surface_prediction": payload["surface_prediction"],
        })

    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)
    tier_sets = list(recipes_by_tier.values())
    checks = {
        "catalog_rows_1563": len(catalog) == 1563,
        "catalog_recipe_keys_unique": len(catalog_recipes) == len(set(catalog_recipes)) == 1563,
        "tier_counts_exact": tier_counts == Counter({
            "T0_EXACT_OBSERVED": 1268,
            "T1_FUTURE_HIGH": 4,
            "T2_FUTURE_STRONG": 43,
            "T3_SECOND_RING_AMBER": 2,
            "T4_NARROW_APPENDIX": 246,
        }),
        "tiers_pairwise_disjoint": all(not tier_sets[i] & tier_sets[j] for i in range(len(tier_sets)) for j in range(i + 1, len(tier_sets))),
        "t0_matches_observed_inventory": recipes_by_tier["T0_EXACT_OBSERVED"] == observed_recipes,
        "t4_matches_narrow_source": recipes_by_tier["T4_NARROW_APPENDIX"] == narrow_source,
        "main_card_count_49": len(main_recipes) == 49,
        "main_register_rows_245": len(main_readings) == 245,
        "five_registers_per_main_card": all(main_counts[recipe] == 5 for recipe in main_recipes),
        "main_register_names_exact": {row["register"] for row in main_readings} == REGISTERS,
        "main_generic_phrases_unique": len(generic_main) == len(set(generic_main.values())) == 49,
        "main_local_phrases_unique_within_register": len(local_phrase_keys) == len(set(local_phrase_keys)) == 245,
        "narrow_rows_246": len(narrow) == 246 and len({row["component_recipe"] for row in narrow}) == 246,
        "narrow_exact_key_rule_everywhere": all(row["appendix_rule"] == "EXACT_RECIPE_KEY_REQUIRED__PHRASE_ALONE_NEVER_MATCHES" for row in narrow),
        "narrow_collision_recipes_8": len(narrow_collisions) == 8,
        "narrow_collision_groups_4": len(narrow_collision_groups) == 4 and all(len(group) == 2 for group in narrow_collision_groups),
        "matcher_test_rows_8": len(tests) == len(test_results) == 8,
        "matcher_tiers_exact": all(row["expected"] == row["actual"] for row in test_results),
        "matcher_never_predicts_surface": all(row["surface_prediction"] == "NONE" for row in test_results),
        "t5_tests_stop": all(str(row["status"]).endswith("__STOP") for row in test_results if row["expected"] == "T5_NO_LICENSED_RECIPE"),
        "result_status_exact": result["status"] == "EXECUTABLE_49_CARD_INTAKE_READER_WITH_SEPARATE_NARROW_APPENDIX",
        "result_counts_exact": result["catalog_recipe_count"] == 1563 and result["main_future_card_count"] == 49 and result["main_register_reading_count"] == 245 and result["narrow_appendix_count"] == 246,
        "result_collision_count_exact": result["narrow_generic_phrase_collision_recipe_count"] == 8,
        "no_new_values_pages_surfaces": result["surface_predictions"] == result["new_component_values"] == result["new_pages"] == 0,
        "all_surface_rules_refuse_invention": all("DO_NOT_INVENT_SURFACE" in row["surface_rule"] or row["intake_tier"] == "T0_EXACT_OBSERVED" for row in catalog),
        "no_forbidden_page_in_outputs": "f84" not in output_text.lower(),
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
        "matcher_tests": test_results,
    }
    (OUT / "gdt434_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
