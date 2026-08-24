#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P503 = ROOT / "experiments/yolo/sidequest_semantic_statement_programs_five_hundred_third"
P517 = ROOT / "experiments/yolo/sidequest_semantic_allograph_blocks_five_hundred_seventeenth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def edit_alignment(source: tuple[str, ...], target: tuple[str, ...]) -> tuple[int, str]:
    """Return deterministic Levenshtein distance and a compact base->target script."""
    n, m = len(source), len(target)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sub = dp[i - 1][j - 1] + (source[i - 1] != target[j - 1])
            delete = dp[i - 1][j] + 1
            insert = dp[i][j - 1] + 1
            dp[i][j] = min(sub, delete, insert)
    i, j = n, m
    reverse_ops: list[str] = []
    while i or j:
        if i and j and source[i - 1] == target[j - 1] and dp[i][j] == dp[i - 1][j - 1]:
            i -= 1
            j -= 1
        elif i and j and dp[i][j] == dp[i - 1][j - 1] + 1:
            reverse_ops.append(f"SUB@{i}:{source[i-1]}>{target[j-1]}")
            i -= 1
            j -= 1
        elif i and dp[i][j] == dp[i - 1][j] + 1:
            reverse_ops.append(f"DEL@{i}:{source[i-1]}")
            i -= 1
        else:
            reverse_ops.append(f"INS@{i+1}:{target[j-1]}")
            j -= 1
    reverse_ops.reverse()
    return dp[n][m], "|".join(reverse_ops) if reverse_ops else "EXACT"


