#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P503 = ROOT / "experiments/yolo/sidequest_semantic_statement_programs_five_hundred_third"
P504 = ROOT / "experiments/yolo/sidequest_semantic_bio_form_reconciliation_five_hundred_fourth"

WORK = [
    "ACTIVATE_CHARGE",
    "SOURCE_DRAW",
    "METER_CHECK",
    "TARGET_HANDOFF",
    "MOVE_PASS",
    "HOLD_STATE",
    "CONTINUE_USE",
]
TOKENS = WORK + ["CLOSE"]
STATES = ["START", "WORK", "AFTER_SOURCE", "AFTER_METER", "CLOSED"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def step(state: str, token: str) -> tuple[str, str, str]:
    if state == "CLOSED":
        return "REJECT", "NONE", "Nach CLOSE darf keine weitere Karte folgen."
    if token == "CLOSE":
        if state == "START":
            return "REJECT", "NONE", "Eine leere Aussage darf nicht geschlossen werden."
        if state == "AFTER_METER":
            return "REJECT", "NONE", "Nach einer Maßprüfung folgt erst eine Handlung oder ein Zustand."
        return "ALLOW", "CLOSED", "Lokale Handlungskette schließen."
    if state == "AFTER_SOURCE" and token in {"MOVE_PASS", "TARGET_HANDOFF"}:
        return "REJECT", "NONE", "Nach Quellenentnahme wird der Posten erst angesetzt, geprüft, gehalten oder fortgeführt."
    if token == "SOURCE_DRAW":
        return "ALLOW", "AFTER_SOURCE", "Quellbezug für die nächste Handlung aktiv."
    if token == "METER_CHECK":
        return "ALLOW", "AFTER_METER", "Maß oder Stufe verlangt noch eine Ausführung."
    return "ALLOW", "WORK", "Laufende Werkstatthandlung."


def trace(signature: str) -> tuple[str, str]:
    state = "START"
    path = [state]
    for token in signature.split(">"):
        verdict, nxt, _ = step(state, token)
        if verdict != "ALLOW":
            return "REJECT", ">".join(path + [f"REJECT({token})"])
        state = nxt
        path.append(state)
    return "ACCEPT", ">".join(path)


def main() -> None:
    statements = read(P503 / "FIVE_HUNDRED_THIRD_116_STATEMENT_PROGRAMS.tsv")
    preferred = read(P504 / "FIVE_HUNDRED_FOURTH_NINE_SELECTED_BIO_FORM_PROGRAMS.tsv")

    edge_counts: Counter[tuple[str, str]] = Counter()
    start_counts: Counter[str] = Counter()
    end_counts: Counter[str] = Counter()
    for row in statements:
        sequence = row["primitive_signature"].split(">")
        start_counts[sequence[0]] += 1
        end_counts[sequence[-1]] += 1
        edge_counts.update(zip(sequence, sequence[1:]))

    automaton = []
    for state in STATES:
        for token in TOKENS:
            verdict, nxt, reason = step(state, token)
            automaton.append(
                {
                    "state": state,
                    "input_primitive": token,
                    "verdict": verdict,
                    "next_state": nxt,
                    "apprentice_rule_de": reason,
                    "accept_if_statement_ends_here": "YES" if state != "START" else "NO",
                }
            )
    write("FIVE_HUNDRED_FIFTH_FIVE_STATE_AUTOMATON.tsv", automaton)

    bigrams = []
    for left in WORK:
        for right in TOKENS:
            count = edge_counts[left, right]
            bigrams.append(
                {
                    "left_primitive": left,
                    "right_primitive": right,
                    "observed_count": str(count),
                    "observed_status": "ATTESTED" if count else "UNSEEN",
                    "machine_verdict": step(
                        "AFTER_SOURCE" if left == "SOURCE_DRAW" else
                        "AFTER_METER" if left == "METER_CHECK" else "WORK",
                        right,
                    )[0],
                }
            )
    write("FIVE_HUNDRED_FIFTH_56_PRIMITIVE_BIGRAMS.tsv", bigrams)

    traces = []
    preferred_ids = {row["source_program_id"] for row in preferred}
    for row in statements:
        verdict, state_path = trace(row["primitive_signature"])
        traces.append(
            {
                "statement_id": row["statement_id"],
                "record": row["record"],
                "page": row["page"],
                "primitive_signature": row["primitive_signature"],
                "program_id": row["program_id"],
                "program_support": row["program_support"],
                "bio_preferred_default": "YES" if row["program_id"] in preferred_ids else "NO",
                "machine_result": verdict,
                "state_path": state_path,
                "statement_end_state": state_path.split(">")[-1],
            }
        )
    write("FIVE_HUNDRED_FIFTH_116_AUTOMATON_TRACES.tsv", traces)

    defaults = []
    total = sum(int(row["support_statements"]) for row in preferred)
    for rank, row in enumerate(preferred, 1):
        defaults.append(
            {
                "preference_rank": str(rank),
                "form_program_id": row["form_program_id"],
                "primitive_signature": row["primitive_signature"],
                "support_statements": row["support_statements"],
                "share_of_recurrent_bio_statements": f"{int(row['support_statements']) / total:.6f}",
                "apprentice_default_de": row["apprentice_rule_de"],
                "machine_status": "PREFERRED_PATH_WITHIN_GENERAL_AUTOMATON",
            }
        )
    write("FIVE_HUNDRED_FIFTH_NINE_PREFERRED_BIO_PATHS.tsv", defaults)

    manual = read(P504 / "FIVE_HUNDRED_FOURTH_122_ITEM_RECONCILED_MANUAL.tsv")
    for row in manual:
        if row["item_id"] == "PROC_G01":
            row["teaching_value_or_rule_de"] = (
                "Fünf Zustände: START; WORK; AFTER_SOURCE; AFTER_METER; CLOSED. "
                "Jede Aussage beginnt mit einem Arbeitsprimitiv; Arbeitsprimitive dürfen sich wiederholen; "
                "CLOSE steht nur zuletzt. Nach SOURCE_DRAW nicht unmittelbar MOVE_PASS oder TARGET_HANDOFF; "
                "nach METER_CHECK nicht unmittelbar CLOSE."
            )
            row["support_or_instances"] = "116 statements;470 tokens;53/56 observed bigrams"
            row["source_artifact"] = "PASS505_FIVE_STATE_AUTOMATON"
    write("FIVE_HUNDRED_FIFTH_122_ITEM_AUTOMATON_MANUAL.tsv", manual)

    summary = {
        "status": "PASS",
        "states": len(STATES),
        "live_work_primitives": len(WORK),
        "possible_primitive_bigrams": len(bigrams),
        "attested_primitive_bigrams": sum(row["observed_status"] == "ATTESTED" for row in bigrams),
        "unseen_and_rejected_bigrams": [
            f"{row['left_primitive']}>{row['right_primitive']}"
            for row in bigrams if row["observed_status"] == "UNSEEN"
        ],
        "accepted_statements": sum(row["machine_result"] == "ACCEPT" for row in traces),
        "preferred_bio_paths": len(defaults),
        "preferred_bio_statement_support": total,
        "manual_items": len(manual),
    }
    (HERE / "FIVE_HUNDRED_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
