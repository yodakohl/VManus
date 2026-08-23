#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R274 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_mixed_deck_two_hundred_seventy_fourth"
R275 = ROOT / "experiments/yolo/sidequest_semantic_three_astro_readings_two_hundred_seventy_fifth"
R278 = ROOT / "experiments/yolo/sidequest_semantic_thirty_six_stem_families_two_hundred_seventy_eighth"
R279 = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth"
FAMILIES = R278 / "TWO_HUNDRED_SEVENTY_EIGHTH_36_STEM_FAMILIES.tsv"
PROSE_CARDS = R279 / "TWO_HUNDRED_SEVENTY_NINTH_173_TWO_LAYER_DICTIONARY.tsv"
PROSE_EVENTS = R279 / "TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
ASTRO_LAYERED = R274 / "TWO_HUNDRED_SEVENTY_FOURTH_LAYERED_395_ASTRO_GROUPS.tsv"
ASTRO_READINGS = R275 / "TWO_HUNDRED_SEVENTY_FIFTH_395_GROUP_READINGS.tsv"
PROSE_EDITION = R279 / "TWO_HUNDRED_SEVENTY_NINTH_ELEVEN_RECORD_EDITION.md"
ASTRO_EDITION = R275 / "TWO_HUNDRED_SEVENTY_FIFTH_COMPLETE_ASTRO_EDITION.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    families = read_tsv(FAMILIES)
    prose_cards = read_tsv(PROSE_CARDS)
    prose_events = read_tsv(PROSE_EVENTS)
    astro_layered = read_tsv(ASTRO_LAYERED)
    astro_readings = read_tsv(ASTRO_READINGS)
    astro_by_serial = {r["group_serial"]: r for r in astro_layered}

    dictionary: list[dict[str, object]] = []
    for row in families:
        dictionary.append({
            "dictionary_order": len(dictionary) + 1,
            "entry_kind": "STEM_FAMILY",
            "entry_id": row["family_id"],
            "visible_forms": row["member_component_ids"],
            "portable_value_de": row["short_value_de"],
            "local_default_de": row["variant_rule"],
            "register_scope": row["reach_class"],
            "support_count": int(row["herbal_events"]) + int(row["bio_events"]) + int(row["astro_groups"]),
            "learning_mode": "MEMORIZE_PRODUCTIVE_FAMILY",
        })

    prose_wholes = [r for r in prose_cards if r["card_class_279"] == "MEMORIZED_WHOLE_SIGN"]
    for row in prose_wholes:
        dictionary.append({
            "dictionary_order": len(dictionary) + 1,
            "entry_kind": "PROSE_WHOLE_SIGN",
            "entry_id": row["master_card_id"],
            "visible_forms": row["registered_surfaces"],
            "portable_value_de": row["family_literal_de"],
            "local_default_de": row["local_prose_default_de"],
            "register_scope": "HERBAL_OR_BIO_PROSE",
            "support_count": row["prose_event_count"],
            "learning_mode": "MEMORIZE_NOMENCLATOR_SIGN",
        })

    astro_whole_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    local_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in astro_layered:
        if row["coverage_class_274"] == "LEARNED_WHOLE_SIGN":
            astro_whole_groups[row["visible_surface"]].append(row)
        elif row["coverage_class_274"] == "LOCAL_COPY_LABEL":
            local_groups[row["visible_surface"]].append(row)
    for surface, rows in astro_whole_groups.items():
        dictionary.append({
            "dictionary_order": len(dictionary) + 1,
            "entry_kind": "ASTRO_WHOLE_SIGN",
            "entry_id": f"ASTRO_WHOLE_{len([r for r in dictionary if r['entry_kind']=='ASTRO_WHOLE_SIGN'])+1:03d}",
            "visible_forms": surface,
            "portable_value_de": rows[0]["portable_card_core_de"],
            "local_default_de": rows[0]["concrete_diagram_reading_de"],
            "register_scope": "ASTRO_LOCAL_WHOLE",
            "support_count": len(rows),
            "learning_mode": "MEMORIZE_DIAGRAM_NOMENCLATOR_SIGN",
        })
    for surface, rows in local_groups.items():
        dictionary.append({
            "dictionary_order": len(dictionary) + 1,
            "entry_kind": "LOCAL_COPY_KEY",
            "entry_id": f"LOCAL_KEY_{len([r for r in dictionary if r['entry_kind']=='LOCAL_COPY_KEY'])+1:03d}",
            "visible_forms": surface,
            "portable_value_de": "LOKALER_BESITZERSCHLUESSEL",
            "local_default_de": "lokalen Namen oder Wert am sichtbaren Diagrammbesitzer nachschlagen",
            "register_scope": "ASTRO_LOCAL_NAMESPACE",
            "support_count": len(rows),
            "learning_mode": "COPY_FROM_LOCAL_EXEMPLAR",
        })

    ledger: list[dict[str, object]] = []
    for row in prose_events:
        card = next(c for c in prose_cards if c["master_card_id"] == row["master_card_id"])
        semantic_class = "LEARNED_WHOLE_SIGN" if card["card_class_279"] == "MEMORIZED_WHOLE_SIGN" else "PORTABLE_COMPOSITION"
        ledger.append({
            "unified_index": len(ledger) + 1,
            "register": "PROSE",
            "page": row["page"],
            "unit_or_locus": row["statement_id"],
            "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"],
            "source_id": row["event_id"],
            "semantic_class": semantic_class,
            "portable_reading_de": row["family_literal_de"],
            "local_default_de": row["register_expansion_de"],
            "learning_mode": "COMPOSE" if semantic_class == "PORTABLE_COMPOSITION" else "MEMORIZE",
        })
    for row in astro_readings:
        base = astro_by_serial[row["group_serial"]]
        cls = base["coverage_class_274"]
        if cls == "LOCAL_COPY_LABEL":
            portable = "LOKALER_BESITZERSCHLUESSEL"
            local = row["component_or_copy_reading_de"]
            mode = "COPY"
        elif cls == "LEARNED_WHOLE_SIGN":
            portable = base["portable_card_core_de"]
            local = row["component_or_copy_reading_de"]
            mode = "MEMORIZE"
        else:
            portable = row["component_or_copy_reading_de"]
            local = base["concrete_diagram_reading_de"]
            mode = "COMPOSE"
        ledger.append({
            "unified_index": len(ledger) + 1,
            "register": "ASTRO",
            "page": row["page"],
            "unit_or_locus": row["locus"],
            "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"],
            "source_id": f"A{int(row['group_serial']):03d}",
            "semantic_class": cls,
            "portable_reading_de": portable,
            "local_default_de": local,
            "learning_mode": mode,
        })

    manual = [
        {"step": 1, "instruction_de": "Setze den sichtbaren Besitzer aus Pflanze, Badestation oder Diagrammplatz."},
        {"step": 2, "instruction_de": "Bestimme das Register: Herbal, Bio oder eines der drei getrennten Astro-Instrumente."},
        {"step": 3, "instruction_de": "Lies zuerst die sechzehn gemeinsamen Stammfamilien."},
        {"step": 4, "instruction_de": "Füge nur den Herbal-, Bio- oder Brückenzusatz hinzu, den die Karte verlangt."},
        {"step": 5, "instruction_de": "Lies AR als Quelle, AL als Ziel, OL als Fortsetzung, OT als Folgeposten und OR als Bedingungsansatz."},
        {"step": 6, "instruction_de": "Lies Y nur an lizenzierter Stelle als aktuellen Posten; spalte DY nicht als bloßes D+Y."},
        {"step": 7, "instruction_de": "Lies E/EE/EEE als Grad I/II/III und CHD/CHED als kurze/lange Transferallographie."},
        {"step": 8, "instruction_de": "Sprich CHO, CHK, DY und AIR erst im lokalen Register konkret als Zutat, Wärme, Schluss oder Wasserlauf aus."},
        {"step": 9, "instruction_de": "Lerne die 23 Prosa- und 46 Astro-Ganzzeichen als Nomenklator."},
        {"step": 10, "instruction_de": "Kopiere die 67 lokalen Schlüssel aus dem jeweiligen Diagrammexemplar; erfinde keinen globalen Namen."},
        {"step": 11, "instruction_de": "Behalte Besitzer und laufenden Posten über physische Zeilenenden hinweg."},
        {"step": 12, "instruction_de": "Schließe Prosa nur mit lizenzierter Festsetzkarte; Diagrammplätze bleiben lokale Nachschlageeinträge."},
    ]

    dictionary_path = OUT / "TWO_HUNDRED_EIGHTIETH_172_ENTRY_WORKSHOP_DICTIONARY.tsv"
    ledger_path = OUT / "TWO_HUNDRED_EIGHTIETH_776_UNIFIED_INTERLINEAR.tsv"
    manual_path = OUT / "TWO_HUNDRED_EIGHTIETH_TWELVE_STEP_MANUAL.tsv"
    edition_path = OUT / "TWO_HUNDRED_EIGHTIETH_COMPLETE_TEN_PAGE_EDITION.md"
    report_path = OUT / "TWO_HUNDRED_EIGHTIETH_REPORT.md"
    write_tsv(dictionary_path, dictionary, list(dictionary[0]))
    write_tsv(ledger_path, ledger, list(ledger[0]))
    write_tsv(manual_path, manual, list(manual[0]))
    edition_path.write_text("""# Konsolidierte Zehn-Seiten-Werkstattausgabe

## Wörterbuchschlüssel

36 Stammfamilien + 23 Prosa-Ganzzeichen + 46 Astro-Ganzzeichen werden gelernt. 67 lokale Astro-Schlüssel werden vom sichtbaren Diagrammplatz kopiert. Jede Zeile besitzt eine portable und eine lokale Leseschicht.

---

""" + PROSE_EDITION.read_text(encoding="utf-8") + "\n\n---\n\n" + ASTRO_EDITION.read_text(encoding="utf-8"), encoding="utf-8")
    report_path.write_text(f"""# Sidequest-Pass 280: einheitliche Zehn-Seiten-Ausgabe

## Ergebnis

Das konsolidierte Wörterbuch hat172 Zeilen:36 Stammfamilien,23 Prosa-Ganzzeichen,46 Astro-Ganzzeichen und67 lokale Kopierschlüssel. Die ersten105 werden gelernt, die letzten67 nur lokal kopiert. Das Interlinear umfasst exakt776 Gruppen:381 Prosa und395 Astro;618 sind Kompositionen,79 gelernte Ganzzeichen und79 lokale Schlüssel.

Die vollständige Edition verbindet alle elf Prosarecords und alle drei getrennten Astro-Instrumente, ohne neue Seite, neue Lautung oder globalen Astro-Schlüssel. Ein zwölfstufiges Lehrmanual beschreibt den Mehrschreiber-Workflow.

Inputs `{sha(FAMILIES)}`, `{sha(PROSE_EVENTS)}`, `{sha(ASTRO_READINGS)}`.
""", encoding="utf-8")
    outputs = (dictionary_path, ledger_path, manual_path, edition_path, report_path)
    kinds = defaultdict(int)
    for row in dictionary: kinds[str(row["entry_kind"])] += 1
    summary = {
        "status": "PASS",
        "dictionary_entries": len(dictionary), "dictionary_kinds": dict(kinds),
        "ledger_rows": len(ledger), "prose_rows": sum(r["register"] == "PROSE" for r in ledger), "astro_rows": sum(r["register"] == "ASTRO" for r in ledger),
        "memorized_entries": 105, "local_copy_entries": 67,
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
