#!/usr/bin/env python3
"""Validate selected-source semantic invariance across the four scribe copies."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    copies = read_tsv("SEVENTY_NINTH_464_SELECTED_SOURCE_SCRIBE_READINGS.tsv")
    statements = read_tsv("SEVENTY_NINTH_116_FOUR_HAND_MEANING_INVARIANCE.tsv")
    profiles = read_tsv("SEVENTY_NINTH_4_SCRIBE_PROFILES_RETAINED.tsv")
    counts = Counter(row["scribe_id"] for row in copies)
    checks = {
        "four_profiles": len(profiles) == 4 and len({row["scribe_id"] for row in profiles}) == 4,
        "464_copies": len(copies) == 464,
        "116_per_scribe": set(counts.values()) == {116},
        "116_statements": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "four_copies_per_statement": all(row["scribe_copies"] == "4" for row in statements),
        "tuple_identity_invariant": all(row["distinct_tuple_sequences"] == "1" for row in statements),
        "minimal_reading_invariant": all(row["distinct_minimal_readings"] == "1" for row in statements),
        "source_vocabulary_invariant": all(row["distinct_selected_vocabularies"] == "1" for row in statements),
        "controlled_reading_invariant": all(row["distinct_controlled_unit_readings"] == "1" for row in statements),
        "meaning_flags": all(row["meaning_invariant"] == "YES" for row in statements),
        "no_semantic_change_by_profile": all(row["selected_source_semantic_changes"] == "0" for row in profiles),
        # Exact tuple hashes may coincidentally contain the hexadecimal substring
        # "f84"; the seal concerns page selectors, not hash text.
        "sealed_pages_absent": all(not row["page"].lower().startswith("f84") for row in copies + statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
