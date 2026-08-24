#!/usr/bin/env python3
"""Validate the atomic Bio dictionary and statement separation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    dictionary = read("THREE_HUNDRED_FOURTEENTH_124_ATOMIC_BIO_DICTIONARY.tsv")
    events = read("THREE_HUNDRED_FOURTEENTH_281_ATOMIC_EVENT_READINGS.tsv")
    statements = read("THREE_HUNDRED_FOURTEENTH_97_ATOMIC_STATEMENT_READINGS.tsv")
    duplicates = read("THREE_HUNDRED_FOURTEENTH_LOCAL_ALLOGRAPH_PAIR.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "cards_124": len(dictionary) == summary["cards"] == 124,
        "events_281": len(events) == summary["events"] == 281,
        "statements_97": len(statements) == summary["statements"] == 97,
        "overrides_28": summary["multiword_glosses_replaced"] == 28,
        "atomic_glosses_114": len({row["atomic_gloss_de"] for row in dictionary}) == summary["distinct_atomic_glosses"] == 114,
        "atomic_scope_keys_123": len({row["atomic_plus_scope_key"] for row in dictionary}) == summary["distinct_atomic_scope_keys"] == 123,
        "one_duplicate_pair": len(duplicates) == summary["duplicate_atomic_scope_groups"] == 1,
        "no_multiword_dictionary_values": all(" " not in row["atomic_gloss_de"] for row in dictionary) and summary["sentence_sized_dictionary_glosses"] == 0,
        "all_events_roundtrip": all(row["reverse_identity_match"] == "YES" for row in events),
        "all_statements_roundtrip": all(row["roundtrip_match"] == "YES" for row in statements),
        "no_sealed_page": not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in events),
    }
    failed = [name for name, passed in checks.items() if not passed]
    result = {"status": "PASS" if not failed else "FAIL", "checks": checks, "failed": failed}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
