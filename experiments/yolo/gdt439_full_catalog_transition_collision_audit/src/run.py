#!/usr/bin/env python3
"""Audit all 1,563 exact intake keys for state-transition collisions."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt439_full_catalog_transition_collision_audit"
OUT = BASE / "artifacts"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"
STREAM = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts/gdt436_4576_oracle_free_stream_readings.tsv"
GDT437_RUN = ROOT / "experiments/yolo/gdt437_future_card_state_transition_order_repair/src/run.py"
ORDERED_RENDERER = ROOT / "experiments/yolo/gdt437_future_card_state_transition_order_repair/src/ordered_renderer.py"
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    gdt437 = load_module("gdt437_transition_engine_for_full_catalog", GDT437_RUN)
    ordered = load_module("gdt437_ordered_renderer_for_full_catalog", ORDERED_RENDERER)
    catalog = sorted(read_tsv(CATALOG), key=lambda row: row["component_recipe"])
    states = sorted({(row["active_action_before"], row["active_argument_before"]) for row in read_tsv(STREAM)})

    full_vectors: dict[str, tuple[tuple[str, ...], ...]] = {}
    clause_vectors: dict[str, tuple[str, ...]] = {}
    state_vectors: dict[str, tuple[tuple[str, str], ...]] = {}
    sample_cells: dict[tuple[str, str], dict[str, str]] = {}
    signature_rows: list[dict[str, object]] = []
    for card in catalog:
        recipe = card["component_recipe"]
        atoms = recipe.split("+")
        full: list[tuple[str, ...]] = []
        clauses: list[str] = []
        outgoing_states: list[tuple[str, str]] = []
        repaired_cells = 0
        for incoming_action, incoming_argument in states:
            for register in REGISTERS:
                transition = gdt437.transition(ordered, atoms, register, incoming_action, incoming_argument)
                cell = (
                    register, incoming_action, incoming_argument,
                    transition["outgoing_action"], transition["outgoing_argument"],
                    transition["order_safe_clause_de"],
                )
                full.append(cell)
                clauses.append(transition["order_safe_clause_de"])
                outgoing_states.append((transition["outgoing_action"], transition["outgoing_argument"]))
                repaired_cells += transition["baseline_clause_de"] != transition["order_safe_clause_de"]
                if incoming_action == "OK" and incoming_argument == "Y":
                    sample_cells[(recipe, register)] = transition
        full_vector = tuple(full)
        clause_vector = tuple(clauses)
        state_vector = tuple(outgoing_states)
        full_vectors[recipe] = full_vector
        clause_vectors[recipe] = clause_vector
        state_vectors[recipe] = state_vector
        signature_rows.append({
            "component_recipe": recipe,
            "intake_tier": card["intake_tier"],
            "atom_count": len(atoms),
            "support_count": card["support_count"],
            "reachable_state_count": len(states),
            "register_count": len(REGISTERS),
            "transition_cell_count": len(full_vector),
            "order_repaired_cell_count": repaired_cells,
            "distinct_outgoing_state_count": len(set(state_vector)),
            "distinct_clause_count": len(set(clause_vector)),
            "state_signature_sha256": digest(state_vector),
            "clause_signature_sha256": digest(clause_vector),
            "full_transition_signature_sha256": digest(full_vector),
        })
    write_tsv(OUT / "gdt439_1563_transition_signatures.tsv", signature_rows, list(signature_rows[0]))

    by_signature: dict[str, list[str]] = defaultdict(list)
    for row in signature_rows:
        by_signature[str(row["full_transition_signature_sha256"])].append(str(row["component_recipe"]))
    collision_sets = [sorted(recipes) for recipes in by_signature.values() if len(recipes) > 1]
    collision_sets.sort(key=lambda recipes: (-len(recipes), recipes))
    catalog_by_recipe = {row["component_recipe"]: row for row in catalog}
    collision_rows: list[dict[str, object]] = []
    membership_rows: list[dict[str, object]] = []
    sample_rows: list[dict[str, object]] = []
    for ordinal, recipes in enumerate(collision_sets, start=1):
        group_id = f"COLLISION{ordinal:04d}"
        atom_multisets = {tuple(sorted(recipe.split("+"))) for recipe in recipes}
        tiers = [catalog_by_recipe[recipe]["intake_tier"] for recipe in recipes]
        observed_counts = [int(catalog_by_recipe[recipe]["support_count"]) for recipe in recipes]
        collision_rows.append({
            "collision_group_id": group_id,
            "recipe_count": len(recipes),
            "component_recipes": "|".join(recipes),
            "intake_tiers": "|".join(tiers),
            "same_atom_multiset": "YES" if len(atom_multisets) == 1 else "NO",
            "combined_observed_event_count": sum(observed_counts),
            "full_transition_signature_sha256": digest(full_vectors[recipes[0]]),
            "exact_vector_equality": "YES" if all(full_vectors[recipe] == full_vectors[recipes[0]] for recipe in recipes[1:]) else "NO",
            "interpretation": "EXACT_KEY_REQUIRED__FLUENT_TRANSITION_NOT_BIJECTIVE",
        })
        for recipe in recipes:
            card = catalog_by_recipe[recipe]
            membership_rows.append({
                "collision_group_id": group_id,
                "component_recipe": recipe,
                "intake_tier": card["intake_tier"],
                "support_count": card["support_count"],
                "atom_multiset": "+".join(sorted(recipe.split("+"))),
                "literal_reading_de": card["literal_reading_de"],
                "generic_workshop_phrase_de": card["generic_workshop_phrase_de"],
            })
        for register in REGISTERS:
            transition = sample_cells[(recipes[0], register)]
            sample_rows.append({
                "collision_group_id": group_id,
                "register": register,
                "sample_incoming_action": "OK",
                "sample_incoming_argument": "Y",
                "shared_outgoing_action": transition["outgoing_action"],
                "shared_outgoing_argument": transition["outgoing_argument"],
                "shared_clause_de": transition["order_safe_clause_de"],
                "component_recipes": "|".join(recipes),
            })
    write_tsv(OUT / "gdt439_collision_groups.tsv", collision_rows, list(collision_rows[0]) if collision_rows else ["collision_group_id"])
    write_tsv(OUT / "gdt439_collision_members.tsv", membership_rows, list(membership_rows[0]) if membership_rows else ["collision_group_id"])
    write_tsv(OUT / "gdt439_collision_register_samples.tsv", sample_rows, list(sample_rows[0]) if sample_rows else ["collision_group_id"])

    multiset_groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for recipe in full_vectors:
        multiset_groups[tuple(sorted(recipe.split("+")))].append(recipe)
    permutation_rows: list[dict[str, object]] = []
    for multiset, recipes in sorted(multiset_groups.items()):
        if len(recipes) < 2:
            continue
        for left, right in itertools.combinations(sorted(recipes), 2):
            permutation_rows.append({
                "atom_multiset": "+".join(multiset),
                "left_recipe": left,
                "right_recipe": right,
                "same_full_transition_signature": "YES" if full_vectors[left] == full_vectors[right] else "NO",
                "same_clause_signature": "YES" if clause_vectors[left] == clause_vectors[right] else "NO",
                "same_state_signature": "YES" if state_vectors[left] == state_vectors[right] else "NO",
                "left_tier": catalog_by_recipe[left]["intake_tier"],
                "right_tier": catalog_by_recipe[right]["intake_tier"],
            })
    write_tsv(OUT / "gdt439_order_permutation_pairs.tsv", permutation_rows, list(permutation_rows[0]) if permutation_rows else ["atom_multiset"])

    collision_members = {recipe for recipes in collision_sets for recipe in recipes}
    tier_rows: list[dict[str, object]] = []
    for tier in sorted({row["intake_tier"] for row in catalog}):
        tier_recipes = [row["component_recipe"] for row in catalog if row["intake_tier"] == tier]
        tier_rows.append({
            "intake_tier": tier,
            "recipe_count": len(tier_recipes),
            "unique_full_signature_count_within_tier": len({digest(full_vectors[recipe]) for recipe in tier_recipes}),
            "collision_member_count_global": sum(recipe in collision_members for recipe in tier_recipes),
            "collision_free_recipe_count_global": sum(recipe not in collision_members for recipe in tier_recipes),
            "order_repaired_recipe_count": sum(
                next(row for row in signature_rows if row["component_recipe"] == recipe)["order_repaired_cell_count"] != 0
                for recipe in tier_recipes
            ),
        })
    write_tsv(OUT / "gdt439_tier_summary.tsv", tier_rows, list(tier_rows[0]))

    main_tiers = {"T1_FUTURE_HIGH", "T2_FUTURE_STRONG", "T3_SECOND_RING_AMBER"}
    main_recipes = {row["component_recipe"] for row in catalog if row["intake_tier"] in main_tiers}
    main_collision_rows: list[dict[str, object]] = []
    for group in collision_rows:
        recipes = str(group["component_recipes"]).split("|")
        touching = sorted(main_recipes & set(recipes))
        if not touching:
            continue
        main_collision_rows.append({
            "collision_group_id": group["collision_group_id"],
            "main_future_recipes": "|".join(touching),
            "external_catalog_recipes": "|".join(sorted(set(recipes) - main_recipes)),
            "all_recipes": group["component_recipes"],
            "same_atom_multiset": group["same_atom_multiset"],
            "repair_route": "PRESERVE_TOP_LEVEL_WRITTEN_ORDER" if group["same_atom_multiset"] == "YES" else "PRESERVE_LOCAL_CHANNEL_CONTRAST",
            "main_internal_collision": "YES" if len(touching) > 1 else "NO",
        })
    write_tsv(OUT / "gdt439_main_deck_external_collisions.tsv", main_collision_rows, list(main_collision_rows[0]) if main_collision_rows else ["collision_group_id"])

    same_multiset_groups = sum(row["same_atom_multiset"] == "YES" for row in collision_rows)
    different_multiset_groups = len(collision_rows) - same_multiset_groups
    collision_pair_count = sum(len(recipes) * (len(recipes) - 1) // 2 for recipes in collision_sets)
    result = {
        "status": "MAIN_DECK_UNIQUE__FULL_CATALOG_COLLISIONS_LOCALIZED" if collision_sets else "FULL_CATALOG_TRANSITIONS_UNIQUE",
        "catalog_recipe_count": len(catalog),
        "reachable_state_count": len(states),
        "register_count": len(REGISTERS),
        "transition_cell_count": len(catalog) * len(states) * len(REGISTERS),
        "unique_full_transition_signature_count": len(by_signature),
        "collision_group_count": len(collision_sets),
        "collision_member_recipe_count": len(collision_members),
        "collision_free_recipe_count": len(catalog) - len(collision_members),
        "collision_recipe_pair_count": collision_pair_count,
        "largest_collision_group_size": max((len(recipes) for recipes in collision_sets), default=1),
        "same_multiset_collision_group_count": same_multiset_groups,
        "different_multiset_collision_group_count": different_multiset_groups,
        "main_future_card_count": len(main_recipes),
        "main_future_collision_member_count": len(main_recipes & collision_members),
        "main_external_collision_group_count": len(main_collision_rows),
        "main_internal_collision_group_count": sum(row["main_internal_collision"] == "YES" for row in main_collision_rows),
        "main_order_repair_candidate_count": sum(row["repair_route"] == "PRESERVE_TOP_LEVEL_WRITTEN_ORDER" for row in main_collision_rows),
        "main_local_channel_contrast_candidate_count": sum(row["repair_route"] == "PRESERVE_LOCAL_CHANNEL_CONTRAST" for row in main_collision_rows),
        "same_multiset_permutation_pair_count": len(permutation_rows),
        "same_multiset_full_collision_pair_count": sum(row["same_full_transition_signature"] == "YES" for row in permutation_rows),
        "order_repaired_recipe_count": sum(int(row["order_repaired_cell_count"]) > 0 for row in signature_rows),
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt439_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
