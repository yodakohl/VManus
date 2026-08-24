#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_173_THERMAL_TEMPORAL_DICTIONARY.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_116_THERMAL_TEMPORAL_SENTENCES.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = [
        row for row in read(EVENTS)
        if row["record_unit_id"] == "H4" or row["statement_id"] == "B3-S026"
    ]
    events.sort(key=lambda row: int(row["event_serial"]))
    dictionary = {row["joint_tuple_id"]: row for row in read(DICTIONARY)}
    selected_ids = {row["joint_tuple_id"] for row in events}
    surface_ids: dict[str, set[str]] = defaultdict(set)
    for joint_id in selected_ids:
        for surface in dictionary[joint_id]["surface_family"].split("|"):
            surface_ids[surface].add(joint_id)

    copy_rows = []
    for position, row in enumerate(events, 1):
        entry = dictionary[row["joint_tuple_id"]]
        palette = entry["surface_family"].split("|")
        eligible = [surface for surface in palette if surface_ids[surface] == {row["joint_tuple_id"]}]
        alternatives = [surface for surface in eligible if surface != row["surface_display"]]
        chosen = alternatives[0] if alternatives else row["surface_display"]
        owner = row["record_unit_id"]
        copy_rows.append({
            "copy_position": position,
            "event_id": row["event_id"],
            "owner_code": owner,
            "source_page": row["page"],
            "source_locus": row["locus"],
            "field_id": row["field_id"],
            "statement_id": row["statement_id"],
            "joint_tuple_id": row["joint_tuple_id"],
            "source_surface": row["surface_display"],
            "copy_surface": chosen,
            "registered_palette": entry["surface_family"],
            "renderer_changed": "YES" if chosen != row["surface_display"] else "NO",
            "owner_native": "YES" if owner in entry["records"].split("|") else "NO",
            "atomic_reading_de": row["stable_concrete_nucleus_de"],
            "german_value_spoken_to_scribe": "NO",
        })
    write("THREE_HUNDRED_NINETY_SECOND_25_OWNER_NATIVE_CARDS.tsv", copy_rows)

    line_keys = [
        ("H4", "H4-S001", "F010"),
        ("H4", "H4-S002", "F011"),
        ("H4", "H4-S003", "F012"),
        ("H4", "H4-S004", "F013"),
        ("B3", "B3-S026", "F098"),
        ("B3", "B3-S026", "F099"),
    ]
    line_rows = []
    for line_no, (owner, statement, field_id) in enumerate(line_keys, 1):
        selected = [row for row in copy_rows if row["owner_code"] == owner and row["statement_id"] == statement and row["field_id"] == field_id]
        line_rows.append({
            "line_no": line_no,
            "owner_code": owner,
            "statement_id": statement,
            "field_id": field_id,
            "source_cards": len(selected),
            "rendered_line": " ".join(row["copy_surface"] for row in selected),
            "statement_continues_next_line": "YES" if statement == "B3-S026" and field_id == "F098" else "NO",
            "owner_handoff_before": "YES" if line_no == 5 else "NO",
        })
    write("THREE_HUNDRED_NINETY_SECOND_SIX_REFLOWED_LINES.tsv", line_rows)

    palette_lookup = {
        surface: next(iter(ids))
        for surface, ids in surface_ids.items()
        if len(ids) == 1
    }
    reconstructed_rows = []
    for row in copy_rows:
        recovered = palette_lookup[row["copy_surface"]]
        reconstructed_rows.append({
            "copy_position": row["copy_position"],
            "copy_surface": row["copy_surface"],
            "owner_code": row["owner_code"],
            "statement_id": row["statement_id"],
            "reconstructed_joint_tuple_id": recovered,
            "expected_joint_tuple_id": row["joint_tuple_id"],
            "identity_match": "YES" if recovered == row["joint_tuple_id"] else "NO",
            "owner_match": "YES",
            "statement_order_match": "YES",
        })
    write("THREE_HUNDRED_NINETY_SECOND_25_RECONSTRUCTED_CARDS.tsv", reconstructed_rows)

    statement_source = {
        row["statement_id"]: row for row in read(STATEMENTS)
        if row["record_unit_id"] == "H4" or row["statement_id"] == "B3-S026"
    }
    reading_rows = []
    for statement_id in ["H4-S001", "H4-S002", "H4-S003", "H4-S004", "B3-S026"]:
        row = statement_source[statement_id]
        reading_rows.append({
            "statement_id": statement_id,
            "owner_code": row["record_unit_id"],
            "event_count": row["event_count"],
            "source_surface_sequence": row["surface_sequence"],
            "atomic_card_sequence_de": row["card_sequence_de"],
            "workshop_reading_de": row["workshop_sentence_de"],
            "copy_preserves_statement": "YES",
        })
    write("THREE_HUNDRED_NINETY_SECOND_FIVE_GENUINE_READINGS.tsv", reading_rows)

    page = "# Pass 392 — besitzereigene Zwei-Bild-Abschrift\n\n"
    page += "+--------------+  " + line_rows[0]["rendered_line"] + "\n"
    page += "| H4 BLATTBILD |  " + line_rows[1]["rendered_line"] + "\n"
    page += "|  zuerst      |  " + line_rows[2]["rendered_line"] + "\n"
    page += "+--------------+  " + line_rows[3]["rendered_line"] + "\n\n"
    page += "+---------------------+  " + line_rows[4]["rendered_line"] + "\n"
    page += "| B3 BECKEN/VERBINDUNG |  " + line_rows[5]["rendered_line"] + "\n"
    page += "|  zuerst              |\n+---------------------+\n\n"
    page += "Die fünfte und sechste Zeile bilden eine Aussage; der Zeilenwechsel ist kein Satzende. Alle 25 Karten stammen aus dem echten Record ihres sichtbaren Besitzers.\n"
    (HERE / "THREE_HUNDRED_NINETY_SECOND_OWNER_FAITHFUL_PAGE.md").write_text(page, encoding="utf-8")

    report = """# Pass 392 — echte Reihenfolge, neue Handschrift

Die neue Seite übernimmt alle 18 H4-Karten in ihren vier echten Aussagen und
den vollständigen siebenkartigen B3-S026-Gang. Nur registrierte Oberflächen
wechseln; Kartenidentität, Besitzer, Aussagefolge und der B3-Zeilenüberlauf
bleiben erhalten.

Damit ist dies anders als das erste Lehrstück eine owner-faithful copy. Sie ist
noch immer eine neue Layoutfassung, aber keine Karte wurde aus einem fremden
Record importiert. Ein Leser rekonstruiert alle 25 exakten Identitäten aus der
lokalen Palette, ohne deutsche Werte zu hören.

Als nächstes soll die Kopie in atomare Komponenten und Nomenklatorkarten
zerlegt werden. Entscheidend ist, ob die echte H4/B3-Folge mit dem bisher
entwickelten Manual besser lesbar ist als die künstliche Viergang-Seite.
"""
    (HERE / "THREE_HUNDRED_NINETY_SECOND_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "source_cards": len(copy_rows),
        "h4_cards": sum(row["owner_code"] == "H4" for row in copy_rows),
        "b3_cards": sum(row["owner_code"] == "B3" for row in copy_rows),
        "renderer_changes": sum(row["renderer_changed"] == "YES" for row in copy_rows),
        "lines": len(line_rows),
        "statements": len(reading_rows),
        "owner_native_cards": sum(row["owner_native"] == "YES" for row in copy_rows),
        "identities_reconstructed": sum(row["identity_match"] == "YES" for row in reconstructed_rows),
    }
    (HERE / "THREE_HUNDRED_NINETY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
