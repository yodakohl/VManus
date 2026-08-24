#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

EVENT_SOURCES = (
    ("B1", ROOT / "experiments/yolo/sidequest_semantic_b1_apprentice_dictionary_four_hundred_thirty_fourth/FOUR_HUNDRED_THIRTY_FOURTH_B1_66_EVENT_APPRENTICE_TRACE.tsv"),
    ("B2", ROOT / "experiments/yolo/sidequest_semantic_b2_apprentice_dictionary_four_hundred_thirty_ninth/FOUR_HUNDRED_THIRTY_NINTH_FINAL_B2_62_EVENTS.tsv"),
    ("B3", ROOT / "experiments/yolo/sidequest_semantic_b3_local_tournament_four_hundred_forty_second/FOUR_HUNDRED_FORTY_SECOND_REVISED_B3_86_EVENTS.tsv"),
    ("B4", ROOT / "experiments/yolo/sidequest_semantic_b4_productive_completion_four_hundred_forty_fourth/FOUR_HUNDRED_FORTY_FOURTH_FINAL_B4_47_EVENTS.tsv"),
    ("B56", ROOT / "experiments/yolo/sidequest_semantic_b5_b6_dictionary_four_hundred_forty_sixth/FOUR_HUNDRED_FORTY_SIXTH_FINAL_20_EVENTS.tsv"),
)

DICTIONARY_SOURCES = (
    ("B1", ROOT / "experiments/yolo/sidequest_semantic_b1_apprentice_dictionary_four_hundred_thirty_fourth/FOUR_HUNDRED_THIRTY_FOURTH_B1_43_CARD_DICTIONARY.tsv", "small_value_de"),
    ("B2", ROOT / "experiments/yolo/sidequest_semantic_b2_apprentice_dictionary_four_hundred_thirty_ninth/FOUR_HUNDRED_THIRTY_NINTH_FINAL_B2_46_CARD_DICTIONARY.tsv", "small_values_de"),
    ("B3", ROOT / "experiments/yolo/sidequest_semantic_b3_local_tournament_four_hundred_forty_second/FOUR_HUNDRED_FORTY_SECOND_FINAL_B3_52_CARD_DICTIONARY.tsv", "small_values_de"),
    ("B4", ROOT / "experiments/yolo/sidequest_semantic_b4_productive_completion_four_hundred_forty_fourth/FOUR_HUNDRED_FORTY_FOURTH_FINAL_B4_34_CARD_DICTIONARY.tsv", "small_values_de"),
    ("B56", ROOT / "experiments/yolo/sidequest_semantic_b5_b6_dictionary_four_hundred_forty_sixth/FOUR_HUNDRED_FORTY_SIXTH_FINAL_16_CARD_DICTIONARY.tsv", "small_values_de"),
)

