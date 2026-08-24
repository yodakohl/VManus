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
    alignment = read("THREE_HUNDRED_EIGHTIETH_14_POSITION_STEM_ALIGNMENT.tsv")
    cores = read("THREE_HUNDRED_EIGHTIETH_EIGHT_PRODUCTIVE_CORES.tsv")
    fixed = read("THREE_HUNDRED_EIGHTIETH_SIX_FIXED_CARDS.tsv")
    predictions = read("THREE_HUNDRED_EIGHTIETH_REMAINING_WRAPPER_PREDICTIONS.tsv")
    checks = {
        "14_positions": len(alignment) == 14,
        "eight_cores": len(cores) == 8 and {r["core"] for r in cores} == {"HO", "OR", "CTHY", "Y", "AIIN", "CKHY", "OKY", "OKEEY"},
        "six_fixed": len(fixed) == 6,
        "partition_complete": sum(r["status"] == "PRODUCTIVE_WRAPPER_PARADIGM" for r in alignment) == 8 and sum(r["status"] == "FIXED_CARD" for r in alignment) == 6,
        "six_predictions": len(predictions) == 6,
        "predictions_registered": all(r["licensed_by_registered_palette"] == "YES" for r in predictions),
        "predicted_surfaces_expected": {r["predicted_surface"] for r in predictions} == {"or", "chy", "dy", "shy", "aiin", "daiin"},
        "values_nonempty": all(r["core_value_de"] and r["predicted_value_de"] for r in cores),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_EIGHTIETH_VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS": raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
