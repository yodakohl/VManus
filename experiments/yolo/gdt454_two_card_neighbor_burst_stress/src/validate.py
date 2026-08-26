#!/usr/bin/env python3
"""Validate the deterministic two-card neighbour-burst stress test."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
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
RUN = BASE / "src/run.py"
COMMAND = ROOT / "experiments/yolo/gdt451_integrated_context_safe_intake/src/intake_command.py"
CONTEXTS = ROOT / "experiments/yolo/gdt448_context_conditioned_neighbor_replay/artifacts/gdt448_source_recipe_contexts.tsv"
NEIGHBOR_DIR = ROOT / "experiments/yolo/gdt447_catalog_near_neighbor_identity_atlas/artifacts"
NEIGHBOR_FILES = [
    NEIGHBOR_DIR / "gdt447_5499_atom_deletion_neighbors.tsv",
    NEIGHBOR_DIR / "gdt447_3936_adjacent_swap_neighbors.tsv",
    NEIGHBOR_DIR / "gdt447_action_substitution_neighbors.tsv",
    NEIGHBOR_DIR / "gdt447_nonaction_substitution_neighbors.tsv",
]
VALIDATION = OUT / "gdt454_validation.json"
BURST_SHARDS = [OUT / f"gdt454_two_card_bursts_part{index:02d}.tsv" for index in range(1, 9)]
RETAINED = [
    OUT / "gdt454_selected_neighbor_variants.tsv",
    *BURST_SHARDS,
    OUT / "gdt454_burst_summary.tsv",
    OUT / "gdt454_third_card_recovery_stops.tsv",
    OUT / "gdt454_result.json",
]


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    before = {path.name: sha256(path) for path in RETAINED}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, check=False, text=True, capture_output=True)
    check("builder_exit_zero", completed.returncode == 0, completed.returncode)
    after = {path.name: sha256(path) for path in RETAINED}
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    selected = read_tsv(OUT / "gdt454_selected_neighbor_variants.tsv")
    bursts = [row for path in BURST_SHARDS for row in read_tsv(path)]
    summary = read_tsv(OUT / "gdt454_burst_summary.tsv")
    stops = read_tsv(OUT / "gdt454_third_card_recovery_stops.tsv")
    result = json.loads((OUT / "gdt454_result.json").read_text(encoding="utf-8"))

    check("selected_rows_5283", len(selected) == 5_283, len(selected))
    selected_keys = {(row["source_recipe"], row["mutation_family"], row["neutral_selection_class"]) for row in selected}
    check("selected_keys_unique", len(selected_keys) == 5_283, len(selected_keys))
    check("selected_source_recipes_1563", len({row["source_recipe"] for row in selected}) == 1_563, len({row["source_recipe"] for row in selected}))
    check("selection_rule_fixed", all(row["selection_rule"] == "LEXICOGRAPHIC_FIRST_WITHIN_SOURCE_MUTATION_FAMILY_AND_NEUTRAL_CLASS" for row in selected), "all fixed")

    source_groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for path in NEIGHBOR_FILES:
        for row in read_tsv(path):
            neutral = "NEUTRAL_STOP" if row["target_execution_decision"] == "STOP" else "NEUTRAL_READABLE"
            source_groups[(row["source_recipe"], row["mutation_family"], neutral)].append(row)
    expected_selection = {
        key: min(members, key=lambda row: (row["target_recipe"], row["neighbor_id"]))["neighbor_id"]
        for key, members in source_groups.items()
    }
    actual_selection = {key: row["neighbor_id"] for key, row in zip([(row["source_recipe"], row["mutation_family"], row["neutral_selection_class"]) for row in selected], selected)}
    check("selection_is_exact_lexicographic_minimum", actual_selection == expected_selection, {"expected": len(expected_selection), "actual": len(actual_selection)})

    check("burst_rows_34205", len(bursts) == 34_205, len(bursts))
    check("burst_ids_unique", len({row["burst_id"] for row in bursts}) == 34_205, len({row["burst_id"] for row in bursts}))
    check("source_pair_count_3861", len({row["source_pair_id"] for row in bursts}) == 3_861, len({row["source_pair_id"] for row in bursts}))
    check("shard_balance", sorted(len(read_tsv(path)) for path in BURST_SHARDS) == [4275, 4275, 4275, 4276, 4276, 4276, 4276, 4276], [len(read_tsv(path)) for path in BURST_SHARDS])
    burst_counts = Counter(row["burst_decision_class"] for row in bursts)
    expected_burst = Counter({
        "FIRST_READABLE__SECOND_READABLE": 25_754,
        "FIRST_READABLE__SECOND_STOP": 3_719,
        "FIRST_STOP__SECOND_READABLE": 4_095,
        "FIRST_STOP__SECOND_STOP": 637,
    })
    check("burst_decision_counts_exact", burst_counts == expected_burst, burst_counts)
    recovery_counts = Counter(row["third_recovery_status"] for row in bursts)
    expected_recovery = Counter({"RECOVERED_GREEN": 28_190, "RECOVERED_AMBER": 50, "RECOVERY_STOP": 3, "NO_THIRD_CARD": 5_962})
    check("third_recovery_counts_exact", recovery_counts == expected_recovery, recovery_counts)
    check("all_first_stops_state_safe", all(row["first_stop_preserves_state"] == "YES" for row in bursts if row["first_decision"] == "STOP"), "all safe")
    check("all_second_stops_state_safe", all(row["second_stop_preserves_state"] == "YES" for row in bursts if row["second_decision"] == "STOP"), "all safe")
    check("no_execution_overrides", all(row["identity_can_override"] == row["advisory_can_override"] == "NO" for row in bursts), "all NO")
    check("no_new_claim_rows", all(row["meaning_revision"] == row["surface_prediction"] == row["occurrence_prediction"] == "NO" for row in bursts), "all NO")

    cascade = [row for row in bursts if row["third_recovery_status"] == "RECOVERY_STOP"]
    check("cascade_count_3", len(cascade) == 3, len(cascade))
    check("cascade_one_source_pair", {row["source_pair_id"] for row in cascade} == {"G454-P1312"} and {row["physical_page"] for row in cascade} == {"f72r"}, sorted({row["source_pair_id"] for row in cascade}))
    check("cascade_third_headless_close", {row["third_source_recipe"] for row in cascade} == {"EEE+DY"} and {row["third_recovery_blocked_factor_rules"] for row in cascade} == {"CLOSE:NO_ACTIVE_ACTION"}, sorted({row["third_recovery_blocked_factor_rules"] for row in cascade}))
    check("cascade_recovers_next_statement", all(row["post_recovery_boundary_event_id"] == "G407-E1392" and row["post_recovery_boundary_recipe"] == "CH+E" and row["post_recovery_boundary_decision"] == "READ" and row["post_recovery_boundary_status"] == "RECOVERED_AT_NEXT_STATEMENT" for row in cascade), Counter(row["post_recovery_boundary_status"] for row in cascade))

    context_by_event = {
        event_id: row
        for row in read_tsv(CONTEXTS)
        for event_id in row["event_ids"].split("|")
    }
    command = load_module("gdt454_validator_intake", COMMAND)
    first_matches = second_matches = third_matches = 0
    for row in bursts:
        context = context_by_event[row["first_event_id"]]
        first = command.issue_integrated_certificate(
            row["first_target_recipe"], context["incoming_action"], context["incoming_argument"],
            context["scope_incoming_action"], row["second_target_recipe"],
        )
        if first["final_execution_decision"] == row["first_decision"] and first["blocked_factor_rules"] == row["first_blocked_factor_rules"]:
            first_matches += 1
        second = command.issue_integrated_certificate(
            row["second_target_recipe"], row["second_incoming_action"], row["second_incoming_argument"],
            row["scope_action_before_second"], row["third_source_recipe"],
        )
        if second["final_execution_decision"] == row["second_decision"] and second["blocked_factor_rules"] == row["second_blocked_factor_rules"]:
            second_matches += 1
        if row["third_source_recipe"] == "NONE":
            third_matches += row["third_recovery_decision"] == "NO_CARD"
        else:
            third = command.issue_integrated_certificate(
                row["third_source_recipe"], row["third_incoming_action"], row["third_incoming_argument"],
                row["scope_action_before_third"], row["third_next_recipe"],
            )
            if third["final_execution_decision"] == row["third_recovery_decision"] and third["blocked_factor_rules"] == row["third_recovery_blocked_factor_rules"]:
                third_matches += 1
    check("all_first_reissues_match", first_matches == 34_205, first_matches)
    check("all_second_reissues_match", second_matches == 34_205, second_matches)
    check("all_third_reissues_match", third_matches == 34_205, third_matches)

    check("summary_total_34205", sum(int(row["burst_count"]) for row in summary) == 34_205, sum(int(row["burst_count"]) for row in summary))
    check("recovery_stop_rows_3", len(stops) == 3, len(stops))
    check("result_status", result["status"] == "TWO_CARD_MUTATION_BURSTS_AUDITED_WITH_SEQUENTIAL_STATE", result["status"])
    check("result_counts", result["selected_variant_count"] == 5_283 and result["adjacent_source_pair_count"] == 3_861 and result["burst_count"] == 34_205, result)
    check("result_state_safe", result["first_stop_state_failure_count"] == result["second_stop_state_failure_count"] == 0, {"first": result["first_stop_state_failure_count"], "second": result["second_stop_state_failure_count"]})
    check("result_cascades_resolve", result["third_recovery_stop_count"] == result["third_stop_next_statement_recovery_count"] == 3, {"stops": result["third_recovery_stop_count"], "resolved": result["third_stop_next_statement_recovery_count"]})
    zero_keys = ("identity_overrides", "advisory_overrides", "meaning_revisions", "surface_predictions", "occurrence_predictions", "new_pages")
    check("result_no_new_claims", all(result[key] == 0 for key in zero_keys), {key: result[key] for key in zero_keys})

    forbidden_hits: list[str] = []
    for path in [BASE / "README.md", BASE / "METHOD.md", BASE / "REPORT.md", BASE / "src/run.py", *RETAINED]:
        if path.exists() and "f84" in path.read_text(encoding="utf-8", errors="ignore").lower():
            forbidden_hits.append(str(path.relative_to(ROOT)))
    check("sealed_tokens_absent", not forbidden_hits, forbidden_hits)

    failed = [item for item in checks if not item["passed"]]
    payload = {"status": "PASS" if not failed else "FAIL", "check_count": len(checks), "failure_count": len(failed), "checks": checks}
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "check_count": len(checks), "failure_count": len(failed)}, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
