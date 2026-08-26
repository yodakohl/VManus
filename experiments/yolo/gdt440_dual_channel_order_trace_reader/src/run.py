#!/usr/bin/env python3
"""Build the dual-channel exact-order semantic reader and collision replay."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt440_dual_channel_order_trace_reader"
OUT = BASE / "artifacts"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"
SIGNATURES = ROOT / "experiments/yolo/gdt439_full_catalog_transition_collision_audit/artifacts/gdt439_1563_transition_signatures.tsv"
OLD_GROUPS = ROOT / "experiments/yolo/gdt439_full_catalog_transition_collision_audit/artifacts/gdt439_collision_groups.tsv"
OLD_MAIN = ROOT / "experiments/yolo/gdt439_full_catalog_transition_collision_audit/artifacts/gdt439_main_deck_external_collisions.tsv"
EVENTS = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts/gdt415_4576_event_owner_local_edition.tsv"
GDT438_EVENTS = ROOT / "experiments/yolo/gdt438_order_safe_streaming_reader/artifacts/gdt438_4576_order_safe_stream_readings.tsv"
DUAL_READER = BASE / "src/dual_channel_stream_read.py"


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


def digest(*parts: str) -> str:
    return hashlib.sha256(json.dumps(parts, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    catalog = {row["component_recipe"]: row for row in read_tsv(CATALOG)}
    signatures = read_tsv(SIGNATURES)
    old_groups = read_tsv(OLD_GROUPS)
    old_group_by_recipe = {
        recipe: row["collision_group_id"]
        for row in old_groups for recipe in row["component_recipes"].split("|")
    }

    signature_rows: list[dict[str, object]] = []
    dual_groups: dict[str, list[str]] = defaultdict(list)
    for row in signatures:
        recipe = row["component_recipe"]
        card = catalog[recipe]
        dual_hash = digest(row["full_transition_signature_sha256"], card["literal_reading_de"])
        dual_groups[dual_hash].append(recipe)
        signature_rows.append({
            "component_recipe": recipe,
            "intake_tier": card["intake_tier"],
            "ordered_literal_reading_de": card["literal_reading_de"],
            "fluent_transition_signature_sha256": row["full_transition_signature_sha256"],
            "dual_channel_signature_sha256": dual_hash,
            "gdt439_collision_group_id": old_group_by_recipe.get(recipe, "NONE"),
        })

    remaining_sets = [sorted(recipes) for recipes in dual_groups.values() if len(recipes) > 1]
    remaining_sets.sort(key=lambda values: (-len(values), values))
    dual_group_id: dict[str, str] = {}
    remaining_rows: list[dict[str, object]] = []
    for ordinal, recipes in enumerate(remaining_sets, start=1):
        group_id = f"DUALCOLLISION{ordinal:03d}"
        for recipe in recipes:
            dual_group_id[recipe] = group_id
        remaining_rows.append({
            "dual_collision_group_id": group_id,
            "recipe_count": len(recipes),
            "component_recipes": "|".join(recipes),
            "intake_tiers": "|".join(catalog[recipe]["intake_tier"] for recipe in recipes),
            "shared_ordered_literal_reading_de": catalog[recipes[0]]["literal_reading_de"],
            "source_gdt439_groups": "|".join(sorted({old_group_by_recipe[recipe] for recipe in recipes})),
            "same_atom_multiset": "YES" if len({tuple(sorted(recipe.split("+"))) for recipe in recipes}) == 1 else "NO",
            "interpretation": "CO_VALUED_LOCAL_CHANNELS__EXACT_CHANNEL_ID_RETAINED",
        })
    for row in signature_rows:
        row["dual_collision_group_id"] = dual_group_id.get(str(row["component_recipe"]), "NONE")
        row["dual_channel_status"] = "CO_VALUED_LOCAL_CHANNEL" if row["dual_collision_group_id"] != "NONE" else "DUAL_CHANNEL_UNIQUE"
    write_tsv(OUT / "gdt440_1563_dual_channel_signatures.tsv", signature_rows, list(signature_rows[0]))
    write_tsv(OUT / "gdt440_remaining_co_valued_channel_groups.tsv", remaining_rows, list(remaining_rows[0]))

    resolution_rows: list[dict[str, object]] = []
    for old in old_groups:
        recipes = old["component_recipes"].split("|")
        literal_groups: dict[str, list[str]] = defaultdict(list)
        for recipe in recipes:
            literal_groups[catalog[recipe]["literal_reading_de"]].append(recipe)
        unresolved_subgroups = [values for values in literal_groups.values() if len(values) > 1]
        if not unresolved_subgroups:
            status = "FULLY_RESOLVED_BY_ORDERED_MEANING_TRACE"
        elif len(literal_groups) == 1:
            status = "REMAINS_CO_VALUED_LOCAL_CHANNELS"
        else:
            status = "PARTLY_RESOLVED__REMAINDER_CO_VALUED_LOCAL_CHANNELS"
        resolution_rows.append({
            "gdt439_collision_group_id": old["collision_group_id"],
            "original_recipe_count": len(recipes),
            "component_recipes": old["component_recipes"],
            "distinct_ordered_literal_count": len(literal_groups),
            "remaining_dual_collision_subgroup_count": len(unresolved_subgroups),
            "remaining_recipe_count": len({recipe for values in unresolved_subgroups for recipe in values}),
            "resolution_status": status,
        })
    write_tsv(OUT / "gdt440_104_collision_resolutions.tsv", resolution_rows, list(resolution_rows[0]))

    main_rows: list[dict[str, object]] = []
    for row in read_tsv(OLD_MAIN):
        recipes = row["all_recipes"].split("|")
        readings = [catalog[recipe]["literal_reading_de"] for recipe in recipes]
        main_rows.append({
            **row,
            "ordered_literal_readings": " | ".join(f"{recipe}={reading}" for recipe, reading in zip(recipes, readings)),
            "dual_signature_distinct": "YES" if len({
                next(item["dual_channel_signature_sha256"] for item in signature_rows if item["component_recipe"] == recipe)
                for recipe in recipes
            }) == len(recipes) else "NO",
        })
    write_tsv(OUT / "gdt440_five_main_collision_resolutions.tsv", main_rows, list(main_rows[0]))

    reader = load_module("gdt440_dual_channel_reader", DUAL_READER)
    streamed = reader.stream_rows(read_tsv(EVENTS))
    baseline = {row["event_id"]: row for row in read_tsv(GDT438_EVENTS)}
    event_rows: list[dict[str, object]] = []
    for row in streamed:
        old = baseline[str(row["event_id"])]
        event_rows.append({
            "stream_ordinal": row["stream_ordinal"],
            "event_id": row["event_id"],
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "owner_de": row["owner_de"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "intake_tier": row["intake_tier"],
            "ordered_literal_reading_de": row["ordered_literal_reading_de"],
            "order_safe_clause_de": row["reader_clause_de"],
            "dual_channel_reading_de": row["dual_channel_reading_de"],
            "state_and_clause_match_gdt438": "YES" if all(
                row[field] == old[field] for field in (
                    "active_action_before", "active_argument_before", "active_action_after",
                    "active_argument_after", "reader_clause_de",
                )
            ) else "NO",
        })
    write_tsv(OUT / "gdt440_4576_dual_channel_stream_readings.tsv", event_rows, list(event_rows[0]))

    remaining_members = {recipe for values in remaining_sets for recipe in values}
    main_recipes = {row["component_recipe"] for row in catalog.values() if row["intake_tier"] in {"T1_FUTURE_HIGH", "T2_FUTURE_STRONG", "T3_SECOND_RING_AMBER"}}
    result = {
        "status": "ORDER_COLLISIONS_RESOLVED__CO_VALUED_LOCAL_CHANNELS_RETAINED",
        "catalog_recipe_count": len(catalog),
        "gdt439_fluent_signature_count": len({row["full_transition_signature_sha256"] for row in signatures}),
        "dual_channel_signature_count": len(dual_groups),
        "gdt439_collision_group_count": len(old_groups),
        "fully_resolved_old_group_count": sum(row["resolution_status"] == "FULLY_RESOLVED_BY_ORDERED_MEANING_TRACE" for row in resolution_rows),
        "partly_resolved_old_group_count": sum(row["resolution_status"].startswith("PARTLY") for row in resolution_rows),
        "unresolved_old_group_count": sum(row["resolution_status"] == "REMAINS_CO_VALUED_LOCAL_CHANNELS" for row in resolution_rows),
        "remaining_dual_collision_group_count": len(remaining_sets),
        "remaining_dual_collision_member_count": len(remaining_members),
        "remaining_same_multiset_collision_group_count": sum(row["same_atom_multiset"] == "YES" for row in remaining_rows),
        "main_future_card_count": len(main_recipes),
        "main_future_dual_collision_member_count": len(main_recipes & remaining_members),
        "main_external_contacts_resolved_count": sum(row["dual_signature_distinct"] == "YES" for row in main_rows),
        "current_event_count": len(event_rows),
        "current_state_and_clause_match_count": sum(row["state_and_clause_match_gdt438"] == "YES" for row in event_rows),
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt440_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
