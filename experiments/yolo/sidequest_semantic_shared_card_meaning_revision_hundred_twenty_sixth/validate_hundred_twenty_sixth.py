#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    cards = rows("HUNDRED_TWENTY_SIXTH_SEVENTEEN_REVISED_MEANINGS.tsv")
    contexts = rows("HUNDRED_TWENTY_SIXTH_136_OCCURRENCE_CONTEXTS.tsv")
    skeletons = rows("HUNDRED_TWENTY_SIXTH_57_REVISED_SHARED_READINGS.tsv")
    exercises = rows("HUNDRED_TWENTY_SIXTH_TWELVE_REVISED_EXERCISES.tsv")
    checks = {
        "cards_17": len(cards) == 17,
        "contexts_136": len(contexts) == 136,
        "skeletons_57": len(skeletons) == 57,
        "exercises_12": len(exercises) == 12,
        "card_forms_unique": len({row["master_form"] for row in cards}) == 17,
        "context_events_unique": len({row["event_serial"] for row in contexts}) == 136,
        "event_counts_sum": sum(int(row["event_count"]) for row in cards) == 136,
        "no_sentence_gloss_for_cheey": next(row["revised_portable_default_de"] for row in cards if row["master_form"] == "cheey") == "Klarlauf",
        "all_defaults_short": all(len(row["revised_portable_default_de"].split()) <= 3 for row in cards),
        "no_empty_cells": all(all(value for value in row.values()) for table in (cards, contexts, skeletons, exercises) for row in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
