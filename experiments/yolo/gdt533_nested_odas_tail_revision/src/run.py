#!/usr/bin/env python3
"""Prefer the nested exact odas tail for dairykodas."""

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
BASE = ROOT / "experiments/yolo/gdt533_nested_odas_tail_revision"
OUT = BASE / "artifacts"
OLD_RUNNING = (
    ROOT
    / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
    / "gdt407_4576_running_event_edition.tsv"
)
SIGNATURES = (
    ROOT
    / "experiments/yolo/gdt522_local_edit_analogy_license_reranker/artifacts"
    / "gdt522_local_edit_analogy_atlas.tsv"
)
CURRENT_EVENTS = (
    ROOT
    / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts"
    / "gdt516_597_contextualized_event_edition.tsv"
)
CANDIDATES = (
    ROOT
    / "experiments/yolo/gdt529_nearest_terminal_m_square/artifacts"
    / "gdt529_candidate_score_atlas.tsv"
)
CURRENT_WORKING = (
    ROOT
    / "experiments/yolo/gdt532_same_owner_exact_card_tiling_revision/artifacts"
    / "gdt532_159_working_revision.tsv"
)
CURRENT_RESULT = (
    ROOT
    / "experiments/yolo/gdt532_same_owner_exact_card_tiling_revision/artifacts"
    / "gdt532_result.json"
)
TILING_ROUTES = (
    ROOT
    / "experiments/yolo/gdt532_same_owner_exact_card_tiling_revision/artifacts"
    / "gdt532_residual_candidate_tiling_atlas.tsv"
)

SELECTED_SURFACE = "dairykodas"
SELECTED_RECIPE = "D_ADDR+AIR+Y+K+O+DA+S"
PREVIOUS_RECIPE = "D_ADDR+AIR+Y+K+O+D_ADDR+A_ADDR+S"
SELECTED_TILING = ("dair", "y", "k", "odas")
RIVAL_TILING = ("dair", "y", "kod", "as")
WORKING_LITERAL_DE = (
    "[D_ADDR:STEUERUNG=HIER] · BAHN · POSTEN · GEBEN · "
    "[O:STEUERUNG=AUSFÜHRUNG] · [DA+S:STEUERUNG=STUFE II WÄHLEN]"
)
WORKING_PHRASE_DE = (
    "Hier entlang der Bahn posten; zur Ausführung geben und Stufe II wählen."
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def exact_inventory(rows: list[dict[str, str]]) -> dict[str, dict]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["surface"]].append(row)
    inventory = {}
    for surface, surface_rows in grouped.items():
        recipes = {row["component_recipe"] for row in surface_rows}
        if len(recipes) != 1:
            continue
        inventory[surface] = {
            "recipe": next(iter(recipes)),
            "event_count": len(surface_rows),
            "pages": "|".join(sorted({row["physical_page"] for row in surface_rows})),
            "registers": "|".join(sorted({row["register"] for row in surface_rows})),
            "event_ids": "|".join(row["global_running_event_id"] for row in surface_rows),
            "loci": "|".join(row["locus"] for row in surface_rows),
        }
    return inventory


def pair_support(rows: list[dict[str, str]], left: str, right: str) -> dict:
    event_rows = []
    occurrence_count = 0
    for row in rows:
        atoms = row["component_recipe"].split("+")
        occurrences = sum(
            atoms[index : index + 2] == [left, right]
            for index in range(len(atoms) - 1)
        )
        if occurrences:
            event_rows.append(row)
            occurrence_count += occurrences
    return {
        "occurrence_count": occurrence_count,
        "event_count": len(event_rows),
        "surface_count": len({row["surface"] for row in event_rows}),
        "recipe_count": len({row["component_recipe"] for row in event_rows}),
        "page_count": len({row["physical_page"] for row in event_rows}),
        "register_count": len({row["register"] for row in event_rows}),
        "examples": " | ".join(
            f"{row['surface']}={row['component_recipe']}@{row['physical_page']}"
            for row in event_rows[:8]
        )
        or "NONE",
    }


