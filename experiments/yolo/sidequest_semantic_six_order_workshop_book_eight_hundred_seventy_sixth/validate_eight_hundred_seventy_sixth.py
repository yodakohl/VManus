#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SEVENTY_SIXTH"
FORBIDDEN = {"UNKNOWN", "OPAQUE", "EXEMPLAR", "UNNAMED", "PLACEHOLDER", "LOCAL_CORE"}


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_seventy_sixth.py")], check=True)
    marks = read(f"{PREFIX}_438_MARK_SIX_ORDER_BOOK.tsv")
    units = read(f"{PREFIX}_119_UNIT_SIX_ORDER_BOOK.tsv")
    orders = read(f"{PREFIX}_6_COMPLETE_ORDER_SUMMARY.tsv")
    payloads = read(f"{PREFIX}_30_FILLED_PAYLOADS.tsv")
    calibrations = read(f"{PREFIX}_6_SHARED_CALIBRATIONS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    stage_counts = Counter("PREP" if row["stage"].startswith("MAKE") else "APP" if row["stage"].startswith("APPLY") else "COND" for row in marks)
    checks = {
        "six_orders": len(orders) == 6 and {row["order_id"] for row in orders} == {"WH01", "WH02", "WH03", "WH04", "WH05", "WH06"},
        "marks": len(marks) == 438 and stage_counts == {"PREP": 84, "APP": 281, "COND": 73},
        "units": len(units) == 119 and sum(int(row["marks"]) for row in units) == 438,
        "order_totals": {row["order_id"]: int(row["total_marks"]) for row in orders} == {"WH01": 118, "WH02": 76, "WH03": 95, "WH04": 94, "WH05": 25, "WH06": 30},
        "bio_once": len({row["source_id"] for row in marks if row["stage"].startswith("APPLY")}) == 281 and sum(row["stage"].startswith("APPLY") for row in marks) == 281,
        "ten_pages": {row["page"] for row in marks} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "condition_loci": {row["condition_handle"] for row in orders} == {"C1@f67r2.1", "C2@f67r2.15", "C3@f68r1.9", "C4@f69v.12", "C5@f69v.2", "C6@f69v.3"},
        "defaults": all(row["concrete_default_de"] for row in marks) and not any(term in row["concrete_default_de"].upper() for row in marks for term in FORBIDDEN),
        "payloads": len(payloads) == 30 and all(row["empty"] == "NO" for row in payloads) and all(Counter(row["order_id"] for row in payloads)[order] == 5 for order in {"WH01", "WH02", "WH03", "WH04", "WH05", "WH06"}),
        "calibrations": len(calibrations) == 6 and all(row["calibration_changed"] == "NO" for row in units),
        "no_changes": summary["calibration_changes"] == 0 and summary["dictionary_changes"] == 0 and summary["marks_without_default"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"] and not any("f84" in " ".join(row.values()).lower() for row in marks + units + orders + payloads + calibrations),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
