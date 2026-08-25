#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_EIGHTY_SIXTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_eighty_sixth.py")], check=True)
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    marks = read(f"{PREFIX}_437_MARK_REVISED_SIX_ORDER_BOOK.tsv")
    units = read(f"{PREFIX}_118_UNIT_REVISED_SIX_ORDER_BOOK.tsv")
    orders = read(f"{PREFIX}_6_REVISED_COMPLETE_ORDERS.tsv")
    payloads = read(f"{PREFIX}_30_FILLED_PAYLOADS.tsv")
    calibrations = read(f"{PREFIX}_6_UNCHANGED_CALIBRATIONS.tsv")
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "orders_6": len(orders) == 6,
        "marks_437": len(marks) == 437 and len({row["order_mark_id"] for row in marks}) == 437,
        "stage_83_281_73": summary["stage_counts"] == {"PREP": 83, "APP": 281, "COND": 73},
        "units_118": len(units) == 118,
        "order_totals": [int(row["total_marks"]) for row in orders] == [118, 80, 101, 94, 19, 25],
        "bio_once": summary["biological_events_covered_once"] == 281,
        "prep_unique_62": summary["unique_preparation_events"] == 62,
        "conditions_6": summary["condition_loci"] == 6,
        "supplies": [row["revised_product"] for row in orders] == ["A.G2", "B.X4", "A.G2", "C.W2", "B.X1", "D.P1"],
        "changes_4": summary["supply_changes"] == 4,
        "payloads_30": len(payloads) == 30 and all(row["empty"] == "NO" for row in payloads),
        "calibrations_6": len(calibrations) == 6,
        "all_defaults": all(row["concrete_default_de"] for row in marks),
        "dictionary_fixed": all(row["dictionary_changed"] == "NO" for row in units) and summary["dictionary_changes"] == 0,
        "ten_pages": summary["fixed_pages_used"] == 10,
        "sealed": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
