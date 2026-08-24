#!/usr/bin/env python3
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
    targets = read("FOUR_HUNDRED_SIXTH_30_TARGET_OCCURRENCES.tsv")
    models = read("FOUR_HUNDRED_SIXTH_FOUR_TRIPLE_MODELS.tsv")
    contexts = read("FOUR_HUNDRED_SIXTH_FOUR_CONTEXT_READINGS.tsv")
    counts = Counter(row["family"] for row in targets)
    checks = {
        "thirty_occurrences": len(targets) == 30,
        "family_counts": counts == {"AIIN": 20, "CTH+Y": 7, "SHED+AL": 2, "SHECTHY": 1},
        "four_exact_cards": len({row["joint_tuple_id"] for row in targets}) == 4,
        "aiin_value_invariant": {row["selected_small_value_de"] for row in targets if row["family"] == "AIIN"} == {"Sollmaß"},
        "shedal_two_records": {row["record"] for row in targets if row["family"] == "SHED+AL"} == {"B3", "B5"},
        "shecthy_singleton": sum(row["family"] == "SHECTHY" for row in targets) == 1,
        "four_models": len(models) == 4,
        "one_selected": sum(row["decision"] == "SELECTED" for row in models) == 1,
        "selected_has_highest_score": max(models, key=lambda row: int(row["score"]))["decision"] == "SELECTED",
        "four_contexts": len(contexts) == 4,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "FOUR_HUNDRED_SIXTH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
