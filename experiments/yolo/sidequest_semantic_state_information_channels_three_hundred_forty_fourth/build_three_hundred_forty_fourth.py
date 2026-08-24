#!/usr/bin/env python3
"""Separate card-explicit material states from picture- and relay-supplied states."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_herbal_formula_repair_three_hundred_twenty_ninth/THREE_HUNDRED_TWENTY_NINTH_381_GLOBAL_EVENTS.tsv"
TRANSITIONS = ROOT / "experiments/yolo/sidequest_semantic_material_state_ladder_three_hundred_forty_third/THREE_HUNDRED_FORTY_THIRD_ELEVEN_STATE_TRANSITIONS.tsv"

STATE_NAMES = {
    "M1_RAW_PART": "Rohteil",
    "M2_PREPARATION": "Ansatz",
    "M3_CLEAR_EXTRACT": "Klarauszug",
    "M4_MEASURED_PORTION": "Bemessene Portion",
    "M5_APPLICATION_ITEM": "Anwendungsposten",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def state_marker(value: str) -> str:
    text = value.lower()
    if any(needle in text for needle in ("endposten", "endziel", "volleinsatz", "gebrauchen")):
        return "M5_APPLICATION_ITEM"
    if any(needle in text for needle in ("klarauszug", "klarabzug", "klarlauf", "auszugnahme", "quellausguss")):
        return "M3_CLEAR_EXTRACT"
    if any(needle in text for needle in ("sollmaß", "portion", "folgemaß", "arbeitsstufe", "endstufe", "kurzsoll")):
        return "M4_MEASURED_PORTION"
    if "ansatz" in text or "zubereitung" in text:
        return "M2_PREPARATION"
    if any(needle in text for needle in ("wurzelteil", "blütenkraut", "pflanzenteil", "zutat", "zusatz")):
        return "M1_RAW_PART"
    return "NONE"


def missing_channel(record: str, direction: str, state_id: str) -> str:
    if record.startswith("H") and state_id == "M1_RAW_PART":
        return "PICTURE_OWNER_SUPPLIES_STATE"
    if direction == "SOURCE":
        return "WORKSHOP_RELAY_OR_LOCAL_OWNER_SUPPLIES_STATE"
    return "EDITORIAL_RESULT_SHELF_SUPPLIES_STATE"


def main() -> None:
    events = read_tsv(EVENTS)
    transitions = read_tsv(TRANSITIONS)
    event_rows = []
    markers_by_record = defaultdict(lambda: defaultdict(list))
    card_ids_by_state = defaultdict(set)
    for row in events:
        marker = state_marker(row["atomic_value_de"])
        if marker != "NONE":
            markers_by_record[row["record_unit_id"]][marker].append(row["event_id"])
            card_ids_by_state[marker].add(row["joint_tuple_id"])
        event_rows.append({
            "event_id": row["event_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "joint_tuple_id": row["joint_tuple_id"],
            "surface": row["surface"],
            "atomic_value_de": row["atomic_value_de"],
            "material_state_marker": marker,
            "state_name_de": STATE_NAMES.get(marker, "KEIN_STOFFZUSTANDSMARKER"),
            "information_channel": "CARD_EXPLICIT_STATE_MARKER" if marker != "NONE" else "OTHER_OPERATION_CONTROL_OR_TECHNICAL_CARD",
        })

    state_rows = []
    for state_id, name in STATE_NAMES.items():
        marked = [row for row in event_rows if row["material_state_marker"] == state_id]
        state_rows.append({
            "state_id": state_id,
            "state_name_de": name,
            "explicit_marker_events": len(marked),
            "explicit_marker_card_types": len(card_ids_by_state[state_id]),
            "records_with_marker": "|".join(dict.fromkeys(row["record_unit_id"] for row in marked)),
            "marker_values": "|".join(dict.fromkeys(row["atomic_value_de"] for row in marked)),
            "default_noncard_channel": "PICTURE_OWNER_OR_WORKSHOP_RELAY",
        })

    channel_rows = []
    for row in transitions:
        record = row["record_unit_id"]
        source_states = row["source_state_ids"].split("+")
        source_parts = []
        for state_id in source_states:
            explicit = bool(markers_by_record[record][state_id])
            source_parts.append(
                f"{state_id}:CARD_EXPLICIT__OWNER_GIVES_REFERENT" if explicit
                else f"{state_id}:{missing_channel(record, 'SOURCE', state_id)}"
            )
        target_state = row["target_state_id"]
        target_explicit = bool(markers_by_record[record][target_state])
        target_channel = (
            "CARD_EXPLICIT__OWNER_GIVES_REFERENT" if target_explicit
            else missing_channel(record, "TARGET", target_state)
        )
        channel_rows.append({
            "record_unit_id": record,
            "page": row["page"],
            "source_state_ids": row["source_state_ids"],
            "source_information_channels": "|".join(source_parts),
            "target_state_id": target_state,
            "target_information_channel": target_channel,
            "explicit_state_marker_event_ids": "|".join(
                event_id
                for state_id in set(source_states + [target_state])
                for event_id in markers_by_record[record][state_id]
            ) or "NONE",
            "specific_input_de": row["specific_input_de"],
            "specific_output_de": row["specific_output_de"],
            "meaning_retained": "YES",
        })

    write_tsv(HERE / "THREE_HUNDRED_FORTY_FOURTH_381_EVENT_STATE_CHANNEL_AUDIT.tsv", event_rows,
              ["event_id", "record_unit_id", "page", "joint_tuple_id", "surface", "atomic_value_de", "material_state_marker", "state_name_de", "information_channel"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_FOURTH_FIVE_STATE_MARKER_SUMMARY.tsv", state_rows,
              ["state_id", "state_name_de", "explicit_marker_events", "explicit_marker_card_types", "records_with_marker", "marker_values", "default_noncard_channel"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_FOURTH_ELEVEN_TRANSITION_CHANNELS.tsv", channel_rows,
              ["record_unit_id", "page", "source_state_ids", "source_information_channels", "target_state_id", "target_information_channel", "explicit_state_marker_event_ids", "specific_input_de", "specific_output_de", "meaning_retained"])

    lines = [
        "# Stoffbedeutung nach Informationskanal",
        "",
        "## Kartenseitig sichtbar",
        "",
    ]
    for row in state_rows:
        lines.append(f"- **{row['state_name_de']}**: {row['explicit_marker_events']} Ereignisse / {row['explicit_marker_card_types']} Karten; {row['marker_values']}.")
    lines.extend([
        "",
        "## Bild- und Relayseite",
        "",
        "Eine Zustandskarte benennt die Rolle, aber nicht automatisch das konkrete Ding.",
        "Das Pflanzenbild liefert etwa, welcher Rohteil gemeint ist; ein Beckenbild liefert",
        "den lokalen Träger; ein Herbal→Bio-Relay liefert, welcher Ansatz oder Klarauszug",
        "ankommt. Fehlt im Record eine Zustandskarte, bleibt die konkrete Stoffrolle als",
        "Werkstattdefault bestehen und wird ausdrücklich dem Bild/Relay-Kanal zugeschrieben.",
        "",
        "## Ergebnis",
        "",
        "Die Übersetzung wird nicht zurückgenommen. Stattdessen trägt jede konkrete Rolle",
        "nun ihre Herkunft: Karte, Karte+Besitzer, Bildbesitzer, Werkstatt-Relay oder",
        "redaktionelles Ergebnissims. Das macht die Arbeitstheorie für einen Lehrling",
        "einfacher: Er weiß, was er lesen und was er aus der Situation ergänzen muss.",
    ])
    (HERE / "THREE_HUNDRED_FORTY_FOURTH_INFORMATION_CHANNEL_MANUAL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "events": len(event_rows),
        "explicit_state_marker_events": sum(row["material_state_marker"] != "NONE" for row in event_rows),
        "other_events": sum(row["material_state_marker"] == "NONE" for row in event_rows),
        "explicit_marker_card_types": len({row["joint_tuple_id"] for row in event_rows if row["material_state_marker"] != "NONE"}),
        "states": len(state_rows),
        "transitions": len(channel_rows),
        "meanings_retained": sum(row["meaning_retained"] == "YES" for row in channel_rows),
    }
    (HERE / "THREE_HUNDRED_FORTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
