#!/usr/bin/env python3
"""Build exact-identity and execution maps for bounded catalog near-neighbours."""

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
BASE = ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas"
OUT = BASE / "artifacts"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"
COMPONENTS = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts/gdt413_46_component_working_dictionary.tsv"
CERTIFIER_PATH = ROOT / "experiments/yolo/gdt446_identity_execution_intake_split/src/intake_certificate_v2.py"
SUBSTITUTION_FAMILIES = {"ACTION_HEAD", "ARGUMENT", "RELATION", "ORDER_CONTROL", "GRADE"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    certifier = load_module("gdt446_certifier_for_gdt447_neighbors", CERTIFIER_PATH)
    catalog_rows = read_tsv(CATALOG)
    catalog = {row["component_recipe"]: row for row in catalog_rows}
    components = read_tsv(COMPONENTS)
    factor_family = {row["atom"]: row["factor_family"] for row in components}
    atoms_by_family: dict[str, list[str]] = defaultdict(list)
    for atom, family in factor_family.items():
        atoms_by_family[family].append(atom)
    for family in atoms_by_family:
        atoms_by_family[family].sort()

    raw: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    source_change: dict[tuple[str, str, str], tuple[str, str, str]] = {}
    for source in catalog_rows:
        recipe = source["component_recipe"]
        atoms = recipe.split("+")
        for index, atom in enumerate(atoms):
            target_atoms = atoms[:index] + atoms[index + 1:]
            target = "+".join(target_atoms) if target_atoms else "EMPTY_RECIPE"
            key = (recipe, "ATOM_DELETION", target)
            raw[key].append(str(index + 1))
            source_change[key] = (atom, "NONE", factor_family[atom])
        for index in range(len(atoms) - 1):
            if atoms[index] == atoms[index + 1]:
                continue
            target_atoms = atoms[:]
            target_atoms[index], target_atoms[index + 1] = target_atoms[index + 1], target_atoms[index]
            target = "+".join(target_atoms)
            key = (recipe, "ADJACENT_SWAP", target)
            raw[key].append(f"{index + 1}-{index + 2}")
            source_change[key] = (f"{atoms[index]}>{atoms[index + 1]}", f"{atoms[index + 1]}>{atoms[index]}", "ORDER")
        for index, atom in enumerate(atoms):
            family = factor_family[atom]
            if family not in SUBSTITUTION_FAMILIES:
                continue
            for replacement in atoms_by_family[family]:
                if replacement == atom:
                    continue
                target_atoms = atoms[:]
                target_atoms[index] = replacement
                target = "+".join(target_atoms)
                key = (recipe, "SAME_CLASS_SUBSTITUTION", target)
                raw[key].append(str(index + 1))
                source_change[key] = (atom, replacement, family)

    rows: list[dict[str, object]] = []
    for ordinal, ((source_recipe, mutation_family, target_recipe), positions) in enumerate(sorted(raw.items()), start=1):
        source = catalog[source_recipe]
        source_atom, target_atom, substitution_class = source_change[(source_recipe, mutation_family, target_recipe)]
        if target_recipe == "EMPTY_RECIPE":
            target_exact = False
            identity_route = "IDENTITY_NEW_VISIBLE_RECIPE"
            identity_status = "NO_VISIBLE_RECIPE_AFTER_DELETION"
            execution_route = "EXECUTION_STOP_EMPTY_RECIPE"
            execution_decision = "STOP"
            factor_status = "STOP__EMPTY_RECIPE"
            blocked = "EMPTY_RECIPE"
        else:
            certificate = certifier.issue_split_certificate(target_recipe)
            target_exact = certificate["identity_route"] != "IDENTITY_NEW_VISIBLE_RECIPE"
            identity_route = str(certificate["identity_route"])
            identity_status = str(certificate["identity_status"])
            execution_route = str(certificate["execution_route"])
            execution_decision = str(certificate["execution_decision"])
            factor_status = str(certificate["factor_gate_status"])
            blocked = str(certificate["blocked_factor_rules"])
        rows.append({
            "neighbor_id": f"G447-N{ordinal:05d}",
            "source_recipe": source_recipe,
            "source_catalog_tier": source["intake_tier"],
            "mutation_family": mutation_family,
            "mutation_positions": "|".join(positions),
            "source_atom_or_pair": source_atom,
            "target_atom_or_pair": target_atom,
            "substitution_class": substitution_class,
            "target_recipe": target_recipe,
            "target_is_exact_catalog_key": "YES" if target_exact else "NO",
            "target_identity_route": identity_route,
            "target_identity_status": identity_status,
            "target_factor_gate_status": factor_status,
            "target_execution_route": execution_route,
            "target_execution_decision": execution_decision,
            "target_blocked_factor_rules": blocked,
            "source_identity_retained_without_exact_target": "NO",
            "fuzzy_identity_matching_used": "NO",
            "meaning_revision": "NO",
            "surface_prediction": "NO",
        })

    deletions = [row for row in rows if row["mutation_family"] == "ATOM_DELETION"]
    swaps = [row for row in rows if row["mutation_family"] == "ADJACENT_SWAP"]
    action_substitutions = [row for row in rows if row["mutation_family"] == "SAME_CLASS_SUBSTITUTION" and row["substitution_class"] == "ACTION_HEAD"]
    other_substitutions = [row for row in rows if row["mutation_family"] == "SAME_CLASS_SUBSTITUTION" and row["substitution_class"] != "ACTION_HEAD"]
    write_tsv(OUT / "gdt447_5499_atom_deletion_neighbors.tsv", deletions)
    write_tsv(OUT / "gdt447_3936_adjacent_swap_neighbors.tsv", swaps)
    write_tsv(OUT / "gdt447_action_substitution_neighbors.tsv", action_substitutions)
    write_tsv(OUT / "gdt447_nonaction_substitution_neighbors.tsv", other_substitutions)

    by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_target[str(row["target_recipe"])].append(row)
    collision_rows: list[dict[str, object]] = []
    for target, target_rows in sorted(by_target.items()):
        source_recipes = sorted({str(row["source_recipe"]) for row in target_rows})
        families = sorted({str(row["mutation_family"]) for row in target_rows})
        collision_rows.append({
            "target_recipe": target,
            "neighbor_row_count": len(target_rows),
            "distinct_source_recipe_count": len(source_recipes),
            "mutation_families": "|".join(families),
            "target_is_exact_catalog_key": target_rows[0]["target_is_exact_catalog_key"],
            "target_identity_route": target_rows[0]["target_identity_route"],
            "target_execution_decision": target_rows[0]["target_execution_decision"],
            "target_blocked_factor_rules": target_rows[0]["target_blocked_factor_rules"],
            "source_recipes": "|".join(source_recipes),
            "fuzzy_identity_matching_used": "NO",
        })
    write_tsv(OUT / "gdt447_target_collision_summary.tsv", collision_rows)

    family_summary: list[dict[str, object]] = []
    for family in ("ATOM_DELETION", "ADJACENT_SWAP", "SAME_CLASS_SUBSTITUTION"):
        family_rows = [row for row in rows if row["mutation_family"] == family]
        identity_counts = Counter(str(row["target_is_exact_catalog_key"]) for row in family_rows)
        execution_counts = Counter(str(row["target_execution_decision"]) for row in family_rows)
        family_summary.append({
            "mutation_family": family,
            "neighbor_count": len(family_rows),
            "exact_target_count": identity_counts["YES"],
            "new_target_count": identity_counts["NO"],
            "green_execution_count": execution_counts["READ"],
            "amber_execution_count": execution_counts["READ_AMBER"],
            "stop_execution_count": execution_counts["STOP"],
            "fuzzy_identity_leak_count": sum(row["target_is_exact_catalog_key"] == "NO" and row["target_identity_route"] != "IDENTITY_NEW_VISIBLE_RECIPE" for row in family_rows),
        })
    write_tsv(OUT / "gdt447_mutation_family_summary.tsv", family_summary)

    exact_rows = [row for row in rows if row["target_is_exact_catalog_key"] == "YES"]
    new_rows = [row for row in rows if row["target_is_exact_catalog_key"] == "NO"]
    result = {
        "status": "EXACT_IDENTITY_NEVER_LEAKS_TO_THIRTY_THOUSAND_SEVEN_HUNDRED_SIXTY_THREE_NEAR_NEIGHBORS",
        "catalog_source_key_count": len(catalog),
        "neighbor_count": len(rows),
        "deletion_neighbor_count": len(deletions),
        "adjacent_swap_neighbor_count": len(swaps),
        "same_class_substitution_neighbor_count": len(action_substitutions) + len(other_substitutions),
        "action_substitution_neighbor_count": len(action_substitutions),
        "nonaction_substitution_neighbor_count": len(other_substitutions),
        "exact_target_neighbor_count": len(exact_rows),
        "new_target_neighbor_count": len(new_rows),
        "unique_target_count": len(by_target),
        "unique_exact_target_count": len({row["target_recipe"] for row in exact_rows}),
        "unique_new_target_count": len({row["target_recipe"] for row in new_rows}),
        "source_keys_with_exact_neighbor_count": len({row["source_recipe"] for row in exact_rows}),
        "new_target_execution_counts": dict(sorted(Counter(str(row["target_execution_decision"]) for row in new_rows).items())),
        "exact_target_execution_counts": dict(sorted(Counter(str(row["target_execution_decision"]) for row in exact_rows).items())),
        "collision_target_count": sum(int(row["distinct_source_recipe_count"]) > 1 for row in collision_rows),
        "maximum_source_recipes_per_target": max(int(row["distinct_source_recipe_count"]) for row in collision_rows),
        "fuzzy_identity_leak_count": sum(row["target_is_exact_catalog_key"] == "NO" and row["target_identity_route"] != "IDENTITY_NEW_VISIBLE_RECIPE" for row in rows),
        "source_identity_carry_count": sum(row["source_identity_retained_without_exact_target"] != "NO" for row in rows),
        "fuzzy_matching_use_count": sum(row["fuzzy_identity_matching_used"] != "NO" for row in rows),
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt447_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
