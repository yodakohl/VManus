#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    names = ["TWO_HUNDRED_NINETEENTH_ELEVEN_PORTABLE_DICTIONARY_ENTRIES.tsv", "TWO_HUNDRED_NINETEENTH_182_PORTABLE_OCCURRENCES.tsv", "TWO_HUNDRED_NINETEENTH_READABLE_PORTABLE_DICTIONARY.md", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    entries = read("TWO_HUNDRED_NINETEENTH_ELEVEN_PORTABLE_DICTIONARY_ENTRIES.tsv")
    occurrences = read("TWO_HUNDRED_NINETEENTH_182_PORTABLE_OCCURRENCES.tsv")
    readable = (OUT / "TWO_HUNDRED_NINETEENTH_READABLE_PORTABLE_DICTIONARY.md").read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    expected = ["OK", "OL", "OT", "AR", "AL", "AIIN", "Y", "DY", "OR", "CHED~CHD", "RESULT"]
    checks = {
        "eleven_entries": [row["entry_key"] for row in entries] == expected,
        "182_unique_occurrences": len(occurrences) == 182 and len({row["unified_serial"] for row in occurrences}) == 182,
        "116_plus_66": summary["prose_occurrences"] == 116 and summary["astro_occurrences"] == 66,
        "every_occurrence_assigned": all(row["dictionary_entries"] for row in occurrences),
        "every_entry_cross_register": all(int(row["prose_membership_occurrences"]) > 0 and int(row["astro_membership_occurrences"]) > 0 for row in entries),
        "result_is_whole_card": next(row for row in entries if row["entry_key"] == "RESULT")["normalized_card_ids"] == "MC119",
        "ey_not_free_entry": not any(row["entry_key"] == "EY" for row in entries),
        "all_readable_entries": all(f"## {entry}" in readable for entry in expected),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in readable.lower() and not any("f84" in value.lower() for table in (entries, occurrences) for row in table for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_nineteenth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
