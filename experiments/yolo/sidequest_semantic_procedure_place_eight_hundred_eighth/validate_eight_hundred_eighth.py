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
    subprocess.run(["python", str(HERE / "build_eight_hundred_eighth.py")], check=True)
    cards = read("EIGHT_HUNDRED_EIGHTH_25_PROCEDURE_PLACE_CARDS.tsv")
    events = read("EIGHT_HUNDRED_EIGHTH_28_PROCEDURE_PLACE_EVENTS.tsv")
    decisions = read("EIGHT_HUNDRED_EIGHTH_3_ROOT_DECISIONS.tsv")
    grid = read("EIGHT_HUNDRED_EIGHTH_8_SOLK_GRID.tsv")
    stacks = read("EIGHT_HUNDRED_EIGHTH_O_IIN_STACK.tsv")
    readings = read("EIGHT_HUNDRED_EIGHTH_5_READABLE_STATEMENTS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_EIGHTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_root = {row["component"]: row for row in decisions}
    checks = {
        "twenty_five_cards_twenty_eight_union_events": len(cards) == 25 and len(events) == 28,
        "component_counts_o19_iin4_solk7": (by_root["O"]["events"], by_root["IIN"]["events"], by_root["SOLK"]["events"]) == ("19", "4", "7"),
        "component_event_sum30": summary["component_event_sum"] == 30,
        "all_three_promoted_with_scope_guard": all(row["decision"] == "PROMOTE_TO_PARADIGM_CORE28" and row["scope_guard"].startswith("only registered") for row in decisions),
        "one_o_iin_stack_two_events": len(stacks) == 1 and stacks[0]["component_recipe"] == "O+IIN" and stacks[0]["events"] == "2",
        "solk_grid_four_attested_four_predicted": len(grid) == 8 and summary["solk_attested_cells"] == 4 and summary["solk_predicted_cells"] == 4,
        "solk_predictions_no_collision": summary["prediction_collisions"] == 0,
        "five_readable_statements": len(readings) == 5,
        "core28_strip3": summary["new_core_size"] == 28 and summary["remaining_recurrent_strip_values"] == 3,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_EIGHTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
