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
    events = read("SEVEN_HUNDRED_NINETY_SEVENTH_82_TRANSFER_EVENTS.tsv")
    ops = read("SEVEN_HUNDRED_NINETY_SEVENTH_3_OPERATIONS.tsv")
    families = read("SEVEN_HUNDRED_NINETY_SEVENTH_7_SHARED_OPERATION_FAMILIES.tsv")
    shared = read("SEVEN_HUNDRED_NINETY_SEVENTH_33_SHARED_OPERATION_EVENTS.tsv")
    stacked = read("SEVEN_HUNDRED_NINETY_SEVENTH_3_STACKED_OPERATION_TYPES.tsv")
    predictions = read("SEVEN_HUNDRED_NINETY_SEVENTH_6_PREDICTED_OPERATIONS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_NINETY_SEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_82_3_7_33_3_6": (len(events), len(ops), len(families), len(shared), len(stacked), len(predictions)) == (82, 3, 7, 33, 3, 6),
        "operation_counts_21_27_48": {row["operation"]: int(row["events"]) for row in ops} == {"K": 21, "L": 27, "CHD": 48},
        "cards51_recipes47": len({row["exact_card_id"] for row in events}) == 51 and len({row["component_recipe"] for row in events}) == 47,
        "all_meanings_present": all(row["all_operation_meanings_present"] == "YES" for row in events),
        "op_y_complete": next(row for row in families if row["operation_signature"] == "OP+Y")["status"] == "THREE_OPERATION_COMPLETE",
        "stack_counts_1_12_1": {row["operation_stack"]: int(row["events"]) for row in stacked} == {"K+CHD": 1, "L+CHD": 12, "L+K": 1},
        "predictions_unseen": all(row["fixed_page_collision"] == "NO" for row in predictions),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for rows in (events, ops, families, shared, stacked, predictions) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["decision"] == "K_ADD_L_GUIDE_CHD_TRANSFER_FORM_DISTINCT_STACKABLE_OPERATIONS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_NINETY_SEVENTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
