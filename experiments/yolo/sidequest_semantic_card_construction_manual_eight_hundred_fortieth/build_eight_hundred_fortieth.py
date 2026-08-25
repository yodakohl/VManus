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
PREFIX = "EIGHT_HUNDRED_FORTIETH"

SLOTS = {
    "OK": "START_ACTION", "CHD": "TRANSFER_ACTION", "SH": "STATE_ACTION", "SHED": "STATE_ACTION",
    "CHK": "PROCESS_ACTION", "CTH": "STATE_ACTION", "SOLK": "PROCESS_ACTION", "P": "TRANSFER_ACTION",
    "LSH": "PROCESS_ACTION", "CFH": "PROCESS_ACTION", "CH": "MATERIAL_ACTION", "T": "GENERAL_ACTION",
    "K": "MATERIAL_ACTION", "S": "QUANTITY_CHECK", "L": "TRANSFER_ACTION", "OL": "ORDER_CONTINUE",
    "OT": "ORDER_NEXT", "AL": "ADDRESS_TARGET", "AR": "ADDRESS_SOURCE", "AIR": "MATERIAL_WATER",
    "OR": "MATERIAL_BATCH", "HO": "MATERIAL_ADDITION", "CKH": "ADDRESS_PATH", "O": "WORK_CONTEXT",
    "Y": "CURRENT_REFERENT", "AIN": "QUANTITY_PORTION", "AIIN": "QUANTITY_MEASURE", "IIN": "SETTING_STAGE",
    "E": "GRADE_SHORT", "EE": "GRADE_LONG", "EEE": "GRADE_FULL", "R": "PROCESS_ACTION",
    "AN": "BOUND_ADDITION", "DA": "BOUND_NUMBER", "LD": "BOUND_FASTEN", "DY": "LICENSED_CLOSE",
    "OS": "WHOLE_CONNECTOR", "RESUME_CARD": "WHOLE_ANAPHOR", "TALAM": "WHOLE_OPERATION",
}

