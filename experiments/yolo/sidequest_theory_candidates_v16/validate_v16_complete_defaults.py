#!/usr/bin/env python3
"""Validate the four independent V16 complete default-reading ledgers."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r",
         "f67r2", "f68r1", "f69v"}
PROSE = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ASTRO = {"f67r2", "f68r1", "f69v"}
EVASIVE = {"", "unknown", "opaque", "untranslated", "content", "payload",
           "item", "value", "state", "unassigned"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def domain(row: dict[str, str]) -> str:
    value = row.get("domain", "").upper()
    if value in {"PROSE", "ASTRO"}:
        return value
    return "PROSE" if row["page"] in PROSE else "ASTRO"


def validate_candidate(number: int) -> dict[str, object]:
    path = ROOT / f"V16_R{number}_COMPLETE_TRANSLATION_LEDGER.tsv"
    rows = read(path)
    assert len(rows) == 776, (number, len(rows))
    assert {row["page"] for row in rows} == PAGES
    prose = [row for row in rows if domain(row) == "PROSE"]
    astro = [row for row in rows if domain(row) == "ASTRO"]
    assert len(prose) == 381, (number, len(prose))
    assert len(astro) == 395, (number, len(astro))
    assert len({row["exact_tuple_id"] for row in prose}) == 173
    glosses = [row["default_English"].strip() for row in rows]
    assert all(gloss and gloss.lower() not in EVASIVE for gloss in glosses)
    assert not any(row["page"].lower().startswith("f84") for row in rows)
    by_tuple: dict[str, set[str]] = {}
    for row in prose:
        by_tuple.setdefault(row["exact_tuple_id"], set()).add(row["default_English"])
    assert all(len(values) == 1 for values in by_tuple.values())
    return {
        "candidate": f"R{number}",
        "ledger": path.name,
        "events": len(rows),
        "prose_events": len(prose),
        "astro_groups": len(astro),
        "exact_prose_cards": len(by_tuple),
        "blank_or_evasive_glosses": 0,
        "f84_rows": 0,
    }


def main() -> None:
    candidates = [validate_candidate(number) for number in range(1, 5)]
    result = {
        "schema": "SIDEQUEST_V16_COMPLETE_DEFAULT_VALIDATION_V1",
        "status": "PASS",
        "candidates": candidates,
        "selected_candidate": "R4",
        "selected_events": 776,
        "selected_prose_events": 381,
        "selected_astro_groups": 395,
        "selected_exact_prose_cards": 173,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
        "claim_ceiling": "Complete speculative defaults, not a decipherment claim.",
    }
    output = ROOT / "V16_VALIDATION.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
