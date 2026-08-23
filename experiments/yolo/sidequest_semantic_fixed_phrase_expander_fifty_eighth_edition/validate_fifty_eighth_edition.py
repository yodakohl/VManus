#!/usr/bin/env python3
"""Validate the fixed phrase expander."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    templates = rows("FIFTY_EIGHTH_10_EXPANSION_TEMPLATES.tsv")
    generated = rows("FIFTY_EIGHTH_116_FIXED_EXPANSIONS.tsv")
    coverage = rows("FIFTY_EIGHTH_20_PHRASE_COVERAGE.tsv")
    checks = {
        "ten_fixed_templates": len(templates) == 10 and len({row["template_id"] for row in templates}) == 10,
        "five_owner_classes_two_modes": len({(row["owner_class"], row["content_mode"]) for row in templates}) == 10,
        "all_116_statements": len(generated) == 116 and len({row["unit_id"] for row in generated}) == 116,
        "twenty_phrases": len(coverage) == 20,
        "every_phrase_use_regenerated": all(row["all_uses_regenerated"] == "YES" for row in coverage),
        "no_sentence_specific_insertions": all(row["sentence_specific_lexical_insertions"] == "0" for row in generated),
        "all_have_generated_prose": all(row["fixed_generated_prose_de"].strip() for row in generated),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for row in generated),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
