#!/usr/bin/env python3
"""Consistency checker for the human dictionary."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    dictionary = read("THIRTY_FIFTH_487_SURFACE_TEACHING_DICTIONARY.tsv")
    deck = read("THIRTY_FIFTH_56_TEACHING_ENTRIES.tsv")
    burden = read("THIRTY_FIFTH_TEACHING_BURDEN.tsv")
    checks = {
        "surface_dictionary_487": len(dictionary) == 487,
        "surface_ids_unique": len({r["surface_id"] for r in dictionary}) == 487,
        "visible_groups_776": sum(int(r["observed_groups"]) for r in dictionary) == 776,
        "teaching_deck_56": len(deck) == 56,
        "teaching_symbols_unique": len({r["symbol"] for r in deck}) == 56,
        "seven_burden_classes": len(burden) == 7,
        "burden_surfaces_487": sum(int(r["surface_type_count"]) for r in burden) == 487,
        "burden_groups_776": sum(int(r["visible_group_count"]) for r in burden) == 776,
        "values_nonempty": all(r["short_spoken_value_de"] for r in dictionary),
        "examples_nonempty": all(r["example_group"] and r["example_value_de"] for r in dictionary),
        "human_dictionary": (OUT / "THIRTY_FIFTH_COMPLETE_HUMAN_DICTIONARY.md").exists(),
        "report": (OUT / "THIRTY_FIFTH_EDITION_REPORT.md").exists(),
        "sealed_absent": not any("f84" in path.name.lower() for path in OUT.iterdir()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
