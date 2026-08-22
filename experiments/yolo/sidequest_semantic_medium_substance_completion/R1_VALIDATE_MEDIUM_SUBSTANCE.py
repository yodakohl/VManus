#!/usr/bin/env python3
"""Validate the complete R1 medium/substance candidate edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
DICT_PATH = HERE / "R1_173_MEDIUM_SUBSTANCE_DICTIONARY.tsv"
EVENT_PATH = HERE / "R1_381_MEDIUM_SUBSTANCE_INTERLINEAR.tsv"
STATEMENT_PATH = HERE / "R1_116_MEDIUM_SUBSTANCE_SENTENCES.tsv"
RECORD_PATH = HERE / "R1_11_MEDIUM_SUBSTANCE_RECORDS.md"
COMPONENT_PATH = HERE / "R1_MEDIUM_SUBSTANCE_COMPONENTS.tsv"
PARADIGM_PATH = HERE / "R1_MEDIUM_SUBSTANCE_PARADIGM.tsv"
SUMMARY_PATH = HERE / "R1_BUILD_SUMMARY.json"
VALIDATION_PATH = HERE / "R1_VALIDATION.json"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
EXPECTED_TARGET_COUNTS = {
    "12efe866f335461823a6": 1,
    "22fb87a5a83e5c3fb510": 1,
    "7d2404c835b10a2c06af": 1,
    "b154ff779abe5f196c80": 1,
    "8aedd154964a78e555d6": 1,
    "087a47b5423438cd6b6a": 1,
    "807591efc3d3f7ddbfab": 1,
    "cbb42a4fe68068325d6b": 1,
    "98bdc4244c84cbef3321": 1,
    "cb57b696b815fdef9cb7": 1,
    "428a5e3662aa57b4b256": 1,
    "0f18de177ed7c878bf95": 2,
    "b2812c8283c3a62438bd": 1,
    "883a6708116c342cb10b": 1,
    "2cc054357a929df85f64": 4,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(message)
    checks.append(message)


def main() -> dict[str, object]:
    checks: list[str] = []
    dictionary = read_tsv(DICT_PATH)
    events = read_tsv(EVENT_PATH)
    statements = read_tsv(STATEMENT_PATH)
    components = read_tsv(COMPONENT_PATH)
    paradigm = read_tsv(PARADIGM_PATH)
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

    require(len(dictionary) == 173, "dictionary has exactly 173 cards", checks)
    require(len(events) == 381, "interlinear has exactly 381 events", checks)
    require(len(statements) == 116, "sentence table has exactly 116 statements", checks)
    require(len({row["record_unit_id"] for row in events}) == 11, "event table has exactly 11 records", checks)
    require(len({row["joint_tuple_id"] for row in dictionary}) == 173, "dictionary card IDs are unique", checks)
    require(len({row["event_id"] for row in events}) == 381, "event IDs are unique", checks)
    require(len({row["statement_id"] for row in statements}) == 116, "statement IDs are unique", checks)
    require({row["page"] for row in events} <= ALLOWED_PAGES, "only the seven fixed pages occur", checks)
    require(all(not row["page"].lower().startswith("f84") for row in events), "no f84/f84r event is present", checks)

    for field in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "reading_type"):
        require(all(row[field].strip() for row in dictionary), f"dictionary field {field} has no blank default", checks)
    for field in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "contextual_event_reading_de"):
        require(all(row[field].strip() for row in events), f"event field {field} has no blank value", checks)

    by_id = {row["joint_tuple_id"]: row for row in dictionary}
    require(all(row["joint_tuple_id"] in by_id for row in events), "every event resolves to one dictionary card", checks)
    for row in events:
        card = by_id[row["joint_tuple_id"]]
        for field in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de"):
            if row[field] != card[field]:
                raise AssertionError(f"event/card mismatch at {row['event_id']} field {field}")
    checks.append("all current event card fields equal their dictionary defaults")

    counts = Counter(row["joint_tuple_id"] for row in events)
    require(all(counts[ident] == count for ident, count in EXPECTED_TARGET_COUNTS.items()), "all 19 revised target occurrences are present with frozen counts", checks)
    changed = [row for row in events if row["medium_revision_family"] != "UNCHANGED"]
    require(len(changed) == 19, "exactly 19 event readings changed", checks)
    require(len([row for row in dictionary if row["medium_revision_family"] != "UNCHANGED"]) == 15, "exactly 15 exact cards changed", checks)

    air_ids = {"12efe866f335461823a6", "22fb87a5a83e5c3fb510", "7d2404c835b10a2c06af", "b154ff779abe5f196c80", "8aedd154964a78e555d6"}
    require(all("AIR=Laufflüssigkeit" in by_id[ident]["stable_concrete_nucleus_de"] for ident in air_ids), "AIR is invariantly Laufflüssigkeit in all five cards", checks)
    cheo_ids = {"087a47b5423438cd6b6a", "807591efc3d3f7ddbfab"}
    require(all("CHEO=Auszug" in by_id[ident]["stable_concrete_nucleus_de"] for ident in cheo_ids), "CHEO is invariantly Auszug in both cards", checks)

    plant_events = [row for row in events if row["joint_tuple_id"] == "2cc054357a929df85f64"]
    require(len(plant_events) == 4 and all(row["concrete_word_reading_de"] == "Pflanzenstoff" for row in plant_events), "all cho|sho exact-card events mean Pflanzenstoff", checks)
    require(all("honig" not in row["contextual_event_reading_de"].lower() for row in events), "no current event invents honey", checks)
    require(by_id["428a5e3662aa57b4b256"]["concrete_word_reading_de"] == "Weinsud", "SCHOAL is the compact whole card Weinsud", checks)
    require(by_id["cb57b696b815fdef9cb7"]["concrete_word_reading_de"] == "Badwasser", "SHECTHY is the compact whole card Badwasser", checks)

    statement_event_ids = [event_id for row in statements for event_id in row["event_ids"].split("|")]
    require(Counter(statement_event_ids) == Counter(row["event_id"] for row in events), "statements cover every event exactly once", checks)
    require(sum(int(row["event_count"]) for row in statements) == 381, "statement event counts sum to 381", checks)
    require(RECORD_PATH.read_text(encoding="utf-8").count("\n## ") == 11, "record markdown contains 11 record headings", checks)
    require(len(components) == 13, "component table has 13 compact rows", checks)
    require(len(paradigm) == 23, "paradigm table has 23 exhaustive target-card rows", checks)
    require(all(row["event_ids"].strip() for row in paradigm), "every paradigm card has explicit event IDs", checks)
    require(summary["cards"] == 173 and summary["events"] == 381 and summary["statements"] == 116 and summary["records"] == 11, "build summary dimensions agree", checks)

    result: dict[str, object] = {
        "schema": "SIDEQUEST_R1_MEDIUM_SUBSTANCE_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks": checks,
        "counts": {
            "cards": len(dictionary),
            "events": len(events),
            "statements": len(statements),
            "records": len({row["record_unit_id"] for row in events}),
            "changed_cards": 15,
            "changed_events": 19,
            "components": len(components),
            "paradigm_rows": len(paradigm),
        },
        "sealed_pages": ["f84", "f84r"],
    }
    VALIDATION_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=2, sort_keys=True))
