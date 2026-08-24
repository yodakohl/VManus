#!/usr/bin/env python3
"""Build a repaired six-record Biological edition from atomic values and owners."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_herbal_formula_repair_three_hundred_twenty_ninth/THREE_HUNDRED_TWENTY_NINTH_381_GLOBAL_EVENTS.tsv"
OLD_ATOMIC_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_bio_glossary_three_hundred_fourteenth/THREE_HUNDRED_FOURTEENTH_281_ATOMIC_EVENT_READINGS.tsv"
OLD_ATOMIC_DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_atomic_bio_glossary_three_hundred_fourteenth/THREE_HUNDRED_FOURTEENTH_124_ATOMIC_BIO_DICTIONARY.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_bio_station_sequences_three_hundred_eighteenth/THREE_HUNDRED_EIGHTEENTH_118_STATION_WORK_UNITS.tsv"

REPAIRED_EXPANSIONS = {
    "Sollstellung": "Stelle das Sollmaß ein",
    "Zieleinsatz": "Setze an der Zielstelle ein",
    "Quelle": "Nimm aus der bezeichneten Quelle",
    "Fortsetzung": "Führe den laufenden Gang fort",
    "Stelle": "Binde die bezeichnete Stelle",
    "Fortsetzungsansatz": "Führe denselben Ansatz weiter",
    "Umsetzschluss": "Setze um und schließe den Schritt",
    "Umsetzen": "Setze den laufenden Posten um",
    "Diesposten": "Halte diesen Posten aktiv",
    "Einsetzen": "Setze den Posten ein",
    "Vorabsetzschluss": "Setze den vorigen Posten ab und schließe",
    "Klarauszug": "Nimm den Klarauszug",
    "Absetzschluss": "Setze ab und schließe",
    "Bereit": "Halte den Posten bereit",
    "Zerkleinern": "Zerkleinere den Posten",
    "Langwärme": "Halte den Posten länger warm",
    "Fortschluss": "Führe fort und schließe",
    "Kurzabzugsschluss": "Ziehe kurz ab und schließe",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sentence_join(parts: list[str]) -> str:
    if not parts:
        return ""
    return "; dann ".join(part[0].lower() + part[1:] if i else part for i, part in enumerate(parts)) + "."


def main() -> None:
    all_events = {x["event_id"]: x for x in read(EVENTS)}
    bio_source = read(OLD_ATOMIC_EVENTS)
    bio_ids = {x["event_id"] for x in bio_source}
    bio_events = [all_events[x["event_id"]] for x in bio_source]

    old_dictionary = {x["master_card_id"]: x for x in read(OLD_ATOMIC_DICTIONARY)}
    old_event_by_id = {x["event_id"]: x for x in bio_source}
    old_expansion_by_joint: dict[str, set[str]] = defaultdict(set)
    old_atom_by_joint: dict[str, set[str]] = defaultdict(set)
    for event in bio_events:
        old = old_event_by_id[event["event_id"]]
        card = old_dictionary[old["master_card_id"]]
        old_expansion_by_joint[event["joint_tuple_id"]].add(card["sentence_expansion_de"])
        old_atom_by_joint[event["joint_tuple_id"]].add(old["atomic_gloss_de"])
    if any(len(values) != 1 for values in old_expansion_by_joint.values()):
        raise ValueError("old Bio expansion not invariant")

    event_owner = {}
    owner_role = {}
    for unit in read(UNITS):
        owner_role[unit["owner_id"]] = unit["station_role"]
        for event_id in unit["event_ids"].split("|"):
            if event_id in event_owner:
                raise ValueError(f"duplicate owner for {event_id}")
            event_owner[event_id] = unit["owner_id"]

    expansions = {}
    changed_cards = []
    for event in bio_events:
        joint = event["joint_tuple_id"]
        value = event["atomic_value_de"]
        old_value = next(iter(old_atom_by_joint[joint]))
        if value in REPAIRED_EXPANSIONS:
            expansions[joint] = REPAIRED_EXPANSIONS[value]
        else:
            expansions[joint] = next(iter(old_expansion_by_joint[joint]))
        if old_value != value and joint not in {x["joint_tuple_id"] for x in changed_cards}:
            changed_cards.append(
                {
                    "joint_tuple_id": joint,
                    "surfaces": "|".join(sorted({x["surface"] for x in bio_events if x["joint_tuple_id"] == joint})),
                    "old_atomic_value_de": old_value,
                    "new_atomic_value_de": value,
                    "new_sentence_expansion_de": expansions[joint],
                    "event_count": str(sum(x["joint_tuple_id"] == joint for x in bio_events)),
                }
            )

    interlinear = []
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in bio_events:
        out = dict(event)
        out["owner_id"] = event_owner[event["event_id"]]
        out["station_role"] = owner_role[out["owner_id"]]
        out["atomic_sentence_expansion_de"] = expansions[event["joint_tuple_id"]]
        interlinear.append(out)
        by_statement[event["statement_id"]].append(out)

    statements = []
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for statement_id, rows in by_statement.items():
        segments = []
        current_owner = None
        current_parts = []
        owner_sequence = []
        for row in rows:
            if row["owner_id"] != current_owner:
                if current_parts:
                    segments.append((current_owner, current_parts))
                current_owner = row["owner_id"]
                owner_sequence.append(current_owner)
                current_parts = []
            current_parts.append(row["atomic_sentence_expansion_de"])
        if current_parts:
            segments.append((current_owner, current_parts))
        translation_parts = [f'Bei {owner_role[owner]}: {sentence_join(parts)}' for owner, parts in segments]
        statement = {
            "statement_id": statement_id,
            "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"],
            "event_ids": "|".join(x["event_id"] for x in rows),
            "surface_sequence": " ".join(x["surface"] for x in rows),
            "atomic_sequence": " → ".join(x["atomic_value_de"] for x in rows),
            "owner_sequence": "|".join(owner_sequence),
            "owner_segment_count": str(len(segments)),
            "fluent_station_translation_de": " Neuer lokaler Posten: ".join(translation_parts),
            "global_flow_claim": "NONE",
        }
        statements.append(statement)
        by_record[rows[0]["record_unit_id"]].append(statement)

    record_rows = []
    markdown = ["# Sechs reparierte Biological-Records", "", "Jede Aussage beginnt am lokalen Bildbesitzer. Ein Besitzerwechsel eröffnet einen neuen lokalen Posten; daraus wird kein globaler Wasserlauf konstruiert.", ""]
    for record in ["B1", "B2", "B3", "B4", "B5", "B6"]:
        rows = by_record[record]
        record_rows.append(
            {
                "record_unit_id": record,
                "page": rows[0]["page"],
                "statement_count": str(len(rows)),
                "event_count": str(sum(len(x["event_ids"].split("|")) for x in rows)),
                "owner_ids": "|".join(dict.fromkeys(owner for x in rows for owner in x["owner_sequence"].split("|"))),
                "record_reading_de": " ".join(x["fluent_station_translation_de"] for x in rows),
                "global_flow_claim": "NONE",
            }
        )
        markdown.extend([f"## {record} / {rows[0]['page']}", ""])
        for row in rows:
            markdown.extend([f"- **{row['statement_id']}** — {row['fluent_station_translation_de']}", ""])

    write("THREE_HUNDRED_THIRTY_SECOND_18_CHANGED_BIO_CARDS.tsv", changed_cards)
    write("THREE_HUNDRED_THIRTY_SECOND_281_REPAIRED_BIO_EVENTS.tsv", interlinear)
    write("THREE_HUNDRED_THIRTY_SECOND_97_REPAIRED_BIO_STATEMENTS.tsv", statements)
    write("THREE_HUNDRED_THIRTY_SECOND_SIX_REPAIRED_RECORDS.tsv", record_rows)
    (HERE / "THREE_HUNDRED_THIRTY_SECOND_COMPLETE_BIO_EDITION.md").write_text("\n".join(markdown), encoding="utf-8")
    names = [
        "THREE_HUNDRED_THIRTY_SECOND_18_CHANGED_BIO_CARDS.tsv",
        "THREE_HUNDRED_THIRTY_SECOND_281_REPAIRED_BIO_EVENTS.tsv",
        "THREE_HUNDRED_THIRTY_SECOND_97_REPAIRED_BIO_STATEMENTS.tsv",
        "THREE_HUNDRED_THIRTY_SECOND_SIX_REPAIRED_RECORDS.tsv",
        "THREE_HUNDRED_THIRTY_SECOND_COMPLETE_BIO_EDITION.md",
    ]
    summary = {
        "status": "PASS",
        "changed_card_types": len(changed_cards),
        "changed_events": sum(int(x["event_count"]) for x in changed_cards),
        "bio_events": len(interlinear),
        "bio_statements": len(statements),
        "bio_records": len(record_rows),
        "owner_resets_inside_statements": sum(int(x["owner_segment_count"]) - 1 for x in statements),
        "global_flow_claims": 0,
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_THIRTY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
