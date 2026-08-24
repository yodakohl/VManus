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
    events = read("FOUR_HUNDRED_TWENTY_SECOND_H4_18_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_TWENTY_SECOND_H4_FOUR_STATEMENTS.tsv")
    comparison = read("FOUR_HUNDRED_TWENTY_SECOND_H4_H5_LAYER_COMPARISON.tsv")
    models = read("FOUR_HUNDRED_TWENTY_SECOND_THREE_H4_H5_MODELS.tsv")
    correction = read("FOUR_HUNDRED_TWENTY_SECOND_SCOPE_CORRECTION.tsv")
    checks = {
        "eighteen_events": len(events) == 18,
        "exact_event_range": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(56, 74)],
        "every_value_nonempty": all(row["selected_small_value_de"].strip() for row in events),
        "four_statements": len(statements) == 4,
        "statement_ids": [row["statement_id"] for row in statements] == [f"H4-S{i:03d}" for i in range(1, 5)],
        "six_layer_comparisons": len(comparison) == 6,
        "three_models": len(models) == 3,
        "common_layer_selected": [row["model"] for row in models if row["decision"] == "SELECT"] == ["GENERAL_PLANT_PREPARATION_COMMON_LAYER"],
        "one_scope_correction": len(correction) == 1 and "H3" in correction[0]["correct_inventory"],
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (events, statements, comparison, models, correction) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_TWENTY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
