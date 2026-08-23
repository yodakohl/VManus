#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    trace = rows("HUNDRED_THIRTY_FIRST_381_EVENT_DRAWER_TRACE.tsv")
    records = rows("HUNDRED_THIRTY_FIRST_ELEVEN_RECORD_PROFILES.tsv")
    sections = rows("HUNDRED_THIRTY_FIRST_HERBAL_BIO_COMPARISON.tsv")
    checks = {
        "trace_381": len(trace) == 381,
        "records_11": len(records) == 11,
        "sections_2": len(sections) == 2,
        "event_serials_unique": len({row["event_serial"] for row in trace}) == 381,
        "record_event_sum": sum(int(row["event_count"]) for row in records) == 381,
        "section_event_sum": sum(int(row["events"]) for row in sections) == 381,
        "herbal_material_gt_transfer": int(sections[0]["material"]) > int(sections[0]["transfer"]),
        "bio_transfer_gt_material": int(sections[1]["transfer"]) > int(sections[1]["material"]),
        "no_empty_cells": all(all(value for value in row.values()) for table in (trace, records, sections) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
