#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUTS = [
    "EIGHT_HUNDRED_FIFTEENTH_39_COMPONENT_FIFTH_GRAMMAR.tsv", "EIGHT_HUNDRED_FIFTEENTH_173_CARD_FIFTH_DICTIONARY.tsv",
    "EIGHT_HUNDRED_FIFTEENTH_381_EVENT_REPARSE.tsv", "EIGHT_HUNDRED_FIFTEENTH_116_STATEMENT_REPARSE.tsv",
    "EIGHT_HUNDRED_FIFTEENTH_6_REMAINDER_CARDS.tsv", "EIGHT_HUNDRED_FIFTEENTH_76_UNATTESTED_PREDICTIONS.tsv",
    "EIGHT_HUNDRED_FIFTEENTH_17_TEACHING_RULES.tsv", "EIGHT_HUNDRED_FIFTEENTH_BUILD_SUMMARY.json",
]


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fifteenth.py")], check=True)
    first = {name: digest(name) for name in OUTPUTS}
    subprocess.run(["python", str(HERE / "build_eight_hundred_fifteenth.py")], check=True)
    second = {name: digest(name) for name in OUTPUTS}
    components = read(OUTPUTS[0]); cards = read(OUTPUTS[1]); events = read(OUTPUTS[2]); statements = read(OUTPUTS[3])
    remainder = read(OUTPUTS[4]); predictions = read(OUTPUTS[5]); rules = read(OUTPUTS[6]); summary = json.loads((HERE / OUTPUTS[7]).read_text(encoding="utf-8"))
    checks = {
        "deterministic_rebuild": first == second,
        "counts_39_173_381_116": (len(components), len(cards), len(events), len(statements)) == (39, 173, 381, 116),
        "tiers_33_3_3": (summary["core_components"], summary["bound_components"], summary["whole_components"]) == (33, 3, 3),
        "event_ids_complete": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)],
        "statement_event_sum": sum(int(row["events"]) for row in statements) == 381,
        "core_touch_170_377": (summary["core_touch_cards"], summary["core_touch_events"]) == (170, 377),
        "fully_core_167_374": (summary["fully_core_cards"], summary["fully_core_events"]) == (167, 374),
        "remainder_6_cards_7_events": len(remainder) == 6 and summary["remainder_events"] == 7,
        "predictions_76_no_collision": len(predictions) == 76 and summary["unique_predictions"] == 76 and summary["prediction_collisions"] == 0,
        "seventeen_rules": len(rules) == 17,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "output_sha256": second}
    (HERE / "EIGHT_HUNDRED_FIFTEENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
