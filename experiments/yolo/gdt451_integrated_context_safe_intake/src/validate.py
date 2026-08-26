#!/usr/bin/env python3
"""Validate the GDT451 integrated intake command and all retained artifacts."""

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
BASE = ROOT / "experiments/yolo/gdt451_integrated_context_safe_intake"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
COMMAND = BASE / "src/intake_command.py"
GDT448 = ROOT / "experiments/yolo/gdt448_context_conditioned_neighbor_replay/artifacts"
TARGETS = ROOT / "experiments/yolo/gdt449_context_robust_neighbor_deck/artifacts/gdt449_target_context_robustness.tsv"
FALSE_SAFE = ROOT / "experiments/yolo/gdt450_target_robustness_page_holdout/artifacts/gdt450_false_safe_cases.tsv"
VALIDATION = OUT / "gdt451_validation.json"

RETAINED = [
    OUT / "gdt451_18381_advisory_index.tsv",
    OUT / "gdt451_4576_current_intake_replay.tsv",
    OUT / "gdt451_61878_precedence_summary.tsv",
    OUT / "gdt451_8_false_safe_regressions.tsv",
    OUT / "gdt451_10_context_warning_targets.tsv",
    OUT / "gdt451_result.json",
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
    completed = subprocess.run(
        [sys.executable, str(RUN)],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    check("builder_exit_zero", completed.returncode == 0, completed.returncode)
    after = {path.name: sha256(path) for path in RETAINED}
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    advisory = read_tsv(OUT / "gdt451_18381_advisory_index.tsv")
    current = read_tsv(OUT / "gdt451_4576_current_intake_replay.tsv")
    summary = read_tsv(OUT / "gdt451_61878_precedence_summary.tsv")
    regressions = read_tsv(OUT / "gdt451_8_false_safe_regressions.tsv")
    warnings = read_tsv(OUT / "gdt451_10_context_warning_targets.tsv")
    result = json.loads((OUT / "gdt451_result.json").read_text(encoding="utf-8"))

    check("advisory_rows_18381", len(advisory) == 18_381, len(advisory))
    check("advisory_unique_targets", len({row["target_recipe"] for row in advisory}) == 18_381, len({row["target_recipe"] for row in advisory}))
    check("advisory_never_overrides", all(row["advisory_can_override_live_execution"] == "NO" for row in advisory), "all NO")
    check("current_rows_4576", len(current) == 4_576, len(current))
    check("current_unique_events", len({row["event_id"] for row in current}) == 4_576, len({row["event_id"] for row in current}))
    check("current_all_match_gdt441", all(row["current_execution_match"] == "YES" for row in current), Counter(row["current_execution_match"] for row in current))
    check("current_live_equals_final", all(row["live_execution_decision"] == row["final_execution_decision"] for row in current), "all equal")
    check("current_decisions_4566_10", Counter(row["final_execution_decision"] for row in current) == Counter({"READ": 4566, "READ_AMBER": 10}), Counter(row["final_execution_decision"] for row in current))
    check("current_precedence_locked", all(row["identity_can_override_live_execution"] == "NO" and row["advisory_can_override_live_execution"] == "NO" and row["final_decision_source"] == "LIVE_GDT446_CONTEXT_CERTIFICATE_ONLY" for row in current), "all locked")

    check("precedence_cells_7", len(summary) == 7, len(summary))
    check("precedence_cases_61878", sum(int(row["replay_case_count"]) for row in summary) == 61_878, sum(int(row["replay_case_count"]) for row in summary))
    check("precedence_stops_5911", sum(int(row["replay_case_count"]) for row in summary if row["final_execution_decision"] == "STOP") == 5_911, sum(int(row["replay_case_count"]) for row in summary if row["final_execution_decision"] == "STOP"))
    check("precedence_source_locked", all(row["final_decision_source"] == "LIVE_GDT446_CONTEXT_CERTIFICATE_ONLY" for row in summary), "all locked")

    target_rows = read_tsv(TARGETS)
    expected_warnings = {row["target_recipe"] for row in target_rows if row["observed_context_robustness"] == "OBSERVED_CONTEXT_MIXED_READ_STOP"}
    check("warning_rows_10", len(warnings) == 10, len(warnings))
    check("warning_set_exact", {row["target_recipe"] for row in warnings} == expected_warnings, sorted(expected_warnings))
    check("warning_instruction_live", all(row["instruction"] == "ALWAYS_RUN_LIVE_CONTEXT_CERTIFICATE" for row in warnings), "all live")

    source_false_safe = read_tsv(FALSE_SAFE)
    check("regression_rows_8", len(regressions) == 8, len(regressions))
    check("regression_ids_exact", {row["critical_id"] for row in regressions} == {row["critical_id"] for row in source_false_safe}, sorted(row["critical_id"] for row in regressions))
    check("regressions_all_stop", all(row["integrated_final_decision"] == "STOP" for row in regressions), Counter(row["integrated_final_decision"] for row in regressions))
    check("regressions_all_pass", all(row["regression_pass"] == "YES" for row in regressions), Counter(row["regression_pass"] for row in regressions))
    check("regressions_warning_visible", all(row["holdout_warning_visible"] == "YES" for row in regressions), "all YES")
    check("regressions_live_source", all(row["integrated_final_source"] == "LIVE_GDT446_CONTEXT_CERTIFICATE_ONLY" for row in regressions), "all live")

    command = load_module("gdt451_validator_command", COMMAND)
    replay_count = 0
    replay_match = 0
    replay_stops = 0
    replay_state_safe_stops = 0
    for path in sorted(GDT448.glob("gdt448_context_neighbor_replay_part*.tsv")):
        for row in read_tsv(path):
            replay_count += 1
            issued = command.issue_integrated_certificate(
                row["target_recipe"],
                row["incoming_action"],
                row["incoming_argument"],
                row["scope_incoming_action"],
                row["next_recipe"],
            )
            if issued["final_execution_decision"] == row["context_execution_decision"]:
                replay_match += 1
            if issued["final_execution_decision"] == "STOP":
                replay_stops += 1
                if issued["execution_stop_preserves_state"] == "YES":
                    replay_state_safe_stops += 1
    check("context_replay_rows_61878", replay_count == 61_878, replay_count)
    check("context_replay_exact_match", replay_match == replay_count, replay_match)
    check("context_replay_stops_5911", replay_stops == 5_911, replay_stops)
    check("context_replay_all_stops_state_safe", replay_state_safe_stops == replay_stops, replay_state_safe_stops)

    probe_focus_stop = command.issue_integrated_certificate("D_ADDR+EEE+Y", "CHD", "NONE", "CHD", "OT+AIIN")
    probe_close_stop = command.issue_integrated_certificate("E+DY", "NONE", "NONE", "NONE", "NONE")
    probe_close_read = command.issue_integrated_certificate("E+DY", "CH", "NONE", "CH", "NONE")
    check("probe_grade_three_gap_stops", probe_focus_stop["final_execution_decision"] == "STOP" and probe_focus_stop["blocked_factor_rules"] == "FOCUS:CHD<-EEE", probe_focus_stop["final_execution_decision"])
    check("probe_headless_close_stops", probe_close_stop["final_execution_decision"] == "STOP" and "CLOSE:NO_ACTIVE_ACTION" in str(probe_close_stop["blocked_factor_rules"]), probe_close_stop["final_execution_decision"])
    check("probe_same_close_reads_with_head", probe_close_read["final_execution_decision"] in {"READ", "READ_AMBER"}, probe_close_read["final_execution_decision"])
    check("all_final_sources_live", all(probe["final_decision_source"] == "LIVE_GDT446_CONTEXT_CERTIFICATE_ONLY" for probe in (probe_focus_stop, probe_close_stop, probe_close_read)), "all live")

    check("result_status", result["status"] == "INTEGRATED_INTAKE_ENFORCES_LIVE_CONTEXT_PRECEDENCE", result["status"])
    zero_keys = ("identity_overrides_allowed", "advisory_overrides_allowed", "meaning_revisions", "surface_predictions", "occurrence_predictions", "new_pages")
    check("result_no_new_claims", all(result[key] == 0 for key in zero_keys), {key: result[key] for key in zero_keys})

    forbidden_hits: list[str] = []
    # The manifest necessarily names the two sealed selectors and this validator
    # necessarily names the check itself. Scan only executable inputs and
    # retained result artifacts for accidental materialization.
    text_paths = [BASE / "README.md", BASE / "METHOD.md", BASE / "REPORT.md", BASE / "src/intake_command.py", BASE / "src/run.py", *RETAINED]
    for path in text_paths:
        if path.exists() and "f84" in path.read_text(encoding="utf-8", errors="ignore").lower():
            forbidden_hits.append(str(path.relative_to(ROOT)))
    check("sealed_tokens_absent", not forbidden_hits, forbidden_hits)

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "check_count": len(checks), "failure_count": len(failed)}, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
