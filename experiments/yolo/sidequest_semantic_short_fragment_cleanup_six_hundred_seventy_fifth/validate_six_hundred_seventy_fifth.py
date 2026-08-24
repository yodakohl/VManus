#!/usr/bin/env python3
"""Validate the final short-fragment cleanup."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_polished_long_statements_six_hundred_seventy_fourth/SIX_HUNDRED_SEVENTY_FOURTH_116_POLISHED_STATEMENTS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    source = {row["statement_id"]: row for row in read(SOURCE)}
    output = read(HERE / "SIX_HUNDRED_SEVENTY_FIFTH_116_CLEAN_STATEMENTS.tsv")
    repairs = read(HERE / "SIX_HUNDRED_SEVENTY_FIFTH_20_FRAGMENT_REPAIRS.tsv")
    records = read(HERE / "SIX_HUNDRED_SEVENTY_FIFTH_11_CLEAN_RECORDS.tsv")
    nominal = re.compile(r"(?:^|; dann )(?:zur Zielstelle|nach Sollmass|aus dem Vorrat|den Ansatz|die Zutat|als Portion|den laufenden Posten)(?:\.|;)")
    checks = {
        "one_hundred_sixteen_statements": len(output) == 116,
        "three_hundred_eighty_one_events": sum(int(row["events"]) for row in output) == 381,
        "eleven_records": len(records) == 11 and sum(int(row["events"]) for row in records) == 381,
        "twenty_fragment_repairs": len(repairs) == 20 and len({row["statement_id"] for row in repairs}) == 20,
        "source_sequences_unchanged": all(row["card_sequence"] == source[row["statement_id"]]["card_sequence"] and row["component_sequence"] == source[row["statement_id"]]["component_sequence"] and row["event_phrases_de"] == source[row["statement_id"]]["event_phrases_de"] for row in output),
        "all_begin_uppercase": all(row["fluent_workshop_reading_de"] and row["fluent_workshop_reading_de"][0].isupper() for row in output),
        "all_end_period": all(row["fluent_workshop_reading_de"].endswith(".") for row in output),
        "no_double_after": not any("; dann danach" in row["fluent_workshop_reading_de"] for row in output),
        "no_known_word_order_break": not any(any(term in row["fluent_workshop_reading_de"] for term in ["dann ihn die ", "dann den laufenden Posten die ", "dann danach ihn", "dann danach zur"]) for row in output),
        "no_detected_nominal_fragment": not any(nominal.search(row["fluent_workshop_reading_de"]) for row in output),
        "all_three_reading_sources": {row["reading_source"] for row in output} == {"HAND_POLISHED_LONG_V2", "HAND_POLISHED_FRAGMENT_V3", "NORMALIZED_SHORT_V3"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SEVENTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
