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
    pairs = read("SEVEN_HUNDRED_EIGHTY_THIRD_10_FACTORED_RECIPE_PAIRS.tsv")
    operations = read("SEVEN_HUNDRED_EIGHTY_THIRD_3_REPEATED_ALLOGRAPH_OPERATIONS.tsv")
    drills = read("SEVEN_HUNDRED_EIGHTY_THIRD_9_VARIANT_DRILLS.tsv")
    events = read("SEVEN_HUNDRED_EIGHTY_THIRD_71_VARIANT_EVENT_TRACE.tsv")
    model = read("SEVEN_HUNDRED_EIGHTY_THIRD_28_MODEL_ONLY_VARIANT_EVENTS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_EIGHTY_THIRD_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_10_3_9_71_28": (len(pairs), len(operations), len(drills), len(events), len(model)) == (10, 3, 9, 71, 28),
        "drills_exact": all(row["forward_result"] in {row["long_form"], row["short_form"]} for row in drills),
        "op_counts_3_2_2": [int(row["families"]) for row in operations] == [3, 2, 2],
        "op_events_13_25_5": [int(row["events"]) for row in operations] == [13, 25, 5],
        "seven_families43_events": sum(row["teaching_tier"] != "COPY_WHOLE_VARIANT_FROM_MODEL" for row in pairs) == 7 and sum(int(row["pair_events"]) for row in pairs if row["teaching_tier"] != "COPY_WHOLE_VARIANT_FROM_MODEL") == 43,
        "three_model_families28_events": sum(row["teaching_tier"] == "COPY_WHOLE_VARIANT_FROM_MODEL" for row in pairs) == 3 and len(model) == 28,
        "all_semantics_preserved": all(row["semantic_value_changed"] == "NO" for row in pairs) and all(row["spoken_reading_preserved"] == "YES" for row in events),
        "model_subset_exact": {row["event_id"] for row in model} == {row["event_id"] for row in events if row["surface_memory"] == "COPY_WHOLE_VARIANT"},
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (pairs, operations, drills, events, model) for row in rows),
        "summary_pass": summary["status"] == "PASS" and (summary["operation_covered_events"], summary["model_only_events"]) == (43, 28),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_EIGHTY_THIRD_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
