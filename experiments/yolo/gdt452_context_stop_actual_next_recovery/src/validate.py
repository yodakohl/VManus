#!/usr/bin/env python3
"""Validate GDT452 actual-next-card recovery after context-conditioned stops."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt452_context_stop_actual_next_recovery"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
COMMAND = ROOT / "experiments/yolo/gdt451_integrated_context_safe_intake/src/intake_command.py"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
VALIDATION = OUT / "gdt452_validation.json"
RETAINED = [
    OUT / "gdt452_stop_occurrence_recovery.tsv",
    OUT / "gdt452_recovery_summary.tsv",
    OUT / "gdt452_recovery_exceptions.tsv",
    OUT / "gdt452_result.json",
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

    rows = read_tsv(OUT / "gdt452_stop_occurrence_recovery.tsv")
    summary = read_tsv(OUT / "gdt452_recovery_summary.tsv")
    exceptions = read_tsv(OUT / "gdt452_recovery_exceptions.tsv")
    result = json.loads((OUT / "gdt452_result.json").read_text(encoding="utf-8"))
    current = read_tsv(CURRENT)
    current_by_event = {row["event_id"]: row for row in current}

    check("occurrence_rows_6008", len(rows) == 6_008, len(rows))
    check("unique_recovery_ids", len({row["recovery_id"] for row in rows}) == 6_008, len({row["recovery_id"] for row in rows}))
    check("unique_stop_scenarios", len({(row["stopped_target_recipe"], row["event_id"], row["incoming_action"], row["incoming_argument"], row["scope_incoming_action"], row["actual_next_recipe"]) for row in rows}) == 6_008, "6008")
    check("all_source_events_known", all(row["event_id"] in current_by_event for row in rows), "all known")
    check("all_stop_reissues_stop", all(row["stop_final_decision"] == "STOP" for row in rows), Counter(row["stop_final_decision"] for row in rows))
    check("all_stops_state_safe", all(row["stop_state_preserved"] == "YES" for row in rows), Counter(row["stop_state_preserved"] for row in rows))
    check("all_next_align", all(row["source_next_recipe_alignment"] == "YES" for row in rows), Counter(row["source_next_recipe_alignment"] for row in rows))
    check("no_identity_override", all(row["identity_can_override"] == "NO" for row in rows), "all NO")
    check("no_advisory_override", all(row["advisory_can_override"] == "NO" for row in rows), "all NO")
    check("no_new_claims", all(row["meaning_revision"] == row["surface_prediction"] == row["occurrence_prediction"] == "NO" for row in rows), "all NO")

    status_counts = Counter(row["immediate_recovery_status"] for row in rows)
    expected_counts = Counter({"RECOVERED_GREEN": 5231, "RECOVERED_AMBER": 9, "RECOVERY_STOP": 3, "NO_FOLLOWING_CARD": 765})
    check("recovery_counts_exact", status_counts == expected_counts, status_counts)
    check("available_count_5243", sum(row["actual_next_available"] == "YES" for row in rows) == 5_243, sum(row["actual_next_available"] == "YES" for row in rows))
    check("readable_recovery_5240", sum(row["recovery_decision_after_stop"] in {"READ", "READ_AMBER"} for row in rows) == 5_240, sum(row["recovery_decision_after_stop"] in {"READ", "READ_AMBER"} for row in rows))
    check("no_card_rows_consistent", all(row["actual_next_recipe"] == "NONE" and row["recovery_decision_after_stop"] == "NO_CARD" for row in rows if row["immediate_recovery_status"] == "NO_FOLLOWING_CARD"), "all consistent")

    transition_counts = Counter((row["actual_next_baseline_decision"], row["recovery_decision_after_stop"]) for row in rows if row["actual_next_available"] == "YES")
    expected_transitions = Counter({("READ", "READ"): 5231, ("READ", "READ_AMBER"): 8, ("READ_AMBER", "READ_AMBER"): 1, ("READ", "STOP"): 3})
    check("baseline_to_recovery_transitions", transition_counts == expected_transitions, {"|".join(key): value for key, value in transition_counts.items()})

    cascade = [row for row in rows if row["immediate_recovery_status"] == "RECOVERY_STOP"]
    check("cascade_count_3", len(cascade) == 3, len(cascade))
    check("cascade_one_source_event", {row["event_id"] for row in cascade} == {"G407-E4231"}, sorted({row["event_id"] for row in cascade}))
    check("cascade_one_following_close", {row["next_event_id"] for row in cascade} == {"G407-E4232"} and {row["actual_next_recipe"] for row in cascade} == {"Y+O+DY"}, sorted({row["actual_next_recipe"] for row in cascade}))
    check("cascade_reason_headless_close", {row["recovery_blocked_factor_rules"] for row in cascade} == {"CLOSE:NO_ACTIVE_ACTION"}, sorted({row["recovery_blocked_factor_rules"] for row in cascade}))
    check("cascade_statement_terminal", all(row["next_next_recipe"] == "NONE" for row in cascade), Counter(row["next_next_recipe"] for row in cascade))
    check("cascade_target_pair_pr", all("PAIR:P>R" in row["stop_blocked_factor_rules"] for row in cascade), [row["stop_blocked_factor_rules"] for row in cascade])
    check("cascade_boundary_event_exact", {row["cascade_boundary_event_id"] for row in cascade} == {"G407-E4233"} and {row["cascade_boundary_recipe"] for row in cascade} == {"OT+E+OL"}, sorted({row["cascade_boundary_recipe"] for row in cascade}))
    check("cascade_recovers_at_next_statement", all(row["cascade_boundary_decision"] == "READ" and row["cascade_resolution_status"] == "RECOVERED_AT_NEXT_STATEMENT" for row in cascade), Counter(row["cascade_resolution_status"] for row in cascade))

    command = load_module("gdt452_validator_intake", COMMAND)
    reissue_matches = 0
    for row in rows:
        stop = command.issue_integrated_certificate(
            row["stopped_target_recipe"], row["incoming_action"], row["incoming_argument"],
            row["scope_incoming_action"], row["actual_next_recipe"],
        )
        if stop["final_execution_decision"] != "STOP" or stop["execution_stop_preserves_state"] != "YES":
            continue
        if row["actual_next_available"] == "NO":
            reissue_matches += 1
            continue
        recovery = command.issue_integrated_certificate(
            row["actual_next_recipe"], str(stop["outgoing_action_v2"]), str(stop["outgoing_argument_v2"]),
            row["scope_incoming_action"], row["next_next_recipe"],
        )
        if recovery["final_execution_decision"] == row["recovery_decision_after_stop"] and recovery["blocked_factor_rules"] == row["recovery_blocked_factor_rules"]:
            reissue_matches += 1
    check("all_6008_two_step_reissues_match", reissue_matches == 6_008, reissue_matches)

    check("summary_nonempty", bool(summary), len(summary))
    check("summary_occurrences_6008", sum(int(row["occurrence_count"]) for row in summary) == 6_008, sum(int(row["occurrence_count"]) for row in summary))
    check("exception_rows_768", len(exceptions) == 768, len(exceptions))
    check("exception_statuses_exact", Counter(row["immediate_recovery_status"] for row in exceptions) == Counter({"NO_FOLLOWING_CARD": 765, "RECOVERY_STOP": 3}), Counter(row["immediate_recovery_status"] for row in exceptions))

    check("result_status", result["status"] == "ACTUAL_NEXT_CARD_RECOVERY_AUDITED_AFTER_ALL_CONTEXT_STOPS", result["status"])
    check("result_stop_probes_5911", result["stop_probe_count"] == 5_911, result["stop_probe_count"])
    check("result_occurrences_6008", result["expanded_stop_occurrence_count"] == 6_008, result["expanded_stop_occurrence_count"])
    check("result_all_stop_safe", result["stop_reissue_match_count"] == result["stop_state_safe_count"] == 6_008, {"match": result["stop_reissue_match_count"], "safe": result["stop_state_safe_count"]})
    check("result_next_alignment", result["source_next_alignment_count"] == 6_008, result["source_next_alignment_count"])
    check("result_three_cascades_recover", result["dependent_close_cascade_count"] == result["next_statement_recovery_count"] == 3, {"cascade": result["dependent_close_cascade_count"], "recovered": result["next_statement_recovery_count"]})
    zero_keys = ("meaning_revisions", "surface_predictions", "occurrence_predictions", "new_pages")
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
