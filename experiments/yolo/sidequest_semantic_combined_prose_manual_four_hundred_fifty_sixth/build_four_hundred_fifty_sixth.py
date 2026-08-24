#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
H_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_herbal_component_completion_four_hundred_fifty_fourth/FOUR_HUNDRED_FIFTY_FOURTH_100_EVENT_HERBAL_EDITION.tsv"
H_CARDS = ROOT / "experiments/yolo/sidequest_semantic_herbal_component_completion_four_hundred_fifty_fourth/FOUR_HUNDRED_FIFTY_FOURTH_66_CARD_HERBAL_DICTIONARY.tsv"
B_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_biological_reverse_compiler_four_hundred_fifty_first/FOUR_HUNDRED_FIFTY_FIRST_281_EVENT_EDITION.tsv"
B_CARDS = ROOT / "experiments/yolo/sidequest_semantic_biological_reverse_compiler_four_hundred_fifty_first/FOUR_HUNDRED_FIFTY_FIRST_124_CARD_DICTIONARY.tsv"
B_GENERATOR = ROOT / "experiments/yolo/sidequest_semantic_biological_apprentice_manual_four_hundred_fiftieth/FOUR_HUNDRED_FIFTIETH_117_PRODUCTIVE_CARD_GENERATOR.tsv"
B_WHOLES = ROOT / "experiments/yolo/sidequest_semantic_biological_apprentice_manual_four_hundred_fiftieth/FOUR_HUNDRED_FIFTIETH_SEVEN_WHOLE_CARDS.tsv"
COMPONENTS = ROOT / "experiments/yolo/sidequest_semantic_biological_apprentice_manual_four_hundred_fiftieth/FOUR_HUNDRED_FIFTIETH_33_COMPONENT_INVENTORY.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    h_events = read(H_EVENTS)
    b_events = read(B_EVENTS)
    h_cards = {row["joint_tuple_id"]: row for row in read(H_CARDS)}
    b_cards = {row["joint_tuple_id"]: row for row in read(B_CARDS)}
    generator = {row["joint_tuple_id"]: row for row in read(B_GENERATOR)}
    bio_wholes = {row["joint_tuple_id"]: row for row in read(B_WHOLES)}
    shared = set(h_cards) & set(b_cards)
    for joint_id in shared:
        if h_cards[joint_id]["small_value_de"] != b_cards[joint_id]["small_value_de"]:
            raise ValueError((joint_id, h_cards[joint_id]["small_value_de"], b_cards[joint_id]["small_value_de"]))

    card_rules: dict[str, dict[str, str]] = {}
    for joint_id, row in b_cards.items():
        if joint_id in generator:
            card_rules[joint_id] = {
                "component_parse": generator[joint_id]["normalized_components"],
                "small_value_de": row["small_value_de"], "lexicon_class": "PRODUCTIVE_COMPOSITION",
                "rule_source": "BIOLOGICAL_33_COMPONENT_MANUAL",
            }
        elif joint_id in bio_wholes:
            card_rules[joint_id] = {
                "component_parse": f"WHOLE[{row['surfaces']}]", "small_value_de": row["small_value_de"],
                "lexicon_class": "MEMORIZED_WHOLE_CARD", "rule_source": "BIOLOGICAL_SEVEN_WHOLE_CARDS",
            }
        else:
            raise ValueError(f"unclassified Biological card {joint_id}")
    for joint_id, row in h_cards.items():
        if joint_id in card_rules:
            continue
        if row["completion_class"] == "HERBAL_WHOLE_CARD":
            lexicon_class = "MEMORIZED_WHOLE_CARD"
        else:
            lexicon_class = "PRODUCTIVE_COMPOSITION"
        card_rules[joint_id] = {
            "component_parse": row["component_parse"], "small_value_de": row["small_value_de"],
            "lexicon_class": lexicon_class, "rule_source": row["completion_class"],
        }

    combined_events = []
    for row in h_events:
        rule = card_rules[row["joint_tuple_id"]]
        combined_events.append({
            "event_id": row["event_id"], "register": "HERBAL", "record_unit_id": row["record_unit_id"],
            "page": row["page"], "locus": row["locus"], "field_id": row["field_id"],
            "statement_id": row["statement_id"], "surface": row["surface"], "joint_tuple_id": row["joint_tuple_id"],
            "owner_zone": row["picture_owner"], "component_parse": rule["component_parse"],
            "small_value_de": rule["small_value_de"], "lexicon_class": rule["lexicon_class"],
        })
    for row in b_events:
        rule = card_rules[row["joint_tuple_id"]]
        combined_events.append({
            "event_id": row["event_id"], "register": "BIOLOGICAL", "record_unit_id": row["record_unit_id"],
            "page": row["page"], "locus": row["locus"], "field_id": row["field_id"],
            "statement_id": row["statement_id"], "surface": row["surface"], "joint_tuple_id": row["joint_tuple_id"],
            "owner_zone": row["owner_zone"], "component_parse": rule["component_parse"],
            "small_value_de": rule["small_value_de"], "lexicon_class": rule["lexicon_class"],
        })
    combined_events.sort(key=lambda row: int(str(row["event_id"])[1:]))
    write("FOUR_HUNDRED_FIFTY_SIXTH_381_EVENT_COMBINED_EDITION.tsv", combined_events)

    by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in combined_events:
        by_card[str(row["joint_tuple_id"])].append(row)
    dictionary = []
    for joint_id, rows in sorted(by_card.items(), key=lambda item: min(int(str(row["event_id"])[1:]) for row in item[1])):
        rule = card_rules[joint_id]
        dictionary.append({
            "card_no": f"PROC{len(dictionary) + 1:03d}", "joint_tuple_id": joint_id,
            "surfaces": "|".join(sorted({str(row["surface"]) for row in rows})),
            "events": len(rows), "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "registers": "|".join(sorted({str(row["register"]) for row in rows})),
            "records": "|".join(sorted({str(row["record_unit_id"]) for row in rows})),
            "component_parse": rule["component_parse"], "small_value_de": rule["small_value_de"],
            "lexicon_class": rule["lexicon_class"], "rule_source": rule["rule_source"],
        })
    write("FOUR_HUNDRED_FIFTY_SIXTH_173_CARD_COMBINED_DICTIONARY.tsv", dictionary)

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in combined_events:
        by_statement[str(row["statement_id"])].append(row)
    statements = []
    for statement_id, rows in by_statement.items():
        statements.append({
            "statement_id": statement_id, "register": rows[0]["register"], "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"], "owner_zones": "|".join(dict.fromkeys(str(row["owner_zone"]) for row in rows)),
            "events": len(rows), "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "field_ids": "|".join(dict.fromkeys(str(row["field_id"]) for row in rows)),
            "component_chain": " > ".join(str(row["component_parse"]) for row in rows),
            "literal_reading_de": "; ".join(str(row["small_value_de"]) for row in rows) + ".",
        })
    write("FOUR_HUNDRED_FIFTY_SIXTH_116_STATEMENT_COMBINED_EDITION.tsv", statements)

    shared_rows = []
    for joint_id in sorted(shared, key=lambda item: min(int(str(row["event_id"])[1:]) for row in by_card[item])):
        rows = by_card[joint_id]
        shared_rows.append({
            "joint_tuple_id": joint_id, "surfaces": "|".join(sorted({str(row["surface"]) for row in rows})),
            "component_parse": card_rules[joint_id]["component_parse"], "small_value_de": card_rules[joint_id]["small_value_de"],
            "herbal_events": sum(row["register"] == "HERBAL" for row in rows),
            "biological_events": sum(row["register"] == "BIOLOGICAL" for row in rows),
            "value_collision": "NO",
        })
    write("FOUR_HUNDRED_FIFTY_SIXTH_17_CROSS_REGISTER_CARDS.tsv", shared_rows)

    component_rows = [dict(row) for row in read(COMPONENTS)]
    component_rows.extend([
        {"component": "HO", "role": "ARGUMENT", "value_de": "Zutat", "support_cards": "5", "teaching_status": "HERBAL_COMPONENT_EXTENSION"},
        {"component": "CHEO", "role": "ARGUMENT", "value_de": "Auszug", "support_cards": "2", "teaching_status": "HERBAL_COMPONENT_EXTENSION"},
    ])
    for component in component_rows:
        token = component["component"]
        card_ids = {row["joint_tuple_id"] for row in dictionary if row["lexicon_class"] == "PRODUCTIVE_COMPOSITION" and token in row["component_parse"].split("+")}
        component["combined_support_cards"] = len(card_ids)
        component["herbal_events"] = sum(row["register"] == "HERBAL" and row["joint_tuple_id"] in card_ids for row in combined_events)
        component["biological_events"] = sum(row["register"] == "BIOLOGICAL" and row["joint_tuple_id"] in card_ids for row in combined_events)
        component["register_scope"] = "BOTH" if component["herbal_events"] and component["biological_events"] else ("HERBAL_ONLY" if component["herbal_events"] else "BIOLOGICAL_ONLY")
    write("FOUR_HUNDRED_FIFTY_SIXTH_35_COMPONENT_MANUAL.tsv", component_rows)

    wholes = [row for row in dictionary if row["lexicon_class"] == "MEMORIZED_WHOLE_CARD"]
    write("FOUR_HUNDRED_FIFTY_SIXTH_TEN_WHOLE_CARDS.tsv", wholes)

    by_value: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in dictionary:
        by_value[str(row["small_value_de"])].append(row)
    aliases = []
    for value, rows in sorted(by_value.items()):
        if len(rows) < 2:
            continue
        aliases.append({
            "small_value_de": value, "cards": len(rows),
            "joint_tuple_ids": "|".join(str(row["joint_tuple_id"]) for row in rows),
            "surfaces": " || ".join(str(row["surfaces"]) for row in rows),
            "registers": "|".join(sorted({register for row in rows for register in str(row["registers"]).split("|")})),
            "distinction_needed": "YES_EXACT_CARD_CHOICE_REMAINS",
        })
    write("FOUR_HUNDRED_FIFTY_SIXTH_VALUE_ALIAS_FAMILIES.tsv", aliases)

    summary = {
        "status": "PASS", "cards": len(dictionary), "events": len(combined_events), "statements": len(statements),
        "components": len(component_rows), "productive_cards": sum(row["lexicon_class"] == "PRODUCTIVE_COMPOSITION" for row in dictionary),
        "productive_events": sum(row["lexicon_class"] == "PRODUCTIVE_COMPOSITION" for row in combined_events),
        "whole_cards": len(wholes), "whole_events": sum(row["lexicon_class"] == "MEMORIZED_WHOLE_CARD" for row in combined_events),
        "cross_register_cards": len(shared_rows), "cross_register_herbal_events": sum(int(row["herbal_events"]) for row in shared_rows),
        "cross_register_biological_events": sum(int(row["biological_events"]) for row in shared_rows),
        "alias_families": len(aliases),
    }
    (HERE / "FOUR_HUNDRED_FIFTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
