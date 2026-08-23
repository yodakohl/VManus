#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ARTIFACTS = [
    "TWO_HUNDRED_THIRTIETH_TWENTY_SEVEN_CARD_PORTABILITY.tsv",
    "TWO_HUNDRED_THIRTIETH_ONE_HUNDRED_FIFTY_TWO_OCCURRENCES.tsv",
    "TWO_HUNDRED_THIRTIETH_THREE_STATION_PORTABILITY.tsv",
    "TWO_HUNDRED_THIRTIETH_REPORT.md",
    "BUILD_SUMMARY.json",
]


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes() -> dict[str, str]:
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in ARTIFACTS}


def main() -> None:
    cards = read(ARTIFACTS[0])
    occurrences = read(ARTIFACTS[1])
    stations = read(ARTIFACTS[2])
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    classes = {row["portability_class"] for row in cards}
    checks = {
        "twenty_seven_unique_cards": len(cards) == 27 and len({row["master_card_id"] for row in cards}) == 27,
        "one_hundred_fifty_two_unique_occurrences": len(occurrences) == 152 and len({row["event_id"] for row in occurrences}) == 152,
        "thirty_five_target_occurrences": sum(row["is_r229_station_event"] == "YES" for row in occurrences) == 35,
        "one_hundred_seventeen_outside": sum(row["is_r229_station_event"] == "NO" for row in occurrences) == 117,
        "classes_exact": classes == {"STRONG_PORTABLE_ACTION_OR_CONTROL", "TENTATIVE_PORTABLE_ACTION_OR_CONTROL", "LOCAL_LEARNED_WHOLE_CARD"},
        "sixteen_three_eight_cards": summary["strong_portable_cards"] == 16 and summary["tentative_portable_cards"] == 3 and summary["local_whole_cards"] == 8,
        "station_event_split": {(row["station_id"], row["target_events"], row["transferable_event_total"], row["local_whole_card_events"]) for row in stations} == {("F83_STATION_1", "10", "9", "1"), ("F83_STATION_2", "9", "8", "1"), ("F83_STATION_3", "16", "10", "6")},
        "local_cards_not_promoted": all(row["dictionary_action"] == "KEEP_AS_LOCAL_WHOLE_CARD_ONLY" for row in cards if row["portability_class"] == "LOCAL_LEARNED_WHOLE_CARD"),
        "generic_values_no_station_noun": all(not any(noun in row["portable_value_de"].lower() for noun in ("sammelstelle", "haltegefäß", "absetzgefäß")) for row in cards),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": "f84" not in " ".join((OUT / name).read_text(encoding="utf-8").lower() for name in ARTIFACTS),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_thirtieth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
