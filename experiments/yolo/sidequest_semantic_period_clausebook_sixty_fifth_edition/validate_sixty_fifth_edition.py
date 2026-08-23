#!/usr/bin/env python3
"""Validate period clausebook coverage."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    templates = read_tsv("SIXTY_FIFTH_36_PERIOD_CLAUSE_TEMPLATES.tsv")
    clauses = read_tsv("SIXTY_FIFTH_381_PERIOD_SOURCE_CLAUSES.tsv")
    rules = read_tsv("SIXTY_FIFTH_12_COMPOSITION_RULES.tsv")
    per_shape_styles = Counter(row["shape_id"] for row in templates)
    checks = {
        "thirty_six_templates": len(templates) == 36,
        "twelve_shapes_three_styles_each": len(per_shape_styles) == 12 and set(per_shape_styles.values()) == {3},
        "three_styles": {row["source_style"] for row in templates} == {"WORKSHOP_VERNACULAR", "LATIN_FORMULARY", "TABULAR_NOTATION"},
        "no_language_identification": all(row["language_identification"] == "NONE" for row in templates),
        "381_source_clauses": len(clauses) == 381,
        "group_ids_unique": len({row["source_group_id"] for row in clauses}) == 381,
        "three_renderings_nonempty": all(row["workshop_vernacular_clause"] and row["latin_formulary_clause"] and row["tabular_notation_clause"] for row in clauses),
        "twelve_rules": len(rules) == 12 and len({row["shape_id"] for row in rules}) == 12,
        "all_shapes_populated": all(int(row["group_count"]) > 0 for row in rules),
        "allowed_pages_only": {row["page"] for row in clauses} <= ALLOWED,
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in templates + clauses + rules),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
