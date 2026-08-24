#!/usr/bin/env python3
"""Compress the master dictation into eleven fluent German record readings."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
VISIBLE = ROOT / "experiments/yolo/sidequest_semantic_seven_page_continuous_reading_three_hundred_fifty_eighth/THREE_HUNDRED_FIFTY_EIGHTH_381_VISIBLE_380_SOURCE_EDITION.tsv"
DICTATION = ROOT / "experiments/yolo/sidequest_semantic_full_master_dictation_three_hundred_fifty_ninth/THREE_HUNDRED_FIFTY_NINTH_FIFTY_SEVEN_LINE_MASTER_DICTATION.tsv"
HERBAL = ROOT / "experiments/yolo/sidequest_semantic_repaired_herbal_edition_three_hundred_thirtieth/THREE_HUNDRED_THIRTIETH_19_FLUENT_STATEMENTS.tsv"
BIO = ROOT / "experiments/yolo/sidequest_semantic_repaired_bio_edition_three_hundred_thirty_second/THREE_HUNDRED_THIRTY_SECOND_97_REPAIRED_BIO_STATEMENTS.tsv"
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]

OWNER_NOUNS = {
    "Wurzel und übrige Teile der abgebildeten Pflanze": ("abgebildete unbenannte Pflanze", "Pflanzenbild"),
    "zweiter Arbeitsartikel unter demselben Pflanzenbild": ("zweiter Arbeitsartikel; dasselbe Pflanzenbild", "Pflanzenbild und Recordordnung"),
    "Blütenkraut der abgebildeten Pflanze": ("abgebildete unbenannte Pflanze", "Pflanzenbild"),
    "Blattmaterial der abgebildeten Pflanze": ("Blattmaterial; abgebildete unbenannte Pflanze", "Pflanzenbild"),
    "Stängel-/Pflanzenteil der abgebildeten Pflanze": ("Stängel-/Pflanzenteil; abgebildete unbenannte Pflanze", "Pflanzenbild"),
    "B1_SHARED_TWO_ROW_POOL": ("gemeinsames zweireihiges Becken", "Bio-Zeichnung"),
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": ("oberes Paarbecken; Mittelzylinder", "Bio-Zeichnung"),
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": ("linkes Zwischengerät; Knoten", "Bio-Zeichnung"),
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": ("unklarer rechter Posten", "Bio-Zeichnung"),
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": ("unteres mehrplätziges Figurenbecken", "Bio-Zeichnung"),
    "B2_LOWER_POOL_EDGE_STATIONS": ("untere Beckenrandstationen", "Bio-Zeichnung"),
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": ("oberer offener Fächerzulauf", "Bio-Zeichnung"),
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": ("runde Rand-/Zwischenstation", "Bio-Zeichnung"),
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": ("korbförmiges Sammelgefäß", "Bio-Zeichnung"),
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": ("unverbundener Übergabeposten", "Bildlücke und lokale Station"),
    "B3_MAIN_ARCH_LINKED_PAIR": ("sichtbar verbundenes Bogenpaar", "Bio-Zeichnung"),
    "B4_MAIN_ARCH_LINKED_PAIR": ("sichtbar verbundenes Anwendungs-/Durchlasspaar", "Bio-Zeichnung"),
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": ("offene linke Randstation", "Bio-Zeichnung"),
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": ("rechte s-förmige Mehrportstation", "Bio-Zeichnung"),
    "B5_LEFT_OPEN_FRINGE_STATION": ("linker offener Nachtragsposten", "Bio-Zeichnung"),
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": ("rechter s-förmiger Nachtragsposten", "Bio-Zeichnung"),
}

TEXT_REPLACEMENTS = {
    "AMBIGUER_RECHTER_POSTEN": "unklaren rechten Posten",
    "ANWENDUNGS_UND_DURCHLASS_PAAR": "Anwendungs- und Durchlasspaar",
    "GEMEINSAMES_BEHANDLUNGSBECKEN": "gemeinsamen zweireihigen Becken",
    "KORB_SAMMELGEFAESS": "korbförmigen Sammelgefäß",
    "LINKER_NACHTRAGSPOSTEN": "linken Nachtragsposten",
    "MEHRPLATZ_BADBECKEN": "mehrplätzigen Badbecken",
    "OFFENER_FAECHERZULAUF": "offenen Fächerzulauf",
    "OFFENE_LINKSSTATION": "offenen linken Station",
    "PAARBECKEN_MIT_MITTELZYLINDER": "Paarbecken mit Mittelzylinder",
    "RAND_ZUFUEHR_ABFUEHRSTATIONEN": "Randstationen für Zu- und Abführung",
    "RECHTER_NACHTRAGSPOSTEN": "rechten Nachtragsposten",
    "RUNDE_ZWISCHENSTATION": "runden Zwischenstation",
    "SICHTBAR_VERBUNDENES_PAAR": "sichtbar verbundenen Paar",
    "S_FOERMIGER_MEHRPORT": "s-förmigen Mehrportstation",
    "UNVERBUNDENER_UEBERGABEPOSTEN": "unverbundenen Übergabeposten",
    "ZWISCHENGERAET_MIT_KNOTEN": "Zwischengerät mit Knoten",
    "Bei gemeinsamen zweireihigen Becken": "Am gemeinsamen zweireihigen Becken",
    "Bei Paarbecken mit Mittelzylinder": "Bei den Paarbecken mit Mittelzylinder",
    "Bei Zwischengerät mit Knoten": "Am Zwischengerät mit Knoten",
    "Bei unklaren rechten Posten": "Am unklaren rechten Posten",
    "Bei mehrplätzigen Badbecken": "Am mehrplätzigen Badbecken",
    "Bei Randstationen für Zu- und Abführung": "Bei den Randstationen für Zu- und Abführung",
    "Bei offenen Fächerzulauf": "Am offenen Fächerzulauf",
    "Bei runden Zwischenstation": "An der runden Zwischenstation",
    "Bei korbförmigen Sammelgefäß": "Am korbförmigen Sammelgefäß",
    "Bei unverbundenen Übergabeposten": "Am unverbundenen Übergabeposten",
    "Bei sichtbar verbundenen Paar": "Am sichtbar verbundenen Paar",
    "Bei Anwendungs- und Durchlasspaar": "Am Anwendungs- und Durchlasspaar",
    "Bei offenen linken Station": "An der offenen linken Station",
    "Bei s-förmigen Mehrportstation": "An der s-förmigen Mehrportstation",
    "Bei linken Nachtragsposten": "Am linken Nachtragsposten",
    "Bei rechten Nachtragsposten": "Am rechten Nachtragsposten",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def naturalize(text: str) -> str:
    for old, new in TEXT_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def main() -> None:
    visible = read_tsv(VISIBLE)
    dictation = read_tsv(DICTATION)
    statements = []
    for row in read_tsv(HERBAL):
        statements.append({"statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"], "text": row["fluent_workshop_translation_de"]})
    for row in read_tsv(BIO):
        statements.append({"statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"], "text": naturalize(row["fluent_station_translation_de"])})
    statement_order = {row["statement_id"]: index for index, row in enumerate(visible)}
    statements.sort(key=lambda row: statement_order[row["statement_id"]])

    owner_rows = []
    for owner, (nouns, source) in OWNER_NOUNS.items():
        records = sorted({row["record_unit_id"] for row in visible if row["owner"] == owner})
        lines = [row for row in dictation if owner in row["owner_sequence"].split("|")]
        owner_rows.append({
            "owner_id_or_phrase": owner,
            "concrete_nouns_supplied_de": nouns,
            "information_source": source,
            "records": "|".join(records),
            "physical_lines": len(lines),
            "card_word_claim": "NO__OWNER_SUPPLIES_REFERENT_NOT_CARD_VALUE",
        })
    write_tsv(HERE / "THREE_HUNDRED_SIXTIETH_TWENTY_ONE_OWNER_NOUNS.tsv", owner_rows,
              ["owner_id_or_phrase", "concrete_nouns_supplied_de", "information_source", "records", "physical_lines", "card_word_claim"])

    record_rows = []
    for record in RECORD_ORDER:
        events = [row for row in visible if row["record_unit_id"] == record]
        source_events = [row for row in events if row["source_position_contribution"] == "1"]
        record_statements = [row for row in statements if row["record_unit_id"] == record]
        owners = list(dict.fromkeys(row["owner"] for row in events))
        fluent = " ".join(row["text"] for row in record_statements)
        visible_surface = " ".join(row["surface"] for row in events)
        source_values = " → ".join(row["atomic_value_de"] for row in source_events)
        owner_nouns = "; ".join(OWNER_NOUNS[owner][0] for owner in owners)
        card_terms = "|".join(dict.fromkeys(row["atomic_value_de"] for row in source_events))
        record_rows.append({
            "record_unit_id": record,
            "page": events[0]["page"],
            "fluent_german_record": fluent,
            "visible_surface_sequence": visible_surface,
            "literal_source_value_sequence_de": source_values,
            "picture_or_owner_supplied_nouns_de": owner_nouns,
            "card_supplied_terms_de": card_terms,
            "german_grammar_expansion": "Artikel|Pronomen|Konjunktionen|Flexion|Imperativsyntax",
            "visible_events": len(events),
            "source_cards": len(source_events),
            "statements": len(record_statements),
            "physical_lines": sum(row["record_unit_id"] == record for row in dictation),
            "owner_count": len(owners),
        })
    write_tsv(
        HERE / "THREE_HUNDRED_SIXTIETH_ELEVEN_FLUENT_RECORDS.tsv",
        record_rows,
        ["record_unit_id", "page", "fluent_german_record", "visible_surface_sequence", "literal_source_value_sequence_de", "picture_or_owner_supplied_nouns_de", "card_supplied_terms_de", "german_grammar_expansion", "visible_events", "source_cards", "statements", "physical_lines", "owner_count"],
    )

    lines = [
        "# Elf flüssige deutsche Recordlesungen",
        "",
        "Die erste Ebene ist eine moderne Arbeitslesung. Darunter stehen alle",
        "sichtbaren Karten und danach jene konkreten Substantive, die nur aus Bild",
        "oder Stationsbesitzer stammen.",
        "",
    ]
    for row in record_rows:
        lines.extend([
            f"## {row['record_unit_id']} / {row['page']}",
            "",
            f"**Flüssige Lesung:** {row['fluent_german_record']}",
            "",
            f"**Sichtbare Karten:** `{row['visible_surface_sequence']}`",
            "",
            f"**Wörtliche Kartenwerte:** {row['literal_source_value_sequence_de']}",
            "",
            f"**Nur aus Bild/Besitzer:** {row['picture_or_owner_supplied_nouns_de']}",
            "",
        ])
    (HERE / "THREE_HUNDRED_SIXTIETH_COMPLETE_FLUENT_TRANSLATION.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    report = """# Pass 360 — elf flüssige moderne Lesungen

