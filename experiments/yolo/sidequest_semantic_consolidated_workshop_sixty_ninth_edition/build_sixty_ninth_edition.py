#!/usr/bin/env python3
"""Consolidate the current ten-page creative workshop edition."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
H_GROUPS = ROOT / "experiments/yolo/sidequest_semantic_herbal_sourcebook_sixty_sixth_edition/SIXTY_SIXTH_100_HERBAL_GROUP_EDITION.tsv"
H_UNITS = ROOT / "experiments/yolo/sidequest_semantic_herbal_sourcebook_sixty_sixth_edition/SIXTY_SIXTH_5_COMPACT_HERBAL_ARTICLES.tsv"
B_GROUPS = ROOT / "experiments/yolo/sidequest_semantic_bio_station_handbook_sixty_seventh_edition/SIXTY_SEVENTH_281_BIO_GROUP_EDITION.tsv"
B_UNITS = ROOT / "experiments/yolo/sidequest_semantic_bio_station_handbook_sixty_seventh_edition/SIXTY_SEVENTH_6_COMPACT_BIO_RECORDS.tsv"
A_GROUPS = ROOT / "experiments/yolo/sidequest_semantic_astro_address_handbook_sixty_eighth_edition/SIXTY_EIGHTH_395_ASTRO_GROUP_ADDRESS_LEDGER.tsv"
A_UNITS = ROOT / "experiments/yolo/sidequest_semantic_astro_address_handbook_sixty_eighth_edition/SIXTY_EIGHTH_3_ASTRO_INSTRUMENT_CARDS.tsv"
HIERARCHY = ROOT / "experiments/yolo/sidequest_semantic_hierarchical_dictionary_fifty_fourth_edition/FIFTY_FOURTH_89_HIERARCHICAL_ENTRIES.tsv"
DESK_RULES = ROOT / "experiments/yolo/sidequest_semantic_pocket_grammar_fifty_fifth_edition/FIFTY_FIFTH_24_DESK_RULES.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    h_groups = read_tsv(H_GROUPS)
    b_groups = read_tsv(B_GROUPS)
    a_groups = read_tsv(A_GROUPS)
    unified = []
    serial = 0
    for row in h_groups:
        serial += 1
        unified.append({
            "unified_serial": serial,
            "register": "HERBAL_PROSE",
            "page": row["page"],
            "unit_or_locus": row["unit_id"],
            "source_group_identity": row["source_group_id"],
            "visible_identity": row["visible_surface"],
            "owner_or_namespace": row["record_id"],
            "construction_or_address": row["clause_shape_id"],
            "current_short_reading": row["period_source_clause"],
            "content_layer": "VISIBLE_PLANT_OWNER_PLUS_WORKSHOP_DICTIONARY_PLUS_MASTER_ARTICLE",
        })
    for row in b_groups:
        serial += 1
        unified.append({
            "unified_serial": serial,
            "register": "BIOLOGICAL_PROSE",
            "page": row["page"],
            "unit_or_locus": row["unit_id"],
            "source_group_identity": row["source_group_id"],
            "visible_identity": row["visible_surface"],
            "owner_or_namespace": row["local_owner"],
            "construction_or_address": row["clause_shape_id"],
            "current_short_reading": row["period_source_clause"],
            "content_layer": "VISIBLE_LOCAL_STATION_PLUS_WORKSHOP_DICTIONARY_PLUS_MASTER_ACTION",
        })
    for row in a_groups:
        serial += 1
        unified.append({
            "unified_serial": serial,
            "register": "ASTRO_LOCAL_LOOKUP",
            "page": row["page"],
            "unit_or_locus": row["locus"],
            "source_group_identity": f"A{int(row['group_serial']):03d}",
            "visible_identity": row["opaque_local_id"],
            "owner_or_namespace": row["local_namespace"],
            "construction_or_address": row["local_owner"],
            "current_short_reading": row["local_readout_instruction_de"],
            "content_layer": "VISIBLE_LOCUS_PLUS_LOCAL_MASTER_NOMENCLATOR",
        })
    write_tsv(OUT / "SIXTY_NINTH_776_CURRENT_GROUP_LEDGER.tsv", unified)

    units = []
    for row in read_tsv(H_UNITS):
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": row["record_id"],
            "page": row["page"],
            "register": "HERBAL_ARTICLE",
            "owner_or_system": row["owner"],
            "group_count": row["group_count"],
            "compact_current_reading_de": row["compact_article_de"],
            "concrete_content_wager": row["concrete_content_wager"],
            "strongest_rival": row["strongest_practical_rival"],
            "source_of_concrete_content": "VISIBLE_PLANT_PLUS_SIMULATED_MASTER_ARTICLE",
        })
    for row in read_tsv(B_UNITS):
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": row["record_id"],
            "page": row["page"],
            "register": "BIO_STATION_RECORD",
            "owner_or_system": row["local_owner_sequence"],
            "group_count": row["group_count"],
            "compact_current_reading_de": row["compact_station_handbook_de"],
            "concrete_content_wager": "LOCAL_BATH_WASH_CLOTH_TEMPER_DRAIN_APPLICATION",
            "strongest_rival": row["strongest_global_rival"],
            "source_of_concrete_content": "VISIBLE_LOCAL_STATION_PLUS_SIMULATED_MASTER_ACTION",
        })
    for row in read_tsv(A_UNITS):
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": row["diagram_id"],
            "page": row["page"],
            "register": "ASTRO_INSTRUMENT",
            "owner_or_system": row["visible_system"],
            "group_count": row["group_count"],
            "compact_current_reading_de": row["apprentice_lookup_instruction_de"],
            "concrete_content_wager": row["creative_content_wager"],
            "strongest_rival": row["strongest_competing_instrument"],
            "source_of_concrete_content": "VISIBLE_LOCUS_PLUS_LOCAL_MASTER_NOMENCLATOR",
        })
    write_tsv(OUT / "SIXTY_NINTH_14_CURRENT_UNITS.tsv", units)

    hierarchy = read_tsv(HIERARCHY)
    write_tsv(OUT / "SIXTY_NINTH_89_CURRENT_DICTIONARY_LAYERS.tsv", hierarchy)

    rules = []
    for row in read_tsv(DESK_RULES):
        rules.append({
            "teaching_order": len(rules) + 1,
            "rule_id": row["rule_id"],
            "desk_phase": row["desk_phase"],
            "cue": row["cue"],
            "apprentice_rule_de": row["apprentice_rule_de"],
        })
    additions = (
        ("F01", "HERBAL", "PLANT_OWNER", "Das ganze Pflanzenbild setzt den Artikelbesitzer; keine Pflanzenart aus der Schrift erfinden."),
        ("F02", "HERBAL", "MASTER_NOUNS", "Wasser, Wein, Öl, Honig, Trank, Salbe und Krankheit nur aus dem Artikelmaster ergänzen."),
        ("F03", "BIO", "LOCAL_STATION", "Bei jedem sichtbaren Stationswechsel Quelle, Ziel und Richtung löschen."),
        ("F04", "BIO", "NO_NETWORK", "Nur sichtbare lokale Kontakte benutzen; kein seitenweites Rohrnetz ergänzen."),
        ("F05", "ASTRO", "LOCAL_NAMESPACE", "Jedes Rad, Paneel und jeder Sternplatz besitzt einen eigenen lokalen Schlüssel."),
        ("F06", "ASTRO", "NO_ORIENTATION", "Ohne Zeiger keinen Start, keine Richtung und keine Rotation annehmen."),
        ("F07", "REGISTER", "NO_UNIVERSAL_WORD", "Kein konkretes Wort automatisch zwischen Prosa und Astro übertragen."),
        ("F08", "READBACK", "FOUR_LAYERS", "Form, Wörterbuch, Bildbesitzer und Meisterprosa bei jeder Lesung getrennt ausweisen."),
    )
    for rule_id, phase, cue, text in additions:
        rules.append({
            "teaching_order": len(rules) + 1,
            "rule_id": rule_id,
            "desk_phase": phase,
            "cue": cue,
            "apprentice_rule_de": text,
        })
    write_tsv(OUT / "SIXTY_NINTH_32_RULE_WORKSHOP_MANUAL.tsv", rules)

    edition = [
        "# Aktuelle vollständige Zehn-Seiten-Werkstattfassung", "",
        "Die Fassung enthält fünf Herbal-Artikel, sechs Biological-Stationsrecords",
        "und drei Astro-Instrumente. Die Texte sind kreative Arbeitsübersetzungen; die",
        "Register teilen Schreiberpraxis, nicht notwendig denselben konkreten Wortschatz.", "",
    ]
    for row in units:
        edition.extend([
            f"## {row['unit_id']} · {row['page']} · {row['register']}", "",
            row["compact_current_reading_de"], "",
            f"**Inhaltswette:** {row['concrete_content_wager']}.", "",
            f"**Rivale:** {row['strongest_rival']}", "",
        ])
    (OUT / "SIXTY_NINTH_COMPLETE_TEN_PAGE_WORKING_EDITION.md").write_text("\n".join(edition).rstrip() + "\n", encoding="utf-8")

    one_page = """# Einseitige aktuelle Arbeitstheorie

