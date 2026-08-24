#!/usr/bin/env python3

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


events = rows("THREE_HUNDRED_THIRTY_SIXTH_16_FRESH_CARD_EVENTS.tsv")
passages = rows("THREE_HUNDRED_THIRTY_SIXTH_TWO_FRESH_PASSAGES.tsv")
anchors = rows("THREE_HUNDRED_THIRTY_SIXTH_TWO_EXACT_HANDOFF_ANCHORS.tsv")
checks = {
    "two_passages": len(passages) == 2,
    "sixteen_events": len(events) == 16 and len({row["fresh_event_id"] for row in events}) == 16,
    "all_identities_registered": all(row["registered_identity_match"] == "YES" for row in events),
    "all_values_registered": all(row["registered_value_match"] == "YES" for row in events),
    "both_sequences_fresh": all(row["fresh_full_sequence"] == "YES" for row in passages),
    "both_contiguous_sequences_fresh": all(row["fresh_contiguous_sequence"] == "YES" for row in passages),
    "two_exact_anchors": len(anchors) == 2 and {row["atomic_value_de"] for row in anchors} == {"Sollmaß", "Klarauszug"},
    "herbal_one_cycle": next(row for row in passages if row["register"] == "HERBAL")["microcycle_count"] == "1",
    "bio_three_cycles": next(row for row in passages if row["register"] == "BIO")["microcycle_count"] == "3",
    "fixed_source_pages_only": {row["source_page"] for row in events} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_absent": all(row["source_page"] not in {"f84", "f84r"} for row in events),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_THIRTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
