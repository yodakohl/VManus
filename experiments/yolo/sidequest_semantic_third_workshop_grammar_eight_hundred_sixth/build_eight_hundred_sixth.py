#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
COMPONENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_39_COMPONENT_DICTIONARY.tsv"
CARDS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_173_CARD_DICTIONARY.tsv"
EVENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
STATEMENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv"

CORE22 = set("OK OT OL K L CHD E EE EEE AIIN AIN AL AR Y DY CH SH CTH CHK SHED P LSH".split())
STRIP9 = set("SOLK T AIR OR HO CKH O IIN R".split())
VALUE_OVERRIDE = {"O": "VORGANG", "SHED": "STEHENLASSEN", "P": "EINFUELLEN", "LSH": "SPUELEN"}
REVISED_STATEMENT_FILES = [
    ROOT / "sidequest_semantic_shed_state_eight_hundred_third" / "EIGHT_HUNDRED_THIRD_15_REVISED_STATEMENTS.tsv",
    ROOT / "sidequest_semantic_p_recipient_eight_hundred_fourth" / "EIGHT_HUNDRED_FOURTH_3_REVISED_STATEMENTS.tsv",
    ROOT / "sidequest_semantic_lsh_rinse_eight_hundred_fifth" / "EIGHT_HUNDRED_FIFTH_2_REVISED_STATEMENTS.tsv",
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tier(component: str, old_category: str) -> str:
    if component in CORE22:
        return "PARADIGM_CORE22"
    if component in STRIP9:
        return "RECURRENT_RULE_STRIP9"
    if old_category == "PARADIGM_SUPPORTED_BOUND_VARIANT_OF_AIN":
        return "BOUND_VARIANT"
    if old_category == "CONTEXT_SINGLETON_COMPONENT":
        return "LOCAL_SINGLETON"
    return "MEMORIZED_WHOLE_COMMAND"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read(COMPONENTS)
    cards = read(CARDS)
    events = read(EVENTS)
    statements = read(STATEMENTS)

    component_rows = []
    for row in components:
        value = VALUE_OVERRIDE.get(row["component"], row["short_value_de"])
        component_rows.append(
            {
                "component_no": row["component_no"],
                "component": row["component"],
                "short_value_de": value,
                "grammar_tier": tier(row["component"], row["category"]),
                "exact_cards": row["exact_cards"],
                "events": row["events"],
                "teaching_rule": (
                    "compose freely in registered slot"
                    if row["component"] in CORE22
                    else "read from recurrent wall strip"
                    if row["component"] in STRIP9
                    else "use only in attested bound frame"
                    if row["category"] == "PARADIGM_SUPPORTED_BOUND_VARIANT_OF_AIN"
                    else "copy owner-local singleton"
                    if row["category"] == "CONTEXT_SINGLETON_COMPONENT"
                    else "memorize complete command card"
                ),
            }
        )
    component_by_name = {row["component"]: row for row in component_rows}

    card_rows = []
    for row in cards:
        tokens = row["component_recipe"].split("+")
        values = [component_by_name[token]["short_value_de"] for token in tokens]
        tiers = {component_by_name[token]["grammar_tier"] for token in tokens}
        if "MEMORIZED_WHOLE_COMMAND" in tiers:
            card_tier = "MEMORIZED_WHOLE_CARD"
        elif "LOCAL_SINGLETON" in tiers:
            card_tier = "LOCAL_SINGLETON_PLUS_RULES"
        elif "BOUND_VARIANT" in tiers:
            card_tier = "BOUND_VARIANT_PLUS_RULES"
        else:
            card_tier = "PRODUCTIVE_RECIPE"
        card_rows.append(
            {
                "exact_card_id": row["exact_card_id"],
                "registered_surfaces": row["registered_surfaces"],
                "component_recipe": row["component_recipe"],
                "third_grammar_reading_de": " · ".join(values),
                "events": row["events"],
                "card_tier": card_tier,
                "core22_components": "+".join(token for token in tokens if token in CORE22) or "NONE",
                "strip9_components": "+".join(token for token in tokens if token in STRIP9) or "NONE",
                "core22_touch": "YES" if set(tokens) & CORE22 else "NO",
                "fully_core22": "YES" if set(tokens) <= CORE22 else "NO",
                "copy_rule": "SPEAK_BY_RECIPE__COPY_BY_EXACT_CARD",
            }
        )
    card_by_id = {row["exact_card_id"]: row for row in card_rows}

    event_rows = []
    for row in events:
        card = card_by_id[row["card_no"]]
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "owner_de": row["owner_de"],
                "exact_card_id": row["card_no"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "third_grammar_reading_de": card["third_grammar_reading_de"],
                "card_tier": card["card_tier"],
                "core22_touch": card["core22_touch"],
                "fully_core22": card["fully_core22"],
                "form_owner_boundary_status": row["form_owner_boundary_status"],
            }
        )

    revised_text = {row["statement_id"]: row["clean_workshop_reading_de"] for row in statements}
    revision_sources: dict[str, list[str]] = defaultdict(list)
    for path in REVISED_STATEMENT_FILES:
        for row in read(path):
            revised_text[row["statement_id"]] = row["revised_reading_de"]
            revision_sources[row["statement_id"]].append(path.parent.name)

    event_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        event_by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for row in statements:
        selected = event_by_statement[row["statement_id"]]
        statement_rows.append(
            {
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "owner_noun_de": row["owner_noun_de"],
                "events": len(selected),
                "surface_sequence": row["surface_sequence"],
                "component_sequence": " | ".join(event["component_recipe"] for event in selected),
                "third_grammar_literal_de": " | ".join(event["third_grammar_reading_de"] for event in selected),
                "working_reading_de": revised_text[row["statement_id"]],
                "fully_core22_events": sum(event["fully_core22"] == "YES" for event in selected),
                "strip9_touch_events": sum(bool(event["component_recipe"] and set(event["component_recipe"].split("+")) & STRIP9) for event in selected),
                "revision_sources": ",".join(revision_sources[row["statement_id"]]) or "PASS739_UNCHANGED",
            }
        )

    predictions: dict[str, dict[str, str]] = {}
    prediction_proposals = 0

    def add_prediction(surface: str, recipe: str, reading: str, source: str) -> None:
        nonlocal prediction_proposals
        prediction_proposals += 1
        if surface in predictions:
            old = predictions[surface]
            if old["component_recipe"] != recipe or old["working_reading_de"] != reading:
                raise ValueError(f"prediction conflict at {surface}")
            old["source"] = ",".join(sorted(set(old["source"].split(",")) | {source}))
        else:
            predictions[surface] = {"predicted_surface": surface, "component_recipe": recipe, "working_reading_de": reading, "source": source}

    for row in read(ROOT / "sidequest_semantic_second_workshop_grammar_seven_hundred_ninety_ninth" / "SEVEN_HUNDRED_NINETY_NINTH_56_UNATTESTED_PREDICTIONS.tsv"):
        add_prediction(row["predicted_surface"], row["component_recipe"], row["working_reading_de"], row["source_passes"])
    for row in read(ROOT / "sidequest_semantic_process_grade_eight_hundred_first" / "EIGHT_HUNDRED_FIRST_CHK_GRADE_GRID.tsv"):
        if not row["status"].startswith("PREDICTED"):
            continue
        for surface in row["surfaces"].split("|"):
            add_prediction(surface, row["component_recipe"], row["reading_de"], "PASS801_CHK_GRID")
    for row in read(ROOT / "sidequest_semantic_lsh_rinse_eight_hundred_fifth" / "EIGHT_HUNDRED_FIFTH_6_LSH_GRADE_CELLS.tsv"):
        if row["status"] != "PREDICTED_UNATTESTED":
            continue
        add_prediction(row["surface"], row["component_recipe"], row["reading_de"], "PASS805_LSH_GRID")
    attested_surfaces = {row["surface"] for row in events}
    prediction_rows = []
    for surface, row in sorted(predictions.items()):
        prediction_rows.append({**row, "attested_on_fixed_pages": "YES" if surface in attested_surfaces else "NO", "use_status": "PREDICTION_ONLY"})

    rules = [
        (1, "CORE22_RECIPE", "read the 22 productive components in registered order"),
        (2, "EXACT_CARD_PACKING", "copy the learned exact surface for that recipe"),
        (3, "ACTION_CH_SH_CTH", "choose take, hold, or prepare in the action slot"),
        (4, "CONTROL_OK_OT_OL", "choose start, next, or continue at the left edge"),
        (5, "TRANSFER_K_L_CHD", "add, guide, and transfer may stack in that order"),
        (6, "GRADE_E_EE_EEE", "choose short, long, or full only in a registered grade slot"),
        (7, "QUANTITY_AIIN_AIN", "distinguish prescribed measure from portion"),
        (8, "ADDRESS_AL_AR", "distinguish owner-local target from source"),
        (9, "ENDPOINT_Y_DY", "keep item active or close with the licensed endpoint card"),
        (10, "CHK_GRADE_BOARD", "warming accepts the grade and endpoint board"),
        (11, "SHED_PROCESS", "leave standing; do not infer sediment"),
        (12, "P_RECIPIENT", "fill inward toward the owner-local receiver"),
        (13, "LSH_RINSE", "rinse as verb or in the compound rinse-cycle"),
    ]
    rule_rows = [{"priority": n, "rule": rule, "instruction": instruction} for n, rule, instruction in rules]

    write("EIGHT_HUNDRED_SIXTH_39_COMPONENT_THIRD_GRAMMAR.tsv", component_rows, ["component_no", "component", "short_value_de", "grammar_tier", "exact_cards", "events", "teaching_rule"])
    write("EIGHT_HUNDRED_SIXTH_173_CARD_THIRD_DICTIONARY.tsv", card_rows, ["exact_card_id", "registered_surfaces", "component_recipe", "third_grammar_reading_de", "events", "card_tier", "core22_components", "strip9_components", "core22_touch", "fully_core22", "copy_rule"])
    write("EIGHT_HUNDRED_SIXTH_381_EVENT_REPARSE.tsv", event_rows, ["event_id", "page", "record", "statement_id", "owner_de", "exact_card_id", "surface", "component_recipe", "third_grammar_reading_de", "card_tier", "core22_touch", "fully_core22", "form_owner_boundary_status"])
    write("EIGHT_HUNDRED_SIXTH_116_STATEMENT_REPARSE.tsv", statement_rows, ["statement_id", "page", "record", "owner_noun_de", "events", "surface_sequence", "component_sequence", "third_grammar_literal_de", "working_reading_de", "fully_core22_events", "strip9_touch_events", "revision_sources"])
    write("EIGHT_HUNDRED_SIXTH_64_UNATTESTED_PREDICTIONS.tsv", prediction_rows, ["predicted_surface", "component_recipe", "working_reading_de", "source", "attested_on_fixed_pages", "use_status"])
    write("EIGHT_HUNDRED_SIXTH_13_TEACHING_RULES.tsv", rule_rows, ["priority", "rule", "instruction"])

    core_touch = [row for row in card_rows if row["core22_touch"] == "YES"]
    fully_core = [row for row in card_rows if row["fully_core22"] == "YES"]
    summary = {
        "status": "PASS",
        "decision": "THIRD_GRAMMAR_REPARSES_ALL_PROSE_WITH_CORE22_AND_STRIP9",
        "components": len(component_rows),
        "core_components": sum(row["grammar_tier"] == "PARADIGM_CORE22" for row in component_rows),
        "strip_components": sum(row["grammar_tier"] == "RECURRENT_RULE_STRIP9" for row in component_rows),
        "cards": len(card_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "core_touch_cards": len(core_touch),
        "core_touch_events": sum(int(row["events"]) for row in core_touch),
        "fully_core_cards": len(fully_core),
        "fully_core_events": sum(int(row["events"]) for row in fully_core),
        "predictions": len(prediction_rows),
        "prediction_source_proposals": prediction_proposals,
        "deduplicated_prediction_proposals": prediction_proposals - len(prediction_rows),
        "prediction_collisions": sum(row["attested_on_fixed_pages"] == "YES" for row in prediction_rows),
        "rules": len(rule_rows),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / "EIGHT_HUNDRED_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
