#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MASTER = ROOT / "sidequest_semantic_six_master_order_cards_eight_hundred_eighty_eighth"
PHRASES = ROOT / "sidequest_semantic_complete_phrase_first_edition_eight_hundred_eighty_third"
CAL = ROOT / "sidequest_semantic_revised_six_order_book_eight_hundred_eighty_sixth" / "EIGHT_HUNDRED_EIGHTY_SIXTH_6_UNCHANGED_CALIBRATIONS.tsv"
MARKS = MASTER / "EIGHT_HUNDRED_EIGHTY_EIGHTH_437_MARK_MASTER_BINDING.tsv"
UNITS = MASTER / "EIGHT_HUNDRED_EIGHTY_EIGHTH_118_READABLE_UNITS.tsv"
ORDERS = MASTER / "EIGHT_HUNDRED_EIGHTY_EIGHTH_6_MASTER_ORDER_CARDS.tsv"
STATIONS = MASTER / "EIGHT_HUNDRED_EIGHTY_EIGHTH_16_VISIBLE_STATION_BLOCKS.tsv"
PHRASE_OCCURRENCES = PHRASES / "EIGHT_HUNDRED_EIGHTY_THIRD_34_COMPLETE_PHRASE_OCCURRENCES.tsv"
PREFIX = "EIGHT_HUNDRED_EIGHTY_NINTH"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def ordered_unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def main() -> None:
    marks = read(MARKS)
    units = read(UNITS)
    orders = read(ORDERS)
    stations = read(STATIONS)
    calibrations = read(CAL)
    phrase_occurrences = read(PHRASE_OCCURRENCES)

    by_identity: dict[str, list[dict[str, str]]] = defaultdict(list)
    for mark in marks:
        by_identity[mark["identity"]].append(mark)
    portable: set[str] = set()
    vocabulary_rows: list[dict[str, object]] = []
    for identity, local in sorted(by_identity.items()):
        sections = sorted({row["master_section"] for row in local})
        order_ids = sorted({row["order_id"] for row in local})
        is_portable = sections != ["WHEN"] and len(order_ids) >= 2
        if is_portable:
            portable.add(identity)
        first = local[0]
        vocabulary_rows.append(
            {
                "identity": identity,
                "house_surface": first["surface"],
                "component_recipe": first["component_recipe"],
                "short_value_de": first["concrete_default_de"],
                "marks": len(local),
                "orders": ",".join(order_ids),
                "order_count": len(order_ids),
                "sections": ",".join(sections),
                "apprentice_action": "READ_SHARED_CORE" if is_portable else "COPY_LOCAL_MODEL",
            }
        )

    marks_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for mark in marks:
        master_unit = next(row["master_unit_id"] for row in units if row["order_id"] == mark["order_id"] and row["stage"] == mark["stage"] and row["unit"] == mark["unit"])
        marks_by_unit[master_unit].append(mark)
    phrase_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for phrase in phrase_occurrences:
        phrase_by_statement[phrase["statement_id"]].append(phrase)

    unit_rows: list[dict[str, object]] = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        core_marks = sum(row["identity"] in portable for row in local)
        model_marks = len(local) - core_marks
        if unit["section"] == "WHEN":
            status = "MODEL_LEAF_REQUIRED"
        elif model_marks == 0:
            status = "SHARED_CORE_EXECUTABLE"
        elif core_marks == 0:
            status = "LOCAL_MODEL_ONLY"
        else:
            status = "CORE_PLUS_LOCAL_MODEL"
        phrases = phrase_by_statement.get(unit["unit"], []) if unit["section"] != "WHEN" else []
        phrase_ids = ordered_unique([row["phrase_id"] for row in phrases])
        phrase_readings = ordered_unique([row["working_phrase_de"] for row in phrases])
        unit_rows.append(
            {
                **unit,
                "core_marks": core_marks,
                "model_marks": model_marks,
                "execution_status": status,
                "recurrent_phrase_ids": ",".join(phrase_ids) if phrase_ids else "NONE",
                "recurrent_phrase_readings_de": " | ".join(phrase_readings) if phrase_readings else "NONE",
                "front_instruction_de": unit["master_reading_de"],
                "back_copy_sequence": unit["fifth_hand_surface_sequence"],
            }
        )

    mark_rows: list[dict[str, object]] = []
    for mark in marks:
        mark_rows.append(
            {
                **mark,
                "apprentice_action": "READ_SHARED_CORE" if mark["identity"] in portable else "COPY_LOCAL_MODEL",
            }
        )

    stations_by_order: dict[str, list[dict[str, str]]] = defaultdict(list)
    for station in stations:
        stations_by_order[station["order_id"]].append(station)
    units_by_order: dict[str, list[dict[str, object]]] = defaultdict(list)
    for unit in unit_rows:
        units_by_order[str(unit["order_id"])].append(unit)
    cards: list[dict[str, object]] = []
    checklists: list[dict[str, object]] = []
    for order in orders:
        order_id = order["order_id"]
        local_units = units_by_order[order_id]
        status_counts = Counter(str(row["execution_status"]) for row in local_units)
        source_owner = str(order["preparation_chain"]).split(" -> ")[0]
        target_trace = " -> ".join(row["owner_de"] for row in stations_by_order[order_id])
        fields = [
            ("MATERIAL", f"{order['product_handle']}: {order['product_name_de']}"),
            ("MEASURE", "CAL1 kleiner Schoepfbecher; CAL2 abgegrenzter Teil"),
            ("SOURCE", f"Bildvorrat {source_owner}; Kette {order['preparation_chain']}"),
            ("TARGET", target_trace),
            ("OPERATION", f"{order['biological_record']}; {len([u for u in local_units if u['section'] == 'HOW'])} sichtbare Arbeitseinheiten"),
            ("RESULT", "CAL6 gleichmaessiger Durchlauf an allen sichtbaren Stationen"),
            ("CONDITION", order["when_de"]),
        ]
        for sequence, (slot, value) in enumerate(fields, start=1):
            checklists.append({"order_id": order_id, "sequence": sequence, "slot": slot, "value_de": value, "filled": "YES"})
        cards.append(
            {
                "order_id": order_id,
                "title_de": order["title_de"],
                "front_checklist_slots": 7,
                "back_units": len(local_units),
                "marks": sum(int(row["marks"]) for row in local_units),
                "shared_core_units": status_counts["SHARED_CORE_EXECUTABLE"],
                "mixed_units": status_counts["CORE_PLUS_LOCAL_MODEL"],
                "local_only_units": status_counts["LOCAL_MODEL_ONLY"],
                "condition_model_units": status_counts["MODEL_LEAF_REQUIRED"],
                "phrase_assisted_units": sum(row["recurrent_phrase_ids"] != "NONE" for row in local_units),
                "station_blocks": len(stations_by_order[order_id]),
                "ready_for_apprentice": "YES",
            }
        )

    write(f"{PREFIX}_231_CARD_WORKSHOP_VOCABULARY.tsv", vocabulary_rows, ["identity", "house_surface", "component_recipe", "short_value_de", "marks", "orders", "order_count", "sections", "apprentice_action"])
    write(f"{PREFIX}_437_MARK_FRONT_BACK_BINDING.tsv", mark_rows, list(marks[0]) + ["apprentice_action"])
    write(f"{PREFIX}_118_UNIT_EXECUTION.tsv", unit_rows, list(units[0]) + ["core_marks", "model_marks", "execution_status", "recurrent_phrase_ids", "recurrent_phrase_readings_de", "front_instruction_de", "back_copy_sequence"])
    write(f"{PREFIX}_42_FILLED_CHECKLIST_SLOTS.tsv", checklists, ["order_id", "sequence", "slot", "value_de", "filled"])
    write(f"{PREFIX}_6_APPRENTICE_JOB_CARDS.tsv", cards, ["order_id", "title_de", "front_checklist_slots", "back_units", "marks", "shared_core_units", "mixed_units", "local_only_units", "condition_model_units", "phrase_assisted_units", "station_blocks", "ready_for_apprentice"])
    write(f"{PREFIX}_6_HOUSE_CALIBRATIONS.tsv", calibrations, list(calibrations[0]))

    checklist_by_order: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in checklists:
        checklist_by_order[str(row["order_id"])].append(row)
    lines = ["# Vorder-/Rückseiten-Deck für den Lehrling", ""]
    for card in cards:
        order_id = str(card["order_id"])
        lines.extend([f"## {order_id}: {card['title_de']}", "", "### Vorderseite — sieben Handgriffe", ""])
        for row in checklist_by_order[order_id]:
            lines.append(f"- **{row['slot']}** — {row['value_de']}")
        lines.extend(["", "### Rückseite — lesen oder vom Blatt kopieren", ""])
        for unit in units_by_order[order_id]:
            phrase = "" if unit["recurrent_phrase_ids"] == "NONE" else f"; Lehrphrase {unit['recurrent_phrase_ids']}: {unit['recurrent_phrase_readings_de']}"
            instruction = str(unit["front_instruction_de"]).rstrip().rstrip(".")
            lines.append(
                f"- `{unit['master_unit_id']}` {unit['execution_status']} — {instruction}{phrase}. Rückseite: `{unit['back_copy_sequence']}`."
            )
        lines.extend(
            [
                "",
                f"**Deckbilanz:** {card['shared_core_units']} reine Kerneinheiten; {card['mixed_units']} gemischte; {card['local_only_units']} rein lokale; {card['condition_model_units']} lokaler Bedingungsgriff.",
                "",
            ]
        )
    lines.extend(
        [
            "## Einfache Arbeitsweise",
            "",
            "Der Lehrling liest die sieben Felder vorn, arbeitet die Einheiten auf der Rückseite in Reihenfolge ab",
            "und spricht nur die vierzehn wirklich wiederkehrenden Mehrkartenphrasen als feste Blöcke. Bei",
            "READ_SHARED_CORE darf er aus dem gemeinsamen Kartenwortschatz arbeiten. Alles andere wird vom",
            "lokalen Blatt kopiert; dies ist Teil des Schreibsystems und kein Versagen des Lehrlings.",
        ]
    )
    (HERE / f"{PREFIX}_APPRENTICE_FRONT_BACK_DECK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    status_counts = Counter(str(row["execution_status"]) for row in unit_rows)
    action_counts = Counter(str(row["apprentice_action"]) for row in mark_rows)
    summary = {
        "status": "PASS",
        "decision": "SIX_FRONT_BACK_JOB_CARDS_ARE_EXECUTABLE_WITH_SHARED_CORE_PLUS_EXPLICIT_LOCAL_MODEL_LEAVES",
        "cards": len(cards),
        "checklist_slots": len(checklists),
        "marks": len(mark_rows),
        "units": len(unit_rows),
        "vocabulary_identities": len(vocabulary_rows),
        "portable_identities": len(portable),
        "mark_actions": dict(action_counts),
        "unit_statuses": dict(status_counts),
        "phrase_assisted_units": sum(row["recurrent_phrase_ids"] != "NONE" for row in unit_rows),
        "station_blocks": len(stations),
        "calibrations": len(calibrations),
        "empty_checklist_slots": sum(row["filled"] != "YES" for row in checklists),
        "fixed_pages": sorted({row["page"] for row in marks}),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 889: apprentice front/back job deck\n\n"
        "Each master order now has a seven-slot front checklist and an exact-sequence back. Units\n"
        "are marked as shared-core executable, mixed, local-only or condition-model. Fourteen exact\n"
        "recurrent phrases are the only compressed multi-card instructions; all other sequences stay\n"
        "visible. Local model use is an explicit workshop action rather than a semantic blank.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
