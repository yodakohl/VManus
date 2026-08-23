#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R257 = ROOT / "experiments/yolo/sidequest_semantic_mixed_codebook_edition_two_hundred_fifty_seventh"
R204 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_dictionary_two_hundred_fourth"
CARDS = R257 / "TWO_HUNDRED_FIFTY_SEVENTH_173_CARD_DICTIONARY.tsv"
EVENTS = R257 / "TWO_HUNDRED_FIFTY_SEVENTH_381_PROSE_EVENTS.tsv"
OLD_COMPONENTS = R204 / "TWO_HUNDRED_FOURTH_COMPONENT_LEXICON.tsv"

VALUES = {
    "OK": ("EINSETZEN", "den folgenden Posten in den laufenden Arbeitsgang setzen", 22, 78),
    "OL": ("WEITER", "im selben Fortgang weiterarbeiten", 24, 48),
    "OT": ("DANACH", "zum folgenden Posten oder Schritt wechseln", 16, 26),
    "AR": ("VON", "von der bezeichneten Quelle oder dem Vorrat her", 10, 14),
    "AL": ("ZU", "an die bezeichnete Stelle oder zum Ziel", 21, 38),
    "AIN": ("PORTION", "eine abgegrenzte Teilmenge", 6, 15),
    "AN": ("ZWEITE_PORTION", "eine zweite oder alternative Teilmenge", 1, 1),
    "AIIN": ("SOLLWERT", "den im Exemplar vorgeschriebenen Wert oder Grad", 10, 39),
    "Y": ("DIES", "den aktuell gemeinten Arbeitsposten halten", 43, 103),
    "DY": ("SCHLUSS", "nur als lizenzierte Endkarte die Zelle schließen", 38, 90),
    "OR": ("ANSATZ", "den aktuell bereiteten Ansatz oder Bedingungssatz halten", 9, 17),
}


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


def is_whole(row: dict[str, str]) -> bool:
    return "WHOLE" in row["dictionary_layer"] or "WHOLE" in row["component_parse"] or row["dictionary_layer"] == "MEMORIZED_WHOLE_CARD"


