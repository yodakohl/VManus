#!/usr/bin/env python3
"""Validate Pass 741 apprentice recoding."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cues = read("SEVEN_HUNDRED_FORTY_FIRST_39_FLUENT_CUES.tsv")
    audit = read("SEVEN_HUNDRED_FORTY_FIRST_116_RECODING_AUDIT.tsv")
    confusion = read("SEVEN_HUNDRED_FORTY_FIRST_11_TEMPLATE_CONFUSIONS.tsv")
    order = read("SEVEN_HUNDRED_FORTY_FIRST_27_ORDER_MISMATCHES.tsv")
    errors = read("SEVEN_HUNDRED_FORTY_FIRST_23_COMPONENT_ERRORS.tsv")
    recovery = read("SEVEN_HUNDRED_FORTY_FIRST_39_COMPONENT_RECOVERY.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FORTY_FIRST_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    missing = Counter()
    extra = Counter()
    for row in audit:
        if row["missing_components"] != "NONE":
            missing.update(row["missing_components"].split("+"))
        if row["extra_components"] != "NONE":
            extra.update(row["extra_components"].split("+"))
    checks = {
        "inventory_39_116_11_27_23_39": (len(cues), len(audit), len(confusion), len(order), len(errors), len(recovery)) == (39, 116, 11, 27, 23, 39),
        "all_generation_inputs_clean_only": all(row["generation_input_contract"] == "OWNER_PLUS_CLEAN_INSTRUCTION_ONLY" for row in audit),
        "exact_sets_93": sum(row["exact_component_set"] == "YES" for row in audit) == 93,
        "template_hits_89": sum(row["template_match"] == "YES" for row in audit) == 89,
        "mismatch_split_25_2": sum(row["repair_class"] == "LEARN_OPERATION_HEAD_PACKING" for row in order) == 25 and sum(row["repair_class"] == "KEEP_CONTEXTUAL_ELLIPSIS" for row in order) == 2,
        "missing_components_exact": missing == {"O": 2, "OS": 1, "Y": 1, "T": 1, "AIN": 1, "OT": 1},
        "extra_components_exact": extra == {"SH": 11, "OT": 5, "OL": 3, "OR": 1, "CTH": 1},
        "all_recall_at_least_point7": all(float(row["component_set_recall"]) >= 0.7 for row in audit),
        "means_exact": summary["mean_component_set_recall"] == 0.994458 and summary["mean_component_set_precision"] == 0.976697,
        "all_ids_unique": len({row["statement_id"] for row in audit}) == 116,
        "fixed_pages_only": {row["page"] for row in audit} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in [cues, audit, confusion, order, errors, recovery] for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FORTY_FIRST_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