Das Manuskriptstück wird als lernbares Werkstattsystem gelesen: eine kleine
produktive Karten- und Klauselgrammatik steht neben einem größeren Bestand
gelernter Fachkarten und lokaler Tabellenetiketten. Mehrere Hände dürfen
Allographe wählen, müssen aber Kartenfolge, Grad, Adresse und Schluss erhalten.

Die Prosagrammatik hat zwölf Klauselformen. Sie kombiniert Reihenfolge,
Handlung, Quelle/Ansatz, Menge/Stufe, Ziel, Grad, aktuellen Posten und
lizenzierte Schlusskarten. Zeilenende ist kein Satzende. Der sichtbare Besitzer
liefert den konkreten Gegenstand, den die kurze Karte auslässt.

Herbal: fünf bildbesessene Zubereitungsartikel. Führende Lesung sind Pflanzen-
fraktionen, Auszüge, Tuchgänge, Maß, Waschung, Auflage und teils innerer
Gebrauch. Keine Pflanzenart ist bestimmt.

Biological: sechs Records mit sechzehn lokalen Becken-/Stationsbesitzern.
Führende Lesung ist Bade-, Wasch- und Anwendungspraxis; Badehausbetrieb bleibt
gleichrangiger Rivale. Besitzerwechsel setzt Stoff, Ziel und Richtung zurück;
es gibt kein globales Rohrnetz.

