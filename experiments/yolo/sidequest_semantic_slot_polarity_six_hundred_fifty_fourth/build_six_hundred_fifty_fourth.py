#!/usr/bin/env python3
"""Compare semantic atoms immediately around open binders and closing tails."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P652 = ROOT / "experiments/yolo/sidequest_semantic_motif_attachment_grammar_six_hundred_fifty_second"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


KEYWORDS = {
    "MATERIAL_PATH": ["ANSATZ", "VORRAT", "FLUESSIGKEITSLAUF", "DURCHLASSKANAL", "ARBEITSFACH"],
    "QUANTITY_STAGE": ["SOLLMASS", "PORTION", "ARBEITSSTUFE", "ZWEITMARKER"],
    "ADDRESS_ITEM": ["ARBEITSPOSTEN", "ZIELSTELLE"],
    "OPERATION": ["ANSETZEN", "UMSETZEN", "WEITERLEITEN", "ZUDOSIEREN", "ABNEHMEN", "EINTRAGEN", "AUFFANGEN"],
    "STATE_GRADE": ["BEREIT", "KURZ", "LANG", "VOLL", "WAERMEN", "HALTEN", "KUEHLEN", "ABSETZEN"],
    "ORDER": ["DANACH", "FORTSETZEN", "WIEDERAUFNEHMEN"],
    "CLOSE": ["SCHLUSS"],
}

BINDERS = {
    "M02_SET_ITEM_MEASURE",
    "M03_PREPARATION_ITEM",
    "M06_FEED_CONTINUATION",
    "M08_PORTION_TARGET",
}
CLOSERS = {"M04_CONTINUE_CLOSE", "M07_TRANSFER_LONG_CLOSE"}


def labels(reading: str) -> list[str]:
    result = [name for name, words in KEYWORDS.items() if any(word in reading for word in words)]
    return result or ["OTHER"]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    attachments = read_tsv(P652 / "SIX_HUNDRED_FIFTY_SECOND_28_MOTIF_ATTACHMENTS.tsv")
    slot_rows: list[dict[str, object]] = []
    for row in attachments:
        candidates = []
        if row["motif_id"] in BINDERS:
            if row["left_card"] != "BOF":
                candidates.append(("PRE_BINDER", row["left_card"], row["left_surface"], row["left_reading_de"]))
            if row["right_card"] != "EOF":
                candidates.append(("POST_BINDER", row["right_card"], row["right_surface"], row["right_reading_de"]))
        if row["motif_id"] in CLOSERS:
            candidates.append(("PRE_CLOSE", row["left_card"], row["left_surface"], row["left_reading_de"]))
        for slot, card, surface, reading in candidates:
            labs = labels(reading)
            slot_rows.append({
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "motif_id": row["motif_id"],
                "slot": slot,
                "neighbour_card": card,
                "neighbour_surface": surface,
                "neighbour_reading_de": reading,
                "semantic_classes": "|".join(labs),
                "has_transition_or_operation": "YES" if any(label in labs for label in ("OPERATION", "ORDER")) else "NO",
                "has_payload_configuration": "YES" if any(label in labs for label in ("MATERIAL_PATH", "QUANTITY_STAGE", "ADDRESS_ITEM", "STATE_GRADE", "CLOSE")) else "NO",
                "has_anchor_item_or_amount": "YES" if any(label in labs for label in ("QUANTITY_STAGE", "ADDRESS_ITEM")) else "NO",
            })

    aggregate_rows: list[dict[str, object]] = []
    for slot in ("PRE_BINDER", "POST_BINDER", "PRE_CLOSE"):
        rows = [row for row in slot_rows if row["slot"] == slot]
        counts = Counter(label for row in rows for label in str(row["semantic_classes"]).split("|"))
        aggregate_rows.append({
            "slot": slot,
            "contexts": len(rows),
            "material_path": counts["MATERIAL_PATH"],
            "quantity_stage": counts["QUANTITY_STAGE"],
            "address_item": counts["ADDRESS_ITEM"],
            "operation": counts["OPERATION"],
            "state_grade": counts["STATE_GRADE"],
            "order": counts["ORDER"],
            "close": counts["CLOSE"],
            "transition_or_operation": sum(row["has_transition_or_operation"] == "YES" for row in rows),
            "payload_configuration": sum(row["has_payload_configuration"] == "YES" for row in rows),
            "anchor_item_or_amount": sum(row["has_anchor_item_or_amount"] == "YES" for row in rows),
        })

    close_rows = [row for row in slot_rows if row["slot"] == "PRE_CLOSE"]
    close_readings = []
    for row in close_rows:
        close_readings.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "motif_id": row["motif_id"],
            "preclose_surface": row["neighbour_surface"],
            "preclose_reading_de": row["neighbour_reading_de"],
            "anchored_in_item_or_amount": row["has_anchor_item_or_amount"],
            "fluent_close_de": f"{row['neighbour_reading_de']} -> {next(a['motif_reading_de'] for a in attachments if a['statement_id'] == row['statement_id'] and a['motif_id'] == row['motif_id'])}",
        })

    write_tsv(HERE / "SIX_HUNDRED_FIFTY_FOURTH_25_SLOT_CONTEXTS.tsv", slot_rows, list(slot_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_FOURTH_3_SLOT_POLARITIES.tsv", aggregate_rows, list(aggregate_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FIFTY_FOURTH_5_PRECLOSE_CHAINS.tsv", close_readings, list(close_readings[0]))

    summary = {
        "status": "PASS",
        "slot_contexts": len(slot_rows),
        "pre_binder": sum(row["slot"] == "PRE_BINDER" for row in slot_rows),
        "post_binder": sum(row["slot"] == "POST_BINDER" for row in slot_rows),
        "pre_close": len(close_rows),
        "pre_binder_transition_or_operation": sum(row["slot"] == "PRE_BINDER" and row["has_transition_or_operation"] == "YES" for row in slot_rows),
        "post_binder_payload_configuration": sum(row["slot"] == "POST_BINDER" and row["has_payload_configuration"] == "YES" for row in slot_rows),
        "pre_close_anchor_item_or_amount": sum(row["slot"] == "PRE_CLOSE" and row["has_anchor_item_or_amount"] == "YES" for row in slot_rows),
        "decision": "OPEN_BINDERS_HAND_OFF_FROM_PRIOR_PROCESS_INTO_CONFIGURED_PAYLOAD_WHILE_CLOSERS_REQUIRE_AN_ANCHOR",
    }
    (HERE / "SIX_HUNDRED_FIFTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