def main() -> None:
    recurring = read_tsv(P503 / "FIVE_HUNDRED_THIRD_NINE_RECURRENT_PROGRAMS.tsv")
    statement_rows = read_tsv(P503 / "FIVE_HUNDRED_THIRD_116_STATEMENT_PROGRAMS.tsv")
    master_log = read_tsv(P517 / "FIVE_HUNDRED_SEVENTEENTH_381_BLOCK_MASTER_LOG.tsv")

    motif_signatures = {
        "M01": "ACTIVATE_CHARGE>METER_CHECK>MOVE_PASS",
        "M02": "METER_CHECK>MOVE_PASS>METER_CHECK",
        "M03": "MOVE_PASS>ACTIVATE_CHARGE>MOVE_PASS",
        "M04": "METER_CHECK>MOVE_PASS",
        "M05": "METER_CHECK>HOLD_STATE",
        "M06": "MOVE_PASS>METER_CHECK",
        "M07": "MOVE_PASS>ACTIVATE_CHARGE",
        "M08": "ACTIVATE_CHARGE>METER_CHECK",
        "M09": "TARGET_HANDOFF>METER_CHECK",
    }
    bases: list[dict[str, str]] = []
    for row in recurring:
        bases.append(
            {
                "base_id": row["program_id"],
                "base_family": "BIO_RECURRENT_DEFAULT",
                "primitive_signature": row["primitive_signature"],
                "observed_support": row["support"],
                "teaching_use": "COMPARISON_BASE_NOT_MEMORIZED_SCRIPT",
            }
        )
    for motif_id, signature in motif_signatures.items():
        bases.append(
            {
                "base_id": motif_id,
                "base_family": "SHARED_SENTENCE_MOTIF",
                "primitive_signature": signature,
                "observed_support": "SEE_PASS477",
                "teaching_use": "COMPARISON_BASE_NOT_MEMORIZED_SCRIPT",
            }
        )
    write_tsv("FIVE_HUNDRED_EIGHTEENTH_EIGHTEEN_BASE_PATHS.tsv", bases)

    base_tokens = {
        row["base_id"]: tuple(row["primitive_signature"].split(">")) for row in bases
    }
    unique_statements = [row for row in statement_rows if row["program_status"] == "UNIQUE"]
    audit: list[dict[str, str]] = []
    for row in unique_statements:
        actual = tuple(row["primitive_signature"].split(">"))
        candidates = []
        for base_id, signature in base_tokens.items():
            distance, script = edit_alignment(signature, actual)
            candidates.append((distance, base_id, script))
        distance, base_id, script = min(candidates)
        if distance == 0:
            fit = "EXACT_BASE"
        elif distance <= 3:
            fit = "SMALL_LOCAL_VARIATION"
        else:
            fit = "LONG_LOCAL_CHAIN"
        audit.append(
            {
                "statement_id": row["statement_id"],
                "record": row["record"],
                "page": row["page"],
                "events": row["events"],
                "actual_signature": row["primitive_signature"],
                "nearest_base_id": base_id,
                "nearest_base_signature": next(
                    base["primitive_signature"] for base in bases if base["base_id"] == base_id
                ),
                "edit_distance": str(distance),
                "edit_script": script,
                "fit_class": fit,
                "teach_as_program": "NO",
                "workshop_reading": "EMERGENT_CARD_BY_CARD_PATH",
            }
        )
    recipe_counts = Counter((row["nearest_base_id"], row["edit_script"]) for row in audit)
    for row in audit:
        key = (row["nearest_base_id"], row["edit_script"])
        row["same_edit_recipe_count"] = str(recipe_counts[key])
        row["reusable_edit_recipe"] = "YES" if recipe_counts[key] > 1 else "NO"
    write_tsv("FIVE_HUNDRED_EIGHTEENTH_63_UNIQUE_PROGRAM_EDIT_AUDIT.tsv", audit)

    distance_counts = Counter(int(row["edit_distance"]) for row in audit)
    distance_summary = []
    for distance in sorted(distance_counts):
        distance_summary.append(
            {
                "edit_distance": str(distance),
                "unique_programs": str(distance_counts[distance]),
                "cumulative_programs": str(
                    sum(count for dist, count in distance_counts.items() if dist <= distance)
                ),
                "interpretation": (
                    "EXACT_BASE"
                    if distance == 0
                    else "SMALL_LOCAL_VARIATION"
                    if distance <= 3
                    else "LONG_LOCAL_CHAIN"
                ),
            }
        )
    write_tsv("FIVE_HUNDRED_EIGHTEENTH_EDIT_DISTANCE_SUMMARY.tsv", distance_summary)

    audit_by_statement = {row["statement_id"]: row for row in audit}
    statement_program = {row["statement_id"]: row["program_id"] for row in statement_rows}
    revised_log: list[dict[str, str]] = []
    decisions: list[dict[str, str]] = []
    for row in master_log:
        reasons: list[str] = []
        if row["owner_reset"] == "YES":
            reasons.append("RESET_VISIBLE_OWNER")
            decisions.append(
                {
                    "decision_no": "",
                    "event_id": row["event_id"],
                    "statement_id": row["statement_id"],
                    "record": row["record"],
                    "page": row["page"],
                    "decision_type": "RESET_VISIBLE_OWNER",
                    "selected_value": row["owner_code"],
                }
            )
        if row["block_start_decision"] == "YES":
            reasons.append("ENTER_ALLOGRAPH_BLOCK")
            decisions.append(
                {
                    "decision_no": "",
                    "event_id": row["event_id"],
                    "statement_id": row["statement_id"],
                    "record": row["record"],
                    "page": row["page"],
                    "decision_type": "ENTER_ALLOGRAPH_BLOCK",
                    "selected_value": row["allograph_block_id"],
                }
            )
        fit = audit_by_statement.get(row["statement_id"])
        revised_log.append(
            {
                **row,
                "nearest_program_base": fit["nearest_base_id"] if fit else statement_program[row["statement_id"]],
                "nearest_program_edit_distance": fit["edit_distance"] if fit else "0",
                "program_selection_decision": "NONE",
                "emergent_program_rule": "READ_NEXT_CARD_AND_APPLY_FIVE_STATE_AUTOMATON",
                "emergent_conscious_decision_count": str(len(reasons)),
                "emergent_conscious_reasons": "|".join(reasons) if reasons else "NONE",
                "emergent_master_mode": "CONSCIOUS_LOCAL_CHOICE" if reasons else "AUTOMATIC_FLOW",
            }
        )
    for decision_no, row in enumerate(decisions, 1):
        row["decision_no"] = str(decision_no)
    write_tsv("FIVE_HUNDRED_EIGHTEENTH_381_EMERGENT_MASTER_LOG.tsv", revised_log)
    write_tsv("FIVE_HUNDRED_EIGHTEENTH_71_CONSCIOUS_DECISIONS.tsv", decisions)

    fit_counts = Counter(row["fit_class"] for row in audit)
    summary = {
        "status": "PASS",
        "comparison_bases": len(bases),
        "unique_statement_programs": len(audit),
        "exact_or_within_three_edits": fit_counts["EXACT_BASE"] + fit_counts["SMALL_LOCAL_VARIATION"],
        "long_local_chains": fit_counts["LONG_LOCAL_CHAIN"],
        "reused_exact_edit_recipes": sum(count > 1 for count in recipe_counts.values()),
        "program_selection_decisions_removed": 63,
        "remaining_decision_instances": len(decisions),
        "remaining_conscious_events": sum(
            row["emergent_master_mode"] == "CONSCIOUS_LOCAL_CHOICE" for row in revised_log
        ),
        "automatic_events": sum(
            row["emergent_master_mode"] == "AUTOMATIC_FLOW" for row in revised_log
        ),
        "decision_types": dict(Counter(row["decision_type"] for row in decisions)),
    }
    (HERE / "FIVE_HUNDRED_EIGHTEENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
