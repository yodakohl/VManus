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
    names = [
        "TWO_HUNDRED_THIRD_15_VALUE_REVISIONS.tsv",
        "TWO_HUNDRED_THIRD_VALUE_COLLISION_AUDIT.tsv",
        "TWO_HUNDRED_THIRD_173_CARD_COMPACT_DICTIONARY.tsv",
        "TWO_HUNDRED_THIRD_381_EVENT_COMPACT_EDITION.tsv",
        "TWO_HUNDRED_THIRD_116_STATEMENT_COMPACT_EDITION.tsv",
        "TWO_HUNDRED_THIRD_AFFECTED_STATEMENTS.tsv",
        "BUILD_SUMMARY.json",
    ]
    return {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in names}


def main() -> None:
    revisions = read("TWO_HUNDRED_THIRD_15_VALUE_REVISIONS.tsv")
    collisions = read("TWO_HUNDRED_THIRD_VALUE_COLLISION_AUDIT.tsv")
    dictionary = read("TWO_HUNDRED_THIRD_173_CARD_COMPACT_DICTIONARY.tsv")
    events = read("TWO_HUNDRED_THIRD_381_EVENT_COMPACT_EDITION.tsv")
    statements = read("TWO_HUNDRED_THIRD_116_STATEMENT_COMPACT_EDITION.tsv")
    affected = read("TWO_HUNDRED_THIRD_AFFECTED_STATEMENTS.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    selected = {row["master_card_id"]: row["new_value_de"] for row in revisions}
    dictionary_values = {row["master_card_id"]: row["current_value_de"] for row in dictionary}
    allowed_records = {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"}
    checks = {
        "15_revisions": len(revisions) == 15 and len(selected) == 15,
        "173_cards": len(dictionary) == 173 and len(dictionary_values) == 173,
        "381_events": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "116_statements": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "all_revisions_applied": all(dictionary_values[card_id] == value for card_id, value in selected.items()),
        "events_match_dictionary": all(row["portable_value_de"] == dictionary_values[row["master_card_id"]] for row in events),
        "statement_literals_match_events": all(
            row["literal_card_reading"] == " | ".join(event["portable_value_de"] for event in events if event["statement_id"] == row["statement_id"])
            for row in statements
        ),
        "162_values_before": summary["distinct_values_before"] == 162,
        "11_duplicates_before": summary["duplicate_groups_before"] == 11,
        "172_values_after": summary["distinct_values_after"] == 172,
        "one_duplicate_after": summary["duplicate_groups_after"] == 1,
        "sole_duplicate_is_chd_allomorphy": summary["sole_duplicate_after"] == {"einführen; Schluss": ["MC005", "MC088"]},
        "collision_audit_complete": len(collisions) == 11,
        "short_atomic_values": all(0 < len(row["current_value_de"].split()) <= 3 for row in dictionary),
        "no_blank_values": all(row["current_value_de"].strip() for row in dictionary),
        "affected_rows_have_real_changes": all(row["old_literal"] != row["new_literal"] or row["old_fluent"] != row["new_fluent"] for row in affected),
        "fixed_records_only": {row["record_unit_id"] for row in events} <= allowed_records,
        "sealed_absent": not any("f84" in value.lower() for rows in (dictionary, events, statements) for row in rows for value in row.values()),
        "sealed_not_accessed": summary["sealed_pages_accessed"] is False,
    }
    first = hashes()
    subprocess.run(["python3", str(OUT / "build_two_hundred_third.py")], check=True)
    second = hashes()
    checks["deterministic_rebuild"] = first == second
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary, "artifact_sha256": second}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
