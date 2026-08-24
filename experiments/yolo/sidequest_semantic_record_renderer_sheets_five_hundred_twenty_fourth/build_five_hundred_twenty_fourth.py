#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P523 = ROOT / "experiments/yolo/sidequest_semantic_context_wrapper_rules_five_hundred_twenty_third"


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
    source = read_tsv(P523 / "FIVE_HUNDRED_TWENTY_THIRD_381_CONTEXT_RENDERER_LOG.tsv")
    residual = read_tsv(P523 / "FIVE_HUNDRED_TWENTY_THIRD_FIFTY_NINE_RESIDUAL_ASSIGNMENTS.tsv")
    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    residual_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        records[row["record"]].append(row)
    for row in residual:
        residual_by_record[row["record"]].append(row)

    sheet_rows: list[dict[str, str]] = []
    entry_rows: list[dict[str, str]] = []
    sheet_for_record: dict[str, str] = {}
    entry_for_event: dict[str, dict[str, str]] = {}
    for number, (record, events) in enumerate(records.items(), 1):
        sheet_id = f"RS{number:02d}"
        sheet_for_record[record] = sheet_id
        items = residual_by_record[record]
        for local_no, item in enumerate(items, 1):
            addressed = {
                "sheet_id": sheet_id,
                "entry_no_within_sheet": str(local_no),
                "record": record,
                "page": item["page"],
                "locus": item["locus"],
                "event_id": item["event_id"],
                "input_rule_surface": item["input_rule_surface"],
                "retain_tail": item["retain_tail"],
                "wrapper_stamp": item["apply_wrapper_stamp"],
                "output_surface": item["local_output_surface"],
                "address_rule": "LOCUS_PLUS_INPUT_SURFACE",
                "instruction_de": f"In {item['locus']} bei {item['input_rule_surface']} den Stempel {item['apply_wrapper_stamp']} setzen.",
            }
            entry_rows.append(addressed)
            entry_for_event[item["event_id"]] = addressed
        sheet_rows.append(
            {
                "sheet_id": sheet_id,
                "record": record,
                "page": events[0]["page"],
                "load_event": events[0]["event_id"],
                "record_events": str(len(events)),
                "addressed_wrapper_entries": str(len(items)),
                "affected_loci": str(len({item["locus"] for item in items})),
                "wrapper_stamps_used": "|".join(sorted({item["apply_wrapper_stamp"] for item in items})),
                "load_instruction_de": "Einmal am Recordanfang laden; Einträge nur an ihrer Locusadresse anwenden.",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_FOURTH_ELEVEN_RECORD_RENDERER_SHEETS.tsv", sheet_rows)
    write_tsv("FIVE_HUNDRED_TWENTY_FOURTH_FIFTY_NINE_ADDRESSED_ENTRIES.tsv", entry_rows)

    load_events = {row["load_event"]: row for row in sheet_rows}
    output: list[dict[str, str]] = []
    decisions: list[dict[str, str]] = []
    for row in source:
        load = row["event_id"] in load_events
        if load:
            sheet = load_events[row["event_id"]]
            decisions.append(
                {
                    "decision_no": "",
                    "event_id": row["event_id"],
                    "statement_id": row["statement_id"],
                    "record": row["record"],
                    "page": row["page"],
                    "decision_type": "LOAD_RECORD_RENDERER_SHEET",
                    "selected_value": sheet["sheet_id"],
                }
            )
        entry = entry_for_event.get(row["event_id"])
        output.append(
            {
                **row,
                "record_renderer_sheet": sheet_for_record[row["record"]],
                "record_sheet_load_here": "YES" if load else "NO",
                "record_sheet_entry": (
                    f"{entry['sheet_id']}:{entry['entry_no_within_sheet']}" if entry else "NONE"
                ),
                "record_renderer_action": (
                    "AUTOMATIC_CONTEXT_RULE"
                    if row["context_wrapper_rule"] != "NONE"
                    else "APPLY_ADDRESSED_RECORD_ENTRY"
                    if entry
                    else "GLOBAL_RULE_RENDERER"
                ),
                "record_sheet_master_mode": "CONSCIOUS_RECORD_SETUP" if load else "AUTOMATIC_FLOW",
            }
        )
    for number, row in enumerate(decisions, 1):
        row["decision_no"] = str(number)
    write_tsv("FIVE_HUNDRED_TWENTY_FOURTH_381_RECORD_SHEET_LOG.tsv", output)
    write_tsv("FIVE_HUNDRED_TWENTY_FOURTH_ELEVEN_CONSCIOUS_DECISIONS.tsv", decisions)

    summary = {
        "status": "PASS",
        "events": len(output),
        "record_sheets": len(sheet_rows),
        "addressed_entries": len(entry_rows),
        "context_rule_events": sum(row["context_wrapper_rule"] != "NONE" for row in output),
        "global_rule_events": sum(row["record_renderer_action"] == "GLOBAL_RULE_RENDERER" for row in output),
        "conscious_record_loads": len(decisions),
        "conscious_events": sum(row["record_sheet_master_mode"] == "CONSCIOUS_RECORD_SETUP" for row in output),
        "automatic_events": sum(row["record_sheet_master_mode"] == "AUTOMATIC_FLOW" for row in output),
        "entries_per_record": dict(Counter({row["record"]: int(row["addressed_wrapper_entries"]) for row in sheet_rows})),
    }
    (HERE / "FIVE_HUNDRED_TWENTY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
