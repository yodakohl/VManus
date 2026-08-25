#!/usr/bin/env python3
"""Validate Pass 761 large-formula parameterization."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    tails = read("SEVEN_HUNDRED_SIXTY_FIRST_19_LOCAL_TAIL_STRIPS.tsv")
    layouts = read("SEVEN_HUNDRED_SIXTY_FIRST_7_PARAMETERIZED_LAYOUTS.tsv")
    families = read("SEVEN_HUNDRED_SIXTY_FIRST_3_FAMILY_PARAMETERS.tsv")
    cards = read("SEVEN_HUNDRED_SIXTY_FIRST_74_RECONSTRUCTED_CARDS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SIXTY_FIRST_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_19_7_3_74": (len(tails), len(layouts), len(families), len(cards)) == (19, 7, 3, 74),
        "all_layouts_exact": all(row["reconstruction_exact"] == "YES" for row in layouts),
        "layout_units_50": sum(int(row["layout_units"]) for row in layouts) == 50,
        "motif31_tail19": (sum(int(row["motif_tokens"]) for row in layouts), sum(int(row["tail_tokens"]) for row in layouts)) == (31, 19),
        "tails_hold_43_cards": sum(int(row["cards"]) for row in tails) == 43,
        "all_tails_unique": all(row["formula_uses"] == "1" for row in tails),
        "family_partition_3_1_3": sorted(int(row["statements"]) for row in families) == [1, 3, 3],
        "saved_24": summary["saved_learning_positions"] == 24,
        "fixed_pages_only": {row["page"] for row in layouts} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for rows in (tails, layouts, families, cards) for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SIXTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
