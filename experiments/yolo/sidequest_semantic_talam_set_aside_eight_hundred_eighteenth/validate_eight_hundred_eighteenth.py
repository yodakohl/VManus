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
    subprocess.run(["python", str(HERE / "build_eight_hundred_eighteenth.py")], check=True)
    candidates = read("EIGHT_HUNDRED_EIGHTEENTH_7_TALAM_CANDIDATES.tsv")
    events = read("EIGHT_HUNDRED_EIGHTEENTH_TALAM_EVENT.tsv")
    statements = read("EIGHT_HUNDRED_EIGHTEENTH_REVISED_STATEMENT.tsv")
    segments = read("EIGHT_HUNDRED_EIGHTEENTH_3_SEGMENTATION_TESTS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_EIGHTEENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "one_talam_event": len(events) == 1 and events[0]["event_id"] == "E063" and events[0]["surface"] == "talam",
        "selected_beiseitestellen": events[0]["selected_reading_de"] == "BEISEITESTELLEN",
        "statement_revised": len(statements) == 1 and "beiseitestellen" in statements[0]["revised_reading_de"] and "verwahren" not in statements[0]["revised_reading_de"],
        "seven_candidates": len(candidates) == 7 and sum(row["decision"] == "SELECT_WHOLE_OPERATION" for row in candidates) == 1,
        "unlicensed_am_split_rejected": len(segments) == 3 and all(row["decision"] == "REJECT" for row in segments if row["missing_piece"] == "AM"),
        "whole_analysis_selected": next(row for row in segments if row["analysis"] == "WHOLE_TALAM")["decision"] == "SELECT",
        "architecture_unchanged": summary["core_size"] == 33 and summary["bound_components"] == 3 and summary["whole_forms"] == 3,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_EIGHTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
