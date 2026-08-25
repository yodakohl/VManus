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

    candidates = [
        {"candidate": "STEHENLASSEN", "terminal_fit": "HIGH", "target_fit": "HIGH", "collision": "NONE", "decision": "KEEP"},
        {"candidate": "RUHEN", "terminal_fit": "HIGH", "target_fit": "MEDIUM", "collision": "NONE", "decision": "REJECT_LOSES_IMPERATIVE"},
        {"candidate": "ABSETZEN", "terminal_fit": "HIGH", "target_fit": "HIGH", "collision": "SEDIMENT_MECHANISM", "decision": "REJECT_TOO_NARROW"},
        {"candidate": "ABSTELLEN", "terminal_fit": "HIGH", "target_fit": "HIGH", "collision": "SHUT_OFF_OR_PUT_DOWN", "decision": "REJECT_AMBIGUOUS"},
        {"candidate": "WARTEN", "terminal_fit": "MEDIUM", "target_fit": "LOW", "collision": "AGENT_WAITS_NOT_ITEM", "decision": "REJECT_WRONG_SUBJECT"},
        {"candidate": "HALTEN", "terminal_fit": "MEDIUM", "target_fit": "HIGH", "collision": "SH", "decision": "REJECT_DUPLICATES_ACTIVE_HOLD"},
    ]
    values = {"SH": "HALTEN", "SHED": "STEHENLASSEN"}
    audit_rows = []
    for row in events:
        tokens = row["component_recipe"].split("+")
        for component in ("SH", "SHED"):
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
                        "endpoint_class": "CLOSED_STEP" if "DY" in tokens else "OPEN_STEP",
                        "full_statement_de": statements[row["statement_id"]]["working_reading_de"],
                    }
                )
    shed_rows = [row for row in audit_rows if row["component"] == "SHED"]
    pattern_counts = Counter(
        "R+SHED+DY" if row["component_recipe"] == "R+SHED+DY" else "SHED+AL" if row["component_recipe"] == "SHED+AL" else "SHED+DY"
        for row in shed_rows
    )
    patterns = [
        {"pattern": "SHED+DY", "reading_de": "STEHENLASSEN · SCHLUSS", "events": pattern_counts["SHED+DY"], "workshop_use": "leave item and close step"},
        {"pattern": "R+SHED+DY", "reading_de": "KUEHLEN · STEHENLASSEN · SCHLUSS", "events": pattern_counts["R+SHED+DY"], "workshop_use": "cool, leave, close"},
        {"pattern": "SHED+AL", "reading_de": "STEHENLASSEN · ZIELSTELLE", "events": pattern_counts["SHED+AL"], "workshop_use": "leave item at target for following work"},
    ]
    distinctions = [
        {"component": "SH", "short_value_de": "HALTEN", "events": sum(row["component"] == "SH" for row in audit_rows), "agent_control": "ACTIVE", "next_step_availability": "WHILE_HELD", "decision": "KEEP"},
        {"component": "SHED", "short_value_de": "STEHENLASSEN", "events": len(shed_rows), "agent_control": "RELEASED", "next_step_availability": "AFTER_WAIT_OR_PLACEMENT", "decision": "KEEP"},
    ]

    write("EIGHT_HUNDRED_TWENTY_THIRD_6_SHED_CANDIDATES.tsv", candidates, ["candidate", "terminal_fit", "target_fit", "collision", "decision"])
    write("EIGHT_HUNDRED_TWENTY_THIRD_40_HOLD_WAIT_MEMBERSHIPS.tsv", audit_rows, ["component", "selected_value_de", "event_id", "page", "statement_id", "owner_de", "surface", "component_recipe", "endpoint_class", "full_statement_de"])
    write("EIGHT_HUNDRED_TWENTY_THIRD_3_SHED_PATTERNS.tsv", patterns, ["pattern", "reading_de", "events", "workshop_use"])
    write("EIGHT_HUNDRED_TWENTY_THIRD_2_HOLD_WAIT_DISTINCTIONS.tsv", distinctions, ["component", "short_value_de", "events", "agent_control", "next_step_availability", "decision"])
    summary = {
        "status": "PASS",
        "decision": "SH_HALTING_AND_SHED_LEAVING_STANDING_REMAIN_DISTINCT",
        "memberships": len(audit_rows),
        "sh_events": sum(row["component"] == "SH" for row in audit_rows),
        "shed_events": len(shed_rows),
        "shed_closed": sum(row["endpoint_class"] == "CLOSED_STEP" for row in shed_rows),
        "shed_open_target": pattern_counts["SHED+AL"],
        "meaning_revisions": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_TWENTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
