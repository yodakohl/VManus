#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
SENTENCES = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_116_THERMAL_TEMPORAL_SENTENCES.tsv"
BIO = ROOT / "experiments/yolo/sidequest_semantic_biological_reverse_compiler_four_hundred_fifty_first/FOUR_HUNDRED_FIFTY_FIRST_124_CARD_DICTIONARY.tsv"

OWNERS = {
    "H1": "F10R_PICTURED_PLANT", "H2": "F10R_PICTURED_PLANT",
    "H3": "F11R_PICTURED_PLANT", "H4": "F55V_PICTURED_PLANT", "H5": "F56R_PICTURED_PLANT",
}


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
    source = [row for row in read(BASE) if row["record_unit_id"] in OWNERS]
    bio = {row["joint_tuple_id"]: row for row in read(BIO)}
    events = []
    for order, row in enumerate(source, 1):
        joint_id = row["joint_tuple_id"]
        old_value = row["selected_thermal_previous_gloss_de"]
        if joint_id in bio:
            value = bio[joint_id]["small_value_de"]
            source_kind = "BIOLOGICAL_EXACT_CARD_TRANSFER"
        else:
            value = old_value
            source_kind = "HERBAL_LOCAL_CARD_PENDING_REANALYSIS"
        events.append({
            "order": order, "event_id": row["event_id"], "record_unit_id": row["record_unit_id"],
            "page": row["page"], "locus": row["locus"], "field_id": row["field_id"],
            "statement_id": row["statement_id"], "surface": row["surface_display"],
            "joint_tuple_id": joint_id, "picture_owner": OWNERS[row["record_unit_id"]],
            "previous_herbal_value_de": old_value, "small_value_de": value,
            "lexicon_source": source_kind, "value_changed": "YES" if value != old_value else "NO",
        })
    write("FOUR_HUNDRED_FIFTY_THIRD_100_EVENT_HERBAL_EDITION.tsv", events)

    values_by_joint: dict[str, set[str]] = defaultdict(set)
    rows_by_joint: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        values_by_joint[str(row["joint_tuple_id"])].add(str(row["small_value_de"]))
        rows_by_joint[str(row["joint_tuple_id"])].append(row)
    if any(len(values) != 1 for values in values_by_joint.values()):
        raise ValueError("Herbal card value collision")
    dictionary = []
    for joint_id in sorted(rows_by_joint, key=lambda item: min(int(row["order"]) for row in rows_by_joint[item])):
        rows = rows_by_joint[joint_id]
        dictionary.append({
            "card_no": f"HERC{len(dictionary) + 1:02d}", "joint_tuple_id": joint_id,
            "surfaces": "|".join(sorted({str(row["surface"]) for row in rows})),
            "events": len(rows), "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "records": "|".join(sorted({str(row["record_unit_id"]) for row in rows})),
            "drawer": "BIOLOGICAL_EXACT_CARD_TRANSFER" if joint_id in bio else "HERBAL_LOCAL_CARD_PENDING_REANALYSIS",
            "small_value_de": next(iter(values_by_joint[joint_id])),
        })
    write("FOUR_HUNDRED_FIFTY_THIRD_66_CARD_HERBAL_DICTIONARY.tsv", dictionary)

    old_statements = {row["statement_id"]: row for row in read(SENTENCES) if row["record_unit_id"] in OWNERS}
    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        by_statement[str(row["statement_id"])].append(row)
    statements = []
    for statement_id, rows in by_statement.items():
        old = old_statements[statement_id]
        statements.append({
            "statement_id": statement_id, "record_unit_id": rows[0]["record_unit_id"],
            "page": rows[0]["page"], "picture_owner": rows[0]["picture_owner"],
            "events": len(rows), "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "field_ids": "|".join(dict.fromkeys(str(row["field_id"]) for row in rows)),
            "card_sequence_de": " > ".join(str(row["small_value_de"]) for row in rows),
            "literal_workshop_reading_de": "; ".join(str(row["small_value_de"]) for row in rows) + ".",
            "previous_fluent_reading_de": old["workshop_sentence_de"],
            "transferred_events": sum(row["lexicon_source"] == "BIOLOGICAL_EXACT_CARD_TRANSFER" for row in rows),
        })
    write("FOUR_HUNDRED_FIFTY_THIRD_19_STATEMENT_HERBAL_EDITION.tsv", statements)

    by_field: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events:
        by_field[str(row["field_id"])].append(row)
    fields = []
    for field_id, rows in by_field.items():
        fields.append({
            "field_id": field_id, "record_unit_id": rows[0]["record_unit_id"], "loci": "|".join(dict.fromkeys(str(row["locus"]) for row in rows)),
            "events": len(rows), "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "statement_ids": "|".join(dict.fromkeys(str(row["statement_id"]) for row in rows)),
            "picture_owner": rows[0]["picture_owner"], "card_sequence_de": " > ".join(str(row["small_value_de"]) for row in rows),
        })
    write("FOUR_HUNDRED_FIFTY_THIRD_20_FIELD_HERBAL_EDITION.tsv", fields)

    transfers = [row for row in dictionary if row["drawer"] == "BIOLOGICAL_EXACT_CARD_TRANSFER"]
    write("FOUR_HUNDRED_FIFTY_THIRD_17_TRANSFERRED_CARDS.tsv", transfers)
    local = [row for row in dictionary if row["drawer"] == "HERBAL_LOCAL_CARD_PENDING_REANALYSIS"]
    write("FOUR_HUNDRED_FIFTY_THIRD_49_PENDING_HERBAL_CARDS.tsv", local)

    changed = []
    for row in events:
        if row["value_changed"] == "YES":
            changed.append({
                "event_id": row["event_id"], "record_unit_id": row["record_unit_id"], "surface": row["surface"],
                "joint_tuple_id": row["joint_tuple_id"], "old_herbal_value_de": row["previous_herbal_value_de"],
                "transferred_value_de": row["small_value_de"], "reason": "SAME_EXACT_CARD_MUST_KEEP_ONE_VALUE",
            })
    write("FOUR_HUNDRED_FIFTY_THIRD_35_TRANSFER_REVISIONS.tsv", changed)

    lines = ["# Five pictured-plant records after Biological card transfer", ""]
    for record in ("H1", "H2", "H3", "H4", "H5"):
        lines.extend([f"## {record} — {OWNERS[record]}", ""])
        for row in statements:
            if row["record_unit_id"] == record:
                lines.append(f"- **{row['statement_id']}**: {row['literal_workshop_reading_de']}")
        lines.append("")
    (HERE / "FOUR_HUNDRED_FIFTY_THIRD_COMPLETE_HERBAL_TRANSFER_EDITION.md").write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "status": "PASS", "records": 5, "events": len(events), "fields": len(fields), "statements": len(statements),
        "cards": len(dictionary), "transferred_cards": len(transfers), "transferred_events": sum(row["lexicon_source"] == "BIOLOGICAL_EXACT_CARD_TRANSFER" for row in events),
        "pending_cards": len(local), "pending_events": sum(row["lexicon_source"] == "HERBAL_LOCAL_CARD_PENDING_REANALYSIS" for row in events),
        "revised_transfer_events": len(changed),
    }
    (HERE / "FOUR_HUNDRED_FIFTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
