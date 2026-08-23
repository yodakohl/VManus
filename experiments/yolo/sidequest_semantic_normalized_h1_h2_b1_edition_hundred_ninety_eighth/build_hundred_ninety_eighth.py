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
    "H1-S001": "Den Grundteil der Bildpflanze nehmen, einen Anteil im Aufnahmegefäß vorbereiten, Flüssigkeit zugießen, den Folgeteil einsetzen und auf Sollmaß bringen.",
    "H1-S002": "Die erste Charge weiterbearbeiten, weiterführen und als bereit halten.",
    "H2-S001": "Aus dem bereiten Auszugsansatz die nächste Charge ansetzen, den Folgeposten wählen und diesen auf Sollmaß bringen.",
    "H2-S002": "Den Folgeansatz und denselben aktiven Ansatz weiterführen, davon eine Sollmenge nehmen und die Folge beibehalten.",
    "H2-S003": "Den Arbeitsansatz in der nächsten Stufe bearbeiten und die vorgeschriebene Zugabemenge einsetzen.",
    "B1-S001": "Kurz einwirken lassen; Schluss.",
    "B1-S002": "Die Charge bemessen und in den Beckenlauf einsetzen; davon erst einen, dann einen weiteren Anteil dorthin geben; über Anschluss und Zusatz mit demselben Ansatz weiterarbeiten; kurze Zielpassage und Sollmaß, langer Zieleinsatz und nochmals Sollmaß setzen, dann durchleiten und überführen; Schluss.",
    "B1-S003": "Weiterführen und haltend übertragen; Schluss.",
    "B1-S004": "Überführen, weiterführen und kurz absetzen lassen; Schluss.",
    "B1-S005": "Weiterführen; Schluss.",
    "B1-S006": "Einen Anteil zugeben, durchleiten und den Zusatz an der Zielmarke halten.",
    "B1-S007": "In die offene Zielstelle einführen; Schluss.",
    "B1-S008": "Diesen Posten weiterführen, kurz wärmen, nochmals weiterführen und kurz absetzen lassen; Schluss.",
    "B1-S009": "Kurz einwirken lassen; Schluss.",
    "B1-S010": "Kurz einwirken lassen; Schluss.",
    "B1-S011": "Durch den verbundenen Gang leiten und einsetzen.",
    "B1-S012": "Waschen, kurz einwirken lassen und nochmals waschen; Schluss.",
    "B1-S013": "Einen Waschgang ausführen; Schluss.",
    "B1-S014": "Überführen, im Weitergang an der Zielstelle abführen und zur Folgequelle weitergehen.",
    "B1-S015": "Den kurzen Teil aus der eben gesetzten Quelle einführen; Schluss.",
    "B1-S016": "Am Ziel einsetzen, länger einwirken lassen, weiterführen und kurz absetzen lassen; Schluss.",
    "B1-S017": "Dorthin bringen, kurz weiterführen und übertragen; Schluss.",
    "B1-S018": "Den Abführposten kurz halten, die Arbeitsstufe setzen und länger auffangen; Schluss.",
    "B1-S019": "Kurz absetzen lassen; Schluss.",
    "B1-S020": "Kurz wärmen und durchlassen; Schluss.",
    "B1-S021": "Dorthin bringen.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def order(statement_id: str) -> tuple[int, int]:
    record = statement_id.split("-")[0]
    return {"H1": 0, "H2": 1, "B1": 2}[record], int(statement_id.split("S")[1])


