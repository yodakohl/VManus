#!/usr/bin/env python3
"""Revise a working recipe through an exact one-character old superform peel."""

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
BASE = ROOT / "experiments/yolo/gdt530_exact_superform_peel_revision"
OUT = BASE / "artifacts"
G529_RUN = ROOT / "experiments/yolo/gdt529_nearest_terminal_m_square/src/run.py"
G529_CURRENT = (
    ROOT
    / "experiments/yolo/gdt529_nearest_terminal_m_square/artifacts"
    / "gdt529_159_m_square_rerank.tsv"
)
G529_RESULT = (
    ROOT
    / "experiments/yolo/gdt529_nearest_terminal_m_square/artifacts"
    / "gdt529_result.json"
)
G522_ATLAS = (
    ROOT
    / "experiments/yolo/gdt522_local_edit_analogy_license_reranker/artifacts"
    / "gdt522_local_edit_analogy_atlas.tsv"
)

SELECTED_SURFACE = "chekchy"
SELECTED_RECIPE = "CH+K+Y"
SELECTED_SUPERFORM = "ychekchy"
SELECTED_SUPERFORM_RECIPE = "Y+CH+K+Y"
WORKING_LITERAL_DE = "NEHMEN · GEBEN · POSTEN"
WORKING_PHRASE_DE = "Nehmen, geben und posten."


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G529 = load_module("gdt529_core_for_gdt530", G529_RUN)


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


def recipe_text(recipe: tuple[str, ...]) -> str:
    return "+".join(recipe)


def position(index: int, total: int) -> str:
    if index == 0:
        return "LEFT"
    if index + 1 == total:
        return "RIGHT"
    return "INNER"


def invariant_old_inventory(old: list[dict[str, str]]):
    recipes: dict[str, set[str]] = defaultdict(set)
    events: Counter[str] = Counter()
    pages: dict[str, set[str]] = defaultdict(set)
    registers: dict[str, set[str]] = defaultdict(set)
    event_ids: dict[str, list[str]] = defaultdict(list)
    loci: dict[str, list[str]] = defaultdict(list)
    for row in old:
        surface = row["surface"]
        recipes[surface].add(row["component_recipe"])
        events[surface] += 1
        pages[surface].add(row["physical_page"])
        registers[surface].add(row["register"])
        event_ids[surface].append(row["source_event_id"])
        loci[surface].append(row["locus"])
    forms = {
        surface: atoms(next(iter(values)))
        for surface, values in recipes.items()
        if len(values) == 1
    }
    return forms, events, pages, registers, event_ids, loci


def load_signatures() -> dict[tuple[str, str, str, str], dict[str, str]]:
    return {
        (
            row["visible_insert"],
            row["visible_position"],
            row["atom_insert"],
            row["atom_position"],
        ): row
        for row in read_tsv(G522_ATLAS)
    }


