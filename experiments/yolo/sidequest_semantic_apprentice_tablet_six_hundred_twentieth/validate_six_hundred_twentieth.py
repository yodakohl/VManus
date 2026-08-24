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
    tablet = read("SIX_HUNDRED_TWENTIETH_8_MODULE_APPRENTICE_TABLET.tsv")
    trace = read("SIX_HUNDRED_TWENTIETH_38_C3_APPRENTICE_TRACE.tsv")
    events = read("SIX_HUNDRED_TWENTIETH_103_C3_EVENT_COPY_TRACE.tsv")
    errors = read("SIX_HUNDRED_TWENTIETH_12_APPRENTICE_ERRORS.tsv")
    checks = {
        "tablet8": len(tablet) == 8 and len({row["module"] for row in tablet}) == 8,
        "all_tablet_fields": all(all(value.strip() for value in row.values()) for row in tablet),
        "trace38": len(trace) == 38 and len({row["statement_id"] for row in trace}) == 38,
        "records_h3_b3": {row["record"] for row in trace} == {"H3", "B3"},
        "events103": len(events) == 103 and len({row["event_id"] for row in events}) == 103,
        "event_cards": len({row["card_no"] for row in events}) > 40,
        "forward_backward38": all(row["forward_backward_agree"] == "YES" and row["module_sequence"] == row["backread_modules"] for row in trace),
        "errors12": len(errors) == 12 and len({row["error_id"] for row in errors}) == 12,
        "fixed_pages": {row["page"] for row in events} == {"f11r", "f83r"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_TWENTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
