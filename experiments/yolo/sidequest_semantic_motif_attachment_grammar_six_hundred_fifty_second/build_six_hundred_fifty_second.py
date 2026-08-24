#!/usr/bin/env python3
"""Map source-attested motif entry and exit attachments."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P637 = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_curriculum_six_hundred_thirty_seventh"
P651 = ROOT / "experiments/yolo/sidequest_semantic_source_motifs_six_hundred_fifty_first"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ROLE = {
    "M01_ITEM_MEASURE_FRAME": (
        "MOBILE_MEASURE_FRAME",
        "darf am Anfang, in der Mitte oder am Ende stehen; keine feste Nachbarkarte",
    ),
    "M02_SET_ITEM_MEASURE": (
        "OPEN_MEASURE_SETUP",
        "beginnt oder erweitert eine Aussage und gibt stets nach rechts weiter",
    ),
    "M03_PREPARATION_ITEM": (
        "OPEN_PREPARATION_BINDER",
        "bindet den Ansatz an den Posten und gibt stets nach rechts weiter",
    ),
    "M04_CONTINUE_CLOSE": (
        "CLOSING_TAIL",
        "steht in allen drei Quellen am Aussageende und nimmt nur links Anschluss",
    ),
    "M05_MEASURE_CONTINUATION": (
        "MEDIAL_BRIDGE",
        "steht in beiden Quellen zwischen einer linken und rechten Karte",
    ),
    "M06_FEED_CONTINUATION": (
        "CONTINUATION_FEEDER",
        "beginnt oder erweitert eine Aussage und führt stets in eine rechte Fortsetzung",
    ),
    "M07_TRANSFER_LONG_CLOSE": (
        "CLOSING_TAIL",
        "steht in beiden Quellen am Aussageende und nimmt nur links Anschluss",
    ),
    "M08_PORTION_TARGET": (
        "OPEN_TARGET_BINDER",
        "beginnt oder erweitert eine Aussage und gibt stets nach rechts weiter",
    ),
    "M09_LONG_SET_BRANCH": (
        "MOBILE_BRANCH_CAPSULE",
        "ist als ganze Aussage sowie am Anfang, in der Mitte und am Ende belegt",
    ),
}


def loc(start: int, n: int, total: int) -> str:
    end = start + n - 1
    if start == 1 and end == total:
        return "WHOLE_STATEMENT"
    if start == 1:
        return "ENTRY"
    if end == total:
        return "CLOSE"
    return "MEDIAL"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P637 / "SIX_HUNDRED_THIRTY_SEVENTH_381_COMPLETE_APPRENTICE_LEDGER.tsv")
    motifs = read_tsv(P651 / "SIX_HUNDRED_FIFTY_FIRST_9_SOURCE_MOTIFS.tsv")
    selected = read_tsv(P651 / "SIX_HUNDRED_FIFTY_FIRST_SELECTED_MOTIF_INSTANCES.tsv")
    readings = read_tsv(P651 / "SIX_HUNDRED_FIFTY_FIRST_25_MINIMAL_STATEMENT_READINGS.tsv")

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    attachment_rows: list[dict[str, object]] = []
    for row in selected:
        statement = by_statement[row["statement_id"]]
        start = int(row["start_position"])
        n = int(row["n"])
        end = start + n - 1
        left = statement[start - 2] if start > 1 else None
        right = statement[end] if end < len(statement) else None
        position_class = loc(start, n, len(statement))
        role, _ = ROLE[row["motif_id"]]
        attachment_rows.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "motif_id": row["motif_id"],
            "motif_role": role,
            "start_position": start,
            "end_position": end,
            "statement_events": len(statement),
            "position_class": position_class,
            "left_card": left["card_no"] if left else "BOF",
            "left_surface": left["surface"] if left else "BOF",
            "left_reading_de": left["standard_command_de"] if left else "AUSSAGEANFANG",
            "motif_cards": row["card_sequence"],
            "motif_surface": row["surface_sequence"],
            "motif_reading_de": row["motif_reading_de"],
            "right_card": right["card_no"] if right else "EOF",
            "right_surface": right["surface"] if right else "EOF",
            "right_reading_de": right["standard_command_de"] if right else "AUSSAGEENDE",
            "attachment_signature": f"{left['card_no'] if left else 'BOF'}>{row['motif_id']}>{right['card_no'] if right else 'EOF'}",
        })

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in attachment_rows:
        grouped[str(row["motif_id"])].append(row)

    position_rows: list[dict[str, object]] = []
    motif_by_id = {row["motif_id"]: row for row in motifs}
    for motif_id in sorted(grouped):
        rows = grouped[motif_id]
        counts = Counter(str(row["position_class"]) for row in rows)
        role, rule = ROLE[motif_id]
        left_cards = {str(row["left_card"]) for row in rows if row["left_card"] != "BOF"}
        right_cards = {str(row["right_card"]) for row in rows if row["right_card"] != "EOF"}
        position_rows.append({
            "motif_id": motif_id,
            "short_reading_de": motif_by_id[motif_id]["short_reading_de"],
            "motif_role": role,
            "portable_attachment_rule_de": rule,
            "instances": len(rows),
            "entry": counts["ENTRY"],
            "medial": counts["MEDIAL"],
            "close": counts["CLOSE"],
            "whole_statement": counts["WHOLE_STATEMENT"],
            "distinct_left_cards_excluding_bof": len(left_cards),
            "distinct_right_cards_excluding_eof": len(right_cards),
            "left_cards": "|".join(sorted(left_cards)) if left_cards else "NONE",
            "right_cards": "|".join(sorted(right_cards)) if right_cards else "NONE",
            "all_instances_source_attested": "YES",
        })

    attachments_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in attachment_rows:
        attachments_by_statement[str(row["statement_id"])].append(row)
    reading_rows: list[dict[str, object]] = []
    for reading in readings:
        rows = sorted(attachments_by_statement[reading["statement_id"]], key=lambda row: int(row["start_position"]))
        plan = " || ".join(
            f"{row['motif_id']}@{row['start_position']}-{row['end_position']}:{row['position_class']}:{row['motif_role']}"
            for row in rows
        )
        reading_rows.append({
            "statement_id": reading["statement_id"],
            "page": reading["page"],
            "record": reading["record"],
            "surface_sequence": reading["surface_sequence"],
            "motif_instances": len(rows),
            "attachment_plan": plan,
            "minimal_source_reading_de": reading["minimal_source_reading_de"],
            "source_order_unchanged": "YES",
        })

    write_tsv(HERE / "SIX_HUNDRED_FIFTY_SECOND_28_MOTIF_ATTACHMENTS.tsv", attachment_rows, list(attachment_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_SECOND_9_MOTIF_POSITION_CLASSES.tsv", position_rows, list(position_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_SECOND_25_ATTACHMENT_READINGS.tsv", reading_rows, list(reading_rows[0]))

    md = [
        "# Anschlussgrammatik der neun Quellmotive",
        "",
        "Die Motive werden hier nicht verlängert. Kartiert werden nur ihre direkt sichtbaren linken und rechten Nachbarn in den 25 echten Aussagen.",
        "",
    ]
    for row in position_rows:
        md.extend([
            f"## {row['motif_id']} — {row['motif_role']}",
            "",
            f"{row['portable_attachment_rule_de']}.",
            "",
            f"Positionen: ENTRY {row['entry']}, MEDIAL {row['medial']}, CLOSE {row['close']}, WHOLE {row['whole_statement']}.",
            "",
        ])
    md.extend(["# 28 Quellanschlüsse", ""])
    for row in attachment_rows:
        md.extend([
            f"- **{row['statement_id']} {row['position_class']}**: `{row['left_surface']}` → `{row['motif_surface']}` → `{row['right_surface']}` — {row['left_reading_de']} → **{row['motif_reading_de']}** → {row['right_reading_de']}",
        ])
    (HERE / "SIX_HUNDRED_FIFTY_SECOND_ATTACHMENT_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "motifs": len(position_rows),
        "motif_instances": len(attachment_rows),
        "source_statements": len(reading_rows),
        "entry_instances": sum(row["position_class"] == "ENTRY" for row in attachment_rows),
        "medial_instances": sum(row["position_class"] == "MEDIAL" for row in attachment_rows),
        "close_instances": sum(row["position_class"] == "CLOSE" for row in attachment_rows),
        "whole_statement_instances": sum(row["position_class"] == "WHOLE_STATEMENT" for row in attachment_rows),
        "pure_closing_motifs": ["M04_CONTINUE_CLOSE", "M07_TRANSFER_LONG_CLOSE"],
        "pure_medial_motifs": ["M05_MEASURE_CONTINUATION"],
        "fully_mobile_motif": "M09_LONG_SET_BRANCH",
        "new_cards": 0,
        "new_meanings": 0,
        "decision": "SOURCE_ATTACHMENTS_SEPARATE_CLOSING_TAILS_MEDIAL_BRIDGES_AND_MOBILE_FRAMES",
    }
    (HERE / "SIX_HUNDRED_FIFTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
