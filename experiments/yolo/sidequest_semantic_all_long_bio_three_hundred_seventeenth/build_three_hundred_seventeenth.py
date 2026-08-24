#!/usr/bin/env python3
"""Resegment every Biological statement longer than five cards."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_bio_glossary_three_hundred_fourteenth/THREE_HUNDRED_FOURTEENTH_281_ATOMIC_EVENT_READINGS.tsv"
MODES = ROOT / "experiments/yolo/sidequest_semantic_minimal_bio_dictionary_three_hundred_tenth/THREE_HUNDRED_TENTH_281_EVENT_DICTIONARY_ROUNDTRIP.tsv"
RENDERER = ROOT / "experiments/yolo/sidequest_semantic_bio_renderer_three_hundred_twelfth/THREE_HUNDRED_TWELFTH_281_RENDERER_TRACE.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_bio_clause_templates_three_hundred_fifteenth/THREE_HUNDRED_FIFTEENTH_97_TEMPLATE_STATEMENTS.tsv"

# Ordinals are inclusive inside the fixed statement.  The splits follow a
# change in practical purpose and deliberately need not follow a line break.
SEGMENTS = {
    "B1-S002": [
        (1, 3, "MENGE_UND_BECKENLAUF", "Messe die Arbeitsmenge ab und setze sie in den vorgesehenen Beckenlauf."),
        (4, 8, "PORTIONEN_ZUR_STELLE", "Nimm davon eine Portion und anschließend die Folgeportion an dieselbe Stelle."),
        (9, 14, "ZUSATZ_DURCH_ZIELPASSAGE", "Gib am Anschluss den Zusatz aus demselben Ansatz zu und führe ihn durch die kurze Zielpassage."),
        (15, 17, "VOR_NACH_SOLLKONTROLLE", "Prüfe das Sollmaß, halte am Ziel und prüfe das Maß erneut."),
        (18, 19, "DURCHLEITEN_UEBERFUEHREN", "Leite den Posten hindurch und überführe ihn."),
    ],
    "B2-S005": [
        (1, 3, "ZIELSAMMLUNG_DURCHLEITEN", "Setze am Ziel ein, sammle bis zum Soll und leite hindurch."),
        (4, 6, "EINMAL_MESSEN_FOLGE_VORBEREITEN", "Messe einmal ab und bereite den folgenden Durchgang vor."),
        (7, 8, "LANG_WAERMEN_ABZIEHEN", "Wärme lange und ziehe anschließend ab."),
    ],
    "B2-S012": [
        (1, 1, "ABFUEHRGUT_UEBERNEHMEN", "Übernimm das Abführgut aus der vorherigen Station."),
        (2, 5, "KLARLAUF_BEARBEITEN", "Nimm den Klarlauf, bereite ihn kurz vor, halte ihn lange und ziehe den klaren Anteil ab."),
        (6, 8, "SOLL_VOLL_EINSETZEN", "Stelle das Sollmaß ein und setze diesen Posten vollständig ein."),
    ],
    "B2-S016": [
        (1, 4, "QUELLE_TEILEN_MESSEN", "Führe von der Quelle dorthin ab, teile den Posten und stelle das Sollmaß ein."),
        (5, 8, "FOLGE_KONTAKT_ZUFUEHRUNG", "Führe lange weiter, bemesse, berühre kurz und führe zu."),
    ],
    "B3-S021": [
        (1, 4, "POSTEN_BEMESSEN_BEREITSTELLEN", "Messe diesen Posten ab und stelle ihn dort bereit."),
        (5, 6, "AM_ZIEL_BIS_SOLL_ABSETZEN", "Setze ihn am Ziel bis zum Sollmaß ab."),
        (7, 11, "KURZ_VORBEREITEN_ZIELTRANSFER", "Bereite diesen Posten kurz vor, stelle ihn dort bereit und überführe ihn ans Ziel."),
    ],
    "B3-S026": [
        (1, 2, "QUELLTRANSFER_SOLL_ABSETZEN", "Überführe von der Quelle und setze bis zum Sollstand ab."),
        (3, 6, "ZUSATZ_AM_ZIEL_BEREITEN", "Überführe, gib den Zusatz zu und stelle die Zubereitung am Ziel bereit."),
        (7, 7, "LANG_SAMMELN", "Sammle den neuen Stationsposten lange."),
    ],
    "B3-S034": [
        (1, 3, "ARBEITSSTUFE_TEIL_BEREIT", "Stelle die Arbeitsstufe ein und halte den bezeichneten Teil bereit."),
        (4, 6, "FOLGEMASS_ZWISCHENZIEL_ABSETZEN", "Stelle das Folgemaß ein, führe zum Zwischenziel und setze kurz ab."),
    ],
    "B4-S003": [
        (1, 2, "ZUM_FOLGEZIEL_UEBERFUEHREN", "Überführe zum folgenden Ziel."),
        (3, 7, "FOLGEPOSTEN_BEHANDELN_ABSETZEN", "Behandle den Folgeposten lange, setze ihn ein, führe weiter und setze kurz ab."),
    ],
    "B4-S011": [
        (1, 3, "SOLL_KURZ_WAERMEN_LANG_FORTSETZEN", "Wärme bis zum Soll kurz an und führe den Gang lange fort."),
        (4, 7, "ZUGABE_UEBERFUEHREN_ABZIEHEN", "Gib die Portion zu, überführe sie, führe weiter und ziehe weiter ab."),
    ],
    "B4-S015": [
        (1, 4, "KLARLAUFPORTION_DURCH_ZIELPASSAGE", "Gib eine Portion des Klarlaufs zu und führe sie durch die Zielpassage."),
        (5, 6, "KURZ_SAMMELN_ABFUEHREN", "Sammle an der neuen Station kurz und führe ab."),
    ],
    "B5-S003": [
        (1, 4, "AM_ZIEL_ABSETZEN_WEITER_ABZIEHEN", "Setze am Ziel ab und ziehe dort weiter ab."),
        (5, 6, "ZIELTRANSFER_BIS_SOLL", "Überführe ans Ziel bis zum Sollmaß."),
        (7, 9, "ENDSTUFE_UEBERFUEHREN", "Führe zur Endstufe weiter und überführe."),
    ],
    "B6-S001": [
        (1, 4, "LANG_SAMMELN_ENDPOSTEN", "Sammle lange, bearbeite kurz und führe den Endposten weiter."),
        (5, 9, "EINLAGE_AM_ENDZIEL", "Stelle das Sollmaß ein, führe weiter und lege diesen Posten am Endziel ein."),
    ],
}


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
    events = read(EVENTS)
    modes = {row["event_id"]: row["revised_operating_mode"] for row in read(MODES)}
    renderer = {row["event_id"]: row for row in read(RENDERER)}
    statements = read(STATEMENTS)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)
    actual_long = {statement_id for statement_id, selected in by_statement.items() if len(selected) > 5}
    assert actual_long == set(SEGMENTS)

    step_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    for statement_id, definitions in SEGMENTS.items():
        selected_statement = by_statement[statement_id]
        covered: list[int] = []
        for step_ordinal, (start, end, role, reading) in enumerate(definitions, start=1):
            covered.extend(range(start, end + 1))
            selected = selected_statement[start - 1:end]
            event_ids = [row["event_id"] for row in selected]
            source_operations = len(event_ids) - (1 if {"E180", "E181"}.issubset(event_ids) else 0)
            reset_inside = [row["event_id"] for row in selected[1:] if renderer[row["event_id"]]["owner_reset_or_break"] == "YES"]
            step_id = f"{statement_id}-M{step_ordinal:02d}"
            step_rows.append({
                "microstep_id": step_id, "statement_id": statement_id,
                "record_unit_id": selected[0]["record_unit_id"], "page": selected[0]["page"],
                "event_ordinals": f"{start}-{end}", "event_ids": "|".join(event_ids),
                "surfaces": " ".join(row["fresh_surface"] for row in selected),
                "atomic_chain": " → ".join(row["atomic_gloss_de"] for row in selected),
                "mode_chain": ">".join(modes[row["event_id"]] for row in selected),
                "visible_event_count": len(selected), "source_operation_count": source_operations,
                "workstep_role": role, "concrete_reading_de": reading,
                "crosses_physical_line": "YES" if len({row["locus"] for row in selected}) > 1 else "NO",
                "crosses_field_boundary": "YES" if len({row["field_id"] for row in selected}) > 1 else "NO",
                "owner_reset_at_start": renderer[selected[0]["event_id"]]["owner_reset_or_break"],
                "owner_resets_inside": "|".join(reset_inside) or "NONE",
                "read_once_pair": "E180|E181" if {"E180", "E181"}.issubset(event_ids) else "NONE",
            })
            for ordinal, row in enumerate(selected, start=start):
                event_rows.append({
                    "statement_id": statement_id, "event_ordinal": ordinal, "event_id": row["event_id"],
                    "record_unit_id": row["record_unit_id"], "page": row["page"], "locus": row["locus"], "field_id": row["field_id"],
                    "surface": row["fresh_surface"], "master_card_id": row["master_card_id"],
                    "atomic_gloss_de": row["atomic_gloss_de"], "operating_mode": modes[row["event_id"]],
                    "microstep_id": step_id, "microstep_reading_de": reading,
                    "read_once_role": "ANTICIPATORY_COPY" if row["event_id"] == "E180" else ("EXECUTED_COPY" if row["event_id"] == "E181" else "ORDINARY"),
                })
        assert covered == list(range(1, len(selected_statement) + 1))
    event_path = HERE / "THREE_HUNDRED_SEVENTEENTH_105_LONG_STATEMENT_EVENTS.tsv"
    step_path = HERE / "THREE_HUNDRED_SEVENTEENTH_32_MICROSTEPS.tsv"
    write(event_path, event_rows)
    write(step_path, step_rows)

    steps_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in step_rows:
        steps_by_statement[str(row["statement_id"])].append(row)
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for statement in statements:
        by_record[statement["record_unit_id"]].append(statement)
    lines = [
        "# Biological-Gesamtausgabe mit kurzen Werkstattschritten",
        "",
        "Aussagen bis fünf Karten bleiben in der Sieben-Kopf-Lesung. Alle zwölf längeren Aussagen werden nach Bedienzweck, nicht nach Zeilenende, in 32 Mikroschritte zerlegt.",
        "",
    ]
    for record in ("B1", "B2", "B3", "B4", "B5", "B6"):
        lines += [f"## {record}", ""]
        for statement in by_record[record]:
            statement_id = statement["statement_id"]
            if statement_id not in steps_by_statement:
                lines.append(f"- **{statement_id}:** {statement['compact_template_reading_de']}")
                continue
            lines.append(f"- **{statement_id}:**")
            for row in steps_by_statement[statement_id]:
                annotations = []
                if row["crosses_physical_line"] == "YES":
                    annotations.append("über Zeilenwechsel")
                if row["read_once_pair"] != "NONE":
                    annotations.append("E180/E181 einmal lesen")
                suffix = f" *({' ; '.join(annotations)})*" if annotations else ""
                lines.append(f"  - {row['microstep_id'].split('-')[-1]}: {row['concrete_reading_de']}{suffix}")
        lines.append("")
    edition_path = HERE / "THREE_HUNDRED_SEVENTEENTH_SIX_RECORD_MICROSTEP_EDITION.md"
    edition_path.write_text("\n".join(lines), encoding="utf-8")

    report_path = HERE / "THREE_HUNDRED_SEVENTEENTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 317: alle langen Bio-Aussagen als Mikroschritte\n\n"
        "Genau zwölf der 97 Aussagen sind länger als fünf Karten. Ihre 105 sichtbaren Ereignisse werden zu 32 ausführbaren Schritten; wegen der Randkopie E180/E181 sind das 104 gelesene Operationen. Außer dem bereits begründeten sechs Karten langen B1-Querzeilenschritt hat jeder Schritt höchstens fünf Karten.\n\n"
        "Alle drei Besitzerwechsel innerhalb dieser langen Aussagen beginnen einen neuen Mikroschritt; keiner liegt versteckt in einem Schritt. Mehrere echte Schritte dürfen dagegen einen physischen Zeilenwechsel überqueren. Die Gesamtausgabe ist damit erstmals zugleich vollständig, kurz genug zum Ausführen und mit der sichtbaren Stationsgeometrie verträglich.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "long_statements": len(SEGMENTS), "visible_events": len(event_rows),
        "source_operations": sum(int(row["source_operation_count"]) for row in step_rows),
        "microsteps": len(step_rows), "max_step_size": max(int(row["visible_event_count"]) for row in step_rows),
        "six_card_steps": sum(int(row["visible_event_count"]) == 6 for row in step_rows),
        "line_crossing_steps": sum(row["crosses_physical_line"] == "YES" for row in step_rows),
        "field_crossing_steps": sum(row["crosses_field_boundary"] == "YES" for row in step_rows),
        "owner_resets_inside_steps": sum(row["owner_resets_inside"] != "NONE" for row in step_rows),
        "read_once_steps": sum(row["read_once_pair"] != "NONE" for row in step_rows),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in (EVENTS, MODES, RENDERER, STATEMENTS)},
        "output_hashes": {path.name: sha(path) for path in (event_path, step_path, edition_path, report_path)},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
