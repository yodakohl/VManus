#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    deck = read_tsv("PASS965_30_COMMON_FORMULA_CARDS.tsv")
    demoted = read_tsv("PASS965_36_PRODUCTIVE_FORMER_FORMULAS.tsv")
    events = read_tsv("PASS965_2511_COMPACT_DECK_EDITION.tsv")
    entries = read_tsv("PASS965_COMPACT_86_ENTRY_CODEBOOK.tsv")
    counts = Counter(row["compact_layer"] for row in events)
    formula_by_recipe = {row["component_recipe"]: row for row in deck}
    checks = {
        "deck_30": len(deck) == 30,
        "demoted_36": len(demoted) == 36,
        "formula_partition_66": {row["formula_card_id"] for row in deck}.isdisjoint({row["formula_card_id"] for row in demoted}) and len(deck) + len(demoted) == 66,
        "all_kept_meet_rule": all(int(row["events_including_local"]) >= 10 and len(row["physical_pages"].split("|")) >= 3 for row in deck),
        "all_demoted_fail_rule": all(int(row["events_including_local"]) < 10 or len(row["physical_pages"].split("|")) < 3 for row in demoted),
        "events_2511": len(events) == 2511 and len({row["event_id"] for row in events}) == 2511,
        "demoted_events_177": sum(row["revision"] == "FORMULA_DEMOTED_TO_PRODUCTIVE_COMPOSITION" for row in events) == 177,
        "layer_counts": counts == Counter({"PRODUCTIVE_ABBREVIATION_COMPOSITION": 1397, "LEARNED_FORMULA_CARD": 613, "LOCAL_NOMENCLATOR_OR_ADDRESS": 501}),
        "compact_entries_86": len(entries) == 86,
        "entry_types": Counter(row["entry_type"] for row in entries) == Counter({"ROOT_OR_LOCAL_SIGN": 56, "FORMULA_CARD": 30}),
        "formula_values_are_portable_cores": all(
            row["portable_value_de"] == formula_by_recipe[row["recognition_form"]]["portable_atomic_core_de"]
            for row in entries if row["entry_type"] == "FORMULA_CARD"
        ),
        "no_empty_meanings": all(row["portable_value_de"] for row in entries),
        "no_sealed_pages": not any("f84" in str(row).lower() for row in deck + demoted + events + entries),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "PASS965_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
