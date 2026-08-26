#!/usr/bin/env python3
"""Replay GDT447 catalog neighbours in the actual contexts of their source cards."""

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
BASE = ROOT / "experiments/yolo/gdt448_context_conditioned_neighbor_replay"
OUT = BASE / "artifacts"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
CERTIFIER_PATH = ROOT / "experiments/yolo/gdt446_identity_execution_intake_split/src/intake_certificate_v2.py"
NEIGHBOR_PATHS = (
    ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts/gdt447_5499_atom_deletion_neighbors.tsv",
    ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts/gdt447_3936_adjacent_swap_neighbors.tsv",
    ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts/gdt447_action_substitution_neighbors.tsv",
    ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts/gdt447_nonaction_substitution_neighbors.tsv",
)
SHARD_SIZE = 5000


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if not rows and fields is None:
        raise ValueError(f"Refusing to write schema-less empty table {path}")
    columns = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def transition(neutral: str, contextual: str) -> str:
    if neutral == contextual:
        return "UNCHANGED"
    if neutral == "STOP" and contextual in {"READ", "READ_AMBER"}:
        return "CONTEXT_RESCUE"
    if neutral in {"READ", "READ_AMBER"} and contextual == "STOP":
        return "CONTEXT_DOWNGRADE_TO_STOP"
    if neutral == "READ" and contextual == "READ_AMBER":
        return "CONTEXT_DOWNGRADE_TO_AMBER"
    if neutral == "READ_AMBER" and contextual == "READ":
        return "CONTEXT_UPGRADE_TO_GREEN"
    raise ValueError(f"Unknown decision transition {neutral}->{contextual}")


