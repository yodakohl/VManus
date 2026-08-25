#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SEVENTY_FIFTH"
FORBIDDEN = {"UNKNOWN", "OPAQUE", "EXEMPLAR", "UNNAMED", "PLACEHOLDER", "LOCAL_CORE"}


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_seventy_fifth.py")], check=True)
    marks = read(f"{PREFIX}_95_MARK_SECOND_COMPLETE_ORDER.tsv")
    units = read(f"{PREFIX}_37_UNIT_SECOND_COMPLETE_ORDER.tsv")
    calibrations = read(f"{PREFIX}_6_REUSED_CALIBRATIONS.tsv")
    payloads = read(f"{PREFIX}_5_FILLED_PAYLOADS.tsv")
    comparison = read(f"{PREFIX}_TWO_ORDER_COMPARISON.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    stage_counts = Counter(row["stage"] for row in marks)
    checks = {
        "marks": len(marks) == 95 and stage_counts == {"MAKE_B.X2": 8, "APPLY_B3": 86, "CONDITION_C2@f67r2.15": 1},
        "mark_ids": [row["mark_id"] for row in marks] == [f"S{index:03d}" for index in range(1, 96)],
        "defaults": all(row["concrete_default_de"] for row in marks) and not any(term in row["concrete_default_de"].upper() for row in marks for term in FORBIDDEN),
        "units": len(units) == 37 and sum(int(row["marks"]) for row in units) == 95 and all(row["calibration_changed"] == "NO" for row in units),
        "calibrations": len(calibrations) == 6,
        "payloads": len(payloads) == 5 and all(row["empty"] == "NO" for row in payloads),
        "condition": marks[-1]["surface"] == "dolchsody" and marks[-1]["component_recipe"] == "D_ADDR+OL+CH+S_ADDR+O+DY",
        "comparison": len(comparison) == 6 and next(row for row in comparison if row["measure"] == "CALIBRATION_CHANGES")["second_order"] == "0",
        "no_changes": summary["calibration_changes"] == 0 and summary["dictionary_changes"] == 0 and summary["empty_payloads"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"] and not any("f84" in " ".join(row.values()).lower() for row in marks + units + calibrations + payloads + comparison),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