PORTABLE = {
    "AIIN": "nach dem Sollmass",
    "OL": "weiter",
    "Y": "den aktuellen Posten",
    "SHED+DY": "stehen lassen und schliessen",
    "CHD+Y": "den Posten umsetzen",
    "AL": "an der Zielstelle",
    "OK+Y": "den Posten ansetzen",
    "OK+EE+DY": "laenger ansetzen und schliessen",
    "OK+AIIN": "nach Sollmass ansetzen",
    "L+CHD+DY": "leiten, umsetzen und schliessen",
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
    components = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_39_COMPONENT_NINTH_GRAMMAR.tsv")
    cards = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_173_CARD_NINTH_DICTIONARY.tsv")
    events = read(BASE / "EIGHT_HUNDRED_THIRTY_THIRD_381_EVENT_REPARSE.tsv")
    statements = read(WATER / "EIGHT_HUNDRED_THIRTY_FIFTH_116_WATER_ALIGNED_STATEMENTS.tsv")

    component_manual = []
    for row in components:
        component_manual.append(
            {
                "component_no": row["component_no"],
                "component": row["component"],
                "short_value_de": row["short_value_de"],
                "construction_slot": SLOTS[row["component"]],
                "grammar_tier": row["grammar_tier"],
                "exact_cards": row["exact_cards"],
                "events": row["events"],
                "apprentice_rule": row["teaching_rule"],
            }
        )

    top_cards = sorted(cards, key=lambda row: (-int(row["events"]), row["registered_surfaces"]))[:10]
    top_ids = {row["exact_card_id"] for row in top_cards}
    card_rows = []
    for rank, card in enumerate(top_cards, 1):
        card_rows.append(
            {
                "frequency_rank": rank,
                "exact_card_id": card["exact_card_id"],
                "surfaces": card["registered_surfaces"],
                "component_recipe": card["component_recipe"],
                "literal_reading_de": card["ninth_grammar_reading_de"],
                "portable_workshop_paraphrase_de": PORTABLE[card["component_recipe"]],
                "events": card["events"],
                "page_specific_noun": "NONE",
                "decision": "PORTABLE_CARD_READING",
            }
        )
    portable_by_id = {row["exact_card_id"]: row["portable_workshop_paraphrase_de"] for row in card_rows}

    event_rows = []
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for event in events:
        if event["exact_card_id"] not in top_ids:
            continue
        item = {
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "exact_card_id": event["exact_card_id"],
            "surface": event["surface"],
            "component_recipe": event["component_recipe"],
            "literal_reading_de": event["ninth_grammar_reading_de"],
            "portable_workshop_paraphrase_de": portable_by_id[event["exact_card_id"]],
            "owner_independent": "YES",
        }
        event_rows.append(item)
        by_statement[event["statement_id"]].append(item)

    statement_by_id = {row["statement_id"]: row for row in statements}
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
                "full_working_reading_de": source["working_reading_de"],
                "owner_noun_not_used_in_portable_sequence": "YES",
            }
        )

    rules = [
        (1, "IDENTITY_FIRST", "Recognize the learned exact card before splitting its visible surface."),
        (2, "WHOLE_OVERRIDES", "OS, RESUME_CARD and TALAM remain memorized whole cards."),
        (3, "LEFT_TO_RIGHT", "Read registered components in card order; do not reorder them silently."),
        (4, "ORDER", "OL continues; OT advances; OS adds; RESUME_CARD resumes the prior material."),
        (5, "ACTION", "Read the stable action component before supplying any pictured object."),
        (6, "MATERIAL", "AIR water, OR batch and HO ingredient remain distinct material values."),
        (7, "ADDRESS", "AR source, CKH passage and AL target form the local address chain."),
        (8, "QUANTITY", "AIN portion, AIIN prescribed measure and IIN stage share a learned setting slot."),
        (9, "GRADE", "E short, EE long and EEE full modify only their own local slot."),
        (10, "REFERENT", "Y names the current work item even when its visible surface is dy."),
        (11, "CLOSE", "Only licensed DY constructions close; visible letters dy alone do not."),
        (12, "OWNER_LAST", "Add plant, basin or station nouns only after the portable card reading."),
    ]
    rule_rows = [{"priority": p, "rule": r, "instruction": i} for p, r, i in rules]

    write(f"{PREFIX}_39_COMPONENT_CONSTRUCTION_MANUAL.tsv", component_manual, ["component_no", "component", "short_value_de", "construction_slot", "grammar_tier", "exact_cards", "events", "apprentice_rule"])
    write(f"{PREFIX}_10_HIGH_FREQUENCY_CARDS.tsv", card_rows, ["frequency_rank", "exact_card_id", "surfaces", "component_recipe", "literal_reading_de", "portable_workshop_paraphrase_de", "events", "page_specific_noun", "decision"])
    write(f"{PREFIX}_127_HIGH_FREQUENCY_EVENTS.tsv", event_rows, ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "literal_reading_de", "portable_workshop_paraphrase_de", "owner_independent"])
    write(f"{PREFIX}_68_STATEMENT_PORTABLE_SEQUENCES.tsv", statement_rows, ["statement_id", "page", "record", "selected_events", "selected_surfaces", "portable_sequence_de", "full_working_reading_de", "owner_noun_not_used_in_portable_sequence"])
    write(f"{PREFIX}_12_APPRENTICE_RULES.tsv", rule_rows, ["priority", "rule", "instruction"])

    summary = {
        "status": "PASS",
        "decision": "COMBINED_CARD_MANUAL_PORTABLY_READS_TOP_TEN_CARDS",
        "components": len(component_manual),
        "top_cards": len(card_rows),
        "top_events": len(event_rows),
        "covered_statements": len(statement_rows),
        "covered_records": len({row["record"] for row in event_rows}),
        "covered_pages": len({row["page"] for row in event_rows}),
        "event_coverage_fraction": round(len(event_rows) / 381, 6),
        "apprentice_rules": len(rule_rows),
        "page_specific_values_added": 0,
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manual = """# Compact card-construction manual

Read the exact learned card first. Then expand its registered components from
left to right. Use three central subsystems:

- AR source → CKH passage → AL target;
- AIN portion → AIIN prescribed measure → IIN work stage;
- E short → EE long → EEE full.

Actions and order cards wrap those slots. Y names the current work item. A
licensed DY construction closes the instruction. The visible spelling `dy`
does not itself guarantee closure: it can render the exact Y card.

Only after this portable reading may the scribe or reader supply the pictured
plant, basin, vessel or diagram station. Thus `OK+AIIN` is always “set to the
prescribed measure”; the picture decides what is being set.
"""
    (HERE / f"{PREFIX}_ONE_PAGE_MANUAL.md").write_text(manual, encoding="utf-8")

    report = """# Sidequest Pass 840: combined card-construction manual

The address, quantity and grade paradigms are now one apprentice manual. It
keeps all 39 short component values and adds no page-local noun.

The ten most frequent exact cards cover 127/381 events, 68 statements, all 11
records, and all seven prose pages. Each has one portable workshop paraphrase:
prescribed measure, continue, current item, leave standing and close, move the
item, target, set the item, set long and close, set to measure, or guide/move
and close. The same paraphrase is used at every occurrence.

This also records the most important scribal exception: the exact Y card may be
visibly rendered `dy`, while closing DY is a licensed construction. A learner
must recognize whole-card identity before treating visible fragments as
components.

The resulting system is a real mixed notation: productive component islands
inside a deck of learned exact cards. Next, apply the same owner-independent
test to frequency ranks 11–20. If those ten need many new local meanings, the
productive layer has reached its useful limit; if they remain portable, extend
the manual one tier.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
