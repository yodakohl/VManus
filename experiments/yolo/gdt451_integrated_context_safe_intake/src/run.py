#!/usr/bin/env python3
"""Build the integrated context-safe intake release and regression audit."""

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
BASE = ROOT / "experiments/yolo/gdt451_integrated_context_safe_intake"
OUT = BASE / "artifacts"
COMMAND_PATH = BASE / "src/intake_command.py"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
GDT448 = ROOT / "experiments/yolo/gdt448_context_conditioned_neighbor_replay/artifacts"
TARGETS = ROOT / "experiments/yolo/gdt449_context_robust_neighbor_deck/artifacts/gdt449_target_context_robustness.tsv"
FALSE_SAFE = ROOT / "experiments/yolo/gdt450_target_robustness_page_holdout/artifacts/gdt450_false_safe_cases.tsv"


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
    command = load_module("gdt451_integrated_intake_command", COMMAND_PATH)
    current = read_tsv(CURRENT)
    contexts = read_tsv(GDT448 / "gdt448_source_recipe_contexts.tsv")
    context_by_event = {
        event_id: row
        for row in contexts
        for event_id in row["event_ids"].split("|")
    }
    targets = read_tsv(TARGETS)
    false_safe = read_tsv(FALSE_SAFE)

    advisory_rows: list[dict[str, object]] = []
    false_safe_targets = {row["target_recipe"] for row in false_safe}
    for row in targets:
        advisory_rows.append({
            "target_recipe": row["target_recipe"],
            "target_is_exact_catalog_key": row["target_is_exact_catalog_key"],
            "target_identity_route": row["target_identity_route"],
            "observed_context_robustness": row["observed_context_robustness"],
            "sampled_context_count": row["unique_sampled_context_count"],
            "green_context_count": row["green_context_count"],
            "amber_context_count": row["amber_context_count"],
            "stop_context_count": row["stop_context_count"],
            "stop_factor_rules": row["stop_factor_rules"],
            "deck_instruction": row["deck_instruction"],
            "gdt450_false_safe_regression_target": "YES" if row["target_recipe"] in false_safe_targets else "NO",
            "advisory_can_override_live_execution": "NO",
        })
    write_tsv(OUT / "gdt451_18381_advisory_index.tsv", advisory_rows)

    current_rows: list[dict[str, object]] = []
    for row in current:
        context = context_by_event[row["event_id"]]
        integrated = command.issue_integrated_certificate(
            row["component_recipe"],
            context["incoming_action"],
            context["incoming_argument"],
            context["scope_incoming_action"],
            context["next_recipe"],
        )
        expected = "READ" if row["factor_gate_status"] == "FACTOR_GREEN_CROSS_PAGE" else "READ_AMBER" if row["factor_gate_status"] == "FACTOR_AMBER_LOCAL_APPENDIX" else "STOP"
        current_rows.append({
            "event_id": row["event_id"],
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "owner_de": row["owner_de"],
            "component_recipe": row["component_recipe"],
            "identity_route": integrated["identity_route"],
            "advisory_history_status": integrated["advisory_history_status"],
            "gdt450_false_safe_regression_target": integrated["gdt450_false_safe_regression_target"],
            "live_execution_decision": integrated["execution_decision"],
            "final_execution_decision": integrated["final_execution_decision"],
            "final_execution_route": integrated["final_execution_route"],
            "advisory_live_relation": integrated["advisory_live_relation"],
            "expected_gdt441_execution_decision": expected,
            "current_execution_match": "YES" if integrated["final_execution_decision"] == expected else "NO",
            "identity_can_override_live_execution": integrated["identity_can_override_live_execution"],
            "advisory_can_override_live_execution": integrated["advisory_can_override_live_execution"],
            "final_decision_source": integrated["final_decision_source"],
        })
    write_tsv(OUT / "gdt451_4576_current_intake_replay.tsv", current_rows)

    replay = [
        row
        for path in sorted(GDT448.glob("gdt448_context_neighbor_replay_part*.tsv"))
        for row in read_tsv(path)
    ]
    summary_groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    full_match_count = 0
    live_stop_count = 0
    for row in replay:
        integrated = command.issue_integrated_certificate(
            row["target_recipe"],
            row["incoming_action"],
            row["incoming_argument"],
            row["scope_incoming_action"],
            row["next_recipe"],
        )
        if integrated["final_execution_decision"] == row["context_execution_decision"]:
            full_match_count += 1
        if integrated["final_execution_decision"] == "STOP":
            live_stop_count += 1
        key = (
            str(integrated["advisory_history_status"]),
            str(integrated["final_execution_decision"]),
            str(integrated["advisory_live_relation"]),
        )
        summary_groups[key].append(row)
    summary_rows: list[dict[str, object]] = []
    for key, rows in sorted(summary_groups.items()):
        summary_rows.append({
            "advisory_history_status": key[0],
            "final_execution_decision": key[1],
            "advisory_live_relation": key[2],
            "replay_case_count": len(rows),
            "weighted_occurrence_count": sum(int(row["context_occurrence_count"]) for row in rows),
            "distinct_target_recipe_count": len({row["target_recipe"] for row in rows}),
            "final_decision_source": "LIVE_GDT446_CONTEXT_CERTIFICATE_ONLY",
        })
    write_tsv(OUT / "gdt451_61878_precedence_summary.tsv", summary_rows)

    regression_rows: list[dict[str, object]] = []
    for row in false_safe:
        integrated = command.issue_integrated_certificate(
            row["target_recipe"],
            row["incoming_action"],
            row["incoming_argument"],
            row["scope_incoming_action"],
            row["next_recipe"],
        )
        regression_rows.append({
            "critical_id": row["critical_id"],
            "held_page": row["held_page"],
            "target_recipe": row["target_recipe"],
            "event_id": row["event_id"],
            "blocked_factor_rules": row["blocked_factor_rules"],
            "holdout_shortcut_class": row["training_shortcut_class"],
            "integrated_advisory_history_status": integrated["advisory_history_status"],
            "integrated_live_decision": integrated["execution_decision"],
            "integrated_final_decision": integrated["final_execution_decision"],
            "integrated_final_source": integrated["final_decision_source"],
            "holdout_warning_visible": integrated["gdt450_false_safe_regression_target"],
            "regression_pass": "YES" if integrated["final_execution_decision"] == "STOP" and integrated["advisory_can_override_live_execution"] == "NO" else "NO",
        })
    write_tsv(OUT / "gdt451_8_false_safe_regressions.tsv", regression_rows)

    warning_rows: list[dict[str, object]] = []
    for row in advisory_rows:
        if row["observed_context_robustness"] != "OBSERVED_CONTEXT_MIXED_READ_STOP":
            continue
        warning_rows.append({
            "target_recipe": row["target_recipe"],
            "observed_context_robustness": row["observed_context_robustness"],
            "green_context_count": row["green_context_count"],
            "amber_context_count": row["amber_context_count"],
            "stop_context_count": row["stop_context_count"],
            "stop_factor_rules": row["stop_factor_rules"],
            "gdt450_false_safe_regression_target": row["gdt450_false_safe_regression_target"],
            "instruction": "ALWAYS_RUN_LIVE_CONTEXT_CERTIFICATE",
        })
    write_tsv(OUT / "gdt451_10_context_warning_targets.tsv", warning_rows)

    current_decisions = Counter(str(row["final_execution_decision"]) for row in current_rows)
    result = {
        "status": "INTEGRATED_INTAKE_ENFORCES_LIVE_CONTEXT_PRECEDENCE",
        "advisory_target_count": len(advisory_rows),
        "current_event_count": len(current_rows),
        "current_execution_match_count": sum(row["current_execution_match"] == "YES" for row in current_rows),
        "current_final_decision_counts": dict(sorted(current_decisions.items())),
        "context_replay_case_count": len(replay),
        "context_replay_final_match_count": full_match_count,
        "context_replay_live_stop_count": live_stop_count,
        "precedence_summary_cell_count": len(summary_rows),
        "context_warning_target_count": len(warning_rows),
        "false_safe_regression_count": len(regression_rows),
        "false_safe_regression_pass_count": sum(row["regression_pass"] == "YES" for row in regression_rows),
        "identity_overrides_allowed": 0,
        "advisory_overrides_allowed": 0,
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt451_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
