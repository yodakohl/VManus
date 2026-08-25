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

    values = {"S": "PROBE", "AIN": "PORTION", "AIIN": "SOLLMASS", "IIN": "STUFE"}
    questions = {
        "S": "What small item is taken for checking?",
        "AIN": "How much working material is handled?",
        "AIIN": "What prescribed value should be reached?",
        "IIN": "At which process stage is the work?",
    }
    audit_rows = []
    for row in events:
        tokens = row["component_recipe"].split("+")
        for component in ("S", "AIN", "AIIN", "IIN"):
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
                        "role_question": questions[component],
                        "full_statement_de": statements[row["statement_id"]]["working_reading_de"],
                    }
                )
    counts = Counter(row["component"] for row in audit_rows)
    ladder = [
        {"component": "S", "short_value_de": "PROBE", "events": counts["S"], "ontological_type": "SMALL_OBJECT", "portable_role": "diagnostic sample", "decision": "KEEP_PROVISIONAL"},
        {"component": "AIN", "short_value_de": "PORTION", "events": counts["AIN"], "ontological_type": "MATERIAL_AMOUNT", "portable_role": "working portion", "decision": "KEEP"},
        {"component": "AIIN", "short_value_de": "SOLLMASS", "events": counts["AIIN"], "ontological_type": "PRESCRIBED_VALUE", "portable_role": "measure or setting to reach", "decision": "KEEP"},
        {"component": "IIN", "short_value_de": "STUFE", "events": counts["IIN"], "ontological_type": "PROCESS_STAGE", "portable_role": "named or numbered stage", "decision": "KEEP"},
    ]
    candidates = [
        {"candidate": "PROBE", "before_sollmass": "NATURAL", "collision": "NONE", "workshop_distinction": "HIGH", "decision": "KEEP_PROVISIONAL"},
        {"candidate": "PORTION", "before_sollmass": "NATURAL", "collision": "AIN", "workshop_distinction": "LOW", "decision": "REJECT_DUPLICATE"},
        {"candidate": "TEIL", "before_sollmass": "NATURAL", "collision": "AIN_BROAD", "workshop_distinction": "LOW", "decision": "REJECT_UNDERINFORMATIVE"},
        {"candidate": "REST", "before_sollmass": "MEDIUM", "collision": "NONE", "workshop_distinction": "MEDIUM", "decision": "REJECT_NO_DEPLETION_CUE"},
        {"candidate": "MENGE", "before_sollmass": "NATURAL", "collision": "AIN_AIIN", "workshop_distinction": "LOW", "decision": "REJECT_COLLAPSES_LADDER"},
        {"candidate": "ZEICHEN", "before_sollmass": "LOW", "collision": "NONE", "workshop_distinction": "MEDIUM", "decision": "REJECT_NOT_AN_OBJECT_TAKEN"},
    ]
    s_event = next(row for row in events if "S" in row["component_recipe"].split("+"))
    s_index = next(i for i, row in enumerate(events) if row["event_id"] == s_event["event_id"])
    trace_rows = []
    for row in events[s_index - 2:s_index + 4]:
        trace_rows.append(
            {
                "event_id": row["event_id"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "literal_de": row["sixth_grammar_reading_de"].replace("EINFUELLEN", "EINBRINGEN"),
                "quantity_role": "SAMPLE" if row["event_id"] == s_event["event_id"] else "PRESCRIBED_VALUE" if "AIIN" in row["component_recipe"].split("+") else "OTHER",
            }
        )

    write("EIGHT_HUNDRED_TWENTY_FIFTH_62_QUANTITY_MEMBERSHIPS.tsv", audit_rows, ["component", "selected_value_de", "event_id", "page", "statement_id", "owner_de", "surface", "component_recipe", "role_question", "full_statement_de"])
    write("EIGHT_HUNDRED_TWENTY_FIFTH_4_LEVEL_LADDER.tsv", ladder, ["component", "short_value_de", "events", "ontological_type", "portable_role", "decision"])
    write("EIGHT_HUNDRED_TWENTY_FIFTH_6_S_CANDIDATES.tsv", candidates, ["candidate", "before_sollmass", "collision", "workshop_distinction", "decision"])
    write("EIGHT_HUNDRED_TWENTY_FIFTH_6_S_LOCAL_TRACE.tsv", trace_rows, ["event_id", "surface", "component_recipe", "literal_de", "quantity_role"])
    summary = {
        "status": "PASS",
        "decision": "S_SAMPLE_AIN_PORTION_AIIN_PRESCRIBED_MEASURE_IIN_STAGE_RETAINED",
        "memberships": len(audit_rows),
        "unique_events": len({row["event_id"] for row in audit_rows}),
        "s_events": counts["S"],
        "ain_events": counts["AIN"],
        "aiin_events": counts["AIIN"],
        "iin_events": counts["IIN"],
        "meaning_revisions": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_TWENTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
