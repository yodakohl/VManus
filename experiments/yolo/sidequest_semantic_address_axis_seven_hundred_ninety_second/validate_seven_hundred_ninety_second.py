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
    events = read("SEVEN_HUNDRED_NINETY_SECOND_53_ADDRESS_EVENTS.tsv")
    cards = read("SEVEN_HUNDRED_NINETY_SECOND_32_ADDRESS_CARDS.tsv")
    pairs = read("SEVEN_HUNDRED_NINETY_SECOND_5_PAIRED_PARADIGMS.tsv")
    rungs = read("SEVEN_HUNDRED_NINETY_SECOND_10_ADDRESS_RUNGS.tsv")
    direct = read("SEVEN_HUNDRED_NINETY_SECOND_6_DIRECT_SURFACE_PAIRS.tsv")
    counterparts = read("SEVEN_HUNDRED_NINETY_SECOND_22_UNPAIRED_COUNTERPARTS.tsv")
    predictions = read("SEVEN_HUNDRED_NINETY_SECOND_22_PREDICTED_SURFACES.tsv")
    false_splits = read("SEVEN_HUNDRED_NINETY_SECOND_1_FALSE_AL_SPLIT.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_NINETY_SECOND_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_53_32_5_10_6_22_22_1": (len(events), len(cards), len(pairs), len(rungs), len(direct), len(counterparts), len(predictions), len(false_splits)) == (53, 32, 5, 10, 6, 22, 22, 1),
        "al39_ar14": sum(row["address_token"] == "AL" for row in events) == 39 and sum(row["address_token"] == "AR" for row in events) == 14,
        "all_true_events_transparent": all(row["surface_transparency"] == "TRANSPARENT" for row in events),
        "paired_signatures": {row["address_signature"] for row in pairs} == {"ADDR", "OK+ADDR", "K+ADDR", "L+CHD+ADDR", "OT+ADDR"},
        "paired_events30": sum(int(row["total_events"]) for row in pairs) == 30,
        "six_direct_pairs": {(row["al_surface"], row["ar_surface"]) for row in direct} == {("dal", "dar"), ("sal", "sar"), ("chal", "char"), ("qokal", "qokar"), ("otal", "otar"), ("lchedal", "lchedar")},
        "predictions_unseen": all(row["fixed_page_collision"] == "NO" for row in predictions),
        "false_split_is_talam": [(row["surface"], row["component_recipe"]) for row in false_splits] == [("talam", "TALAM")],
        "readings_invariant": all(row["address_reading_de"] == ("ZIELSTELLE" if row["address_token"] == "AL" else "QUELLE") for row in events),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for rows in (events, cards, pairs, rungs, direct, counterparts, predictions, false_splits) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["decision"] == "AL_TARGET_AND_AR_SOURCE_FORM_PRODUCTIVE_ADDRESS_PAIRS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_NINETY_SECOND_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
