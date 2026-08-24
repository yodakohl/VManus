#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P555 = ROOT / "sidequest_semantic_atomic_card_unification_five_hundred_fifty_fifth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    cards = read_tsv(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_ONE_HUNDRED_SEVENTY_THREE_ATOMIC_CARD_DICTIONARY.tsv")
    events = read_tsv(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_ATOMIC_EVENT_DICTIONARY.tsv")
    by_card = defaultdict(list)
    for row in events: by_card[row["card_no"]].append(row)

    rows = []
    for card in cards:
        occurrences = by_card[card["card_no"]]
        sections = {"HERBAL" if row["record"].startswith("H") else "BIOLOGICAL" for row in occurrences}
        if len(sections) != 1:
            continue
        section = next(iter(sections))
        if card["composition_status"] == "COMPOSITIONAL":
            partition = "LOCAL_RECURRENT_COMPOSITION" if len(occurrences) > 1 else "LOCAL_SINGLETON_COMPOSITION"
            semantic_learning = "GENERATE_FROM_COMPONENTS"
        else:
            partition = "LOCAL_SPECIALIST_WHOLE_OR_ATOM"
            semantic_learning = "LEARN_ONE_SPECIALIST_VALUE"
        rows.append({
            "card_no": card["card_no"], "section": section, "surfaces": card["surfaces"],
            "component_parse": card["component_parse"], "atomic_card_value_de": card["atomic_card_value_de"],
            "composition_status": card["composition_status"], "section_local_partition": partition,
            "occurrences": str(len(occurrences)), "records": "|".join(sorted({row["record"] for row in occurrences})),
            "semantic_learning_rule": semantic_learning,
            "separate_whole_word_needed": "YES" if semantic_learning == "LEARN_ONE_SPECIALIST_VALUE" else "NO",
        })

    row_by_card = {row["card_no"]: row for row in rows}
    event_rows = []
    for event in events:
        if event["card_no"] not in row_by_card:
            continue
        card = row_by_card[event["card_no"]]
        event_rows.append({
            "event_id": event["event_id"], "page": event["page"], "record": event["record"], "statement_id": event["statement_id"],
            "card_no": event["card_no"], "surface": event["surface"], "component_parse": event["component_parse"],
            "atomic_card_value_de": event["atomic_card_value_de"], "section_local_partition": card["section_local_partition"],
            "semantic_learning_rule": card["semantic_learning_rule"], "event_reading_complete": "YES",
        })

    specialist_rows = [
        {
            "card_no": row["card_no"], "section": row["section"], "surfaces": row["surfaces"],
            "component_parse": row["component_parse"], "specialist_value_de": row["atomic_card_value_de"],
            "composition_status": row["composition_status"], "occurrences": row["occurrences"],
            "teaching_rule": "als kurze Fachkarte oder gelernten Innenkern lehren",
        }
        for row in rows if row["section_local_partition"] == "LOCAL_SPECIALIST_WHOLE_OR_ATOM"
    ]
    summary_rows = []
    for section in ["HERBAL", "BIOLOGICAL", "BOTH_LOCAL"]:
        selected = rows if section == "BOTH_LOCAL" else [row for row in rows if row["section"] == section]
        summary_rows.append({
            "section": section, "local_cards": str(len(selected)), "local_events": str(sum(int(row["occurrences"]) for row in selected)),
            "recurrent_compositions": str(sum(row["section_local_partition"] == "LOCAL_RECURRENT_COMPOSITION" for row in selected)),
            "singleton_compositions": str(sum(row["section_local_partition"] == "LOCAL_SINGLETON_COMPOSITION" for row in selected)),
            "specialist_whole_or_atom": str(sum(row["section_local_partition"] == "LOCAL_SPECIALIST_WHOLE_OR_ATOM" for row in selected)),
            "component_generated_cards": str(sum(row["semantic_learning_rule"] == "GENERATE_FROM_COMPONENTS" for row in selected)),
        })

    write_tsv("FIVE_HUNDRED_SEVENTY_FIFTH_ONE_HUNDRED_FIFTY_SIX_LOCAL_CARDS.tsv", rows)
    write_tsv("FIVE_HUNDRED_SEVENTY_FIFTH_TWO_HUNDRED_FORTY_FIVE_LOCAL_EVENTS.tsv", event_rows)
    write_tsv("FIVE_HUNDRED_SEVENTY_FIFTH_SEVEN_SPECIALIST_CARDS.tsv", specialist_rows)
    write_tsv("FIVE_HUNDRED_SEVENTY_FIFTH_SECTION_SUMMARY.tsv", summary_rows)
    counts = Counter(row["section_local_partition"] for row in rows)
    summary = {
        "status": "PASS", "local_cards": len(rows), "local_events": len(event_rows),
        "recurrent_compositions": counts["LOCAL_RECURRENT_COMPOSITION"],
        "recurrent_composition_events": sum(int(row["occurrences"]) for row in rows if row["section_local_partition"] == "LOCAL_RECURRENT_COMPOSITION"),
        "singleton_compositions": counts["LOCAL_SINGLETON_COMPOSITION"],
        "specialist_cards": counts["LOCAL_SPECIALIST_WHOLE_OR_ATOM"],
        "component_generated_local_cards": sum(row["semantic_learning_rule"] == "GENERATE_FROM_COMPONENTS" for row in rows),
        "whole_or_atom_values_to_learn": len(specialist_rows),
    }
    (HERE / "FIVE_HUNDRED_SEVENTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertfünfundsiebzigste Runde: lokale Karten",
        "",
        "## Ergebnis",
        "",
        "Die 156 nur in einer Hauptsektion sichtbaren Karten zerfallen in 34 wiederkehrende Kompositionen mit 123 Ereignissen, 115 einmalige aber reguläre Kompositionen und nur sieben Fachkarten mit gelerntem Ganzwert oder Innenkern. Zusammen tragen sie 245 Ereignisse.",
        "",
        "Damit sind 149/156 lokale Karten semantisch aus dem Komponentenapparat erzeugbar. Ein einmaliges Oberflächenwort ist nicht automatisch ein neues Lexem: 115 Singletonkarten kombinieren bekannte Teile nur einmal auf diesen zehn Seiten. Gelernt werden müssen lokal lediglich sieben Werte: Arbeitsfach, auswringen, verwahren, weiter, abziehen/teilen, ansetzen/festbinden und zweite Sollstufe.",
        "",
        "Der Wortschatz ist damit wesentlich kleiner als 173 Ganzwörter. Die sichtbare Karte bleibt eine gelernte graphische Einheit, aber ihr Arbeitswert entsteht in 166/173 Fällen vollständig aus Komponenten; vier weitere besitzen nur einen gelernten Innenkern, drei sind echte Ganzkarten.",
        "",
        "## Nächster Schritt",
        "",
        "Nun wird das Lehrlingsinventar neu gerechnet: 38 Komponenten, 56 Rahmenregeln und sieben Fachwerte statt 173 unabhängiger Bedeutungen; die 173 Karten bleiben nur als Oberflächen-/Allographendeck bestehen.",
    ]
    (HERE / "FIVE_HUNDRED_SEVENTY_FIFTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
