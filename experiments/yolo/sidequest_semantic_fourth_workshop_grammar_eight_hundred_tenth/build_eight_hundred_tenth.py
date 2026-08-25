#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_third_workshop_grammar_eight_hundred_sixth"
COMPONENTS = BASE / "EIGHT_HUNDRED_SIXTH_39_COMPONENT_THIRD_GRAMMAR.tsv"
CARDS = BASE / "EIGHT_HUNDRED_SIXTH_173_CARD_THIRD_DICTIONARY.tsv"
EVENTS = BASE / "EIGHT_HUNDRED_SIXTH_381_EVENT_REPARSE.tsv"
STATEMENTS = BASE / "EIGHT_HUNDRED_SIXTH_116_STATEMENT_REPARSE.tsv"

CORE31 = set("OK OT OL K L CHD E EE EEE AIIN AIN AL AR Y DY CH SH CTH CHK SHED P LSH AIR OR HO O IIN SOLK T CKH R".split())
BOUND = {"AN"}
LOCAL = {"CFH", "S", "DA", "LD"}
WHOLE = {"OS", "RESUME_CARD", "TALAM"}
VALUE_OVERRIDE = {"IIN": "STUFE"}


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
    components = read(COMPONENTS)
    cards = read(CARDS)
    events = read(EVENTS)
    statements = read(STATEMENTS)

    component_rows = []
    for row in components:
        component = row["component"]
        value = VALUE_OVERRIDE.get(component, row["short_value_de"])
        if component in CORE31:
            tier = "PARADIGM_CORE31"
            rule = "compose freely in registered recipe slot"
        elif component in BOUND:
            tier = "BOUND_VARIANT"
            rule = "use only in attested bound frame"
        elif component in LOCAL:
            tier = "LOCAL_SINGLETON"
            rule = "copy owner-local singleton card"
        elif component in WHOLE:
            tier = "MEMORIZED_WHOLE_COMMAND"
            rule = "memorize complete command card"
        else:
            raise ValueError(component)
        component_rows.append(
            {
                "component_no": row["component_no"],
                "component": component,
                "short_value_de": value,
                "grammar_tier": tier,
                "exact_cards": row["exact_cards"],
                "events": row["events"],
                "teaching_rule": rule,
            }
        )
    by_component = {row["component"]: row for row in component_rows}

    card_rows = []
    for row in cards:
        tokens = row["component_recipe"].split("+")
        values = [by_component[token]["short_value_de"] for token in tokens]
        if set(tokens) & WHOLE:
            tier = "MEMORIZED_WHOLE_CARD"
        elif set(tokens) & LOCAL:
            tier = "LOCAL_SINGLETON_PLUS_CORE"
        elif set(tokens) & BOUND:
            tier = "BOUND_VARIANT_PLUS_CORE"
        else:
            tier = "FULLY_CORE31_RECIPE"
        card_rows.append(
            {
                "exact_card_id": row["exact_card_id"],
                "registered_surfaces": row["registered_surfaces"],
                "component_recipe": row["component_recipe"],
                "fourth_grammar_reading_de": " · ".join(values),
                "events": row["events"],
                "card_tier": tier,
                "core31_components": "+".join(token for token in tokens if token in CORE31) or "NONE",
                "core31_touch": "YES" if set(tokens) & CORE31 else "NO",
                "fully_core31": "YES" if set(tokens) <= CORE31 else "NO",
                "remainder_components": "+".join(token for token in tokens if token not in CORE31) or "NONE",
            }
        )
    by_card = {row["exact_card_id"]: row for row in card_rows}

    event_rows = []
    for row in events:
        card = by_card[row["exact_card_id"]]
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "owner_de": row["owner_de"],
                "exact_card_id": row["exact_card_id"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "fourth_grammar_reading_de": card["fourth_grammar_reading_de"],
                "card_tier": card["card_tier"],
                "core31_touch": card["core31_touch"],
                "fully_core31": card["fully_core31"],
                "form_owner_boundary_status": row["form_owner_boundary_status"],
            }
        )

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for row in statements:
        selected = by_statement[row["statement_id"]]
        statement_rows.append(
            {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "owner_noun_de": row["owner_noun_de"],
                "events": len(selected),
                "surface_sequence": row["surface_sequence"],
                "component_sequence": " | ".join(event["component_recipe"] for event in selected),
                "fourth_grammar_literal_de": " | ".join(event["fourth_grammar_reading_de"] for event in selected),
                "working_reading_de": row["working_reading_de"].replace("Arbeitsstufe", "Stufe"),
                "fully_core31_events": sum(event["fully_core31"] == "YES" for event in selected),
                "remainder_events": sum(event["fully_core31"] == "NO" for event in selected),
                "revision_sources": row["revision_sources"],
            }
        )

    remainder_rows = [
        {
            "exact_card_id": row["exact_card_id"],
            "surfaces": row["registered_surfaces"],
            "component_recipe": row["component_recipe"],
            "reading_de": row["fourth_grammar_reading_de"],
            "events": row["events"],
            "card_tier": row["card_tier"],
            "next_question": (
                "can singleton join a repeatable semantic family?"
                if row["card_tier"] == "LOCAL_SINGLETON_PLUS_CORE"
                else "is bound AN a productive suffix or one memorized variant?"
                if row["card_tier"] == "BOUND_VARIANT_PLUS_CORE"
                else "can whole command be decomposed without losing its invariant reading?"
            ),
        }
        for row in card_rows
        if row["fully_core31"] == "NO"
    ]

    predictions: dict[str, dict[str, str]] = {}
    proposal_count = 0

    def add(surface: str, recipe: str, reading: str, source: str) -> None:
        nonlocal proposal_count
        proposal_count += 1
        if surface in predictions:
            old = predictions[surface]
            if old["component_recipe"] != recipe or old["reading_de"] != reading:
                raise ValueError(f"prediction conflict {surface}")
            old["sources"] = ",".join(sorted(set(old["sources"].split(",")) | {source}))
        else:
            predictions[surface] = {"predicted_surface": surface, "component_recipe": recipe, "reading_de": reading, "sources": source}

    for row in read(BASE / "EIGHT_HUNDRED_SIXTH_64_UNATTESTED_PREDICTIONS.tsv"):
        add(row["predicted_surface"], row["component_recipe"], row["working_reading_de"], row["source"])
    for row in read(ROOT / "sidequest_semantic_procedure_place_eight_hundred_eighth" / "EIGHT_HUNDRED_EIGHTH_8_SOLK_GRID.tsv"):
        if row["status"] == "PREDICTED_UNATTESTED":
            for surface in row["surfaces"].split("|"):
                add(surface, row["component_recipe"], row["reading_de"], "PASS808_SOLK_GRID")
    for row in read(ROOT / "sidequest_semantic_final_strip_eight_hundred_ninth" / "EIGHT_HUNDRED_NINTH_5_T_GRADE_ROWS.tsv"):
        if row["status"].startswith("PREDICTED"):
            for surface in row["surfaces"].split("|"):
                add(surface, row["recipe"], row["reading_de"], "PASS809_T_GRADE")
    observed = {row["surface"] for row in events}
    prediction_rows = [
        {**row, "attested_on_fixed_pages": "YES" if surface in observed else "NO", "use_status": "PREDICTION_ONLY"}
        for surface, row in sorted(predictions.items())
    ]

    rules = [
        (1, "RECIPE", "read registered core components in order"),
        (2, "PACK", "copy the exact learned card surface"),
        (3, "OWNER", "supply pictured plant, basin, vessel, station, or local item"),
        (4, "CONTROL", "OK start; OT next; OL continue"),
        (5, "ACTION", "CH take; SH hold; CTH prepare; T apply"),
        (6, "TRANSFER", "K add; L guide; CHD transfer; P fill inward"),
        (7, "PROCESS", "CHK warm; SHED leave standing; LSH rinse; R cool"),
        (8, "MATERIAL", "AIR water; OR batch; HO ingredient"),
        (9, "PATH_PLACE", "CKH passage; SOLK collection place; O procedure"),
        (10, "QUANTITY_STAGE", "AIIN prescribed measure; AIN portion; IIN stage"),
        (11, "ADDRESS", "AL target; AR source"),
        (12, "GRADE", "E short; EE long; EEE full"),
        (13, "ENDPOINT", "Y keep current; licensed DY closes"),
        (14, "BOUND", "AN only inside its learned frame"),
        (15, "LOCAL", "copy CFH/S/DA/LD from the owner-local exemplar"),
        (16, "WHOLE", "memorize OS/RESUME/TALAM as complete command cards"),
    ]
    rule_rows = [{"priority": n, "rule": name, "instruction": instruction} for n, name, instruction in rules]

    write("EIGHT_HUNDRED_TENTH_39_COMPONENT_FOURTH_GRAMMAR.tsv", component_rows, ["component_no", "component", "short_value_de", "grammar_tier", "exact_cards", "events", "teaching_rule"])
    write("EIGHT_HUNDRED_TENTH_173_CARD_FOURTH_DICTIONARY.tsv", card_rows, ["exact_card_id", "registered_surfaces", "component_recipe", "fourth_grammar_reading_de", "events", "card_tier", "core31_components", "core31_touch", "fully_core31", "remainder_components"])
    write("EIGHT_HUNDRED_TENTH_381_EVENT_REPARSE.tsv", event_rows, ["event_id", "page", "record", "statement_id", "owner_de", "exact_card_id", "surface", "component_recipe", "fourth_grammar_reading_de", "card_tier", "core31_touch", "fully_core31", "form_owner_boundary_status"])
    write("EIGHT_HUNDRED_TENTH_116_STATEMENT_REPARSE.tsv", statement_rows, ["statement_id", "page", "record", "owner_noun_de", "events", "surface_sequence", "component_sequence", "fourth_grammar_literal_de", "working_reading_de", "fully_core31_events", "remainder_events", "revision_sources"])
    write("EIGHT_HUNDRED_TENTH_8_REMAINDER_CARDS.tsv", remainder_rows, ["exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "card_tier", "next_question"])
    write("EIGHT_HUNDRED_TENTH_69_UNATTESTED_PREDICTIONS.tsv", prediction_rows, ["predicted_surface", "component_recipe", "reading_de", "sources", "attested_on_fixed_pages", "use_status"])
    write("EIGHT_HUNDRED_TENTH_16_TEACHING_RULES.tsv", rule_rows, ["priority", "rule", "instruction"])

    touched = [row for row in card_rows if row["core31_touch"] == "YES"]
    full = [row for row in card_rows if row["fully_core31"] == "YES"]
    summary = {
        "status": "PASS",
        "decision": "FOURTH_GRAMMAR_REPARSES_PROSE_WITH_CORE31_AND_EIGHT_REMAINDER_CARDS",
        "components": len(component_rows),
        "core_components": sum(row["grammar_tier"] == "PARADIGM_CORE31" for row in component_rows),
        "bound_components": sum(row["grammar_tier"] == "BOUND_VARIANT" for row in component_rows),
        "local_components": sum(row["grammar_tier"] == "LOCAL_SINGLETON" for row in component_rows),
        "whole_components": sum(row["grammar_tier"] == "MEMORIZED_WHOLE_COMMAND" for row in component_rows),
        "cards": len(card_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "core_touch_cards": len(touched),
        "core_touch_events": sum(int(row["events"]) for row in touched),
        "fully_core_cards": len(full),
        "fully_core_events": sum(int(row["events"]) for row in full),
        "remainder_cards": len(remainder_rows),
        "remainder_events": sum(int(row["events"]) for row in remainder_rows),
        "prediction_proposals": proposal_count,
        "unique_predictions": len(prediction_rows),
        "deduplicated_prediction_rows": proposal_count - len(prediction_rows),
        "prediction_collisions": sum(row["attested_on_fixed_pages"] == "YES" for row in prediction_rows),
        "teaching_rules": len(rule_rows),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_TENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
