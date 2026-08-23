#!/usr/bin/env python3
"""Validate Pass 301 endpoint scope."""

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
    events = read("THREE_HUNDRED_FIRST_381_EVENT_SCOPE.tsv")
    fields = read("THREE_HUNDRED_FIRST_135_FIELD_SCOPE.tsv")
    statements = read("THREE_HUNDRED_FIRST_116_STATEMENT_SCOPE.tsv")
    crossings = read("THREE_HUNDRED_FIRST_19_LINE_CROSSINGS.tsv")
    crossing_counts = Counter(row["crossing_type"] for row in crossings)
    checks = {
        "events_381": len(events) == 381,
        "source_tokens_380": len({row["source_token_id"] for row in events}) == 380,
        "fields_135": len(fields) == 135,
        "fields_90_45": sum(row["field_status"] == "COMMITTED_FIELD" for row in fields) == 90 and sum(row["field_status"] == "OPEN_FIELD" for row in fields) == 45,
        "statements_116": len(statements) == 116,
        "statements_90_26": sum(row["statement_status"] == "COMMITTED_STATEMENT" for row in statements) == 90 and sum(row["statement_status"] == "OPEN_STATEMENT" for row in statements) == 26,
        "crossings_19_in_18": len(crossings) == 19 and sum(int(row["internal_line_crossings"]) > 0 for row in statements) == 18,
        "crossing_types": crossing_counts == Counter({"ORDINARY_CONTINUATION_ACROSS_PHYSICAL_LINE": 14, "VISIBLE_OWNER_RESET_INSIDE_RUNNING_STATEMENT": 4, "READ_ONCE_ANTICIPATION_OR_CARRY": 1}),
        "dy_split": sum(row["surface_end_class"] == "VISIBLE_DY_END" and row["terminal_status"] == "TERMINAL" for row in events) == 89 and sum(row["surface_end_class"] == "VISIBLE_DY_END" and row["terminal_status"] == "NONCLOSE" for row in events) == 16,
        "other_terminal_talam": [row["visible_surface"] for row in events if row["surface_end_class"] == "OTHER_VISIBLE_END" and row["terminal_status"] == "TERMINAL"] == ["talam"],
        "all_terminal_field_final": all(row["field_boundary_after"] == "YES" for row in events if row["terminal_status"] == "TERMINAL"),
        "no_sealed_page": not any("f" + "84" in path.read_text(encoding="utf-8").lower() for path in [HERE / "THREE_HUNDRED_FIRST_381_EVENT_SCOPE.tsv", HERE / "THREE_HUNDRED_FIRST_SCOPE_MANUAL.md", HERE / "THREE_HUNDRED_FIRST_REPORT.md"]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "failed": [key for key, value in checks.items() if not value]}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
