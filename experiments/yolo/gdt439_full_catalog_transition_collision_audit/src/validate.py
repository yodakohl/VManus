#!/usr/bin/env python3
"""Validate the complete GDT439 transition-signature audit."""

from __future__ import annotations

import csv
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
BASE = ROOT / "experiments/yolo/gdt439_full_catalog_transition_collision_audit"
OUT = BASE / "artifacts"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt439_1563_transition_signatures.tsv",
        OUT / "gdt439_collision_groups.tsv",
        OUT / "gdt439_collision_members.tsv",
        OUT / "gdt439_collision_register_samples.tsv",
        OUT / "gdt439_order_permutation_pairs.tsv",
        OUT / "gdt439_tier_summary.tsv",
        OUT / "gdt439_main_deck_external_collisions.tsv",
        OUT / "gdt439_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    signatures = read_tsv(tracked[0])
    groups = read_tsv(tracked[1])
    members = read_tsv(tracked[2])
    samples = read_tsv(tracked[3])
    permutations = read_tsv(tracked[4])
    tiers = read_tsv(tracked[5])
    main = read_tsv(tracked[6])
    result = json.loads(tracked[7].read_text(encoding="utf-8"))
    catalog = read_tsv(CATALOG)

    recipes = {row["component_recipe"] for row in signatures}
    catalog_recipes = {row["component_recipe"] for row in catalog}
    signature_groups: dict[str, list[str]] = defaultdict(list)
    for row in signatures:
        signature_groups[row["full_transition_signature_sha256"]].append(row["component_recipe"])
    recomputed_collision_sets = [set(values) for values in signature_groups.values() if len(values) > 1]
    published_collision_sets = [set(row["component_recipes"].split("|")) for row in groups]
    member_by_group: dict[str, set[str]] = defaultdict(set)
    for row in members:
        member_by_group[row["collision_group_id"]].add(row["component_recipe"])
    sample_counts = Counter(row["collision_group_id"] for row in samples)
    tier_counts = {row["intake_tier"]: int(row["recipe_count"]) for row in tiers}
    expected_tiers = {
        "T0_EXACT_OBSERVED": 1268, "T1_FUTURE_HIGH": 4,
        "T2_FUTURE_STRONG": 43, "T3_SECOND_RING_AMBER": 2,
        "T4_NARROW_APPENDIX": 246,
    }
    main_tiers = {"T1_FUTURE_HIGH", "T2_FUTURE_STRONG", "T3_SECOND_RING_AMBER"}
    main_recipes = {row["component_recipe"] for row in catalog if row["intake_tier"] in main_tiers}
    collision_members = {recipe for values in recomputed_collision_sets for recipe in values}
    collision_pairs = sum(len(values) * (len(values) - 1) // 2 for values in recomputed_collision_sets)
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)

    checks = {
        "signature_rows_1563_unique": len(signatures) == len(recipes) == 1563,
        "signature_recipes_match_catalog": recipes == catalog_recipes,
        "signature_cells_245": all(int(row["transition_cell_count"]) == 245 and int(row["reachable_state_count"]) == 49 and int(row["register_count"]) == 5 for row in signatures),
        "unique_signature_count_1449": len(signature_groups) == 1449,
        "collision_groups_104_unique": len(groups) == len({row["collision_group_id"] for row in groups}) == 104,
        "collision_sets_match_signatures": {frozenset(values) for values in recomputed_collision_sets} == {frozenset(values) for values in published_collision_sets},
        "collision_vectors_exact": all(row["exact_vector_equality"] == "YES" for row in groups),
        "collision_members_218_unique": len(members) == len({row["component_recipe"] for row in members}) == 218,
        "collision_membership_matches_groups": all(member_by_group[row["collision_group_id"]] == set(row["component_recipes"].split("|")) for row in groups),
        "collision_member_union_exact": {row["component_recipe"] for row in members} == collision_members,
        "collision_pairs_125": collision_pairs == 125,
        "largest_group_four": max(int(row["recipe_count"]) for row in groups) == 4,
        "collision_group_types_76_28": Counter(row["same_atom_multiset"] for row in groups) == {"YES": 76, "NO": 28},
        "collision_samples_five_each": len(samples) == 520 and set(sample_counts.values()) == {5},
        "collision_samples_registers": {row["register"] for row in samples} == {"SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"},
        "permutation_pairs_155_unique": len(permutations) == 155 and len({(row["left_recipe"], row["right_recipe"]) for row in permutations}) == 155,
        "permutation_full_collisions_82": sum(row["same_full_transition_signature"] == "YES" for row in permutations) == 82,
        "full_collision_implies_clause_and_state": all(row["same_clause_signature"] == row["same_state_signature"] == "YES" for row in permutations if row["same_full_transition_signature"] == "YES"),
        "tier_counts_exact": tier_counts == expected_tiers and sum(tier_counts.values()) == 1563,
        "tier_signature_counts_valid": all(int(row["unique_full_signature_count_within_tier"]) <= int(row["recipe_count"]) for row in tiers),
        "main_external_rows_five": len(main) == 5 and len({row["collision_group_id"] for row in main}) == 5,
        "main_collision_members_five": {recipe for row in main for recipe in row["main_future_recipes"].split("|")} == main_recipes & collision_members,
        "no_main_internal_collision": all(row["main_internal_collision"] == "NO" for row in main),
        "main_repair_routes_four_one": Counter(row["repair_route"] for row in main) == {"PRESERVE_TOP_LEVEL_WRITTEN_ORDER": 4, "PRESERVE_LOCAL_CHANNEL_CONTRAST": 1},
        "order_repaired_recipes_47": sum(int(row["order_repaired_cell_count"]) > 0 for row in signatures) == 47,
        "result_status_exact": result["status"] == "MAIN_DECK_UNIQUE__FULL_CATALOG_COLLISIONS_LOCALIZED",
        "result_inventory_exact": result["catalog_recipe_count"] == 1563 and result["reachable_state_count"] == 49 and result["register_count"] == 5 and result["transition_cell_count"] == 382935,
        "result_signature_counts_exact": result["unique_full_transition_signature_count"] == 1449 and result["collision_group_count"] == 104 and result["collision_member_recipe_count"] == 218 and result["collision_free_recipe_count"] == 1345 and result["collision_recipe_pair_count"] == 125,
        "result_main_counts_exact": result["main_future_card_count"] == 49 and result["main_future_collision_member_count"] == result["main_external_collision_group_count"] == 5 and result["main_internal_collision_group_count"] == 0,
        "result_route_counts_exact": result["main_order_repair_candidate_count"] == 4 and result["main_local_channel_contrast_candidate_count"] == 1,
        "result_no_expansion": result["meaning_revisions"] == result["surface_predictions"] == result["new_pages"] == 0,
        "no_forbidden_folio_token": re.search(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", output_text) is None,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {"status": "PASS" if not failed else "FAIL", "check_count": len(checks), "failure_count": len(failed), "checks": checks}
    (OUT / "gdt439_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
