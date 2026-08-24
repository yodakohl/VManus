#!/usr/bin/env python3
"""Extract the exact-card lexicon shared by Herbal and Biological records."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_bio_station_sequences_three_hundred_eighteenth/THREE_HUNDRED_EIGHTEENTH_118_STATION_WORK_UNITS.tsv"

HANDOFFS = [
    ("H1", "B1-S002-M03", "Wurzelauszug zum gemeinsamen Becken"),
    ("H2", "B1-S002-M04", "Folgeansatz zur Maßkontrolle"),
    ("H3", "B2-S012-M02", "Klarauszug zur Klarlaufbehandlung"),
    ("H4", "B4-S008", "gekühlte Sollportion zur längeren Zielbehandlung"),
    ("H5", "B4-S003-M02", "Folgeposten zur wiederholten Anwendung"),
]

ATOMIC = {
    "2f1c5e56e8f0ff459065": "Sollmaß",
    "dcda95c81a5460feb191": "Fortsetzung",
    "b921a237be883a820352": "Diesposten",
    "6f7ff8287eddf4da9fdb": "Umsetzen",
    "dd0ecaf5e27d81befffc": "Stelle",
    "276a7c2d74d1143446f4": "Einsetzen",
    "b5fcea1eaed06b2f2291": "Sollstellung",
    "7a4bb8136330ee4e6e56": "Ansatz",
    "e0b630cb1b5df5e7105b": "Bereit",
    "308e8ea2d5d190c498e8": "Zieleinsatz",
    "4d4559019a961b834aa1": "Gleichvorrat",
    "b5df9126607030b95175": "Klarauszug",
    "80ebbbbf238eee9f0aef": "Zerkleinern",
    "1b1ffdd869fb1429ad03": "Fortschluss",
    "2c1a5fd92b9e3c762242": "Langwärme",
    "faf321940aed922846a9": "Folgeposten",
    "dec401773c1f0347793d": "Fortsetzungsansatz",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = read(LEDGER)
    herbal: dict[str, list[dict[str, str]]] = defaultdict(list)
    bio: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_event = {}
    for row in rows:
        by_record[row["record_unit_id"]].append(row)
        by_event[row["event_id"]] = row
        target = herbal if row["record_unit_id"].startswith("H") else bio
        target[row["joint_tuple_id"]].append(row)

    shared = sorted(set(herbal) & set(bio), key=lambda key: (-(len(herbal[key]) + len(bio[key])), key))
    lexicon = []
    audit = []
    for number, key in enumerate(shared, 1):
        both = herbal[key] + bio[key]
        glosses = {x["concrete_word_reading_de"] for x in both}
        if len(glosses) != 1:
            raise ValueError(f"non-invariant gloss for {key}: {glosses}")
        lexicon.append(
            {
                "handoff_word_id": f"HW{number:02d}",
                "joint_tuple_id": key,
                "source_reading_de": next(iter(glosses)),
                "handoff_atomic_value_de": ATOMIC[key],
                "surface_forms": "|".join(sorted({x["surface_display"] for x in both})),
                "herbal_events": str(len(herbal[key])),
                "bio_events": str(len(bio[key])),
                "total_events": str(len(both)),
                "herbal_records": "|".join(sorted({x["record_unit_id"] for x in herbal[key]})),
                "bio_records": "|".join(sorted({x["record_unit_id"] for x in bio[key]})),
                "portable_rule": "SAME_CARD_SAME_SHORT_MEANING_ACROSS_HERBAL_AND_BIO",
            }
        )
        for event in both:
            audit.append(
                {
                    "handoff_word_id": f"HW{number:02d}",
                    "event_id": event["event_id"],
                    "section": "HERBAL" if event["record_unit_id"].startswith("H") else "BIO",
                    "record_unit_id": event["record_unit_id"],
                    "page": event["page"],
                    "statement_id": event["statement_id"],
                    "surface": event["surface_display"],
                    "source_reading_de": event["concrete_word_reading_de"],
                    "handoff_atomic_value_de": ATOMIC[key],
                }
            )

    units = {x["station_work_unit_id"]: x for x in read(UNITS)}
    anchors = []
    for herbal_record, bio_unit, reading in HANDOFFS:
        hrows = by_record[herbal_record]
        brows = [by_event[e] for e in units[bio_unit]["event_ids"].split("|")]
        common = sorted(set(x["joint_tuple_id"] for x in hrows) & set(x["joint_tuple_id"] for x in brows))
        for key in common:
            hs = [x for x in hrows if x["joint_tuple_id"] == key]
            bs = [x for x in brows if x["joint_tuple_id"] == key]
            lex = next(x for x in lexicon if x["joint_tuple_id"] == key)
            anchors.append(
                {
                    "herbal_record": herbal_record,
                    "bio_unit": bio_unit,
                    "handoff_reading": reading,
                    "handoff_word_id": lex["handoff_word_id"],
                    "joint_tuple_id": key,
                    "handoff_atomic_value_de": lex["handoff_atomic_value_de"],
                    "herbal_surfaces": "|".join(x["surface_display"] for x in hs),
                    "bio_surfaces": "|".join(x["surface_display"] for x in bs),
                    "exact_identity_bridge": "YES",
                }
            )

    write("THREE_HUNDRED_TWENTIETH_17_SHARED_HANDOFF_WORDS.tsv", lexicon)
    write("THREE_HUNDRED_TWENTIETH_136_SHARED_WORD_EVENTS.tsv", audit)
    write("THREE_HUNDRED_TWENTIETH_FIVE_HANDOFF_ANCHORS.tsv", anchors)

    names = [
        "THREE_HUNDRED_TWENTIETH_17_SHARED_HANDOFF_WORDS.tsv",
        "THREE_HUNDRED_TWENTIETH_136_SHARED_WORD_EVENTS.tsv",
        "THREE_HUNDRED_TWENTIETH_FIVE_HANDOFF_ANCHORS.tsv",
    ]
    summary = {
        "status": "PASS",
        "shared_card_types": len(lexicon),
        "shared_card_events": len(audit),
        "herbal_shared_events": sum(int(x["herbal_events"]) for x in lexicon),
        "bio_shared_events": sum(int(x["bio_events"]) for x in lexicon),
        "selected_handoff_exact_anchors": len(anchors),
        "selected_handoffs": len(HANDOFFS),
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_TWENTIETH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
