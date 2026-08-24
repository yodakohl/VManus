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
    occ = read("FOUR_HUNDRED_TWENTIETH_THIRTEEN_OKY_OKCHY_OCCURRENCES.tsv")
    rules = read("FOUR_HUNDRED_TWENTIETH_TWO_CARD_RULES.tsv")
    models = read("FOUR_HUNDRED_TWENTIETH_FOUR_DISTINCTION_MODELS.tsv")
    passages = read("FOUR_HUNDRED_TWENTIETH_FIVE_REVISED_PASSAGES.tsv")
    checks = {
        "thirteen_occurrences": len(occ) == 13,
        "oky_ten": sum(row["family"] == "OKY" for row in occ) == 10,
        "okchy_three": sum(row["family"] == "OKCHY" for row in occ) == 3,
        "two_exact_cards": len({row["joint_tuple_id"] for row in occ}) == 2,
        "oky_value_invariant": {row["selected_card_value_de"] for row in occ if row["family"] == "OKY"} == {"verwende dies"},
        "okchy_value_invariant": {row["selected_card_value_de"] for row in occ if row["family"] == "OKCHY"} == {"nimm dies"},
        "three_okchy_new": all(row["referent_class"].startswith("NEW_") or row["referent_class"].startswith("TAKE_") for row in occ if row["family"] == "OKCHY"),
        "two_rules": len(rules) == 2,
        "four_models": len(models) == 4,
        "take_use_selected": [row["model"] for row in models if row["decision"] == "SELECT"] == ["TAKE_VERSUS_USE"],
        "five_passages": len(passages) == 5,
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (occ, rules, models, passages) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_TWENTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
