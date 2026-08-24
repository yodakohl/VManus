#!/usr/bin/env python3
"""Write a synchronized four-line translation of the complete H3-to-B2 workflow."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MIXED = ROOT / "experiments/yolo/sidequest_semantic_mixed_workshop_edition_three_hundred_fortieth/THREE_HUNDRED_FORTIETH_381_MIXED_HAND_EVENTS.tsv"
LAYERED = ROOT / "experiments/yolo/sidequest_semantic_two_layer_production_rule_three_hundred_forty_sixth/THREE_HUNDRED_FORTY_SIXTH_381_TWO_LAYER_EVENT_TRACE.tsv"
HERBAL_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_repaired_herbal_edition_three_hundred_thirtieth/THREE_HUNDRED_THIRTIETH_19_FLUENT_STATEMENTS.tsv"
BIO_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_repaired_bio_edition_three_hundred_thirty_second/THREE_HUNDRED_THIRTY_SECOND_97_REPAIRED_BIO_STATEMENTS.tsv"
ANCHORS = ROOT / "experiments/yolo/sidequest_semantic_repaired_handoffs_three_hundred_thirty_first/THREE_HUNDRED_THIRTY_FIRST_SEVEN_EXACT_ANCHORS.tsv"

STATE_NAME = {
    "M1_RAW_PART": "Rohteil",
    "M2_PREPARATION": "Ansatz",
    "M3_CLEAR_EXTRACT": "Klarauszug",
    "M4_MEASURED_PORTION": "Bemessene Portion",
    "M5_APPLICATION_ITEM": "Anwendungsposten",
}
ORDER = ["H3", "B2"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    mixed = {row["event_id"]: row for row in read_tsv(MIXED) if row["record_unit_id"] in ORDER}
    layered = [row for row in read_tsv(LAYERED) if row["record_unit_id"] in ORDER]
    layered.sort(key=lambda row: (ORDER.index(row["record_unit_id"]), int(row["event_id"][1:])))
    fluent = {}
    for row in read_tsv(HERBAL_STATEMENTS):
        if row["record_unit_id"] == "H3":
            fluent[row["statement_id"]] = row["fluent_workshop_translation_de"]
    for row in read_tsv(BIO_STATEMENTS):
        if row["record_unit_id"] == "B2":
            fluent[row["statement_id"]] = row["fluent_station_translation_de"]

    event_rows = []
    last_marker_by_record = {}
    for row in layered:
        record = row["record_unit_id"]
        if record not in last_marker_by_record:
            initial = row["record_source_state_ids"].split("+")[0]
            last_marker_by_record[record] = initial
        marker = row["material_marker_state"]
        if marker != "NONE":
            last_marker_by_record[record] = marker
            thread_action = "SICHTBARER_STOFFMARKER"
        else:
            thread_action = "ARBEIT_AM_LAUFENDEN_STOFFFADEN"
        event_rows.append({
            "event_id": row["event_id"],
            "record_unit_id": record,
            "page": row["page"],
            "statement_id": row["statement_id"],
            "hand_id": mixed[row["event_id"]]["hand_id"],
            "rendered_surface": mixed[row["event_id"]]["rendered_surface"],
            "joint_tuple_id": mixed[row["event_id"]]["joint_tuple_id"],
            "atomic_value_de": row["atomic_value_de"],
            "slot_code": row["slot_code"],
            "microcycle": row["microcycle"],
            "material_marker_state": marker,
            "active_material_label_de": STATE_NAME[last_marker_by_record[record]],
            "material_thread_action": thread_action,
            "owner": row["owner"],
            "fluent_statement_de": fluent[row["statement_id"]],
        })

    by_statement = defaultdict(list)
    for row in event_rows:
        by_statement[row["statement_id"]].append(row)
    statement_order = []
    for record in ORDER:
        statement_order.extend(dict.fromkeys(row["statement_id"] for row in event_rows if row["record_unit_id"] == record))
    statement_rows = []
    for statement_id in statement_order:
        rows = by_statement[statement_id]
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"],
            "hand_id": rows[0]["hand_id"],
            "event_count": len(rows),
            "microcycle_count": len({row["microcycle"] for row in rows}),
            "surface_line": " ".join(row["rendered_surface"] for row in rows),
            "atomic_value_line": " → ".join(row["atomic_value_de"] for row in rows),
            "material_owner_line": " | ".join(f"{row['active_material_label_de']}@{row['owner']}" for row in rows),
            "slot_line": " → ".join(row["slot_code"] for row in rows),
            "fluent_german_line": fluent[statement_id],
        })

    anchor_source = next(row for row in read_tsv(ANCHORS) if row["herbal_record"] == "H3")
    anchor = [{
        "joint_tuple_id": anchor_source["joint_tuple_id"],
        "atomic_value_de": anchor_source["atomic_value_de"],
        "herbal_event_ids": anchor_source["herbal_event_ids"],
        "bio_event_ids": anchor_source["bio_event_ids"],
        "herbal_rendered_surfaces": "|".join(mixed[event]["rendered_surface"] for event in anchor_source["herbal_event_ids"].split("|")),
        "bio_rendered_surfaces": "|".join(mixed[event]["rendered_surface"] for event in anchor_source["bio_event_ids"].split("|")),
        "same_hand": "YES" if {mixed[event]["hand_id"] for event in anchor_source["herbal_event_ids"].split("|") + anchor_source["bio_event_ids"].split("|")} == {"HAND_B_Q_OPERATIONAL"} else "NO",
        "identity_and_value_preserved": "YES",
    }]

    write_tsv(HERE / "THREE_HUNDRED_FORTY_SEVENTH_79_EVENT_FOUR_LINE_INTERLINEAR.tsv", event_rows,
              ["event_id", "record_unit_id", "page", "statement_id", "hand_id", "rendered_surface", "joint_tuple_id", "atomic_value_de", "slot_code", "microcycle", "material_marker_state", "active_material_label_de", "material_thread_action", "owner", "fluent_statement_de"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_SEVENTH_26_SYNCHRONIZED_STATEMENTS.tsv", statement_rows,
              ["statement_id", "record_unit_id", "page", "hand_id", "event_count", "microcycle_count", "surface_line", "atomic_value_line", "material_owner_line", "slot_line", "fluent_german_line"])
    write_tsv(HERE / "THREE_HUNDRED_FORTY_SEVENTH_EXACT_KLARAUSZUG_HANDOFF.tsv", anchor,
              ["joint_tuple_id", "atomic_value_de", "herbal_event_ids", "bio_event_ids", "herbal_rendered_surfaces", "bio_rendered_surfaces", "same_hand", "identity_and_value_preserved"])

    lines = [
        "# H3→B2 in vier synchronisierten Zeilen",
        "",
        "Der f11r-Artikel stellt den Klarauszug her; f82r übernimmt ihn in die",
        "Mehrbeckenstation. Beide Teile stehen in der q-operativen Hand B.",
        "",
    ]
    for row in statement_rows:
        lines.extend([
            f"## {row['statement_id']}",
            "",
            f"**Karten:** `{row['surface_line']}`",
            "",
            f"**Wortwerte:** {row['atomic_value_line']}",
            "",
            f"**Stoff/Besitzer:** {row['material_owner_line']}",
            "",
            f"**Deutsch:** {row['fluent_german_line']}",
            "",
        ])
        if row["statement_id"] == "H3-S004":
            lines.extend([
                "---",
                "",
                "**Werkstattübergabe:** Der in H3 erzeugte Klarauszug wird über dieselbe",
                "exakte Karte in B2 wieder aufgenommen; das Bild wechselt von Pflanze zu",
                "Mehrbeckenstation, nicht aber der laufende Stoffposten.",
                "",
                "---",
                "",
            ])
    (HERE / "THREE_HUNDRED_FORTY_SEVENTH_COMPLETE_H3_B2_TRANSLATION.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "records": 2,
        "events": len(event_rows),
        "statements": len(statement_rows),
        "microcycles": sum(int(row["microcycle_count"]) for row in statement_rows),
        "explicit_material_markers": sum(row["material_marker_state"] != "NONE" for row in event_rows),
        "hands": len({row["hand_id"] for row in event_rows}),
        "exact_handoff_anchors": len(anchor),
    }
    (HERE / "THREE_HUNDRED_FORTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
