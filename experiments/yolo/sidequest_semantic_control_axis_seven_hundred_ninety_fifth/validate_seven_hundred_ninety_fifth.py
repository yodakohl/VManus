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
    events = read("SEVEN_HUNDRED_NINETY_FIFTH_138_CONTROL_EVENTS.tsv")
    cores = read("SEVEN_HUNDRED_NINETY_FIFTH_3_CONTROL_CORES.tsv")
    tails = read("SEVEN_HUNDRED_NINETY_FIFTH_11_SHARED_TAILS.tsv")
    shared_events = read("SEVEN_HUNDRED_NINETY_FIFTH_89_SHARED_TAIL_EVENTS.tsv")
    predictions = read("SEVEN_HUNDRED_NINETY_FIFTH_8_PREDICTED_THIRD_CORES.tsv")
    withheld = read("SEVEN_HUNDRED_NINETY_FIFTH_1_WITHHELD_RECURSION.tsv")
    opaque = read("SEVEN_HUNDRED_NINETY_FIFTH_1_OPAQUE_OL_ALLOGRAPH.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_NINETY_FIFTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_138_3_11_89_8_1_1": (len(events), len(cores), len(tails), len(shared_events), len(predictions), len(withheld), len(opaque)) == (138, 3, 11, 89, 8, 1, 1),
        "core_counts_79_26_33": {row["control_core"]: int(row["events"]) for row in cores} == {"OK": 79, "OT": 26, "OL": 33},
        "cards49_recipes43": len({row["exact_card_id"] for row in events}) == 49 and len({row["component_recipe"] for row in events}) == 43,
        "meaning_invariant138": all(row["meaning_invariant"] == "YES" for row in events),
        "transparent137_opaque1": sum(row["surface_transparency"] == "TRANSPARENT" for row in events) == 137 and len(opaque) == 1,
        "opaque_is_ls": opaque[0]["surface"] == "ls" and opaque[0]["component_recipe"] == "OL",
        "complete_tails_y_chddy": {row["tail_recipe"] for row in tails if row["status"] == "THREE_CORE_COMPLETE"} == {"Y", "CHD+DY"},
        "predictions_unseen": all(row["fixed_page_collision"] == "NO" for row in predictions),
        "recursion_withheld": withheld[0]["would_be_recipe"] == "OL+OL" and withheld[0]["decision"] == "WITHHOLD_RECURSIVE_CONTROL_AS_NEW_CARD",
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for rows in (events, cores, tails, shared_events, predictions, withheld, opaque) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["decision"] == "OK_OT_OL_CONTROL_AXIS_INVARIANT_OVER_ELEVEN_SHARED_TAILS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_NINETY_FIFTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
