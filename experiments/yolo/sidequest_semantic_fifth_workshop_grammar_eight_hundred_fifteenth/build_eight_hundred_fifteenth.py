#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_fourth_workshop_grammar_eight_hundred_tenth"
COMPONENTS = BASE / "EIGHT_HUNDRED_TENTH_39_COMPONENT_FOURTH_GRAMMAR.tsv"
CARDS = BASE / "EIGHT_HUNDRED_TENTH_173_CARD_FOURTH_DICTIONARY.tsv"
EVENTS = BASE / "EIGHT_HUNDRED_TENTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_TENTH_116_STATEMENT_REPARSE.tsv"

CORE33 = set("OK OT OL K L CHD E EE EEE AIIN AIN AL AR Y DY CH SH CTH CHK SHED P LSH AIR OR HO O IIN SOLK T CKH R CFH S".split())
BOUND3 = {"AN", "DA", "LD"}
WHOLE3 = {"OS", "RESUME_CARD", "TALAM"}
VALUES = {"CFH": "AUSPRESSEN", "S": "PROBE", "DA": "ZWEI", "LD": "BEFESTIGEN"}
REVISION_FILES = [
    ROOT / "sidequest_semantic_cfh_press_eight_hundred_eleventh" / "EIGHT_HUNDRED_ELEVENTH_REVISED_STATEMENT.tsv",
    ROOT / "sidequest_semantic_s_sample_eight_hundred_twelfth" / "EIGHT_HUNDRED_TWELFTH_REVISED_STATEMENT.tsv",
    ROOT / "sidequest_semantic_da_two_eight_hundred_thirteenth" / "EIGHT_HUNDRED_THIRTEENTH_REVISED_STATEMENT.tsv",
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read(COMPONENTS); cards = read(CARDS); events = read(EVENTS); statements = read(STATEMENTS)

    component_rows = []
    for row in components:
        component = row["component"]
        value = VALUES.get(component, row["short_value_de"])
        if component in CORE33:
            tier = "PARADIGM_CORE33"; rule = "compose freely in registered recipe slot"
        elif component in BOUND3:
            tier = "BOUND_COMPONENT"; rule = "use only in attested bound frame"
        elif component in WHOLE3:
            tier = "MEMORIZED_WHOLE_COMMAND"; rule = "memorize complete command card"
        else:
            raise ValueError(component)
        component_rows.append({"component_no": row["component_no"], "component": component, "short_value_de": value, "grammar_tier": tier, "exact_cards": row["exact_cards"], "events": row["events"], "teaching_rule": rule})
    by_component = {row["component"]: row for row in component_rows}

    card_rows = []
    for row in cards:
        tokens = row["component_recipe"].split("+")
        values = [by_component[token]["short_value_de"] for token in tokens]
        if set(tokens) & WHOLE3:
            tier = "MEMORIZED_WHOLE_CARD"
        elif set(tokens) & BOUND3:
            tier = "BOUND_RECIPE"
        else:
            tier = "FULLY_CORE33_RECIPE"
        card_rows.append({
            "exact_card_id": row["exact_card_id"], "registered_surfaces": row["registered_surfaces"], "component_recipe": row["component_recipe"],
            "fifth_grammar_reading_de": " · ".join(values), "events": row["events"], "card_tier": tier,
            "core33_components": "+".join(token for token in tokens if token in CORE33) or "NONE",
            "core33_touch": "YES" if set(tokens) & CORE33 else "NO", "fully_core33": "YES" if set(tokens) <= CORE33 else "NO",
            "remainder_components": "+".join(token for token in tokens if token not in CORE33) or "NONE",
        })
    by_card = {row["exact_card_id"]: row for row in card_rows}

    event_rows = []
    for row in events:
        card = by_card[row["exact_card_id"]]
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"], "statement_id": row["statement_id"], "owner_de": row["owner_de"],
            "exact_card_id": row["exact_card_id"], "surface": row["surface"], "component_recipe": row["component_recipe"],
            "fifth_grammar_reading_de": card["fifth_grammar_reading_de"], "card_tier": card["card_tier"], "core33_touch": card["core33_touch"],
            "fully_core33": card["fully_core33"], "form_owner_boundary_status": row["form_owner_boundary_status"],
        })

    revised = {row["statement_id"]: row["working_reading_de"] for row in statements}
    revision_sources: dict[str, list[str]] = defaultdict(list)
    for path in REVISION_FILES:
        for row in read(path):
            revised[row["statement_id"]] = row["revised_reading_de"]
            revision_sources[row["statement_id"]].append(path.parent.name)
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for row in statements:
        selected = by_statement[row["statement_id"]]
        old_sources = [] if row["revision_sources"] == "PASS739_UNCHANGED" else row["revision_sources"].split(",")
        sources = old_sources + revision_sources[row["statement_id"]]
        statement_rows.append({
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"], "owner_noun_de": row["owner_noun_de"], "events": len(selected),
            "surface_sequence": row["surface_sequence"], "component_sequence": " | ".join(event["component_recipe"] for event in selected),
            "fifth_grammar_literal_de": " | ".join(event["fifth_grammar_reading_de"] for event in selected), "working_reading_de": revised[row["statement_id"]],
            "fully_core33_events": sum(event["fully_core33"] == "YES" for event in selected), "remainder_events": sum(event["fully_core33"] == "NO" for event in selected),
            "revision_sources": ",".join(sources) or "PASS739_UNCHANGED",
        })

    remainder_rows = [
        {"exact_card_id": row["exact_card_id"], "surfaces": row["registered_surfaces"], "component_recipe": row["component_recipe"], "reading_de": row["fifth_grammar_reading_de"], "events": row["events"], "card_tier": row["card_tier"]}
        for row in card_rows if row["fully_core33"] == "NO"
    ]

    predictions: dict[str, dict[str, str]] = {}
    proposals = 0
    def add(surface: str, recipe: str, reading: str, source: str) -> None:
        nonlocal proposals
        proposals += 1
        if surface in predictions:
            old = predictions[surface]
            if old["component_recipe"] != recipe or old["reading_de"] != reading:
                raise ValueError(surface)
            old["sources"] = ",".join(sorted(set(old["sources"].split(",")) | {source}))
        else:
            predictions[surface] = {"predicted_surface": surface, "component_recipe": recipe, "reading_de": reading, "sources": source}
    for row in read(BASE / "EIGHT_HUNDRED_TENTH_69_UNATTESTED_PREDICTIONS.tsv"):
        add(row["predicted_surface"], row["component_recipe"], row["reading_de"], row["sources"])
    for row in read(ROOT / "sidequest_semantic_cfh_press_eight_hundred_eleventh" / "EIGHT_HUNDRED_ELEVENTH_8_CFH_GRID.tsv"):
        if row["status"] == "PREDICTED_UNATTESTED":
            add(row["surface"], row["component_recipe"], row["reading_de"], "PASS811_CFH_GRID")
    observed = {row["surface"] for row in events}
    prediction_rows = [{**row, "attested_on_fixed_pages": "YES" if surface in observed else "NO", "use_status": "PREDICTION_ONLY"} for surface, row in sorted(predictions.items())]

    rules = [
        (1, "RECIPE", "read registered core components in order"), (2, "PACK", "copy the exact learned card surface"),
        (3, "OWNER", "supply the pictured or local work owner"), (4, "CONTROL", "OK start; OT next; OL continue"),
        (5, "ACTION", "CH take; SH hold; CTH prepare; T apply"), (6, "TRANSFER", "K add; L guide; CHD transfer; P fill inward"),
        (7, "PROCESS", "CHK warm; SHED leave standing; LSH rinse; R cool; CFH press out"),
        (8, "MATERIAL", "AIR water; OR batch; HO ingredient"), (9, "PATH_PLACE", "CKH passage; SOLK collection place; O procedure"),
        (10, "QUANTITY_STAGE", "S sample; AIN portion; AIIN prescribed measure; IIN stage"),
        (11, "ADDRESS", "AL target; AR source"), (12, "GRADE", "E short; EE long; EEE full"),
        (13, "ENDPOINT", "Y keep current; licensed DY closes"),
        (14, "BOUND_AN", "use AN only in its learned after-addition frame"), (15, "BOUND_DA", "use DA as TWO only before IIN stage"),
        (16, "BOUND_LD", "use LD as FASTEN only before DY in its learned frame"), (17, "WHOLE", "memorize OS/RESUME/TALAM as complete commands"),
    ]
    rule_rows = [{"priority": n, "rule": name, "instruction": instruction} for n, name, instruction in rules]

    write("EIGHT_HUNDRED_FIFTEENTH_39_COMPONENT_FIFTH_GRAMMAR.tsv", component_rows, ["component_no", "component", "short_value_de", "grammar_tier", "exact_cards", "events", "teaching_rule"])
    write("EIGHT_HUNDRED_FIFTEENTH_173_CARD_FIFTH_DICTIONARY.tsv", card_rows, ["exact_card_id", "registered_surfaces", "component_recipe", "fifth_grammar_reading_de", "events", "card_tier", "core33_components", "core33_touch", "fully_core33", "remainder_components"])
    write("EIGHT_HUNDRED_FIFTEENTH_381_EVENT_REPARSE.tsv", event_rows, ["event_id", "page", "record", "statement_id", "owner_de", "exact_card_id", "surface", "component_recipe", "fifth_grammar_reading_de", "card_tier", "core33_touch", "fully_core33", "form_owner_boundary_status"])
    write("EIGHT_HUNDRED_FIFTEENTH_116_STATEMENT_REPARSE.tsv", statement_rows, ["statement_id", "page", "record", "owner_noun_de", "events", "surface_sequence", "component_sequence", "fifth_grammar_literal_de", "working_reading_de", "fully_core33_events", "remainder_events", "revision_sources"])
    write("EIGHT_HUNDRED_FIFTEENTH_6_REMAINDER_CARDS.tsv", remainder_rows, ["exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "card_tier"])
    write("EIGHT_HUNDRED_FIFTEENTH_76_UNATTESTED_PREDICTIONS.tsv", prediction_rows, ["predicted_surface", "component_recipe", "reading_de", "sources", "attested_on_fixed_pages", "use_status"])
    write("EIGHT_HUNDRED_FIFTEENTH_17_TEACHING_RULES.tsv", rule_rows, ["priority", "rule", "instruction"])

    touched = [row for row in card_rows if row["core33_touch"] == "YES"]; full = [row for row in card_rows if row["fully_core33"] == "YES"]
    summary = {
        "status": "PASS", "decision": "FIFTH_GRAMMAR_REPARSES_PROSE_WITH_CORE33_THREE_BOUND_AND_THREE_WHOLE_COMMANDS",
        "components": len(component_rows), "core_components": sum(row["grammar_tier"] == "PARADIGM_CORE33" for row in component_rows),
        "bound_components": sum(row["grammar_tier"] == "BOUND_COMPONENT" for row in component_rows), "whole_components": sum(row["grammar_tier"] == "MEMORIZED_WHOLE_COMMAND" for row in component_rows),
        "cards": len(card_rows), "events": len(event_rows), "statements": len(statement_rows),
        "core_touch_cards": len(touched), "core_touch_events": sum(int(row["events"]) for row in touched),
        "fully_core_cards": len(full), "fully_core_events": sum(int(row["events"]) for row in full),
        "remainder_cards": len(remainder_rows), "remainder_events": sum(int(row["events"]) for row in remainder_rows),
        "prediction_input_rows": proposals, "unique_predictions": len(prediction_rows), "prediction_collisions": sum(row["attested_on_fixed_pages"] == "YES" for row in prediction_rows),
        "teaching_rules": len(rule_rows), "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_FIFTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
