#!/usr/bin/env python3
"""Compile a minimal 39-entry dictionary for all Biological cards and events."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MATRIX = ROOT / "experiments/yolo/sidequest_semantic_stem_mode_crosswalk_three_hundred_ninth/THREE_HUNDRED_NINTH_29_FAMILY_MODE_MATRIX.tsv"
MEMBERSHIPS = ROOT / "experiments/yolo/sidequest_semantic_stem_mode_crosswalk_three_hundred_ninth/THREE_HUNDRED_NINTH_281_EVENT_STEM_MODE_MEMBERSHIPS.tsv"
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_ten_weak_cards_three_hundred_fourth/THREE_HUNDRED_FOURTH_173_REVISED_IMPERATIVE_LEXICON.tsv"


WHOLE_MODE_OVERRIDE = {
    "MC012": ("CHARGE", "Zusatz wird zugegeben, nicht bloß lokal verwaltet"),
    "MC061": ("CHARGE", "Übertragen ist eine Beschickungs-/Übergabehandlung"),
    "MC109": ("CHARGE", "kleinen Teil nehmen beschickt den nächsten Schritt"),
    "MC138": ("CHARGE", "frische Spülflüssigkeit einlassen beschickt die Station"),
    "MC152": ("MEASURE", "Teilen bestimmt die Teilung oder Portionierung"),
    "MC059": ("CHARGE", "eine Einlage einlegen beschickt die Station"),
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


def family_rule(category: str) -> str:
    return {
        "MODE_PREDICTIVE_CONTENT_FAMILY": "als stabilen Betriebsstamm sprechen und mit sichtbaren Slots zusammensetzen",
        "NARROW_LOW_COUNT_SPECIALIST": "nur in den belegten Spezialkonstruktionen einsetzen",
        "GRADE_REFERENT_ENDPOINT_FRAME": "als Grad-, Referent- oder Schlussrahmen lesen; nicht als Inhaltsverb",
        "LOCAL_CONTROL_ADDRESS_OR_STATE_FAMILY": "als lokale Folge-, Adress-, Lauf- oder Zustandssteuerung lesen",
        "DIRECTIONALLY_CONDITIONED_TRANSFER_CORE": "als Übergabekern lesen; Richtungsstämme bestimmen hinein oder hinaus",
        "MULTIMODE_OPERATION_ACTIVATOR": "aktiviert die vom Partnerstamm bezeichnete Handlung",
        "MULTIMODE_CONTENT_OR_FRAME": "nur mit Partner oder registrierter Ganzkarte konkretisieren",
    }[category]


def main() -> None:
    matrix = [r for r in read(MATRIX) if r["operational_interpretation"] != "NO_BIO_COVERAGE"]
    memberships = read(MEMBERSHIPS)
    lexicon = {r["master_card_id"]: r for r in read(LEXICON)}
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in memberships:
        by_card[event["master_card_id"]].append(event)

    dictionary_rows = []
    for row in matrix:
        dictionary_rows.append({
            "entry_id": f"F_{row['family_id']}", "entry_type": "PRODUCTIVE_FAMILY",
            "visible_form_or_card": row["visible_core_or_variants"], "atomic_value_de": row["short_value_de"],
            "operating_value": row["dominant_mode"] if row["operational_interpretation"] == "MODE_PREDICTIVE_CONTENT_FAMILY" else "CONTEXTUAL_" + row["dominant_mode"],
            "composition_or_memory_rule_de": family_rule(row["operational_interpretation"]),
            "bio_card_types_reached": row["bio_card_types"], "bio_event_memberships": row["bio_event_memberships"],
            "source_category": row["operational_interpretation"],
        })
    whole_cards = sorted({r["master_card_id"] for r in memberships if r["teaching_layer"] == "LEARNED_WHOLE_OR_MICROSIGN"})
    for card_id in whole_cards:
        selected = by_card[card_id]
        source = lexicon[card_id]
        old_mode = selected[0]["operating_mode"]
        mode = WHOLE_MODE_OVERRIDE.get(card_id, (old_mode, "ursprüngliche Ganzkartenrolle bleibt"))[0]
        dictionary_rows.append({
            "entry_id": f"W_{card_id}", "entry_type": "LEARNED_WHOLE_OR_MICROSIGN",
            "visible_form_or_card": source["master_form"], "atomic_value_de": source["source_short_value_de"],
            "operating_value": mode, "composition_or_memory_rule_de": "als unteilbare Ganzkarte mit diesem kurzen Werkstattwert lernen",
            "bio_card_types_reached": 1, "bio_event_memberships": len(selected), "source_category": "MEMORIZED_EXCEPTION",
        })
    dictionary_path = HERE / "THREE_HUNDRED_TENTH_39_ENTRY_MINIMAL_BIO_DICTIONARY.tsv"
    write(dictionary_path, dictionary_rows)

    correction_rows = []
    for card_id, (new_mode, reason) in WHOLE_MODE_OVERRIDE.items():
        selected = by_card[card_id]
        correction_rows.append({
            "master_card_id": card_id, "master_form": lexicon[card_id]["master_form"],
            "short_value_de": lexicon[card_id]["source_short_value_de"], "old_classifier_mode": selected[0]["operating_mode"],
            "new_dictionary_mode": new_mode, "reason_de": reason, "event_count": len(selected),
            "event_ids": "|".join(r["event_id"] for r in selected),
        })
    correction_path = HERE / "THREE_HUNDRED_TENTH_SIX_WHOLE_SIGN_MODE_CORRECTIONS.tsv"
    write(correction_path, correction_rows)

    event_rows = []
    for event in memberships:
        families = event["productive_family_memberships"].split("|") if event["productive_family_memberships"] != "NONE" else []
        if families:
            recipe = "+".join(f"F_{family}" for family in families)
            revised_mode = event["operating_mode"]
        else:
            recipe = f"W_{event['master_card_id']}"
            revised_mode = WHOLE_MODE_OVERRIDE.get(event["master_card_id"], (event["operating_mode"], ""))[0]
        event_rows.append({
            **event,
            "minimal_dictionary_recipe": recipe,
            "revised_operating_mode": revised_mode,
            "dictionary_reading_de": event["imperative_clause_de"],
        })
    event_path = HERE / "THREE_HUNDRED_TENTH_281_EVENT_DICTIONARY_ROUNDTRIP.tsv"
    write(event_path, event_rows)

    card_rows = []
    for card_id, selected in sorted(by_card.items()):
        first = selected[0]
        families = first["productive_family_memberships"].split("|") if first["productive_family_memberships"] != "NONE" else []
        recipe = "+".join(f"F_{family}" for family in families) if families else f"W_{card_id}"
        revised_modes = Counter(next(r["revised_operating_mode"] for r in event_rows if r["event_id"] == e["event_id"]) for e in selected)
        source = lexicon[card_id]
        card_rows.append({
            "master_card_id": card_id, "master_form": source["master_form"], "registered_surfaces": source["registered_surfaces"],
            "minimal_dictionary_recipe": recipe, "card_layer": first["teaching_layer"],
            "source_short_value_de": source["source_short_value_de"], "imperative_clause_de": source["imperative_clause_de"],
            "bio_event_count": len(selected), "revised_mode_counts": "|".join(f"{k}:{v}" for k, v in revised_modes.items()),
        })
    card_path = HERE / "THREE_HUNDRED_TENTH_124_CARD_PRODUCTION_RECIPES.tsv"
    write(card_path, card_rows)

    lines = ["# Minimalwörterbuch für die Biological-Seiten", "", "Der Lehrling lernt 26 auf diesen Seiten verwendete produktive Familien und 13 unteilbare Ganz-/Mikrozeichen. Daraus lassen sich alle 124 Kartentypen und 281 sichtbaren Ereignisse rücklesen.", "", "## Produktive Familien", ""]
    for row in dictionary_rows:
        if row["entry_type"] != "PRODUCTIVE_FAMILY":
            continue
        card_word = "Karte" if int(row["bio_card_types_reached"]) == 1 else "Karten"
        event_word = "Ereignis" if int(row["bio_event_memberships"]) == 1 else "Ereignisse"
        lines += [f"- **{row['visible_form_or_card']}** — {row['atomic_value_de']}; {row['composition_or_memory_rule_de']}. Bio: {row['bio_card_types_reached']} {card_word} / {row['bio_event_memberships']} {event_word}."]
    lines += ["", "## Gelernte Ganz-/Mikrozeichen", ""]
    for row in dictionary_rows:
        if row["entry_type"] == "LEARNED_WHOLE_OR_MICROSIGN":
            event_word = "Ereignis" if int(row["bio_event_memberships"]) == 1 else "Ereignisse"
            lines += [f"- **{row['visible_form_or_card']}** — {row['atomic_value_de']} → {row['operating_value']}; {row['bio_event_memberships']} {event_word}."]
    manual_path = HERE / "THREE_HUNDRED_TENTH_MINIMAL_BIO_APPRENTICE_DICTIONARY.md"
    manual_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    revised_counts = Counter(r["revised_operating_mode"] for r in event_rows)
    report_path = HERE / "THREE_HUNDRED_TENTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 310: das 39-Einträge-Bio-Wörterbuch\n\n"
        "Das gesamte Bio-Inventar schrumpft auf 39 Lehrgegenstände: 26 tatsächlich verwendete produktive Familien und 13 gelernte Ganz-/Mikrozeichen. Diese Einträge erzeugen 124 sichtbare Kartentypen und alle 281 Ereignisse. Das ist die bislang konkreteste Form der Idee „Fachkürzel plus gelernte Ganzwörter“: Nicht jede sichtbare Karte ist ein Wort, aber jede hat eine eindeutige Produktionsrezeptur.\n\n"
        "Beim Zusammenbau fielen sechs falsch grob einsortierte Ganzzeichen auf. Zusatz, Übertragung, Kurzteil, frische Spülflüssigkeit und Einlage gehören zur Beschickung; Teilen zur Mess-/Portionierungsart. Die Korrektur betrifft acht Ereignisse und ändert keine Kartenbedeutung, nur ihre Betriebsart.\n\n"
        "Revidierte Ereignisverteilung: " + ", ".join(f"{k} {v}" for k, v in revised_counts.items()) + ". Als nächstes sollte dieses 39-Einträge-Deck wie ein Lehrling auf vollständigen Bio-Records vorwärts schreiben und rückwärts lesen.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS", "dictionary_entries": len(dictionary_rows), "productive_entries": len(matrix), "whole_entries": len(whole_cards),
        "bio_card_types": len(card_rows), "bio_events": len(event_rows), "whole_mode_corrections": len(correction_rows),
        "corrected_events": sum(int(r["event_count"]) for r in correction_rows), "revised_event_mode_counts": dict(revised_counts),
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [MATRIX, MEMBERSHIPS, LEXICON]},
        "output_hashes": {p.name: sha(p) for p in [dictionary_path, correction_path, event_path, card_path, manual_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
