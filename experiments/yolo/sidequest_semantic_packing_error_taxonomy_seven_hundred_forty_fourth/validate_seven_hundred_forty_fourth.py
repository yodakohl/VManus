#!/usr/bin/env python3
"""Validate Pass 744 packing-error taxonomy."""

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
    taxonomy = read("SEVEN_HUNDRED_FORTY_FOURTH_42_ERROR_TAXONOMY.tsv")
    components = read("SEVEN_HUNDRED_FORTY_FOURTH_18_MISSING_COPY_COMPONENTS.tsv")
    priorities = read("SEVEN_HUNDRED_FORTY_FOURTH_6_REPAIR_PRIORITIES.tsv")
    segmentation = read("SEVEN_HUNDRED_FORTY_FOURTH_3_TRUE_SEGMENTATION_CASES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_FORTY_FOURTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    classes = Counter(row["error_class"] for row in taxonomy)
    missing = Counter()
    extra = Counter()
    for row in taxonomy:
        if row["missing_occurrences"] != "NONE":
            missing.update(row["missing_occurrences"].split("+"))
        if row["extra_occurrences"] != "NONE":
            extra.update(row["extra_occurrences"].split("+"))
    checks = {
        "inventory_42_18_6_3": (len(taxonomy), len(components), len(priorities), len(segmentation)) == (42, 18, 6, 3),
        "class_counts_exact": classes == {"Y_COPY_ONLY": 20, "Y_PLUS_OTHER_COPY": 10, "NON_Y_COPY": 5, "SEMANTIC_SET_GAP": 3, "TRUE_SEGMENTATION": 3, "EXTRA_HELPER_OR_MIXED": 1},
        "missing_104_y60": sum(missing.values()) == 104 and missing["Y"] == 60,
        "next_missing_exact": {key: missing[key] for key in ["OL", "AL", "AIIN", "OK"]} == {"OL": 6, "AL": 5, "AIIN": 4, "OK": 4},
        "only_extra_ol": extra == {"OL": 1},
        "true_segmentation_ids": {row["statement_id"] for row in segmentation} == {"B1-S006", "B1-S015", "B3-S030"},
        "register_totals": sum(int(row["herbal_statements"]) for row in priorities) == 15 and sum(int(row["biological_statements"]) for row in priorities) == 27,
        "all_statement_ids_unique": len({row["statement_id"] for row in taxonomy}) == 42,
        "fixed_pages_only": {row["page"] for row in taxonomy} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in [taxonomy, components, priorities, segmentation] for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FORTY_FOURTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
