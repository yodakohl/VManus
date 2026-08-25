#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_EIGHTY_FIRST"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_eighty_first.py")], check=True)
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    phrases = read(f"{PREFIX}_10_RECURRENT_PHRASES.tsv")
    occurrences = read(f"{PREFIX}_22_PHRASE_OCCURRENCES.tsv")
    statements = read(f"{PREFIX}_107_PHRASE_FIRST_STATEMENTS.tsv")
    checks = {
        "summary_pass": summary["status"] == "PASS",
        "physical_334": summary["physical_prose_events"] == 334,
        "statements_107": len(statements) == 107 and len({row["unit"] for row in statements}) == 107,
        "phrases_10": len(phrases) == 10,
        "nine_bigrams": sum(row["card_length"] == "2" for row in phrases) == 9,
        "one_trigram": sum(row["card_length"] == "3" for row in phrases) == 1,
        "no_longer": all(int(row["card_length"]) <= 3 for row in phrases),
        "occurrences_22": len(occurrences) == 22,
        "all_cross_page": all(len(row["pages"].split(",")) >= 2 for row in phrases),
        "all_concrete": all(row["working_phrase_de"] and row["workshop_use"] == "MEMORIZE_AS_ACTION_CHUNK" for row in phrases),
        "all_events_once_in_statements": sum(int(row["cards"]) for row in statements) == 334,
        "all_statements_read": all(row["phrase_first_segmentation_de"] and row["fluent_workshop_reading_de"] for row in statements),
        "no_new_card_meanings": summary["new_card_meanings"] == 0,
        "sealed": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
