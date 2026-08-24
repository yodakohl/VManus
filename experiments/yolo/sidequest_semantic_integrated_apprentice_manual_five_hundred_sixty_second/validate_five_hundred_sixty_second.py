#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    manual = read("FIVE_HUNDRED_SIXTY_SECOND_TWENTY_TWO_RULE_APPRENTICE_MANUAL.tsv")
    inventory = read("FIVE_HUNDRED_SIXTY_SECOND_TRAINING_INVENTORY.tsv")
    traces = read("FIVE_HUNDRED_SIXTY_SECOND_THREE_HUNDRED_EIGHTY_ONE_FULL_TRACES.tsv")
    records = read("FIVE_HUNDRED_SIXTY_SECOND_ELEVEN_RECORD_EXAMS.tsv")
    checks = {
        "manual22": len(manual) == 22 and len({row["rule_no"] for row in manual}) == 22,
        "six_lessons": len({row["lesson"] for row in manual}) == 6,
        "inventory8": len(inventory) == 8,
        "traces381": len(traces) == 381 and len({row["event_id"] for row in traces}) == 381,
        "statements116": len({row["statement_id"] for row in traces}) == 116,
        "records11": len(records) == 11 and len({row["record"] for row in records}) == 11,
        "card_roundtrip381": all(row["card_roundtrip"] == "YES" and row["predicted_card_no"] == row["observed_card_no"] for row in traces),
        "surface_roundtrip381": all(row["surface_roundtrip"] == "YES" and row["predicted_surface"] == row["observed_surface"] for row in traces),
        "record_exams": all(row["card_roundtrip"] == "YES" and row["surface_roundtrip"] == "YES" for row in records),
        "complete_values": all(row["atomic_card_value_de"].strip() and row["containing_clause_de"].strip() for row in traces),
        "no_free_choice": all(row["free_choice"] == "NO" for row in traces),
        "fixed_pages": {row["page"] for row in traces} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in traces),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_SIXTY_SECOND_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name, value in checks.items():
        print(f"{name}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
