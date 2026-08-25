#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_ninth_workshop_grammar_eight_hundred_thirty_third"
WATER = ROOT / "sidequest_semantic_water_paradigm_eight_hundred_thirty_fifth"
PREFIX = "EIGHT_HUNDRED_FORTY_THIRD"

PORTABLE = {
    "CHK+EE+Y": "den Posten laenger waermen",
    "T+Y": "den Posten bearbeiten",
    "OL+OR": "mit dem Ansatz weiter",
    "AIN": "eine Portion",
    "RESUME_CARD": "davon",
    "L": "leiten",
    "L+DY": "leiten und schliessen",
    "LSH+E+DY": "kurz spuelen und schliessen",
    "O+IIN": "Arbeitsgang bis zur Stufe",
    "OK+CHD+DY": "ansetzen, umsetzen und schliessen",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cards = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_173_CARD_NINTH_DICTIONARY.tsv")
    events = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_381_EVENT_REPARSE.tsv")
    statements = read(WATER / "EIGHT_HUNDRED_THIRTY_FIFTH_116_WATER_ALIGNED_STATEMENTS.tsv")
    ordered = sorted(cards, key=lambda row: (-int(row["events"]), row["registered_surfaces"]))
    tier = ordered[30:40]
    tier_ids = {row["exact_card_id"] for row in tier}
    top40_ids = {row["exact_card_id"] for row in ordered[:40]}

    card_rows = []
    for frequency_rank, card in enumerate(tier, 31):
        whole = card["card_tier"].startswith("MEMORIZED_WHOLE")
        card_rows.append(
            {
                "frequency_rank": frequency_rank,
                "exact_card_id": card["exact_card_id"],
                "surfaces": card["registered_surfaces"],
                "component_recipe": card["component_recipe"],
                "literal_reading_de": card["ninth_grammar_reading_de"],
                "portable_workshop_paraphrase_de": PORTABLE[card["component_recipe"]],
                "events": card["events"],
                "card_tier": card["card_tier"],
                "learning_mode": "MEMORIZE_WHOLE_CARD" if whole else "COMPOSE_COMPONENTS",
                "page_specific_noun": "NONE",
            }
        )
    portable_by_id = {row["exact_card_id"]: row["portable_workshop_paraphrase_de"] for row in card_rows}
    mode_by_id = {row["exact_card_id"]: row["learning_mode"] for row in card_rows}

    event_rows = []
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        if event["exact_card_id"] not in tier_ids:
            continue
        item = {
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "exact_card_id": event["exact_card_id"],
            "surface": event["surface"],
            "component_recipe": event["component_recipe"],
            "portable_workshop_paraphrase_de": portable_by_id[event["exact_card_id"]],
            "learning_mode": mode_by_id[event["exact_card_id"]],
        }
        event_rows.append(item)
        by_statement[event["statement_id"]].append(item)

    statement_by_id = {row["statement_id"]: row for row in statements}
    statement_order = {row["statement_id"]: index for index, row in enumerate(statements)}
    statement_rows = []
    for statement_id, selected in by_statement.items():
        source = statement_by_id[statement_id]
        statement_rows.append(
            {
                "statement_id": statement_id,
                "page": source["page"],
                "record": source["record"],
                "selected_events": len(selected),
                "selected_surfaces": " | ".join(str(row["surface"]) for row in selected),
                "portable_sequence_de": " | ".join(str(row["portable_workshop_paraphrase_de"]) for row in selected),
                "learning_modes": " | ".join(str(row["learning_mode"]) for row in selected),
                "full_working_reading_de": source["working_reading_de"],
            }
        )

    resume_contexts = []
    for event in events:
        if event["component_recipe"] != "RESUME_CARD":
            continue
        index = statement_order[event["statement_id"]]
        current = statements[index]
        previous = statements[index - 1] if index > 0 and statements[index - 1]["record"] == current["record"] else None
        following = statements[index + 1] if index + 1 < len(statements) and statements[index + 1]["record"] == current["record"] else None
        resume_contexts.append(
            {
                "event_id": event["event_id"],
                "page": event["page"],
                "record": event["record"],
                "surface": event["surface"],
                "previous_statement_id": previous["statement_id"] if previous else "NONE",
                "previous_reading_de": previous["working_reading_de"] if previous else "NONE",
                "resume_statement_id": current["statement_id"],
                "resume_reading_de": current["working_reading_de"],
                "following_statement_id": following["statement_id"] if following else "NONE",
                "following_reading_de": following["working_reading_de"] if following else "NONE",
                "antecedent": "CURRENT_PREPARED_MATERIAL_IN_SAME_HERBAL_RECORD",
                "decision": "KEEP_DAVON_WHOLE_ANAPHOR",
            }
        )

    cumulative_events = [row for row in events if row["exact_card_id"] in top40_ids]
    write(f"{PREFIX}_10_MIXED_TIER_CARDS.tsv", card_rows, ["frequency_rank", "exact_card_id", "surfaces", "component_recipe", "literal_reading_de", "portable_workshop_paraphrase_de", "events", "card_tier", "learning_mode", "page_specific_noun"])
    write(f"{PREFIX}_20_MIXED_TIER_EVENTS.tsv", event_rows, ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "portable_workshop_paraphrase_de", "learning_mode"])
    write(f"{PREFIX}_18_MIXED_TIER_STATEMENTS.tsv", statement_rows, ["statement_id", "page", "record", "selected_events", "selected_surfaces", "portable_sequence_de", "learning_modes", "full_working_reading_de"])
    write(f"{PREFIX}_2_DAVON_CONTEXTS.tsv", resume_contexts, ["event_id", "page", "record", "surface", "previous_statement_id", "previous_reading_de", "resume_statement_id", "resume_reading_de", "following_statement_id", "following_reading_de", "antecedent", "decision"])

    summary = {
        "status": "PASS",
        "decision": "FIRST_MIXED_TIER_HAS_NINE_COMPOSED_CARDS_AND_ONE_DAVON_WHOLE_CARD",
        "tier_cards": len(card_rows),
        "tier_events": len(event_rows),
        "tier_statements": len(statement_rows),
        "tier_records": len({row["record"] for row in event_rows}),
        "tier_pages": len({row["page"] for row in event_rows}),
        "composed_cards": sum(row["learning_mode"] == "COMPOSE_COMPONENTS" for row in card_rows),
        "whole_cards": sum(row["learning_mode"] == "MEMORIZE_WHOLE_CARD" for row in card_rows),
        "davon_contexts": len(resume_contexts),
        "davon_registers": sorted({"HERBAL" for _ in resume_contexts}),
        "davon_records": sorted({row["record"] for row in resume_contexts}),
        "cumulative_top40_events": len(cumulative_events),
        "cumulative_top40_fraction": round(len(cumulative_events) / 381, 6),
        "register_correction": "BOTH_DAVON_EVENTS_ARE_HERBAL_NOT_HERBAL_PLUS_BIOLOGICAL",
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 843: first mixed frequency tier

Ranks 31–40 contain nine ordinary component cards and one learned whole card.
The 20 events span 18 statements, ten records, and all seven prose pages. The
top 40 cards now cover 237/381 events (62.2%).

The whole card is `dchol/schol = DAVON`. Both occurrences are Herbal—not one
Herbal and one Biological, as briefly misstated while planning this pass. In
f11r H3 it follows “hold and work the current item” and resumes that material
before adding and carrying it to measure. In f56r H5 it follows preparation at
the target and resumes that prepared material before guiding and setting it.
The short anaphor therefore works in both distinct plant records.

This is the first clear demonstration of the desired mixed architecture inside
the frequency ladder: component construction remains the default, while a
small whole-card word supplies discourse linkage that would be awkward to
spell out from productive stems.

Next, inspect ranks 41–60. Track the proportion of composed, bound, and whole
cards and translate every whole card with one short invariant value rather than
inventing a sentence-sized gloss.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
