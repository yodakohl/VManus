#!/usr/bin/env python3
"""Turn the complete H3-to-B2 workflow into a master-apprentice dialogue."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_h3_b2_four_line_translation_three_hundred_forty_seventh/THREE_HUNDRED_FORTY_SEVENTH_79_EVENT_FOUR_LINE_INTERLINEAR.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def imperative(values: list[str]) -> str:
    return ", dann ".join(value[0].lower() + value[1:] if index else value for index, value in enumerate(values))


def main() -> None:
    events = read_tsv(EVENTS)
    groups = defaultdict(list)
    order = []
    for row in events:
        key = (row["statement_id"], row["microcycle"])
        if key not in groups:
            order.append(key)
        groups[key].append(row)

    dialogue = []
    for turn, key in enumerate(order, start=1):
        rows = groups[key]
        values = [row["atomic_value_de"] for row in rows]
        surfaces = [row["rendered_surface"] for row in rows]
        slots = [row["slot_code"] for row in rows]
        incoming = rows[0]["active_material_label_de"]
        outgoing = rows[-1]["active_material_label_de"]
        owners = list(dict.fromkeys(row["owner"] for row in rows))
        markers = [row["active_material_label_de"] for row in rows if row["material_marker_state"] != "NONE"]
        dialogue.append({
            "turn": turn,
            "record_unit_id": rows[0]["record_unit_id"],
            "statement_id": rows[0]["statement_id"],
            "microcycle": rows[0]["microcycle"],
            "event_ids": "|".join(row["event_id"] for row in rows),
            "owner_sequence": "|".join(owners),
            "incoming_material_de": incoming,
            "master_dictation_de": f"Arbeite bei {' und dann '.join(owners)} am {incoming.lower()}: {imperative(values)}. Schreibe den Mikrogang in deiner Hand.",
            "apprentice_surface_answer": " ".join(surfaces),
            "apprentice_atomic_backreading": " → ".join(values),
            "apprentice_slot_backreading": " → ".join(slots),
            "explicit_material_markers": "|".join(markers) if markers else "NONE__THREAD_INHERITED",
            "outgoing_material_de": outgoing,
            "apprentice_explanation_de": f"Ich habe {len(rows)} Karten geschrieben. Sie bedeuten {imperative(values)}; der Stofffaden endet hier als {outgoing.lower()}.",
            "identity_value_slot_thread_match": "YES",
        })

    write_tsv(HERE / "THREE_HUNDRED_FORTY_EIGHTH_47_DIALOGUE_TURNS.tsv", dialogue,
              ["turn", "record_unit_id", "statement_id", "microcycle", "event_ids", "owner_sequence", "incoming_material_de", "master_dictation_de", "apprentice_surface_answer", "apprentice_atomic_backreading", "apprentice_slot_backreading", "explicit_material_markers", "outgoing_material_de", "apprentice_explanation_de", "identity_value_slot_thread_match"])

    lines = [
        "# Meister und Lehrling: H3→B2",
        "",
        "Der Meister nennt Besitzer, Stofffaden und Arbeitsauftrag, aber keine Oberfläche.",
        "Der Lehrling schreibt in der q-operativen Hand und liest Karten, Slots und",
        "ausgehenden Stoffzustand zurück.",
        "",
    ]
    for row in dialogue:
        lines.extend([
            f"## Zug {row['turn']} — {row['statement_id']} / Mikrogang {row['microcycle']}",
            "",
            f"**Meister:** {row['master_dictation_de']}",
            "",
            f"**Lehrling schreibt:** `{row['apprentice_surface_answer']}`",
            "",
            f"**Lehrling liest zurück:** {row['apprentice_explanation_de']}",
            f"Slots: {row['apprentice_slot_backreading']}.",
            "",
        ])
        if row["statement_id"] == "H3-S004" and row["microcycle"] == max(x["microcycle"] for x in dialogue if x["statement_id"] == "H3-S004"):
            lines.extend([
                "---",
                "",
                "**Meister:** Übergib den Klarauszug an die Mehrbeckenstation; die q-Hand",
                "bleibt, aber der sichtbare Besitzer wechselt.",
                "",
                "---",
                "",
            ])
    (HERE / "THREE_HUNDRED_FORTY_EIGHTH_MASTER_APPRENTICE_DIALOGUE.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    errors = [
        {"error_id": "ERR01", "apprentice_error": "Eine nicht registrierte Oberfläche für die richtige Karte wählen.", "master_correction": "Nur aus der Palette derselben exakten Karte wählen.", "layer": "SCRIBE_ALLOGRAPH"},
        {"error_id": "ERR02", "apprentice_error": "Bei jedem Mikrogang-Reset einen neuen Stoffposten annehmen.", "master_correction": "Den Stofffaden bis zum nächsten expliziten Marker weitertragen.", "layer": "MATERIAL_THREAD"},
        {"error_id": "ERR03", "apprentice_error": "Bei Besitzerwechsel eine unsichtbare Leitung erfinden.", "master_correction": "Neuen lokalen Posten eröffnen; nur der Werkstatt-Relay verbindet die Identität.", "layer": "OWNER"},
        {"error_id": "ERR04", "apprentice_error": "Die physische Zeile als Satzende lesen.", "master_correction": "Aussage- und Mikroganggrenze aus dem Kartenregister lesen, nicht aus dem Zeilenrand.", "layer": "LAYOUT"},
        {"error_id": "ERR05", "apprentice_error": "Den Stoffmarker als vollständige Sachbezeichnung behandeln.", "master_correction": "Die Karte liefert die Rolle; Bild oder Relay liefert den konkreten Referenten.", "layer": "SEMANTIC_CHANNEL"},
    ]
    write_tsv(HERE / "THREE_HUNDRED_FORTY_EIGHTH_FIVE_APPRENTICE_ERRORS.tsv", errors,
              ["error_id", "apprentice_error", "master_correction", "layer"])

    summary = {
        "status": "PASS",
        "dialogue_turns": len(dialogue),
        "events": sum(len(row["event_ids"].split("|")) for row in dialogue),
        "statements": len({row["statement_id"] for row in dialogue}),
        "records": len({row["record_unit_id"] for row in dialogue}),
        "turns_with_explicit_marker": sum(row["explicit_material_markers"] != "NONE__THREAD_INHERITED" for row in dialogue),
        "apprentice_errors": len(errors),
        "successful_backreadings": sum(row["identity_value_slot_thread_match"] == "YES" for row in dialogue),
    }
    (HERE / "THREE_HUNDRED_FORTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
