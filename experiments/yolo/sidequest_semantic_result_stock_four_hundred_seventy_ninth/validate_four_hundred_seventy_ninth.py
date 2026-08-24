#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    traces = read("FOUR_HUNDRED_SEVENTY_NINTH_FOUR_RECEIVED_STOCK_TRACES.tsv")
    dictionary = read("FOUR_HUNDRED_SEVENTY_NINTH_173_RECEIVED_STOCK_DICTIONARY.tsv")
    events = read("FOUR_HUNDRED_SEVENTY_NINTH_381_RECEIVED_STOCK_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_SEVENTY_NINTH_116_RECEIVED_STOCK_STATEMENTS.tsv")
    units = read("FOUR_HUNDRED_SEVENTY_NINTH_14_RECEIVED_STOCK_UNIT_EDITIONS.tsv")
    checks = {
        "traces_4": len(traces) == 4,
        "trace_records_3": len({row["record_unit_id"] for row in traces}) == 3,
        "trace_registers_2": len({next(e["register"] for e in events if e["event_id"] == row["event_id"]) for row in traces}) == 2,
        "dictionary_173": len(dictionary) == 173,
        "dictionary_one_revision": sum(row["pass479_revision"] == "YES" for row in dictionary) == 1,
        "events_381": len(events) == 381,
        "target_events_4": sum(row["pass479_target_card"] == "YES" for row in events) == 4,
        "old_result_stock_absent": all("ERGEBNISPOSTEN" not in row["pass479_event_de"] and "Ergebnisbestand" not in row["pass479_event_de"] for row in events),
        "statements_116": len(statements) == 116,
        "affected_statements_4": sum(row["contains_received_stock_card"] == "YES" for row in statements) == 4,
        "units_14": len(units) == 14,
        "groups_776": sum(int(row["groups"]) for row in units) == 776,
        "fixed_pages_only": {row["page"] for row in events + units} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row.get("page", "").startswith("f84") for row in events + statements + units),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_SEVENTY_NINTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
