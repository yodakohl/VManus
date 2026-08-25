#!/usr/bin/env python3
"""Validate the Pass 1021 repeated-core adjudication."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    source = read_tsv("REPEATED_CORE_OCCURRENCES.tsv")
    selected = read_tsv("PASS1021_ADJUDICATED_DOUBLING.tsv")
    rules = Counter(row["selected_doubling_rule"] for row in selected)
    cores = Counter(row["core"] for row in selected)
    checks = {
        "forty_source_occurrences": len(source) == 40,
        "forty_selected_occurrences": len(selected) == 40,
        "same_occurrence_ids": [r["duplicate_id"] for r in source] == [r["duplicate_id"] for r in selected],
        "twenty_eight_nested": rules["PACKAGE_SCOPE_DESCENT"] == 28,
        "twelve_free": rules["FREE_PLURAL_OR_REPEAT"] == 12,
        "core_counts": cores == Counter({"CH": 27, "OL": 5, "AR": 2, "AL": 2, "Y": 2, "OR": 1, "OK": 1}),
        "all_ch_nested": all(r["selected_doubling_rule"] == "PACKAGE_SCOPE_DESCENT" for r in selected if r["core"] == "CH"),
        "or_nested": all(r["selected_doubling_rule"] == "PACKAGE_SCOPE_DESCENT" for r in selected if r["core"] == "OR"),
        "other_cores_free": all(r["selected_doubling_rule"] == "FREE_PLURAL_OR_REPEAT" for r in selected if r["core"] not in {"CH", "OR"}),
        "one_f13_focus": sum(r["f13r_s009_focus"] == "YES" for r in selected) == 1,
        "sixteen_pages": len({r["physical_page"] for r in selected}) == 16,
        "all_four_registers": {r["register"] for r in selected} == {"HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"},
        "no_sealed_pages": all(not r["physical_page"].startswith("f84") for r in selected),
        "core_values_unchanged": {
            (r["core"], r["core_value_de"]) for r in selected
        } == {
            ("CH", "NEHMEN"), ("OL", "FORTSETZEN"), ("AR", "AUSGANG"),
            ("AL", "ZIELORT"), ("Y", "AKTIVER POSTEN"),
            ("OR", "EINHEIT"), ("OK", "SETZEN"),
        },
        "historical_note_present": (OUT / "HISTORICAL_DOUBLING_WORKSHOP_NOTE.md").is_file(),
        "revised_sheet_present": (OUT / "PASS1021_CURRENT_APPRENTICE_SHEET.md").is_file(),
        "revised_sheet_has_both_rules": all(
            marker in (OUT / "PASS1021_CURRENT_APPRENTICE_SHEET.md").read_text(encoding="utf-8")
            for marker in ("PAKETGRENZE", "FREI:", "mehrere X", "äußeres X")
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    result = {"status": "PASS" if not failures else "FAIL", "checks": checks, "failures": failures}
    (OUT / "PASS1021_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
