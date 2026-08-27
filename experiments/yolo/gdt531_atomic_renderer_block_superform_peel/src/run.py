#!/usr/bin/env python3
"""Peel licensed multi-character renderer blocks from exact old superforms."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt531_atomic_renderer_block_superform_peel"
OUT = BASE / "artifacts"
G530_RUN = (
    ROOT / "experiments/yolo/gdt530_exact_superform_peel_revision/src/run.py"
)
G530_CURRENT = (
    ROOT
    / "experiments/yolo/gdt530_exact_superform_peel_revision/artifacts"
    / "gdt530_159_working_revision.tsv"
)
G530_RESULT = (
    ROOT
    / "experiments/yolo/gdt530_exact_superform_peel_revision/artifacts"
    / "gdt530_result.json"
)
G529_CANDIDATES = (
    ROOT
    / "experiments/yolo/gdt529_nearest_terminal_m_square/artifacts"
    / "gdt529_candidate_score_atlas.tsv"
)
G522_ATLAS = (
    ROOT
    / "experiments/yolo/gdt522_local_edit_analogy_license_reranker/artifacts"
    / "gdt522_local_edit_analogy_atlas.tsv"
)

SELECTED_SURFACE = "saiis"
SELECTED_RECIPE = "S+A_ADDR+IIN+S"
SELECTED_SUPERFORM = "saiisol"
SELECTED_SUPERFORM_RECIPE = "S+A_ADDR+IIN+S+OL"
WORKING_LITERAL_DE = "WÄHLEN · HIER · STUFE · WÄHLEN"
WORKING_PHRASE_DE = "Wählen; hier die Stufe wählen."
MIN_VISIBLE_WIDTH = 2
MAX_VISIBLE_WIDTH = 3
MAX_ATOM_WIDTH = 3


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G530 = load_module("gdt530_core_for_gdt531", G530_RUN)


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


def atoms(recipe: str) -> tuple[str, ...]:
    return tuple(part for part in recipe.split("+") if part)


def position(index: int, total: int, width: int) -> str:
    if index == 0:
        return "LEFT"
    if index + width == total:
        return "RIGHT"
    return "INNER"


def strong_signature(row: dict[str, str]) -> bool:
    return (
        int(row["support_pair_count"]) >= 3
        and float(row["conditional_probability"]) >= 0.5
        and float(row["reliability"]) >= 0.6
    )


def enumerate_routes(
    current: list[dict[str, str]],
    forms: dict[str, tuple[str, ...]],
    events: Counter[str],
    pages: dict[str, set[str]],
    registers: dict[str, set[str]],
    event_ids: dict[str, list[str]],
    loci: dict[str, list[str]],
    signatures: dict[tuple[str, str, str, str], dict[str, str]],
) -> list[dict]:
    rows = []
    for current_row in current:
        surface = current_row["surface"]
        working = current_row["gdt530_working_recipe"]
        top1 = current_row["gdt529_top1"]
        roles_by_recipe: dict[str, set[str]] = defaultdict(set)
        roles_by_recipe[working].add("WORKING")
        roles_by_recipe[top1].add("TOP1")
        for old_surface, old_recipe in sorted(forms.items()):
            visible_width = len(old_surface) - len(surface)
            if not MIN_VISIBLE_WIDTH <= visible_width <= MAX_VISIBLE_WIDTH:
                continue
            for visible_index in range(len(old_surface) - visible_width + 1):
                if (
                    old_surface[:visible_index]
                    + old_surface[visible_index + visible_width :]
                    != surface
                ):
                    continue
                visible_insert = old_surface[
                    visible_index : visible_index + visible_width
                ]
                visible_position = position(
                    visible_index, len(old_surface), visible_width
                )
                for candidate_recipe, roles in sorted(roles_by_recipe.items()):
                    candidate_atoms = atoms(candidate_recipe)
                    for atom_width in range(1, min(MAX_ATOM_WIDTH, len(old_recipe)) + 1):
                        if len(old_recipe) - atom_width != len(candidate_atoms):
                            continue
                        for atom_index in range(len(old_recipe) - atom_width + 1):
                            if (
                                old_recipe[:atom_index]
                                + old_recipe[atom_index + atom_width :]
                                != candidate_atoms
                            ):
                                continue
                            atom_insert = "+".join(
                                old_recipe[atom_index : atom_index + atom_width]
                            )
                            atom_position = position(
                                atom_index, len(old_recipe), atom_width
                            )
                            signature = signatures.get(
                                (
                                    visible_insert,
                                    visible_position,
                                    atom_insert,
                                    atom_position,
                                )
                            )
                            if signature is None or not strong_signature(signature):
                                continue
                            if roles == {"TOP1"}:
                                route_class = "SUPPORTS_TOP1_ALTERNATIVE"
                            elif roles == {"WORKING"}:
                                route_class = "SUPPORTS_EXISTING_WORKING"
                            else:
                                route_class = "SUPPORTS_EXISTING_WORKING_AND_TOP1"
                            rows.append(
                                {
                                    "surface": surface,
                                    "previous_working_recipe": working,
                                    "gdt529_top1": top1,
                                    "supported_candidate_recipe": candidate_recipe,
                                    "supported_candidate_roles": "|".join(sorted(roles)),
                                    "route_class": route_class,
                                    "old_superform": old_surface,
                                    "old_superform_recipe": "+".join(old_recipe),
                                    "removed_visible_block": visible_insert,
                                    "visible_block_width": visible_width,
                                    "visible_index": visible_index,
                                    "visible_position": visible_position,
                                    "removed_atom_block": atom_insert,
                                    "atom_block_width": atom_width,
                                    "atom_index": atom_index,
                                    "atom_position": atom_position,
                                    "support_pair_count": int(
                                        signature["support_pair_count"]
                                    ),
                                    "visible_condition_total": int(
                                        signature["visible_condition_total"]
                                    ),
                                    "visible_condition_option_count": int(
                                        signature["visible_condition_option_count"]
                                    ),
                                    "conditional_probability": signature[
                                        "conditional_probability"
                                    ],
                                    "reliability": signature["reliability"],
                                    "signature_examples": signature["examples"],
                                    "old_event_count": events[old_surface],
                                    "old_pages": "|".join(sorted(pages[old_surface])),
                                    "old_registers": "|".join(
                                        sorted(registers[old_surface])
                                    ),
                                    "old_event_ids": "|".join(event_ids[old_surface]),
                                    "old_loci": "|".join(loci[old_surface]),
                                }
                            )
    unique = {
        (
            row["surface"],
            row["supported_candidate_recipe"],
            row["old_superform"],
            row["visible_index"],
            row["atom_index"],
            row["visible_block_width"],
            row["atom_block_width"],
        ): row
        for row in rows
    }
    return sorted(
        unique.values(),
        key=lambda row: (
            row["surface"],
            row["old_superform"],
            row["supported_candidate_recipe"],
            row["visible_index"],
            row["atom_index"],
        ),
    )


def selected_revisions(
    current: list[dict[str, str]], routes: list[dict], forms: dict[str, tuple[str, ...]]
) -> list[dict]:
    routes_by_surface: dict[str, list[dict]] = defaultdict(list)
    for route in routes:
        routes_by_surface[route["surface"]].append(route)
    selected = []
    for row in current:
        surface = row["surface"]
        working = row["gdt530_working_recipe"]
        top1 = row["gdt529_top1"]
        if working == top1 or surface in forms:
            continue
        top_routes = [
            route
            for route in routes_by_surface[surface]
            if route["supported_candidate_recipe"] == top1
        ]
        working_routes = [
            route
            for route in routes_by_surface[surface]
            if route["supported_candidate_recipe"] == working
        ]
        if not top_routes or working_routes:
            continue
        for route in top_routes:
            selected.append(
                {
                    **route,
                    "gdt530_working_rank": int(row["gdt530_working_rank"]),
                    "gdt531_working_rank": 1,
                    "gdt531_working_recipe": top1,
                    "working_literal_de": WORKING_LITERAL_DE,
                    "working_phrase_de": WORKING_PHRASE_DE,
                    "decision": "REVISE_WORKING_RECIPE_TO_BLOCK_PEELED_TOP1",
                }
            )
    return selected


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
    old = read_tsv(G530.G529.G518.G407_RUNNING)
    current = read_tsv(G530_CURRENT)
    inherited_result = json.loads(G530_RESULT.read_text(encoding="utf-8"))
    candidate_rows = read_tsv(G529_CANDIDATES)
    forms, events, pages, registers, event_ids, loci = G530.invariant_old_inventory(old)
    signatures = {
        (
            row["visible_insert"],
            row["visible_position"],
            row["atom_insert"],
            row["atom_position"],
        ): row
        for row in read_tsv(G522_ATLAS)
    }
    routes = enumerate_routes(
        current, forms, events, pages, registers, event_ids, loci, signatures
    )
    revisions = selected_revisions(current, routes, forms)
    revision_by_surface = {
        row["surface"]: row["gdt531_working_recipe"] for row in revisions
    }
    edition = []
    for row in current:
        surface = row["surface"]
        recipe = revision_by_surface.get(surface, row["gdt530_working_recipe"])
        rank = 1 if surface in revision_by_surface else int(row["gdt530_working_rank"])
        if surface == SELECTED_SURFACE:
            literal = WORKING_LITERAL_DE
            phrase = WORKING_PHRASE_DE
            evidence = (
                "saiisol=S+A_ADDR+IIN+S+OL; peel terminal ol/OL; "
                "old right ol/OL signature 29/33"
            )
            policy = "GDT531_ATOMIC_RENDERER_BLOCK_SUPERFORM_PEEL"
        else:
            literal = row["gdt530_literal_reading_de"]
            phrase = row["gdt530_short_phrase_de"]
            evidence = "NO_SELECTED_ATOMIC_BLOCK_PEEL_REVISION"
            policy = "INHERIT_GDT530_WORKING_RECIPE"
        edition.append(
            {
                **row,
                "gdt531_working_recipe": recipe,
                "gdt531_working_rank": rank,
                "gdt531_literal_reading_de": literal,
                "gdt531_short_phrase_de": phrase,
                "gdt531_evidence": evidence,
                "gdt531_policy": policy,
            }
        )

    rank_by_candidate = {
        row["candidate_recipe"]: int(row["gdt529_rank"])
        for row in candidate_rows
        if row["surface"] == SELECTED_SURFACE
    }
    competitor_rows = [
        {
            "surface": SELECTED_SURFACE,
            "candidate_recipe": SELECTED_RECIPE,
            "gdt529_rank": rank_by_candidate[SELECTED_RECIPE],
            "route_type": "EXACT_OLD_SUPERFORM_ATOMIC_BLOCK_PEEL",
            "visible_derivation": "saiisol-ol=saiis",
            "recipe_derivation": "S+A_ADDR+IIN+S+OL-OL=S+A_ADDR+IIN+S",
            "evidence": "exact old saiisol; ol/OL@RIGHT/RIGHT=29/33",
            "decision": "SELECTED",
        },
        {
            "surface": SELECTED_SURFACE,
            "candidate_recipe": "S+AIIN+S",
            "gdt529_rank": rank_by_candidate["S+AIIN+S"],
            "route_type": "EXACT_CARD_TILING",
            "visible_derivation": "saii|s",
            "recipe_derivation": "S+AIIN | S",
            "evidence": "old saii once; same-recipe saiin 20 events; old s 45 events",
            "decision": "RUNNER_UP_LESS_SPECIFIC_THAN_EXACT_SUPERFORM",
        },
        {
            "surface": SELECTED_SURFACE,
            "candidate_recipe": "S+IIN+S",
            "gdt529_rank": rank_by_candidate["S+IIN+S"],
            "route_type": "PREVIOUS_VISIBLE_ATOMIZATION",
            "visible_derivation": "s|aii|s",
            "recipe_derivation": "S | IIN | S",
            "evidence": "no exact old full-superform carrier",
            "decision": "REPLACED",
        },
    ]
    family_rows = []
    for old_surface, old_recipe in sorted(forms.items()):
        if not old_surface.startswith("saii"):
            continue
        family_rows.append(
            {
                "surface": old_surface,
                "recipe": "+".join(old_recipe),
                "event_count": events[old_surface],
                "pages": "|".join(sorted(pages[old_surface])),
                "registers": "|".join(sorted(registers[old_surface])),
                "event_ids": "|".join(event_ids[old_surface]),
                "relation_to_saiis": (
                    "EXACT_RIGHT_OL_SUPERFORM" if old_surface == "saiisol"
                    else "AIIN_STEM_FAMILY"
                ),
            }
        )

    remaining = [row for row in edition if int(row["gdt531_working_rank"]) != 1]
    previous_metrics = metric(edition, "gdt530_working_rank")
    revised_metrics = metric(edition, "gdt531_working_rank")
    route_classes = Counter(row["route_class"] for row in routes)
    selected_surfaces = sorted({row["surface"] for row in revisions})
    status = (
        "PASS_ATOMIC_RENDERER_BLOCK_SUPERFORM_PEEL"
        if len(forms) == 1558
        and len(current) == 159
        and len(routes) == 29
        and len({row["surface"] for row in routes}) == 15
        and route_classes
        == Counter(
            {
                "SUPPORTS_EXISTING_WORKING_AND_TOP1": 28,
                "SUPPORTS_TOP1_ALTERNATIVE": 1,
            }
        )
        and selected_surfaces == [SELECTED_SURFACE]
        and len(revisions) == 1
        and revisions[0]["old_superform"] == SELECTED_SUPERFORM
        and revisions[0]["old_superform_recipe"] == SELECTED_SUPERFORM_RECIPE
        and revisions[0]["removed_visible_block"] == "ol"
        and revisions[0]["removed_atom_block"] == "OL"
        and revisions[0]["support_pair_count"] == 29
        and previous_metrics == inherited_result["gdt530_working_metrics"]
        and revised_metrics["top1_exact_count"] == 154
        and revised_metrics["top2_exact_count"] == 158
        and revised_metrics["rank_sum"] == 171
        and len(remaining) == 5
        else "FAIL_SELECTION_GATE"
    )
    result = {
        "experiment_id": "GDT531",
        "status": status,
        "claim_ceiling": "EXPLORATORY_ATOMIC_RENDERER_BLOCK_SUPERFORM_PEEL__NO_GLOBAL_OL_SUFFIX_OR_CONFIRMED_PLAINTEXT",
        "selected_policy": {
            "visible_block_widths": [2, 3],
            "atom_block_widths": [1, 2, 3],
            "surface_relation": "EXACT_OLD_SUPERFORM_MINUS_ONE_CONTIGUOUS_VISIBLE_BLOCK",
            "recipe_relation": "EXACT_OLD_RECIPE_MINUS_ONE_CONTIGUOUS_ATOM_BLOCK",
            "license": "GDT522_POSITION_MATCHED_SIGNATURE_SUPPORT_GE3_PROBABILITY_GE0.5_RELIABILITY_GE0.6",
            "candidate_requirement": "EXISTING_GDT529_TOP1",
            "conflict": "NO_STRONG_ROUTE_FOR_PREVIOUS_WORKING_AND_NO_EXACT_OLD_TARGET_CONFLICT",
        },
        "old_invariant_surface_count": len(forms),
        "current_target_count": len(current),
        "licensed_block_route_count": len(routes),
        "licensed_block_surface_count": len({row["surface"] for row in routes}),
        "route_classes": dict(sorted(route_classes.items())),
        "selected_revision_count": len(revisions),
        "selected_surfaces": selected_surfaces,
        "selected_revision": {
            "surface": SELECTED_SURFACE,
            "previous_working_recipe": "S+IIN+S",
            "new_working_recipe": SELECTED_RECIPE,
            "old_superform": SELECTED_SUPERFORM,
            "old_superform_recipe": SELECTED_SUPERFORM_RECIPE,
            "removed_visible_atom_pair": "ol/OL@RIGHT/RIGHT",
            "old_signature_support": "29/33",
            "old_signature_probability": 0.830985915,
            "old_signature_reliability": 0.935483871,
            "working_literal_de": WORKING_LITERAL_DE,
            "working_phrase_de": WORKING_PHRASE_DE,
        },
        "previous_working_metrics": previous_metrics,
        "gdt531_working_metrics": revised_metrics,
        "remaining_working_error_count": len(remaining),
        "remaining_surfaces": [row["surface"] for row in remaining],
        "saii_family_surface_count": len(family_rows),
        "saii_family_event_count": sum(int(row["event_count"]) for row in family_rows),
        "guard": "ATOMIC_OL_BLOCK_PEEL_ONLY_WHERE_EXACT_SUPERFORM_AND_POSITION_SIGNATURE_AGREE__NO_GLOBAL_OL_SUFFIX__NO_NEW_PAGES",
    }

    write_tsv(
        OUT / "gdt531_159_working_revision.tsv", edition, list(edition[0])
    )
    write_tsv(
        OUT / "gdt531_atomic_block_peel_route_atlas.tsv", routes, list(routes[0])
    )
    write_tsv(
        OUT / "gdt531_selected_revision_atlas.tsv", revisions, list(revisions[0])
    )
    write_tsv(
        OUT / "gdt531_saiis_competing_route_atlas.tsv",
        competitor_rows,
        list(competitor_rows[0]),
    )
    write_tsv(
        OUT / "gdt531_saii_family_atlas.tsv", family_rows, list(family_rows[0])
    )
    write_tsv(
        OUT / "gdt531_remaining_working_error_atlas.tsv",
        remaining,
        list(edition[0]),
    )
    write_json(OUT / "gdt531_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
