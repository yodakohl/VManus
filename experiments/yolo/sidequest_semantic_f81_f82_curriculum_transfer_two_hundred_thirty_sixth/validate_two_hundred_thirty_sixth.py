#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ARTIFACTS = [
    "TWO_HUNDRED_THIRTY_SIXTH_ONE_HUNDRED_TWENTY_EIGHT_EVENTS.tsv",
    "TWO_HUNDRED_THIRTY_SIXTH_FORTY_THREE_DICTATION_TRACES.tsv",
    "TWO_HUNDRED_THIRTY_SIXTH_SIXTEEN_NONBASE_CARDS.tsv",
    "TWO_HUNDRED_THIRTY_SIXTH_READABLE_CURRICULUM_TRANSFER.md",
    "TWO_HUNDRED_THIRTY_SIXTH_REPORT.md",
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
    cards = read(ARTIFACTS[2])
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "one_hundred_twenty_eight_events": len(events) == 128 and {row["event_id"] for row in events} == {f"E{i:03d}" for i in range(101, 229)},
        "forty_three_statements": len(statements) == 43 and len({row["statement_id"] for row in statements}) == 43,
        "all_events_once": sorted(event for row in statements for event in row["event_ids"].split("|")) == [f"E{i:03d}" for i in range(101, 229)],
        "sixteen_nonbase_cards": len(cards) == 16 and len({row["master_card_id"] for row in cards}) == 16,
        "status_split_108_13_2_5": summary["base_rule_events"] == 108 and summary["existing_specialist_events"] == 13 and summary["partial_events"] == 2 and summary["local_whole_events"] == 5,
        "twenty_nine_base_statements": summary["fully_base_ruled_statements"] == 29,
        "four_local_whole_cards": len([row for row in cards if row["analysis_status"] == "LEARNED_LOCAL_WHOLE_CARD"]) == 4,
        "all_prompts_nonempty": all(row["master_dictation_de"].strip() and row["apprentice_response"].strip() for row in statements),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in " ".join((OUT / name).read_text(encoding="utf-8").lower() for name in ARTIFACTS[:-1]),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_thirty_sixth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
