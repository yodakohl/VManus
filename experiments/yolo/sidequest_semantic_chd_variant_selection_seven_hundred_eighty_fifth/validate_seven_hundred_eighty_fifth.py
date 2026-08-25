#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("SEVEN_HUNDRED_EIGHTY_FIFTH_48_CHD_EVENTS.tsv")
    cards = read("SEVEN_HUNDRED_EIGHTY_FIFTH_22_CHD_CARD_LESSONS.tsv")
    short = read("SEVEN_HUNDRED_EIGHTY_FIFTH_6_SHORT_CARD_STRIP.tsv")
    features = read("SEVEN_HUNDRED_EIGHTY_FIFTH_10_SELECTION_FEATURES.tsv")
    models = read("SEVEN_HUNDRED_EIGHTY_FIFTH_3_SELECTION_MODELS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_EIGHTY_FIFTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_48_22_6_10_3": (len(events), len(cards), len(short), len(features), len(models)) == (48, 22, 6, 10, 3),
        "classes_38_9_1": (sum(row["observed_length_class"] == "LONG_CHED" for row in events), sum(row["observed_length_class"] == "SHORT_CHD" for row in events), sum(row["observed_length_class"] == "COMPLEX_INTERLEAVED" for row in events)) == (38, 9, 1),
        "all_hand2": {row["hand"] for row in events} == {"HAND_2"},
        "short_ids": {row["exact_card_id"] for row in short} == {"PROC077", "PROC082", "PROC094", "PROC144", "PROC166", "PROC168"},
        "proc042_mixed_wrapper_rule": next(row for row in cards if row["exact_card_id"] == "PROC042")["lesson"] == "WRAPPER_SELECTS_CH_OR_CHE",
        "all_selected": all(row["selection_correct"] == "YES" for row in events),
        "model_scores_38_40_48": [int(row["correct_events"]) for row in models] == [38, 40, 48],
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (events, cards, short, features, models) for row in rows),
        "summary_pass": summary["status"] == "PASS" and (summary["events"], summary["cards"], summary["selected_correct"]) == (48, 22, 48),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_EIGHTY_FIFTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
