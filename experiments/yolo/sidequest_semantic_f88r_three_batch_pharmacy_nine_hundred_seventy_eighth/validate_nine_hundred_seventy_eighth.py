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
    events = read("PASS978_F88R_150_EVENT_THREE_BATCH_EDITION.tsv")
    batches = read("PASS978_THREE_BATCH_RECIPES.tsv")
    checks = {
        "events_150": len(events) == 150,
        "event_ids_unique": len({r["event_id"] for r in events}) == 150,
        "labels_16": sum(r["role"] == "LEARNED_DRUG_LABEL" for r in events) == 16,
        "prose_134": sum(r["role"] == "PRODUCTIVE_RECIPE_PROSE" for r in events) == 134,
        "batches_3": len(batches) == 3,
        "batch_event_totals_150": sum(int(r["label_events"]) + int(r["prose_events"]) for r in batches) == 150,
        "labels_have_objects": all(r["visual_object_id"] != "NONE" for r in events if r["role"] == "LEARNED_DRUG_LABEL"),
        "prose_has_clause": all(r["clause_id"] != "NONE__LABEL" for r in events if r["role"] == "PRODUCTIVE_RECIPE_PROSE"),
        "three_label_counts": [int(r["label_events"]) for r in batches] == [6, 6, 4],
        "all_concrete": all(r["short_working_reading_de"] for r in events),
        "sealed_absent": all("f84" not in r["locus"].lower() for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS978_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
