#!/usr/bin/env python3
"""Stress the streaming intake with deterministic two-card mutation bursts."""

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
BASE = ROOT / "experiments/yolo/gdt454_two_card_neighbor_burst_stress"
OUT = BASE / "artifacts"
COMMAND_PATH = ROOT / "experiments/yolo/gdt451_integrated_context_safe_intake/src/intake_command.py"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
CONTEXTS = ROOT / "experiments/yolo/gdt448_context_conditioned_neighbor_replay/artifacts/gdt448_source_recipe_contexts.tsv"
NEIGHBOR_DIR = ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts"
NEIGHBOR_FILES = [
    NEIGHBOR_DIR / "gdt447_5499_atom_deletion_neighbors.tsv",
    NEIGHBOR_DIR / "gdt447_3936_adjacent_swap_neighbors.tsv",
    NEIGHBOR_DIR / "gdt447_action_substitution_neighbors.tsv",
    NEIGHBOR_DIR / "gdt447_nonaction_substitution_neighbors.tsv",
]


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


def atoms_of(recipe: str) -> list[str]:
    return [] if recipe in {"", "EMPTY_RECIPE", "NONE"} else recipe.split("+")


def scope_seed(action: str, event_id: str, ordinal: int) -> dict[str, object] | None:
    if action == "NONE":
        return None
    return {"action": action, "event_id": event_id, "card_ordinal": ordinal, "atom_ordinal": 0, "r_mode": "NONE"}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    command = load_module("gdt454_integrated_intake", COMMAND_PATH)
    scope_module = command.CERTIFIER.LEGACY.READER.SCOPE
    current = sorted(read_tsv(CURRENT), key=lambda row: int(row["stream_ordinal"]))
    context_by_event = {
        event_id: row
        for row in read_tsv(CONTEXTS)
        for event_id in row["event_ids"].split("|")
    }

    neighbor_rows = [row for path in NEIGHBOR_FILES for row in read_tsv(path)]
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in neighbor_rows:
        neutral_class = "NEUTRAL_STOP" if row["target_execution_decision"] == "STOP" else "NEUTRAL_READABLE"
        grouped[(row["source_recipe"], row["mutation_family"], neutral_class)].append(row)

    selected: dict[str, list[dict[str, str]]] = defaultdict(list)
    selected_rows: list[dict[str, object]] = []
    for key, members in sorted(grouped.items()):
        chosen = min(members, key=lambda row: (row["target_recipe"], row["neighbor_id"]))
        selected[chosen["source_recipe"]].append(chosen)
        selected_rows.append({
            "selection_id": f"G454-V{len(selected_rows) + 1:05d}",
            "source_recipe": chosen["source_recipe"],
            "mutation_family": chosen["mutation_family"],
            "neutral_selection_class": key[2],
            "neighbor_id": chosen["neighbor_id"],
            "target_recipe": chosen["target_recipe"],
            "target_is_exact_catalog_key": chosen["target_is_exact_catalog_key"],
            "neutral_execution_decision": chosen["target_execution_decision"],
            "neutral_blocked_factor_rules": chosen["target_blocked_factor_rules"],
            "selection_rule": "LEXICOGRAPHIC_FIRST_WITHIN_SOURCE_MUTATION_FAMILY_AND_NEUTRAL_CLASS",
        })
    write_tsv(OUT / "gdt454_selected_neighbor_variants.tsv", selected_rows)

    adjacent_pairs: list[tuple[dict[str, str], dict[str, str], dict[str, str] | None]] = []
    for index, first in enumerate(current[:-1]):
        second = current[index + 1]
        if not (
            second["statement_id"] == first["statement_id"]
            and second["physical_page"] == first["physical_page"]
            and second["owner_de"] == first["owner_de"]
        ):
            continue
        third = None
        if index + 2 < len(current):
            candidate = current[index + 2]
            if candidate["statement_id"] == first["statement_id"] and candidate["physical_page"] == first["physical_page"] and candidate["owner_de"] == first["owner_de"]:
                third = candidate
        adjacent_pairs.append((first, second, third))

    burst_rows: list[dict[str, object]] = []
    for pair_ordinal, (first_source, second_source, third_source) in enumerate(adjacent_pairs, start=1):
        first_context = context_by_event[first_source["event_id"]]
        first_variants = selected[first_source["component_recipe"]]
        second_variants = selected[second_source["component_recipe"]]
        fourth_recipe = "NONE"
        if third_source is not None:
            third_index = int(third_source["stream_ordinal"]) - 1
            if third_index + 1 < len(current):
                fourth = current[third_index + 1]
                if fourth["statement_id"] == third_source["statement_id"] and fourth["physical_page"] == third_source["physical_page"] and fourth["owner_de"] == third_source["owner_de"]:
                    fourth_recipe = fourth["component_recipe"]
        for first_variant in first_variants:
            for second_variant in second_variants:
                first_recipe = first_variant["target_recipe"]
                second_recipe = second_variant["target_recipe"]
                first = command.issue_integrated_certificate(
                    first_recipe,
                    first_context["incoming_action"],
                    first_context["incoming_argument"],
                    first_context["scope_incoming_action"],
                    second_recipe,
                )
                previous_scope = scope_seed(first_context["scope_incoming_action"], first_source["event_id"], int(first_source["stream_ordinal"]))
                if first["final_execution_decision"] == "STOP":
                    scope_after_first = previous_scope
                else:
                    scope_after_first = scope_module.active_after_card(
                        atoms_of(first_recipe),
                        {"event_id": f"BURST1:{first_source['event_id']}", "source_event_id": f"BURST1:{first_source['event_id']}"},
                        int(first_source["stream_ordinal"]),
                        previous_scope,
                    )
                scope_action_second = str(scope_after_first["action"]) if scope_after_first else "NONE"
                second = command.issue_integrated_certificate(
                    second_recipe,
                    str(first["outgoing_action_v2"]),
                    str(first["outgoing_argument_v2"]),
                    scope_action_second,
                    third_source["component_recipe"] if third_source else "NONE",
                )
                if second["final_execution_decision"] == "STOP":
                    scope_after_second = scope_after_first
                else:
                    scope_after_second = scope_module.active_after_card(
                        atoms_of(second_recipe),
                        {"event_id": f"BURST2:{second_source['event_id']}", "source_event_id": f"BURST2:{second_source['event_id']}"},
                        int(second_source["stream_ordinal"]),
                        scope_after_first,
                    )
                scope_action_third = str(scope_after_second["action"]) if scope_after_second else "NONE"
                boundary_event_id = "NONE"
                boundary_recipe = "NONE"
                boundary_decision = "NOT_APPLICABLE"
                boundary_blocked = "NONE"
                boundary_resolution = "NOT_APPLICABLE"

                if third_source is None:
                    recovery_decision = "NO_CARD"
                    recovery_blocked = "NONE"
                    recovery_status = "NO_THIRD_CARD"
                else:
                    recovery = command.issue_integrated_certificate(
                        third_source["component_recipe"],
                        str(second["outgoing_action_v2"]),
                        str(second["outgoing_argument_v2"]),
                        scope_action_third,
                        fourth_recipe,
                    )
                    recovery_decision = str(recovery["final_execution_decision"])
                    recovery_blocked = str(recovery["blocked_factor_rules"])
                    recovery_status = "RECOVERED_GREEN" if recovery_decision == "READ" else "RECOVERED_AMBER" if recovery_decision == "READ_AMBER" else "RECOVERY_STOP"
                    if recovery_decision == "STOP":
                        third_index = int(third_source["stream_ordinal"]) - 1
                        candidate = current[third_index + 1] if third_index + 1 < len(current) else None
                        if candidate is None or candidate["physical_page"] != third_source["physical_page"] or candidate["owner_de"] != third_source["owner_de"] or candidate["statement_id"] == third_source["statement_id"]:
                            boundary_resolution = "NO_NEXT_STATEMENT_SAME_OWNER_CARD"
                        else:
                            candidate_next = "NONE"
                            if third_index + 2 < len(current):
                                after_candidate = current[third_index + 2]
                                if after_candidate["statement_id"] == candidate["statement_id"] and after_candidate["physical_page"] == candidate["physical_page"] and after_candidate["owner_de"] == candidate["owner_de"]:
                                    candidate_next = after_candidate["component_recipe"]
                            boundary = command.issue_integrated_certificate(
                                candidate["component_recipe"],
                                str(recovery["outgoing_action_v2"]),
                                str(recovery["outgoing_argument_v2"]),
                                "NONE",
                                candidate_next,
                            )
                            boundary_event_id = candidate["event_id"]
                            boundary_recipe = candidate["component_recipe"]
                            boundary_decision = str(boundary["final_execution_decision"])
                            boundary_blocked = str(boundary["blocked_factor_rules"])
                            boundary_resolution = "RECOVERED_AT_NEXT_STATEMENT" if boundary_decision in {"READ", "READ_AMBER"} else "CASCADE_CONTINUES_AFTER_STATEMENT_RESET"

                first_decision = str(first["final_execution_decision"])
                second_decision = str(second["final_execution_decision"])
                burst_class = f"FIRST_{'STOP' if first_decision == 'STOP' else 'READABLE'}__SECOND_{'STOP' if second_decision == 'STOP' else 'READABLE'}"
                burst_rows.append({
                    "burst_id": f"G454-B{len(burst_rows) + 1:07d}",
                    "source_pair_id": f"G454-P{pair_ordinal:04d}",
                    "statement_id": first_source["statement_id"],
                    "physical_page": first_source["physical_page"],
                    "owner_de": first_source["owner_de"],
                    "first_event_id": first_source["event_id"],
                    "second_event_id": second_source["event_id"],
                    "third_event_id": third_source["event_id"] if third_source else "NONE",
                    "first_source_recipe": first_source["component_recipe"],
                    "second_source_recipe": second_source["component_recipe"],
                    "first_neighbor_id": first_variant["neighbor_id"],
                    "second_neighbor_id": second_variant["neighbor_id"],
                    "first_mutation_family": first_variant["mutation_family"],
                    "second_mutation_family": second_variant["mutation_family"],
                    "first_neutral_selection_class": "NEUTRAL_STOP" if first_variant["target_execution_decision"] == "STOP" else "NEUTRAL_READABLE",
                    "second_neutral_selection_class": "NEUTRAL_STOP" if second_variant["target_execution_decision"] == "STOP" else "NEUTRAL_READABLE",
                    "first_target_recipe": first_recipe,
                    "second_target_recipe": second_recipe,
                    "first_decision": first_decision,
                    "first_blocked_factor_rules": first["blocked_factor_rules"],
                    "first_stop_preserves_state": first["execution_stop_preserves_state"],
                    "scope_action_before_first": first_context["scope_incoming_action"],
                    "scope_action_before_second": scope_action_second,
                    "second_incoming_action": first["outgoing_action_v2"],
                    "second_incoming_argument": first["outgoing_argument_v2"],
                    "second_decision": second_decision,
                    "second_blocked_factor_rules": second["blocked_factor_rules"],
                    "second_stop_preserves_state": second["execution_stop_preserves_state"],
                    "burst_decision_class": burst_class,
                    "third_source_recipe": third_source["component_recipe"] if third_source else "NONE",
                    "third_incoming_action": second["outgoing_action_v2"],
                    "third_incoming_argument": second["outgoing_argument_v2"],
                    "scope_action_before_third": scope_action_third,
                    "third_next_recipe": fourth_recipe,
                    "third_recovery_decision": recovery_decision,
                    "third_recovery_blocked_factor_rules": recovery_blocked,
                    "third_recovery_status": recovery_status,
                    "post_recovery_boundary_event_id": boundary_event_id,
                    "post_recovery_boundary_recipe": boundary_recipe,
                    "post_recovery_boundary_decision": boundary_decision,
                    "post_recovery_boundary_blocked_factor_rules": boundary_blocked,
                    "post_recovery_boundary_status": boundary_resolution,
                    "identity_can_override": "NO",
                    "advisory_can_override": "NO",
                    "meaning_revision": "NO",
                    "surface_prediction": "NO",
                    "occurrence_prediction": "NO",
                })

    shard_count = 8
    for shard in range(shard_count):
        members = burst_rows[shard::shard_count]
        write_tsv(OUT / f"gdt454_two_card_bursts_part{shard + 1:02d}.tsv", members)

    summary_groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in burst_rows:
        summary_groups[(str(row["burst_decision_class"]), str(row["third_recovery_status"]))].append(row)
    summary_rows: list[dict[str, object]] = []
    for key, members in sorted(summary_groups.items()):
        summary_rows.append({
            "burst_decision_class": key[0],
            "third_recovery_status": key[1],
            "burst_count": len(members),
            "source_pair_count": len({str(row["source_pair_id"]) for row in members}),
            "page_count": len({str(row["physical_page"]) for row in members}),
            "first_target_count": len({str(row["first_target_recipe"]) for row in members}),
            "second_target_count": len({str(row["second_target_recipe"]) for row in members}),
        })
    write_tsv(OUT / "gdt454_burst_summary.tsv", summary_rows)

    failure_rows = [row for row in burst_rows if row["third_recovery_status"] == "RECOVERY_STOP"]
    compact_failures = [{
        "burst_id": row["burst_id"],
        "source_pair_id": row["source_pair_id"],
        "physical_page": row["physical_page"],
        "first_target_recipe": row["first_target_recipe"],
        "second_target_recipe": row["second_target_recipe"],
        "burst_decision_class": row["burst_decision_class"],
        "third_source_recipe": row["third_source_recipe"],
        "third_recovery_blocked_factor_rules": row["third_recovery_blocked_factor_rules"],
        "post_recovery_boundary_event_id": row["post_recovery_boundary_event_id"],
        "post_recovery_boundary_recipe": row["post_recovery_boundary_recipe"],
        "post_recovery_boundary_decision": row["post_recovery_boundary_decision"],
        "post_recovery_boundary_status": row["post_recovery_boundary_status"],
    } for row in failure_rows]
    if not compact_failures:
        compact_failures = [{
            "burst_id": "NONE", "source_pair_id": "NONE", "physical_page": "NONE",
            "first_target_recipe": "NONE", "second_target_recipe": "NONE",
            "burst_decision_class": "NONE", "third_source_recipe": "NONE",
            "third_recovery_blocked_factor_rules": "NO_RECOVERY_STOPS",
            "post_recovery_boundary_event_id": "NONE", "post_recovery_boundary_recipe": "NONE",
            "post_recovery_boundary_decision": "NONE", "post_recovery_boundary_status": "NOT_APPLICABLE",
        }]
    write_tsv(OUT / "gdt454_third_card_recovery_stops.tsv", compact_failures)

    burst_counts = Counter(str(row["burst_decision_class"]) for row in burst_rows)
    recovery_counts = Counter(str(row["third_recovery_status"]) for row in burst_rows)
    result = {
        "status": "TWO_CARD_MUTATION_BURSTS_AUDITED_WITH_SEQUENTIAL_STATE",
        "selected_variant_count": len(selected_rows),
        "source_recipe_with_variant_count": len(selected),
        "adjacent_source_pair_count": len(adjacent_pairs),
        "burst_count": len(burst_rows),
        "burst_decision_counts": dict(sorted(burst_counts.items())),
        "third_recovery_counts": dict(sorted(recovery_counts.items())),
        "first_stop_state_failure_count": sum(row["first_decision"] == "STOP" and row["first_stop_preserves_state"] != "YES" for row in burst_rows),
        "second_stop_state_failure_count": sum(row["second_decision"] == "STOP" and row["second_stop_preserves_state"] != "YES" for row in burst_rows),
        "third_recovery_stop_count": recovery_counts["RECOVERY_STOP"],
        "third_stop_next_statement_recovery_count": sum(row["post_recovery_boundary_status"] == "RECOVERED_AT_NEXT_STATEMENT" for row in burst_rows),
        "identity_overrides": 0,
        "advisory_overrides": 0,
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt454_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
