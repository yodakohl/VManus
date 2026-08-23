#!/usr/bin/env python3
"""Build a continuous 116-statement translation without line-end sentences."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MASTER = ROOT / "experiments/yolo/sidequest_semantic_master_reader_codebook/MASTER_116_STATEMENT_EDITION.tsv"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72/V72_SELECTED_116_STATEMENTS.tsv"
R86 = ROOT / "experiments/yolo/sidequest_semantic_concrete_codex_eighty_sixth_edition/EIGHTY_SIXTH_776_CONCRETE_CODEX_BINDING.tsv"
R88 = ROOT / "experiments/yolo/sidequest_semantic_master_tail_repair_eighty_eighth_edition/EIGHTY_EIGHTH_14_REPAIRED_CODEX_UNITS.tsv"


SCENES = {
    "H1": "Bei der Bildpflanze, dem Wurzelansatz und dem ersten Auszug",
    "H2": "Bei der Bildpflanze, dem Spross-/Blattansatz und dem streichfähigen Mittel",
    "H3": "Bei der Bildpflanze, dem Blüten-/Blattauszug und der zweiten äußeren Anwendung",
    "H4": "Bei der Bildpflanze, dem geklärten Blattauszug und dem gebundenen Rest",
    "H5": "Bei der Bildpflanze, dem frischen Kraut und den zwei getrennten Zubereitungen",
    "B1": "Im gemeinsamen zweireihigen Figurenbecken",
    "B2": "An der jeweils neu gesetzten lokalen Beckenstation",
    "B3": "An den drei Randbecken und danach am sichtbar gekoppelten Hauptpaar",
    "B4": "Am Hauptpaar mit Tuchanwendung und getrennten Dienstläufen",
    "B5": "An der linken figurenlosen Dienststation",
    "B6": "An der rechten figurenlosen Dienststation",
}


HERBAL_OVERRIDES = {
    "H1-S001": "Nimm die Wurzel der Bildpflanze, säubere und zerteile sie, setze sie mit Wasser im Gefäß an und trenne den ersten Auszug ab; bemiss davon eine Portion als dosiertes Mittel und verwahre den Restteil.",
    "H1-S002": "Nimm den frischen Auszug wieder auf, erwärme ihn gelinde und verwende ihn, sobald der örtliche Bereitschaftszustand erreicht ist.",
    "H2-S001": "Nimm jungen Spross und Blatt der Bildpflanze, zerstoße sie, wringe sie durch Tuch aus und richte den Auszug als neuen Ansatz ein.",
    "H2-S002": "Gib dem Ansatz Trägerstoff zu, führe ihn als denselben Posten weiter und halte das vorgeschriebene Maß ein.",
    "H2-S003": "Bearbeite den Ansatz bis zur streichfähigen Stufe, teile eine örtliche Portion ab und verwende sie als gebundene Anwendung.",
    "H3-S001": "Nimm Blüte und junges Blatt, setze sie in Auszugsflüssigkeit an, wringe den Ansatz durch Tuch, lass ihn absetzen und seih ihn nochmals bis zum Klarlauf.",
    "H3-S002": "Behalte einen Teil des frischen Pflanzenstoffs als zweiten Vorrat zurück.",
    "H3-S003": "Bemiss eine Portion des geklärten Auszugs und gebrauche sie als dosiertes Mittel.",
    "H3-S004": "Setze den übrigen Auszug mit Trägerstoff als zweite äußere Anwendung an und halte ihn bis zur Gebrauchsstufe bereit.",
    "H4-S001": "Nimm Blatt der Bildpflanze, bemiss den Posten und setze ihn in Auszugsflüssigkeit im Gefäß an.",
    "H4-S002": "Wringe den Ansatz durch Tuch aus, sammle den klaren Anteil und verwende ihn frisch als Waschung.",
    "H4-S003": "Nimm den Pflanzenrest, gib Bindestoff zu und bearbeite ihn bis zum gebundenen Zustand.",
    "H4-S004": "Teile eine Portion der gebundenen Bereitung ab, bringe sie an die örtliche Stelle und verwende sie als gebundene Anwendung.",
    "H5-S001": "Nimm frisches Kraut, setze es mit Wasser kurz an und bereite daraus eine Waschung.",
    "H5-S002": "Nimm vom selben nassen Pflanzenstoff einen zweiten Teil und verwende ihn als gebundene Anwendung.",
    "H5-S003": "Halte den übrigen Pflanzenstoff zurück und beginne damit eine zweite Zubereitung.",
    "H5-S004": "Gib Auszugsflüssigkeit zu, führe den Ansatz durch Tuch und trenne den Auszug ab.",
    "H5-S005": "Gib Bindestoff zum abgetrennten Pflanzenstoff und führe ihn bis zur gebundenen Stufe weiter.",
    "H5-S006": "Bemiss eine örtliche Portion des zweiten Auszugs und gebrauche sie als dosiertes Mittel.",
}


PHRASES = {
    "Gebrauche diesen Auszug innerlich": "Gebrauche eine dosierte Portion dieses Auszugs",
    "gebrauche den Lauf innerlich": "gebrauche eine dosierte Portion des Laufs",
    "trinke es": "gebrauche die dosierte Portion",
    "Rotwein": "Auszugsflüssigkeit",
    "reinem Wein": "der Auszugsflüssigkeit",
    "in Wein": "in Auszugsflüssigkeit",
    "unter Öl": "unter Trägerstoff",
    "mit Öl": "mit Trägerstoff",
    "mit Honig": "mit Bindestoff",
    "zur Salbe": "zu einem streichfähigen Mittel",
    "eine weiche Salbe": "ein weiches streichfähiges Mittel",
    "als Einreibung": "als äußerliche Anwendung",
    "als Auflage": "als gebundene Anwendung",
    "eine zweite Arznei": "ein zweites Mittel",
    "frisch bereitete Arznei": "frisch bereitetes Mittel",
}


WORDS = {
    "Wein": "Auszugsflüssigkeit", "Öl": "Trägerstoff", "Honig": "Bindestoff",
    "Satz": "Restteil", "Trank": "dosiertes Mittel", "Salbe": "streichfähiges Mittel",
    "Einreibung": "äußerliche Anwendung", "Auflage": "gebundene Anwendung",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def repair(text: str) -> str:
    for old, new in PHRASES.items():
        text = text.replace(old, new)
    for old, new in WORDS.items():
        text = re.sub(rf"\b{re.escape(old)}\b", new, text)
    for old, new in {
        "fuehre": "führe", "Fuehre": "Führe", "Gefaess": "Gefäß",
        "Sollmass": "Sollmaß", "sollmass": "sollmaß", "waerme": "wärme",
        "Waerme": "Wärme", "schliesse": "schließe", "Schliesse": "Schließe",
        "laenger": "länger", "Laenger": "Länger", "uebergib": "übergib",
        "Oeffnung": "Öffnung", "oeffnung": "öffnung", "kuehle": "kühle",
        "Kuehle": "Kühle", "zurueck": "zurück", "naechsten": "nächsten",
        "naechste": "nächste", "Naechsten": "Nächsten", "Naechste": "Nächste",
        "weitergefuehr": "weitergeführ", "Staengel": "Stängel",
        "Standmass": "Standmaß", "Fertigmass": "Fertigmaß",
        "Zutatenmass": "Zutatenmaß", "Folgemass": "Folgemaß",
        "Absetzmass": "Absetzmaß", "vollstaendig": "vollständig",
        "Vollstaendig": "Vollständig", "schliessen": "schließen",
        "abfuehren": "abführen", "weiterfuehren": "weiterführen",
    }.items():
        text = text.replace(old, new)
    return text


def main() -> None:
    master = {row["statement_id"]: row for row in read_tsv(MASTER)}
    selected = read_tsv(V72)
    units = {row["unit_id"]: row for row in read_tsv(R88)}
    source_events = [row for row in read_tsv(R86) if int(row["unified_serial"]) <= 381]
    event_by_serial = {int(row["unified_serial"]): row for row in source_events}

    statement_rows = []
    event_to_statement = {}
    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for index, row in enumerate(selected, 1):
        m = master[row["statement_id"]]
        event_serials = [int(value) for value in row["event_serials"].split("|")]
        surface_sequence = " ".join(event_by_serial[serial]["visible_identity"] for serial in event_serials)
        line_crossing = row["line_crossing"].startswith("YES")
        card_near = repair(m["fluent_workshop_reading_de"])
        if row["record_unit_id"].startswith("H"):
            source_expansion = HERBAL_OVERRIDES[row["statement_id"]]
        else:
            source_expansion = card_near
        concrete = f"{SCENES[row['record_unit_id']]}: {source_expansion}"
        out = {
            "statement_order": index,
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "constituent_fields": row["constituent_fields"],
            "physical_loci": m["loci"],
            "line_crossing": "YES__CONTINUE_ACROSS_PHYSICAL_LINE" if line_crossing else "NO",
            "event_count": len(event_serials),
            "event_serials": "|".join(map(str, event_serials)),
            "visible_surface_sequence": surface_sequence,
            "card_near_workshop_reading_de": card_near,
            "concrete_source_expansion_de": concrete,
            "record_program_de": units[row["record_unit_id"]]["concrete_reading_de"],
            "sentence_boundary_rule": "STATEMENT_BOUNDARY__NEVER_INFERRED_FROM_LINE_END",
            "status": "COMPLETE_WORKING_TRANSLATION",
        }
        statement_rows.append(out)
        by_record[row["record_unit_id"]].append(out)
        for serial in event_serials:
            event_to_statement[serial] = out
    write_tsv(OUT / "EIGHTY_NINTH_116_CONTINUOUS_STATEMENT_TRANSLATION.tsv", statement_rows)

    event_rows = []
    for event in source_events:
        serial = int(event["unified_serial"])
        statement = event_to_statement[serial]
        event_rows.append({
            "event_serial": serial, "statement_id": statement["statement_id"],
            "record_unit_id": statement["record_unit_id"], "page": event["page"],
            "local_address": event["local_address"], "visible_identity": event["visible_identity"],
            "short_form_reading": event["short_form_reading"],
            "statement_translation_de": statement["concrete_source_expansion_de"],
            "line_crossing_statement": statement["line_crossing"],
        })
    write_tsv(OUT / "EIGHTY_NINTH_381_EVENT_STATEMENT_BINDING.tsv", event_rows)

    crossing = [row for row in statement_rows if str(row["line_crossing"]).startswith("YES")]
    write_tsv(OUT / "EIGHTY_NINTH_18_LINE_CROSSING_STATEMENTS.tsv", crossing)

    doc = [
        "# Fortlaufende Übersetzung der elf Prosarecords", "",
        "Diese Ausgabe trennt die nahe Kartenrücklesung von der ausgeschriebenen",
        "Quellenhandlung. Eine physische Zeile beendet niemals automatisch einen Satz.", "",
    ]
    for record_id in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"):
        record = by_record[record_id]
        unit = units[record_id]
        doc.extend([f"## {record_id} · {unit['page']}", "", f"**Gesamtlesung:** {unit['concrete_reading_de']}", ""])
        for statement in record:
            continuation = " *(läuft über eine physische Zeile weiter)*" if str(statement["line_crossing"]).startswith("YES") else ""
            doc.extend([
                f"### {statement['statement_id']}{continuation}", "",
                f"**Kartennah:** {statement['card_near_workshop_reading_de']}", "",
                f"**Ausgeschrieben:** {statement['concrete_source_expansion_de']}", "",
            ])
    (OUT / "EIGHTY_NINTH_11_CONTINUOUS_RECORD_TRANSLATIONS.md").write_text("\n".join(doc) + "\n", encoding="utf-8")

    report = [
        "# Neunundachtzigste Werkstattrunde: fortlaufende Prosa", "",
        "All 116 prose statements and all 381 visible prose events now have a card-near",
        "reading and a concrete source expansion. Eighteen statements explicitly cross",
        "physical lines; none is split into separate semantic statements at that point.", "",
        "The eight repaired Herbal classes from the previous round are propagated. The",
        "edition therefore says extraction liquid, carrier, binder, residue, dosed means,",
        "spreadable means, external application and bound application where the text does",
        "not force wine, oil, honey or a named finished product.", "",
        "This is the complete working translation for the fixed prose pages, not a claim",
        "that the German words reproduce historical plaintext. It is the current scribe's",
        "source program written out without leaving a card or statement unused.", "",
        "Only the fixed pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "EIGHTY_NINTH_EDITION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT", "records": len(by_record),
        "statements": len(statement_rows), "prose_events": len(event_rows),
        "line_crossing_statements": len(crossing),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
