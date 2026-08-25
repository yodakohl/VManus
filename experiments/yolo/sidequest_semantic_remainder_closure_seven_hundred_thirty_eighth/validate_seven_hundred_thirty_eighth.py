#!/usr/bin/env python3
"""Validate Pass 738 remainder closure."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read("SEVEN_HUNDRED_THIRTY_EIGHTH_39_COMPONENT_DICTIONARY.tsv")
    pair = read("SEVEN_HUNDRED_THIRTY_EIGHTH_1_AN_AIN_MINIMAL_PAIR.tsv")
    decisions = read("SEVEN_HUNDRED_THIRTY_EIGHTH_8_REMAINDER_DECISIONS.tsv")
    contexts = read("SEVEN_HUNDRED_THIRTY_EIGHTH_9_REMAINDER_CONTEXTS.tsv")
    classes = read("SEVEN_HUNDRED_THIRTY_EIGHTH_4_COMPOSITION_CLASSES.tsv")
    cards = read("SEVEN_HUNDRED_THIRTY_EIGHTH_173_CARD_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_THIRTY_EIGHTH_381_EVENT_INTERLINEAR.tsv")
    statements = read("SEVEN_HUNDRED_THIRTY_EIGHTH_116_STATEMENT_EDITION.tsv")
    records = read("SEVEN_HUNDRED_THIRTY_EIGHTH_11_RECORD_EDITION.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_THIRTY_EIGHTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    class_counts = {row["composition_status"]: (int(row["cards"]), int(row["events"])) for row in classes}
    checks = {
        "components_39_one_paired_four_singleton_three_mem": len(components) == 39 and sum(row["category"] == "PARADIGM_SUPPORTED_BOUND_VARIANT_OF_AIN" for row in components) == 1 and sum(row["category"] == "CONTEXT_SINGLETON_COMPONENT" for row in components) == 4 and sum(row["category"] == "MEMORIZED_WHOLE_COMMAND" for row in components) == 3,
        "minimal_pair_exact": len(pair) == 1 and pair[0]["first_event"] == "E058" and pair[0]["second_event"] == "E059" and pair[0]["invariant_frame"] == "Y+K" and pair[0]["varying_component"] == "AIN→AN",
        "decisions_8_contexts_9": len(decisions) == 8 and len(contexts) == 9,
        "class_counts_exact": class_counts == {"FULLY_COMPOSED_FROM_RECURRENT_ROOTS": (165, 372), "COMPOSED_WITH_PARADIGM_SUPPORTED_AIN_VARIANT": (1, 1), "HAS_CONTEXT_SINGLETON_COMPONENT": (4, 4), "HAS_MEMORIZED_WHOLE_COMMAND": (3, 4)},
        "cards_173_events_381": len(cards) == 173 and len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "statements_116_records_11": len(statements) == 116 and len(records) == 11,
        "event_card_status_match": all(next(card["pass738_status"] for card in cards if card["exact_card_id"] == row["card_no"]) == row["composition_status"] for row in events),
        "all_core_unchanged": all(row["productive_core_changed"] == "NO" for row in decisions) and summary["productive_core_changes"] == 0,
        "form_fixed": summary["form_changes"] == 0 and all(row["form_owner_boundary_status"] == "UNCHANGED" for row in events + statements),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_THIRTY_EIGHTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
