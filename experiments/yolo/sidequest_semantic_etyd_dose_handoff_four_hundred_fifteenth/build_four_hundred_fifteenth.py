#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = list(csv.DictReader(handle, delimiter="\t"))
    by_id = {row["event_id"]: row for row in events}
    target = by_id["E010"]

    occurrence = [{
        "event_id": target["event_id"],
        "record": target["record_unit_id"],
        "statement_id": target["statement_id"],
        "field_id": target["field_id"],
        "surface": target["surface_display"],
        "joint_tuple_id": target["joint_tuple_id"],
        "left_context": "OKY/Posten ansetzen > AIIN/Mass",
        "right_context_across_field": "OKY/Posten ansetzen > QOTCHOL/anwärmen > OL/fortsetzen > CTH/bereit",
        "terminal": "NO",
        "selected_whole_word_de": "Gabe",
        "workshop_expansion_de": "abgemessene Portion für den nächsten Arbeitsgang",
        "composition": "MEMORIZED_WHOLE_CARD",
    }]
    write("FOUR_HUNDRED_FIFTEENTH_ETYD_OCCURRENCE.tsv", occurrence)

    models = [
        {"candidate": "WURZELTEIL", "left_fit": 1, "handoff_fit": 2, "brevity": 4, "score": 7, "decision": "REJECT_OLD_OWNER_OVERREAD"},
        {"candidate": "VORRATSREST", "left_fit": 2, "handoff_fit": 3, "brevity": 3, "score": 8, "decision": "KEEP_AS_SECOND_EXTRACTION_RIVAL"},
        {"candidate": "GABE", "left_fit": 4, "handoff_fit": 4, "brevity": 4, "score": 12, "decision": "SELECT"},
        {"candidate": "GEBRAUCH", "left_fit": 3, "handoff_fit": 3, "brevity": 4, "score": 10, "decision": "KEEP_AS_FUNCTION_RIVAL"},
    ]
    write("FOUR_HUNDRED_FIFTEENTH_FOUR_ETYD_MODELS.tsv", models)

    values = {
        "E001": "Wurzelteil", "E002": "säubern", "E003": "aus demselben Vorrat", "E004": "bearbeiten",
        "E005": "Topf", "E006": "Wasserzulauf", "E007": "Auszug", "E008": "Posten ansetzen",
        "E009": "Sollmaß", "E010": "Gabe", "E011": "Posten ansetzen", "E012": "anwärmen",
        "E013": "fortsetzen", "E014": "bereit",
    }
    trace = []
    for order, event_id in enumerate([f"E{i:03d}" for i in range(1, 15)], start=1):
        row = by_id[event_id]
        trace.append({
            "order": order,
            "event_id": event_id,
            "locus": row["locus"],
            "field_id": row["field_id"],
            "statement_id": row["statement_id"],
            "surface": row["surface_display"],
            "selected_small_value_de": values[event_id],
            "register_action": "CREATE_NEXT_ACTIVE_ITEM" if event_id == "E010" else ("REACTIVATE_CARRIED_ITEM" if event_id == "E011" else "CONTINUE_LOCAL_SEQUENCE"),
        })
    write("FOUR_HUNDRED_FIFTEENTH_H1_FOURTEEN_EVENT_TRACE.tsv", trace)

    statements = [
        {
            "statement_id": "H1-S001",
            "card_sequence_de": "Wurzelteil > säubern > Vorrat > bearbeiten > Topf > Wasserzulauf > Auszug > Posten ansetzen > Sollmaß > Gabe",
            "continuous_reading_de": "Einen Wurzelteil säubern und bearbeiten, im Topf mit Wasser ausziehen, den Auszug als Posten setzen, bemessen und eine Gabe abteilen.",
            "end_state": "GABE_CARRIED_OPEN",
        },
        {
            "statement_id": "H1-S002",
            "card_sequence_de": "Posten ansetzen > anwärmen > fortsetzen > bereit",
            "continuous_reading_de": "Diese Gabe ansetzen, anwärmen und weiterbearbeiten, bis sie bereit ist.",
            "end_state": "PREPARED_GABE_READY_OPEN",
        },
    ]
    write("FOUR_HUNDRED_FIFTEENTH_TWO_H1_STATEMENTS.tsv", statements)

    summary = {
        "status": "PASS",
        "etyd_occurrences": 1,
        "h1_events": len(trace),
        "h1_statements": len(statements),
        "decision": "ETYD_MEMORIZED_DOSE_OR_SERVING_HANDOFF",
        "small_value_de": "GABE",
    }
    (HERE / "FOUR_HUNDRED_FIFTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
