#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ARTIFACTS = [
    "TWO_HUNDRED_THIRTY_SEVENTH_ONE_HUNDRED_TWENTY_EIGHT_EVENTS.tsv",
    "TWO_HUNDRED_THIRTY_SEVENTH_FORTY_THREE_STATEMENTS.tsv",
    "TWO_HUNDRED_THIRTY_SEVENTH_SIX_SPECIALIST_COMPONENTS.tsv",
    "TWO_HUNDRED_THIRTY_SEVENTH_SIX_WHOLE_SIGNS.tsv",
    "TWO_HUNDRED_THIRTY_SEVENTH_READABLE_SECOND_LESSON.md",
    "TWO_HUNDRED_THIRTY_SEVENTH_REPORT.md",
    "BUILD_SUMMARY.json",
]


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in ARTIFACTS}


def main() -> None:
    events = read(ARTIFACTS[0])
    statements = read(ARTIFACTS[1])
    components = read(ARTIFACTS[2])
    signs = read(ARTIFACTS[3])
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "one_hundred_twenty_eight_events": len(events) == 128 and {row["event_id"] for row in events} == {f"E{i:03d}" for i in range(101, 229)},
        "forty_three_statements": len(statements) == 43 and len({row["statement_id"] for row in statements}) == 43,
        "all_events_once": sorted(event for row in statements for event in row["event_ids"].split("|")) == [f"E{i:03d}" for i in range(101, 229)],
        "six_components": len(components) == 6 and {row["component"] for row in components} == {"AIN", "AIR", "IIN", "CKH", "LSH", "RESULT"},
        "six_whole_signs": len(signs) == 6 and len({row["master_card_id"] for row in signs}) == 6,
        "status_split_108_13_7": summary["base_events"] == 108 and summary["specialist_component_events"] == 13 and summary["whole_sign_events"] == 7,
        "seven_revised_statements": summary["revised_statements"] == 7 and sum(row["statement_status"] == "REVISED_WHOLE_SIGN_READING" for row in statements) == 7,
        "all_values_concrete": all(row["lesson_two_value_de"].strip() for row in events),
        "no_placeholders": all(not any(term in row["lesson_two_value_de"].upper() for term in ("UNKNOWN", "EXEMPLAR", "FORMAL")) for row in events),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in " ".join((OUT / name).read_text(encoding="utf-8").lower() for name in ARTIFACTS[:-1]),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_thirty_seventh.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
