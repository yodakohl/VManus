#!/usr/bin/env python3
"""Validate Pass 705 fillable forms."""

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
    forms = read("SEVEN_HUNDRED_FIFTH_5_FILLABLE_FORMS.tsv")
    practice = read("SEVEN_HUNDRED_FIFTH_15_FRESH_PRACTICE_STATEMENTS.tsv")
    counts = Counter(row["domain"] for row in practice)
    per_form = Counter(row["form_id"] for row in practice)
    checks = {
        "forms_5": len(forms) == 5,
        "form_templates_unique": len({row["role_template"] for row in forms}) == 5,
        "practice_15": len(practice) == 15,
        "three_domains_five_each": counts == {"HERBAL": 5, "BIOLOGICAL": 5, "APPARATUS": 5},
        "three_fillings_per_form": all(per_form[f"F0{i}"] == 3 for i in range(1, 6)),
        "all_templates_attested": all(int(row["role_template_support"]) >= 1 for row in practice),
        "two_cards_each": all(len(row["selected_card_sequence"].split("|")) == 2 for row in practice),
        "surface_two_atoms_each": all(len(row["practice_surface_sequence"].split()) == 2 for row in practice),
        "all_backreadings": all(bool(row["literal_backreading_de"]) for row in practice),
        "no_new_cards": all(row["new_card"] == "NO" for row in practice),
        "no_new_surfaces": all(row["new_surface"] == "NO" for row in practice),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_FIFTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
