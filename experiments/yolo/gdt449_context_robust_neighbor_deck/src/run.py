#!/usr/bin/env python3
"""Collapse GDT448 replays into edge-, target-, and operator-robustness decks."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt449_context_robust_neighbor_deck"
OUT = BASE / "artifacts"
GDT448 = ROOT / "experiments/yolo/gdt448_context_conditioned_neighbor_replay/artifacts"
NEIGHBOR_PATHS = (
    ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts/gdt447_5499_atom_deletion_neighbors.tsv",
    ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts/gdt447_3936_adjacent_swap_neighbors.tsv",
    ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts/gdt447_action_substitution_neighbors.tsv",
    ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts/gdt447_nonaction_substitution_neighbors.tsv",
)


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


def robustness(decisions: Counter[str]) -> str:
    if decisions["STOP"] == 0 and decisions["READ_AMBER"] == 0:
        return "OBSERVED_CONTEXT_ALL_GREEN"
    if decisions["STOP"] == 0:
        return "OBSERVED_CONTEXT_ALL_READABLE_WITH_AMBER"
    if decisions["READ"] + decisions["READ_AMBER"] == 0:
        return "OBSERVED_CONTEXT_ALL_STOP"
    return "OBSERVED_CONTEXT_MIXED_READ_STOP"


def instruction(status: str) -> str:
    return {
        "OBSERVED_CONTEXT_ALL_GREEN": "REISSUE_CONTEXT_CERTIFICATE__HISTORICALLY_ALL_GREEN",
        "OBSERVED_CONTEXT_ALL_READABLE_WITH_AMBER": "REISSUE_CONTEXT_CERTIFICATE__AMBER_POSSIBLE",
        "OBSERVED_CONTEXT_MIXED_READ_STOP": "CONTEXT_REQUIRED__STOP_POSSIBLE",
        "OBSERVED_CONTEXT_ALL_STOP": "STOP_UNDER_ALL_SAMPLED_CONTEXTS",
    }[status]


def split_values(value: str) -> set[str]:
    return set() if not value or value == "NONE" else set(value.split("|"))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    replay = [
        row
        for path in sorted(GDT448.glob("gdt448_context_neighbor_replay_part*.tsv"))
        for row in read_tsv(path)
    ]
    contexts = read_tsv(GDT448 / "gdt448_source_recipe_contexts.tsv")
    context_by_id = {row["context_id"]: row for row in contexts}
    neighbors = [row for path in NEIGHBOR_PATHS for row in read_tsv(path)]
    neighbor_by_id = {row["neighbor_id"]: row for row in neighbors}

    by_neighbor: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in replay:
        by_neighbor[row["neighbor_id"]].append(row)

    edge_rows: list[dict[str, object]] = []
    for neighbor_id, rows in sorted(by_neighbor.items()):
        source = neighbor_by_id[neighbor_id]
        decisions = Counter(row["context_execution_decision"] for row in rows)
        weighted = Counter()
        pages: set[str] = set()
        stop_rules: set[str] = set()
        for row in rows:
            weighted[row["context_execution_decision"]] += int(row["context_occurrence_count"])
            pages.update(split_values(context_by_id[row["context_id"]]["physical_pages"]))
            if row["context_execution_decision"] == "STOP":
                stop_rules.update(split_values(row["context_blocked_factor_rules"]))
        status = robustness(decisions)
        edge_rows.append({
            "neighbor_id": neighbor_id,
            "source_recipe": source["source_recipe"],
            "target_recipe": source["target_recipe"],
            "mutation_family": source["mutation_family"],
            "mutation_positions": source["mutation_positions"],
            "source_atom_or_pair": source["source_atom_or_pair"],
            "target_atom_or_pair": source["target_atom_or_pair"],
            "substitution_class": source["substitution_class"],
            "target_is_exact_catalog_key": source["target_is_exact_catalog_key"],
            "target_identity_route": source["target_identity_route"],
            "neutral_execution_decision": source["target_execution_decision"],
            "sampled_context_count": len(rows),
            "sampled_occurrence_weight": sum(int(row["context_occurrence_count"]) for row in rows),
            "sampled_page_count": len(pages),
            "sampled_pages": "|".join(sorted(pages)),
            "green_context_count": decisions["READ"],
            "amber_context_count": decisions["READ_AMBER"],
            "stop_context_count": decisions["STOP"],
            "green_occurrence_weight": weighted["READ"],
            "amber_occurrence_weight": weighted["READ_AMBER"],
            "stop_occurrence_weight": weighted["STOP"],
            "observed_context_robustness": status,
            "stop_factor_rules": "|".join(sorted(stop_rules)) or "NONE",
            "neutral_stop_rescued_in_any_context": "YES" if source["target_execution_decision"] == "STOP" and decisions["READ"] + decisions["READ_AMBER"] else "NO",
            "neutral_read_stops_in_any_context": "YES" if source["target_execution_decision"] in {"READ", "READ_AMBER"} and decisions["STOP"] else "NO",
            "deck_instruction": instruction(status),
            "identity_is_not_inferred_from_robustness": "YES",
            "occurrence_is_not_predicted_from_robustness": "YES",
        })
    stale_combined = OUT / "gdt449_25576_neighbor_edge_robustness.tsv"
    if stale_combined.exists():
        stale_combined.unlink()
    write_tsv(
        OUT / "gdt449_deletion_edge_robustness.tsv",
        [row for row in edge_rows if row["mutation_family"] == "ATOM_DELETION"],
    )
    write_tsv(
        OUT / "gdt449_adjacent_swap_edge_robustness.tsv",
        [row for row in edge_rows if row["mutation_family"] == "ADJACENT_SWAP"],
    )
    write_tsv(
        OUT / "gdt449_same_class_substitution_edge_robustness.tsv",
        [row for row in edge_rows if row["mutation_family"] == "SAME_CLASS_SUBSTITUTION"],
    )

    # A target can be reached from several source cards and even through more
    # than one mutation family. Deduplicate identical target×context probes so
    # source multiplicity cannot make a target look more stable than it is.
    target_context: dict[tuple[str, str], dict[str, str]] = {}
    target_edges: dict[str, set[str]] = defaultdict(set)
    for row in replay:
        key = (row["target_recipe"], row["context_id"])
        previous = target_context.get(key)
        if previous and previous["context_execution_decision"] != row["context_execution_decision"]:
            raise ValueError(f"Decision disagreement for target/context {key}")
        target_context[key] = row
        target_edges[row["target_recipe"]].add(row["neighbor_id"])

    by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for (target_recipe, _), row in target_context.items():
        by_target[target_recipe].append(row)
    target_rows: list[dict[str, object]] = []
    for target_recipe, rows in sorted(by_target.items()):
        decisions = Counter(row["context_execution_decision"] for row in rows)
        pages: set[str] = set()
        sources: set[str] = set()
        families: set[str] = set()
        stop_rules: set[str] = set()
        identity_routes = {row["context_identity_route"] for row in rows}
        exact_flags = {row["target_is_exact_catalog_key"] for row in rows}
        for row in rows:
            pages.update(split_values(context_by_id[row["context_id"]]["physical_pages"]))
            sources.add(row["source_recipe"])
            families.add(row["mutation_family"])
            if row["context_execution_decision"] == "STOP":
                stop_rules.update(split_values(row["context_blocked_factor_rules"]))
        if len(identity_routes) != 1 or len(exact_flags) != 1:
            raise ValueError(f"Identity disagreement for target {target_recipe}")
        status = robustness(decisions)
        target_rows.append({
            "target_recipe": target_recipe,
            "target_is_exact_catalog_key": next(iter(exact_flags)),
            "target_identity_route": next(iter(identity_routes)),
            "source_neighbor_edge_count": len(target_edges[target_recipe]),
            "distinct_source_recipe_count": len(sources),
            "source_recipes": "|".join(sorted(sources)),
            "mutation_families": "|".join(sorted(families)),
            "unique_sampled_context_count": len(rows),
            "sampled_page_count": len(pages),
            "sampled_pages": "|".join(sorted(pages)),
            "green_context_count": decisions["READ"],
            "amber_context_count": decisions["READ_AMBER"],
            "stop_context_count": decisions["STOP"],
            "observed_context_robustness": status,
            "stop_factor_rules": "|".join(sorted(stop_rules)) or "NONE",
            "deck_instruction": instruction(status),
            "identity_is_not_inferred_from_robustness": "YES",
            "occurrence_is_not_predicted_from_robustness": "YES",
        })
    write_tsv(OUT / "gdt449_target_context_robustness.tsv", target_rows)

    operator_groups: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in edge_rows:
        key = (
            str(row["mutation_family"]),
            str(row["source_atom_or_pair"]),
            str(row["target_atom_or_pair"]),
            str(row["substitution_class"]),
        )
        operator_groups[key].append(row)
    operator_rows: list[dict[str, object]] = []
    for key, rows in sorted(operator_groups.items()):
        classes = Counter(str(row["observed_context_robustness"]) for row in rows)
        operator_rows.append({
            "mutation_family": key[0],
            "source_atom_or_pair": key[1],
            "target_atom_or_pair": key[2],
            "substitution_class": key[3],
            "neighbor_edge_count": len(rows),
            "sampled_context_count": sum(int(row["sampled_context_count"]) for row in rows),
            "all_green_edge_count": classes["OBSERVED_CONTEXT_ALL_GREEN"],
            "all_readable_with_amber_edge_count": classes["OBSERVED_CONTEXT_ALL_READABLE_WITH_AMBER"],
            "mixed_read_stop_edge_count": classes["OBSERVED_CONTEXT_MIXED_READ_STOP"],
            "all_stop_edge_count": classes["OBSERVED_CONTEXT_ALL_STOP"],
            "edge_readable_rate": f"{sum(row['observed_context_robustness'] in {'OBSERVED_CONTEXT_ALL_GREEN', 'OBSERVED_CONTEXT_ALL_READABLE_WITH_AMBER'} for row in rows) / len(rows):.6f}",
            "operator_is_not_an_authorial_rule": "YES",
        })
    write_tsv(OUT / "gdt449_mutation_operator_summary.tsv", operator_rows)

    failure_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in replay:
        if row["context_execution_decision"] != "STOP":
            continue
        for rule in split_values(row["context_blocked_factor_rules"]):
            failure_groups[(row["mutation_family"], rule)].append(row)
    failure_rows: list[dict[str, object]] = []
    for (family, rule), rows in sorted(failure_groups.items()):
        failure_rows.append({
            "mutation_family": family,
            "blocked_factor_rule": rule,
            "stop_replay_case_count": len(rows),
            "distinct_neighbor_edge_count": len({row["neighbor_id"] for row in rows}),
            "distinct_target_recipe_count": len({row["target_recipe"] for row in rows}),
            "distinct_source_recipe_count": len({row["source_recipe"] for row in rows}),
            "context_event_occurrence_weight": sum(int(row["context_occurrence_count"]) for row in rows),
            "instruction": "STOP_AND_PRESERVE_STATE",
        })
    write_tsv(OUT / "gdt449_context_failure_deck.tsv", failure_rows)

    edge_classes = Counter(str(row["observed_context_robustness"]) for row in edge_rows)
    target_classes = Counter(str(row["observed_context_robustness"]) for row in target_rows)
    result = {
        "status": "CONTEXT_ROBUSTNESS_DECK_SEPARATES_STABLE_AND_CONTEXT_DEPENDENT_NEIGHBORS",
        "source_replay_case_count": len(replay),
        "eligible_neighbor_edge_count": len(edge_rows),
        "unique_target_recipe_count": len(target_rows),
        "unique_target_context_count": len(target_context),
        "mutation_operator_count": len(operator_rows),
        "failure_rule_family_count": len(failure_rows),
        "edge_robustness_counts": dict(sorted(edge_classes.items())),
        "target_robustness_counts": dict(sorted(target_classes.items())),
        "edge_all_sampled_contexts_readable_count": edge_classes["OBSERVED_CONTEXT_ALL_GREEN"] + edge_classes["OBSERVED_CONTEXT_ALL_READABLE_WITH_AMBER"],
        "target_all_sampled_contexts_readable_count": target_classes["OBSERVED_CONTEXT_ALL_GREEN"] + target_classes["OBSERVED_CONTEXT_ALL_READABLE_WITH_AMBER"],
        "target_context_decision_disagreement_count": 0,
        "identity_promotions": 0,
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt449_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
