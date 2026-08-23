#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    names = ["TWO_HUNDRED_TWENTY_SECOND_SIX_RECURRENT_PHRASES.tsv", "TWO_HUNDRED_TWENTY_SECOND_TWELVE_REAL_OCCURRENCES.tsv", "TWO_HUNDRED_TWENTY_SECOND_REAL_PHRASEBOOK.md", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    phrases = read("TWO_HUNDRED_TWENTY_SECOND_SIX_RECURRENT_PHRASES.tsv")
    occurrences = read("TWO_HUNDRED_TWENTY_SECOND_TWELVE_REAL_OCCURRENCES.tsv")
    readable = (OUT / "TWO_HUNDRED_TWENTY_SECOND_REAL_PHRASEBOOK.md").read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    counts = Counter(row["phrase_id"] for row in occurrences)
    checks = {
        "six_phrases": len(phrases) == 6 and [row["phrase_id"] for row in phrases] == [f"P0{i}" for i in range(1, 7)],
        "twelve_occurrences": len(occurrences) == 12 and all(counts[f"P0{i}"] == 2 for i in range(1, 7)),
        "all_cross_statement": all(int(row["distinct_statements"]) == 2 for row in phrases),
        "only_length_three_repeats": summary["recurrent_length_3"] == 6 and summary["recurrent_length_4"] == 0 and summary["recurrent_length_5"] == 0,
        "y_aiin_y_exact": all(row["card_value_window"] == "dies > Sollwert > dies" for row in occurrences if row["phrase_id"] == "P01"),
        "all_real_event_ids": all(row["window_start_event"].startswith("E") for row in occurrences),
        "lead_explained": "zwei bezeichnete Posten" in readable,
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in readable.lower() and not any("f84" in value.lower() for table in (phrases, occurrences) for row in table for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_twenty_second.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