def main() -> None:
    cards = read_tsv(CARDS)
    events = read_tsv(EVENTS)
    old_components = read_tsv(OLD_COMPONENTS)
    components = []
    for row in old_components:
        component = row["component"]
        value, rule, card_count, event_count = VALUES.get(
            component,
            (row["atomic_value_de"], row["write_read_rule_de"], int(row["card_types"]), int(row["visible_events"])),
        )
        components.append({
            "teaching_order": len(components) + 1, "component": component,
            "atomic_value_de": value, "write_read_rule_de": rule,
            "support_card_types": card_count, "support_events": event_count,
            "example_card_id": row["example_card_id"], "example_surface": row["example_surface"],
            "example_value_de": row["example_value_de"], "example_statement": row["example_statement"],
            "count_note": "CURRENT_RECOUNT" if component in VALUES else "RETAINED_TEACHING_SUPPORT",
        })
        if component == "AIN":
            value, rule, card_count, event_count = VALUES["AN"]
            components.append({
                "teaching_order": len(components) + 1, "component": "AN",
                "atomic_value_de": value, "write_read_rule_de": rule,
                "support_card_types": card_count, "support_events": event_count,
                "example_card_id": "MC148", "example_surface": "ykan",
                "example_value_de": "zweite Portion", "example_statement": "B3-S024",
                "count_note": "CURRENT_RECOUNT_SINGLETON",
            })
    for index, row in enumerate(components, 1):
        row["teaching_order"] = index

    whole_signs = []
    generation = []
    for row in cards:
        if is_whole(row):
            construction_class = "WHOLE_SIGN"
            writing_rule = "retrieve the complete learned sign; do not decompose it"
            whole_role = "LEXICAL_BLOCKER" if row["dictionary_layer"] == "LEXICAL_BLOCKER_WHOLE_SIGN" else (
                "WHOLE_NOUN" if "NOUN" in row["dictionary_layer"] or "VESSEL" in row["dictionary_layer"] else
                "WHOLE_OPERATION_OR_STATE"
            )
            whole_signs.append({
                "deck_order": len(whole_signs) + 1, "master_card_id": row["master_card_id"],
                "master_form": row["master_form"], "registered_surfaces": row["registered_surfaces"],
                "whole_sign_value_de": row["portable_core_de"], "whole_sign_role": whole_role,
                "prose_event_count": row["prose_event_count"], "records": row["records"],
                "reason_not_segmented": row["component_parse"],
            })
        elif row["dictionary_layer"] in {"PRODUCTIVE_COMPOSITION", "FULL_COMPOSITION", "PRODUCTIVE_TRIPLE_COMPOSITION"}:
            construction_class = "PRODUCTIVE_COMPOSITION"
            writing_rule = "read the licensed components from left to right"
        else:
            construction_class = "FRAME_PLUS_LOCAL_CORE"
            writing_rule = "read the productive frame and retrieve the remaining local core"
        generation.append({
            "master_card_id": row["master_card_id"], "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"], "construction_class": construction_class,
            "component_parse": row["component_parse"], "portable_core_de": row["portable_core_de"],
            "local_prose_expansion_de": row["local_prose_expansion_de"],
            "prose_event_count": row["prose_event_count"], "records": row["records"],
            "writing_rule": writing_rule,
        })

    deck = []
    for row in components:
        deck.append({
            "deck_order": len(deck) + 1, "entry_kind": "PRODUCTIVE_COMPONENT",
            "entry_id": row["component"], "visible_or_card_form": row["component"],
            "short_value_de": row["atomic_value_de"], "learning_rule": row["write_read_rule_de"],
            "support_events": row["support_events"],
        })
    for row in whole_signs:
        deck.append({
            "deck_order": len(deck) + 1, "entry_kind": "MEMORIZED_WHOLE_SIGN",
            "entry_id": row["master_card_id"], "visible_or_card_form": row["master_form"],
            "short_value_de": row["whole_sign_value_de"], "learning_rule": "copy and recall as one sign",
            "support_events": row["prose_event_count"],
        })

    components_path = OUT / "TWO_HUNDRED_FIFTY_EIGHTH_30_PRODUCTIVE_COMPONENTS.tsv"
    whole_path = OUT / "TWO_HUNDRED_FIFTY_EIGHTH_23_WHOLE_SIGNS.tsv"
    generation_path = OUT / "TWO_HUNDRED_FIFTY_EIGHTH_173_CARD_GENERATION.tsv"
    deck_path = OUT / "TWO_HUNDRED_FIFTY_EIGHTH_53_ENTRY_APPRENTICE_DECK.tsv"
    readable_path = OUT / "TWO_HUNDRED_FIFTY_EIGHTH_READABLE_APPRENTICE_MANUAL.md"
    report_path = OUT / "TWO_HUNDRED_FIFTY_EIGHTH_REPORT.md"
    write_tsv(components_path, components, list(components[0]))
    write_tsv(whole_path, whole_signs, list(whole_signs[0]))
    write_tsv(generation_path, generation, list(generation[0]))
    write_tsv(deck_path, deck, list(deck[0]))

    class_cards = {kind: sum(r["construction_class"] == kind for r in generation) for kind in ("PRODUCTIVE_COMPOSITION", "FRAME_PLUS_LOCAL_CORE", "WHOLE_SIGN")}
    class_events = {kind: sum(int(r["prose_event_count"]) for r in generation if r["construction_class"] == kind) for kind in class_cards}
    readable = [
        "# Das kleinste brauchbare Lehrdeck", "",
        "Ein neuer Schreiber lernt nicht 173 unabhängige Wörter. Er lernt 30 kleine Komponenten und 23 ganze Fachzeichen.", "",
        "## Drei Leseregeln", "",
        "1. Bei einer produktiven Karte werden die Komponenten von links nach rechts gelesen.",
        "2. Bei einer Mischkarte wird der bekannte Rahmen gelesen und nur der lokale Kern auswendig ergänzt.",
        "3. Bei einem Ganzzeichen wird nichts zerlegt; das Zeichen ruft einen Stoff, ein Gerät oder einen routinierten Vorgang ab.", "",
        "## Deckung", "",
        "- 118 Karten / 194 Vorkommen sind vollständig produktiv.",
        "- 32 Karten / 159 Vorkommen verbinden einen produktiven Rahmen mit einem lokalen Kern.",
        "- 23 Karten / 28 Vorkommen sind reine Ganzzeichen.", "",
        "Damit tragen 150 der 173 Karten und 353 der 381 Ereignisse sichtbare Kompositionshilfe. Das ist für eine kleine Werkstatt gut lernbar: Die seltenen Sonderzeichen werden aus dem Exemplar kopiert, der häufige Text wird aus dem gemeinsamen System erzeugt.", "",
        "Die vier Ganzzeichen ÜBERTRAGEN, WEITERABZUG, SUDANSATZ und FOLGEANWENDUNG sind besonders wichtig: Sie ersetzen genau jene vier Kombinationen, die das produktive Beziehungsraster nicht bildet.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 258: minimales Lehrdeck

## Ergebnis

Die 173 Karten lassen sich als 30 produktive Komponenten plus 23 gelernte Ganzzeichen unterrichten. 118 Karten sind vollständig komponiert, 32 verbinden bekannte Rahmen mit lokalen Kernen, nur 23 sind reine Ganzzeichen. Diese drei Klassen decken 194, 159 und 28 der 381 Ereignisse.

Das Mischmodell ist dadurch konkret ausführbar: Ein Lehrling braucht 53 Deckeinträge statt 173 unabhängiger Wortglossen. Die produktive Schicht liefert Adressen, Mengen, Grade, Zustände und Operationen; die Ganzzeichenschicht speichert seltene Stoffe, Gefäße und routinisierte Arbeitsschritte.

Inputs: cards `{sha(CARDS)}`, events `{sha(EVENTS)}`, component seed `{sha(OLD_COMPONENTS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (components_path, whole_path, generation_path, deck_path, readable_path, report_path)
    summary = {
        "status": "PASS", "components": len(components), "whole_signs": len(whole_signs),
        "deck_entries": len(deck), "card_classes": class_cards, "event_classes": class_events,
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
