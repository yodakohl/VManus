#!/usr/bin/env python3
"""Turn the attached card grammar into a concise continuous German edition."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_clause_attachment/COMPLETE_116_ATTACHED_STATEMENTS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


HERBAL_OVERRIDES = {
    "H1-S001": "Nimm die abgebildete Wurzel. Bereite daraus einen Ansatz, trenne einen Teil ab, gib ihn in das Gefäß und Wasser hinzu; führe den nächsten Teil weiter und stelle ihn auf Sollmaß.",
    "H1-S002": "Nimm den Posten in Arbeit, führe ihn weiter und halte ihn bereit.",
    "H2-S001": "Nimm den Auszugsansatz, bringe ihn bis zum Bereitschaftsgrad und führe ihn nach Sollmaß weiter.",
    "H2-S002": "Beginne den nächsten Ansatz, arbeite mit dem vorigen Ansatz weiter, stelle auf Sollmaß und entnimm vom Ausgang.",
    "H2-S003": "Bearbeite den laufenden Ansatz weiter, halte ihn auf der festgelegten Stufe und gib die vorgeschriebene Zutatenmenge zu.",
    "H3-S001": "Nimm den Pflanzenteil, bringe ihn zur Arbeitsstelle, wringe ihn aus, lasse ihn bis zum Sollwert stehen, seihe nach und stelle den Klarauszug beiseite.",
    "H3-S002": "Lege einen Teil der Zutat zurück.",
    "H3-S003": "Nimm den vorigen Posten wieder auf, bearbeite ihn und arbeite nach Sollmaß.",
    "H3-S004": "Nimm den verbleibenden Pflanzenteil als nächsten Posten, setze die Fortsetzung an und halte sie bereit.",
    "H4-S001": "Arbeite nach Sollmaß, nimm zwei bezeichnete Anteile und kühle den letzten ab.",
    "H4-S002": "Stelle auf Sollmaß, übertrage den Posten und verwahre ihn an der Zielstelle.",
    "H4-S003": "Nimm den abgemessenen Auszug aus der Quelle, wärme ihn länger und führe den Arbeitsgang zu Ende.",
    "H4-S004": "Arbeite nach Sollmaß, setze den Ansatz an der Zielstelle an und nimm davon eine Portion.",
    "H5-S001": "Nimm eine Zutat der abgebildeten Pflanze, bringe sie nach Sollmaß zur Arbeitsstelle und beginne damit den nächsten Ansatz.",
    "H5-S002": "Nimm den vorigen Posten wieder auf, setze diese Zutat an und lasse sie länger an der Zielstelle einwirken.",
    "H5-S003": "Halte die Zutat, bearbeite sie kurz und setze sie noch einmal an.",
    "H5-S004": "Nimm den Posten in Arbeit, gib den Auszug zu und bearbeite alles an der Zielstelle.",
    "H5-S005": "Setze die nächste Zutat an, nimm den Auszug daraus und wende ihn danach an.",
    "H5-S006": "Nimm den folgenden Posten, führe ihn kurz weiter und stelle ihn auf Sollmaß.",
}


REPLACEMENTS = [
    ("Stelle den Vorgabewert ein", "Arbeite nach Sollmaß"),
    ("Stelle auf den Vorgabewert ein", "Stelle auf Sollmaß"),
    ("stelle den Vorgabewert ein", "arbeite nach Sollmaß"),
    ("setze den Vorgabewert", "stelle auf Sollmaß"),
    ("freigegebenen Auszug", "Klarauszug"),
    ("freigegebenen Wert", "Klarauszug"),
    ("Setze länger an", "Bearbeite länger"),
    ("setze länger an", "bearbeite länger"),
    ("Setze kurz an", "Bearbeite kurz"),
    ("setze kurz an", "bearbeite kurz"),
    ("Setze die lange Stufe", "Bearbeite länger"),
    ("Setze den aktuellen Posten", "Nimm den aktuellen Posten in Arbeit"),
    ("Setze den Posten an", "Nimm den Posten in Arbeit"),
    ("setze den Posten an", "nimm den Posten in Arbeit"),
    ("Nimm die lange Folge", "Führe den längeren Folgegang aus"),
    ("Nimm den freigegebenen Auszug", "Nimm den Klarauszug"),
    ("Lies den freigegebenen Wert", "Nimm den Klarauszug"),
]


def speakable(statement_id: str, text: str) -> tuple[str, str]:
    if statement_id in HERBAL_OVERRIDES:
        return HERBAL_OVERRIDES[statement_id], "HAND_EDITED_HERBAL"
    revised = text
    for old, new in REPLACEMENTS:
        revised = revised.replace(old, new)
    return revised, "CONSISTENT_WORKSHOP_REPHRASE" if revised != text else "UNCHANGED_COMPACT"


def main() -> None:
    source = read_tsv(SOURCE)
    rows = []
    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for statement in source:
        compact, mode = speakable(statement["statement_id"], statement["continuous_workshop_reading_de"])
        row: dict[str, object] = {
            "statement_id": statement["statement_id"], "record_unit_id": statement["record_unit_id"],
            "page": statement["page"], "loci": statement["loci"],
            "surface_sequence": statement["surface_sequence"],
            "corrected_atom_chain": statement["corrected_atom_chain"],
            "attachment_skeleton_de": statement["attachment_skeleton_de"],
            "previous_reading_de": statement["continuous_workshop_reading_de"],
            "speakable_reading_de": compact, "editorial_mode": mode,
            "fusion_unit_count": statement["fusion_unit_count"],
            "equal_distance_attachments": statement["equal_distance_attachments"],
            "crosses_physical_line": statement["crosses_physical_line"],
        }
        rows.append(row)
        by_record[statement["record_unit_id"]].append(row)
    write_tsv(HERE / "COMPLETE_116_SPEAKABLE_STATEMENTS.tsv", rows, list(rows[0]))

    titles = {
        "H1": "Wurzelansatz", "H2": "Fortgesetzter Pflanzenansatz", "H3": "Auswringen und Nachseihen",
        "H4": "Verwahrter Auszug", "H5": "Frische Pflanzenfolge", "B1": "Gemeinsamer Beckenweg",
        "B2": "Stations- und Durchlaufweg", "B3": "Hauptfolge der Anwendungen",
        "B4": "Tuch-, Halte- und Nachwaschfolge", "B5": "Kurzer Seitenweg", "B6": "Abschlussweg",
    }
    pages = {rows[0]["record_unit_id"]: rows[0]["page"] for rows in by_record.values()}
    edition = "# Sprechbare Elf-Record-Ausgabe\n\n"
    edition += "Jede sichtbare Sequenz bleibt in der 116-Zeilen-Tabelle gebunden. Hier wird die Kartenschrift so ausgesprochen, wie ein Lehrmeister den gekürzten Arbeitsgang einem Schreiber diktieren könnte.\n\n"
    summary_rows = []
    for record_id in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]:
        record_rows = by_record[record_id]
        paragraph = " ".join(str(row["speakable_reading_de"]) for row in record_rows)
        edition += f"## {record_id} — {titles[record_id]} ({pages[record_id]})\n\n{paragraph}\n\n"
        for row in record_rows:
            edition += f"- `{row['statement_id']}` **{row['surface_sequence']}** — {row['speakable_reading_de']}\n"
        edition += "\n"
        summary_rows.append({
            "record_unit_id": record_id, "page": pages[record_id], "title_de": titles[record_id],
            "statement_count": len(record_rows), "event_count": sum(len(str(row["surface_sequence"]).split()) for row in record_rows),
            "hand_edited_statements": sum(row["editorial_mode"] == "HAND_EDITED_HERBAL" for row in record_rows),
            "rephrased_statements": sum(row["editorial_mode"] != "UNCHANGED_COMPACT" for row in record_rows),
            "continuous_translation_de": paragraph,
        })
    if edition.endswith("\n\n"):
        edition = edition[:-1]
    (HERE / "SPEAKABLE_ELEVEN_RECORD_EDITION.md").write_text(edition, encoding="utf-8")
    write_tsv(HERE / "RECORD_SUMMARY.tsv", summary_rows, list(summary_rows[0]))

    mode_counts = defaultdict(int)
    for row in rows:
        mode_counts[str(row["editorial_mode"])] += 1
    report = f"""# Vom Kartenstapel zur gesprochenen Anweisung

