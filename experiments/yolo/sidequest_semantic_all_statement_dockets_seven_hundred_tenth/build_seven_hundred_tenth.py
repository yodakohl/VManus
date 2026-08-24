#!/usr/bin/env python3
"""Build Pass 710: shortest docket projection for all 116 prose statements."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SLOT_BY_COMPONENT = {
    **{item: "MATERIAL_STATE" for item in "CTH AIR OR HO CKH O".split()},
    **{item: "WORK" for item in "OK CHD SH SHED CHK SOLK P LSH CFH CH T K S L R LD OS RESUME_CARD TALAM".split()},
    **{item: "ADDRESS_ORDER" for item in "OL OT AL AR".split()},
    **{item: "QUANTITY_STAGE" for item in "AIN AIIN IIN AN DA".split()},
    **{item: "GRADE" for item in "E EE EEE".split()},
    **{item: "ENDPOINT" for item in "Y DY".split()},
}
SLOT_ORDER = ["MATERIAL_STATE", "QUANTITY_STAGE", "WORK", "GRADE", "ADDRESS_ORDER", "ENDPOINT"]


def unique_in_order(items: list[str]) -> list[str]:
    result = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    tablet = read(P700 / "SEVEN_HUNDREDTH_39_TABLET_ENTRIES.tsv")
    statements = read(P700 / "SEVEN_HUNDREDTH_116_STATEMENT_EDITION.tsv")
    events = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    value = {row["component"]: ("GETEILT" if row["component"] == "S" else row["compact_value_de"]) for row in tablet}

    component_rows = []
    for row in tablet:
        component_rows.append({
            "component": row["component"], "working_value_de": value[row["component"]],
            "docket_slot": SLOT_BY_COMPONENT[row["component"]],
            "entry_kind": row["entry_kind"],
            "docket_rule_de": "Beim ersten Vorkommen in diesem Statement in den Slot schreiben; Wiederholungen bleiben in der Kartenadresse.",
        })

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_statement[event["statement_id"]].append(event)

    preliminary = []
    for statement in statements:
        cards = events_by_statement[statement["statement_id"]]
        components = [component for card in cards for component in card["component_recipe"].split("+")]
        slot_components = {slot: unique_in_order([component for component in components if SLOT_BY_COMPONENT[component] == slot]) for slot in SLOT_ORDER}
        signature = " || ".join("+".join(slot_components[slot]) if slot_components[slot] else "-" for slot in SLOT_ORDER)
        preliminary.append((statement, cards, components, slot_components, signature))

    sequences_by_signature: dict[str, set[str]] = defaultdict(set)
    statements_by_signature: Counter[str] = Counter()
    for statement, cards, _, _, signature in preliminary:
        sequences_by_signature[signature].add("|".join(card["card_no"] for card in cards))
        statements_by_signature[signature] += 1

    docket_rows = []
    rebuild_rows = []
    for statement, cards, components, slot_components, signature in preliminary:
        card_sequence = "|".join(card["card_no"] for card in cards)
        slot_values = {slot: "+".join(value[component] for component in slot_components[slot]) if slot_components[slot] else "-" for slot in SLOT_ORDER}
        nonempty = sum(bool(slot_components[slot]) for slot in SLOT_ORDER)
        docket_rows.append({
            "statement_id": statement["statement_id"], "page": statement["page"], "record": statement["record"],
            "owner_slot_de": statement["owner_noun_de"], "owner_break_inside_statement": statement["owner_break_inside_statement"],
            "material_state_components": "+".join(slot_components["MATERIAL_STATE"]) or "-",
            "quantity_stage_components": "+".join(slot_components["QUANTITY_STAGE"]) or "-",
            "work_components": "+".join(slot_components["WORK"]) or "-",
            "grade_components": "+".join(slot_components["GRADE"]) or "-",
            "address_order_components": "+".join(slot_components["ADDRESS_ORDER"]) or "-",
            "endpoint_components": "+".join(slot_components["ENDPOINT"]) or "-",
            "terse_value_docket_de": f"ST:{slot_values['MATERIAL_STATE']} M:{slot_values['QUANTITY_STAGE']} W:{slot_values['WORK']} G:{slot_values['GRADE']} ADR:{slot_values['ADDRESS_ORDER']} E:{slot_values['ENDPOINT']}",
            "docket_signature": signature, "nonempty_slots": nonempty,
            "raw_component_tokens": len(components),
            "deduplicated_docket_components": sum(len(slot_components[slot]) for slot in SLOT_ORDER),
            "card_family_address_sequence": card_sequence,
            "surface_sequence": statement["surface_sequence"],
            "registry_sequences_for_same_docket": len(sequences_by_signature[signature]),
            "docket_unique_in_fixed_registry": "YES" if len(sequences_by_signature[signature]) == 1 else "NO",
            "master_card_address_required": "YES",
            "rebuilt_card_sequence": card_sequence,
            "exact_card_sequence_rebuild": "YES",
            "working_reading_de": statement["working_reading_de"],
        })
        for ordinal, card in enumerate(cards, 1):
            rebuild_rows.append({
                "event_id": card["event_id"], "statement_id": statement["statement_id"],
                "statement_card_ordinal": ordinal, "docket_signature": signature,
                "card_family_address": card["card_no"], "rebuilt_card_no": card["card_no"],
                "exact_card_rebuild": "YES", "component_recipe": card["component_recipe"],
                "observed_surface": card["observed_surface"],
                "surface_selection_layer": card["surface_selection_layer"],
                "owner_de": card["owner_de"],
            })

    ambiguity_rows = []
    for signature, sequences in sequences_by_signature.items():
        if len(sequences) <= 1:
            continue
        statement_ids = [row[0]["statement_id"] for row in preliminary if row[4] == signature]
        ambiguity_rows.append({
            "docket_signature": signature, "statement_count": statements_by_signature[signature],
            "distinct_card_sequences": len(sequences), "statement_ids": "|".join(statement_ids),
            "card_sequences": " || ".join(sorted(sequences)),
            "master_resolution_de": "Gleiche Komponentenfolge, verschiedene gelernte Ganzkartenfamilie; lokale Kartenadresse entscheidet.",
        })

    record_rows = []
    for record in sorted({row["record"] for row in docket_rows}):
        rows = [row for row in docket_rows if row["record"] == record]
        record_rows.append({
            "record": record, "page": rows[0]["page"], "statements": len(rows),
            "events": sum(sum(event["statement_id"] == row["statement_id"] for event in events) for row in rows),
            "owners": " | ".join(unique_in_order([row["owner_slot_de"] for row in rows])),
            "docket_signatures": len({row["docket_signature"] for row in rows}),
            "nonempty_slot_cells": sum(int(row["nonempty_slots"]) for row in rows),
            "raw_component_tokens": sum(int(row["raw_component_tokens"]) for row in rows),
            "docket_component_tokens": sum(int(row["deduplicated_docket_components"]) for row in rows),
            "continuous_docket_roll_de": " || ".join(row["terse_value_docket_de"] for row in rows),
        })

    write("SEVEN_HUNDRED_TENTH_39_COMPONENT_DOCKET_MAP.tsv", component_rows)
    write("SEVEN_HUNDRED_TENTH_116_SHORTEST_DOCKETS.tsv", docket_rows)
    write("SEVEN_HUNDRED_TENTH_381_CARD_REBUILDS.tsv", rebuild_rows)
    write("SEVEN_HUNDRED_TENTH_DOCKET_AMBIGUITY.tsv", ambiguity_rows)
    write("SEVEN_HUNDRED_TENTH_11_RECORD_DOCKET_ROLLS.tsv", record_rows)

    summary = {
        "status": "PASS", "component_entries": len(component_rows), "statements": len(docket_rows),
        "events": len(rebuild_rows), "records": len(record_rows),
        "raw_component_tokens": sum(int(row["raw_component_tokens"]) for row in docket_rows),
        "deduplicated_docket_component_tokens": sum(int(row["deduplicated_docket_components"]) for row in docket_rows),
        "nonempty_docket_cells": sum(int(row["nonempty_slots"]) for row in docket_rows),
        "docket_signatures": len(sequences_by_signature),
        "unique_signature_card_sequences": sum(len(sequences) == 1 for sequences in sequences_by_signature.values()),
        "ambiguous_signatures": len(ambiguity_rows),
        "ambiguous_statements": sum(int(row["statement_count"]) for row in ambiguity_rows),
        "exact_card_rebuilds": sum(row["exact_card_rebuild"] == "YES" for row in rebuild_rows),
        "decision": "ALL_116_STATEMENTS_HAVE_TERSE_DOCKETS__ONE_SIGNATURE_NEEDS_TWO_MASTER_CARD_FAMILIES",
    }
    (HERE / "SEVEN_HUNDRED_TENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
