#!/usr/bin/env python3
"""Validate the hand-polished long statement edition."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P673 = ROOT / "experiments/yolo/sidequest_semantic_fluent_workshop_edition_six_hundred_seventy_third/SIX_HUNDRED_SEVENTY_THIRD_116_FLUENT_STATEMENTS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    source = {row["statement_id"]: row for row in read(P673)}
    output = read(HERE / "SIX_HUNDRED_SEVENTY_FOURTH_116_POLISHED_STATEMENTS.tsv")
    repairs = read(HERE / "SIX_HUNDRED_SEVENTY_FOURTH_25_POLISH_REPAIRS.tsv")
    records = read(HERE / "SIX_HUNDRED_SEVENTY_FOURTH_11_POLISHED_RECORDS.tsv")
    checks = {
        "one_hundred_sixteen_statements": len(output) == 116 and len({row["statement_id"] for row in output}) == 116,
        "three_hundred_eighty_one_events": sum(int(row["events"]) for row in output) == 381,
        "eleven_records": len(records) == 11 and sum(int(row["events"]) for row in records) == 381,
        "twenty_five_repairs": len(repairs) == 25 and len({row["statement_id"] for row in repairs}) == 25,
        "all_prior_nonclean_repaired": {sid for sid, row in source.items() if row["fluency_grade"] != "CLEAN"} == {row["statement_id"] for row in repairs},
        "card_sequences_unchanged": all(row["card_sequence"] == source[row["statement_id"]]["card_sequence"] for row in output),
        "component_sequences_unchanged": all(row["component_sequence"] == source[row["statement_id"]]["component_sequence"] for row in output),
        "event_phrases_unchanged": all(row["event_phrases_de"] == source[row["statement_id"]]["event_phrases_de"] for row in output),
        "all_repairs_marked": all(row["card_sequence_unchanged"] == "YES" and row["component_sequence_unchanged"] == "YES" for row in repairs),
        "zero_dense_workable": not any(row["fluency_grade"] in {"DENSE", "WORKABLE"} for row in output),
        "all_readings_end": all(row["fluent_workshop_reading_de"].endswith(".") for row in output),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SIX_HUNDRED_SEVENTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, passed in checks.items():
        print(f"{name}\t{'PASS' if passed else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
