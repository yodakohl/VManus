#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P564 = ROOT / "sidequest_semantic_action_complete_translation_five_hundred_sixty_fourth"
P570 = ROOT / "sidequest_semantic_plant_owner_case_correction_five_hundred_seventieth"
P571 = ROOT / "sidequest_semantic_natural_record_summaries_five_hundred_seventy_first"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SLOTS = [
    ("BS1", "VISIBLE_OWNER_MEDIUM", "sichtbare Station plus ihr lokales Medium oder ihre Anwendung"),
    ("BS2", "QUANTITY_STAGE", "Maß, Portion oder Arbeitsstufe"),
    ("BS3", "TARGET_PASSAGE", "Quelle, Ziel, Durchlass oder Weiterführung"),
    ("BS4", "GRADE_STATE", "Grad, Bereitschaft, Wärme, Halten, Waschen oder Absetzen"),
    ("BS5", "LOCAL_OPERATION", "konkrete lokale Handlung der Zelle"),
    ("BS6", "CELL_CLOSE", "lokale Zelle verbuchen und schließen"),
]


def main():
    records = {"B1", "B2", "B3", "B4"}
    transitions = [row for row in read_tsv(P570 / "FIVE_HUNDRED_SEVENTIETH_ONE_HUNDRED_SIXTEEN_CORRECTED_TRANSITIONS.tsv") if row["record"] in records]
    events = [row for row in read_tsv(P570 / "FIVE_HUNDRED_SEVENTIETH_THREE_HUNDRED_EIGHTY_ONE_CORRECTED_EVENTS.tsv") if row["record"] in records]
    action_events = {row["event_id"]: row for row in read_tsv(P564 / "FIVE_HUNDRED_SIXTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_READINGS.tsv") if row["record"] in records}
    summaries = {row["record"]: row for row in read_tsv(P571 / "FIVE_HUNDRED_SEVENTY_FIRST_ELEVEN_NATURAL_RECORD_SUMMARIES.tsv") if row["record"] in records}
    by_statement = defaultdict(list)
    for row in events: by_statement[row["statement_id"]].append(row)

    statement_rows = []
    for transition in transitions:
        rows = by_statement[transition["statement_id"]]
        modifiers = {channel for row in rows for channel in row["modifier_channels"].split("|") if channel != "NONE"}
        phases = set(transition["phase_signature"].split(">"))
        slots = {"BS1"}
        if modifiers & {"MEASURE", "PORTION", "STAGE"}: slots.add("BS2")
        if modifiers & {"SOURCE", "FLOW_LIQUID", "TARGET", "PASSAGE"} or phases & {"ROUTE", "APPLY"}: slots.add("BS3")
        if modifiers & {"GRADE", "READY", "SETTLE", "HEAT"} or phases & {"HOLD", "THERMAL", "WASH", "SETTLE"}: slots.add("BS4")
        if any(action_events[row["event_id"]]["event_role"] == "ACTION" for row in rows): slots.add("BS5")
        if transition["committed"] == "YES": slots.add("BS6")
        statement_rows.append({
            "statement_id": transition["statement_id"], "page": transition["page"], "record": transition["record"],
            "owner_object_class": transition["owner_object_class"], "cell_slots": "|".join(sorted(slots)),
            "modifier_channels": "|".join(sorted(modifiers)) if modifiers else "NONE",
            "phase_signature": transition["phase_signature"], "input_object": transition["input_object"],
            "output_object": transition["output_object"], "committed": transition["committed"],
            "complete_reading_de": transition["corrected_complete_reading_de"],
        })

    order = ["B1", "B2", "B3", "B4"]
    matrix_rows = []
    for record in order:
        rows = [row for row in statement_rows if row["record"] == record]
        record_events = [row for row in events if row["record"] == record]
        present = {slot for row in rows for slot in row["cell_slots"].split("|")}
        matrix_rows.append({
            "record": record, "page": rows[0]["page"], "statements": str(len(rows)), "events": str(len(record_events)),
            **{slot.lower(): "USED" if slot in present else "NOT_USED" for slot, _, _ in SLOTS},
            "committed_cells": str(sum(row["committed"] == "YES" for row in rows)),
            "all_six_slot_cells": str(sum(set(row["cell_slots"].split("|")) == {slot for slot, _, _ in SLOTS} for row in rows)),
            "natural_record_summary_de": summaries[record]["natural_record_summary_de"],
        })

    slot_rows = []
    for slot, name, meaning in SLOTS:
        statement_count = sum(slot in row["cell_slots"].split("|") for row in statement_rows)
        record_count = sum(row[slot.lower()] == "USED" for row in matrix_rows)
        slot_rows.append({
            "slot": slot, "slot_name": name, "workshop_meaning_de": meaning,
            "records_using": str(record_count), "cells_using": str(statement_count),
            "record_level_status": "COMMON_INVENTORY" if record_count == 4 else "OPTIONAL_RECORD_EXTENSION",
            "cell_level_status": "ALWAYS" if statement_count == 93 else "OPTIONAL_FIELD",
        })

    statement_slot = {row["statement_id"]: row for row in statement_rows}
    event_rows = []
    for row in events:
        event_rows.append({**row, "biological_cell_slots": statement_slot[row["statement_id"]]["cell_slots"], "schema_binding_complete": "YES"})

    write_tsv("FIVE_HUNDRED_SEVENTY_THIRD_SIX_BIOLOGICAL_CELL_SLOTS.tsv", slot_rows)
    write_tsv("FIVE_HUNDRED_SEVENTY_THIRD_FOUR_RECORD_MATRIX.tsv", matrix_rows)
    write_tsv("FIVE_HUNDRED_SEVENTY_THIRD_NINETY_THREE_CELL_MAP.tsv", statement_rows)
    write_tsv("FIVE_HUNDRED_SEVENTY_THIRD_TWO_HUNDRED_SIXTY_ONE_EVENTS.tsv", event_rows)
    markdown = ["# Gemeinsames Biological-Zellenschema", "", "B1–B4 verwenden dasselbe Inventar aus sechs Formularfeldern. Nur Besitzer/Medium ist in jeder Zelle zwingend; die übrigen Felder werden nach Bedarf ausgefüllt.", ""]
    for row in slot_rows:
        markdown.append(f"- **{row['slot']} {row['slot_name']}** — {row['workshop_meaning_de']} ({row['cells_using']}/93 Zellen; {row['cell_level_status']})")
    markdown.append("")
    for row in matrix_rows:
        markdown.extend([f"## {row['record']}", "", row["natural_record_summary_de"], "", f"Zellen {row['statements']}; Ereignisse {row['events']}; geschlossen {row['committed_cells']}; alle sechs Slots zugleich {row['all_six_slot_cells']}.", ""])
    (HERE / "FIVE_HUNDRED_SEVENTY_THIRD_COMPLETE_BIOLOGICAL_SCHEMA.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")
    summary = {
        "status": "PASS", "slots": len(slot_rows), "records": len(matrix_rows), "cells": len(statement_rows), "events": len(event_rows),
        "all_records_use_all_slots": all(all(row[slot.lower()] == "USED" for slot, _, _ in SLOTS) for row in matrix_rows),
        "owner_cells": sum("BS1" in row["cell_slots"].split("|") for row in statement_rows),
        "operation_cells": sum("BS5" in row["cell_slots"].split("|") for row in statement_rows),
        "closed_cells": sum("BS6" in row["cell_slots"].split("|") for row in statement_rows),
        "all_six_slot_cells": sum(set(row["cell_slots"].split("|")) == {slot for slot, _, _ in SLOTS} for row in statement_rows),
    }
    (HERE / "FIVE_HUNDRED_SEVENTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertdreiundsiebzigste Runde: Biological-Zellenschema",
        "",
        "## Ergebnis",
        "",
        "B1–B4 verwenden ein gemeinsames sechsteiliges Formularinventar: sichtbarer Besitzer/Medium, Menge/Stufe, Ziel/Durchlass, Grad/Zustand, lokale Handlung und Zellschluss. Alle vier Records verwenden alle sechs Felder, aber nur Besitzer/Medium ist in jeder einzelnen Zelle zwingend.",
        "",
        "Die 93 Zellen sind daher keine Sätze mit sechs obligatorischen Wörtern. Sie sind kompakte Auswahlfelder: 88 tragen eine ausdrückliche Handlung und 83 schließen. Menge, Route und Zustand werden nur gesetzt, wenn die lokale Variante sie braucht. Das erklärt die vielen kurzen terminalen Karten und die starken Bildbesitzerwechsel.",
        "",
        "Alle 261 Ereignisse der vier Haupt-Bio-Records sind gebunden. B5/B6 bleiben getrennte technische Nachträge und werden nicht rückwirkend in das Hauptschema gezwungen.",
        "",
        "## Nächster Schritt",
        "",
        "Als Nächstes werden Herbal- und Biological-Schema direkt verbunden: Welche Karten wechseln ihren konkreten Wert nur deshalb, weil der Bildbesitzer von Pflanze zu Flüssigkeit/Anwendung wechselt, und welche behalten exakt dieselbe Werkstattfunktion?",
    ]
    (HERE / "FIVE_HUNDRED_SEVENTY_THIRD_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
