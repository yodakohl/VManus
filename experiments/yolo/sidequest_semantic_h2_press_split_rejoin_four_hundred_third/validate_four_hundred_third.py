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
    critical = read("FOUR_HUNDRED_THIRD_TEN_CRITICAL_EVENTS.tsv")
    pairs = read("FOUR_HUNDRED_THIRD_TWO_PARALLEL_PAIRS.tsv")
    models = read("FOUR_HUNDRED_THIRD_FOUR_SPLIT_MODELS.tsv")
    edges = read("FOUR_HUNDRED_THIRD_EIGHT_FLOW_EDGES.tsv")
    checks = {
        "ten_critical_events": len(critical) == 10,
        "two_parallel_pairs": len(pairs) == 2,
        "pair_events_exact": {row["events"] for row in pairs} == {"E020|E021", "E033|E034"},
        "both_pairs_collapse_to_y": all("Y" in row["following_collapse"] for row in pairs),
        "four_models": len(models) == 4,
        "one_selected_model": sum(row["decision"] == "SELECTED" for row in models) == 1,
        "eight_edges": len(edges) == 8,
        "two_press_outputs": sum(row["relation"].startswith("PRESS_OUTPUT") for row in edges) == 2,
        "two_or_inputs": sum(row["relation"].startswith("OR_SLOT") for row in edges) == 2,
        "all_readings_concrete": all(row["working_reading_de"] for row in critical),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "FOUR_HUNDRED_THIRD_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
