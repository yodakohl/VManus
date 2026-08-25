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
    subprocess.run(["python", str(HERE / "build_eight_hundred_eleventh.py")], check=True)
    candidates = read("EIGHT_HUNDRED_ELEVENTH_4_CFH_CANDIDATES.tsv")
    events = read("EIGHT_HUNDRED_ELEVENTH_CFH_EVENT.tsv")
    statements = read("EIGHT_HUNDRED_ELEVENTH_REVISED_STATEMENT.tsv")
    grid = read("EIGHT_HUNDRED_ELEVENTH_8_CFH_GRID.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_ELEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "one_event_statement": len(events) == 1 and len(statements) == 1 and events[0]["event_id"] == "E041",
        "four_candidates_press_selected": len(candidates) == 4 and next(row for row in candidates if row["decision"] == "SELECT")["candidate"] == "AUSPRESSEN",
        "statement_revised": statements[0]["old_reading_de"] != statements[0]["revised_reading_de"] and "auspressen" in statements[0]["revised_reading_de"],
        "eight_grid_cells_one_observed": len(grid) == 8 and sum(row["events"] != "0" for row in grid) == 1,
        "seven_predictions_no_collision": sum(row["events"] == "0" for row in grid) == 7 and summary["prediction_collisions"] == 0,
        "core32_three_singletons": summary["new_core_size"] == 32 and summary["remaining_local_singletons"] == 3,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_ELEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
