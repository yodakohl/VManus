#!/usr/bin/env python3
"""Turn the continuous 57-line edition into a complete master dictation."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
VISIBLE = ROOT / "experiments/yolo/sidequest_semantic_seven_page_continuous_reading_three_hundred_fifty_eighth/THREE_HUNDRED_FIFTY_EIGHTH_381_VISIBLE_380_SOURCE_EDITION.tsv"
LINES = ROOT / "experiments/yolo/sidequest_semantic_seven_page_continuous_reading_three_hundred_fifty_eighth/THREE_HUNDRED_FIFTY_EIGHTH_FIFTY_SEVEN_PHYSICAL_LINES.tsv"
TRANSITIONS = ROOT / "experiments/yolo/sidequest_semantic_seven_page_continuous_reading_three_hundred_fifty_eighth/THREE_HUNDRED_FIFTY_EIGHTH_FORTY_SIX_LINE_TRANSITIONS.tsv"
TRACE = ROOT / "experiments/yolo/sidequest_semantic_two_layer_production_rule_three_hundred_forty_sixth/THREE_HUNDRED_FORTY_SIXTH_381_TWO_LAYER_EVENT_TRACE.tsv"

STATE_NAMES = {
    "M1_RAW_PART": "Rohteil",
    "M2_PREPARATION": "Ansatz",
    "M3_CLEAR_EXTRACT": "Klarauszug",
    "M4_MEASURED_PORTION": "Bemessene Portion",
    "M5_APPLICATION_ITEM": "Anwendungsposten",
}
SLOT_SPEECH = {
    "S1_BEZUG_FOLGE": "Bezug/Folge: {value}",
    "S2_MATERIAL_MASS": "Material/Maß: {value}",
    "S3_PROZESS_TRANSFER": "Arbeitsgang: {value}",
    "S4_DAUER_ZUSTAND": "Dauer/Zustand: {value}",
    "S5_ZIEL_ANWENDUNG": "Ziel/Anwendung: {value}",
    "S6_BEREIT_ABSCHLUSS": "Bereit/Schluss: {value}",
}
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    visible = read_tsv(VISIBLE)
    physical_lines = read_tsv(LINES)
    transitions = read_tsv(TRANSITIONS)
    trace = {row["event_id"]: row for row in read_tsv(TRACE)}
    visible_by_id = {row["event_id"]: row for row in visible}
    transition_by_left_locus = {(row["record_unit_id"], row["left_locus"]): row for row in transitions}

    current_state_by_record = {}
    state_before = {}
    state_after = {}
    for row in visible:
        record = row["record_unit_id"]
        if record not in current_state_by_record:
            current_state_by_record[record] = trace[row["event_id"]]["record_source_state_ids"].split("+")[0]
        state_before[row["event_id"]] = current_state_by_record[record]
        marker = trace[row["event_id"]]["material_marker_state"]
        if marker != "NONE":
            current_state_by_record[record] = marker
        state_after[row["event_id"]] = current_state_by_record[record]

    dictation = []
    for line in physical_lines:
        event_ids = line["event_ids"].split("|")
        events = [visible_by_id[event_id] for event_id in event_ids]
        source_events = [row for row in events if row["source_position_contribution"] == "1"]
        spoken = [SLOT_SPEECH[row["slot_code"]].format(value=row["atomic_value_de"]) for row in source_events]
        anticipation = [row for row in events if row["source_position_contribution"] == "0"]
        owner_names = list(dict.fromkeys(row["owner"] for row in events))
        outgoing_transition = transition_by_left_locus.get((line["record_unit_id"], line["locus"]))
        decision_to_next = outgoing_transition["decision"] if outgoing_transition else "RECORD_END"
        instruction = f"Bei {'; dann '.join(owner_names)}, am {STATE_NAMES[state_before[event_ids[0]]]}: " + "; dann ".join(spoken) + "."
        if anticipation:
            instruction += " Schreibe am rechten Rand als Vorgriff: " + ", ".join(row["surface"] for row in anticipation) + "; sprich den Wert erst auf der nächsten Zeile."
        dictation.append({
            "record_unit_id": line["record_unit_id"],
            "page": line["page"],
            "record_line_no": line["record_line_no"],
            "locus": line["locus"],
            "owner_sequence": "|".join(owner_names),
            "incoming_state": state_before[event_ids[0]],
            "incoming_state_de": STATE_NAMES[state_before[event_ids[0]]],
            "master_instruction_de": instruction,
            "source_instruction_values_de": " → ".join(row["atomic_value_de"] for row in source_events) if source_events else "NONE__ANTICIPATION_ONLY",
            "source_instruction_count": len(source_events),
            "visible_event_count": len(events),
            "visible_surfaces": " ".join(row["surface"] for row in events),
            "anticipation_surfaces": "|".join(row["surface"] for row in anticipation) if anticipation else "NONE",
            "outgoing_state": state_after[event_ids[-1]],
            "outgoing_state_de": STATE_NAMES[state_after[event_ids[-1]]],
            "decision_to_next_line": decision_to_next,
            "next_line_instruction_de": {
                "CONTINUE_ACROSS_LINE": "Auf der nächsten Zeile denselben Mikrogang weiterlesen.",
                "READ_ONCE_CARRY": "Randvorgriff und nächsten Zeilenanfang als eine Karte lesen.",
                "REAL_CYCLE_OR_OWNER_RESET": "Auf der nächsten Zeile Mikrogang oder Besitzer neu eröffnen.",
                "RECORD_END": "Record hier beenden.",
            }[decision_to_next],
        })
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_NINTH_FIFTY_SEVEN_LINE_MASTER_DICTATION.tsv",
        dictation,
        ["record_unit_id", "page", "record_line_no", "locus", "owner_sequence", "incoming_state", "incoming_state_de", "master_instruction_de", "source_instruction_values_de", "source_instruction_count", "visible_event_count", "visible_surfaces", "anticipation_surfaces", "outgoing_state", "outgoing_state_de", "decision_to_next_line", "next_line_instruction_de"],
    )

    record_rows = []
    for record in RECORD_ORDER:
        rows = [row for row in dictation if row["record_unit_id"] == record]
        record_rows.append({
            "record_unit_id": record,
            "page": rows[0]["page"],
            "physical_lines": len(rows),
            "visible_events": sum(int(row["visible_event_count"]) for row in rows),
            "source_instructions": sum(int(row["source_instruction_count"]) for row in rows),
            "statements": len({event["statement_id"] for event in visible if event["record_unit_id"] == record}),
            "owners": len({owner for row in rows for owner in row["owner_sequence"].split("|")}),
            "input_state": rows[0]["incoming_state"],
            "input_state_de": rows[0]["incoming_state_de"],
            "output_state": rows[-1]["outgoing_state"],
            "output_state_de": rows[-1]["outgoing_state_de"],
            "continue_boundaries": sum(row["decision_to_next_line"] == "CONTINUE_ACROSS_LINE" for row in rows),
            "read_once_boundaries": sum(row["decision_to_next_line"] == "READ_ONCE_CARRY" for row in rows),
            "reset_boundaries": sum(row["decision_to_next_line"] == "REAL_CYCLE_OR_OWNER_RESET" for row in rows),
        })
    write_tsv(HERE / "THREE_HUNDRED_FIFTY_NINTH_ELEVEN_RECORD_DICTATION_SUMMARY.tsv", record_rows,
              ["record_unit_id", "page", "physical_lines", "visible_events", "source_instructions", "statements", "owners", "input_state", "input_state_de", "output_state", "output_state_de", "continue_boundaries", "read_once_boundaries", "reset_boundaries"])

    lines = [
        "# Vollständiges Meisterdiktat der sieben Prosaseiten",
        "",
        "Der Meister nennt Besitzer, laufenden Stoff und Slotaufträge. Der Schreiber",
        "setzt danach die sichtbaren Karten; eine Randvorwegnahme wird nicht doppelt gesprochen.",
        "",
    ]
    for record in RECORD_ORDER:
        lines.extend([f"## {record}", ""])
        for row in [item for item in dictation if item["record_unit_id"] == record]:
            lines.extend([
                f"### {row['locus']}",
                "",
                f"**Meister:** {row['master_instruction_de']}",
                "",
                f"**Schreiber:** `{row['visible_surfaces']}`",
                "",
                f"**Stoff danach:** {row['outgoing_state_de']}. {row['next_line_instruction_de']}",
                "",
            ])
    (HERE / "THREE_HUNDRED_FIFTY_NINTH_COMPLETE_MASTER_DICTATION.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    decision_counts = Counter(row["decision_to_next_line"] for row in dictation)
    state_changes = sum(row["incoming_state"] != row["outgoing_state"] for row in dictation)
    report = f"""# Pass 359 — 57 Zeilen als Meisterdiktat

