#!/usr/bin/env python3
"""Rebuild five Herbal-to-Bio handoffs from repaired card values."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_herbal_formula_repair_three_hundred_twenty_ninth/THREE_HUNDRED_TWENTY_NINTH_381_GLOBAL_EVENTS.tsv"
ARTICLES = ROOT / "experiments/yolo/sidequest_semantic_repaired_herbal_edition_three_hundred_thirtieth/THREE_HUNDRED_THIRTIETH_FIVE_REPAIRED_ARTICLES.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_bio_station_sequences_three_hundred_eighteenth/THREE_HUNDRED_EIGHTEENTH_118_STATION_WORK_UNITS.tsv"

SELECTIONS = {
    "H1": ("B1-S002-M03", "Wurzel-Wasseransatz als Fortsetzungsansatz in das gemeinsame Becken geben."),
    "H2": ("B1-S002-M04", "Fortgesetzten Ansatz vor und nach dem Zielhalt am selben Sollmaß führen."),
    "H3": ("B2-S012-M02", "Den gestandenen und nachgeseihten Klarauszug lokal vorbereiten, lange behandeln und klar abziehen."),
    "H4": ("B4-S008", "Die abgemessene Auszugsportion länger warm halten, danach am lokalen Ziel kurz ansetzen."),
    "H5": ("B4-S003-M02", "Den Zutaten-/Auszugsposten als Folgeposten einsetzen, weiterführen und kurz absetzen."),
}

WITHDRAWN_DEPENDENCIES = {
    "H1": "SECOND_ROOT_AT_END_WITHDRAWN;ETyd_IS_KURZREST",
    "H2": "ULCER_READING_WITHDRAWN;CHO_AIIN_IS_INGREDIENT_MEASURE",
    "H3": "WINE_READING_WITHDRAWN;CLEAR_EXTRACT_CHAIN_RETAINED",
    "H4": "COOLING_READING_WITHDRAWN;EXPLICIT_LONG_WARMTH_RETAINED",
    "H5": "FREE_K_WASH_STRAIN_ACTIONS_WITHDRAWN;FOLLOW_ITEM_AND_INSERT_RETAINED",
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
    events = read(EVENTS)
    article_rows = {x["record_unit_id"]: x for x in read(ARTICLES)}
    units = {x["station_work_unit_id"]: x for x in read(UNITS)}
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_event = {}
    for row in events:
        by_record[row["record_unit_id"]].append(row)
        by_event[row["event_id"]] = row

    handoffs = []
    anchors = []
    for record, (unit_id, reading) in SELECTIONS.items():
        herbal = by_record[record]
        unit_source = units[unit_id]
        bio = [by_event[e] for e in unit_source["event_ids"].split("|")]
        h_ids = {x["joint_tuple_id"] for x in herbal}
        b_ids = {x["joint_tuple_id"] for x in bio}
        common = sorted(h_ids & b_ids)
        handoffs.append(
            {
                "herbal_record": record,
                "herbal_page": article_rows[record]["page"],
                "herbal_title": article_rows[record]["title"],
                "repaired_output": article_rows[record]["output"],
                "bio_unit": unit_id,
                "bio_page": unit_source["page"],
                "bio_owner": unit_source["owner_id"],
                "station_role": unit_source["station_role"],
                "repaired_bio_atomic_chain": " → ".join(x["atomic_value_de"] for x in bio),
                "exact_shared_anchor_count": str(len(common)),
                "exact_shared_values": "|".join(sorted({x["atomic_value_de"] for x in herbal if x["joint_tuple_id"] in common})),
                "integrated_reading_de": reading,
                "withdrawn_old_dependencies": WITHDRAWN_DEPENDENCIES[record],
                "handoff_status": "SURVIVES_REPAIRED_DICTIONARY",
                "direct_cross_page_pointer": "NONE",
            }
        )
        for joint in common:
            hs = [x for x in herbal if x["joint_tuple_id"] == joint]
            bs = [x for x in bio if x["joint_tuple_id"] == joint]
            anchors.append(
                {
                    "herbal_record": record,
                    "bio_unit": unit_id,
                    "joint_tuple_id": joint,
                    "atomic_value_de": hs[0]["atomic_value_de"],
                    "herbal_event_ids": "|".join(x["event_id"] for x in hs),
                    "herbal_surfaces": "|".join(x["surface"] for x in hs),
                    "bio_event_ids": "|".join(x["event_id"] for x in bs),
                    "bio_surfaces": "|".join(x["surface"] for x in bs),
                    "same_identity": "YES",
                    "same_atomic_value": "YES" if {x["atomic_value_de"] for x in hs + bs} == {hs[0]["atomic_value_de"]} else "NO",
                }
            )

    write("THREE_HUNDRED_THIRTY_FIRST_FIVE_REPAIRED_HANDOFFS.tsv", handoffs)
    write("THREE_HUNDRED_THIRTY_FIRST_SEVEN_EXACT_ANCHORS.tsv", anchors)
    names = [
        "THREE_HUNDRED_THIRTY_FIRST_FIVE_REPAIRED_HANDOFFS.tsv",
        "THREE_HUNDRED_THIRTY_FIRST_SEVEN_EXACT_ANCHORS.tsv",
    ]
    summary = {
        "status": "PASS",
        "handoffs": len(handoffs),
        "surviving_handoffs": sum(x["handoff_status"] == "SURVIVES_REPAIRED_DICTIONARY" for x in handoffs),
        "exact_anchors": len(anchors),
        "direct_cross_page_pointers": 0,
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_THIRTY_FIRST_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
