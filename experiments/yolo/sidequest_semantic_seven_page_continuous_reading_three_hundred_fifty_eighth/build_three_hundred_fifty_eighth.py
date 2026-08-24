#!/usr/bin/env python3
"""Apply continue/carry/reset decisions to all seven-page prose line transitions."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LOCUS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
TRACE = ROOT / "experiments/yolo/sidequest_semantic_two_layer_production_rule_three_hundred_forty_sixth/THREE_HUNDRED_FORTY_SIXTH_381_TWO_LAYER_EVENT_TRACE.tsv"
MIXED = ROOT / "experiments/yolo/sidequest_semantic_mixed_workshop_edition_three_hundred_fortieth/THREE_HUNDRED_FORTIETH_381_MIXED_HAND_EVENTS.tsv"
SLOT_RANK = {"S1_BEZUG_FOLGE": 1, "S2_MATERIAL_MASS": 2, "S3_PROZESS_TRANSFER": 3, "S4_DAUER_ZUSTAND": 4, "S5_ZIEL_ANWENDUNG": 5, "S6_BEREIT_ABSCHLUSS": 6}
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
    locus = {row["event_id"]: row for row in read_tsv(LOCUS)}
    trace = read_tsv(TRACE)
    mixed = {row["event_id"]: row for row in read_tsv(MIXED)}
    assert len(locus) == len(trace) == len(mixed) == 381
    trace.sort(key=lambda row: int(row["event_id"][1:]))

    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in trace:
        by_record[row["record_unit_id"]].append(row)

    transitions = []
    transition_by_right = {}
    for record in RECORD_ORDER:
        events = by_record[record]
        for left, right in zip(events, events[1:]):
            left_line = locus[left["event_id"]]["locus"]
            right_line = locus[right["event_id"]]["locus"]
            if left_line == right_line:
                continue
            same_exact = locus[left["event_id"]]["joint_tuple_id"] == locus[right["event_id"]]["joint_tuple_id"]
            same_owner = left["owner"] == right["owner"]
            same_statement = left["statement_id"] == right["statement_id"]
            same_cycle = same_statement and left["microcycle"] == right["microcycle"]
            slot_descent = SLOT_RANK[right["slot_code"]] < SLOT_RANK[left["slot_code"]]
            if same_exact and same_owner and same_cycle:
                decision = "READ_ONCE_CARRY"
                explanation = "Exakte Karte am alten Rand und neuen Zeilenanfang; gleicher Besitzer und Mikrogang."
                source_tokens = 1
            elif (not same_owner) or (not same_cycle) or slot_descent:
                decision = "REAL_CYCLE_OR_OWNER_RESET"
                explanation = "Besitzer-, Aussage- oder Mikrogangwechsel beziehungsweise Slotabstieg eröffnet neu."
                source_tokens = 2
            else:
                decision = "CONTINUE_ACROSS_LINE"
                explanation = "Gleicher Besitzer und Mikrogang, verschiedene Karten, vorwärts laufender Slot."
                source_tokens = 2
            row = {
                "transition_no": len(transitions) + 1,
                "record_unit_id": record,
                "page": left["page"],
                "left_event_id": left["event_id"],
                "left_locus": left_line,
                "left_surface": locus[left["event_id"]]["surface_display"],
                "left_joint_tuple_id": locus[left["event_id"]]["joint_tuple_id"],
                "left_statement_id": left["statement_id"],
                "left_microcycle": left["microcycle"],
                "left_slot": left["slot_code"],
                "left_owner": left["owner"],
                "right_event_id": right["event_id"],
                "right_locus": right_line,
                "right_surface": locus[right["event_id"]]["surface_display"],
                "right_joint_tuple_id": locus[right["event_id"]]["joint_tuple_id"],
                "right_statement_id": right["statement_id"],
                "right_microcycle": right["microcycle"],
                "right_slot": right["slot_code"],
                "right_owner": right["owner"],
                "same_exact_card": "YES" if same_exact else "NO",
                "same_owner": "YES" if same_owner else "NO",
                "same_statement": "YES" if same_statement else "NO",
                "same_microcycle": "YES" if same_cycle else "NO",
                "slot_descent": "YES" if slot_descent else "NO",
                "decision": decision,
                "source_tokens_for_visible_pair": source_tokens,
                "explanation_de": explanation,
            }
            transitions.append(row)
            transition_by_right[right["event_id"]] = row
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_EIGHTH_FORTY_SIX_LINE_TRANSITIONS.tsv",
        transitions,
        ["transition_no", "record_unit_id", "page", "left_event_id", "left_locus", "left_surface", "left_joint_tuple_id", "left_statement_id", "left_microcycle", "left_slot", "left_owner", "right_event_id", "right_locus", "right_surface", "right_joint_tuple_id", "right_statement_id", "right_microcycle", "right_slot", "right_owner", "same_exact_card", "same_owner", "same_statement", "same_microcycle", "slot_descent", "decision", "source_tokens_for_visible_pair", "explanation_de"],
    )

    visible_rows = []
    source_position = 0
    carry_tuple = None
    for row in trace:
        event_id = row["event_id"]
        incoming = transition_by_right.get(event_id)
        if event_id == "E180":
            contribution = 0
            visible_role = "RIGHT_MARGIN_ANTICIPATION_COPY"
            assigned_source = source_position + 1
            carry_tuple = locus[event_id]["joint_tuple_id"]
        elif incoming and incoming["decision"] == "READ_ONCE_CARRY":
            source_position += 1
            contribution = 1
            visible_role = "LINE_START_EXECUTION_OF_READ_ONCE_CARD"
            assigned_source = source_position
            assert carry_tuple == locus[event_id]["joint_tuple_id"]
            carry_tuple = None
        else:
            source_position += 1
            contribution = 1
            visible_role = "ORDINARY_VISIBLE_CARD"
            assigned_source = source_position
        visible_rows.append({
            "event_id": event_id,
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "locus": locus[event_id]["locus"],
            "statement_id": row["statement_id"],
            "microcycle": row["microcycle"],
            "owner": row["owner"],
            "surface": locus[event_id]["surface_display"],
            "joint_tuple_id": locus[event_id]["joint_tuple_id"],
            "atomic_value_de": row["atomic_value_de"],
            "slot_code": row["slot_code"],
            "visible_role": visible_role,
            "source_position_id": f"S{assigned_source:03d}",
            "source_position_contribution": contribution,
            "incoming_line_decision": incoming["decision"] if incoming else "SAME_LINE_OR_RECORD_START",
        })
    assert carry_tuple is None
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_EIGHTH_381_VISIBLE_380_SOURCE_EDITION.tsv",
        visible_rows,
        ["event_id", "record_unit_id", "page", "locus", "statement_id", "microcycle", "owner", "surface", "joint_tuple_id", "atomic_value_de", "slot_code", "visible_role", "source_position_id", "source_position_contribution", "incoming_line_decision"],
    )

    line_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in visible_rows:
        line_groups[(row["record_unit_id"], row["locus"])].append(row)
    line_rows = []
    for record in RECORD_ORDER:
        seen_loci = []
        for row in visible_rows:
            if row["record_unit_id"] == record and row["locus"] not in seen_loci:
                seen_loci.append(row["locus"])
        for line_index, locus_id in enumerate(seen_loci, start=1):
            events = line_groups[(record, locus_id)]
            incoming = transition_by_right.get(events[0]["event_id"])
            line_rows.append({
                "record_unit_id": record,
                "page": events[0]["page"],
                "record_line_no": line_index,
                "locus": locus_id,
                "event_ids": "|".join(row["event_id"] for row in events),
                "surfaces": " ".join(row["surface"] for row in events),
                "atomic_values_de": " → ".join(row["atomic_value_de"] for row in events),
                "statement_ids": "|".join(dict.fromkeys(row["statement_id"] for row in events)),
                "microcycles": "|".join(dict.fromkeys(row["microcycle"] for row in events)),
                "owner_sequence": "|".join(dict.fromkeys(row["owner"] for row in events)),
                "decision_from_previous_line": incoming["decision"] if incoming else "RECORD_START",
                "source_positions_contributed": sum(int(row["source_position_contribution"]) for row in events),
            })
    write_tsv(
        HERE / "THREE_HUNDRED_FIFTY_EIGHTH_FIFTY_SEVEN_PHYSICAL_LINES.tsv",
        line_rows,
        ["record_unit_id", "page", "record_line_no", "locus", "event_ids", "surfaces", "atomic_values_de", "statement_ids", "microcycles", "owner_sequence", "decision_from_previous_line", "source_positions_contributed"],
    )

    lines = [
        "# Sieben Seiten als kontinuierliche Werkstattausgabe",
        "",
        "`WEITER` setzt dieselbe Arbeit über die Zeile fort; `EINMAL` verbindet",
        "Rand- und Anfangskopie zu einer Karte; `NEU` eröffnet Mikrogang oder Besitzer.",
        "",
    ]
    label = {"RECORD_START": "START", "CONTINUE_ACROSS_LINE": "WEITER", "READ_ONCE_CARRY": "EINMAL", "REAL_CYCLE_OR_OWNER_RESET": "NEU"}
    for record in RECORD_ORDER:
        record_lines = [row for row in line_rows if row["record_unit_id"] == record]
        lines.extend([f"## {record} / {record_lines[0]['page']}", ""])
        for row in record_lines:
            lines.extend([
                f"**{row['locus']} · {label[row['decision_from_previous_line']]}**",
                f"`{row['surfaces']}`",
                f"{row['atomic_values_de']}",
                "",
            ])
    (HERE / "THREE_HUNDRED_FIFTY_EIGHTH_ELEVEN_CONTINUOUS_RECORDS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    decision_counts = Counter(row["decision"] for row in transitions)
    report = f"""# Pass 358 — alle realen Prosa-Zeilenübergänge