def route_strength(signature: dict[str, str]) -> str:
    support = int(signature["support_pair_count"])
    probability = float(signature["conditional_probability"])
    reliability = float(signature["reliability"])
    return (
        "STRONG_OLD_EDIT_SIGNATURE"
        if support >= 3 and probability >= 0.5 and reliability >= 0.6
        else "WEAK_OLD_EDIT_SIGNATURE"
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
    rows: list[dict] = []
    for current_row in current:
        surface = current_row["surface"]
        working = current_row["revised_working_recipe"]
        top1 = current_row["gdt529_top1"]
        roles_by_recipe: dict[str, set[str]] = defaultdict(set)
        roles_by_recipe[working].add("WORKING")
        roles_by_recipe[top1].add("TOP1")
        for candidate_recipe in sorted(roles_by_recipe):
            candidate_atoms = atoms(candidate_recipe)
            for old_surface, old_recipe in sorted(forms.items()):
                if len(old_surface) != len(surface) + 1:
                    continue
                if len(old_recipe) != len(candidate_atoms) + 1:
                    continue
                for visible_index in range(len(old_surface)):
                    if (
                        old_surface[:visible_index] + old_surface[visible_index + 1 :]
                        != surface
                    ):
                        continue
                    visible_insert = old_surface[visible_index]
                    visible_position = position(visible_index, len(old_surface))
                    for atom_index in range(len(old_recipe)):
                        if old_recipe[:atom_index] + old_recipe[atom_index + 1 :] != candidate_atoms:
                            continue
                        atom_insert = old_recipe[atom_index]
                        atom_position = position(atom_index, len(old_recipe))
                        signature = signatures.get(
                            (
                                visible_insert,
                                visible_position,
                                atom_insert,
                                atom_position,
                            )
                        )
                        if signature is None:
                            continue
                        roles = roles_by_recipe[candidate_recipe]
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
                                "old_superform_recipe": recipe_text(old_recipe),
                                "removed_visible": visible_insert,
                                "visible_index": visible_index,
                                "visible_position": visible_position,
                                "removed_atom": atom_insert,
                                "atom_index": atom_index,
                                "atom_position": atom_position,
                                "support_pair_count": int(signature["support_pair_count"]),
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
                                "route_strength": route_strength(signature),
                                "old_event_count": events[old_surface],
                                "old_pages": "|".join(sorted(pages[old_surface])),
                                "old_registers": "|".join(sorted(registers[old_surface])),
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
        ): row
        for row in rows
    }
    return sorted(
        unique.values(),
        key=lambda row: (
            row["surface"],
            row["supported_candidate_recipe"],
            row["old_superform"],
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
        working = row["revised_working_recipe"]
        top1 = row["gdt529_top1"]
        if top1 == working or surface in forms:
            continue
        strong = [
            route
            for route in routes_by_surface[surface]
            if route["route_strength"] == "STRONG_OLD_EDIT_SIGNATURE"
        ]
        top_routes = [
            route for route in strong if route["supported_candidate_recipe"] == top1
        ]
        working_routes = [
            route for route in strong if route["supported_candidate_recipe"] == working
        ]
        if not top_routes or working_routes:
            continue
        for route in top_routes:
            selected.append(
                {
                    **route,
                    "gdt529_working_rank": int(row["gdt529_revised_rank"]),
                    "gdt530_working_rank": 1,
                    "gdt530_working_recipe": top1,
                    "working_literal_de": WORKING_LITERAL_DE,
                    "working_phrase_de": WORKING_PHRASE_DE,
                    "decision": "REVISE_WORKING_RECIPE_TO_SUPPORTED_TOP1",
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


def old_chy_atlas(
    forms: dict[str, tuple[str, ...]],
    events: Counter[str],
    pages: dict[str, set[str]],
    registers: dict[str, set[str]],
    event_ids: dict[str, list[str]],
) -> list[dict]:
    rows = []
    for surface, recipe in sorted(forms.items()):
        if not surface.endswith("chy") or not recipe or recipe[-1] != "Y":
            continue
        category = (
            "TAIL_CH_PLUS_Y" if len(recipe) >= 2 and recipe[-2:] == ("CH", "Y")
            else "TAIL_Y_WITHOUT_CH"
        )
        rows.append(
            {
                "surface": surface,
                "recipe": recipe_text(recipe),
                "tail_category": category,
                "event_count": events[surface],
                "pages": "|".join(sorted(pages[surface])),
                "registers": "|".join(sorted(registers[surface])),
                "event_ids": "|".join(event_ids[surface]),
            }
        )
    return rows


def tail_category(recipe: str) -> str:
    value = atoms(recipe)
    if len(value) >= 2 and value[-2:] == ("CH", "Y"):
        return "TAIL_CH_PLUS_Y"
    if value and value[-1] == "Y":
        return "TAIL_Y_WITHOUT_CH"
    return "OTHER_TAIL"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old = read_tsv(G529.G518.G407_RUNNING)
    current = read_tsv(G529_CURRENT)
    contexts = read_tsv(G529.G518.G516_SELECTED)
    inherited_result = json.loads(G529_RESULT.read_text(encoding="utf-8"))
    forms, events, pages, registers, event_ids, loci = invariant_old_inventory(old)
    signatures = load_signatures()
    routes = enumerate_routes(
        current, forms, events, pages, registers, event_ids, loci, signatures
    )
    revisions = selected_revisions(current, routes, forms)
    revision_by_surface = {
        row["surface"]: row["gdt530_working_recipe"] for row in revisions
    }
    literal_by_surface: dict[str, str] = {}
    event_context_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in contexts:
        event_context_by_surface[row["surface"]].append(row)
        literal_by_surface.setdefault(row["surface"], row["gdt516_literal_reading_de"])

    edition = []
    for row in current:
        surface = row["surface"]
        revised_recipe = revision_by_surface.get(surface, row["revised_working_recipe"])
        revised_rank = 1 if surface in revision_by_surface else int(row["gdt529_revised_rank"])
        if surface == SELECTED_SURFACE:
            literal = WORKING_LITERAL_DE
            phrase = WORKING_PHRASE_DE
            evidence = (
                "ychekchy=Y+CH+K+Y; peel initial y/Y; "
                "old left y/Y signature 54/59; exact old ckhy=CH+K+Y"
            )
            policy = "GDT530_EXACT_SUPERFORM_PEEL_REVISION"
        else:
            literal = literal_by_surface.get(surface, "INHERITED")
            phrase = "INHERITED"
            evidence = "NO_SELECTED_SUPERFORM_PEEL_REVISION"
            policy = "INHERIT_GDT529_WORKING_RECIPE"
        edition.append(
            {
                **row,
                "gdt530_working_recipe": revised_recipe,
                "gdt530_working_rank": revised_rank,
                "gdt530_literal_reading_de": literal,
                "gdt530_short_phrase_de": phrase,
                "gdt530_evidence": evidence,
                "gdt530_policy": policy,
            }
        )

    chy_old = old_chy_atlas(forms, events, pages, registers, event_ids)
    chy_current = []
    for row in edition:
        if not row["surface"].endswith("chy"):
            continue
        contexts_for_surface = event_context_by_surface[row["surface"]]
        chy_current.append(
            {
                "surface": row["surface"],
                "pages": row["physical_pages"],
                "previous_working_recipe": row["revised_working_recipe"],
                "previous_tail_category": tail_category(row["revised_working_recipe"]),
                "gdt529_top1": row["gdt529_top1"],
                "gdt530_working_recipe": row["gdt530_working_recipe"],
                "gdt530_tail_category": tail_category(row["gdt530_working_recipe"]),
                "event_ids": "|".join(
                    value["event_id"] for value in contexts_for_surface
                ),
                "loci": "|".join(value["locus"] for value in contexts_for_surface),
                "decision": (
                    "TAIL_Y_SELECTED_BY_EXACT_SUPERFORM_PEEL"
                    if row["surface"] == SELECTED_SURFACE
                    else "INHERITED_CONTEXTUAL_CH_PLUS_Y"
                ),
            }
        )

    remaining = [row for row in edition if int(row["gdt530_working_rank"]) != 1]
    route_classes = Counter(row["route_class"] for row in routes)
    old_chy_types = Counter(row["tail_category"] for row in chy_old)
    old_chy_events = Counter()
    for row in chy_old:
        old_chy_events[row["tail_category"]] += int(row["event_count"])
    current_chy_types = Counter(row["gdt530_tail_category"] for row in chy_current)
    previous_metrics = metric(edition, "gdt529_revised_rank")
    revised_metrics = metric(edition, "gdt530_working_rank")
    selected_surfaces = sorted({row["surface"] for row in revisions})
    status = (
        "PASS_EXACT_SUPERFORM_PEEL_WORKING_REVISION"
        if len(current) == 159
        and len(forms) == 1558
        and len(routes) == 25
        and len({row["surface"] for row in routes}) == 14
        and selected_surfaces == [SELECTED_SURFACE]
        and len(revisions) == 1
        and revisions[0]["old_superform"] == SELECTED_SUPERFORM
        and revisions[0]["old_superform_recipe"] == SELECTED_SUPERFORM_RECIPE
        and revisions[0]["support_pair_count"] == 54
        and previous_metrics == inherited_result["current_revised_gdt529_metrics"]
        and revised_metrics["top1_exact_count"] == 153
        and revised_metrics["rank_sum"] == 173
        and len(remaining) == 6
        and old_chy_types == Counter(
            {"TAIL_Y_WITHOUT_CH": 28, "TAIL_CH_PLUS_Y": 26}
        )
        and old_chy_events == Counter(
            {"TAIL_Y_WITHOUT_CH": 69, "TAIL_CH_PLUS_Y": 34}
        )
        and current_chy_types == Counter(
            {"TAIL_CH_PLUS_Y": 6, "TAIL_Y_WITHOUT_CH": 1}
        )
        else "FAIL_SELECTION_GATE"
    )
    result = {
        "experiment_id": "GDT530",
        "status": status,
        "claim_ceiling": "EXPLORATORY_EXACT_SUPERFORM_PEEL_WORKING_REVISION__NO_GLOBAL_CHY_RULE_OR_CONFIRMED_PLAINTEXT",
        "selected_policy": {
            "surface_relation": "EXACT_OLD_SUPERFORM_MINUS_ONE_VISIBLE_CHARACTER",
            "recipe_relation": "EXACT_OLD_RECIPE_MINUS_ONE_ATOM",
            "edit_license": "MATCHING_GDT522_VISIBLE_AND_ATOM_POSITION_SIGNATURE",
            "candidate_requirement": "EXISTING_GDT529_TOP1",
            "working_conflict": "NO_EQUIVALENT_STRONG_ROUTE_FOR_PREVIOUS_WORKING_RECIPE",
            "old_target_conflict": "EXACT_OLD_TARGET_RECIPE_OVERRIDES_REVISION",
        },
        "old_invariant_surface_count": len(forms),
        "current_target_count": len(current),
        "licensed_superform_route_count": len(routes),
        "licensed_superform_surface_count": len({row["surface"] for row in routes}),
        "route_classes": dict(sorted(route_classes.items())),
        "selected_revision_count": len(revisions),
        "selected_surfaces": selected_surfaces,
        "selected_revision": {
            "surface": SELECTED_SURFACE,
            "previous_working_recipe": "CH+K+CH+Y",
            "new_working_recipe": SELECTED_RECIPE,
            "old_superform": SELECTED_SUPERFORM,
            "old_superform_recipe": SELECTED_SUPERFORM_RECIPE,
            "removed_visible_atom_pair": "y/Y@LEFT/LEFT",
            "old_signature_support": "54/59",
            "old_signature_probability": 0.886178862,
            "old_signature_reliability": 0.964285714,
            "independent_exact_old_recipe_surfaces": "ckhy",
            "independent_exact_old_recipe_event_count": events["ckhy"],
            "working_literal_de": WORKING_LITERAL_DE,
            "working_phrase_de": WORKING_PHRASE_DE,
        },
        "previous_working_metrics": previous_metrics,
        "gdt530_working_metrics": revised_metrics,
        "remaining_working_error_count": len(remaining),
        "remaining_surfaces": [row["surface"] for row in remaining],
        "old_chy_tail_type_counts": dict(sorted(old_chy_types.items())),
        "old_chy_tail_event_counts": dict(sorted(old_chy_events.items())),
        "current_chy_tail_type_counts": dict(sorted(current_chy_types.items())),
        "guard": "CHY_IS_CONTEXT_DEPENDENT__EXACT_SUPERFORM_PEEL_IS_NOT_A_GLOBAL_SUFFIX_RULE__NO_NEW_PAGES",
    }

    write_tsv(
        OUT / "gdt530_159_working_revision.tsv", edition, list(edition[0])
    )
    write_tsv(
        OUT / "gdt530_superform_peel_route_atlas.tsv", routes, list(routes[0])
    )
    write_tsv(
        OUT / "gdt530_selected_revision_atlas.tsv", revisions, list(revisions[0])
    )
    write_tsv(
        OUT / "gdt530_old_chy_tail_atlas.tsv", chy_old, list(chy_old[0])
    )
    write_tsv(
        OUT / "gdt530_current_chy_tail_atlas.tsv", chy_current, list(chy_current[0])
    )
    write_tsv(
        OUT / "gdt530_remaining_working_error_atlas.tsv",
        remaining,
        list(edition[0]),
    )
    write_json(OUT / "gdt530_result.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
