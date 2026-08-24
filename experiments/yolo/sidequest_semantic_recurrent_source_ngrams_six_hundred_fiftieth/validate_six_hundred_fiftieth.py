#!/usr/bin/env python3
"""Validate the recurrent exact-card source grammar."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    grammar = read("SIX_HUNDRED_FIFTIETH_RECURRENT_SOURCE_GRAMMAR.tsv")
    instances = read("SIX_HUNDRED_FIFTIETH_RECURRENT_NGRAM_INSTANCES.tsv")
    statements = read("SIX_HUNDRED_FIFTIETH_116_STATEMENT_SOURCE_GRAMMAR.tsv")
    summary = read("SIX_HUNDRED_FIFTIETH_2_NGRAM_SUMMARY.tsv")
    expected_bigram_instances = sum(max(int(row["event_count"]) - 1, 0) for row in statements)
    expected_trigram_instances = sum(max(int(row["event_count"]) - 2, 0) for row in statements)
    checks = {
        "one_hundred_sixteen_statements": len(statements) == 116,
        "three_hundred_eighty_one_events": sum(int(row["event_count"]) for row in statements) == 381,
        "two_summary_rows": len(summary) == 2 and {row["n"] for row in summary} == {"2", "3"},
        "bigram_instance_accounting": int(next(row["source_instances"] for row in summary if row["n"] == "2")) == expected_bigram_instances,
        "trigram_instance_accounting": int(next(row["source_instances"] for row in summary if row["n"] == "3")) == expected_trigram_instances,
        "all_grammar_recurrent": all(int(row["occurrences"]) >= 2 for row in grammar),
        "all_source_only": all(row["source_only"] == "YES" for row in grammar),
        "instance_binding": len(instances) == sum(int(row["occurrences"]) for row in grammar),
        "portable_requires_two_records": all((row["construction_status"] == "PORTABLE_SOURCE_CONSTRUCTION") == (int(row["records"]) >= 2) for row in grammar),
        "local_status_consistent": all(row["construction_status"] in {"PORTABLE_SOURCE_CONSTRUCTION", "RECORD_LOCAL_RECURRENT_CONSTRUCTION", "WITHIN_STATEMENT_REPETITION"} for row in grammar),
        "only_bigrams_trigrams": all(row["n"] in {"2", "3"} for row in grammar + instances),
        "statement_links_consistent": all((row["recurrent_source_constructions"] != "NONE") == (int(row["recurrent_bigram_instances"]) + int(row["recurrent_trigram_instances"]) > 0) for row in statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_FIFTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
