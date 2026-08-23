#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("HUNDRED_NINETY_SEVENTH_103_EVENT_NORMALIZED_INTERLINEAR.tsv")
    fields = read("HUNDRED_NINETY_SEVENTH_42_FIELD_NORMALIZED_EDITION.tsv")
    statements = read("HUNDRED_NINETY_SEVENTH_38_STATEMENT_REVISED_EDITION.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "103_events": len(events) == 103 and len({row["event_id"] for row in events}) == 103,
        "h3_17_b3_86": sum(row["record_unit_id"] == "H3" for row in events) == 17 and sum(row["record_unit_id"] == "B3" for row in events) == 86,
        "42_fields": len(fields) == 42 and len({row["field_id"] for row in fields}) == 42,
        "38_statements": len(statements) == 38 and len({row["statement_id"] for row in statements}) == 38,
        "field_event_accounting": sum(len(row["card_sequence"].split()) for row in fields) == 103,
        "all_normalized": all(row["normalized_master_form"] for row in events),
        "all_translated": all(row["revised_fluent_translation_de"] for row in statements),
        "only_h3_b3": {row["record_unit_id"] for row in events} == {"H3", "B3"},
        "sealed_absent": summary["sealed_pages_accessed"] is False,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
