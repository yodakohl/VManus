#!/usr/bin/env python3
"""Validate complete Biological operating modes."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    events = read("THREE_HUNDRED_EIGHTH_281_EVENT_OPERATING_MODES.tsv")
    statements = read("THREE_HUNDRED_EIGHTH_97_STATEMENT_OPERATING_MODES.tsv")
    modes = read("THREE_HUNDRED_EIGHTH_SEVEN_MODE_LEXICON.tsv")
    records = read("THREE_HUNDRED_EIGHTH_SIX_RECORD_MODE_SUMMARY.tsv")
    expected = {"CHARGE", "TREAT", "SETTLE", "PASS_FILTER", "DISCHARGE", "MEASURE", "LOCAL_CONTROL"}
    checks = {
        "events_281": len(events) == 281 and len({r["event_id"] for r in events}) == 281,
        "statements_97": len(statements) == 97 and len({r["statement_id"] for r in statements}) == 97,
        "records_6": len(records) == 6 and {r["record_unit_id"] for r in records} == {f"B{i}" for i in range(1, 7)},
        "modes_7": len(modes) == 7 and {r["operating_mode"] for r in modes} == expected,
        "all_modes_used_events": {r["operating_mode"] for r in events} == expected,
        "all_modes_used_statements": {r["primary_operating_mode"] for r in statements} == expected,
        "mode_event_totals": sum(int(r["event_count"]) for r in modes) == 281,
        "mode_statement_totals": sum(int(r["primary_statement_count"]) for r in modes) == 97,
        "block_bindings_18": sum(r["procedure_block_id"] != "NONE" for r in statements) == 18,
        "no_empty_sequences": all(r["operating_mode_sequence"].strip() for r in statements),
        "no_sealed_page": not any("f" + "84" in p.read_text(encoding="utf-8").lower() for p in HERE.glob("*") if p.suffix in {".tsv", ".md"}),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
