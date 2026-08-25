#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_EIGHTY_THIRD"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_eighty_third.py")], check=True)
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    events = read(f"{PREFIX}_381_EVENT_COMPLETE_FIFTH_HAND.tsv")
    statements = read(f"{PREFIX}_116_COMPLETE_PHRASE_FIRST_STATEMENTS.tsv")
    phrases = read(f"{PREFIX}_14_COMPLETE_RECURRENT_PHRASES.tsv")
    occurrences = read(f"{PREFIX}_34_COMPLETE_PHRASE_OCCURRENCES.tsv")
    restored = read(f"{PREFIX}_9_RESTORED_STATEMENTS.tsv")
    records = read(f"{PREFIX}_11_CONTINUOUS_RECORDS.tsv")
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "events_381": len(events) == 381 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)],
        "statements_116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "records_11": len(records) == 11 and sum(int(row["statements"]) for row in records) == 116 and sum(int(row["events"]) for row in records) == 381,
        "herbal_100_bio_281": summary["herbal_events"] == 100 and summary["biological_events"] == 281,
        "restored_9_47": len(restored) == 9 and sum(int(row["events"]) for row in restored) == 47,
        "phrases_14": len(phrases) == 14,
        "phrases_12_plus_2": sum(row["card_length"] == "2" for row in phrases) == 12 and sum(row["card_length"] == "3" for row in phrases) == 2,
        "no_long_phrase": all(int(row["card_length"]) <= 3 for row in phrases),
        "occurrences_34": len(occurrences) == 34,
        "y_aiin_y_present": any(row["component_sequence"] == "Y | AIIN | Y" for row in phrases),
        "all_events_read": all(row["concrete_default_de"] and row["phrase_ready_card_de"] for row in events),
        "all_statements_read": all(row["phrase_first_reading_de"] and row["fluent_workshop_reading_de"] for row in statements),
        "identities_173": summary["identities"] == 173,
        "no_new_card_meanings": summary["new_card_meanings"] == 0,
        "fixed_pages": summary["fixed_pages"] == ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"],
        "sealed": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
