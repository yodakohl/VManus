#!/usr/bin/env python3
"""Validate the complete fixed-page punctuated edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    rows = read("THREE_HUNDRED_SECOND_116_PUNCTUATED_STATEMENTS.tsv")
    classes = Counter(r["punctuation_class"] for r in rows)
    checks = {
        "statements_116": len(rows) == 116 and len({r["statement_id"] for r in rows}) == 116,
        "records_11": len({r["record_unit_id"] for r in rows}) == 11,
        "events_381": sum(int(r["visible_event_count"]) for r in rows) == 381,
        "source_tokens_380": sum(int(r["read_source_token_count"]) for r in rows) == 380,
        "punctuation_90_18_8": classes == Counter({"COMMIT_SEMICOLON": 90, "OPEN_TO_NEXT_STATEMENT": 18, "OPEN_RECORD_RELEASE": 8}),
        "line_crossings_19": sum(int(r["physical_line_crossings_absorbed"]) for r in rows) == 19,
        "owner_resets_4": sum(int(r["owner_resets_marked"]) for r in rows) == 4,
        "read_once_1": sum(int(r["read_once_duplicates_collapsed"]) for r in rows) == 1,
        "commit_has_semicolon": all(r["surface_punctuated"].endswith(";") for r in rows if r["punctuation_class"] == "COMMIT_SEMICOLON"),
        "open_not_semicolon": all(not r["surface_punctuated"].endswith(";") for r in rows if r["punctuation_class"] != "COMMIT_SEMICOLON"),
        "no_pipe_translation": all("|" not in r["workshop_german_punctuated"] for r in rows),
        "no_sealed_page": not any("f" + "84" in p.read_text(encoding="utf-8").lower() for p in HERE.glob("*")),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [k for k, v in checks.items() if not v]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