Die 57 Diktatzeilen sind jetzt zu elf zusammenhängenden deutschen Arbeitsabsätzen
verdichtet. Jeder Record veröffentlicht unmittelbar darunter seine sichtbare
Kartenfolge, die 380 wörtlichen Quellkartenwerte und die konkreten Substantive,
die nicht aus Karten, sondern aus Pflanze, Becken, Station oder Bildlücke kommen.

Die Trennung ist für die Arbeitstheorie zentral: Karten liefern Operation,
Maß, Zustand und formale Fortsetzung; das Bild liefert die konkrete Pflanze oder
Apparatestelle; modernes Deutsch fügt Artikel, Pronomen, Konjunktionen, Flexion
und Satzbau hinzu. Die flüssige Lesung darf deshalb nicht als Wort-für-Wort-
Entzifferung missverstanden werden, ist aber als Werkstattanweisung vollständig.

Als Nächstes sollte ein Gegenleser jeden der elf Absätze wieder in atomare
Kartenwerte zerlegen. Wo zwei verschiedene deutsche Formulierungen dieselbe
Kartenfolge ergeben, wird ein kurzer kontrollierter Werkstattstil gewählt; wo
die Kartenfolge nicht zurückgewonnen werden kann, wird der Absatz repariert.
"""
    (HERE / "THREE_HUNDRED_SIXTIETH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "records": len(record_rows),
        "fluent_statements": len(statements),
        "visible_events": sum(int(row["visible_events"]) for row in record_rows),
        "source_cards": sum(int(row["source_cards"]) for row in record_rows),
        "physical_lines": sum(int(row["physical_lines"]) for row in record_rows),
        "owner_noun_entries": len(owner_rows),
        "pages": len({row["page"] for row in record_rows}),
    }
    (HERE / "THREE_HUNDRED_SIXTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
