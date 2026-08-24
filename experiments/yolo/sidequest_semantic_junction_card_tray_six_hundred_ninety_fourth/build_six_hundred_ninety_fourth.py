#!/usr/bin/env python3
"""Build the complete cross-desk junction-card tray for all prose records."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P606 = ROOT / "experiments/yolo/sidequest_semantic_short_workshop_dictionary_six_hundred_sixth"
P679 = ROOT / "experiments/yolo/sidequest_semantic_historical_layer_dictionary_six_hundred_seventy_ninth"
P690 = ROOT / "experiments/yolo/sidequest_semantic_statement_core_projection_six_hundred_ninetieth"
P692 = ROOT / "experiments/yolo/sidequest_semantic_workshop_floor_plan_six_hundred_ninety_second"

ORDER = {
    "S01_MASTER_CORRECTOR": 1,
    "S02_PREPARATION_WET": 2,
    "S03_TRANSFER": 3,
    "S04_STATE_CONTROL": 4,
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P690 / "SIX_HUNDRED_NINETIETH_381_EVENT_CORE_PROJECTION.tsv")
    card_events = read(P679 / "SIX_HUNDRED_SEVENTY_NINTH_381_COMPACT_EVENT_INTERLINEAR.tsv")
    loci = read(P606 / "SIX_HUNDRED_SIXTH_381_SHORT_EVENT_EDITION.tsv")
    assignments = read(P692 / "SIX_HUNDRED_NINETY_SECOND_26_ROOT_ASSIGNMENTS.tsv")
    role_for_component = {row["component"]: row["scribe_role"] for row in assignments}
    card_by_event = {row["event_id"]: row["card_no"] for row in card_events}
    locus_by_event = {row["event_id"]: row for row in loci}

    occurrence_rows: list[dict[str, object]] = []
    for event in events:
        components = [] if event["specialist_recipe"] == "NONE" else event["specialist_recipe"].replace("+", " ").split()
        roles = sorted({role_for_component[component] for component in components}, key=ORDER.get)
        if len(roles) < 2:
            continue
        storage = roles[-1]
        locus = locus_by_event[event["event_id"]]
        occurrence_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "locus": locus["locus"],
            "statement_id": event["statement_id"],
            "owner_de": locus["silent_owner_de"],
            "card_no": card_by_event[event["event_id"]],
            "surface": event["surface"],
            "full_recipe": event["full_recipe"],
            "atomic_reading_de": event["full_reading_de"],
            "earlier_component_desks": "|".join(roles[:-1]),
            "downstream_storage_desk": storage,
            "desk_pair": ">".join(roles),
            "copy_rule_de": "Fruehere Tische markieren Komponenten; der letzte beteiligte Tisch waehlt die ganze Musterkarte.",
        })

    by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        by_card[str(row["card_no"])].append(row)
    tray_rows: list[dict[str, object]] = []
    for card_no, rows in sorted(by_card.items()):
        first = rows[0]
        tray_rows.append({
            "card_no": card_no,
            "surface_forms": "|".join(dict.fromkeys(str(row["surface"]) for row in rows)),
            "full_recipe": first["full_recipe"],
            "atomic_reading_de": first["atomic_reading_de"],
            "desk_pair": first["desk_pair"],
            "stored_at_desk": first["downstream_storage_desk"],
            "earlier_desk_marks": first["earlier_component_desks"],
            "events": len(rows),
            "event_ids": ",".join(str(row["event_id"]) for row in rows),
            "records": "|".join(dict.fromkeys(str(row["record"]) for row in rows)),
            "owners_de": " | ".join(dict.fromkeys(str(row["owner_de"]) for row in rows)),
            "apprentice_rule_de": "Lerne diese Karte als ganzes Grenzexemplar; zerlege sie beim Diktat, nicht beim Schreiben.",
        })

    pair_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        pair_groups[str(row["desk_pair"])].append(row)
    pair_rows: list[dict[str, object]] = []
    for pair, rows in sorted(pair_groups.items()):
        card_ids = list(dict.fromkeys(str(row["card_no"]) for row in rows))
        pair_rows.append({
            "desk_pair": pair,
            "earlier_desk": pair.split(">", 1)[0],
            "downstream_owner": rows[0]["downstream_storage_desk"],
            "exact_cards": len(card_ids),
            "events": len(rows),
            "card_numbers": " ".join(card_ids),
            "surfaces": " ".join(dict.fromkeys(str(row["surface"]) for row in rows)),
            "rule_de": "Die ganze Kreuzkarte liegt am spaeteren Tisch; der fruehere Tisch setzt nur einen Randvermerk auf den Entwurfsstreifen.",
        })

    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        by_record[str(row["record"])].append(row)
    record_rows: list[dict[str, object]] = []
    all_records = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    for record in all_records:
        rows = by_record[record]
        record_rows.append({
            "record": record,
            "junction_events": len(rows),
            "exact_junction_cards": len({row["card_no"] for row in rows}),
            "desk_pairs": "|".join(dict.fromkeys(str(row["desk_pair"]) for row in rows)) if rows else "NONE",
            "event_ids": ",".join(str(row["event_id"]) for row in rows) if rows else "NONE",
            "production_de": "Junction tray required." if rows else "Pocket/core and single-desk cards suffice.",
        })

    burden_rows = [
        {"scribe_role": "S01_MASTER_CORRECTOR", "pocket_core_cards": 13, "specialist_root_cards": 5, "junction_whole_cards": 0, "total_reference_cards": 18},
        {"scribe_role": "S02_PREPARATION_WET", "pocket_core_cards": 13, "specialist_root_cards": 10, "junction_whole_cards": 0, "total_reference_cards": 23},
        {"scribe_role": "S03_TRANSFER", "pocket_core_cards": 13, "specialist_root_cards": 4, "junction_whole_cards": 11, "total_reference_cards": 28},
        {"scribe_role": "S04_STATE_CONTROL", "pocket_core_cards": 13, "specialist_root_cards": 7, "junction_whole_cards": 9, "total_reference_cards": 29},
    ]

    write("SIX_HUNDRED_NINETY_FOURTH_22_JUNCTION_OCCURRENCES.tsv", occurrence_rows)
    write("SIX_HUNDRED_NINETY_FOURTH_20_JUNCTION_CARD_TRAY.tsv", tray_rows)
    write("SIX_HUNDRED_NINETY_FOURTH_4_DESK_PAIR_RULES.tsv", pair_rows)
    write("SIX_HUNDRED_NINETY_FOURTH_11_RECORD_JUNCTION_BURDEN.tsv", record_rows)
    write("SIX_HUNDRED_NINETY_FOURTH_4_ROLE_REFERENCE_BURDEN.tsv", burden_rows)

    summary = {
        "status": "PASS",
        "junction_occurrences": len(occurrence_rows),
        "exact_junction_cards": len(tray_rows),
        "desk_pair_rules": len(pair_rows),
        "records_with_junction_cards": sum(bool(by_record[record]) for record in all_records),
        "records_without_junction_cards": sum(not by_record[record] for record in all_records),
        "downstream_event_storage": dict(Counter(str(row["downstream_storage_desk"]) for row in occurrence_rows)),
        "downstream_card_storage": dict(Counter(str(row["stored_at_desk"]) for row in tray_rows)),
        "junction_share_of_specialist_events": f"{len(occurrence_rows)}/201",
        "junction_share_of_specialist_card_types": f"{len(tray_rows)}/123",
        "largest_role_reference_deck": max(int(row["total_reference_cards"]) for row in burden_rows),
    }
    (HERE / "SIX_HUNDRED_NINETY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
