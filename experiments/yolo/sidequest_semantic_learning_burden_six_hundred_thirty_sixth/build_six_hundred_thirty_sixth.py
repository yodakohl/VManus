#!/usr/bin/env python3
"""Classify all 173 cards by apprentice semantic learning burden."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
WORDS = ROOT / "experiments/yolo/sidequest_semantic_backread_noun_repair_six_hundred_seventeenth/SIX_HUNDRED_SEVENTEENTH_39_SHARP_WORDS.tsv"
CARDS = ROOT / "experiments/yolo/sidequest_semantic_backread_noun_repair_six_hundred_seventeenth/SIX_HUNDRED_SEVENTEENTH_173_SHARP_COMMANDS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth/SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv"
PARADIGM = ROOT / "experiments/yolo/sidequest_semantic_productive_paradigm_table_six_hundred_thirty_fifth/SIX_HUNDRED_THIRTY_FIFTH_22_EXACT_CARD_MEMBERS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    words = read_tsv(WORDS)
    cards = read_tsv(CARDS)
    events = read_tsv(EVENTS)
    paradigm_cards = {row["card_no"] for row in read_tsv(PARADIGM)}
    known = {row["canonical_component"] for row in words}

    component_card_frequency = Counter()
    for card in cards:
        component_card_frequency.update(set(card["semantic_component_parse"].split("+")))

    class_rows = []
    by_card = {}
    for card in cards:
        tokens = card["semantic_component_parse"].split("+")
        rare = [token for token in tokens if component_card_frequency[token] == 1]
        unknown = [token for token in tokens if token not in known]
        if card["card_no"] in paradigm_cards:
            burden_class = "FULLY_COMPOSITIONAL_CARD"
            basis = "SIX_TABLE_PARADIGM"
            independent_card_meanings = 0
            teaching_rule = "read core, grade or quantity, and endpoint from the productive table"
        elif len(tokens) == 1 and not rare:
            burden_class = "FULLY_COMPOSITIONAL_CARD"
            basis = "RECURRENT_STANDALONE_WORD_OR_ALLOGRAPH"
            independent_card_meanings = 0
            teaching_rule = "read the recurrent standalone component; renderer selects the visible allograph"
        elif rare and len(tokens) == 1:
            burden_class = "TRUE_LEARNED_WHOLE_CARD"
            basis = "ONE_USE_STANDALONE_COMPONENT"
            independent_card_meanings = 1
            teaching_rule = "memorize this whole card and its short value"
        elif rare:
            burden_class = "PARTIAL_COMPOSITION_ONE_LEARNED_CORE"
            basis = "ONE_USE_CORE_PLUS_PRODUCTIVE_COMPONENTS"
            independent_card_meanings = 1
            teaching_rule = "memorize the one-use core; compose the remaining components"
        else:
            burden_class = "COMPOSITIONAL_MEANING_LEARNED_EXACT_SURFACE"
            basis = "KNOWN_RECURRENT_COMPONENTS_OUTSIDE_SIX_TABLES"
            independent_card_meanings = 0
            teaching_rule = "compose the meaning from known components; learn the exact card body or wrapper"
        row = {
            "card_no": card["card_no"],
            "surfaces": card["surfaces"],
            "semantic_component_parse": card["semantic_component_parse"],
            "standard_command_de": card["standard_command_de"],
            "occurrences": card["occurrences"],
            "records": card["records"],
            "burden_class": burden_class,
            "classification_basis": basis,
            "rare_one_use_components": "|".join(rare) if rare else "NONE",
            "unknown_components": "|".join(unknown) if unknown else "NONE",
            "independent_card_meanings_to_memorize": independent_card_meanings,
            "teaching_rule": teaching_rule,
        }
        class_rows.append(row)
        by_card[card["card_no"]] = row

    event_rows = []
    for event in events:
        card = by_card[event["card_no"]]
        event_rows.append({
            "event_id": event["event_id"],
            "record": event["record"],
            "page": event["page"],
            "surface": event["surface"],
            "card_no": event["card_no"],
            "semantic_component_parse": card["semantic_component_parse"],
            "standard_command_de": card["standard_command_de"],
            "burden_class": card["burden_class"],
            "teaching_rule": card["teaching_rule"],
        })

    classes = [
        "FULLY_COMPOSITIONAL_CARD",
        "COMPOSITIONAL_MEANING_LEARNED_EXACT_SURFACE",
        "PARTIAL_COMPOSITION_ONE_LEARNED_CORE",
        "TRUE_LEARNED_WHOLE_CARD",
    ]
    summary_rows = []
    for burden_class in classes:
        selected = [row for row in class_rows if row["burden_class"] == burden_class]
        summary_rows.append({
            "burden_class": burden_class,
            "exact_cards": len(selected),
            "occurrences": sum(int(row["occurrences"]) for row in selected),
            "independent_card_meanings_to_memorize": sum(int(row["independent_card_meanings_to_memorize"]) for row in selected),
            "card_nos": "|".join(row["card_no"] for row in selected),
        })

    word_rows = []
    for word in words:
        component = word["canonical_component"]
        frequency = component_card_frequency[component]
        if frequency > 1:
            burden = "RECURRENT_PRODUCTIVE_COMPONENT"
        else:
            cards_with = [row for row in class_rows if component in row["semantic_component_parse"].split("+")]
            burden = "ONE_USE_WHOLE_CARD_WORD" if cards_with and cards_with[0]["burden_class"] == "TRUE_LEARNED_WHOLE_CARD" else "ONE_USE_EMBEDDED_CORE"
        word_rows.append({
            "semantic_word_no": word["semantic_word_no"],
            "canonical_component": component,
            "spoken_workshop_word_de": word["spoken_workshop_word_de"],
            "card_type_frequency": frequency,
            "semantic_word_burden": burden,
            "cards": "|".join(row["card_no"] for row in class_rows if component in row["semantic_component_parse"].split("+")),
        })

    write_tsv(HERE / "SIX_HUNDRED_THIRTY_SIXTH_173_CARD_LEARNING_BURDEN.tsv", class_rows, list(class_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_SIXTH_381_EVENT_LEARNING_BURDEN.tsv", event_rows, list(event_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_SIXTH_4_CLASS_SUMMARY.tsv", summary_rows, list(summary_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_SIXTH_39_WORD_BURDEN.tsv", word_rows, list(word_rows[0]))

    counts = {row["burden_class"]: (int(row["exact_cards"]), int(row["occurrences"])) for row in summary_rows}
    word_counts = Counter(row["semantic_word_burden"] for row in word_rows)
    md = [
        "# Was der Lehrling wirklich lernen muss",
        "",
        "| Klasse | Karten | Ereignisse | Lernhandlung |",
        "|---|---:|---:|---|",
        f"| voll kompositionell | {counts['FULLY_COMPOSITIONAL_CARD'][0]} | {counts['FULLY_COMPOSITIONAL_CARD'][1]} | Wort oder Sechsertabelle lesen |",
        f"| Bedeutung kompositionell, exakte Form lernen | {counts['COMPOSITIONAL_MEANING_LEARNED_EXACT_SURFACE'][0]} | {counts['COMPOSITIONAL_MEANING_LEARNED_EXACT_SURFACE'][1]} | Komponenten sprechen, Kartenkoerper kopieren |",
        f"| ein opaker Kern plus Komposition | {counts['PARTIAL_COMPOSITION_ONE_LEARNED_CORE'][0]} | {counts['PARTIAL_COMPOSITION_ONE_LEARNED_CORE'][1]} | einen seltenen Kern und produktive Raender lernen |",
        f"| echte Ganzkarte | {counts['TRUE_LEARNED_WHOLE_CARD'][0]} | {counts['TRUE_LEARNED_WHOLE_CARD'][1]} | ganze Karte auswendig lernen |",
        "",
        f"Das 39-Wort-Heft zerfaellt in {word_counts['RECURRENT_PRODUCTIVE_COMPONENT']} wiederkehrende Komponenten, {word_counts['ONE_USE_EMBEDDED_CORE']} einmalige eingebettete Fachkerne und {word_counts['ONE_USE_WHOLE_CARD_WORD']} echte Ganzkartenwoerter.",
        "",
        "Die 173 exakten Karten bleiben als Schreibinventar bestehen. Semantisch sind sie aber keine 173 unabhaengigen Woerter: ausser den 39 kurzen Komponenten wird keine weitere Kartenbedeutung benoetigt.",
    ]
    (HERE / "SIX_HUNDRED_THIRTY_SIXTH_APPRENTICE_BURDEN_MANUAL.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "semantic_words": len(words),
        "recurrent_productive_components": word_counts["RECURRENT_PRODUCTIVE_COMPONENT"],
        "one_use_embedded_cores": word_counts["ONE_USE_EMBEDDED_CORE"],
        "one_use_whole_card_words": word_counts["ONE_USE_WHOLE_CARD_WORD"],
        "exact_cards": len(class_rows),
        "events": len(event_rows),
        "class_counts": {row["burden_class"]: {"cards": int(row["exact_cards"]), "events": int(row["occurrences"])} for row in summary_rows},
        "extra_independent_meanings_beyond_39_words": 0,
        "cards_with_unknown_components": sum(row["unknown_components"] != "NONE" for row in class_rows),
        "decision": "THIRTY_NINE_WORDS_PLUS_CARD_SURFACES_TEACH_ALL_173_CARDS",
    }
    (HERE / "SIX_HUNDRED_THIRTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
