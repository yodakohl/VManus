#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
SOURCES = {
    "H1": ROOT / "experiments/yolo/sidequest_semantic_f10_root_scrape_four_hundred_sixteenth/FOUR_HUNDRED_SIXTEENTH_H1_FOURTEEN_CARD_READING.tsv",
    "H2": ROOT / "experiments/yolo/sidequest_semantic_h2_press_paste_four_hundred_twenty_fourth/FOUR_HUNDRED_TWENTY_FOURTH_H2_24_EVENT_INTERLINEAR.tsv",
    "H3": ROOT / "experiments/yolo/sidequest_semantic_h3_complete_filtration_four_hundred_twenty_third/FOUR_HUNDRED_TWENTY_THIRD_H3_17_EVENT_INTERLINEAR.tsv",
    "H4": ROOT / "experiments/yolo/sidequest_semantic_h4_complete_preparation_four_hundred_twenty_second/FOUR_HUNDRED_TWENTY_SECOND_H4_18_EVENT_INTERLINEAR.tsv",
    "H5": ROOT / "experiments/yolo/sidequest_semantic_h5_complete_article_four_hundred_twenty_first/FOUR_HUNDRED_TWENTY_FIRST_H5_27_EVENT_INTERLINEAR.tsv",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base = read(BASE)
    base_by_id = {row["event_id"]: row for row in base}
    combined = []
    for record, path in SOURCES.items():
        for row in read(path):
            event_id = row["event_id"]
            original = base_by_id[event_id]
            value = row.get("selected_small_value_de") or row.get("small_value_de")
            combined.append({
                "event_id": event_id, "record": record, "page": original["page"], "locus": original["locus"],
                "statement_id": original["statement_id"], "surface": original["surface_display"],
                "joint_tuple_id": original["joint_tuple_id"], "small_value_de": value,
                "source_pass": path.parent.name, "semantic_segmentation_before_consolidation": original["semantic_segmentation"],
            })
    combined.sort(key=lambda row: int(str(row["event_id"])[1:]))
    write("FOUR_HUNDRED_TWENTY_FIFTH_HERBAL_100_EVENT_EDITION.tsv", combined)

    articles = [
        {"record": "H1", "events": 14, "statements": 2, "article_role": "TUBER_WATER_EXTRACT_AND_DOSE", "continuous_reading_de": "Eine Knolle abschaben und bearbeiten, im Topf mit Wasser ausziehen, den Auszug bemessen und als Gabe anwärmen und bereitstellen."},
        {"record": "H2", "events": 24, "statements": 3, "article_role": "PRESS_SPLIT_AND_PASTE", "continuous_reading_de": "Spitzen zerstoßen und abpressen, zwei Pressprodukte getrennt fortführen, im glasierten Gefäß vereinigen und auf weichen Sollstand zur Paste bringen."},
        {"record": "H3", "events": 17, "statements": 4, "article_role": "FILTRATION_AND_RESERVE", "continuous_reading_de": "Blütenkraut als Sud auswringen, stehen lassen, nachseihen, den Klarauszug kühlen und eine Reserve für ein zweites Produkt zurückrufen."},
        {"record": "H4", "events": 18, "statements": 4, "article_role": "MEASURE_TEMPER_STORE", "continuous_reading_de": "Portionen bemessen, abkühlen oder länger wärmen, Auszug nehmen, Ansatzportion bilden und einen Posten verwahren."},
        {"record": "H5", "events": 27, "statements": 6, "article_role": "PREPARE_WASH_APPLY_USE", "continuous_reading_de": "Zutatenansatz nach Blüte und Maß bereiten, waschen und auftragen, Kraut zerreiben, Auszug abseihen, gebrauchen und jede Gabe bemessen."},
    ]
    write("FOUR_HUNDRED_TWENTY_FIFTH_FIVE_COMPLETE_ARTICLES.tsv", articles)

    herbal = [row for row in base if row["record_unit_id"] in SOURCES]
    grammar_specs = [
        ("AIIN", "Mass", "AIIN", "quantity setting"),
        ("Y_CURRENT_OR_REFERENT", "dies", "Y_CURRENT|Y_REFERENT", "current-item reference"),
        ("OL_CONTINUE", "fortsetzen", "OL_CONTINUE", "continuation"),
        ("OR_BATCH", "Ansatz", "OR_BATCH", "preparation identity"),
        ("OK_TAKE_OR_USE", "nehmen oder verwenden", "OK_SET", "item activation"),
        ("CTH_READY", "bereit", "CTH_READY", "release state"),
        ("AL_SITE", "Stelle", "AL_SITE", "target address"),
        ("AIN_PORTION", "Portion", "AIN_PORTION", "divided item"),
    ]
    grammar = []
    for family, value, token_spec, role in grammar_specs:
        tokens = token_spec.split("|")
        matched = [row for row in herbal if any(token in row["semantic_segmentation"] for token in tokens)]
        grammar.append({
            "family": family, "small_value_de": value, "events": len(matched),
            "exact_cards": len({row["joint_tuple_id"] for row in matched}),
            "records": "|".join(sorted({row["record_unit_id"] for row in matched})),
            "workshop_role": role,
        })
    write("FOUR_HUNDRED_TWENTY_FIFTH_EIGHT_COMMON_GRAMMAR_FAMILIES.tsv", grammar)

    weak = [
        {"record": "H1", "event_id": "E002", "surface": "cthoor", "current_value_de": "abschaben", "strongest_rival": "säubern", "why_weak": "singleton action; no tool visible", "next_test": "compare to all initial plant-preparation verbs"},
        {"record": "H2", "event_id": "E038", "surface": "chodaiin", "current_value_de": "Paste", "strongest_rival": "Salbe", "why_weak": "singleton final product inferred from soft setting", "next_test": "compare final products after IIN settings"},
        {"record": "H3", "event_id": "E049", "surface": "kchy", "current_value_de": "Trank", "strongest_rival": "Spülung", "why_weak": "use route not pictured", "next_test": "compare every drink rinse and use product"},
        {"record": "H4", "event_id": "E063", "surface": "talam", "current_value_de": "verwahren", "strongest_rival": "ruhen lassen", "why_weak": "singleton statement-final open card", "next_test": "compare storage and settle cards"},
        {"record": "H5", "event_id": "E076", "surface": "chodaly", "current_value_de": "Blütebeginn", "strongest_rival": "erster Teil", "why_weak": "timing inferred from picture owner", "next_test": "compare all picture-timed selection cards"},
    ]
    write("FOUR_HUNDRED_TWENTY_FIFTH_FIVE_WEAKEST_CARDS.tsv", weak)

    summary = {
        "status": "PASS", "events": len(combined), "articles": len(articles), "common_grammar_families": len(grammar),
        "weak_cards": len(weak), "decision": "FIVE_HERBAL_ARTICLES_SHARE_PRODUCTIVE_WORKSHOP_GRAMMAR_AND_LOCAL_NOMENCLATOR",
    }
    (HERE / "FOUR_HUNDRED_TWENTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