def metric(rows: list[dict], field: str) -> dict[str, int]:
    ranks = [int(row[field]) for row in rows]
    return {
        "target_count": len(ranks),
        "truth_generated_count": len(ranks),
        "top1_exact_count": sum(rank <= 1 for rank in ranks),
        "top2_exact_count": sum(rank <= 2 for rank in ranks),
        "top3_exact_count": sum(rank <= 3 for rank in ranks),
        "top5_exact_count": sum(rank <= 5 for rank in ranks),
        "rank_sum": sum(ranks),
        "deepest_truth_rank": max(ranks),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(OLD_RUNNING)
    signatures = read_tsv(SIGNATURES)
    current_events = read_tsv(CURRENT_EVENTS)
    candidate_rows = read_tsv(CANDIDATES)
    current = read_tsv(CURRENT_WORKING)
    inherited_result = json.loads(CURRENT_RESULT.read_text(encoding="utf-8"))
    tiling_routes = [
        row for row in read_tsv(TILING_ROUTES) if row["surface"] == SELECTED_SURFACE
    ]
    inventory = exact_inventory(old)
    candidate_rank = {
        row["candidate_recipe"]: int(row["gdt529_rank"])
        for row in candidate_rows
        if row["surface"] == SELECTED_SURFACE
    }
    target_row = next(row for row in current if row["surface"] == SELECTED_SURFACE)

    routes_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tiling_routes:
        routes_by_recipe[row["candidate_recipe"]].append(row)

    selected_routes = routes_by_recipe[SELECTED_RECIPE]
    rival_routes = routes_by_recipe[PREVIOUS_RECIPE]
    preferred_selected = min(
        selected_routes,
        key=lambda row: (
            int(row["tile_count"]),
            -int(row["longest_tile_width"]),
            row["surface_tiling"],
        ),
    )
    preferred_rival = min(
        rival_routes,
        key=lambda row: (
            int(row["tile_count"]),
            -int(row["longest_tile_width"]),
            row["surface_tiling"],
        ),
    )

    tile_rows = []
    for route_label, tiling in (
        ("SELECTED_NESTED_ODAS", SELECTED_TILING),
        ("RIVAL_KOD_AS", RIVAL_TILING),
    ):
        for ordinal, surface in enumerate(tiling, start=1):
            card = inventory[surface]
            tile_rows.append(
                {
                    "route": route_label,
                    "tile_ordinal": ordinal,
                    "tile_surface": surface,
                    "tile_recipe": card["recipe"],
                    "old_event_count": card["event_count"],
                    "old_pages": card["pages"],
                    "old_registers": card["registers"],
                    "old_event_ids": card["event_ids"],
                    "old_loci": card["loci"],
                    "relation": (
                        "EXACT_TERMINAL_WHOLE_CARD"
                        if surface == "odas"
                        else "EXACT_ROUTE_CARD"
                    ),
                }
            )

    signature = next(
        row
        for row in signatures
        if row["visible_insert"] == "o"
        and row["visible_position"] == "LEFT"
        and row["atom_insert"] == "O"
        and row["atom_position"] == "LEFT"
    )
    nested_rows = []
    for surface, relation in (
        ("das", "INNER_STAGE_SELECTION_CARD"),
        ("odas", "EXACT_LEFT_O_SUPERFORM_AND_TARGET_SUFFIX"),
    ):
        card = inventory[surface]
        nested_rows.append(
            {
                "surface": surface,
                "recipe": card["recipe"],
                "old_event_count": card["event_count"],
                "old_pages": card["pages"],
                "old_registers": card["registers"],
                "old_event_ids": card["event_ids"],
                "relation": relation,
                "visible_derivation": "odas-o=das" if surface == "odas" else "BASE",
                "recipe_derivation": (
                    "O+DA+S-O=DA+S" if surface == "odas" else "BASE"
                ),
                "left_o_O_support": signature["support_pair_count"],
                "left_o_O_total": signature["visible_condition_total"],
                "left_o_O_probability": signature["conditional_probability"],
                "left_o_O_reliability": signature["reliability"],
                "left_o_O_examples": signature["examples"],
            }
        )

    pair_rows = []
    for route_label, recipe in (
        ("SELECTED_RANK1", SELECTED_RECIPE),
        ("RIVAL_RANK2", PREVIOUS_RECIPE),
    ):
        atoms = recipe.split("+")
        for ordinal, (left, right) in enumerate(zip(atoms, atoms[1:]), start=1):
            support = pair_support(old, left, right)
            pair = f"{left}+{right}"
            if pair == "DA+S":
                relation = "SELECTED_CRITICAL_STAGE_SELECTION_PAIR"
            elif pair == "D_ADDR+A_ADDR":
                relation = "RIVAL_CRITICAL_DOUBLE_ADDRESS_PAIR"
            elif ordinal <= 4:
                relation = "SHARED_PREFIX_PAIR"
            else:
                relation = "ROUTE_SPECIFIC_PAIR"
            pair_rows.append(
                {
                    "route": route_label,
                    "candidate_recipe": recipe,
                    "gdt529_rank": candidate_rank[recipe],
                    "pair_ordinal": ordinal,
                    "pair": pair,
                    **support,
                    "relation": relation,
                }
            )

    grouped_old: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in old:
        grouped_old[row["surface"]].append(row)
    as_ending_rows = []
    for surface, rows in sorted(grouped_old.items()):
        if not surface.endswith("as"):
            continue
        recipes = sorted({row["component_recipe"] for row in rows})
        as_ending_rows.append(
            {
                "surface": surface,
                "recipes": "|".join(recipes),
                "event_count": len(rows),
                "pages": "|".join(sorted({row["physical_page"] for row in rows})),
                "registers": "|".join(sorted({row["register"] for row in rows})),
                "ends_A_ADDR_S": "YES"
                if all(recipe.split("+")[-2:] == ["A_ADDR", "S"] for recipe in recipes)
                else "NO",
                "relation": (
                    "EXACT_RIVAL_AS_CARD"
                    if surface == "as"
                    else "VISIBLE_AS_ENDING_CONTROL"
                ),
            }
        )

    statement_rows = []
    for row in current_events:
        if row["statement_id"] != "G515-S042":
            continue
        statement_rows.append(
            {
                "event_id": row["event_id"],
                "physical_page": row["physical_page"],
                "locus": row["locus"],
                "card_ordinal_in_statement": row["card_ordinal_in_statement"],
                "surface": row["surface"],
                "recipe": row["gdt516_context_recipe"],
                "literal_reading_de": row["gdt516_literal_reading_de"],
                "relation": "TARGET" if row["surface"] == SELECTED_SURFACE else "CONTEXT",
            }
        )

    route_count_by_recipe = Counter(row["candidate_recipe"] for row in tiling_routes)
    selected_pair_counts = [
        int(row["occurrence_count"])
        for row in pair_rows
        if row["route"] == "SELECTED_RANK1"
    ]
    rival_pair_counts = [
        int(row["occurrence_count"])
        for row in pair_rows
        if row["route"] == "RIVAL_RANK2"
    ]
    comparison_rows = []
    for row in candidate_rows:
        if row["surface"] != SELECTED_SURFACE:
            continue
        recipe = row["candidate_recipe"]
        if recipe == SELECTED_RECIPE:
            decision = "SELECT_NESTED_EXACT_ODAS_TAIL"
            preferred = preferred_selected["surface_tiling"]
            respects_odas = "YES"
        elif recipe == PREVIOUS_RECIPE:
            decision = "REPLACE_RIVAL_SPLITS_EXACT_ODAS_TAIL"
            preferred = preferred_rival["surface_tiling"]
            respects_odas = "NO"
        else:
            decision = "RETAIN_ALTERNATIVE"
            preferred = "NONE"
            respects_odas = "NO"
        comparison_rows.append(
            {
                "surface": SELECTED_SURFACE,
                "candidate_recipe": recipe,
                "gdt529_rank": int(row["gdt529_rank"]),
                "exact_card_tiling_route_count": route_count_by_recipe[recipe],
                "preferred_surface_tiling": preferred,
                "preserves_exact_terminal_odas": respects_odas,
                "nested_das_odas_certificate": "YES" if recipe == SELECTED_RECIPE else "NO",
                "decision": decision,
            }
        )

    edition = []
    for row in current:
        surface = row["surface"]
        if surface == SELECTED_SURFACE:
            recipe = SELECTED_RECIPE
            rank = 1
            literal = WORKING_LITERAL_DE
            phrase = WORKING_PHRASE_DE
            evidence = (
                "dair|y|k|odas preserves exact odas=O+DA+S and nested "
                "das=DA+S; left o/O signature 31/37"
            )
            policy = "GDT533_NESTED_ODAS_TAIL_REVISION"
            resolution = "RESOLVED_BY_NESTED_EXACT_TERMINAL_WHOLE_CARD"
        else:
            recipe = row["gdt532_working_recipe"]
            rank = int(row["gdt532_candidate_rank"])
            literal = row["gdt532_literal_reading_de"]
            phrase = row["gdt532_short_phrase_de"]
            evidence = "NO_SELECTED_NESTED_ODAS_REVISION"
            policy = "INHERIT_GDT532_WORKING_RECIPE"
            resolution = row["gdt532_resolution_status"]
        edition.append(
            {
                **row,
                "gdt533_working_recipe": recipe,
                "gdt533_candidate_rank": rank,
                "gdt533_literal_reading_de": literal,
                "gdt533_short_phrase_de": phrase,
                "gdt533_evidence": evidence,
                "gdt533_policy": policy,
                "gdt533_resolution_status": resolution,
            }
        )

    unresolved = [
        row for row in edition if row["gdt533_resolution_status"] == "UNRESOLVED_NON_TOP1"
    ]
    previous_metrics = metric(edition, "gdt532_candidate_rank")
    revised_metrics = metric(edition, "gdt533_candidate_rank")
    status = (
        "PASS_NESTED_ODAS_TAIL_WORKING_REVISION"
        if len(old) == 4576
        and len(current) == 159
        and len(tiling_routes) == 12
        and Counter(row["candidate_recipe"] for row in tiling_routes)
        == Counter({SELECTED_RECIPE: 4, PREVIOUS_RECIPE: 8})
        and preferred_selected["surface_tiling"] == "dair|y|k|odas"
        and preferred_rival["surface_tiling"] == "dair|y|kod|as"
        and inventory["dair"]["event_count"] == 9
        and inventory["y"]["event_count"] == 39
        and inventory["k"]["event_count"] == 4
        and inventory["odas"]["event_count"] == 1
        and inventory["das"]["event_count"] == 1
        and signature["support_pair_count"] == "31"
        and signature["visible_condition_total"] == "37"
        and signature["conditional_probability"] == "0.797468354"
        and signature["reliability"] == "0.939393939"
        and min(selected_pair_counts) == 2
        and min(rival_pair_counts) == 1
        and len(as_ending_rows) == 6
        and len(statement_rows) == 22
        and previous_metrics == inherited_result["gdt532_candidate_agreement_metrics"]
        and revised_metrics["top1_exact_count"] == 155
        and revised_metrics["rank_sum"] == 174
        and len(unresolved) == 3
        else "FAIL_SELECTION_GATE"
    )
    result = {
        "experiment_id": "GDT533",
        "status": status,
        "claim_ceiling": "EXPLORATORY_NESTED_EXACT_TERMINAL_WHOLE_CARD_REVISION__NO_GLOBAL_ODAS_OR_AS_SUFFIX",
        "old_running_event_count": len(old),
        "current_target_count": len(current),
        "dairykodas_exact_tiling_route_count": len(tiling_routes),
        "tileable_candidate_recipe_count": len(routes_by_recipe),
        "selected_revision_count": 1,
        "selected_revision": {
            "surface": SELECTED_SURFACE,
            "previous_working_recipe": target_row["gdt532_working_recipe"],
            "previous_candidate_rank": int(target_row["gdt532_candidate_rank"]),
            "new_working_recipe": SELECTED_RECIPE,
            "new_candidate_rank": 1,
            "surface_tiling": "dair|y|k|odas",
            "recipe_tiling": "D_ADDR+AIR | Y | K | O+DA+S",
            "nested_tail": "das=DA+S -> odas=O+DA+S",
            "left_o_O_signature": "31/37",
            "left_o_O_probability": 0.797468354,
            "left_o_O_reliability": 0.939393939,
            "working_literal_de": WORKING_LITERAL_DE,
            "working_phrase_de": WORKING_PHRASE_DE,
        },
        "selected_route_old_card_counts": {
            surface: inventory[surface]["event_count"] for surface in SELECTED_TILING
        },
        "selected_pair_minimum_support": min(selected_pair_counts),
        "rival_pair_minimum_support": min(rival_pair_counts),
        "critical_pair_support": {
            "DA+S": next(
                int(row["occurrence_count"])
                for row in pair_rows
                if row["pair"] == "DA+S" and row["route"] == "SELECTED_RANK1"
            ),
            "D_ADDR+A_ADDR": next(
                int(row["occurrence_count"])
                for row in pair_rows
                if row["pair"] == "D_ADDR+A_ADDR" and row["route"] == "RIVAL_RANK2"
            ),
        },
        "previous_candidate_agreement_metrics": previous_metrics,
        "gdt533_candidate_agreement_metrics": revised_metrics,
        "remaining_unresolved_surface_count": len(unresolved),
        "remaining_unresolved_surfaces": [row["surface"] for row in unresolved],
        "guard": "PRESERVE_EXACT_TERMINAL_ODAS_ONLY_WHERE_FULL_TARGET_CANDIDATE_AND_NESTED_DAS_SUPERFORM_AGREE__NO_GLOBAL_ODAS_OR_AS_SUFFIX__NO_NEW_PAGES",
    }

    write_tsv(OUT / "gdt533_159_working_revision.tsv", edition, list(edition[0]))
    write_tsv(
        OUT / "gdt533_dairykodas_candidate_comparison.tsv",
        comparison_rows,
        list(comparison_rows[0]),
    )
    write_tsv(
        OUT / "gdt533_dairykodas_exact_card_certificate.tsv",
        tile_rows,
        list(tile_rows[0]),
    )
    write_tsv(
        OUT / "gdt533_nested_das_odas_atlas.tsv", nested_rows, list(nested_rows[0])
    )
    write_tsv(
        OUT / "gdt533_candidate_pair_support_atlas.tsv", pair_rows, list(pair_rows[0])
    )
    write_tsv(
        OUT / "gdt533_old_as_ending_control.tsv",
        as_ending_rows,
        list(as_ending_rows[0]),
    )
    write_tsv(
        OUT / "gdt533_target_statement_atlas.tsv",
        statement_rows,
        list(statement_rows[0]),
    )
    write_tsv(
        OUT / "gdt533_remaining_unresolved_atlas.tsv",
        unresolved,
        list(edition[0]),
    )
    write_json(OUT / "gdt533_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
