#!/usr/bin/env python3
"""Resolve one residual through exact old cards and a same-owner carrier."""

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
BASE = ROOT / "experiments/yolo/gdt532_same_owner_exact_card_tiling_revision"
OUT = BASE / "artifacts"
OLD_RUNNING = (
    ROOT
    / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
    / "gdt407_4576_running_event_edition.tsv"
)
OLD_LOCAL = (
    ROOT
    / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
    / "gdt407_693_local_group_edition.tsv"
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
    / "experiments/yolo/gdt531_atomic_renderer_block_superform_peel/artifacts"
    / "gdt531_159_working_revision.tsv"
)
CURRENT_RESULT = (
    ROOT
    / "experiments/yolo/gdt531_atomic_renderer_block_superform_peel/artifacts"
    / "gdt531_result.json"
)

SELECTED_SURFACE = "dsholdaiir"
SELECTED_RECIPE = "D_ADDR+SH+OL+DA+IIN+R"
SELECTED_TILING = ("d", "shol", "daiir")
WORKING_LITERAL_DE = (
    "[D_ADDR:STEUERUNG=HIER] · HALTEN · FORTSETZEN · "
    "[DA+IIN:STEUERUNG=STUFE II] · MARKIEREN"
)
WORKING_PHRASE_DE = "Hier halten und fortsetzen; Stufe II markieren."


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


def invariant_inventory(
    running: list[dict[str, str]], local: list[dict[str, str]]
) -> dict[str, dict]:
    grouped: dict[str, dict[str, list[dict[str, str]]]] = {
        "OLD_RUNNING_INVARIANT": defaultdict(list),
        "OLD_LOCAL_INVARIANT": defaultdict(list),
    }
    for row in running:
        grouped["OLD_RUNNING_INVARIANT"][row["surface"]].append(row)
    for row in local:
        grouped["OLD_LOCAL_INVARIANT"][row["surface"]].append(row)

    inventory = {}
    all_surfaces = sorted(
        set(grouped["OLD_RUNNING_INVARIANT"])
        | set(grouped["OLD_LOCAL_INVARIANT"])
    )
    for surface in all_surfaces:
        running_rows = grouped["OLD_RUNNING_INVARIANT"].get(surface, [])
        local_rows = grouped["OLD_LOCAL_INVARIANT"].get(surface, [])
        running_recipes = {row["component_recipe"] for row in running_rows}
        local_recipes = {row["component_recipe"] for row in local_rows}
        if running_rows and len(running_recipes) == 1:
            source_tier = "OLD_RUNNING_INVARIANT"
            rows = running_rows
            recipe = next(iter(running_recipes))
            event_field = "global_running_event_id"
        elif not running_rows and local_rows and len(local_recipes) == 1:
            source_tier = "OLD_LOCAL_INVARIANT"
            rows = local_rows
            recipe = next(iter(local_recipes))
            event_field = "source_event_id"
        else:
            continue
        inventory[surface] = {
            "surface": surface,
            "recipe": recipe,
            "source_tier": source_tier,
            "old_event_count": len(rows),
            "old_pages": "|".join(sorted({row["physical_page"] for row in rows})),
            "old_registers": "|".join(sorted({row["register"] for row in rows})),
            "old_event_ids": "|".join(row[event_field] for row in rows),
            "old_loci": "|".join(row["locus"] for row in rows),
        }
    return inventory


