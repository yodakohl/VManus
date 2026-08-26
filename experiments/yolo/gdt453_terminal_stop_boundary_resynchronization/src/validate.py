#!/usr/bin/env python3
"""Validate terminal-stop boundary resynchronization."""

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
BASE = ROOT / "experiments/yolo/gdt453_terminal_stop_boundary_resynchronization"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
COMMAND = ROOT / "experiments/yolo/gdt451_integrated_context_safe_intake/src/intake_command.py"
VALIDATION = OUT / "gdt453_validation.json"
RETAINED = [
    OUT / "gdt453_765_terminal_boundary_recovery.tsv",
    OUT / "gdt453_boundary_summary.tsv",
    OUT / "gdt453_boundary_warnings.tsv",
    OUT / "gdt453_result.json",
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

    rows = read_tsv(OUT / "gdt453_765_terminal_boundary_recovery.tsv")
    summary = read_tsv(OUT / "gdt453_boundary_summary.tsv")
    warnings = read_tsv(OUT / "gdt453_boundary_warnings.tsv")
    result = json.loads((OUT / "gdt453_result.json").read_text(encoding="utf-8"))

    check("rows_765", len(rows) == 765, len(rows))
    check("unique_ids", len({row["boundary_recovery_id"] for row in rows}) == 765, len({row["boundary_recovery_id"] for row in rows}))
    check("all_initial_stops", all(row["stop_final_decision"] == "STOP" for row in rows), Counter(row["stop_final_decision"] for row in rows))
    check("all_initial_stops_safe", all(row["stop_state_preserved"] == "YES" for row in rows), Counter(row["stop_state_preserved"] for row in rows))
    class_counts = Counter(row["boundary_class"] for row in rows)
    expected_classes = Counter({"SAME_OWNER_NEXT_STATEMENT": 695, "SAME_PAGE_NEW_OWNER_BANK": 29, "NEW_PAGE_OWNER_BANK": 31, "END_OF_STREAM": 10})
    check("boundary_classes_exact", class_counts == expected_classes, class_counts)
    status_counts = Counter(row["boundary_recovery_status"] for row in rows)
    check("boundary_status_exact", status_counts == Counter({"BOUNDARY_RECOVERED_GREEN": 755, "NO_BOUNDARY_CARD": 10}), status_counts)
    check("all_available_green", all(row["boundary_recovery_decision"] == "READ" and row["boundary_baseline_decision"] == "READ" for row in rows if row["boundary_event_id"] != "NONE"), "755 READ")
    check("end_rows_no_card", all(row["boundary_event_id"] == row["boundary_recipe"] == "NONE" and row["boundary_recovery_decision"] == "NO_CARD" for row in rows if row["boundary_class"] == "END_OF_STREAM"), "10 no-card")
    check("end_rows_one_source_event", {row["terminal_event_id"] for row in rows if row["boundary_class"] == "END_OF_STREAM"} == {"G407-E4576"}, sorted({row["terminal_event_id"] for row in rows if row["boundary_class"] == "END_OF_STREAM"}))
    check("same_owner_uses_preserved_state", all(row["boundary_state_source"] == "PRESERVED_STOP_STATE_SAME_OWNER" for row in rows if row["boundary_class"] == "SAME_OWNER_NEXT_STATEMENT"), "695")
    check("owner_page_resets_use_independent_bank", all(row["boundary_state_source"] == "INDEPENDENT_OWNER_BANK" for row in rows if row["boundary_class"] in {"SAME_PAGE_NEW_OWNER_BANK", "NEW_PAGE_OWNER_BANK"}), "60")
    check("no_cross_owner_state_leak", all(row["cross_owner_stop_state_used"] != "YES" for row in rows), Counter(row["cross_owner_stop_state_used"] for row in rows))
    check("scope_resets_at_boundaries", all(row["boundary_scope_incoming_action"] == "NONE" for row in rows), "all NONE")
    check("no_overclaim_rows", all(row["meaning_revision"] == row["surface_prediction"] == row["occurrence_prediction"] == "NO" for row in rows), "all NO")

    command = load_module("gdt453_validator_intake", COMMAND)
    reissue_matches = 0
    for row in rows:
        if row["boundary_event_id"] == "NONE":
            reissue_matches += row["boundary_recovery_decision"] == "NO_CARD"
            continue
        issued = command.issue_integrated_certificate(
            row["boundary_recipe"], row["boundary_incoming_action"], row["boundary_incoming_argument"],
            "NONE", row["boundary_next_recipe"],
        )
        if issued["final_execution_decision"] == row["boundary_recovery_decision"] and issued["blocked_factor_rules"] == row["boundary_blocked_factor_rules"]:
            reissue_matches += 1
    check("all_boundary_reissues_match", reissue_matches == 765, reissue_matches)

    check("summary_rows_4", len(summary) == 4, len(summary))
    check("summary_total_765", sum(int(row["occurrence_count"]) for row in summary) == 765, sum(int(row["occurrence_count"]) for row in summary))
    check("warning_rows_10", len(warnings) == 10, len(warnings))
    check("warnings_only_end_of_stream", all(row["boundary_class"] == "END_OF_STREAM" and row["boundary_recovery_status"] == "NO_BOUNDARY_CARD" for row in warnings), Counter(row["boundary_class"] for row in warnings))

    check("result_status", result["status"] == "TERMINAL_STOPS_RESYNCHRONIZE_AT_NEXT_AVAILABLE_BOUNDARY", result["status"])
    check("result_counts", result["terminal_stop_occurrence_count"] == 765 and result["available_boundary_count"] == result["readable_boundary_count"] == 755 and result["boundary_stop_count"] == 0, result)
    check("result_no_state_leak", result["cross_owner_state_leak_count"] == 0, result["cross_owner_state_leak_count"])
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
