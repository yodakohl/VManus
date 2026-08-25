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
    subprocess.run(["python", str(HERE / "build_eight_hundred_second.py")], check=True)
    substitutions = read("EIGHT_HUNDRED_SECOND_3_CHK_SUBSTITUTIONS.tsv")
    traces = read("EIGHT_HUNDRED_SECOND_6_BEFORE_AFTER_TRACES.tsv")
    readbacks = read("EIGHT_HUNDRED_SECOND_3_FULL_READBACKS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_SECOND_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "three_substitutions": len(substitutions) == 3 and {row["target_recipe"] for row in substitutions} == {"CHK+E+DY", "CHK+EEE+Y", "CHK+EEE+DY"},
        "six_phase_traces": len(traces) == 6 and all(sum(row["prediction_id"] == pid for row in traces) == 2 for pid in {row["prediction_id"] for row in substitutions}),
        "three_full_readbacks": len(readbacks) == 3,
        "only_grade_changes": all(row["grade_change_only"] == "YES" and row["endpoint_preserved"] == "YES" and row["owner_preserved"] == "YES" and row["other_events_preserved"] == "YES" for row in substitutions),
        "four_surface_candidates_no_collisions": summary["unique_prediction_surfaces"] == 4 and summary["observed_surface_collisions"] == 0,
        "two_real_source_statements": summary["source_statements"] == ["B3-S002", "H4-S003"],
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
