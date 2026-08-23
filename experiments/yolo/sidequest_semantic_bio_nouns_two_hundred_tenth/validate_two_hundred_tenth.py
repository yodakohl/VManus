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
    names = ["TWO_HUNDRED_TENTH_15_BIO_VISIBLE_OWNERS.tsv", "TWO_HUNDRED_TENTH_25_BIO_NOUN_LOCATION_CARDS.tsv", "TWO_HUNDRED_TENTH_281_EVENT_OWNER_NOUN_EDITION.tsv", "TWO_HUNDRED_TENTH_SIX_BIO_RECORD_READINGS.tsv", "BUILD_SUMMARY.json"]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    owners = read("TWO_HUNDRED_TENTH_15_BIO_VISIBLE_OWNERS.tsv")
    nouns = read("TWO_HUNDRED_TENTH_25_BIO_NOUN_LOCATION_CARDS.tsv")
    events = read("TWO_HUNDRED_TENTH_281_EVENT_OWNER_NOUN_EDITION.tsv")
    records = read("TWO_HUNDRED_TENTH_SIX_BIO_RECORD_READINGS.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "15_visible_owners": len(owners) == 15,
        "249_direct_32_unresolved_owner_events": summary["direct_owner_events"] == 249 and summary["unresolved_owner_events"] == 32,
        "25_noun_location_cards": len(nouns) == 25 and len({row["master_card_id"] for row in nouns}) == 25,
        "281_events": len(events) == 281 and len({row["event_id"] for row in events}) == 281,
        "97_statements": summary["statements"] == 97,
        "six_records": len(records) == 6 and {row["record_unit_id"] for row in records} == {"B1", "B2", "B3", "B4", "B5", "B6"},
        "one_freshwater_occurrence": summary["freshwater_occurrences"] == 1,
        "zero_person_word_cards": summary["person_word_cards"] == 0,
        "no_global_circuit_claim": all("Gesamtkreislauf" in row["intentionally_unassigned_nouns"] for row in records),
        "fixed_pages_only": {row["page"] for row in events} == {"f81v", "f82r", "f83r"},
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
        "sealed_absent": not any("f84" in value.lower() for rows in (owners, nouns, events, records) for row in rows for value in row.values()),
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_tenth.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
