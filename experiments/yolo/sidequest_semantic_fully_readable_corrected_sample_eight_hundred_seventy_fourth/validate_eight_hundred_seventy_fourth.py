#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SEVENTY_FOURTH"
FORBIDDEN = {"UNKNOWN", "OPAQUE", "EXEMPLAR", "UNNAMED", "PLACEHOLDER", "LOCAL_CORE"}


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_seventy_fourth.py")], check=True)
    marks = read(f"{PREFIX}_76_MARK_FULLY_READABLE_SAMPLE.tsv")
    units = read(f"{PREFIX}_25_UNIT_FULLY_READABLE_SAMPLE.tsv")
    calibrations = read(f"{PREFIX}_6_EXPLICIT_CALIBRATIONS.tsv")
    payloads = read(f"{PREFIX}_5_FILLED_PAYLOADS.tsv")
    correction = read(f"{PREFIX}_PASS869_CORRECTION.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    stage_counts = Counter(row["stage"] for row in marks)
    checks = {
        "corrected_76_marks": len(marks) == 76 and stage_counts == {"MAKE_D.P1": 13, "APPLY_B2": 62, "CONDITION_C4@f69v.12": 1},
        "mark_ids": [row["mark_id"] for row in marks] == [f"R{index:03d}" for index in range(1, 77)],
        "all_defaults": all(row["concrete_default_de"] for row in marks) and not any(term in row["concrete_default_de"].upper() for row in marks for term in FORBIDDEN),
        "units": len(units) == 25 and all(row["all_marks_have_concrete_default"] == "YES" for row in units) and sum(int(row["marks"]) for row in units) == 76,
        "calibrations": len(calibrations) == 6 and all(row["source"] in {"WORKSHOP_CONVENTION", "PICTURE_PLUS_WORKSHOP_CONVENTION"} for row in calibrations),
        "payloads": len(payloads) == 5 and all(row["empty"] == "NO" and row["concrete_sample_value"] for row in payloads),
        "correction": len(correction) == 4 and {row["item"] for row in correction} == {"HERBAL_SAMPLE_SCOPE", "TOTAL_SAMPLE_MARKS", "PRODUCT_IDENTITY", "MISSING_PAYLOADS"},
        "specific_condition": marks[-1]["surface"] == "otody" and marks[-1]["concrete_default_de"] == "DEN FOLGENDEN LOKALEN BEDINGUNGSEINTRAG WAEHLEN UND SCHLIESSEN",
        "summary": summary["empty_payloads"] == 0 and summary["marks_without_default"] == 0 and summary["supersedes_pass_869_sample_mark_count"] is True,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"] and not any("f84" in " ".join(row.values()).lower() for row in marks + units + calibrations + payloads + correction),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
