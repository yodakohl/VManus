#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUTS = [
    "EIGHT_HUNDRED_TENTH_39_COMPONENT_FOURTH_GRAMMAR.tsv",
    "EIGHT_HUNDRED_TENTH_173_CARD_FOURTH_DICTIONARY.tsv",
    "EIGHT_HUNDRED_TENTH_381_EVENT_REPARSE.tsv",
    "EIGHT_HUNDRED_TENTH_116_STATEMENT_REPARSE.tsv",
    "EIGHT_HUNDRED_TENTH_8_REMAINDER_CARDS.tsv",
    "EIGHT_HUNDRED_TENTH_69_UNATTESTED_PREDICTIONS.tsv",
    "EIGHT_HUNDRED_TENTH_16_TEACHING_RULES.tsv",
    "EIGHT_HUNDRED_TENTH_BUILD_SUMMARY.json",
]


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_tenth.py")], check=True)
    first = {name: digest(name) for name in OUTPUTS}
    subprocess.run(["python", str(HERE / "build_eight_hundred_tenth.py")], check=True)
    second = {name: digest(name) for name in OUTPUTS}
    components = read(OUTPUTS[0]); cards = read(OUTPUTS[1]); events = read(OUTPUTS[2]); statements = read(OUTPUTS[3])
    remainder = read(OUTPUTS[4]); predictions = read(OUTPUTS[5]); rules = read(OUTPUTS[6])
    summary = json.loads((HERE / OUTPUTS[7]).read_text(encoding="utf-8"))
    checks = {
        "deterministic_rebuild": first == second,
        "counts_39_173_381_116": (len(components), len(cards), len(events), len(statements)) == (39, 173, 381, 116),
        "tiers_31_1_4_3": (summary["core_components"], summary["bound_components"], summary["local_components"], summary["whole_components"]) == (31, 1, 4, 3),
        "event_ids_complete": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)],
        "statement_event_sum": sum(int(row["events"]) for row in statements) == 381,
        "core_touch_170_377": (summary["core_touch_cards"], summary["core_touch_events"]) == (170, 377),
        "fully_core_165_372": (summary["fully_core_cards"], summary["fully_core_events"]) == (165, 372),
        "remainder_8_cards_9_events": len(remainder) == 8 and summary["remainder_events"] == 9,
        "predictions_69_no_collision_one_new_dedup": len(predictions) == 69 and summary["prediction_proposals"] == 70 and summary["deduplicated_prediction_rows"] == 1 and summary["prediction_collisions"] == 0,
        "solkeeey_two_sources": set(next(row for row in predictions if row["predicted_surface"] == "solkeeey")["sources"].split(",")) == {"PASS789_GRADE_HAND_BOARD", "PASS808_SOLK_GRID"},
        "sixteen_rules": len(rules) == 16,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "output_sha256": second}
    (HERE / "EIGHT_HUNDRED_TENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
