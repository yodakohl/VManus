#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    stats = read_tsv("PASS968_WRAPPER_POSITION_COUNTS.tsv")
    events = read_tsv("PASS968_281_POSITION_RENDERER_TRACE.tsv")
    exceptions = read_tsv("PASS968_12_COPY_EXCEPTIONS.tsv")
    by_wrapper = {row["wrapper"]: row for row in stats}
    checks = {
        "events_281": len(events) == 281 and len({row["event_id"] for row in events}) == 281,
        "position_matches_269": sum(row["record_position_match"] == "YES" for row in events) == 269,
        "exceptions_12": len(exceptions) == 12,
        "exception_identity": {row["event_id"] for row in exceptions} == {row["event_id"] for row in events if row["record_position_match"] != "YES"},
        "q_events_75": by_wrapper["q"]["events"] == "75",
        "q_after_close_33": by_wrapper["q"]["after_close"] == "33",
        "q_field_entry_40": by_wrapper["q"]["field_first_or_only"] == "40",
        "q_line_first_7": by_wrapper["q"]["line_first"] == "7",
        "s_events_23": by_wrapper["s"]["events"] == "23",
        "s_line_first_14": by_wrapper["s"]["line_first"] == "14",
        "no_semantic_wrapper_effect": all(row["portable_renderer_reading_de"] == "gleiche Kartenbedeutung; nur Stellungs-/Handhülle" for row in events),
        "no_sealed_pages": not any("f84" in str(row).lower() for row in stats + events + exceptions),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS968_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
