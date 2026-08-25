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
    attested = read("SEVEN_HUNDRED_NINETY_FOURTH_6_ATTESTED_MULTI_AXIS_CARDS.tsv")
    neighbors = read("SEVEN_HUNDRED_NINETY_FOURTH_6_LICENSED_NEIGHBORS.tsv")
    readbacks = read("SEVEN_HUNDRED_NINETY_FOURTH_12_READBACKS.tsv")
    axes = read("SEVEN_HUNDRED_NINETY_FOURTH_4_AXIS_COMBINATIONS.tsv")
    rules = read("SEVEN_HUNDRED_NINETY_FOURTH_5_COMPILER_RULES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_NINETY_FOURTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_6_6_12_4_5": (len(attested), len(neighbors), len(readbacks), len(axes), len(rules)) == (6, 6, 12, 4, 5),
        "axis_counts_5_1_0_0": {row["axis_combination"]: int(row["attested_events"]) for row in axes} == {"GRADE+ADDRESS": 5, "GRADE+QUANTITY": 1, "QUANTITY+ADDRESS": 0, "GRADE+QUANTITY+ADDRESS": 0},
        "five_address_one_quantity_neighbors": sum(row["changed_axis"] == "ADDRESS" for row in neighbors) == 5 and sum(row["changed_axis"] == "QUANTITY" for row in neighbors) == 1,
        "axis_count_preserved": all(row["axis_count_preserved"] == "YES" and row["axes_before"] == row["axes_after"] for row in neighbors),
        "readback12": all(row["readback"] == "PASS" for row in readbacks),
        "provenance_split6_6": sum(row["provenance"] == "ATTESTED" for row in readbacks) == 6 and sum(row["provenance"] == "WORKSHOP_PREDICTION" for row in readbacks) == 6,
        "no_free_insertion": all(row["compiler_action"] == "do not invent" for row in axes if row["axis_combination"] in {"QUANTITY+ADDRESS", "GRADE+QUANTITY+ADDRESS"}),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for rows in (attested, neighbors, readbacks, axes, rules) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["decision"] == "SIX_ONE_AXIS_NEIGHBORS__NO_FREE_AXIS_INSERTION",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_NINETY_FOURTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