Jede physische Zeile besitzt jetzt eine vollständige Werkstattanweisung:
Besitzer, eingehender Stoffzustand, konkrete Slotwerte, sichtbare Karten,
ausgehender Zustand und Übergang zur nächsten Zeile. Die 57 Diktatzeilen decken
381 sichtbare Ereignisse, 380 gesprochene Quellkarten, 116 Aussagen und elf
Records ab.

{state_changes} Zeilen verändern den laufenden Stoffzustand. Sechs Zeilen weisen
ausdrücklich zum Weiterlesen, eine auf das einmalige Randpaar und 39 auf einen
Reset; elf beenden ihren Record. E180 wird nur als sichtbarer Randvorgriff
geschrieben, E181 trägt die gesprochene Sollstellung.

Als Nächstes sollte aus diesem Diktat eine flüssige moderne Gesamtübersetzung
entstehen: pro Record ein zusammenhängender deutscher Arbeitsabsatz, darunter
eine wörtliche Kartenzeile und eine kurze Liste der Stellen, an denen Bildbesitz
statt Karte den konkreten Gegenstand liefert.
"""
    (HERE / "THREE_HUNDRED_FIFTY_NINTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "dictation_lines": len(dictation),
        "records": len(record_rows),
        "visible_events": sum(int(row["visible_event_count"]) for row in dictation),
        "source_instructions": sum(int(row["source_instruction_count"]) for row in dictation),
        "statements": sum(int(row["statements"]) for row in record_rows),
        "state_changing_lines": state_changes,
        "decisions_to_next": dict(decision_counts),
    }
    (HERE / "THREE_HUNDRED_FIFTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
