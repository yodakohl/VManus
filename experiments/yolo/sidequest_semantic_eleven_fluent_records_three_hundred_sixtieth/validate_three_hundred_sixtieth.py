#!/usr/bin/env python3
"""Validate eleven fluent record readings and owner noun separation."""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    records = read_tsv("THREE_HUNDRED_SIXTIETH_ELEVEN_FLUENT_RECORDS.tsv")
    owners = read_tsv("THREE_HUNDRED_SIXTIETH_TWENTY_ONE_OWNER_NOUNS.tsv")
    checks = {
        "eleven_records": len(records) == 11 and [row["record_unit_id"] for row in records] == ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"],
        "116_statements": sum(int(row["statements"]) for row in records) == 116,
        "381_visible_events": sum(int(row["visible_events"]) for row in records) == 381,
        "380_source_cards": sum(int(row["source_cards"]) for row in records) == 380,
        "57_physical_lines": sum(int(row["physical_lines"]) for row in records) == 57,
        "twenty_one_owner_entries": len(owners) == 21 and len({row["owner_id_or_phrase"] for row in owners}) == 21,
        "all_owner_nouns_nonempty": all(row["concrete_nouns_supplied_de"] and row["information_source"] for row in owners),
        "owner_not_card_claim": all(row["card_word_claim"] == "NO__OWNER_SUPPLIES_REFERENT_NOT_CARD_VALUE" for row in owners),
        "all_records_fluent_literal_owner_layers": all(row["fluent_german_record"] and row["visible_surface_sequence"] and row["literal_source_value_sequence_de"] and row["picture_or_owner_supplied_nouns_de"] for row in records),
        "fixed_pages_only": {row["page"] for row in records} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "no_raw_bio_owner_tokens_in_fluent": all("B1_" not in row["fluent_german_record"] and "B2_" not in row["fluent_german_record"] and "B3_" not in row["fluent_german_record"] and "B4_" not in row["fluent_german_record"] for row in records),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_SIXTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