def main() -> None:
    records = {"H1", "H2", "B1"}
    events = [row for row in read(EVENTS) if row["record_unit_id"] in records]
    master_rows = [row for row in read(MASTER) if row["record_unit_id"] in records]
    master_by_event = {int(row["event_serial"]): row for row in master_rows}
    normalization = {row["surface"]: row for row in read(NORMALIZATION)}
    modes = {row["field_id"]: row for row in read(MODES)}

    event_rows: list[dict[str, object]] = []
    for row in events:
        norm = normalization[row["surface"]]
        master = master_by_event[int(row["event_id"][1:])]
        event_rows.append({
            "event_id": row["event_id"], "statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"],
            "page": row["page"], "field_id": row["field_id"], "field_position": row["field_position"],
            "visible_surface": row["surface"], "normalized_master_form": norm["master_form"],
            "master_card_id": row["master_card_id"], "portable_value_de": norm["portable_value_de"],
            "normalization_rule": norm["normalization_rule"], "field_frame_mode": modes[row["field_id"]]["field_frame_mode"],
            "visible_owner": master["visible_owner"], "terminal_status": master["terminal_status"],
        })
    write(OUT / "HUNDRED_NINETY_EIGHTH_104_EVENT_NORMALIZED_INTERLINEAR.tsv", event_rows)

    by_field: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_field[str(row["field_id"])].append(row); by_statement[str(row["statement_id"])].append(row)
    field_rows: list[dict[str, object]] = []
    for field_id in sorted(by_field, key=lambda value: int(value[1:])):
        rows = by_field[field_id]
        field_rows.append({
            "field_id": field_id, "statement_id": rows[0]["statement_id"], "record_unit_id": rows[0]["record_unit_id"],
            "visible_owner": rows[0]["visible_owner"], "field_frame_mode": rows[0]["field_frame_mode"],
            "visible_sequence": " ".join(str(row["visible_surface"]) for row in rows),
            "normalized_sequence": " ".join(str(row["normalized_master_form"]) for row in rows),
            "card_sequence": " ".join(str(row["master_card_id"]) for row in rows),
            "literal_values": " | ".join(str(row["portable_value_de"]) for row in rows),
            "terminal": "YES" if rows[-1]["terminal_status"] == "CLOSE" else "NO",
        })
    write(OUT / "HUNDRED_NINETY_EIGHTH_29_FIELD_NORMALIZED_EDITION.tsv", field_rows)

    old = {}
    for row in master_rows:
        old.setdefault(row["statement_id"], row["complete_workshop_expansion_de"])
    statement_rows: list[dict[str, object]] = []
    for statement_id in sorted(by_statement, key=order):
        rows = by_statement[statement_id]
        field_ids = list(dict.fromkeys(str(row["field_id"]) for row in rows))
        statement_rows.append({
            "statement_id": statement_id, "record_unit_id": rows[0]["record_unit_id"], "visible_owner": rows[0]["visible_owner"],
            "field_ids": "|".join(field_ids), "frame_modes": "|".join(modes[field_id]["field_frame_mode"] for field_id in field_ids),
            "visible_sequence": " ".join(str(row["visible_surface"]) for row in rows),
            "normalized_sequence": " ".join(str(row["normalized_master_form"]) for row in rows),
            "literal_card_reading": " | ".join(str(row["portable_value_de"]) for row in rows),
            "previous_fluent_expansion": old[statement_id], "revised_fluent_translation_de": TRANSLATIONS[statement_id],
            "revision_reason": "CH_BASE_PREPARATION" if statement_id.startswith(("H1", "H2")) else "O_Q_BATH_CELL_AND_ALLOGRAPH_NORMALIZATION",
        })
    write(OUT / "HUNDRED_NINETY_EIGHTH_26_STATEMENT_REVISED_EDITION.tsv", statement_rows)

    lines = ["# Normalisierte fortlaufende Ausgabe H1, H2 und B1", ""]
    for record_id, title in (("H1", "H1 / f10r — Grundansatz"), ("H2", "H2 / f10r — Folgechargen"), ("B1", "B1 / f81v — gemeinsames Beckenfeld")):
        lines.extend([f"## {title}", ""])
        for row in [item for item in statement_rows if item["record_unit_id"] == record_id]:
            lines.append(f"- **{row['statement_id']}** `{row['visible_sequence']}`")
            lines.append(f"  - Normalisiert: `{row['normalized_sequence']}`")
            lines.append(f"  - Lesung: {row['revised_fluent_translation_de']}")
        lines.append("")
    lines.extend([
        "## Continuous reading", "",
        "H1 prepares a base batch from the pictured plant. H2 reuses that batch as the source for successive measured charges. B1 then treats those charges as short basin cells: set, pass, warm, hold, wash, settle and transfer. The repeated one-card cells are operational repeats, not new sentences with omitted vocabulary.", "",
    ])
    (OUT / "HUNDRED_NINETY_EIGHTH_THREE_RECORD_CONTINUOUS_EDITION.md").write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(), "master_source_sha256": hashlib.sha256(MASTER.read_bytes()).hexdigest(),
        "normalization_sha256": hashlib.sha256(NORMALIZATION.read_bytes()).hexdigest(), "mode_source_sha256": hashlib.sha256(MODES.read_bytes()).hexdigest(),
        "records": 3, "events": len(event_rows), "fields": len(field_rows), "statements": len(statement_rows),
        "record_event_counts": {record: sum(row["record_unit_id"] == record for row in event_rows) for record in sorted(records)},
        "all_translations_present": all(row["revised_fluent_translation_de"] for row in statement_rows),
        "all_surfaces_normalized": all(row["normalized_master_form"] for row in event_rows), "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
