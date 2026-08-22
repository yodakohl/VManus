#!/usr/bin/env python3
"""Validate the bounded V79 R2 apprentice/read-once audit."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_381_EVENT_INTERLINEAR.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_116_STATEMENTS.tsv"
GROUPS = ROOT / "experiments/yolo/sidequest_theory_candidates_v75/V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv"

TRANSITIONS = HERE / "V79_R2_19_LINE_TRANSITION_AUDIT.tsv"
TRACES = HERE / "V79_R2_COMPLETE_FORWARD_BACKWARD_TRACES.tsv"
REPAIRS = HERE / "V79_R2_REPAIR_DECISIONS.tsv"
RESULT = HERE / "V79_R2_RESULT.json"
REPORT = HERE / "V79_R2_APPRENTICE_WORKFLOW_REPORT.md"
OUT = HERE / "V79_R2_VALIDATION.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def check(name: str, condition: bool, detail: object, checks: list[dict[str, object]]) -> None:
    checks.append({"check": name, "pass": bool(condition), "detail": detail})


def main() -> None:
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    groups = read_tsv(GROUPS)
    transitions = read_tsv(TRANSITIONS)
    traces = read_tsv(TRACES)
    repairs = read_tsv(REPAIRS)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    report = REPORT.read_text(encoding="utf-8")
    checks: list[dict[str, object]] = []

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    expected_pairs: list[tuple[str, str]] = []
    expected_rule_matches: list[tuple[str, str]] = []
    expected_owner_reset_pairs: list[tuple[str, str]] = []
    for statement in statements:
        rows = by_statement[statement["statement_id"]]
        for left, right in zip(rows, rows[1:]):
            if left["locus"] == right["locus"]:
                continue
            pair = (left["event_id"], right["event_id"])
            expected_pairs.append(pair)
            same_card = left["joint_tuple_id"] == right["joint_tuple_id"]
            same_owner = left["image_owner_id"] == right["image_owner_id"]
            no_close = left["terminal_status"] != "TERMINAL"
            no_reset = not right["owner_break_before"].startswith("BREAK_")
            if same_card and same_owner and no_close and no_reset:
                expected_rule_matches.append(pair)
            if not no_reset:
                expected_owner_reset_pairs.append(pair)

    actual_pairs = [(row["left_event_id"], row["right_event_id"]) for row in transitions]
    actual_matches = [
        (row["left_event_id"], row["right_event_id"])
        for row in transitions if row["read_once_rule_match"] == "YES"
    ]
    check("all_19_transitions_covered_in_source_order", actual_pairs == expected_pairs and len(actual_pairs) == 19, actual_pairs, checks)
    check("18_cross_line_statements", len({row["statement_id"] for row in transitions}) == 18, sorted({row["statement_id"] for row in transitions}), checks)
    check("only_visible_rule_match_is_E180_E181", actual_matches == expected_rule_matches == [("E180", "E181")], actual_matches, checks)
    check(
        "four_cross_line_owner_resets_retained",
        expected_owner_reset_pairs == [("E202", "E203"), ("E263", "E264"), ("E290", "E291"), ("E355", "E356")],
        expected_owner_reset_pairs,
        checks,
    )

    match = next(row for row in transitions if row["read_once_rule_match"] == "YES")
    check(
        "read_once_match_passes_all_visible_conditions",
        all(match[key] == "YES" for key in ["same_statement", "same_exact_card", "same_visible_owner", "no_close_between", "no_owner_reset_between"]),
        {key: match[key] for key in ["same_statement", "same_exact_card", "same_visible_owner", "no_close_between", "no_owner_reset_between"]},
        checks,
    )
    nonmatches = [row for row in transitions if row["read_once_rule_match"] == "NO"]
    check("all_other_transitions_read_both", len(nonmatches) == 18 and all(row["source_token_count_for_visible_pair"] == "2" for row in nonmatches), len(nonmatches), checks)
    check(
        "hypothesis_not_promoted_to_standard_catchword",
        match["historical_hypothesis_label"] == "LOCAL_ANTICIPATION_CARRY_OR_DITTOGRAPHY_HYPOTHESIS__NOT_ATTESTED_STANDARD_CATCHWORD",
        match["historical_hypothesis_label"],
        checks,
    )

    by_trace: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in traces:
        by_trace[row["trace_unit"]].append(row)
    check("trace_row_total_119", len(traces) == 119, len(traces), checks)
    check("H2_complete_E015_E038", [r["atom_id"] for r in by_trace["H2"]] == [f"E{i:03d}" for i in range(15, 39)], len(by_trace["H2"]), checks)
    check("B2_complete_E167_E228", [r["atom_id"] for r in by_trace["B2"]] == [f"E{i:03d}" for i in range(167, 229)], len(by_trace["B2"]), checks)

    expected_astro = [
        row for row in groups
        if row["page"] == "f69v" and row["local_namespace"] == "A3_LEFT_WHEEL_ONLY" and row["locus"] != "f69v.1"
    ]
    expected_astro.sort(key=lambda row: int(row["group_serial"]))
    astro = by_trace["F69_LEFT_28_SLOTS"]
    check("f69_all_33_left_wheel_segments", [r["atom_id"] for r in astro] == [r["opaque_local_id"] for r in expected_astro], len(astro), checks)
    slot_counts = Counter(row["physical_locus"] for row in astro)
    check("f69_exactly_28_local_slots", len(slot_counts) == 28, dict(slot_counts), checks)
    check(
        "f69_exactly_five_two_segment_slots",
        {slot for slot, count in slot_counts.items() if count == 2} == {"f69v.4", "f69v.5", "f69v.25", "f69v.26", "f69v.31"}
        and all(count in {1, 2} for count in slot_counts.values()),
        dict(slot_counts),
        checks,
    )

    for unit, rows in by_trace.items():
        n = len(rows)
        check(
            f"{unit}_forward_backward_indices_complete",
            [int(row["forward_audit_order"]) for row in rows] == list(range(1, n + 1))
            and [int(row["backward_audit_order"]) for row in rows] == list(range(n, 0, -1)),
            n,
            checks,
        )

    trace_by_id = {row["atom_id"]: row for row in traces}
    check(
        "E180_E181_visible_two_source_one",
        trace_by_id["E180"]["source_token_count"] == "0"
        and trace_by_id["E181"]["source_token_count"] == "1"
        and "ANTICIPATION" in trace_by_id["E180"]["visible_copy_role"],
        {event: trace_by_id[event]["visible_copy_role"] for event in ["E180", "E181"]},
        checks,
    )
    b2_resets = [row["atom_id"] for row in by_trace["B2"] if row["owner_action"].startswith("VISIBLE_OWNER_RESET")]
    check("B2_exact_owner_resets", b2_resets == ["E189", "E198", "E203", "E212"], b2_resets, checks)
    check("all_trace_semantics_without_master_unrecoverable", all(row["concrete_semantics_without_master"].startswith("NOT_RECOVERABLE") for row in traces), len(traces), checks)
    check("visible_119_rows_reduce_to_118_source_tokens", sum(int(row["source_token_count"]) for row in traces) == 118, sum(int(row["source_token_count"]) for row in traces), checks)

    issues = {row["issue"]: row for row in repairs}
    expected_issues = {
        "GENERAL_VISIBLE_READ_ONCE_RULE", "HISTORICAL_CATCHWORD_LABEL",
        "ET_QUESTION_MARK_VS_FORMAL_LINK", "PER_QUESTION_MARK_VS_ENTRY_RESET",
        "B2_VISIBLE_OWNER_RESETS", "F69_LEFT_28_SLOT_TRACE", "MASTER_EXEMPLAR_SEPARATION",
    }
    check("all_seven_repair_decisions_present", set(issues) == expected_issues, sorted(issues), checks)
    check("ET_internal_winner_is_formal_link", issues["ET_QUESTION_MARK_VS_FORMAL_LINK"]["formal_decision"] == "FORMAL_LINK_SLOT_RECOVERABLE_WITHOUT_MASTER", issues["ET_QUESTION_MARK_VS_FORMAL_LINK"]["formal_decision"], checks)
    check("PER_internal_winner_is_formal_relation_entry", issues["PER_QUESTION_MARK_VS_ENTRY_RESET"]["formal_decision"] == "FORMAL_RELATION_OR_ENTRY_MARK_WITH_ENTRY_BIAS", issues["PER_QUESTION_MARK_VS_ENTRY_RESET"]["formal_decision"], checks)
    check("no_new_portable_meanings", result["new_portable_word_meanings"] == 0, result["new_portable_word_meanings"], checks)
    check("formal_master_copy_pass_semantic_self_continuation_fail", result["formal_copy_and_readback_with_master"] == "PASS" and result["semantic_forward_continuation_without_master"].startswith("FAIL"), {"formal": result["formal_copy_and_readback_with_master"], "semantic": result["semantic_forward_continuation_without_master"]}, checks)
    check("sealed_pages_not_inputs", all("f84" not in path.lower() for path in result["inputs"]), result["inputs"], checks)

    required_report_phrases = [
        "lokale anticipation/carry/dittography-hypothese",
        "kein belegter standard-catchword",
        "E180→E181",
        "FORMAL_LINK",
        "FORMAL_RELATION_OR_ENTRY_MARK_WITH_ENTRY_BIAS",
        "Ohne Masterexemplar",
        "28 lokale Slots",
    ]
    normalized_report = " ".join(report.lower().split())
    check("report_contains_required_decisions", all(phrase.lower() in normalized_report for phrase in required_report_phrases), required_report_phrases, checks)

    status = "PASS" if all(row["pass"] for row in checks) else "FAIL"
    payload = {
        "experiment": "V79_R2_HISTORICAL_APPRENTICE_RECONSTRUCTION",
        "status": status,
        "checks_passed": sum(row["pass"] for row in checks),
        "checks_total": len(checks),
        "checks": checks,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        failed = [row["check"] for row in checks if not row["pass"]]
        raise SystemExit(f"FAIL: {failed}")
    print(f"PASS: {len(checks)}/{len(checks)} checks")


if __name__ == "__main__":
    main()