STATEMENT_SOURCES = (
    ROOT / "experiments/yolo/sidequest_semantic_b1_apprentice_dictionary_four_hundred_thirty_fourth/FOUR_HUNDRED_THIRTY_FOURTH_B1_21_CELL_EDITION.tsv",
    ROOT / "experiments/yolo/sidequest_semantic_b2_apprentice_dictionary_four_hundred_thirty_ninth/FOUR_HUNDRED_THIRTY_NINTH_FINAL_B2_22_STATEMENTS.tsv",
    ROOT / "experiments/yolo/sidequest_semantic_b3_local_tournament_four_hundred_forty_second/FOUR_HUNDRED_FORTY_SECOND_REVISED_B3_34_STATEMENTS.tsv",
    ROOT / "experiments/yolo/sidequest_semantic_b4_productive_completion_four_hundred_forty_fourth/FOUR_HUNDRED_FORTY_FOURTH_FINAL_B4_16_STATEMENTS.tsv",
    ROOT / "experiments/yolo/sidequest_semantic_b5_b6_dictionary_four_hundred_forty_sixth/FOUR_HUNDRED_FORTY_SIXTH_FINAL_FOUR_STATEMENTS.tsv",
)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base_by_event = {row["event_id"]: row for row in read(BASE)}
    event_versions: dict[str, list[tuple[str, str]]] = defaultdict(list)
    event_source_rows: dict[str, tuple[str, dict[str, str]]] = {}
    for deck, path in EVENT_SOURCES:
        for row in read(path):
            event_versions[row["event_id"]].append((deck, row["small_value_de"]))
            event_source_rows[row["event_id"]] = (deck, row)

    expected_ids = [f"E{number}" for number in range(101, 382)]
    if sorted(event_source_rows, key=lambda event_id: int(event_id[1:])) != expected_ids:
        raise ValueError("Biological event coverage is not E101-E381")
    value_collisions = {event_id: versions for event_id, versions in event_versions.items() if len({value for _, value in versions}) > 1}
    if value_collisions:
        raise ValueError(f"event value collisions: {value_collisions}")

    events: list[dict[str, object]] = []
    for order, event_id in enumerate(expected_ids, 1):
        base = base_by_event[event_id]
        deck, source = event_source_rows[event_id]
        if deck == "B1":
            owner_zone = "B1_SHARED_POOL_WORKSTATION"
        elif deck == "B56":
            owner_zone = f"{base['record_unit_id']}_LOCAL_RECORD_OWNER"
        else:
            owner_zone = source["owner_zone"]
        events.append({
            "order": order,
            "event_id": event_id,
            "record_unit_id": base["record_unit_id"],
            "page": base["page"],
            "locus": base["locus"],
            "field_id": base["field_id"],
            "statement_id": base["statement_id"],
            "surface": source["surface"],
            "joint_tuple_id": base["joint_tuple_id"],
            "small_value_de": source["small_value_de"],
            "owner_zone": owner_zone,
            "selected_record_deck": deck,
        })

    values_by_joint: dict[str, set[str]] = defaultdict(set)
    records_by_joint: dict[str, set[str]] = defaultdict(set)
    surfaces_by_joint: dict[str, set[str]] = defaultdict(set)
    events_by_joint: dict[str, list[str]] = defaultdict(list)
    for row in events:
        joint_id = str(row["joint_tuple_id"])
        values_by_joint[joint_id].add(str(row["small_value_de"]))
        records_by_joint[joint_id].add(str(row["record_unit_id"]))
        surfaces_by_joint[joint_id].add(str(row["surface"]))
        events_by_joint[joint_id].append(str(row["event_id"]))
    joint_collisions = {joint_id: values for joint_id, values in values_by_joint.items() if len(values) > 1}
    if joint_collisions:
        raise ValueError(f"joint tuple value collisions: {joint_collisions}")

    origin: dict[str, tuple[str, str]] = {}
    for deck, path, _ in DICTIONARY_SOURCES:
        for row in read(path):
            origin.setdefault(row["joint_tuple_id"], (deck, row["drawer"]))

    first_order = {joint_id: min(int(row["order"]) for row in events if row["joint_tuple_id"] == joint_id) for joint_id in values_by_joint}
    dictionary = []
    for joint_id in sorted(values_by_joint, key=first_order.get):
        origin_deck, origin_drawer = origin[joint_id]
        if "PRODUCTIVE" in origin_drawer:
            union_drawer = "PRODUCTIVE_COMPOSITION"
        elif len(records_by_joint[joint_id]) > 1 or "PORTABLE" in origin_drawer:
            union_drawer = "PORTABLE_LEARNED_WHOLE_CARD"
        else:
            union_drawer = "RECORD_LOCAL_LEARNED_WHOLE_CARD"
        dictionary.append({
            "card_no": f"BIOC{len(dictionary) + 1:03d}",
            "joint_tuple_id": joint_id,
            "surfaces": "|".join(sorted(surfaces_by_joint[joint_id])),
            "events": len(events_by_joint[joint_id]),
            "event_ids": "|".join(events_by_joint[joint_id]),
            "records": "|".join(sorted(records_by_joint[joint_id])),
            "origin_deck": origin_deck,
            "origin_drawer": origin_drawer,
            "union_drawer": union_drawer,
            "small_value_de": next(iter(values_by_joint[joint_id])),
        })
    write("FOUR_HUNDRED_FORTY_SEVENTH_124_CARD_DICTIONARY.tsv", dictionary)
    category_by_joint = {row["joint_tuple_id"]: row["union_drawer"] for row in dictionary}
    for row in events:
        row["union_drawer"] = category_by_joint[str(row["joint_tuple_id"])]
    write("FOUR_HUNDRED_FORTY_SEVENTH_281_EVENT_EDITION.tsv", events)

    fluent: dict[str, str] = {}
    for path in STATEMENT_SOURCES:
        for row in read(path):
            fluent[row["statement_id"]] = row["continuous_reading_de"]
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        by_statement[str(row["statement_id"])].append(row)
    statements = []
    for statement_id, rows in by_statement.items():
        zones = list(dict.fromkeys(str(row["owner_zone"]) for row in rows))
        statements.append({
            "statement_id": statement_id,
            "record_unit_id": rows[0]["record_unit_id"],
            "events": len(rows),
            "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "fields": "|".join(dict.fromkeys(str(row["field_id"]) for row in rows)),
            "owner_zones": "|".join(zones),
            "owner_break_inside_statement": "YES" if len(zones) > 1 else "NO",
            "card_sequence_de": " > ".join(str(row["small_value_de"]) for row in rows),
            "continuous_reading_de": fluent[statement_id],
        })
    write("FOUR_HUNDRED_FORTY_SEVENTH_97_STATEMENT_EDITION.tsv", statements)

    by_field: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        by_field[str(row["field_id"])].append(row)
    fields = []
    for field_id, rows in by_field.items():
        fields.append({
            "field_id": field_id,
            "record_unit_id": rows[0]["record_unit_id"],
            "loci": "|".join(dict.fromkeys(str(row["locus"]) for row in rows)),
            "statement_ids": "|".join(dict.fromkeys(str(row["statement_id"]) for row in rows)),
            "events": len(rows),
            "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "owner_zones": "|".join(dict.fromkeys(str(row["owner_zone"]) for row in rows)),
            "card_sequence_de": " > ".join(str(row["small_value_de"]) for row in rows),
        })
    write("FOUR_HUNDRED_FORTY_SEVENTH_115_FIELD_EDITION.tsv", fields)

    resets = []
    previous = None
    for row in events:
        if previous is None or row["record_unit_id"] != previous["record_unit_id"]:
            resets.append({
                "event_id": row["event_id"], "record_unit_id": row["record_unit_id"], "reset_kind": "RECORD_START",
                "from_owner": "NONE" if previous is None else previous["owner_zone"], "to_owner": row["owner_zone"],
                "inherit_previous_state": "NO",
            })
        elif row["owner_zone"] != previous["owner_zone"]:
            resets.append({
                "event_id": row["event_id"], "record_unit_id": row["record_unit_id"], "reset_kind": "VISIBLE_OWNER_CHANGE",
                "from_owner": previous["owner_zone"], "to_owner": row["owner_zone"], "inherit_previous_state": "NO",
            })
        previous = row
    write("FOUR_HUNDRED_FORTY_SEVENTH_OWNER_RESETS.tsv", resets)

    local = [row for row in dictionary if row["union_drawer"] == "RECORD_LOCAL_LEARNED_WHOLE_CARD"]
    write("FOUR_HUNDRED_FORTY_SEVENTH_31_LOCAL_WHOLE_CARDS.tsv", local)

    reconciliation = []
    for joint_id in sorted(values_by_joint, key=first_order.get):
        reconciliation.append({
            "joint_tuple_id": joint_id,
            "surfaces": "|".join(sorted(surfaces_by_joint[joint_id])),
            "records": "|".join(sorted(records_by_joint[joint_id])),
            "distinct_selected_values": len(values_by_joint[joint_id]),
            "selected_value_de": next(iter(values_by_joint[joint_id])),
            "collision": "NO",
        })
    write("FOUR_HUNDRED_FORTY_SEVENTH_VALUE_RECONCILIATION.tsv", reconciliation)

    lines = ["# Six Biological workshop records", ""]
    for record in ("B1", "B2", "B3", "B4", "B5", "B6"):
        lines.extend([f"## {record}", ""])
        for row in statements:
            if row["record_unit_id"] == record:
                marker = " [BILDWECHSEL IM SATZ]" if row["owner_break_inside_statement"] == "YES" else ""
                lines.append(f"- **{row['statement_id']}**{marker}: {row['continuous_reading_de']}")
        lines.append("")
    (HERE / "FOUR_HUNDRED_FORTY_SEVENTH_COMPLETE_BIOLOGICAL_EDITION.md").write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "status": "PASS", "records": 6, "events": len(events), "fields": len(fields), "statements": len(statements),
        "cards": len(dictionary), "value_collisions": len(joint_collisions),
        "productive_cards": sum(row["union_drawer"] == "PRODUCTIVE_COMPOSITION" for row in dictionary),
        "portable_whole_cards": sum(row["union_drawer"] == "PORTABLE_LEARNED_WHOLE_CARD" for row in dictionary),
        "local_whole_cards": len(local),
        "productive_events": sum(row["union_drawer"] == "PRODUCTIVE_COMPOSITION" for row in events),
        "portable_whole_events": sum(row["union_drawer"] == "PORTABLE_LEARNED_WHOLE_CARD" for row in events),
        "local_whole_events": sum(row["union_drawer"] == "RECORD_LOCAL_LEARNED_WHOLE_CARD" for row in events),
        "reset_rows": len(resets), "visible_owner_changes": sum(row["reset_kind"] == "VISIBLE_OWNER_CHANGE" for row in resets),
    }
    (HERE / "FOUR_HUNDRED_FORTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
