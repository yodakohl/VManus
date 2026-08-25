#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_EIGHTY_FIFTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_eighty_fifth.py")], check=True)
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    stock = read(f"{PREFIX}_10_STOCK_PROCESS_PROFILES.tsv")
    demands = read(f"{PREFIX}_6_APPLICATION_DEMAND_PROFILES.tsv")
    matrix = read(f"{PREFIX}_60_STOCK_APPLICATION_MATRIX.tsv")
    selected = read(f"{PREFIX}_6_SELECTED_SUPPLIES.tsv")
    orders = read(f"{PREFIX}_6_REVISED_ORDER_HEADERS.tsv")
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "stock_10": len(stock) == 10 and len({row["product_handle"] for row in stock}) == 10,
        "demands_6": len(demands) == 6,
        "matrix_60": len(matrix) == 60 and len({(row["biological_record"], row["product_handle"]) for row in matrix}) == 60,
        "one_winner_each": all(sum(row["biological_record"] == record and row["selected"] == "YES" for row in matrix) == 1 for record in {row["biological_record"] for row in demands}),
        "selected_6": len(selected) == 6 and len(orders) == 6,
        "mapping": summary["selected_mapping"] == {"B1": "A.G2", "B2": "B.X4", "B3": "A.G2", "B4": "C.W2", "B5": "B.X1", "B6": "D.P1"},
        "four_changes": sum(row["supply_changed"] == "YES" for row in selected) == 4,
        "two_keeps": sum(row["supply_changed"] == "NO" for row in selected) == 2,
        "all_selected_ready": all(row["selected_supply"] in {stock_row["product_handle"] for stock_row in stock} for row in selected),
        "all_profiles_concrete": all(row["feature_set"] and row["feature_counts"] for row in stock) and all(row["weighted_demand"] for row in demands),
        "no_dictionary_change": summary["dictionary_changes"] == 0 and summary["new_card_meanings"] == 0,
        "sealed": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
