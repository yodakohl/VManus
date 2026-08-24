#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P524 = ROOT / "experiments/yolo/sidequest_semantic_record_renderer_sheets_five_hundred_twenty_fourth"


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
    source = read_tsv(P524 / "FIVE_HUNDRED_TWENTY_FOURTH_381_RECORD_SHEET_LOG.tsv")
    entries = read_tsv(P524 / "FIVE_HUNDRED_TWENTY_FOURTH_FIFTY_NINE_ADDRESSED_ENTRIES.tsv")
    page_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    page_entries: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        page_events[row["page"]].append(row)
    for row in entries:
        page_entries[row["page"]].append(row)

    sheets: list[dict[str, str]] = []
    addressed: list[dict[str, str]] = []
    sheet_for_page: dict[str, str] = {}
    entry_for_event: dict[str, dict[str, str]] = {}
    for number, (page, events) in enumerate(page_events.items(), 1):
        sheet_id = f"PS{number:02d}"
        sheet_for_page[page] = sheet_id
        items = page_entries[page]
        for local_no, item in enumerate(items, 1):
            row = {
                "page_sheet_id": sheet_id,
                "entry_no_within_page": str(local_no),
                "page": page,
                "record": item["record"],
                "locus": item["locus"],
                "event_id": item["event_id"],
                "input_rule_surface": item["input_rule_surface"],
                "retain_tail": item["retain_tail"],
                "wrapper_stamp": item["wrapper_stamp"],
                "output_surface": item["output_surface"],
                "full_address": f"{item['record']}:{item['locus']}:{item['input_rule_surface']}",
                "instruction_de": f"Nur an {item['record']} / {item['locus']} den Stempel {item['wrapper_stamp']} auf {item['input_rule_surface']} anwenden.",
            }
            addressed.append(row)
            entry_for_event[item["event_id"]] = row
        sheets.append(
            {
                "page_sheet_id": sheet_id,
                "page": page,
                "load_event": events[0]["event_id"],
                "page_events": str(len(events)),
                "records": "|".join(dict.fromkeys(row["record"] for row in events)),
                "record_count": str(len({row["record"] for row in events})),
                "addressed_wrapper_entries": str(len(items)),
                "affected_loci": str(len({(item["record"], item["locus"]) for item in items})),
                "load_instruction_de": "Beim Auflegen der Seite einmal laden; Record- und Locusadresse verhindern Kollisionen.",
            }
        )
    write_tsv("FIVE_HUNDRED_TWENTY_FIFTH_SEVEN_PAGE_RENDERER_SHEETS.tsv", sheets)
    write_tsv("FIVE_HUNDRED_TWENTY_FIFTH_FIFTY_NINE_PAGE_ADDRESSED_ENTRIES.tsv", addressed)

    load_event = {row["load_event"]: row for row in sheets}
    output: list[dict[str, str]] = []
    decisions: list[dict[str, str]] = []
    for row in source:
        load = row["event_id"] in load_event
        if load:
            sheet = load_event[row["event_id"]]
            decisions.append(
                {
                    "decision_no": "",
                    "event_id": row["event_id"],
                    "statement_id": row["statement_id"],
                    "record": row["record"],
                    "page": row["page"],
                    "decision_type": "LOAD_PAGE_RENDERER_SHEET",
                    "selected_value": sheet["page_sheet_id"],
                }
            )
        entry = entry_for_event.get(row["event_id"])
        output.append(
            {
                **row,
                "page_renderer_sheet": sheet_for_page[row["page"]],
                "page_sheet_load_here": "YES" if load else "NO",
                "page_sheet_entry": (
                    f"{entry['page_sheet_id']}:{entry['entry_no_within_page']}" if entry else "NONE"
                ),
                "page_renderer_action": (
                    "AUTOMATIC_CONTEXT_RULE"
                    if row["context_wrapper_rule"] != "NONE"
                    else "APPLY_PAGE_ADDRESSED_ENTRY"
                    if entry
                    else "GLOBAL_RULE_RENDERER"
                ),
                "page_sheet_master_mode": "CONSCIOUS_PAGE_SETUP" if load else "AUTOMATIC_FLOW",
            }
        )
    for number, row in enumerate(decisions, 1):
        row["decision_no"] = str(number)
    write_tsv("FIVE_HUNDRED_TWENTY_FIFTH_381_PAGE_SHEET_LOG.tsv", output)
    write_tsv("FIVE_HUNDRED_TWENTY_FIFTH_SEVEN_CONSCIOUS_DECISIONS.tsv", decisions)

    summary = {
        "status": "PASS",
        "events": len(output),
        "page_sheets": len(sheets),
        "record_namespaces": sum(int(row["record_count"]) for row in sheets),
        "addressed_entries": len(addressed),
        "conscious_page_loads": len(decisions),
        "conscious_events": sum(row["page_sheet_master_mode"] == "CONSCIOUS_PAGE_SETUP" for row in output),
        "automatic_events": sum(row["page_sheet_master_mode"] == "AUTOMATIC_FLOW" for row in output),
        "entries_per_page": {row["page"]: int(row["addressed_wrapper_entries"]) for row in sheets},
    }
    (HERE / "FIVE_HUNDRED_TWENTY_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
