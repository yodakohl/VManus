#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R101 = ROOT / "experiments/yolo/sidequest_semantic_atomic_defaults_hundred_first_edition"
R99 = ROOT / "experiments/yolo/sidequest_semantic_renderer_inventory_ninety_ninth_edition"
R104 = ROOT / "experiments/yolo/sidequest_semantic_component_ecology_hundred_fourth_edition"
R107 = ROOT / "experiments/yolo/sidequest_semantic_creative_owner_resolution_hundred_seventh_edition"
R109 = ROOT / "experiments/yolo/sidequest_semantic_bath_service_choice_hundred_ninth_edition"
R100 = ROOT / "experiments/yolo/sidequest_semantic_centennial_working_edition"


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    atoms = load(R101 / "HUNDRED_FIRST_44_ATOMIC_COMPONENTS.tsv")
    ecology = {r["atom"]: r for r in load(R104 / "HUNDRED_FOURTH_44_COMPONENT_ECOLOGY.tsv")}
    atom_rows = []
    for row in atoms:
        e = ecology[row["atom"]]
        atom_rows.append({
            "atom": row["atom"],
            "short_value_de": row["atomic_default_de"],
            "word_class": row["word_class"],
            "ecology": e["ecology_status"],
            "total_occurrences": e["total_atom_occurrences"],
            "herbal_occurrences": e["herbal_occurrences"],
            "biological_occurrences": e["biological_occurrences"],
            "teaching_rule": e["apprentice_use"],
        })
    write_tsv("HUNDRED_TENTH_44_ATOM_POCKET.tsv", atom_rows)

    cards = load(R101 / "HUNDRED_FIRST_173_ATOMIC_DICTIONARY.tsv")
    events = load(R101 / "HUNDRED_FIRST_381_EVENT_ATOMIC_INTERLINEAR.tsv")
    surfaces = load(R99 / "NINETY_NINTH_230_SURFACE_COVERAGE.tsv")
    by_card_events = defaultdict(list)
    by_card_surfaces = defaultdict(list)
    for row in events:
        by_card_events[row["master_card_id"]].append(row)
    for row in surfaces:
        by_card_surfaces[row["master_card_id"]].append(row)
    core = {r["atom"] for r in atom_rows if r["ecology"] == "PORTABLE_WORKSHOP_CORE"}
    bridge = {r["atom"] for r in atom_rows if r["ecology"] == "THIN_CROSS_SECTION_BRIDGE"}
    card_rows = []
    for row in cards:
        atom_set = set(row["semantic_atoms"].split("+"))
        if atom_set <= core:
            tier = "CORE_CARD"
        elif atom_set <= core | bridge:
            tier = "BRIDGE_CARD"
        else:
            tier = "SPECIALIST_OR_LEARNED_CARD"
        ev = by_card_events[row["master_card_id"]]
        sr = by_card_surfaces[row["master_card_id"]]
        card_rows.append({
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "all_registered_surfaces": "|".join(r["visible_surface"] for r in sr),
            "semantic_atoms": row["semantic_atoms"],
            "short_default_de": row["atomic_default_de"],
            "teaching_tier": tier,
            "productivity_tier": row["productivity_tier"],
            "event_count": str(len(ev)),
            "records": "|".join(sorted({r["record_unit_id"] for r in ev})),
            "pages": "|".join(sorted({r["page"] for r in ev})),
        })
    write_tsv("HUNDRED_TENTH_173_CARD_POCKET.tsv", card_rows)

    card_map = {r["master_card_id"]: r for r in card_rows}
    surface_rows = []
    for row in surfaces:
        card = card_map[row["master_card_id"]]
        surface_rows.append({
            "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"],
            "master_form": card["master_form"],
            "renderer_gesture": row["renderer_gesture"],
            "family_class": row["family_class"],
            "semantic_atoms": card["semantic_atoms"],
            "short_default_de": card["short_default_de"],
        })
    write_tsv("HUNDRED_TENTH_230_SURFACE_INDEX.tsv", surface_rows)

    owner_statements = {r["statement_id"]: r for r in load(R107 / "HUNDRED_SEVENTH_116_OWNER_RESOLVED_STATEMENTS.tsv")}
    hybrid = {r["statement_id"]: r for r in load(R109 / "HUNDRED_NINTH_56_BATH_VS_SERVICE_CHOICES.tsv")}
    source_statements = load(R100 / "HUNDREDTH_116_STATEMENT_TRANSLATION.tsv")
    statement_rows = []
    for row in source_statements:
        owner = owner_statements[row["statement_id"]]
        if row["statement_id"] in hybrid:
            selected = hybrid[row["statement_id"]]["selected_reading_de"]
            layer = hybrid[row["statement_id"]]["selected_local_role"]
        else:
            selected = row["concrete_source_expansion_de"]
            layer = "HERBAL_OR_OTHER_BIO_CURRENT_READING"
        statement_rows.append({
            "statement_order": row["statement_order"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "visible_surface_sequence": row["visible_surface_sequence"],
            "semantic_atom_program": row["semantic_atom_program"],
            "owner_expanded_literal_statement_de": owner["owner_expanded_literal_statement_de"],
            "selected_content_layer": layer,
            "current_reading_de": selected,
        })
    write_tsv("HUNDRED_TENTH_116_CURRENT_STATEMENTS.tsv", statement_rows)

    tiers = Counter(r["teaching_tier"] for r in card_rows)
    handbook = """# Einblatt-Handbuch der Zehnerseiten-Werkstatt

## Was das System ist

Ein Bild- und Tabellenregister aus 173 gelernten Karten. Die Karten können aus
kurzen Bedeutungsbausteinen zusammengesetzt sein, bleiben aber als Ganzformen
registriert. 230 sichtbare Schreibformen gehören zu diesen Karten; q-, sh-, s-,
ch-, d- und t-Antritte sind zugelassene Schreiberformen, keine neuen Wörter.

## So liest der Schreiber

1. Bestimme zuerst Bild, Station, Record oder Diagrammplatz als stillen Besitzer.
2. Lies immer die längste registrierte Karte; zerlege keine bekannte Ganzkarte neu.
3. Führe die sichtbare Form über die Allographentafel auf ihre Masterkarte zurück.
4. Lies ihre kurzen Atome, nicht die alte flüssige Satzglosse.
5. Quelle, Maß, Stufe, Ziel und Posten binden rückwärts an den Arbeitsgang.
6. Ein dazwischenstehender Stoff- oder Zustandswert bindet vorwärts an den nächsten Arbeitsgang.
7. Fehlende Hauptnomen kommen vom Bildbesitzer oder vom laufenden Stationsregister.
8. E / EE / EEE bedeuten kurz / länger / vollständig nur in lizenzierten Familien.
9. Y hält den aktuellen Posten; Schluss ist eine registrierte Endkonstruktion, nicht jedes sichtbare -dy.
10. Eine physische Zeile beendet keinen Satz. Bildlücken dagegen löschen Stoff, Ziel und Richtung.
11. Biological: Randgefäße bereiten und warten; figurenbezogene Becken wenden an.
12. Astro: jeden Ring, Sternplatz oder Sektor aus seinem lokalen Exemplar kopieren; keine Prosa-Wörter importieren.

## Aktuelle Inhaltslesung

Herbal sind fünf bildbesitzergesteuerte Pflanzen- und Zubereitungsartikel.
Biological ist ein therapeutischer Badebetrieb mit eigener Zubereitung und
Wartung: 35 Service-/Zubereitungsaussagen und 21 Körper-/Badeaussagen. Astro
besteht aus drei unabhängigen lokalen Himmelsinstrumenten ohne gemeinsamen Key.

## Merksatz

**Bild nennt das Ding; Karte nennt den kurzen Arbeitswert; Stellung nennt die
Bindung; Masterexemplar nennt seltene Werte; Schreiberhand ändert nur die Form.**
"""
    (OUT / "HUNDRED_TENTH_ONE_PAGE_SCRIBE_HANDBOOK.md").write_text(handbook, encoding="utf-8")
    report = [
        "# Hundertzehnte Runde: post-centenniales Taschenbuch", "",
        "R101 bis R109 sind jetzt in einer einzigen kompakten Arbeitsbasis zusammengeführt:",
        "44 atomare Werte, 173 Masterkarten, 230 sichtbare Formen und 116 aktuelle Aussagen.", "",
        f"Kartenschichtung: {tiers['CORE_CARD']} Core-Karten, {tiers['BRIDGE_CARD']} Brückenkarten und",
        f"{tiers['SPECIALIST_OR_LEARNED_CARD']} Spezial-/Lernkarten. Die Kartenbedeutung bleibt atomar;",
        "nur die Satzfassung erhält Besitzer- und Inhaltsnomen.", "",
        "Die wichtigste redaktionelle Änderung ist die neue Biological-Lesung aus R107–R109. Die alte",
        "pauschale Stationspräambel ist ersetzt. Jede Aussage nennt nun ihren lokalen Besitzer und wird",
        "als Zubereitung/Service oder Körper-/Badeanwendung geführt.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_TENTH_POST_CENTENNIAL_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE", "atoms": len(atom_rows), "cards": len(card_rows),
        "surfaces": len(surface_rows), "statements": len(statement_rows), "card_tiers": dict(tiers),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