def enumerate_candidate_tilings(
    target_rows: list[dict[str, str]],
    inventory: dict[str, dict],
    candidate_ranks: dict[str, dict[str, int]],
    current_events: list[dict[str, str]],
) -> list[dict]:
    target_surfaces = {row["surface"] for row in target_rows}
    target_context = {
        row["surface"]: row
        for row in current_events
        if row["surface"] in target_surfaces
    }
    current_by_card: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in current_events:
        current_by_card[(row["surface"], row["gdt516_context_recipe"])].append(row)

    routes = []
    for target_row in target_rows:
        surface = target_row["surface"]
        context = target_context[surface]
        paths: list[tuple[dict, ...]] = []

        def walk(index: int, path: tuple[dict, ...]) -> None:
            if index == len(surface):
                if len(path) >= 2:
                    paths.append(path)
                return
            for end in range(index + 1, len(surface) + 1):
                tile_surface = surface[index:end]
                if index == 0 and end == len(surface):
                    continue
                tile = inventory.get(tile_surface)
                if tile is not None:
                    walk(end, path + (tile,))

        walk(0, ())
        for path in paths:
            recipe = "+".join(tile["recipe"] for tile in path)
            rank = candidate_ranks.get(surface, {}).get(recipe)
            if rank is None:
                continue
            same_owner_events = []
            cross_role_tiles = []
            for tile in path:
                matches = current_by_card.get((tile["surface"], tile["recipe"]), [])
                if tile["source_tier"] == "OLD_LOCAL_INVARIANT" and matches:
                    cross_role_tiles.append(tile["surface"])
                same_owner_events.extend(
                    row
                    for row in matches
                    if row["event_id"] != context["event_id"]
                    and row["owner_id"] == context["owner_id"]
                    and row["prose_block_id"] == context["prose_block_id"]
                )
            routes.append(
                {
                    "surface": surface,
                    "previous_working_recipe": target_row["gdt531_working_recipe"],
                    "candidate_recipe": recipe,
                    "gdt529_rank": rank,
                    "surface_tiling": "|".join(tile["surface"] for tile in path),
                    "recipe_tiling": " | ".join(tile["recipe"] for tile in path),
                    "tile_count": len(path),
                    "longest_tile_width": max(len(tile["surface"]) for tile in path),
                    "old_running_tile_count": sum(
                        tile["source_tier"] == "OLD_RUNNING_INVARIANT" for tile in path
                    ),
                    "old_local_tile_count": sum(
                        tile["source_tier"] == "OLD_LOCAL_INVARIANT" for tile in path
                    ),
                    "cross_role_old_local_tiles": "|".join(sorted(set(cross_role_tiles)))
                    or "NONE",
                    "same_owner_block_other_carrier_count": len(
                        {row["event_id"] for row in same_owner_events}
                    ),
                    "same_owner_block_other_carrier_ids": "|".join(
                        sorted({row["event_id"] for row in same_owner_events})
                    )
                    or "NONE",
                    "target_event_id": context["event_id"],
                    "target_page": context["physical_page"],
                    "target_locus": context["locus"],
                    "target_owner_id": context["owner_id"],
                    "target_prose_block_id": context["prose_block_id"],
                }
            )
    unique = {
        (row["surface"], row["candidate_recipe"], row["surface_tiling"]): row
        for row in routes
    }
    return sorted(
        unique.values(),
        key=lambda row: (
            row["surface"],
            row["gdt529_rank"],
            row["tile_count"],
            row["surface_tiling"],
        ),
    )


def preferred_route(routes: list[dict]) -> dict:
    return min(
        routes,
        key=lambda row: (
            int(row["tile_count"]),
            -int(row["longest_tile_width"]),
            -int(row["old_running_tile_count"]),
            row["surface_tiling"],
        ),
    )


