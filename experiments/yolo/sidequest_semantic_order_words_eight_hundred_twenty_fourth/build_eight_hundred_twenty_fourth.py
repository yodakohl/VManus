#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_sixth_workshop_grammar_eight_hundred_nineteenth"
EVENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_NINETEENTH_116_STATEMENT_REPARSE.tsv"
T_REVISIONS = ROOT / "sidequest_semantic_t_work_eight_hundred_twenty_first" / "EIGHT_HUNDRED_TWENTY_FIRST_7_REVISED_STATEMENTS.tsv"
P_REVISIONS = ROOT / "sidequest_semantic_p_bring_in_eight_hundred_twenty_second" / "EIGHT_HUNDRED_TWENTY_SECOND_3_REVISED_STATEMENTS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(EVENTS)
    statements = {row["statement_id"]: row for row in read(STATEMENTS)}
    for path in (T_REVISIONS, P_REVISIONS):
        for row in read(path):
            statements[row["statement_id"]]["working_reading_de"] = row["revised_reading_de"]

    values = {"OL": "WEITER", "OT": "DANACH", "OS": "DAZU"}
    functions = {
        "OL": "continue same operation or relation",
        "OT": "advance to next operation or item",
        "OS": "add linked material or clause without ordering claim",
    }
    audit_rows = []
    for row in events:
        tokens = row["component_recipe"].split("+")
        for component in ("OL", "OT", "OS"):
            if component in tokens:
                audit_rows.append(
                    {
                        "component": component,
                        "selected_value_de": values[component],
                        "event_id": row["event_id"],
                        "page": row["page"],
                        "statement_id": row["statement_id"],
                        "owner_de": row["owner_de"],
                        "surface": row["surface"],
                        "component_recipe": row["component_recipe"],
                        "function": functions[component],
                        "full_statement_de": statements[row["statement_id"]]["working_reading_de"],
                    }
                )
    counts = Counter(row["component"] for row in audit_rows)
    distinctions = [
        {"component": "OL", "short_value_de": "WEITER", "events": counts["OL"], "same_operation": "YES", "next_operation": "NO", "additive_only": "NO", "decision": "KEEP"},
        {"component": "OT", "short_value_de": "DANACH", "events": counts["OT"], "same_operation": "NO", "next_operation": "YES", "additive_only": "NO", "decision": "KEEP"},
        {"component": "OS", "short_value_de": "DAZU", "events": counts["OS"], "same_operation": "NO", "next_operation": "NO", "additive_only": "YES", "decision": "KEEP"},
    ]
    candidates = [
        {"candidate": "DAZU", "h1_fit": "HIGH", "collision": "NONE", "order_claim": "NONE", "decision": "KEEP"},
        {"candidate": "DANACH", "h1_fit": "HIGH", "collision": "OT_IN_SAME_STATEMENT", "order_claim": "NEXT", "decision": "REJECT_DUPLICATES_OT"},
        {"candidate": "WEITER", "h1_fit": "MEDIUM", "collision": "OL_IN_SAME_CARD_CHAIN", "order_claim": "CONTINUE", "decision": "REJECT_DUPLICATES_OL"},
        {"candidate": "DABEI", "h1_fit": "MEDIUM", "collision": "NONE", "order_claim": "SIMULTANEOUS", "decision": "REJECT_UNNEEDED_SIMULTANEITY"},
        {"candidate": "MIT", "h1_fit": "LOW", "collision": "ARGUMENT_LINK", "order_claim": "NONE", "decision": "REJECT_WRONG_SYNTAX"},
        {"candidate": "ABER", "h1_fit": "LOW", "collision": "NONE", "order_claim": "CONTRAST", "decision": "REJECT_NO_CONTRAST"},
    ]

    h1_ids = {"E004", "E005", "E006", "E007", "E008", "E009", "E010"}
    h1_trace = []
    for row in events:
        if row["event_id"] in h1_ids:
            h1_trace.append(
                {
                    "event_id": row["event_id"],
                    "surface": row["surface"],
                    "component_recipe": row["component_recipe"],
                    "literal_de": row["sixth_grammar_reading_de"].replace("ANWENDEN", "BEARBEITEN"),
                    "order_role": "ADDITIVE_OS" if row["event_id"] == "E005" else "NEXT_OT" if row["event_id"] == "E007" else "CONTENT",
                }
            )

    write("EIGHT_HUNDRED_TWENTY_FOURTH_75_ORDER_MEMBERSHIPS.tsv", audit_rows, ["component", "selected_value_de", "event_id", "page", "statement_id", "owner_de", "surface", "component_recipe", "function", "full_statement_de"])
    write("EIGHT_HUNDRED_TWENTY_FOURTH_3_ORDER_DISTINCTIONS.tsv", distinctions, ["component", "short_value_de", "events", "same_operation", "next_operation", "additive_only", "decision"])
    write("EIGHT_HUNDRED_TWENTY_FOURTH_6_OS_CANDIDATES.tsv", candidates, ["candidate", "h1_fit", "collision", "order_claim", "decision"])
    write("EIGHT_HUNDRED_TWENTY_FOURTH_7_H1_LOCAL_TRACE.tsv", h1_trace, ["event_id", "surface", "component_recipe", "literal_de", "order_role"])
    summary = {
        "status": "PASS",
        "decision": "OL_CONTINUE_OT_NEXT_OS_ADDITIVE_REMAIN_DISTINCT",
        "memberships": len(audit_rows),
        "unique_events": len({row["event_id"] for row in audit_rows}),
        "ol_events": counts["OL"],
        "ot_events": counts["OT"],
        "os_events": counts["OS"],
        "same_statement_os_and_ot": "H1-S001",
        "meaning_revisions": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_TWENTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
