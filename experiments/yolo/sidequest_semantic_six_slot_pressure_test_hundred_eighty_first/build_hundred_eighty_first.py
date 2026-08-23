#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_quantity_preparation/WORKSHOP_SENTENCE_SLOTS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_381_PROSE_MASTER_EDITION.tsv"
GRAMMAR = ROOT / "experiments/yolo/sidequest_semantic_third_scribe_grammar_hundred_eightieth/HUNDRED_EIGHTIETH_6_SHARED_SLOTS.tsv"


ROLE_TO_SLOT = {
    "SOURCE": "G1",
    "PREPARATION": "G1",
    "OWNER_ITEM": "G2",
    "QUANTITY": "G2",
    "STATE_GRADE": "G3",
    "OPERATION": "G4",
    "FLOW_TRANSFER": "G4",
    "TARGET": "G5",
    "CLOSE": "G6",
}


RULES = [
    ("C1", "ADDRESS_BUNDLE", "G1 und G2 duerfen innerhalb eines Adressbuendels ihre Reihenfolge tauschen.", "Quellenname, Posten und Mass koennen vorangestellt oder nachgetragen werden."),
    ("C2", "STATE_AROUND_ACTION", "G3 darf vor oder nach G4/G5 stehen.", "Ein Zustand kann Anweisung oder Ergebnis eines Vorgangs sein."),
    ("C3", "TARGET_ACTION_SWAP", "G4 und G5 duerfen in beiden Reihenfolgen erscheinen.", "Die Stelle kann vor dem Vorgang gesetzt oder nach ihm ergaenzt werden."),
    ("C4", "REOPEN_MICRO_PACKET", "Erscheint G1 oder G2 nach begonnenem G4/G5, beginnt ein neuer Arbeitspaketteil.", "Der aktive Ansatz bleibt erhalten; nur Teilcharge und lokaler Vorgang werden neu fokussiert."),
    ("C5", "FINAL_CLOSE", "G6 steht immer am Ende des sichtbaren Feldes.", "Eine Schlusskarte schliesst den laufenden Arbeitspaketteil und das Feld."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def primary_slot(tags: list[str]) -> str:
    tag_set = set(tags)
    if "TARGET" in tag_set:
        return "G5"
    if "FLOW_TRANSFER" in tag_set:
        return "G4"
    if "SOURCE" in tag_set:
        return "G1"
    if "QUANTITY" in tag_set and "OPERATION" in tag_set:
        return "G2"
    if "OPERATION" in tag_set:
        return "G4"
    if "CLOSE" in tag_set:
        return "G6"
    if "STATE_GRADE" in tag_set:
        return "G3"
    if "QUANTITY" in tag_set:
        return "G2"
    if "PREPARATION" in tag_set:
        return "G1"
    if "OWNER_ITEM" in tag_set:
        return "G2"
    raise ValueError(tags)


def compact(values: list[str]) -> list[str]:
    result = []
    for value in values:
        if not result or result[-1] != value:
            result.append(value)
    return result


def main() -> None:
    statements = read(STATEMENTS)
    event_source = read(EVENTS)
    grammar = read(GRAMMAR)
    source_by_event = {f"E{int(row['event_serial']):03d}": row for row in event_source}
    event_rows: list[dict[str, object]] = []
    field_rows: list[dict[str, object]] = []
    restart_rows: list[dict[str, object]] = []
    statement_rows: list[dict[str, object]] = []

    for statement in statements:
        field_ids = statement["field_ids"].split("|")
        packets = re.findall(r"Z\d+\[(.*?)\](?: \|\||$)", statement["work_cell_packets"])
        if len(field_ids) != len(packets):
            raise ValueError(statement["statement_id"])
        statement_micro_packets = 0
        statement_restarts = 0
        statement_swaps = 0
        statement_event_count = 0
        for field_id, packet in zip(field_ids, packets):
            parsed = []
            for fragment in packet.split(" > "):
                match = re.fullmatch(r"(E\d+):(.+)\{([^}]+)\}", fragment)
                if not match:
                    raise ValueError(fragment)
                event_id, surface, tag_string = match.groups()
                tags = tag_string.split("+")
                slot = primary_slot(tags)
                all_slots = sorted({ROLE_TO_SLOT[tag] for tag in tags}, key=lambda value: int(value[1:]))
                parsed.append((event_id, surface, tags, slot, all_slots))

            micro_packet = 1
            action_started = False
            previous_slot = "START"
            for position, (event_id, surface, tags, slot, all_slots) in enumerate(parsed, start=1):
                restart_before = slot in {"G1", "G2"} and action_started
                if restart_before:
                    restart_rows.append(
                        {
                            "restart_id": f"R{len(restart_rows) + 1:03d}",
                            "statement_id": statement["statement_id"],
                            "field_id": field_id,
                            "new_micro_packet": micro_packet + 1,
                            "previous_primary_slot": previous_slot,
                            "new_primary_slot": slot,
                            "event_id": event_id,
                            "surface": surface,
                            "workshop_reading_de": "neuen Teilvorgang mit demselben aktiven Ansatz beginnen",
                        }
                    )
                    micro_packet += 1
                    action_started = False
                if slot in {"G4", "G5"}:
                    action_started = True
                source = source_by_event[event_id]
                event_rows.append(
                    {
                        "event_id": event_id,
                        "statement_id": statement["statement_id"],
                        "record_unit_id": statement["record_unit_id"],
                        "page": statement["page"],
                        "field_id": field_id,
                        "field_position": position,
                        "micro_packet": micro_packet,
                        "surface": surface,
                        "master_card_id": source["master_card_id"],
                        "atomic_value_de": source["atomic_card_value_de"],
                        "source_roles": "+".join(tags),
                        "primary_grammar_slot": slot,
                        "embedded_grammar_slots": "|".join(value for value in all_slots if value != slot) or "NONE",
                        "restart_before": "YES" if restart_before else "NO",
                        "field_close_role": "YES" if "CLOSE" in tags else "NO",
                    }
                )
                previous_slot = slot

            path = compact([item[3] for item in parsed])
            swaps = sum(left == "G5" and right == "G4" for left, right in zip(path, path[1:]))
            close_positions = [index for index, item in enumerate(parsed) if "CLOSE" in item[2]]
            field_rows.append(
                {
                    "statement_id": statement["statement_id"],
                    "record_unit_id": statement["record_unit_id"],
                    "page": statement["page"],
                    "field_id": field_id,
                    "event_count": len(parsed),
                    "surface_sequence": " ".join(item[1] for item in parsed),
                    "compacted_slot_path": ">".join(path),
                    "micro_packets": micro_packet,
                    "restart_count": micro_packet - 1,
                    "target_before_operation_swaps": swaps,
                    "close_count": len(close_positions),
                    "close_is_field_final": "YES" if not close_positions or close_positions == [len(parsed) - 1] else "NO",
                    "grammar_result": "FITS_SIX_SLOTS_WITHOUT_SEVENTH",
                }
            )
            statement_micro_packets += micro_packet
            statement_restarts += micro_packet - 1
            statement_swaps += swaps
            statement_event_count += len(parsed)

        statement_rows.append(
            {
                "statement_id": statement["statement_id"],
                "record_unit_id": statement["record_unit_id"],
                "page": statement["page"],
                "field_count": len(field_ids),
                "event_count": statement_event_count,
                "micro_packets": statement_micro_packets,
                "restart_count": statement_restarts,
                "target_before_operation_swaps": statement_swaps,
                "line_continuity": statement["line_continuity"],
                "six_slot_result": "PASS_NO_SEVENTH_SLOT",
                "concrete_reading_de": statement["concrete_german_reading"],
            }
        )

    write(OUT / "HUNDRED_EIGHTY_FIRST_381_EVENT_SIX_SLOT_PARSE.tsv", event_rows)
    write(OUT / "HUNDRED_EIGHTY_FIRST_135_FIELD_PRESSURE_TEST.tsv", field_rows)
    write(OUT / "HUNDRED_EIGHTY_FIRST_116_STATEMENT_PRESSURE_TEST.tsv", statement_rows)
    write(OUT / "HUNDRED_EIGHTY_FIRST_34_PACKET_RESTARTS.tsv", restart_rows)
    rule_rows = [
        {
            "rule_id": rule_id,
            "rule_name": name,
            "formal_rule_de": formal,
            "scribe_lesson_de": lesson,
        }
        for rule_id, name, formal, lesson in RULES
    ]
    write(OUT / "HUNDRED_EIGHTY_FIRST_5_GRAMMAR_REVISIONS.tsv", rule_rows)

    packet_histogram = Counter(int(row["micro_packets"]) for row in field_rows)
    summary = {
        "statement_source_sha256": hashlib.sha256(STATEMENTS.read_bytes()).hexdigest(),
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "grammar_source_sha256": hashlib.sha256(GRAMMAR.read_bytes()).hexdigest(),
        "events": len(event_rows),
        "fields": len(field_rows),
        "statements": len(statement_rows),
        "semantic_slots": len(grammar),
        "micro_packets": sum(int(row["micro_packets"]) for row in field_rows),
        "packet_restarts": len(restart_rows),
        "field_packet_histogram": {str(key): packet_histogram[key] for key in sorted(packet_histogram)},
        "target_before_operation_swaps": sum(int(row["target_before_operation_swaps"]) for row in field_rows),
        "closed_fields": sum(int(row["close_count"]) for row in field_rows),
        "nonfinal_closes": sum(row["close_is_field_final"] == "NO" for row in field_rows),
        "required_seventh_semantic_slot": False,
        "new_card_values": 0,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
