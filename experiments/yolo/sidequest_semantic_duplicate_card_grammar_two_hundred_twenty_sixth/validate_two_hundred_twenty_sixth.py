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
    names = ["TWO_HUNDRED_TWENTY_SIXTH_SIX_DUPLICATE_PAIRS.tsv", "TWO_HUNDRED_TWENTY_SIXTH_THREE_DUPLICATION_RULES.tsv", "TWO_HUNDRED_TWENTY_SIXTH_DUPLICATION_MANUAL.md", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    pairs = read("TWO_HUNDRED_TWENTY_SIXTH_SIX_DUPLICATE_PAIRS.tsv")
    rules = read("TWO_HUNDRED_TWENTY_SIXTH_THREE_DUPLICATION_RULES.tsv")
    manual = (OUT / "TWO_HUNDRED_TWENTY_SIXTH_DUPLICATION_MANUAL.md").read_text(encoding="utf-8")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    classes = Counter(row["boundary_class"] for row in pairs)
    checks = {
        "six_pairs": len(pairs) == 6 and len({row["first_event"] for row in pairs}) == 6,
        "three_rules": len(rules) == 3,
        "class_counts": classes == {"ADJACENT_CLOSED_FIELD_REPEAT": 3, "OPEN_SAME_FIELD_PAIR": 2, "OPEN_CROSS_LINE_CARRY": 1},
        "eleven_source_tokens": summary["visible_tokens"] == 12 and summary["source_tokens"] == 11,
        "carry_is_e180": [row["first_event"] for row in pairs if row["selected_rule"] == "READ_ONCE_CARRY"] == ["E180"],
        "two_open_pairs": {row["visible_pair"] for row in pairs if row["boundary_class"] == "OPEN_SAME_FIELD_PAIR"} == {"dy chy", "shor chor"},
        "three_closed_repeats": all(row["first_terminal"] == "TERMINAL" and row["second_terminal"] == "TERMINAL" for row in pairs if row["boundary_class"] == "ADJACENT_CLOSED_FIELD_REPEAT"),
        "y_y_not_aiin_plural": "Mehrzahl stammt aus Y–Y, nicht aus AIIN" in manual,
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in manual.lower() and not any("f84" in value.lower() for table in (pairs, rules) for row in table for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_twenty_sixth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
