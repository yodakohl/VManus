#!/usr/bin/env python3
"""Validate GDT440's dual-channel exact-order reader."""

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
BASE = ROOT / "experiments/yolo/gdt440_dual_channel_order_trace_reader"
OUT = BASE / "artifacts"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"
OLD_GROUPS = ROOT / "experiments/yolo/gdt439_full_catalog_transition_collision_audit/artifacts/gdt439_collision_groups.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt440_1563_dual_channel_signatures.tsv",
        OUT / "gdt440_remaining_co_valued_channel_groups.tsv",
        OUT / "gdt440_104_collision_resolutions.tsv",
        OUT / "gdt440_five_main_collision_resolutions.tsv",
        OUT / "gdt440_4576_dual_channel_stream_readings.tsv",
        OUT / "gdt440_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    signatures = read_tsv(tracked[0])
    remaining = read_tsv(tracked[1])
    resolutions = read_tsv(tracked[2])
    main = read_tsv(tracked[3])
    events = read_tsv(tracked[4])
    result = json.loads(tracked[5].read_text(encoding="utf-8"))
    catalog = {row["component_recipe"]: row for row in read_tsv(CATALOG)}
    old_groups = read_tsv(OLD_GROUPS)

    dual_groups: dict[str, list[str]] = defaultdict(list)
    for row in signatures:
        dual_groups[row["dual_channel_signature_sha256"]].append(row["component_recipe"])
    collision_sets = [set(recipes) for recipes in dual_groups.values() if len(recipes) > 1]
    published_sets = [set(row["component_recipes"].split("|")) for row in remaining]
    collision_members = {recipe for values in collision_sets for recipe in values}
    main_tiers = {"T1_FUTURE_HIGH", "T2_FUTURE_STRONG", "T3_SECOND_RING_AMBER"}
    main_recipes = {recipe for recipe, row in catalog.items() if row["intake_tier"] in main_tiers}
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)

    checks = {
        "signature_rows_1563_unique": len(signatures) == len({row["component_recipe"] for row in signatures}) == 1563,
        "signature_recipes_match_catalog": {row["component_recipe"] for row in signatures} == set(catalog),
        "ordered_literals_match_catalog": all(row["ordered_literal_reading_de"] == catalog[row["component_recipe"]]["literal_reading_de"] for row in signatures),
        "dual_signature_count_1543": len(dual_groups) == 1543,
        "remaining_groups_18_unique": len(remaining) == len({row["dual_collision_group_id"] for row in remaining}) == 18,
        "remaining_sets_match_signatures": {frozenset(values) for values in collision_sets} == {frozenset(values) for values in published_sets},
        "remaining_members_38": len(collision_members) == 38,
        "remaining_groups_max_three": max(int(row["recipe_count"]) for row in remaining) == 3,
        "remaining_no_same_multiset": all(row["same_atom_multiset"] == "NO" for row in remaining),
        "remaining_all_local_channels": all(row["interpretation"] == "CO_VALUED_LOCAL_CHANNELS__EXACT_CHANNEL_ID_RETAINED" for row in remaining),
        "remaining_literal_shared": all(len({catalog[recipe]["literal_reading_de"] for recipe in row["component_recipes"].split("|")}) == 1 for row in remaining),
        "resolutions_104_match_old": len(resolutions) == 104 and {row["gdt439_collision_group_id"] for row in resolutions} == {row["collision_group_id"] for row in old_groups},
        "resolution_status_counts_87_6_11": Counter(row["resolution_status"] for row in resolutions) == {
            "FULLY_RESOLVED_BY_ORDERED_MEANING_TRACE": 87,
            "PARTLY_RESOLVED__REMAINDER_CO_VALUED_LOCAL_CHANNELS": 6,
            "REMAINS_CO_VALUED_LOCAL_CHANNELS": 11,
        },
        "main_rows_five": len(main) == 5,
        "main_contacts_all_resolved": all(row["dual_signature_distinct"] == "YES" for row in main),
        "main_no_remaining_collision": not (main_recipes & collision_members),
        "events_4576_unique": len(events) == len({row["event_id"] for row in events}) == 4576,
        "events_state_clause_match": all(row["state_and_clause_match_gdt438"] == "YES" for row in events),
        "event_literals_match_catalog": all(row["ordered_literal_reading_de"] == catalog[row["component_recipe"]]["literal_reading_de"] for row in events),
        "dual_event_reading_complete": all(row["dual_channel_reading_de"] == f"Kernfolge: {row['ordered_literal_reading_de']}. {row['order_safe_clause_de']}" for row in events),
        "result_status_exact": result["status"] == "ORDER_COLLISIONS_RESOLVED__CO_VALUED_LOCAL_CHANNELS_RETAINED",
        "result_signature_counts_exact": result["catalog_recipe_count"] == 1563 and result["gdt439_fluent_signature_count"] == 1449 and result["dual_channel_signature_count"] == 1543,
        "result_resolution_counts_exact": result["gdt439_collision_group_count"] == 104 and result["fully_resolved_old_group_count"] == 87 and result["partly_resolved_old_group_count"] == 6 and result["unresolved_old_group_count"] == 11,
        "result_remaining_counts_exact": result["remaining_dual_collision_group_count"] == 18 and result["remaining_dual_collision_member_count"] == 38 and result["remaining_same_multiset_collision_group_count"] == 0,
        "result_main_counts_exact": result["main_future_card_count"] == 49 and result["main_future_dual_collision_member_count"] == 0 and result["main_external_contacts_resolved_count"] == 5,
        "result_current_counts_exact": result["current_event_count"] == result["current_state_and_clause_match_count"] == 4576,
        "result_no_expansion": result["meaning_revisions"] == result["surface_predictions"] == result["new_pages"] == 0,
        "no_forbidden_folio_token": re.search(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", output_text) is None,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {"status": "PASS" if not failed else "FAIL", "check_count": len(checks), "failure_count": len(failed), "checks": checks}
    (OUT / "gdt440_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
