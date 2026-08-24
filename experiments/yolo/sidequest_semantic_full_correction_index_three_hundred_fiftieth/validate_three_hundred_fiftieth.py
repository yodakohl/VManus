#!/usr/bin/env python3
"""Validate the complete one-card correction index."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read_tsv("THREE_HUNDRED_FIFTIETH_381_SINGLE_CARD_REPAIR_INDEX.tsv")
    classes = read_tsv("THREE_HUNDRED_FIFTIETH_REPAIR_CLASS_SUMMARY.tsv")
    pairs = read_tsv("THREE_HUNDRED_FIFTIETH_AMBIGUOUS_CARD_PAIRS.tsv")
    counts = Counter(row["repair_class"] for row in events)
    checks = {
        "381_events": len(events) == 381,
        "event_ids_exact": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)],
        "173_cards": len({row["source_joint_tuple_id"] for row in events}) == 173,
        "three_classes": set(counts) == {"AUTOMATICALLY_REPAIRABLE", "DETECTABLE_BUT_AMBIGUOUS", "MASTER_EXEMPLAR_ONLY"},
        "class_counts_297_72_12": counts == {"AUTOMATICALLY_REPAIRABLE": 297, "DETECTABLE_BUT_AMBIGUOUS": 72, "MASTER_EXEMPLAR_ONLY": 12},
        "summary_matches": {row["repair_class"]: int(row["events"]) for row in classes} == dict(counts),
        "14_ambiguous_pairs": len(pairs) == 14,
        "each_pair_has_two_cards": all(len(row["competing_joint_tuple_ids"].split("|")) == 2 for row in pairs),
        "wrong_card_is_different": all(row["source_joint_tuple_id"] != row["nearest_wrong_joint_tuple_id"] for row in events),
        "all_wrong_forms_registered": all(int(row["surface_edit_distance"]) >= 0 and row["nearest_wrong_surface"] for row in events),
        "all_meanings_preserved": all(row["meaning_preserved_after_repair"] == "YES" for row in events),
        "master_rows_are_singletons": all(row["deck_class"] == "MEMORIZED_WHOLE_CARD" and row["card_occurrences"] == "1" for row in events if row["repair_class"] == "MASTER_EXEMPLAR_ONLY"),
        "all_current_pair_contexts_resolve": all(row["all_current_occurrences_resolved_by_owner_plus_right_neighbor"] == "YES" for row in pairs),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    result = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_FIFTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("validation failed")
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
