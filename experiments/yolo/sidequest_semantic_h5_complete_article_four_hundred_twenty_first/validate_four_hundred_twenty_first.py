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
    events = read("FOUR_HUNDRED_TWENTY_FIRST_H5_27_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_TWENTY_FIRST_H5_SIX_STATEMENTS.tsv")
    learned = read("FOUR_HUNDRED_TWENTY_FIRST_TEN_H5_WHOLE_WORDS.tsv")
    models = read("FOUR_HUNDRED_TWENTY_FIRST_THREE_H5_MODELS.tsv")
    checks = {
        "twenty_seven_events": len(events) == 27,
        "event_range": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(74, 101)],
        "every_value_nonempty": all(row["selected_small_value_de"].strip() for row in events),
        "six_statements": len(statements) == 6,
        "statement_ids": [row["statement_id"] for row in statements] == [f"H5-S{i:03d}" for i in range(1, 7)],
        "ten_whole_words": len(learned) == 10,
        "dry_cough_removed": all("Husten" not in value and "cough" not in value.lower() for rows in (events, statements, learned) for row in rows for value in row.values()),
        "three_models": len(models) == 3,
        "one_selected": [row["model"] for row in models if row["decision"] == "SELECT"] == ["PLANT_PREPARATION_AND_APPLICATION"],
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (events, statements, learned, models) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_TWENTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
