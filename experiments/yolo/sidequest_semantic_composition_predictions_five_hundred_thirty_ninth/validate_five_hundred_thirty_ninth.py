#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    address = read("FIVE_HUNDRED_THIRTY_NINTH_TWENTY_OPERATOR_ADDRESS_MATRIX.tsv")
    grade = read("FIVE_HUNDRED_THIRTY_NINTH_THIRTY_GRADE_ENDPOINT_MATRIX.tsv")
    predictions = read("FIVE_HUNDRED_THIRTY_NINTH_TWENTY_MISSING_COMPOSITION_PREDICTIONS.tsv")
    collisions = read("FIVE_HUNDRED_THIRTY_NINTH_PREDICTION_SURFACE_COLLISIONS.tsv")
    checks = {
        "address20": len(address) == 20,
        "address12_8": sum(row["status_on_ten_pages"] == "ATTESTED" for row in address) == 12 and sum(row["status_on_ten_pages"] == "PREDICTED_MISSING_CELL" for row in address) == 8,
        "grade30": len(grade) == 30,
        "grade18_12": sum(row["status_on_ten_pages"] == "ATTESTED" for row in grade) == 18 and sum(row["status_on_ten_pages"] == "PREDICTED_MISSING_CELL" for row in grade) == 12,
        "predictions20": len(predictions) == 20 and len({row["component_parse"] for row in predictions}) == 20,
        "all_predictions_unattested": all(row["claim_scope"] == "PREDICTED_COMPOSITION_NOT_OBSERVED_CARD" for row in predictions),
        "ranked_support": [int(row["support_score"]) for row in predictions] == sorted((int(row["support_score"]) for row in predictions), reverse=True),
        "no_empty_meanings": all(row["predicted_atomic_reading_de"] for row in predictions),
        "collision_ledger_present": bool(collisions),
        "no_sealed_tokens": all("f84" not in "\t".join(row.values()).lower() for row in [*address, *grade, *predictions]),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_THIRTY_NINTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
