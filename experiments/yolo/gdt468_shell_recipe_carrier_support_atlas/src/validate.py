#!/usr/bin/env python3
"""Validate GDT468 and verify a byte-identical deterministic rebuild."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt468_shell_recipe_carrier_support_atlas"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
PHRASEBOOK_SOURCE = ROOT / "experiments/yolo/gdt467_bounded_shell_composition_atlas/artifacts/gdt467_2760_shell_phrasebook.tsv"
RUNNING_SOURCE = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
ADDRESS_SOURCE = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake/artifacts/gdt466_107_intake_dictionary.tsv"

ATLAS = OUT / "gdt468_2300_recipe_support_atlas.tsv"
SHELLS = OUT / "gdt468_2760_supported_shell_phrasebook.tsv"
FACTORS = OUT / "gdt468_423_factorization_family_support.tsv"
CARRIERS = OUT / "gdt468_old_recipe_carriers.tsv"
RESULT = OUT / "gdt468_result.json"
VALIDATION = OUT / "gdt468_validation.json"
GENERATED = (ATLAS, SHELLS, FACTORS, CARRIERS, RESULT)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    phrasebook = read_tsv(PHRASEBOOK_SOURCE)
    running = read_tsv(RUNNING_SOURCE)
    addresses = read_tsv(ADDRESS_SOURCE)
    atlas = read_tsv(ATLAS)
    shells = read_tsv(SHELLS)
    factors = read_tsv(FACTORS)
    carriers = read_tsv(CARRIERS)
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("phrasebook_source_count", len(phrasebook) == 2760 and len({row["flattened_recipe_trace"] for row in phrasebook}) == 2300, "2760/2300")
    check("running_source_count", len(running) == 4576, f"observed={len(running)}")
    check("address_source_count", len(addresses) == 107, f"observed={len(addresses)}")
    running_surface_recipe: dict[str, str] = {}
    invariant = True
    for row in running:
        previous = running_surface_recipe.setdefault(row["surface"], row["component_recipe"])
        invariant &= previous == row["component_recipe"]
    check("running_surface_invariance", invariant, "one recipe per surface")

    recipe_set = {row["flattened_recipe_trace"] for row in phrasebook}
    source_shells: dict[str, list[dict[str, str]]] = defaultdict(list)
    source_running: dict[str, list[dict[str, str]]] = defaultdict(list)
    source_full: dict[str, list[dict[str, str]]] = defaultdict(list)
    source_hybrid: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in phrasebook:
        source_shells[row["flattened_recipe_trace"]].append(row)
    for row in running:
        if row["component_recipe"] in recipe_set:
            source_running[row["component_recipe"]].append(row)
    for row in addresses:
        recipe = row["ordered_function_recipe_trace"]
        if recipe not in recipe_set:
            continue
        if row["gdt466_hybrid_status"] == "FULL_FUNCTION_FORMULA":
            source_full[recipe].append(row)
        elif int(row["known_function_character_count"]) > 0:
            source_hybrid[recipe].append(row)

    check("atlas_count", len(atlas) == 2300 and len({row["flattened_recipe_trace"] for row in atlas}) == 2300, f"observed={len(atlas)}")
    check("atlas_ids", [row["recipe_id"] for row in atlas] == [f"G468-R{i:04d}" for i in range(1, 2301)], "R0001-R2300")
    check("atlas_recipe_set", {row["flattened_recipe_trace"] for row in atlas} == recipe_set, "complete phrasebook recipe set")
    check("atlas_ranks", {int(row["support_rank"]) for row in atlas} == set(range(1, 2301)), "one rank each")
    tier_counts = Counter(row["support_tier"] for row in atlas)
    check("atlas_tier_counts", tier_counts == Counter({"RUNNING_EXACT_RECIPE": 75, "ADDRESS_FULL_FORMULA_ONLY": 14, "ADDRESS_HYBRID_SHELL_ONLY": 14, "COMPOSITION_ONLY": 2197}), str(tier_counts))

    metrics_ok = True
    tier_ok = True
    shell_trace_ok = True
    for row in atlas:
        recipe = row["flattened_recipe_trace"]
        recipe_shells = source_shells[recipe]
        run_rows = source_running.get(recipe, [])
        full_rows = source_full.get(recipe, [])
        hybrid_rows = source_hybrid.get(recipe, [])
        run_surfaces = {item["surface"] for item in run_rows}
        run_pages = {item["physical_page"] for item in run_rows}
        metrics_ok &= (
            int(row["shell_factorization_count"]) == len(recipe_shells)
            and int(row["running_surface_type_count"]) == len(run_surfaces)
            and int(row["running_event_count"]) == len(run_rows)
            and int(row["running_page_count"]) == len(run_pages)
            and int(row["address_full_formula_count"]) == len(full_rows)
            and int(row["address_hybrid_shell_count"]) == len(hybrid_rows)
        )
        expected_tier = "RUNNING_EXACT_RECIPE" if run_rows else "ADDRESS_FULL_FORMULA_ONLY" if full_rows else "ADDRESS_HYBRID_SHELL_ONLY" if hybrid_rows else "COMPOSITION_ONLY"
        tier_ok &= row["support_tier"] == expected_tier
        shell_trace_ok &= (
            row["shell_ids"].split("|") == [item["shell_id"] for item in recipe_shells]
            and row["surface_templates"].split("|") == [item["surface_template"] for item in recipe_shells]
            and row["exact_channel_signatures"].split("|") == [item["exact_channel_signature"] for item in recipe_shells]
        )
    check("atlas_source_metrics", metrics_ok, "all counts recomputed")
    check("atlas_tier_precedence", tier_ok, "running > full address > hybrid shell > composition")
    check("atlas_shell_traces", shell_trace_ok, "all factorization lists exact")

    tier_order = {"RUNNING_EXACT_RECIPE": 0, "ADDRESS_FULL_FORMULA_ONLY": 1, "ADDRESS_HYBRID_SHELL_ONLY": 2, "COMPOSITION_ONLY": 3}
    ranked = sorted(
        atlas,
        key=lambda row: (
            tier_order[row["support_tier"]], -int(row["running_page_count"]), -int(row["running_event_count"]),
            -int(row["address_full_formula_count"]), -int(row["address_hybrid_shell_count"]),
            -int(row["shell_factorization_count"]), row["flattened_recipe_trace"],
        ),
    )
    check("atlas_rank_order", all(int(row["support_rank"]) == rank for rank, row in enumerate(ranked, start=1)), "rank formula exact")
    check("atlas_top_recipe", ranked[0]["flattened_recipe_trace"] == "OK+Y" and ranked[0]["running_event_count"] == "59" and ranked[0]["running_page_count"] == "18", str(ranked[0]))
    check("atlas_old_carrier_recipes", sum(row["support_tier"] != "COMPOSITION_ONLY" for row in atlas) == 103, "103")
    check("atlas_composition_only", sum(row["support_tier"] == "COMPOSITION_ONLY" for row in atlas) == 2197, "2197")

    check("shell_output_count", len(shells) == 2760, f"observed={len(shells)}")
    phrase_fields = list(phrasebook[0])
    check("shell_output_source_fields", all(all(row[field] == source[field] for field in phrase_fields) for row, source in zip(shells, phrasebook)), "phrasebook unchanged")
    atlas_map = {row["flattened_recipe_trace"]: row for row in atlas}
    check("shell_output_join", all(row["recipe_id"] == atlas_map[row["flattened_recipe_trace"]]["recipe_id"] and row["support_tier"] == atlas_map[row["flattened_recipe_trace"]]["support_tier"] and row["support_rank"] == atlas_map[row["flattened_recipe_trace"]]["support_rank"] for row in shells), "all support joins exact")
    shell_tiers = Counter(row["support_tier"] for row in shells)
    check("shell_output_tiers", shell_tiers == Counter({"RUNNING_EXACT_RECIPE": 105, "ADDRESS_FULL_FORMULA_ONLY": 24, "ADDRESS_HYBRID_SHELL_ONLY": 18, "COMPOSITION_ONLY": 2613}), str(shell_tiers))
    check("shell_old_supported_count", sum(row["support_tier"] != "COMPOSITION_ONLY" for row in shells) == 147, "147")

    check("carrier_count", len(carriers) == 210, f"observed={len(carriers)}")
    carrier_layers = Counter(row["source_layer"] for row in carriers)
    check("carrier_layer_counts", carrier_layers == Counter({"GDT407_RUNNING_EXACT": 154, "GDT466_ADDRESS_FULL": 14, "GDT466_ADDRESS_HYBRID": 42}), str(carrier_layers))
    check("carrier_ids", [row["carrier_id"] for row in carriers] == [f"G468-C{i:04d}" for i in range(1, 211)], "C0001-C0210")
    check("carrier_recipe_ids", all(row["recipe_id"] == atlas_map[row["flattened_recipe_trace"]]["recipe_id"] for row in carriers), "all recipes linked")
    check("carrier_running_counts", sum(int(row["carrier_count"]) for row in carriers if row["source_layer"] == "GDT407_RUNNING_EXACT") == 757, "757 events")
    check("carrier_running_surfaces", len({row["carrier_surface"] for row in carriers if row["source_layer"] == "GDT407_RUNNING_EXACT"}) == 154, "154 types")
    check("carrier_address_counts", sum(int(row["carrier_count"]) for row in carriers if row["source_layer"] == "GDT466_ADDRESS_FULL") == 14 and sum(int(row["carrier_count"]) for row in carriers if row["source_layer"] == "GDT466_ADDRESS_HYBRID") == 42, "14/42")

    check("factor_count", len(factors) == 423, f"observed={len(factors)}")
    repeated_recipes = {row["flattened_recipe_trace"] for row in atlas if int(row["shell_factorization_count"]) > 1}
    check("factor_recipe_set", {row["flattened_recipe_trace"] for row in factors} == repeated_recipes and len(repeated_recipes) == 423, "all repeated recipes")
    check("factor_ids", [row["factorization_group_id"] for row in factors] == [f"G468-F{i:04d}" for i in range(1, 424)], "F0001-F0423")
    check("factor_rank_order", [int(row["support_rank"]) for row in factors] == sorted(int(row["support_rank"]) for row in factors), "support ranked")
    factor_tiers = Counter(row["support_tier"] for row in factors)
    check("factor_tier_counts", factor_tiers == Counter({"RUNNING_EXACT_RECIPE": 29, "ADDRESS_FULL_FORMULA_ONLY": 5, "ADDRESS_HYBRID_SHELL_ONLY": 4, "COMPOSITION_ONLY": 385}), str(factor_tiers))
    check("factor_join_fields", all(row["recipe_id"] == atlas_map[row["flattened_recipe_trace"]]["recipe_id"] and row["shell_factorization_count"] == atlas_map[row["flattened_recipe_trace"]]["shell_factorization_count"] and row["support_tier"] == atlas_map[row["flattened_recipe_trace"]]["support_tier"] for row in factors), "all atlas joins exact")
    check("factor_disposition", all(row["disposition"] == "KEEP_ALL_VISIBLE_FACTORIZATIONS__RANK_BY_SHARED_RECIPE_SUPPORT" for row in factors), "all traces retained")

    check("matched_running_events", sum(len(rows) for rows in source_running.values()) == 757, "757")
    check("matched_running_types", len({row["surface"] for rows in source_running.values() for row in rows}) == 154, "154")
    check("matched_running_pages", len({row["physical_page"] for rows in source_running.values() for row in rows}) == 24, "24")
    check("matched_address_labels", sum(len(rows) for rows in source_full.values()) == 14 and sum(len(rows) for rows in source_hybrid.values()) == 42, "14 full / 42 hybrid")

    check("result_status", result["status"] == "SHELL_RECIPES_SEPARATED_INTO_OLD_CARRIER_AND_COMPOSITION_TIERS", result["status"])
    check("result_source_counts", result["shell_count"] == 2760 and result["recipe_count"] == 2300 and result["running_event_count"] == 4576 and result["address_label_count"] == 107, str(result))
    check("result_recipe_tiers", result["recipe_support_tier_counts"] == dict(sorted(tier_counts.items())) and result["recipe_with_any_old_carrier_count"] == 103 and result["composition_only_recipe_count"] == 2197, str(result))
    check("result_shell_tiers", result["shell_support_tier_counts"] == dict(sorted(shell_tiers.items())), str(result["shell_support_tier_counts"]))
    check("result_carriers", result["matched_running_event_count"] == 757 and result["matched_running_surface_type_count"] == 154 and result["matched_running_page_count"] == 24 and result["matched_address_full_label_count"] == 14 and result["matched_address_hybrid_label_count"] == 42 and result["carrier_row_count"] == 210, str(result))
    check("result_factors", result["factorization_family_count"] == 423 and result["factorization_support_tier_counts"] == dict(sorted(factor_tiers.items())), str(result))
    check("result_top", result["top_supported_recipe"] == "OK+Y" and result["top_supported_running_event_count"] == 59 and result["top_supported_running_page_count"] == 18, str(result))
    check("result_claim_ceiling", result["new_pages"] == result["new_channels"] == result["new_component_meanings"] == result["surface_predictions"] == result["confirmed_lexemes"] == 0, "no expanded claim")
    check("sealed_pages_absent", all(not row.get("physical_page", "").startswith("f84") for table in (running, addresses) for row in table), "no sealed page rows")

    before = {path.name: sha256(path) for path in GENERATED}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    check("deterministic_rebuild_exit", completed.returncode == 0, completed.stderr[-500:] or "exit 0")
    after = {path.name: sha256(path) for path in GENERATED}
    check("deterministic_rebuild_bytes", before == after, "all generated artifact hashes unchanged")

    passed = sum(row["status"] == "PASS" for row in checks)
    failed = len(checks) - passed
    payload = {"status": "PASS" if failed == 0 else "FAIL", "check_count": len(checks), "passed": passed, "failed": failed, "checks": checks}
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "passed": passed, "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