Astro: drei selbständige Himmels-/Kalenderinstrumente mit dreizehn lokalen
Namensräumen. f67 hat zwei unverbundene Räder, f68 einen Mehrpaneel-Sternatlas,
f69 drei Rosetten und nur links 28 Plätze. Kein Start, keine Richtung und kein
f68–f69-Schlüssel werden ergänzt.

Die Oberfläche liefert Form und Bauart; das Werkstattwörterbuch liefert kurze
Kartenwerte; das Bild liefert Besitzer; das simulierte Meisterexemplar liefert
reiche Fachnomen und konkrete Zwecke. Das ist die derzeit kohärenteste
Arbeitslesung, keine historische Entzifferung.
"""
    (OUT / "SIXTY_NINTH_ONE_PAGE_WORKING_THEORY.md").write_text(one_page, encoding="utf-8")

    counts = Counter(row["register"] for row in unified)
    report = [
        "# Neunundsechzigste Werkstattfassung: konsolidierte Zehn-Seiten-Ausgabe", "",
        "## Ergebnis", "",
        "The current edition joins all 776 visible groups without collapsing their",
        "registers: 100 Herbal groups, 281 Biological groups and 395 Astro groups.",
        "Fourteen compact units and 32 desk rules are enough to teach the current",
        "reading and writing workflow.", "",
        "The strongest shared claim is architectural: mixed productive abbreviation,",
        "learned whole cards, silent visual ownership and local nomenclator lookup.",
        "The strongest content lead is practical preparation/bath/celestial reference;",
        "the practical material/bathhouse/atlas rival remains alive.", "",
        "No extra page was used; f84 and f84r remained sealed.",
    ]
    (OUT / "SIXTY_NINTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "ten_pages": len({row["page"] for row in unified}),
            "current_units": len(units),
            "dictionary_layer_entries": len(hierarchy),
            "workshop_rules": len(rules),
            "unified_groups": len(unified),
            **dict(sorted(counts.items())),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (H_GROUPS, H_UNITS, B_GROUPS, B_UNITS, A_GROUPS, A_UNITS, HIERARCHY, DESK_RULES)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