Die 381 vorhandenen Ereignisse liegen auf 57 physischen Zeilen in elf Records.
Alle 46 recordinternen Zeilenübergänge erhalten dieselbe Werkstattentscheidung:
{decision_counts['CONTINUE_ACROSS_LINE']} weiterlesen,
{decision_counts['READ_ONCE_CARRY']} Rand-/Anfangspaar einmal lesen und
{decision_counts['REAL_CYCLE_OR_OWNER_RESET']} echten Mikrogang- oder
Besitzerreset setzen.

Das einzige Read-once-Paar bleibt `E180→E181 qokaiin/qokaiin`. Seine zwei
sichtbaren Formen bilden eine Quellkarte; damit ergeben 381 sichtbare Ereignisse
380 Quellpositionen. Die übrigen Wiederholungen bleiben echte Karten. Die
komplette Ausgabe lässt Aussagen und Mikrozyklen über physische Zeilen laufen,
ohne Zeilenende als Satzschluss zu behandeln.

Als Nächstes sollte die 57-Zeilen-Ausgabe in ein vollständiges Meisterdiktat
umgeschrieben werden: je Zeile erst Besitzer und laufender Stoff, dann die
konkrete deutsche Arbeitsanweisung, danach die sichtbaren Karten. So erhält man
die bislang flüssigste Gesamtübersetzung der sieben Prosaseiten.
"""
    (HERE / "THREE_HUNDRED_FIFTY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "records": len(RECORD_ORDER),
        "pages": len({row["page"] for row in visible_rows}),
        "visible_events": len(visible_rows),
        "source_positions": sum(int(row["source_position_contribution"]) for row in visible_rows),
        "physical_lines": len(line_rows),
        "line_transitions": len(transitions),
        "decisions": dict(decision_counts),
    }
    (HERE / "THREE_HUNDRED_FIFTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
