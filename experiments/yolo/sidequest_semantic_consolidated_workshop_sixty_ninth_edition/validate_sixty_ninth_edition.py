#!/usr/bin/env python3
"""Validate the current consolidated ten-page workshop edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    ledger = read_tsv("SIXTY_NINTH_776_CURRENT_GROUP_LEDGER.tsv")
    units = read_tsv("SIXTY_NINTH_14_CURRENT_UNITS.tsv")
    dictionary = read_tsv("SIXTY_NINTH_89_CURRENT_DICTIONARY_LAYERS.tsv")
    rules = read_tsv("SIXTY_NINTH_32_RULE_WORKSHOP_MANUAL.tsv")
    counts = Counter(row["register"] for row in ledger)
    checks = {
        "ten_pages": {row["page"] for row in ledger} == ALLOWED,
        "776_groups": len(ledger) == 776 and [int(row["unified_serial"]) for row in ledger] == list(range(1, 777)),
        "register_counts": counts == Counter({"HERBAL_PROSE": 100, "BIOLOGICAL_PROSE": 281, "ASTRO_LOCAL_LOOKUP": 395}),
        "fourteen_units": len(units) == 14 and {row["unit_id"] for row in units} == {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3"},
        "unit_group_counts": sum(int(row["group_count"]) for row in units) == 776,
        "eighty_nine_dictionary_entries": len(dictionary) == 89,
        "thirty_two_rules": len(rules) == 32 and [int(row["teaching_order"]) for row in rules] == list(range(1, 33)),
        "all_units_readable": all(row["compact_current_reading_de"] and row["concrete_content_wager"] and row["strongest_rival"] for row in units),
        "sealed_pages_absent": all("f84" not in "\t".join(row.values()).lower() for row in ledger + units + dictionary + rules),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
