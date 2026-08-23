#!/usr/bin/env python3
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    coverage = rows("HUNDRED_SEVENTEENTH_116_MINIMAL_DECK_COVERAGE.tsv")
    records = rows("HUNDRED_SEVENTEENTH_ELEVEN_RECORD_COVERAGE.tsv")
    exercises = rows("HUNDRED_SEVENTEENTH_TWELVE_MINIMAL_DECK_EXERCISES.tsv")
    checks = {
        "statements_116": len(coverage) == 116,
        "records_11": len(records) == 11,
        "exercises_12": len(exercises) == 12,
        "full_3": sum(r["coverage_status"] == "FULLY_WRITABLE_WITH_17" for r in coverage) == 3,
        "partial_54": sum(r["coverage_status"] == "PORTABLE_SKELETON_ONLY" for r in coverage) == 54,
        "none_59": sum(r["coverage_status"] == "NO_PORTABLE_CARD" for r in coverage) == 59,
        "events_136_of_381": sum(int(r["portable_card_count"]) for r in coverage) == 136 and sum(int(r["total_card_count"]) for r in coverage) == 381,
        "all_exercises_deck_only": all(r["uses_only_17_card_deck"] == "YES" for r in exercises),
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in coverage),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
