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
    trace = read("FOUR_HUNDRED_SEVENTH_NINE_EVENT_B5_TRACE.tsv")
    comparison = read("FOUR_HUNDRED_SEVENTH_B3_B5_STATION_COMPARISON.tsv")
    endings = read("FOUR_HUNDRED_SEVENTH_THREE_ENDING_MODELS.tsv")
    checks = {
        "nine_events": len(trace) == 9,
        "exact_events": [row["event_id"] for row in trace] == [f"E{n:03d}" for n in range(364, 373)],
        "three_loci": {row["locus"] for row in trace} == {"f83r.47", "f83r.48", "f83r.49"},
        "owner_constant": {row["owner"] for row in trace} == {"B5_LEFT_OPEN_FRINGE_STATION"},
        "shedal_first": trace[0]["surface"] == "shedal",
        "second_opening_before_nonterminal_work": [row["operation"] for row in trace[-2:]] == ["SELECT_SECOND_OPENING", "WORK_THROUGH"],
        "five_comparisons": len(comparison) == 5,
        "b5_not_terminal": next(row for row in comparison if row["feature"] == "END")["b5_s003"].startswith("DAIIIN+CHEDY remains open"),
        "three_ending_models": len(endings) == 3,
        "one_selected": sum(row["decision"] == "SELECTED" for row in endings) == 1,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "FOUR_HUNDRED_SEVENTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
