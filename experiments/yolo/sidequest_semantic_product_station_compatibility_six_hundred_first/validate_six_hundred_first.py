#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    products = read("SIX_HUNDRED_FIRST_FIVE_PRODUCT_CLASSES.tsv")
    stations = read("SIX_HUNDRED_FIRST_SIXTEEN_STATION_CLASSES.tsv")
    matrix = read("SIX_HUNDRED_FIRST_EIGHTY_PRODUCT_STATION_COMPATIBILITIES.tsv")
    strongest = read("SIX_HUNDRED_FIRST_FIVE_STRONGEST_COMPATIBILITY_SETS.tsv")
    checks = {
        "products5": len(products) == 5 and len({row["product_id"] for row in products}) == 5,
        "stations16": len(stations) == 16 and len({row["station_id"] for row in stations}) == 16,
        "matrix80": len(matrix) == 80 and len({(row["product_id"], row["station_id"]) for row in matrix}) == 80,
        "all_products_direct": all(any(row["product_id"] == product["product_id"] and row["compatibility"] == "DIRECT_WORKING_MATCH" for row in matrix) for product in products),
        "all_stations_evidenced": all(int(row["statements"]) > 0 and row["observed_operations_de"] for row in stations),
        "no_pointer": all(row["written_cross_pointer"] == "NO" for row in matrix),
        "strongest5": len(strongest) == 5 and all(row["one_to_one_claim"] == "NO" for row in strongest),
        "local_stations": all(row["global_flow_claim"] == "NONE__LOCAL_STATION_ONLY" for row in stations),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