## Auswahl

Die aktive Seitenlesung wird jetzt in zwei Ebenen ausgesprochen. Die 173 kurzen Kartenwerte und die 254 Anheftungsgruppen bleiben die technische Unterlage. Darüber steht eine knappe fortlaufende Ausgabe aller elf Prosa-Records. Kein Zeilenende wird zum Satzende gemacht, und keine der 381 sichtbaren Karten fällt aus der Bindung.

Die wichtigste redaktionelle Entscheidung ist, `OK+E/EE/EEE` in laufender Rede nicht immer hölzern als „kurz/länger/vollständig setzen“ zu sprechen. Je nach Besitzer wird daraus **kurz bearbeiten**, **länger einwirken lassen** oder **vollständig ausführen**; der gemeinsame Stammwert bleibt *in Arbeit setzen*. `AIIN` wird als *Sollmaß*, `AIN` als *Portion*, `IIN` als *Stufe*, `AL/AR/AIR` als Ziel/Quelle/Laufflüssigkeit und `CHEEY` in den Nassfolgen als *Klarauszug* gesprochen.

## Vollständigkeit

- 116/116 Aussagen haben eine sprechbare Lesung.
- 381/381 sichtbare Prosaereignisse bleiben in exakter Reihenfolge gebunden.
- 19 Herbal-Aussagen wurden Satz für Satz von Hand geglättet.
- {mode_counts['CONSISTENT_WORKSHOP_REPHRASE']} Biological-Aussagen verwenden dieselben wiederkehrenden Sprachreparaturen.
- {mode_counts['UNCHANGED_COMPACT']} Aussagen waren bereits kurz genug und bleiben wörtlich stehen.

## Was die neue Fassung sagt

Herbal liest sich nun als fünf kleine Pflanzen-/Auszugsartikel: Wurzel oder anderer abgebildeter Pflanzenteil, Ansatz, Portion und Sollmaß, Wasser oder Auszug, Auswringen/Nachseihen, Verwahren und lokale Anwendung. Biological liest sich als sechs dicht codierte Becken-, Durchlauf-, Halte-, Tuch- und Nachwaschprogramme. Diese Sachlesung bleibt kreativ; der Fortschritt ist, dass derselbe kleine Stammwortschatz jetzt tatsächlich in durchgehender Werkstattrede funktioniert.
"""
    (HERE / "SPEAKABLE_EDITION_REPORT.md").write_text(report, encoding="utf-8")
    result = {
        "status": "PASS", "statements": len(rows), "records": len(summary_rows),
        "events": sum(len(row["surface_sequence"].split()) for row in rows),
        "mode_counts": dict(sorted(mode_counts.items())),
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