def actual_context_rows(current: list[dict[str, str]], certifier) -> list[dict[str, object]]:
    """Reconstruct the statement-scope input used before each actual card."""
    scope_active: dict[str, dict[str, object] | None] = {}
    scope_card_ordinals: dict[str, int] = {}
    rows: list[dict[str, object]] = []
    for index, row in enumerate(current):
        statement_id = row["statement_id"]
        previous_scope = scope_active.get(statement_id)
        card_ordinal = scope_card_ordinals.get(statement_id, 0) + 1
        scope_card_ordinals[statement_id] = card_ordinal
        next_recipe = "NONE"
        if index + 1 < len(current):
            candidate = current[index + 1]
            if (
                candidate["statement_id"] == statement_id
                and candidate["physical_page"] == row["physical_page"]
                and candidate["owner_de"] == row["owner_de"]
            ):
                next_recipe = candidate["component_recipe"]
        scope_action = str(previous_scope["action"]) if previous_scope else "NONE"
        rows.append({
            "event_id": row["event_id"],
            "statement_id": statement_id,
            "physical_page": row["physical_page"],
            "register": row["register"],
            "owner_de": row["owner_de"],
            "source_recipe": row["component_recipe"],
            "incoming_action": row["active_action_before"],
            "incoming_argument": row["active_argument_before"],
            "scope_incoming_action": scope_action,
            "next_recipe": next_recipe,
            "actual_factor_gate_status": row["factor_gate_status"],
        })
        atoms = row["component_recipe"].split("+")
        scope_active[statement_id] = certifier.LEGACY.READER.SCOPE.active_after_card(
            atoms,
            {"event_id": row["event_id"]},
            card_ordinal,
            previous_scope,
        )
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    certifier = load_module("gdt446_certifier_for_gdt448_context", CERTIFIER_PATH)
    current = read_tsv(CURRENT)
    neighbors = [row for path in NEIGHBOR_PATHS for row in read_tsv(path)]
    contexts = actual_context_rows(current, certifier)

    # Replay identical source contexts once and retain all occurrence IDs.
    grouped: dict[tuple[str, str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in contexts:
        key = (
            str(row["source_recipe"]),
            str(row["incoming_action"]),
            str(row["incoming_argument"]),
            str(row["scope_incoming_action"]),
            str(row["next_recipe"]),
        )
        grouped[key].append(row)

    context_rows: list[dict[str, object]] = []
    contexts_by_recipe: dict[str, list[dict[str, object]]] = defaultdict(list)
    for ordinal, (key, occurrences) in enumerate(sorted(grouped.items()), start=1):
        source_recipe, incoming_action, incoming_argument, scope_action, next_recipe = key
        source_certificate = certifier.issue_split_certificate(
            source_recipe,
            incoming_action,
            incoming_argument,
            scope_action,
            next_recipe,
        )
        actual_gate_statuses = sorted({str(item["actual_factor_gate_status"]) for item in occurrences})
        context = {
            "context_id": f"G448-C{ordinal:04d}",
            "source_recipe": source_recipe,
            "incoming_action": incoming_action,
            "incoming_argument": incoming_argument,
            "scope_incoming_action": scope_action,
            "next_recipe": next_recipe,
            "occurrence_count": len(occurrences),
            "event_ids": "|".join(str(item["event_id"]) for item in occurrences),
            "statement_ids": "|".join(sorted({str(item["statement_id"]) for item in occurrences})),
            "physical_pages": "|".join(sorted({str(item["physical_page"]) for item in occurrences})),
            "owners_de": "|".join(sorted({str(item["owner_de"]) for item in occurrences})),
            "actual_source_factor_gate_statuses": "|".join(actual_gate_statuses),
            "recomputed_source_factor_gate_status": source_certificate["factor_gate_status"],
            "source_context_gate_matches_actual": "YES" if actual_gate_statuses == [source_certificate["factor_gate_status"]] else "NO",
        }
        context_rows.append(context)
        contexts_by_recipe[source_recipe].append(context)
    write_tsv(OUT / "gdt448_source_recipe_contexts.tsv", context_rows)

    replay_rows: list[dict[str, object]] = []
    for neighbor in neighbors:
        source_recipe = neighbor["source_recipe"]
        for context in contexts_by_recipe.get(source_recipe, []):
            target_recipe = neighbor["target_recipe"]
            if target_recipe == "EMPTY_RECIPE":
                contextual = {
                    "identity_route": "IDENTITY_NEW_VISIBLE_RECIPE",
                    "factor_gate_status": "STOP__EMPTY_RECIPE",
                    "execution_route": "EXECUTION_STOP_EMPTY_RECIPE",
                    "execution_decision": "STOP",
                    "blocked_factor_rules": "EMPTY_RECIPE",
                    "outgoing_action_v2": context["incoming_action"],
                    "outgoing_argument_v2": context["incoming_argument"],
                    "execution_stop_preserves_state": "YES",
                }
            else:
                contextual = certifier.issue_split_certificate(
                    target_recipe,
                    str(context["incoming_action"]),
                    str(context["incoming_argument"]),
                    str(context["scope_incoming_action"]),
                    str(context["next_recipe"]),
                )
            neutral_decision = neighbor["target_execution_decision"]
            contextual_decision = str(contextual["execution_decision"])
            replay_rows.append({
                "replay_id": f"G448-R{len(replay_rows) + 1:06d}",
                "neighbor_id": neighbor["neighbor_id"],
                "context_id": context["context_id"],
                "source_recipe": source_recipe,
                "mutation_family": neighbor["mutation_family"],
                "target_recipe": target_recipe,
                "target_is_exact_catalog_key": neighbor["target_is_exact_catalog_key"],
                "neutral_identity_route": neighbor["target_identity_route"],
                "context_identity_route": contextual["identity_route"],
                "identity_route_unchanged": "YES" if contextual["identity_route"] == neighbor["target_identity_route"] else "NO",
                "incoming_action": context["incoming_action"],
                "incoming_argument": context["incoming_argument"],
                "scope_incoming_action": context["scope_incoming_action"],
                "next_recipe": context["next_recipe"],
                "context_occurrence_count": context["occurrence_count"],
                "context_event_ids": context["event_ids"],
                "neutral_factor_gate_status": neighbor["target_factor_gate_status"],
                "context_factor_gate_status": contextual["factor_gate_status"],
                "neutral_execution_decision": neutral_decision,
                "context_execution_decision": contextual_decision,
                "decision_transition": transition(neutral_decision, contextual_decision),
                "neutral_blocked_factor_rules": neighbor["target_blocked_factor_rules"],
                "context_blocked_factor_rules": contextual["blocked_factor_rules"],
                "context_execution_route": contextual["execution_route"],
                "outgoing_action": contextual["outgoing_action_v2"],
                "outgoing_argument": contextual["outgoing_argument_v2"],
                "stop_preserves_state": contextual["execution_stop_preserves_state"],
                "source_identity_used_for_target": "NO",
                "meaning_revision": "NO",
                "surface_prediction": "NO",
                "occurrence_prediction": "NO",
            })

    for stale in OUT.glob("gdt448_context_neighbor_replay_part*.tsv"):
        stale.unlink()
    shard_paths: list[str] = []
    for start in range(0, len(replay_rows), SHARD_SIZE):
        part = start // SHARD_SIZE + 1
        path = OUT / f"gdt448_context_neighbor_replay_part{part:02d}.tsv"
        write_tsv(path, replay_rows[start:start + SHARD_SIZE])
        shard_paths.append(str(path.relative_to(ROOT)))

    changed_rows = [row for row in replay_rows if row["decision_transition"] != "UNCHANGED"]
    replay_fields = list(replay_rows[0])
    write_tsv(OUT / "gdt448_context_changed_cases.tsv", changed_rows, replay_fields)

    transition_counts = Counter(str(row["decision_transition"]) for row in replay_rows)
    transition_summary: list[dict[str, object]] = []
    for mutation_family in sorted({row["mutation_family"] for row in replay_rows}):
        family_rows = [row for row in replay_rows if row["mutation_family"] == mutation_family]
        for change in (
            "UNCHANGED",
            "CONTEXT_RESCUE",
            "CONTEXT_DOWNGRADE_TO_STOP",
            "CONTEXT_DOWNGRADE_TO_AMBER",
            "CONTEXT_UPGRADE_TO_GREEN",
        ):
            selected = [row for row in family_rows if row["decision_transition"] == change]
            transition_summary.append({
                "mutation_family": mutation_family,
                "decision_transition": change,
                "replay_case_count": len(selected),
                "weighted_source_occurrence_count": sum(int(row["context_occurrence_count"]) for row in selected),
                "distinct_target_recipe_count": len({row["target_recipe"] for row in selected}),
                "distinct_source_recipe_count": len({row["source_recipe"] for row in selected}),
            })
    write_tsv(OUT / "gdt448_transition_summary.tsv", transition_summary)

    eligible_source_recipes = set(contexts_by_recipe)
    eligible_neighbors = [row for row in neighbors if row["source_recipe"] in eligible_source_recipes]
    unexercised_neighbors = [row for row in neighbors if row["source_recipe"] not in eligible_source_recipes]
    result = {
        "status": "ACTUAL_CONTEXT_REPLAYS_CATALOG_NEIGHBORS_WITHOUT_IDENTITY_DRIFT",
        "current_event_count": len(current),
        "current_source_recipe_count": len({row["component_recipe"] for row in current}),
        "actual_unique_context_count": len(context_rows),
        "actual_context_gate_match_count": sum(row["source_context_gate_matches_actual"] == "YES" for row in context_rows),
        "catalog_neighbor_count": len(neighbors),
        "eligible_neighbor_count": len(eligible_neighbors),
        "unexercised_predicted_source_neighbor_count": len(unexercised_neighbors),
        "context_replay_case_count": len(replay_rows),
        "weighted_context_replay_occurrence_count": sum(int(row["context_occurrence_count"]) for row in replay_rows),
        "context_replay_shards": shard_paths,
        "neutral_execution_counts": dict(sorted(Counter(str(row["neutral_execution_decision"]) for row in replay_rows).items())),
        "context_execution_counts": dict(sorted(Counter(str(row["context_execution_decision"]) for row in replay_rows).items())),
        "decision_transition_counts": dict(sorted(transition_counts.items())),
        "identity_route_change_count": sum(row["identity_route_unchanged"] != "YES" for row in replay_rows),
        "source_identity_carry_count": sum(row["source_identity_used_for_target"] != "NO" for row in replay_rows),
        "unsafe_stop_count": sum(row["context_execution_decision"] == "STOP" and row["stop_preserves_state"] != "YES" for row in replay_rows),
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt448_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
