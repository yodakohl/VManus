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
    sheets = read("FIVE_HUNDRED_TWENTY_FOURTH_ELEVEN_RECORD_RENDERER_SHEETS.tsv")
    entries = read("FIVE_HUNDRED_TWENTY_FOURTH_FIFTY_NINE_ADDRESSED_ENTRIES.tsv")
    log = read("FIVE_HUNDRED_TWENTY_FOURTH_381_RECORD_SHEET_LOG.tsv")
    decisions = read("FIVE_HUNDRED_TWENTY_FOURTH_ELEVEN_CONSCIOUS_DECISIONS.tsv")
    checks = {
        "sheets11": len(sheets) == 11 and len({row["record"] for row in sheets}) == 11,
        "entries59": len(entries) == 59 and len({row["event_id"] for row in entries}) == 59,
        "record_entry_counts": Counter({row["record"]: int(row["addressed_wrapper_entries"]) for row in sheets})
        == Counter({"H1": 2, "H2": 7, "H3": 2, "H4": 4, "H5": 2, "B1": 14, "B2": 6, "B3": 15, "B4": 4, "B5": 2, "B6": 1}),
        "address_keys_unique": len({(row["record"], row["locus"], row["input_rule_surface"], row["event_id"]) for row in entries}) == 59,
        "log381": len(log) == 381 and len({row["event_id"] for row in log}) == 381,
        "renderer_partition314_8_59": Counter(row["record_renderer_action"] for row in log)
        == Counter({"GLOBAL_RULE_RENDERER": 314, "AUTOMATIC_CONTEXT_RULE": 8, "APPLY_ADDRESSED_RECORD_ENTRY": 59}),
        "decisions11": len(decisions) == 11,
        "only_record_loads": Counter(row["decision_type"] for row in decisions)
        == Counter({"LOAD_RECORD_RENDERER_SHEET": 11}),
        "conscious11": sum(row["record_sheet_master_mode"] == "CONSCIOUS_RECORD_SETUP" for row in log) == 11,
        "automatic370": sum(row["record_sheet_master_mode"] == "AUTOMATIC_FLOW" for row in log) == 370,
        "surface_roundtrip": all(row["stamp_output_surface"] == row["renderer_final_surface"] for row in log),
        "owner_choice_stays_removed": all(row["free_owner_choice"] == "NO" for row in log),
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in sheets + entries + log + decisions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_TWENTY_FOURTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
