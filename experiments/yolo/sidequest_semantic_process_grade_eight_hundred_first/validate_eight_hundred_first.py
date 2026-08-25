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
    subprocess.run(["python", str(HERE / "build_eight_hundred_first.py")], check=True)
    cards = read("EIGHT_HUNDRED_FIRST_12_PROCESS_CARDS.tsv")
    decisions = read("EIGHT_HUNDRED_FIRST_4_PROCESS_DECISIONS.tsv")
    grid = read("EIGHT_HUNDRED_FIRST_CHK_GRADE_GRID.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_FIRST_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_component = {row["component"]: row for row in decisions}
    checks = {
        "twelve_cards_twenty_eight_events": len(cards) == 12 and sum(int(row["events"]) for row in cards) == 28,
        "four_meaning_invariant_components": len(decisions) == 4 and all(row["meaning_invariant"] == "YES" for row in decisions),
        "no_shared_cross_target_tail": all(row["shared_tail_with_other_target"] == "NO" for row in decisions),
        "only_chk_promoted": by_component["CHK"]["decision"] == "PROMOTE_TO_PARADIGM_CORE19" and all(by_component[x]["decision"] == "RETAIN_RECURRENT_RULE_STRIP" for x in ("SHED", "P", "LSH")),
        "chk_four_cards_seven_events": by_component["CHK"]["exact_cards"] == "4" and by_component["CHK"]["events"] == "7",
        "chk_grid_six_cells": len(grid) == 6,
        "chk_grid_three_attested_three_predicted": sum(int(row["events"]) > 0 for row in grid) == 3 and sum(int(row["events"]) == 0 for row in grid) == 3,
        "predictions_have_no_collision": all(row["surface_collision"] == "NO" for row in grid if int(row["events"]) == 0),
        "core19_strip12": summary["new_core_size"] == 19 and summary["remaining_recurrent_strip_values"] == 12,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
