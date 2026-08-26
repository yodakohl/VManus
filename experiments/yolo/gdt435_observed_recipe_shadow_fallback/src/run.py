#!/usr/bin/env python3
"""Build the GDT435 context-safe shadow replay and fallback audit."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt435_observed_recipe_shadow_fallback"
OUT = BASE / "artifacts"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
DENSITY = ROOT / "experiments/yolo/gdt430_nineteen_core_paradigm_prediction_deck/artifacts/gdt430_4938_candidate_density.tsv"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fallback_rank(neighbors: int) -> str:
    if neighbors >= 4:
        return "REGENERATED_HIGH"
    if neighbors == 3:
        return "REGENERATED_STRONG"
    if neighbors == 2:
        return "REGENERATED_NARROW"
    if neighbors == 1:
        return "ONE_NEIGHBOR__STOP"
    return "NO_NEIGHBOR__STOP"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    clauses = read_tsv(CLAUSES)
    density_rows = read_tsv(DENSITY)
    catalog = read_tsv(CATALOG)
    catalog_map = {row["component_recipe"]: row for row in catalog}
    observed_density = {
        row["candidate_recipe"]: row for row in density_rows if row["current_status"] == "OBSERVED"
    }

    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_recipe_register: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    by_context: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        by_recipe[row["component_recipe"]].append(row)
        by_recipe_register[(row["component_recipe"], row["register"])].append(row)
        by_context[(
            row["component_recipe"], row["register"],
            row["inherited_action_root"], row["inherited_argument_root"],
        )].append(row)

    context_rows: list[dict[str, object]] = []
    context_id: dict[tuple[str, str, str, str], str] = {}
    for index, (key, rows) in enumerate(sorted(by_context.items()), start=1):
        clauses_here = sorted({row["imperative_clause_de"] for row in rows})
        context_id[key] = f"CTX{index:04d}"
        context_rows.append({
            "context_key_id": context_id[key],
            "component_recipe": key[0],
            "register": key[1],
            "inherited_action_root": key[2],
            "inherited_argument_root": key[3],
            "owner_count": len({row["owner_de"] for row in rows}),
            "event_count": len(rows),
            "distinct_clause_count": len(clauses_here),
            "unique_clause_de": clauses_here[0] if len(clauses_here) == 1 else "CONFLICT",
            "event_ids": "|".join(sorted(row["global_running_event_id"] for row in rows)),
        })
    write_tsv(OUT / "gdt435_2465_context_key_map.tsv", context_rows, list(context_rows[0]))

    ambiguity_rows: list[dict[str, object]] = []
    naive_mismatch_total = 0
    ambiguous_event_total = 0
    for (recipe, register), rows in sorted(by_recipe_register.items()):
        rows = sorted(rows, key=lambda row: row["global_running_event_id"])
        first = rows[0]
        clause_set = {row["imperative_clause_de"] for row in rows}
        state_keys = {
            (row["inherited_action_root"], row["inherited_argument_root"])
            for row in rows
        }
        mismatch_count = sum(row["imperative_clause_de"] != first["imperative_clause_de"] for row in rows)
        naive_mismatch_total += mismatch_count
        if len(clause_set) > 1:
            ambiguous_event_total += len(rows)
        ambiguity_rows.append({
            "component_recipe": recipe,
            "register": register,
            "event_count": len(rows),
            "owner_count": len({row["owner_de"] for row in rows}),
            "context_state_key_count": len(state_keys),
            "distinct_clause_count": len(clause_set),
            "context_required": "YES" if len(clause_set) > 1 else "NO",
            "naive_first_event_id": first["global_running_event_id"],
            "naive_first_clause_mismatch_count": mismatch_count,
            "safe_context_free_reading_de": catalog_map[recipe]["generic_workshop_phrase_de"],
        })
    write_tsv(OUT / "gdt435_1766_recipe_register_ambiguity.tsv", ambiguity_rows, list(ambiguity_rows[0]))

    replay_rows: list[dict[str, object]] = []
    for row in clauses:
        group = sorted(
            by_recipe_register[(row["component_recipe"], row["register"])],
            key=lambda item: item["global_running_event_id"],
        )
        first = group[0]
        key = (
            row["component_recipe"], row["register"],
            row["inherited_action_root"], row["inherited_argument_root"],
        )
        replay_rows.append({
            "event_id": row["global_running_event_id"],
            "statement_id": row["global_statement_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "inherited_action_root": row["inherited_action_root"],
            "inherited_argument_root": row["inherited_argument_root"],
            "catalog_tier": catalog_map[row["component_recipe"]]["intake_tier"],
            "recipe_register_clause_variant_count": len({item["imperative_clause_de"] for item in group}),
            "naive_first_event_id": first["global_running_event_id"],
            "naive_first_clause_matches_actual": "YES" if first["imperative_clause_de"] == row["imperative_clause_de"] else "NO",
            "context_key_id": context_id[key],
            "context_key_clause_unique": "YES" if len({item["imperative_clause_de"] for item in by_context[key]}) == 1 else "NO",
            "actual_context_clause_de": row["imperative_clause_de"],
        })
    write_tsv(OUT / "gdt435_4576_event_shadow_replay.tsv", replay_rows, list(replay_rows[0]))

    jackknife_rows: list[dict[str, object]] = []
    for recipe, rows in sorted(by_recipe.items()):
        density = observed_density.get(recipe)
        neighbors = int(density["source_neighbor_count"]) if density else 0
        rank = fallback_rank(neighbors)
        event_count = len(rows)
        single_event_outcome = "T0_EXACT_SURVIVES" if event_count > 1 else rank
        jackknife_rows.append({
            "component_recipe": recipe,
            "current_event_count": event_count,
            "current_page_count": len({row["physical_page"] for row in rows}),
            "current_register_count": len({row["register"] for row in rows}),
            "one_event_jackknife_outcome": single_event_outcome,
            "whole_recipe_deletion_fixed_reader_outcome": "T5_STOP__FIXED_PREDICTIVE_TIERS_ARE_DISJOINT",
            "regenerated_neighbor_count": neighbors,
            "regenerated_fallback_rank": rank,
            "regenerated_source_recipes": density["source_recipes"] if density else "NONE",
            "literal_reading_de": catalog_map[recipe]["literal_reading_de"],
        })
    write_tsv(OUT / "gdt435_1268_recipe_jackknife.tsv", jackknife_rows, list(jackknife_rows[0]))

    main_cards = [
        row for row in catalog
        if row["intake_tier"] in {"T1_FUTURE_HIGH", "T2_FUTURE_STRONG", "T3_SECOND_RING_AMBER"}
    ]
    reversal_rows: list[dict[str, object]] = []
    for row in sorted(main_cards, key=lambda item: item["component_recipe"]):
        reverse = "+".join(reversed(row["component_recipe"].split("+")))
        reverse_hit = catalog_map.get(reverse)
        reversal_rows.append({
            "component_recipe": row["component_recipe"],
            "original_tier": row["intake_tier"],
            "reversed_recipe": reverse,
            "order_relation": "PALINDROME_SAME_KEY" if reverse == row["component_recipe"] else "ORDER_CHANGED",
            "reversed_intake_tier": reverse_hit["intake_tier"] if reverse_hit else "T5_NO_LICENSED_RECIPE",
            "original_phrase_de": row["generic_workshop_phrase_de"],
            "reversed_phrase_de": reverse_hit["generic_workshop_phrase_de"] if reverse_hit else "NONE",
            "exact_key_keeps_distinct": "YES" if reverse == row["component_recipe"] or reverse_hit is None or reverse_hit["component_recipe"] != row["component_recipe"] else "NO",
        })
    write_tsv(OUT / "gdt435_49_order_reversal_controls.tsv", reversal_rows, list(reversal_rows[0]))

    phrase_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in catalog:
        phrase_groups[row["generic_workshop_phrase_de"]].append(row)
    collision_rows: list[dict[str, object]] = []
    for index, (phrase, rows) in enumerate(sorted(phrase_groups.items()), start=1):
        if len(rows) < 2:
            continue
        collision_rows.append({
            "collision_group_id": f"PC{len(collision_rows) + 1:03d}",
            "generic_workshop_phrase_de": phrase,
            "recipe_count": len(rows),
            "component_recipes": "|".join(sorted(row["component_recipe"] for row in rows)),
            "intake_tiers": "|".join(sorted({row["intake_tier"] for row in rows})),
            "matcher_rule": "EXACT_COMPONENT_RECIPE_ONLY__NEVER_PHRASE",
        })
    write_tsv(OUT / "gdt435_121_catalog_phrase_collisions.tsv", collision_rows, list(collision_rows[0]))

    context_conflicts = sum(int(row["distinct_clause_count"]) != 1 for row in context_rows)
    ambiguous_keys = sum(row["context_required"] == "YES" for row in ambiguity_rows)
    singleton_rows = [row for row in jackknife_rows if int(row["current_event_count"]) == 1]
    singleton_counts = Counter(row["one_event_jackknife_outcome"] for row in singleton_rows)
    all_recipe_counts = Counter(row["regenerated_fallback_rank"] for row in jackknife_rows)
    reversal_counts = Counter(row["reversed_intake_tier"] for row in reversal_rows)
    result = {
        "status": "CONTEXT_SAFE_READER_REQUIRED__49_CARD_DECK_UNCHANGED",
        "event_shadow_replay_count": len(replay_rows),
        "recipe_register_key_count": len(ambiguity_rows),
        "ambiguous_recipe_register_key_count": ambiguous_keys,
        "events_inside_ambiguous_recipe_register_keys": ambiguous_event_total,
        "naive_first_clause_mismatch_event_count": naive_mismatch_total,
        "context_state_key_count": len(context_rows),
        "context_state_conflict_count": context_conflicts,
        "single_event_jackknife_exact_survival_count": sum(int(row["current_event_count"]) for row in jackknife_rows if int(row["current_event_count"]) > 1),
        "singleton_recipe_count": len(singleton_rows),
        "singleton_dynamic_fallback_counts": dict(sorted(singleton_counts.items())),
        "all_recipe_dynamic_fallback_counts": dict(sorted(all_recipe_counts.items())),
        "main_card_reversal_counts": dict(sorted(reversal_counts.items())),
        "catalog_phrase_count": len(phrase_groups),
        "catalog_phrase_collision_group_count": len(collision_rows),
        "catalog_recipes_in_phrase_collisions": sum(int(row["recipe_count"]) for row in collision_rows),
        "main_future_card_count": len(main_cards),
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt435_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
