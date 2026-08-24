#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P518 = ROOT / "experiments/yolo/sidequest_semantic_emergent_programs_five_hundred_eighteenth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read_tsv(P518 / "FIVE_HUNDRED_EIGHTEENTH_381_EMERGENT_MASTER_LOG.tsv")
    first_event_by_record: dict[str, str] = {}
    for row in source:
        first_event_by_record.setdefault(row["record"], row["event_id"])

    owner_rows: list[dict[str, str]] = []
    for row in source:
        if row["owner_reset"] != "YES":
            continue
        kind = (
            "AUTOMATIC_RECORD_OWNER_INITIALIZATION"
            if row["event_id"] == first_event_by_record[row["record"]]
            else "CONSCIOUS_INTERNAL_VISIBLE_SCENE_SHIFT"
        )
        owner_rows.append(
            {
                "owner_transition_no": str(len(owner_rows) + 1),
                "event_id": row["event_id"],
                "statement_id": row["statement_id"],
                "record": row["record"],
                "page": row["page"],
                "locus": row["locus"],
                "owner_code": row["owner_code"],
                "transition_kind": kind,
                "master_decision": "NO" if kind.startswith("AUTOMATIC") else "YES",
                "allograph_block_starts_here": row["block_start_decision"],
                "instruction_de": (
                    "Am Recordanfang den sichtbaren Hauptbesitzer automatisch laden."
                    if kind.startswith("AUTOMATIC")
                    else "Innerhalb des Records zur neu sichtbaren lokalen Szene umschalten."
                ),
            }
        )
    write_tsv("FIVE_HUNDRED_NINETEENTH_21_OWNER_TRANSITIONS.tsv", owner_rows)

    owner_by_event = {row["event_id"]: row for row in owner_rows}
    revised: list[dict[str, str]] = []
    decisions: list[dict[str, str]] = []
    for row in source:
        reasons: list[str] = []
        owner = owner_by_event.get(row["event_id"])
        owner_mode = "INHERIT_CURRENT_OWNER"
        if owner:
            owner_mode = owner["transition_kind"]
            if owner["master_decision"] == "YES":
                reasons.append("SHIFT_TO_VISIBLE_SUBSCENE")
                decisions.append(
                    {
                        "decision_no": "",
                        "event_id": row["event_id"],
                        "statement_id": row["statement_id"],
                        "record": row["record"],
                        "page": row["page"],
                        "decision_type": "SHIFT_TO_VISIBLE_SUBSCENE",
                        "selected_value": row["owner_code"],
                    }
                )
        if row["block_start_decision"] == "YES":
            reasons.append("ENTER_ALLOGRAPH_BLOCK")
            decisions.append(
                {
                    "decision_no": "",
                    "event_id": row["event_id"],
                    "statement_id": row["statement_id"],
                    "record": row["record"],
                    "page": row["page"],
                    "decision_type": "ENTER_ALLOGRAPH_BLOCK",
                    "selected_value": row["allograph_block_id"],
                }
            )
        revised.append(
            {
                **row,
                "owner_handling_mode": owner_mode,
                "record_start_owner_is_decision": "NO",
                "owner_revised_conscious_decision_count": str(len(reasons)),
                "owner_revised_conscious_reasons": "|".join(reasons) if reasons else "NONE",
                "owner_revised_master_mode": "CONSCIOUS_LOCAL_CHOICE" if reasons else "AUTOMATIC_FLOW",
            }
        )
    for number, row in enumerate(decisions, 1):
        row["decision_no"] = str(number)
    write_tsv("FIVE_HUNDRED_NINETEENTH_381_OWNER_AWARE_MASTER_LOG.tsv", revised)
    write_tsv("FIVE_HUNDRED_NINETEENTH_60_CONSCIOUS_DECISIONS.tsv", decisions)

    records: list[dict[str, str]] = []
    for record, first_event in first_event_by_record.items():
        first = next(row for row in revised if row["event_id"] == first_event)
        internal = [
            row for row in owner_rows if row["record"] == record and row["master_decision"] == "YES"
        ]
        records.append(
            {
                "record": record,
                "page": first["page"],
                "first_event": first_event,
                "initial_owner": first["owner_code"],
                "initialization": "AUTOMATIC_FROM_VISIBLE_RECORD_OWNER",
                "internal_scene_shifts": str(len(internal)),
                "internal_shift_events": "|".join(row["event_id"] for row in internal) or "NONE",
                "copy_instruction_de": "Bildbesitzer setzen; Kartenfolge bis zum nächsten sichtbaren Szenenwechsel fortführen.",
            }
        )
    write_tsv("FIVE_HUNDRED_NINETEENTH_ELEVEN_RECORD_OWNER_RULES.tsv", records)

    summary = {
        "status": "PASS",
        "events": len(revised),
        "records": len(records),
        "owner_transitions": len(owner_rows),
        "automatic_record_initializations": sum(
            row["transition_kind"] == "AUTOMATIC_RECORD_OWNER_INITIALIZATION" for row in owner_rows
        ),
        "conscious_internal_scene_shifts": sum(row["master_decision"] == "YES" for row in owner_rows),
        "decision_instances": len(decisions),
        "decision_types": dict(Counter(row["decision_type"] for row in decisions)),
        "conscious_events": sum(row["owner_revised_master_mode"] == "CONSCIOUS_LOCAL_CHOICE" for row in revised),
        "automatic_events": sum(row["owner_revised_master_mode"] == "AUTOMATIC_FLOW" for row in revised),
    }
    (HERE / "FIVE_HUNDRED_NINETEENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
