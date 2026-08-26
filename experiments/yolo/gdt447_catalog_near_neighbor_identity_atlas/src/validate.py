#!/usr/bin/env python3
"""Validate GDT447's bounded exact-identity near-neighbour atlas."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import subprocess
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    tracked = [
        OUT / "gdt447_5499_atom_deletion_neighbors.tsv",
        OUT / "gdt447_3936_adjacent_swap_neighbors.tsv",
        OUT / "gdt447_action_substitution_neighbors.tsv",
        OUT / "gdt447_nonaction_substitution_neighbors.tsv",
        OUT / "gdt447_target_collision_summary.tsv",
        OUT / "gdt447_mutation_family_summary.tsv",
        OUT / "gdt447_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    deletions = read_tsv(tracked[0])
    swaps = read_tsv(tracked[1])
    action_subs = read_tsv(tracked[2])
    other_subs = read_tsv(tracked[3])
    collisions = read_tsv(tracked[4])
    family_summary = read_tsv(tracked[5])
    result = json.loads(tracked[6].read_text(encoding="utf-8"))
    rows = deletions + swaps + action_subs + other_subs
    catalog = {row["component_recipe"]: row for row in read_tsv(CATALOG)}
    factor_family = {row["atom"]: row["factor_family"] for row in read_tsv(COMPONENTS)}
    certifier = load_module("gdt446_certifier_for_gdt447_validation", CERTIFIER_PATH)

    mutation_validity: list[bool] = []
    for row in rows:
        source = row["source_recipe"].split("+")
        positions = row["mutation_positions"].split("|")
        valid = True
        for position in positions:
            if row["mutation_family"] == "ATOM_DELETION":
                index = int(position) - 1
                expected = "+".join(source[:index] + source[index + 1:]) or "EMPTY_RECIPE"
            elif row["mutation_family"] == "ADJACENT_SWAP":
                left, right = (int(value) - 1 for value in position.split("-"))
                target = source[:]
                target[left], target[right] = target[right], target[left]
                expected = "+".join(target)
            else:
                index = int(position) - 1
                target = source[:]
                target[index] = row["target_atom_or_pair"]
                expected = "+".join(target)
                valid = valid and factor_family[source[index]] == factor_family[target[index]] == row["substitution_class"]
            valid = valid and expected == row["target_recipe"]
        mutation_validity.append(valid)

    target_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        target_rows[row["target_recipe"]].append(row)
    recomputed_targets: dict[str, tuple[str, str, str, str]] = {}
    for target in target_rows:
        if target == "EMPTY_RECIPE":
            recomputed_targets[target] = (
                "IDENTITY_NEW_VISIBLE_RECIPE", "STOP", "EXECUTION_STOP_EMPTY_RECIPE", "EMPTY_RECIPE"
            )
        else:
            certificate = certifier.issue_split_certificate(target)
            recomputed_targets[target] = (
                str(certificate["identity_route"]),
                str(certificate["execution_decision"]),
                str(certificate["execution_route"]),
                str(certificate["blocked_factor_rules"]),
            )
    target_recompute_ok = all(
        all((
            row["target_identity_route"], row["target_execution_decision"],
            row["target_execution_route"], row["target_blocked_factor_rules"],
        ) == recomputed_targets[target] for row in target_rows[target])
        for target in target_rows
    )

    exact_rows = [row for row in rows if row["target_is_exact_catalog_key"] == "YES"]
    new_rows = [row for row in rows if row["target_is_exact_catalog_key"] == "NO"]
    identity_equivalence = all(
        (row["target_recipe"] in catalog) == (row["target_is_exact_catalog_key"] == "YES")
        and (row["target_recipe"] in catalog) == (row["target_identity_route"] != "IDENTITY_NEW_VISIBLE_RECIPE")
        for row in rows
    )
    collision_by_target = {row["target_recipe"]: row for row in collisions}
    collision_recompute = all(
        target in collision_by_target
        and int(collision_by_target[target]["neighbor_row_count"]) == len(target_rows[target])
        and int(collision_by_target[target]["distinct_source_recipe_count"]) == len({row["source_recipe"] for row in target_rows[target]})
        and collision_by_target[target]["target_identity_route"] == target_rows[target][0]["target_identity_route"]
        and collision_by_target[target]["target_execution_decision"] == target_rows[target][0]["target_execution_decision"]
        for target in target_rows
    )
    summary_by_family = {row["mutation_family"]: row for row in family_summary}
    family_counts = Counter(row["mutation_family"] for row in rows)
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)

    checks = {
        "source_catalog_1563": len(catalog) == 1563,
        "neighbor_30763_unique": len(rows) == len({row["neighbor_id"] for row in rows}) == 30763,
        "neighbor_source_family_target_unique": len(rows) == len({(row["source_recipe"], row["mutation_family"], row["target_recipe"]) for row in rows}),
        "all_source_recipes_cataloged": {row["source_recipe"] for row in rows} == set(catalog),
        "family_counts_5499_3936_21328": family_counts == {"ATOM_DELETION": 5499, "ADJACENT_SWAP": 3936, "SAME_CLASS_SUBSTITUTION": 21328},
        "substitution_split_15240_6088": len(action_subs) == 15240 and len(other_subs) == 6088,
        "mutation_derivations_exact": all(mutation_validity),
        "target_count_19807": len(target_rows) == len(collisions) == 19807,
        "target_recompute_exact": target_recompute_ok,
        "identity_iff_exact_catalog_membership": identity_equivalence,
        "exact_neighbor_count_6372": len(exact_rows) == 6372,
        "new_neighbor_count_24391": len(new_rows) == 24391,
        "unique_exact_target_1073": len({row["target_recipe"] for row in exact_rows}) == 1073,
        "unique_new_target_18734": len({row["target_recipe"] for row in new_rows}) == 18734,
        "source_with_exact_neighbor_1313": len({row["source_recipe"] for row in exact_rows}) == 1313,
        "new_execution_19792_941_3658": Counter(row["target_execution_decision"] for row in new_rows) == {"READ": 19792, "READ_AMBER": 941, "STOP": 3658},
        "exact_execution_6107_179_86": Counter(row["target_execution_decision"] for row in exact_rows) == {"READ": 6107, "READ_AMBER": 179, "STOP": 86},
        "collision_summary_complete": set(collision_by_target) == set(target_rows),
        "collision_summary_recomputes": collision_recompute,
        "collision_targets_3955": sum(int(row["distinct_source_recipe_count"]) > 1 for row in collisions) == 3955,
        "maximum_sources_per_target_39": max(int(row["distinct_source_recipe_count"]) for row in collisions) == 39,
        "family_summary_three": len(family_summary) == len(summary_by_family) == 3,
        "family_summary_counts": all(int(summary_by_family[family]["neighbor_count"]) == count for family, count in family_counts.items()),
        "no_fuzzy_identity_leak": all(not (row["target_is_exact_catalog_key"] == "NO" and row["target_identity_route"] != "IDENTITY_NEW_VISIBLE_RECIPE") for row in rows),
        "no_source_identity_carry": all(row["source_identity_retained_without_exact_target"] == "NO" for row in rows),
        "no_fuzzy_matcher": all(row["fuzzy_identity_matching_used"] == "NO" for row in rows + collisions),
        "no_meaning_revision": all(row["meaning_revision"] == "NO" for row in rows),
        "no_surface_prediction": all(row["surface_prediction"] == "NO" for row in rows),
        "result_status_exact": result["status"] == "EXACT_IDENTITY_NEVER_LEAKS_TO_THIRTY_THOUSAND_SEVEN_HUNDRED_SIXTY_THREE_NEAR_NEIGHBORS",
        "result_counts_exact": result["catalog_source_key_count"] == 1563 and result["neighbor_count"] == 30763 and result["deletion_neighbor_count"] == 5499 and result["adjacent_swap_neighbor_count"] == 3936 and result["same_class_substitution_neighbor_count"] == 21328 and result["exact_target_neighbor_count"] == 6372 and result["new_target_neighbor_count"] == 24391 and result["unique_target_count"] == 19807,
        "result_no_leak": result["fuzzy_identity_leak_count"] == result["source_identity_carry_count"] == result["fuzzy_matching_use_count"] == 0,
        "result_no_expansion": result["meaning_revisions"] == result["surface_predictions"] == result["occurrence_predictions"] == result["new_pages"] == 0,
        "no_forbidden_folio_token": re.search(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", output_text) is None,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt447_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
