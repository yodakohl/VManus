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
    words = read("SIX_HUNDRED_FIFTEENTH_39_WORD_GLOSSARY.tsv")
    events = read("SIX_HUNDRED_FIFTEENTH_381_READABLE_INTERLINEAR.tsv")
    statements = read("SIX_HUNDRED_FIFTEENTH_116_READABLE_STATEMENTS.tsv")
    records = read("SIX_HUNDRED_FIFTEENTH_11_RECORD_SUMMARY.tsv")
    checks = {
        "words39": len(words) == 39 and len({row["canonical_component"] for row in words}) == 39,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "cards173": len({row["card_no"] for row in events}) == 173,
        "commands163": len({(row["semantic_component_parse"], row["standard_command_de"]) for row in events}) == 163,
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "statement_events381": sum(int(row["event_count"]) for row in statements) == 381,
        "records11": len(records) == 11 and {row["record"] for row in records} == {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"},
        "record_events381": sum(int(row["events"]) for row in records) == 381,
        "three_revisions": sum(row["new_613_nuance"] == "YES" for row in statements) == 3,
        "all_readable": all(row["readable_workshop_de"].strip() for row in statements),
        "fixed_pages": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIFTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
