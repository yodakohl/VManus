#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_six_slot_pressure_test_hundred_eighty_first/HUNDRED_EIGHTY_FIRST_381_EVENT_SIX_SLOT_PARSE.tsv"
MASTER = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_381_PROSE_MASTER_EDITION.tsv"
NORMALIZATION = ROOT / "experiments/yolo/sidequest_semantic_reader_normalization_hundred_ninety_sixth/HUNDRED_NINETY_SIXTH_230_SURFACE_NORMALIZATION.tsv"
MODES = ROOT / "experiments/yolo/sidequest_semantic_field_frame_modes_hundred_ninety_third/HUNDRED_NINETY_THIRD_135_FIELD_FRAME_MODES.tsv"


TRANSLATIONS = {
    "H3-S001": "Das Kochgut in einem Sud ansetzen, ausdrücken, eine Stehzeit abwarten, nachseihen, den klaren Auszug abnehmen und die Endzugabe einsetzen; Schluss.",
    "H3-S002": "Den weiteren Zugabeteil bereitlegen.",
    "H3-S003": "Vom vorigen Ansatz diesen Posten weiterbearbeiten und auf Sollmaß bringen.",
    "H3-S004": "Zum Folgeposten wechseln, ihn weiterverarbeiten, Bereitschaft prüfen und als aktuellen Posten halten.",
    "B3-S001": "An der oberen offenen Randstation länger auffangen; Schluss.",
    "B3-S002": "Danach zur nächsten Stelle führen und dort länger erwärmen; Schluss.",
    "B3-S003": "Diesen Posten auf Sollmaß bringen und abführen; Schluss.",
    "B3-S004": "Davon eine Menge abmessen und zur folgenden Stelle bringen.",
    "B3-S005": "In die mittlere runde Randstation überführen; Schluss.",
    "B3-S006": "Den Posten übertragen, am Ziel einsetzen und weiterführen; Schluss.",
    "B3-S007": "Bemessen, überführen und länger einwirken lassen; Schluss.",
    "B3-S008": "Aus der Station abführen; Schluss.",
    "B3-S009": "Den Posten einsetzen.",
    "B3-S010": "Der unteren korbartigen Randstation zuführen und kurz weiterführen; Schluss.",
    "B3-S011": "Die Vorbereitung übertragen, einsetzen, weiterführen und beim Quellposten belassen.",
    "B3-S012": "Den Ansatz kurz absetzen lassen; Schluss.",
    "B3-S013": "Einen Anteil bemessen, kurz vorbereiten und kurz einwirken lassen; Schluss.",
    "B3-S014": "In den Lauf einsetzen und länger absetzen lassen; Schluss.",
    "B3-S015": "Aus der Station abführen; Schluss.",
    "B3-S016": "Abziehen und in die nächste Station einführen; Schluss.",
    "B3-S017": "Länger einwirken lassen; Schluss.",
    "B3-S018": "Kurz absetzen lassen; Schluss.",
    "B3-S019": "Nach dem Einsatz absetzen lassen; Schluss.",
    "B3-S020": "Dorthin führen und abführen; Schluss.",
    "B3-S021": "Den Posten bemessen und, sobald er bereit ist, dorthin bringen. Für den zweiten Zustand das Sollmaß am Ziel absetzen, kurz vorbereiten, den aktuellen Posten dorthin bringen, die Bereitschaft prüfen und den Zieltransfer schließen.",
    "B3-S022": "Zur folgenden Station übertragen; Schluss.",
    "B3-S023": "Aus der Station abführen; Schluss.",
    "B3-S024": "Überführen; Schluss.",
    "B3-S025": "In die nächste Station einführen; Schluss.",
    "B3-S026": "Von der Quelle übertragen, auf den Sollabsetzstand bringen, weiterführen, einen Anteil zugeben, Bereitschaft prüfen, am Ziel vorbereiten und länger sammeln; Schluss.",
    "B3-S027": "Die folgende Stufe länger halten; Schluss.",
    "B3-S028": "Länger einwirken lassen, dann den kurzen Einwirkpunkt schließen.",
    "B3-S029": "Weiterführen, den vollen Anteil nehmen und kurz einwirken lassen; Schluss.",
    "B3-S030": "Einsetzen, auf Sollmaß bringen, im Lauf weiterführen und zur nächsten Station übertragen; Schluss.",
    "B3-S031": "Länger einwirken lassen; Schluss.",
    "B3-S032": "Einen Anteil übertragen, weiterführen, den kurzen Sollwert und das Folgemaß einstellen, dann kurz weiterführen; Schluss.",
    "B3-S033": "Abziehen; Schluss.",
    "B3-S034": "Die Arbeitsstufe auf bereit stellen, Anteil und Folgemaß nehmen und am Zwischenziel kurz absetzen; Schluss.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def statement_number(statement_id: str) -> int:
    return int(statement_id.split("S")[1])


def main() -> None:
    selected_events = [row for row in read(EVENTS) if row["record_unit_id"] in {"H3", "B3"}]
    master_rows = [row for row in read(MASTER) if row["record_unit_id"] in {"H3", "B3"}]
    master_by_event = {int(row["event_serial"]): row for row in master_rows}
    normalization = {row["surface"]: row for row in read(NORMALIZATION)}
    modes = {row["field_id"]: row for row in read(MODES)}

    event_rows: list[dict[str, object]] = []
    for row in selected_events:
        event_serial = int(row["event_id"][1:])
        norm = normalization[row["surface"]]
        master = master_by_event[event_serial]
        event_rows.append(
            {
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "field_id": row["field_id"],
                "field_position": row["field_position"],
                "visible_surface": row["surface"],
                "normalized_master_form": norm["master_form"],
                "master_card_id": row["master_card_id"],
                "portable_value_de": norm["portable_value_de"],
                "normalization_rule": norm["normalization_rule"],
                "field_frame_mode": modes[row["field_id"]]["field_frame_mode"],
                "visible_owner": master["visible_owner"],
                "terminal_status": master["terminal_status"],
            }
        )
    write(OUT / "HUNDRED_NINETY_SEVENTH_103_EVENT_NORMALIZED_INTERLINEAR.tsv", event_rows)

    by_field: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_field[str(row["field_id"])].append(row)
        by_statement[str(row["statement_id"])].append(row)

    field_rows: list[dict[str, object]] = []
    for field_id in sorted(by_field, key=lambda value: int(value[1:])):
        rows = by_field[field_id]
        field_rows.append(
            {
                "field_id": field_id,
                "statement_id": rows[0]["statement_id"],
                "record_unit_id": rows[0]["record_unit_id"],
                "visible_owner": rows[0]["visible_owner"],
                "field_frame_mode": rows[0]["field_frame_mode"],
                "visible_sequence": " ".join(str(row["visible_surface"]) for row in rows),
                "normalized_sequence": " ".join(str(row["normalized_master_form"]) for row in rows),
                "card_sequence": " ".join(str(row["master_card_id"]) for row in rows),
                "literal_values": " | ".join(str(row["portable_value_de"]) for row in rows),
                "terminal": "YES" if rows[-1]["terminal_status"] == "CLOSE" else "NO",
            }
        )
    write(OUT / "HUNDRED_NINETY_SEVENTH_42_FIELD_NORMALIZED_EDITION.tsv", field_rows)

    old_by_statement: dict[str, str] = {}
    for row in master_rows:
        old_by_statement.setdefault(row["statement_id"], row["complete_workshop_expansion_de"])
    statement_rows: list[dict[str, object]] = []
    ordered_statements = sorted(by_statement, key=lambda value: (0 if value.startswith("H3") else 1, statement_number(value)))
    for statement_id in ordered_statements:
        rows = by_statement[statement_id]
        field_ids = list(dict.fromkeys(str(row["field_id"]) for row in rows))
        statement_rows.append(
            {
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "visible_owner": rows[0]["visible_owner"],
                "field_ids": "|".join(field_ids),
                "frame_modes": "|".join(modes[field_id]["field_frame_mode"] for field_id in field_ids),
                "visible_sequence": " ".join(str(row["visible_surface"]) for row in rows),
                "normalized_sequence": " ".join(str(row["normalized_master_form"]) for row in rows),
                "literal_card_reading": " | ".join(str(row["portable_value_de"]) for row in rows),
                "previous_fluent_expansion": old_by_statement[statement_id],
                "revised_fluent_translation_de": TRANSLATIONS[statement_id],
                "revision_reason": "D_FRAME_CARRY_READING" if statement_id == "H3-S003" else "S_FRAME_TWO_STATE_READING" if statement_id == "B3-S021" else "NORMALIZE_ALLOGRAPHS_AND_REMOVE_REPEATED_PREAMBLE",
            }
        )
    write(OUT / "HUNDRED_NINETY_SEVENTH_38_STATEMENT_REVISED_EDITION.tsv", statement_rows)

    lines = ["# Normalisierte fortlaufende Ausgabe H3 und B3", ""]
    for record_id, title in (("H3", "H3 / f11r — Pflanzenzubereitung"), ("B3", "B3 / f83r — Gefäß- und Randstationsfolge")):
        lines.extend([f"## {title}", ""])
        selected = [row for row in statement_rows if row["record_unit_id"] == record_id]
        for row in selected:
            lines.append(f"- **{row['statement_id']}** `{row['visible_sequence']}`")
            lines.append(f"  - Normalisiert: `{row['normalized_sequence']}`")
            lines.append(f"  - Lesung: {row['revised_fluent_translation_de']}")
        lines.append("")
    lines.extend([
        "## Continuous reading", "",
        "H3 describes a compact preparation chain: set up the plant material in a liquid preparation, press it out, let it stand, strain again, take the clear extract, then carry the previous batch forward by measure.", "",
        "B3 is not one enormous sentence. It is a station ledger of short cells: collect, move, measure, set at a target, let act, settle, drain and repeat at the next visible owner. The long S-framed statement B3-S021 records two linked state/target entries inside that sequence.", "",
    ])
    (OUT / "HUNDRED_NINETY_SEVENTH_TWO_RECORD_CONTINUOUS_EDITION.md").write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "master_source_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest(),
        "normalization_sha256": hashlib.sha256(NORMALIZATION.read_bytes()).hexdigest(),
        "mode_source_sha256": hashlib.sha256(MODES.read_bytes()).hexdigest(),
        "records": 2,
        "events": len(event_rows),
        "fields": len(field_rows),
        "statements": len(statement_rows),
        "h3_events": sum(row["record_unit_id"] == "H3" for row in event_rows),
        "b3_events": sum(row["record_unit_id"] == "B3" for row in event_rows),
        "all_translations_present": all(row["revised_fluent_translation_de"] for row in statement_rows),
        "all_surfaces_normalized": all(row["normalized_master_form"] for row in event_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
