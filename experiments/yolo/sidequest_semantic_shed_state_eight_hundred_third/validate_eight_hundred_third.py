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
    subprocess.run(["python", str(HERE / "build_eight_hundred_third.py")], check=True)
    events = read("EIGHT_HUNDRED_THIRD_15_SHED_EVENTS.tsv")
    families = read("EIGHT_HUNDRED_THIRD_3_SHED_FAMILIES.tsv")
    statements = read("EIGHT_HUNDRED_THIRD_15_REVISED_STATEMENTS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_THIRD_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "fifteen_unique_events": len(events) == 15 and len({row["event_id"] for row in events}) == 15,
        "three_recipe_families": len(families) == 3 and {row["component_recipe"] for row in families} == {"SHED+DY", "R+SHED+DY", "SHED+AL"},
        "fifteen_affected_statements": len(statements) == 15,
        "thirteen_terminal_two_target": summary["terminal_events"] == 13 and summary["target_addressed_events"] == 2,
        "single_selected_core_value": all(row["selected_core_value"] == "STEHENLASSEN" for row in families),
        "no_result_state_selected": summary["result_state_selected"] == 0,
        "all_revised_sentences_changed": all(row["old_reading_de"] != row["revised_reading_de"] for row in statements),
        "core20_strip11": summary["new_core_size"] == 20 and summary["remaining_recurrent_strip_values"] == 11,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
