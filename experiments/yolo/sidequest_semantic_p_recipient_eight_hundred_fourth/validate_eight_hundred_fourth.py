#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fourth.py")], check=True)
    events = read("EIGHT_HUNDRED_FOURTH_3_P_EVENTS.tsv")
    candidates = read("EIGHT_HUNDRED_FOURTH_4_P_CANDIDATES.tsv")
    statements = read("EIGHT_HUNDRED_FOURTH_3_REVISED_STATEMENTS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_FOURTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "three_events_cards_statements": len(events) == 3 and len({row["surface"] for row in events}) == 3 and len(statements) == 3,
        "three_recipes_complete": {row["component_recipe"] for row in events} == {"P+Y", "P+CHD+DY", "P+CHD+AL"},
        "four_candidates_one_selected": len(candidates) == 4 and sum(row["decision"] == "SELECT" for row in candidates) == 1,
        "einfuellen_selected": next(row for row in candidates if row["decision"] == "SELECT")["candidate"] == "EINFUELLEN",
        "all_events_same_value": all(row["selected_value"] == "EINFUELLEN" for row in events),
        "all_states_concrete": all(row["input_state"] and row["output_state"] for row in events),
        "all_statements_revised": all(row["old_reading_de"] != row["revised_reading_de"] for row in statements),
        "core21_strip10": summary["new_core_size"] == 21 and summary["remaining_recurrent_strip_values"] == 10,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
