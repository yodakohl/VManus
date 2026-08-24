#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    trace = read("FIVE_HUNDRED_NINETY_FIFTH_381_COMPLETE_SURFACE_TRACE.tsv")
    prefs = read("FIVE_HUNDRED_NINETY_FIFTH_34_CARD_PREFERENCES.tsv")
    sources = read("FIVE_HUNDRED_NINETY_FIFTH_FOUR_RENDERER_SOURCES.tsv")
    melodies = read("FIVE_HUNDRED_NINETY_FIFTH_NINE_RECORD_MELODIES.tsv")
    counts = Counter(row["renderer_source"] for row in trace)
    checks = {
        "trace381": len(trace) == 381 and len({row["event_id"] for row in trace}) == 381,
        "cards173": len({row["card_no"] for row in trace}) == 173,
        "preferences34": len(prefs) == 34 and len({row["card_no"] for row in prefs}) == 34,
        "palette_events202": sum(int(row["events"]) for row in prefs) == 202,
        "source_counts": counts == Counter({"GLOBAL_RULE_RENDERER": 314, "FORMULA_CADENCE_RULE": 32, "RECORD_WRAPPER_MELODY": 27, "AUTOMATIC_CONTEXT_RULE": 8}),
        "sources4": len(sources) == 4 and sum(int(row["events"]) for row in sources) == 381,
        "melodies9": len(melodies) == 9,
        "exact_surfaces": all(row["final_surface"] and row["requires_local_event_lookup"] == "NO" for row in trace),
        "meaning_unchanged": all(row["surface_changes_meaning"] == "NO" for row in trace),
        "no_free_choice": all(row["free_choice"] == "NO" for row in prefs),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_NINETY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
