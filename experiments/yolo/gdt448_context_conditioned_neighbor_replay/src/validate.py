#!/usr/bin/env python3
"""Validate the context-conditioned GDT447 neighbour replay."""

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
BASE = ROOT / "experiments/yolo/gdt448_context_conditioned_neighbor_replay"
OUT = BASE / "artifacts"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
NEIGHBOR_PATHS = (
    ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts/gdt447_5499_atom_deletion_neighbors.tsv",
    ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts/gdt447_3936_adjacent_swap_neighbors.tsv",
    ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts/gdt447_action_substitution_neighbors.tsv",
    ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts/gdt447_nonaction_substitution_neighbors.tsv",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    shard_paths = sorted(OUT.glob("gdt448_context_neighbor_replay_part*.tsv"))
    tracked = [
        OUT / "gdt448_source_recipe_contexts.tsv",
        *shard_paths,
        OUT / "gdt448_context_changed_cases.tsv",
        OUT / "gdt448_transition_summary.tsv",
        OUT / "gdt448_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    rebuilt_shards = sorted(OUT.glob("gdt448_context_neighbor_replay_part*.tsv"))
    after_paths = [tracked[0], *rebuilt_shards, tracked[-3], tracked[-2], tracked[-1]]
    after = {path: path.read_bytes() for path in after_paths}

    current = read_tsv(CURRENT)
    neighbors = [row for path in NEIGHBOR_PATHS for row in read_tsv(path)]
    neighbor_by_id = {row["neighbor_id"]: row for row in neighbors}
    contexts = read_tsv(OUT / "gdt448_source_recipe_contexts.tsv")
    context_by_id = {row["context_id"]: row for row in contexts}
    replay = [row for path in rebuilt_shards for row in read_tsv(path)]
    changed = read_tsv(OUT / "gdt448_context_changed_cases.tsv")
    summary = read_tsv(OUT / "gdt448_transition_summary.tsv")
    result = json.loads((OUT / "gdt448_result.json").read_text(encoding="utf-8"))

    events_from_contexts = [event for row in contexts for event in row["event_ids"].split("|")]
    contexts_by_recipe: dict[str, set[str]] = defaultdict(set)
    for row in contexts:
        contexts_by_recipe[row["source_recipe"]].add(row["context_id"])
    eligible_neighbors = [row for row in neighbors if row["source_recipe"] in contexts_by_recipe]
    expected_pairs = {
        (row["neighbor_id"], context_id)
        for row in eligible_neighbors
        for context_id in contexts_by_recipe[row["source_recipe"]]
    }
    observed_pairs = {(row["neighbor_id"], row["context_id"]) for row in replay}
    transitions = Counter(row["decision_transition"] for row in replay)
    neutral = Counter(row["neutral_execution_decision"] for row in replay)
    contextual = Counter(row["context_execution_decision"] for row in replay)
    rescue = [row for row in replay if row["decision_transition"] == "CONTEXT_RESCUE"]
    downgrade_stop = [row for row in replay if row["decision_transition"] == "CONTEXT_DOWNGRADE_TO_STOP"]

    row_links_ok = True
    for row in replay:
        neighbor = neighbor_by_id.get(row["neighbor_id"])
        context = context_by_id.get(row["context_id"])
        if not neighbor or not context:
            row_links_ok = False
            break
        if not (
            row["source_recipe"] == neighbor["source_recipe"] == context["source_recipe"]
            and row["target_recipe"] == neighbor["target_recipe"]
            and row["neutral_identity_route"] == neighbor["target_identity_route"]
            and row["neutral_execution_decision"] == neighbor["target_execution_decision"]
            and row["incoming_action"] == context["incoming_action"]
            and row["incoming_argument"] == context["incoming_argument"]
            and row["scope_incoming_action"] == context["scope_incoming_action"]
            and row["next_recipe"] == context["next_recipe"]
        ):
            row_links_ok = False
            break

    output_text = "\n".join(path.read_text(encoding="utf-8") for path in after_paths)
    checks = {
        "current_4576_events_1268_recipes": len(current) == len({row["event_id"] for row in current}) == 4576 and len({row["component_recipe"] for row in current}) == 1268,
        "catalog_30763_neighbors_unique": len(neighbors) == len(neighbor_by_id) == 30763,
        "contexts_4275_unique": len(contexts) == len(context_by_id) == 4275,
        "contexts_cover_current_events_once": len(events_from_contexts) == len(set(events_from_contexts)) == 4576 and set(events_from_contexts) == {row["event_id"] for row in current},
        "context_occurrence_counts_sum_4576": sum(int(row["occurrence_count"]) for row in contexts) == 4576,
        "all_source_gate_reconstructions_match": all(row["source_context_gate_matches_actual"] == "YES" for row in contexts),
        "eligible_25576_unexercised_5187": len(eligible_neighbors) == 25576 and len(neighbors) - len(eligible_neighbors) == 5187,
        "replay_61878_unique": len(replay) == len({row["replay_id"] for row in replay}) == 61878,
        "replay_ids_contiguous": [row["replay_id"] for row in replay] == [f"G448-R{i:06d}" for i in range(1, 61879)],
        "replay_cross_product_exact": observed_pairs == expected_pairs and len(observed_pairs) == len(replay),
        "replay_source_links_exact": row_links_ok,
        "weighted_occurrence_count_65746": sum(int(row["context_occurrence_count"]) for row in replay) == 65746,
        "thirteen_shards_bounded": len(rebuilt_shards) == 13 and all(len(read_tsv(path)) == 5000 for path in rebuilt_shards[:-1]) and len(read_tsv(rebuilt_shards[-1])) == 1878,
        "neutral_counts_exact": neutral == {"READ": 53476, "READ_AMBER": 1743, "STOP": 6659},
        "context_counts_exact": contextual == {"READ": 54622, "READ_AMBER": 1345, "STOP": 5911},
        "transition_counts_exact": transitions == {"UNCHANGED": 60633, "CONTEXT_RESCUE": 757, "CONTEXT_UPGRADE_TO_GREEN": 443, "CONTEXT_DOWNGRADE_TO_AMBER": 36, "CONTEXT_DOWNGRADE_TO_STOP": 9},
        "changed_table_exact": len(changed) == 1245 and {row["replay_id"] for row in changed} == {row["replay_id"] for row in replay if row["decision_transition"] != "UNCHANGED"},
        "rescues_are_inherited_close_only": len(rescue) == 757 and all(row["neutral_blocked_factor_rules"] == "CLOSE:NO_ACTIVE_ACTION" and row["context_execution_route"] in {"EXECUTE_INHERITED_HEAD_CLOSE_GREEN", "EXECUTE_INHERITED_HEAD_CLOSE_AMBER"} for row in rescue),
        "rescues_748_green_9_amber": Counter(row["context_execution_decision"] for row in rescue) == {"READ": 748, "READ_AMBER": 9},
        "nine_stops_are_grade_three_gaps": Counter(row["context_blocked_factor_rules"] for row in downgrade_stop) == {"FOCUS:CHD<-EEE": 8, "FOCUS:R<-EEE": 1},
        "identity_never_changes": all(row["identity_route_unchanged"] == "YES" and row["context_identity_route"] == row["neutral_identity_route"] for row in replay),
        "no_source_identity_carry": all(row["source_identity_used_for_target"] == "NO" for row in replay),
        "all_stops_state_safe": all(row["context_execution_decision"] != "STOP" or row["stop_preserves_state"] == "YES" for row in replay),
        "summary_has_15_cells": len(summary) == 15,
        "result_status_exact": result["status"] == "ACTUAL_CONTEXT_REPLAYS_CATALOG_NEIGHBORS_WITHOUT_IDENTITY_DRIFT",
        "result_counts_exact": result["actual_context_gate_match_count"] == 4275 and result["eligible_neighbor_count"] == 25576 and result["context_replay_case_count"] == 61878 and result["weighted_context_replay_occurrence_count"] == 65746,
        "result_transition_counts_exact": result["decision_transition_counts"] == dict(sorted(transitions.items())),
        "result_zero_drift_and_expansion": result["identity_route_change_count"] == result["source_identity_carry_count"] == result["unsafe_stop_count"] == result["meaning_revisions"] == result["surface_predictions"] == result["occurrence_predictions"] == result["new_pages"] == 0,
        "no_forbidden_folio_token": re.search(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", output_text) is None,
        "deterministic_rebuild": set(before) == set(after) and before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "failed_checks": failed,
        "checks": checks,
    }
    (OUT / "gdt448_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
