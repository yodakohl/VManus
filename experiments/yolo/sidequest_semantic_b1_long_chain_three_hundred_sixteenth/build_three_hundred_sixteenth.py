#!/usr/bin/env python3
"""Resegment the nineteen-card B1-S002 chain into executable worksteps."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_bio_glossary_three_hundred_fourteenth/THREE_HUNDRED_FOURTEENTH_281_ATOMIC_EVENT_READINGS.tsv"
MODES = ROOT / "experiments/yolo/sidequest_semantic_minimal_bio_dictionary_three_hundred_tenth/THREE_HUNDRED_TENTH_281_EVENT_DICTIONARY_ROUNDTRIP.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_bio_clause_templates_three_hundred_fifteenth/THREE_HUNDRED_FIFTEENTH_97_TEMPLATE_STATEMENTS.tsv"

STEPS = (
    (1, 1, 3, "MENGE_UND_BECKENLAUF_EINRICHTEN", "Messe die Arbeitsmenge ab und setze sie in den vorgesehenen Beckenlauf."),
    (2, 4, 8, "PORTIONEN_AN_DIESELBE_STELLE", "Nimm davon eine Portion und anschließend die Folgeportion an dieselbe Stelle."),
    (3, 9, 14, "ZUSATZ_AUS_GLEICHEM_ANSATZ_DURCH_ZIELPASSAGE", "Gib am Anschluss den Zusatz aus demselben Ansatz zu und führe ihn durch die kurze Zielpassage."),
    (4, 15, 17, "SOLLWERT_VOR_UND_NACH_ZIELHALT", "Prüfe das Sollmaß, halte am Ziel und prüfe das Maß erneut."),
    (5, 18, 19, "DURCHLEITEN_UND_UEBERFUEHREN", "Leite den Posten hindurch und überführe ihn."),
)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    target = [row for row in read(EVENTS) if row["statement_id"] == "B1-S002"]
    modes = {row["event_id"]: row["revised_operating_mode"] for row in read(MODES)}
    assert len(target) == 19
    event_rows: list[dict[str, object]] = []
    step_rows: list[dict[str, object]] = []
    for step_number, start, end, role, reading in STEPS:
        selected = target[start - 1:end]
        crosses_line = len({row["locus"] for row in selected}) > 1
        crosses_field = len({row["field_id"] for row in selected}) > 1
        step_rows.append({
            "microstep_id": f"B1-S002-M{step_number}",
            "event_ordinals": f"{start}-{end}",
            "event_ids": "|".join(row["event_id"] for row in selected),
            "surfaces": " ".join(row["fresh_surface"] for row in selected),
            "atomic_chain": " → ".join(row["atomic_gloss_de"] for row in selected),
            "mode_chain": ">".join(modes[row["event_id"]] for row in selected),
            "workstep_role": role,
            "concrete_reading_de": reading,
            "crosses_physical_line": "YES" if crosses_line else "NO",
            "crosses_field_boundary": "YES" if crosses_field else "NO",
            "segmentation_reason_de": "Neuer Bedienzweck beginnt; keine Satzgrenze wird aus dem Zeilenende abgeleitet.",
        })
        for ordinal, row in enumerate(selected, start=start):
            event_rows.append({
                "event_ordinal": ordinal,
                "event_id": row["event_id"], "page": row["page"], "locus": row["locus"], "field_id": row["field_id"],
                "surface": row["fresh_surface"], "master_card_id": row["master_card_id"],
                "atomic_gloss_de": row["atomic_gloss_de"], "operating_mode": modes[row["event_id"]],
                "terminal_scope": row["terminal_scope"], "microstep_id": f"B1-S002-M{step_number}",
                "event_role_in_microstep": "START" if ordinal == start else ("END" if ordinal == end else "MIDDLE"),
                "concrete_microstep_reading_de": reading,
            })
    event_rows.sort(key=lambda row: int(row["event_ordinal"]))
    event_path = HERE / "THREE_HUNDRED_SIXTEENTH_19_EVENT_RESEGMENTATION.tsv"
    step_path = HERE / "THREE_HUNDRED_SIXTEENTH_FIVE_MICROSTEPS.tsv"
    write(event_path, event_rows)
    write(step_path, step_rows)

    all_statements = [row for row in read(STATEMENTS) if row["record_unit_id"] == "B1"]
    lines = [
        "# B1 mit reparierter langer Arbeitsfolge",
        "",
        "B1-S002 bleibt eine einzige über zwei physische Zeilen laufende Aussage. Für die Ausführung wird sie jedoch in fünf Mikroschritte gegliedert.",
        "",
    ]
    for statement in all_statements:
        if statement["statement_id"] != "B1-S002":
            lines.append(f"- **{statement['statement_id']}:** {statement['compact_template_reading_de']}")
            continue
        lines += ["- **B1-S002:**", ""]
        for row in step_rows:
            cross = " *(über f81v.2→f81v.7 hinweg)*" if row["crosses_physical_line"] == "YES" else ""
            lines.append(f"  {row['microstep_id'][-2:]}. {row['concrete_reading_de']}{cross}")
    lines.append("")
    edition_path = HERE / "THREE_HUNDRED_SIXTEENTH_REVISED_B1_RECORD.md"
    edition_path.write_text("\n".join(lines), encoding="utf-8")

    report_path = HERE / "THREE_HUNDRED_SIXTEENTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 316: B1-S002 als fünf Werkstattschritte\n\n"
        "Die 19 Karten sind keine sinnvolle einzelne deutsche Satzperiode, aber auch nicht zwei Sätze an den beiden physischen Zeilen. Sie ergeben fünf Bedienblöcke mit Größen 3/5/6/3/2. Der dritte Block läuft ausdrücklich über die Grenze f81v.2→f81v.7: Anschluss und Zusatz stehen vor dem Umbruch, derselbe Ansatz und Zielpassage danach.\n\n"
        "Die stärkste neue Lesung ist das symmetrische Sollmaß–Ziellanghalt–Sollmaß als Vor-/Nachkontrolle: Sollmaß prüfen, am Ziel halten, Maß erneut prüfen. Der Gesamtgang lautet damit: Menge und Beckenlauf einrichten; Portion plus Folgeportion an dieselbe Stelle; Zusatz aus gleichem Ansatz durch die Zielpassage; Sollwert vor und nach dem Zielhalt; schließlich durchleiten und überführen.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS",
        "events": len(event_rows),
        "microsteps": len(step_rows),
        "step_sizes": [int(row["event_ordinals"].split("-")[1]) - int(row["event_ordinals"].split("-")[0]) + 1 for row in step_rows],
        "line_crossing_microsteps": sum(row["crosses_physical_line"] == "YES" for row in step_rows),
        "field_crossing_microsteps": sum(row["crosses_field_boundary"] == "YES" for row in step_rows),
        "terminal_events": sum(row["terminal_scope"] == "TERMINAL" for row in event_rows),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in (EVENTS, MODES, STATEMENTS)},
        "output_hashes": {path.name: sha(path) for path in (event_path, step_path, edition_path, report_path)},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
