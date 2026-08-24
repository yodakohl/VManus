#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    sheets = read("FIVE_HUNDRED_TWENTY_FIFTH_SEVEN_PAGE_RENDERER_SHEETS.tsv")
    entries = read("FIVE_HUNDRED_TWENTY_FIFTH_FIFTY_NINE_PAGE_ADDRESSED_ENTRIES.tsv")
    log = read("FIVE_HUNDRED_TWENTY_FIFTH_381_PAGE_SHEET_LOG.tsv")
    decisions = read("FIVE_HUNDRED_TWENTY_FIFTH_SEVEN_CONSCIOUS_DECISIONS.tsv")
    checks = {
        "sheets7": len(sheets) == 7
        and [row["page"] for row in sheets] == ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"],
        "records11": sum(int(row["record_count"]) for row in sheets) == 11,
        "entries59": len(entries) == 59 and len({row["event_id"] for row in entries}) == 59,
        "page_entry_counts": {row["page"]: int(row["addressed_wrapper_entries"]) for row in sheets}
        == {"f10r": 9, "f11r": 2, "f55v": 4, "f56r": 2, "f81v": 14, "f82r": 6, "f83r": 22},
        "addresses_unique": len({row["full_address"] for row in entries}) == 59,
        "log381": len(log) == 381 and len({row["event_id"] for row in log}) == 381,
        "renderer_partition314_8_59": Counter(row["page_renderer_action"] for row in log)
        == Counter({"GLOBAL_RULE_RENDERER": 314, "AUTOMATIC_CONTEXT_RULE": 8, "APPLY_PAGE_ADDRESSED_ENTRY": 59}),
        "decisions7": len(decisions) == 7,
        "only_page_loads": Counter(row["decision_type"] for row in decisions)
        == Counter({"LOAD_PAGE_RENDERER_SHEET": 7}),
        "conscious7": sum(row["page_sheet_master_mode"] == "CONSCIOUS_PAGE_SETUP" for row in log) == 7,
        "automatic374": sum(row["page_sheet_master_mode"] == "AUTOMATIC_FLOW" for row in log) == 374,
        "surface_roundtrip": all(row["stamp_output_surface"] == row["renderer_final_surface"] for row in log),
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in sheets + entries + log + decisions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_TWENTY_FIFTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