def summarize_tilings(routes: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    recipes_by_surface: dict[str, set[str]] = defaultdict(set)
    for row in routes:
        grouped[(row["surface"], row["candidate_recipe"])].append(row)
        recipes_by_surface[row["surface"]].add(row["candidate_recipe"])
    summary = []
    for (surface, recipe), rows in sorted(
        grouped.items(), key=lambda item: (item[0][0], int(item[1][0]["gdt529_rank"]))
    ):
        best = preferred_route(rows)
        distinct = len(recipes_by_surface[surface])
        if surface == SELECTED_SURFACE and recipe == SELECTED_RECIPE:
            decision = "SELECT_UNIQUE_RECIPE_WITH_SAME_OWNER_CROSS_ROLE_CARRIER"
        elif distinct > 1:
            decision = "AMBIGUOUS_MULTIPLE_EXACTLY_TILEABLE_RECIPES"
        else:
            decision = "UNIQUE_BUT_NO_SELECTED_CROSS_ROLE_OWNER_CERTIFICATE"
        summary.append(
            {
                "surface": surface,
                "candidate_recipe": recipe,
                "gdt529_rank": best["gdt529_rank"],
                "distinct_tileable_candidate_recipe_count": distinct,
                "exact_tiling_route_count": len(rows),
                "minimum_tile_count": min(int(row["tile_count"]) for row in rows),
                "preferred_surface_tiling": best["surface_tiling"],
                "preferred_recipe_tiling": best["recipe_tiling"],
                "cross_role_old_local_tiles": best["cross_role_old_local_tiles"],
                "same_owner_block_other_carrier_count": best[
                    "same_owner_block_other_carrier_count"
                ],
                "same_owner_block_other_carrier_ids": best[
                    "same_owner_block_other_carrier_ids"
                ],
                "decision": decision,
            }
        )
    return summary


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
    old_running = read_tsv(OLD_RUNNING)
    old_local = read_tsv(OLD_LOCAL)
    current_events = read_tsv(CURRENT_EVENTS)
    current = read_tsv(CURRENT_WORKING)
    inherited_result = json.loads(CURRENT_RESULT.read_text(encoding="utf-8"))
    candidate_rows = read_tsv(CANDIDATES)
    candidate_ranks: dict[str, dict[str, int]] = defaultdict(dict)
    for row in candidate_rows:
        candidate_ranks[row["surface"]][row["candidate_recipe"]] = int(
            row["gdt529_rank"]
        )

    inventory = invariant_inventory(old_running, old_local)
    inherited_residuals = [
        row for row in current if int(row["gdt531_working_rank"]) != 1
    ]
    routes = enumerate_candidate_tilings(
        inherited_residuals, inventory, candidate_ranks, current_events
    )
    summaries = summarize_tilings(routes)
    selected_routes = [
        row
        for row in routes
        if row["surface"] == SELECTED_SURFACE
        and row["candidate_recipe"] == SELECTED_RECIPE
    ]
    selected = preferred_route(selected_routes)
    previous_selected_row = next(
        row for row in current if row["surface"] == SELECTED_SURFACE
    )

    target_context = next(
        row for row in current_events if row["surface"] == SELECTED_SURFACE
    )
    current_by_card: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in current_events:
        current_by_card[(row["surface"], row["gdt516_context_recipe"])].append(row)

    certificate_rows = []
    tile_roles = {
        "d": "INITIAL_ADDRESS_CARD",
        "shol": "STABLE_ACTION_PACKAGE",
        "daiir": "CROSS_ROLE_STAGE_MARKING_CARD",
    }
    for ordinal, tile_surface in enumerate(SELECTED_TILING, start=1):
        tile = inventory[tile_surface]
        matches = current_by_card[(tile_surface, tile["recipe"])]
        same_owner = [
            row
            for row in matches
            if row["event_id"] != target_context["event_id"]
            and row["owner_id"] == target_context["owner_id"]
            and row["prose_block_id"] == target_context["prose_block_id"]
        ]
        certificate_rows.append(
            {
                "tile_ordinal": ordinal,
                "tile_surface": tile_surface,
                "tile_recipe": tile["recipe"],
                "tile_role": tile_roles[tile_surface],
                "source_tier": tile["source_tier"],
                "old_event_count": tile["old_event_count"],
                "old_pages": tile["old_pages"],
                "old_registers": tile["old_registers"],
                "old_event_ids": tile["old_event_ids"],
                "old_loci": tile["old_loci"],
                "current_same_recipe_event_count": len(matches),
                "current_pages": "|".join(
                    sorted({row["physical_page"] for row in matches})
                )
                or "NONE",
                "current_event_ids": "|".join(row["event_id"] for row in matches)
                or "NONE",
                "current_prose_event_count": sum(
                    row["source_kind"] == "P" for row in matches
                ),
                "same_owner_block_other_event_count": len(same_owner),
                "same_owner_block_other_event_ids": "|".join(
                    row["event_id"] for row in same_owner
                )
                or "NONE",
            }
        )

    block_rows = []
    for row in current_events:
        if row["prose_block_id"] != target_context["prose_block_id"]:
            continue
        atoms = row["gdt516_context_recipe"].split("+")
        if row["event_id"] == target_context["event_id"]:
            relation = "TARGET"
        elif row["surface"] == "daiir" and row["gdt516_context_recipe"] == "DA+IIN+R":
            relation = "SAME_OWNER_EXACT_TAIL_CARRIER"
        elif any(
            atoms[index : index + 2] == ["SH", "OL"]
            for index in range(len(atoms) - 1)
        ):
            relation = "SAME_OWNER_SHOL_PACKAGE_CARRIER"
        else:
            relation = "SAME_OWNER_BLOCK_CONTEXT"
        block_rows.append(
            {
                "event_id": row["event_id"],
                "physical_page": row["physical_page"],
                "locus": row["locus"],
                "line_number": row["line_number"],
                "statement_id": row["statement_id"],
                "card_ordinal_in_statement": row["card_ordinal_in_statement"],
                "prose_block_id": row["prose_block_id"],
                "owner_id": row["owner_id"],
                "surface": row["surface"],
                "recipe": row["gdt516_context_recipe"],
                "literal_reading_de": row["gdt516_literal_reading_de"],
                "relation_to_selected_route": relation,
            }
        )

    dshold_routes = [row for row in routes if row["surface"] == SELECTED_SURFACE]
    route_count_by_recipe = Counter(row["candidate_recipe"] for row in dshold_routes)
    best_by_recipe = {}
    for recipe in route_count_by_recipe:
        best_by_recipe[recipe] = preferred_route(
            [row for row in dshold_routes if row["candidate_recipe"] == recipe]
        )
    competitor_rows = []
    for row in candidate_rows:
        if row["surface"] != SELECTED_SURFACE:
            continue
        recipe = row["candidate_recipe"]
        best = best_by_recipe.get(recipe)
        if recipe == SELECTED_RECIPE:
            decision = "SELECT_EXACT_THREE_CARD_SAME_OWNER_ROUTE"
        elif recipe == previous_selected_row["gdt531_working_recipe"]:
            decision = "REPLACE_PREVIOUS_WORKING_NO_EXACT_CARD_TILING"
        elif int(row["gdt529_rank"]) == 1:
            decision = "RETAIN_SCORER_RUNNER_UP_NO_EXACT_CARD_TILING"
        else:
            decision = "RETAIN_ALTERNATIVE"
        competitor_rows.append(
            {
                "surface": SELECTED_SURFACE,
                "candidate_recipe": recipe,
                "gdt529_rank": int(row["gdt529_rank"]),
                "exact_card_tiling_route_count": route_count_by_recipe[recipe],
                "preferred_surface_tiling": best["surface_tiling"] if best else "NONE",
                "preferred_recipe_tiling": best["recipe_tiling"] if best else "NONE",
                "same_owner_block_other_carrier_count": (
                    best["same_owner_block_other_carrier_count"] if best else 0
                ),
                "decision": decision,
            }
        )

    edition = []
    for row in current:
        surface = row["surface"]
        if surface == SELECTED_SURFACE:
            recipe = SELECTED_RECIPE
            rank = candidate_ranks[surface][recipe]
            literal = WORKING_LITERAL_DE
            phrase = WORKING_PHRASE_DE
            evidence = (
                "d|shol|daiir=D_ADDR|SH+OL|DA+IIN+R; daiir recurs later "
                "in the same F66R_PROSE_02 owner block"
            )
            policy = "GDT532_SAME_OWNER_EXACT_CARD_TILING_REVISION"
            resolution = "RESOLVED_BY_EXACT_CARD_COMPOSITION_OVERRIDE"
        else:
            recipe = row["gdt531_working_recipe"]
            rank = int(row["gdt531_working_rank"])
            literal = row["gdt531_literal_reading_de"]
            phrase = row["gdt531_short_phrase_de"]
            evidence = "NO_SELECTED_SAME_OWNER_EXACT_CARD_TILING_REVISION"
            policy = "INHERIT_GDT531_WORKING_RECIPE"
            resolution = (
                "UNRESOLVED_NON_TOP1"
                if rank != 1
                else "INHERITED_RESOLVED_WORKING_DEFAULT"
            )
        edition.append(
            {
                **row,
                "gdt532_working_recipe": recipe,
                "gdt532_candidate_rank": rank,
                "gdt532_literal_reading_de": literal,
                "gdt532_short_phrase_de": phrase,
                "gdt532_evidence": evidence,
                "gdt532_policy": policy,
                "gdt532_resolution_status": resolution,
            }
        )

    unresolved = [
        row for row in edition if row["gdt532_resolution_status"] == "UNRESOLVED_NON_TOP1"
    ]
    previous_metrics = metric(edition, "gdt531_working_rank")
    revised_metrics = metric(edition, "gdt532_candidate_rank")
    summary_counts = Counter(row["surface"] for row in routes)
    distinct_recipe_count = len(
        {(row["surface"], row["candidate_recipe"]) for row in routes}
    )
    status = (
        "PASS_UNIQUE_SAME_OWNER_EXACT_CARD_TILING_REVISION"
        if len(old_running) == 4576
        and len(old_local) == 693
        and len(current) == 159
        and len(inherited_residuals) == 5
        and len(routes) == 16
        and summary_counts == Counter({"dairykodas": 12, "dsholdaiir": 4})
        and distinct_recipe_count == 3
        and selected["surface_tiling"] == "d|shol|daiir"
        and selected["candidate_recipe"] == SELECTED_RECIPE
        and int(selected["gdt529_rank"]) == 6
        and certificate_rows[2]["old_event_count"] == 2
        and certificate_rows[2]["current_same_recipe_event_count"] == 2
        and certificate_rows[2]["same_owner_block_other_event_count"] == 1
        and len(block_rows) == 56
        and len(unresolved) == 4
        and previous_metrics == inherited_result["gdt531_working_metrics"]
        and revised_metrics["top1_exact_count"] == 154
        and revised_metrics["top2_exact_count"] == 157
        and revised_metrics["rank_sum"] == 175
        else "FAIL_SELECTION_GATE"
    )
    result = {
        "experiment_id": "GDT532",
        "status": status,
        "claim_ceiling": "EXPLORATORY_UNIQUE_EXACT_CARD_COMPOSITION_OVERRIDE__NO_FREE_TILING_OR_CONFIRMED_PLAINTEXT",
        "old_running_event_count": len(old_running),
        "old_local_group_count": len(old_local),
        "exact_card_inventory_surface_count": len(inventory),
        "inherited_residual_surface_count": len(inherited_residuals),
        "candidate_tiling_route_count": len(routes),
        "candidate_tiling_surface_count": len(summary_counts),
        "distinct_surface_recipe_count": distinct_recipe_count,
        "route_counts_by_surface": dict(sorted(summary_counts.items())),
        "selected_revision_count": 1,
        "selected_revision": {
            "surface": SELECTED_SURFACE,
            "previous_working_recipe": previous_selected_row["gdt531_working_recipe"],
            "previous_candidate_rank": int(previous_selected_row["gdt531_working_rank"]),
            "new_working_recipe": SELECTED_RECIPE,
            "new_candidate_rank": candidate_ranks[SELECTED_SURFACE][SELECTED_RECIPE],
            "surface_tiling": "d|shol|daiir",
            "recipe_tiling": "D_ADDR | SH+OL | DA+IIN+R",
            "old_tile_event_counts": {
                row["tile_surface"]: row["old_event_count"] for row in certificate_rows
            },
            "same_owner_tail_carrier": "G515-E0408@f66r.62/F66R_PROSE_02",
            "working_literal_de": WORKING_LITERAL_DE,
            "working_phrase_de": WORKING_PHRASE_DE,
        },
        "previous_candidate_agreement_metrics": previous_metrics,
        "gdt532_candidate_agreement_metrics": revised_metrics,
        "candidate_rank_cost": {
            "selected_surface_rank_change": "2->6",
            "rank_sum_change": 4,
            "top2_change": -1,
            "interpretation": "EXACT_CARD_COMPOSITION_OVERRIDES_HEURISTIC_CANDIDATE_ORDER_FOR_ONE_WORKING_READING",
        },
        "resolved_non_top1_surface_count": 1,
        "remaining_unresolved_surface_count": len(unresolved),
        "remaining_unresolved_surfaces": [row["surface"] for row in unresolved],
        "same_owner_block_event_count": len(block_rows),
        "guard": "UNIQUE_CANDIDATE_RECIPE_AMONG_EXACT_RESIDUAL_TILINGS__OLD_LOCAL_TILE_REQUIRES_CURRENT_CROSS_ROLE_AND_SAME_OWNER_BLOCK_CARRIER__NO_FREE_SUBSTRING_TILING__NO_NEW_PAGES",
    }

    write_tsv(OUT / "gdt532_159_working_revision.tsv", edition, list(edition[0]))
    write_tsv(
        OUT / "gdt532_residual_candidate_tiling_atlas.tsv", routes, list(routes[0])
    )
    write_tsv(
        OUT / "gdt532_distinct_candidate_tiling_summary.tsv",
        summaries,
        list(summaries[0]),
    )
    write_tsv(
        OUT / "gdt532_dsholdaiir_tile_certificate.tsv",
        certificate_rows,
        list(certificate_rows[0]),
    )
    write_tsv(
        OUT / "gdt532_dsholdaiir_competing_route_atlas.tsv",
        competitor_rows,
        list(competitor_rows[0]),
    )
    write_tsv(
        OUT / "gdt532_same_owner_block_atlas.tsv", block_rows, list(block_rows[0])
    )
    write_tsv(
        OUT / "gdt532_remaining_unresolved_atlas.tsv",
        unresolved,
        list(edition[0]),
    )
    write_json(OUT / "gdt532_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
