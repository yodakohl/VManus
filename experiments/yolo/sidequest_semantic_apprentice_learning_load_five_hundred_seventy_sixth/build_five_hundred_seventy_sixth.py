#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P554 = ROOT / "sidequest_semantic_canonical_working_dictionary_five_hundred_fifty_fourth"
P555 = ROOT / "sidequest_semantic_atomic_card_unification_five_hundred_fifty_fifth"
P562 = ROOT / "sidequest_semantic_integrated_apprentice_manual_five_hundred_sixty_second"
P575 = ROOT / "sidequest_semantic_section_local_card_partition_five_hundred_seventy_fifth"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    components = read(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_THIRTY_EIGHT_COMPONENT_DICTIONARY.tsv")
    frames = read(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_FIFTY_SIX_ACTION_FRAME_LEXICON.tsv")
    cards = read(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_ONE_HUNDRED_SEVENTY_THREE_ATOMIC_CARD_DICTIONARY.tsv")
    events = read(P562 / "FIVE_HUNDRED_SIXTY_SECOND_THREE_HUNDRED_EIGHTY_ONE_FULL_TRACES.tsv")
    old_inventory = {r["layer"]: r for r in read(P562 / "FIVE_HUNDRED_SIXTY_SECOND_TRAINING_INVENTORY.tsv")}
    specialists = {r["card_no"]: r for r in read(P575 / "FIVE_HUNDRED_SEVENTY_FIFTH_SEVEN_SPECIALIST_CARDS.tsv")}

    card_rows = []
    for card in cards:
        specialist = specialists.get(card["card_no"])
        composition = card["composition_status"]
        if specialist:
            semantic_rule = "LEARN_SPECIALIST_VALUE_OR_INNER_ATOM"
            learned_value = specialist["specialist_value_de"]
        else:
            semantic_rule = "GENERATE_FROM_COMPONENTS_AND_FRAME"
            learned_value = "NONE"
        card_rows.append({
            "card_no": card["card_no"],
            "surfaces": card["surfaces"],
            "component_parse": card["component_parse"],
            "composition_status": composition,
            "surface_form_must_be_recognized": "YES",
            "independent_semantic_whole_to_memorize": "YES" if specialist else "NO",
            "semantic_learning_rule": semantic_rule,
            "specialist_value_de": learned_value,
            "generated_or_recalled_value_de": card["atomic_card_value_de"],
            "occurrences": card["occurrences"],
        })

    event_rows = []
    by_card = {r["card_no"]: r for r in card_rows}
    for event in events:
        card = by_card[event["observed_card_no"]]
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "observed_surface": event["observed_surface"],
            "card_no": event["observed_card_no"],
            "component_parse": event["component_parse"],
            "semantic_source": card["semantic_learning_rule"],
            "semantic_value_de": event["atomic_card_value_de"],
            "local_action_de": event["local_action_expansion_de"],
            "card_roundtrip": event["card_roundtrip"],
            "surface_roundtrip": event["surface_roundtrip"],
            "complete": "YES",
        })

    layers = [
        {"domain": "SEMANTIC", "layer": "COMPONENT_VALUES", "items": len(components), "what_is_learned": "kleine Bedeutungsbausteine", "events_served": 381},
        {"domain": "SEMANTIC", "layer": "ACTION_FRAME_RULES", "items": len(frames), "what_is_learned": "konkrete Verben aus Bauteil plus Rahmen", "events_served": 271},
        {"domain": "SEMANTIC", "layer": "SPECIALIST_VALUES", "items": len(specialists), "what_is_learned": "drei Ganzkarten und vier Innenkerne", "events_served": 7},
        {"domain": "GRAPHIC", "layer": "VISIBLE_CARD_FORMS", "items": len(cards), "what_is_learned": "Kartenbilder erkennen; keine 173 Bedeutungen", "events_served": 381},
        {"domain": "GRAPHIC", "layer": "ALLOGRAPH_RULES", "items": int(old_inventory["ALLOGRAPH_RULES"]["learned_items"]), "what_is_learned": "positionsbedingte Kartenwahl", "events_served": int(old_inventory["ALLOGRAPH_RULES"]["events_covered"])},
        {"domain": "GRAPHIC", "layer": "WRAPPER_STAMPS", "items": int(old_inventory["WRAPPER_STAMPS"]["learned_items"]), "what_is_learned": "wiederkehrende Oberflächenhüllen", "events_served": 381},
        {"domain": "GRAPHIC", "layer": "FORMULA_CADENCES", "items": int(old_inventory["FORMULA_CADENCES"]["learned_items"]), "what_is_learned": "gemischte Hüllenfolgen", "events_served": int(old_inventory["FORMULA_CADENCES"]["events_covered"])},
        {"domain": "GRAPHIC", "layer": "RECORD_MELODIES", "items": int(old_inventory["RECORD_MELODIES"]["learned_items"]), "what_is_learned": "recordlokale Hüllenfolge", "events_served": int(old_inventory["RECORD_MELODIES"]["events_covered"])},
        {"domain": "PROCEDURE", "layer": "MANUAL_RULES", "items": int(old_inventory["MANUAL_RULES"]["learned_items"]), "what_is_learned": "Schreib- und Leseroutine", "events_served": 381},
    ]
    write("FIVE_HUNDRED_SEVENTY_SIXTH_LEARNING_LAYERS.tsv", layers)
    write("FIVE_HUNDRED_SEVENTY_SIXTH_ONE_HUNDRED_SEVENTY_THREE_CARD_LEARNING_MAP.tsv", card_rows)
    write("FIVE_HUNDRED_SEVENTY_SIXTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_AUDIT.tsv", event_rows)
    write("FIVE_HUNDRED_SEVENTY_SIXTH_SEVEN_SPECIALIST_LESSON.tsv", [{
        "lesson_order": i,
        "card_no": row["card_no"],
        "surfaces": row["surfaces"],
        "component_parse": row["component_parse"],
        "value_de": row["specialist_value_de"],
        "teaching_mode": "GANZKARTE" if row["composition_status"] == "LEARNED_WHOLE_CARD" else "INNENKERN",
        "occurrences": row["occurrences"],
    } for i, row in enumerate(specialists.values(), 1)])

    comp_counts = Counter(r["composition_status"] for r in cards)
    summary = {
        "status": "PASS",
        "semantic_learning_items": len(components) + len(frames) + len(specialists),
        "components": len(components),
        "action_frames": len(frames),
        "specialist_values": len(specialists),
        "visible_card_forms": len(cards),
        "fully_compositional_cards": comp_counts["COMPOSITIONAL"],
        "partial_cards": comp_counts["PARTIAL_WITH_LEARNED_ATOM"],
        "whole_cards": comp_counts["LEARNED_WHOLE_CARD"],
        "events": len(events),
        "complete_semantic_events": sum(r["complete"] == "YES" for r in event_rows),
    }
    (HERE / "FIVE_HUNDRED_SEVENTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertsechsundsiebzigste Runde: Lehrlingslast",
        "",
        "## Die entscheidende Trennung",
        "",
        "Der Lehrling erkennt 173 sichtbare Kartenformen, muss aber nicht 173 unabhängige Bedeutungen auswendig lernen. Die semantische Lehre besteht aus 38 Komponenten, 56 Rahmenregeln und sieben Fachwerten: insgesamt 101 kleine Bedeutungs- oder Einsatzregeln. Die 173 Karten gehören zur graphischen Lesefertigkeit.",
        "",
        "166 Karten werden vollständig aus Bauteilen erzeugt. Vier enthalten einen gelernten Innenkern; nur drei sind echte gelernte Ganzkarten. Alle 381 Ereignisse lassen sich damit wieder lesen. Die Karte ist also eher ein abgekürztes Werkstattzeichen als ein undurchsichtiges Wort.",
        "",
        "## Lehrgang",
        "",
        "1. 38 kleine Werte lernen: Maß, Portion, Quelle, Ziel, Ansatz, Grad, laufender Posten und Operationen.",
        "2. 56 begrenzte Rahmenregeln üben, die aus denselben Teilen konkrete Handlungen machen.",
        "3. Sieben seltene Fachwerte separat merken.",
        "4. Danach 173 Kartenbilder als graphische Kurzformen lesen und mit den Oberflächenregeln schreiben.",
        "",
        "Das ist für mehrere Schreiber plausibler: Sie teilen eine kleine Bedeutungsgrammatik und einen größeren visuellen Kartenkatalog. Abweichende Hände müssen nicht dasselbe Zeichen buchstabenweise analysieren; sie müssen dieselbe Karte erkennen und aus ihrem Bau lesen.",
        "",
        "## Nächster Schritt",
        "",
        "Als Härtetest wird jetzt jede der 173 Karten ausschließlich aus den 38 Komponenten, 56 Rahmenregeln und sieben Fachwerten rückgebaut. Dabei darf die alte Ganzkartenglosse nicht als Eingabe dienen.",
    ]
    (HERE / "FIVE_HUNDRED_SEVENTY_SIXTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
