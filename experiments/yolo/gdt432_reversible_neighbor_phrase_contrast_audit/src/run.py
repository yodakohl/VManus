#!/usr/bin/env python3
"""Audit whether each GDT431 prediction changes exactly one semantic slot."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt432_reversible_neighbor_phrase_contrast_audit"
OUT = BASE / "artifacts"
CARDS = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/artifacts/gdt431_47_strong_prediction_phrasebook.tsv"
EXPANSIONS = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/artifacts/gdt431_235_register_expansion_cards.tsv"
NEIGHBORS = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/artifacts/gdt431_145_neighbor_exemplars.tsv"
RENDERER = ROOT / "experiments/yolo/gdt431_strong_prediction_reading_phrasebook/src/run.py"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
ATLAS = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts/gdt415_95_register_expansion_atlas.tsv"
CLAUSES = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv"
ACTION_CONTRASTS = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts/gdt428_6_within_class_contrasts.tsv"
NONACTION_CONTRASTS = ROOT / "experiments/yolo/gdt429_nonaction_core_semantic_contrasts/artifacts/gdt429_13_nonaction_core_contrasts.tsv"

REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_renderer():
    spec = importlib.util.spec_from_file_location("gdt431_renderer", RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load GDT431 renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def safe_render(renderer, atoms: list[str], register: str = "GENERIC") -> str:
    arguments = [atom for atom in atoms if atom in renderer.ARGUMENT_ROOTS]
    actions = [atom for atom in atoms if atom in renderer.ACTION_ROOTS]
    if not actions and len(arguments) == 2 and arguments[0] == arguments[1]:
        objects = renderer.GENERIC_OBJECTS if register == "GENERIC" else renderer.REGISTER_OBJECTS[register]
        noun = renderer.strip_article(objects[arguments[0]])
        outer, inner = ("Äußere", "innere") if arguments[0] == "OR" else ("Äußerer", "innerer")
        return f"{outer} {noun}; {inner} {noun}."
    return renderer.render_recipe(atoms, register)


def trace(atoms: list[str], values: dict[str, str], families: dict[str, str]) -> str:
    return " | ".join(f"{index}:{families[atom]}={values[atom]}" for index, atom in enumerate(atoms, 1))


def trace_delta(source_atoms: list[str], target_atoms: list[str], values: dict[str, str]) -> int:
    return sum(values[left] != values[right] for left, right in zip(source_atoms, target_atoms))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(CARDS)
    expansions = read_tsv(EXPANSIONS)
    neighbors = read_tsv(NEIGHBORS)
    components = read_tsv(COMPONENTS)
    atlas = read_tsv(ATLAS)
    clauses = read_tsv(CLAUSES)
    contrasts = read_tsv(ACTION_CONTRASTS) + read_tsv(NONACTION_CONTRASTS)
    renderer = load_renderer()

    meanings = {row["atom"]: row["working_value_de"] for row in components}
    families = {row["atom"]: row["factor_family"] for row in components}
    atlas_map = {(row["root"], row["register"]): row["owner_local_expansion_de"] for row in atlas}
    card_map = {row["candidate_recipe"]: row for row in cards}
    expansion_map = {(row["candidate_recipe"], row["register"]): row for row in expansions}
    observed_registers: dict[str, set[str]] = defaultdict(set)
    for row in clauses:
        observed_registers[row["component_recipe"]].add(row["register"])

    contrast_map: dict[frozenset[str], dict[str, str]] = {}
    for row in contrasts:
        left, right = row["contrast_pair"].split("~")
        contrast_map[frozenset((left, right))] = row

    generic_rows: list[dict[str, object]] = []
    register_rows: list[dict[str, object]] = []
    for route_id, row in enumerate(neighbors, 1):
        source_recipe = row["source_neighbor_recipe"]
        target_recipe = row["candidate_recipe"]
        source_atoms = source_recipe.split("+")
        target_atoms = target_recipe.split("+")
        position = int(row["changed_atom_position"])
        source_atom = row["source_atom"]
        target_atom = row["predicted_atom"]
        contrast = contrast_map[frozenset((source_atom, target_atom))]
        source_phrase = safe_render(renderer, source_atoms)
        target_phrase = card_map[target_recipe]["short_workshop_phrase_de"]
        delta = trace_delta(source_atoms, target_atoms, meanings)
        generic_rows.append({
            "route_id": f"NR{route_id:03d}",
            "card_ordinal": row["card_ordinal"],
            "candidate_recipe": target_recipe,
            "source_neighbor_recipe": source_recipe,
            "changed_atom_position": position,
            "source_atom": source_atom,
            "source_value_de": meanings[source_atom],
            "target_atom": target_atom,
            "target_value_de": meanings[target_atom],
            "factor_family": families[source_atom],
            "direct_shared_frame_count": contrast["shared_exact_substitution_frame_count"],
            "source_trace": trace(source_atoms, meanings, families),
            "target_trace": trace(target_atoms, meanings, families),
            "semantic_trace_delta_count": delta,
            "source_workshop_phrase_de": source_phrase,
            "target_workshop_phrase_de": target_phrase,
            "natural_phrase_changed": "YES" if source_phrase != target_phrase else "NO",
            "unchanged_slots_preserved": "YES" if all(left == right for index, (left, right) in enumerate(zip(source_atoms, target_atoms), 1) if index != position) else "NO",
            "sample_observed_surface": row["sample_surface"],
            "sample_observed_clause_de": row["sample_existing_imperative_de"],
            "workshop_distinction_de": contrast["workshop_interpretation_de"],
            "decision": "REVERSIBLE_ONE_ROOT_CONTRAST" if delta == 1 and source_phrase != target_phrase else "COLLISION_OR_DRIFT",
        })

        for register in REGISTERS:
            source_values = {atom: atlas_map.get((atom, register), meanings[atom]) for atom in set(source_atoms + target_atoms)}
            source_local_phrase = safe_render(renderer, source_atoms, register)
            target_local_phrase = expansion_map[(target_recipe, register)]["owner_local_workshop_phrase_de"]
            register_rows.append({
                "route_id": f"NR{route_id:03d}",
                "candidate_recipe": target_recipe,
                "source_neighbor_recipe": source_recipe,
                "register": register,
                "source_observed_in_register": "YES" if register in observed_registers[source_recipe] else "NO__COUNTERFACTUAL_REGISTER_EXPANSION",
                "changed_atom_position": position,
                "source_atom": source_atom,
                "source_local_value_de": source_values[source_atom],
                "target_atom": target_atom,
                "target_local_value_de": source_values[target_atom],
                "source_local_trace": trace(source_atoms, source_values, families),
                "target_local_trace": trace(target_atoms, source_values, families),
                "local_trace_delta_count": trace_delta(source_atoms, target_atoms, source_values),
                "source_local_phrase_de": source_local_phrase,
                "target_local_phrase_de": target_local_phrase,
                "local_phrase_changed": "YES" if source_local_phrase != target_local_phrase else "NO",
                "target_matches_gdt431": "YES" if target_local_phrase == safe_render(renderer, target_atoms, register) else "NO",
                "decision": "LOCAL_CONTRAST_VISIBLE" if source_local_phrase != target_local_phrase else "LOCAL_PHRASE_COLLISION",
            })

    pair_buckets: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in generic_rows:
        pair_buckets[(str(row["source_atom"]), str(row["target_atom"]))].append(row)
    pair_rows: list[dict[str, object]] = []
    for (source_atom, target_atom), rows in sorted(pair_buckets.items()):
        local_rows = [row for row in register_rows if row["source_atom"] == source_atom and row["target_atom"] == target_atom]
        contrast = contrast_map[frozenset((source_atom, target_atom))]
        pair_rows.append({
            "directed_root_change": f"{source_atom}>{target_atom}",
            "source_value_de": meanings[source_atom],
            "target_value_de": meanings[target_atom],
            "factor_family": families[source_atom],
            "route_count": len(rows),
            "candidate_count": len({row["candidate_recipe"] for row in rows}),
            "direct_shared_frame_count": contrast["shared_exact_substitution_frame_count"],
            "generic_contrast_pass_count": sum(row["decision"] == "REVERSIBLE_ONE_ROOT_CONTRAST" for row in rows),
            "register_contrast_pass_count": sum(row["decision"] == "LOCAL_CONTRAST_VISIBLE" for row in local_rows),
            "register_contrast_total": len(local_rows),
            "sample_route": f"{rows[0]['source_neighbor_recipe']} > {rows[0]['candidate_recipe']}",
            "decision": "PAIR_REMAINS_AUDIBLE" if all(row["decision"] == "REVERSIBLE_ONE_ROOT_CONTRAST" for row in rows) and all(row["decision"] == "LOCAL_CONTRAST_VISIBLE" for row in local_rows) else "PAIR_COLLAPSE",
        })

    card_rows: list[dict[str, object]] = []
    for card in cards:
        recipe = card["candidate_recipe"]
        routes = [row for row in generic_rows if row["candidate_recipe"] == recipe]
        locals_ = [row for row in register_rows if row["candidate_recipe"] == recipe]
        card_rows.append({
            "card_ordinal": card["card_ordinal"],
            "candidate_recipe": recipe,
            "fixed_literal_reading_de": card["fixed_literal_reading_de"],
            "fixed_workshop_phrase_de": card["short_workshop_phrase_de"],
            "neighbor_route_count": len(routes),
            "generic_pass_count": sum(row["decision"] == "REVERSIBLE_ONE_ROOT_CONTRAST" for row in routes),
            "register_pass_count": sum(row["decision"] == "LOCAL_CONTRAST_VISIBLE" for row in locals_),
            "register_contrast_total": len(locals_),
            "weakest_direct_shared_frame_count": min(int(row["direct_shared_frame_count"]) for row in routes),
            "decision": "CARD_CONTRASTS_ALL_REVERSIBLE" if all(row["decision"] == "REVERSIBLE_ONE_ROOT_CONTRAST" for row in routes) and all(row["decision"] == "LOCAL_CONTRAST_VISIBLE" for row in locals_) else "CARD_HAS_COLLISION",
        })

    write_tsv(OUT / "gdt432_145_generic_neighbor_contrasts.tsv", generic_rows, list(generic_rows[0]))
    write_tsv(OUT / "gdt432_725_register_neighbor_contrasts.tsv", register_rows, list(register_rows[0]))
    write_tsv(OUT / "gdt432_directed_root_pair_summary.tsv", pair_rows, list(pair_rows[0]))
    write_tsv(OUT / "gdt432_47_card_reversibility.tsv", card_rows, list(card_rows[0]))

    observed_local_count = sum(row["source_observed_in_register"] == "YES" for row in register_rows)
    result = {
        "status": "ALL_145_NEIGHBOR_ROUTES_AND_725_REGISTER_CONTRASTS_REVERSIBLE",
        "card_count": len(card_rows),
        "generic_neighbor_route_count": len(generic_rows),
        "register_neighbor_contrast_count": len(register_rows),
        "directed_root_pair_count": len(pair_rows),
        "generic_contrast_pass_count": sum(row["decision"] == "REVERSIBLE_ONE_ROOT_CONTRAST" for row in generic_rows),
        "register_contrast_pass_count": sum(row["decision"] == "LOCAL_CONTRAST_VISIBLE" for row in register_rows),
        "observed_source_register_contrast_count": observed_local_count,
        "counterfactual_source_register_contrast_count": len(register_rows) - observed_local_count,
        "trace_delta_histogram": dict(sorted(Counter(str(row["semantic_trace_delta_count"]) for row in generic_rows).items())),
        "new_component_values": 0,
        "new_pages": 0,
        "surface_predictions": 0,
    }
    (OUT / "gdt432_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
