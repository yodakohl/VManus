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
    names = ["TWO_HUNDRED_TWENTIETH_33_SUBSTITUTION_TESTS.tsv", "TWO_HUNDRED_TWENTIETH_ELEVEN_REVISED_ENTRIES.tsv", "TWO_HUNDRED_TWENTIETH_THREE_OWNER_PHRASEBOOK.md", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    tests = read("TWO_HUNDRED_TWENTIETH_33_SUBSTITUTION_TESTS.tsv")
    entries = read("TWO_HUNDRED_TWENTIETH_ELEVEN_REVISED_ENTRIES.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    phrasebook = (OUT / "TWO_HUNDRED_TWENTIETH_THREE_OWNER_PHRASEBOOK.md").read_text(encoding="utf-8")
    counts = Counter(row["entry_key"] for row in tests)
    revised = {row["entry_key"]: row["selected_headword_de"] for row in entries if row["decision"] == "REVISE"}
    checks = {
        "11_entries": len(entries) == 11 and len({row["entry_key"] for row in entries}) == 11,
        "33_tests": len(tests) == 33 and all(count == 3 for count in counts.values()),
        "three_owners_each": all({row["owner_register"] for row in tests if row["entry_key"] == key} == {"PLANT", "BIO", "ASTRO"} for key in counts),
        "scores_bounded": all(0 <= int(row["current_naturalness_0_3"]) <= 3 and 0 <= int(row["alternate_naturalness_0_3"]) <= 3 for row in tests),
        "exact_two_revisions": revised == {"DY": "SCHLUSS", "RESULT": "ERGEBNIS"},
        "nine_kept": sum(row["decision"] == "KEEP" for row in entries) == 9,
        "revisions_improve": all(int(row["alternate_three_owner_score"]) > int(row["current_three_owner_score"]) for row in entries if row["decision"] == "REVISE"),
        "all_entries_readable": all(f"## {row['entry_key']}:" in phrasebook for row in entries),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in phrasebook.lower() and not any("f84" in value.lower() for table in (tests, entries) for row in table for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_twentieth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
