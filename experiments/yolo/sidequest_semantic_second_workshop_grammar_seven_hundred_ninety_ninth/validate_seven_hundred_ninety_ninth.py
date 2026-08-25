#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = read("SEVEN_HUNDRED_NINETY_NINTH_39_COMPONENT_SECOND_GRAMMAR.tsv")
    cards = read("SEVEN_HUNDRED_NINETY_NINTH_173_CARD_SECOND_DICTIONARY.tsv")
    events = read("SEVEN_HUNDRED_NINETY_NINTH_381_EVENT_REPARSE.tsv")
    statements = read("SEVEN_HUNDRED_NINETY_NINTH_116_STATEMENT_REPARSE.tsv")
    whole = read("SEVEN_HUNDRED_NINETY_NINTH_3_MEMORIZED_WHOLE_CARDS.tsv")
    predictions = read("SEVEN_HUNDRED_NINETY_NINTH_56_UNATTESTED_PREDICTIONS.tsv")
    renderer = read("SEVEN_HUNDRED_NINETY_NINTH_8_RENDERER_RULES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_NINETY_NINTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    tier_counts = Counter(row["grammar_tier"] for row in components)
    card_tiers = Counter(row["card_tier"] for row in cards)
    event_tiers = Counter(row["card_tier"] for row in events)
    checks = {
        "counts_39_173_381_116_3_56_8": (len(components), len(cards), len(events), len(statements), len(whole), len(predictions), len(renderer)) == (39, 173, 381, 116, 3, 56, 8),
        "component_tiers_15_16_1_4_3": tier_counts == {"PARADIGM_CORE15": 15, "RECURRENT_RULE_STRIP": 16, "BOUND_VARIANT": 1, "LOCAL_SINGLETON": 4, "MEMORIZED_WHOLE_COMMAND": 3},
        "card_tiers_165_1_4_3": card_tiers == {"PRODUCTIVE_RECIPE": 165, "BOUND_VARIANT_PLUS_RULES": 1, "LOCAL_SINGLETON_PLUS_RULES": 4, "MEMORIZED_WHOLE_CARD": 3},
        "event_tiers_372_1_4_4": event_tiers == {"PRODUCTIVE_RECIPE": 372, "BOUND_VARIANT_PLUS_RULES": 1, "LOCAL_SINGLETON_PLUS_RULES": 4, "MEMORIZED_WHOLE_CARD": 4},
        "all_rebuilds_exact": all(row["exact_semantic_rebuild"] == "YES" for row in cards) and all(row["exact_semantic_rebuild"] == "YES" for row in events) and all(row["semantic_rebuild"] == "PASS" for row in statements),
        "core_coverage_161_358_76_237": (sum(row["core15_touch"] == "YES" for row in cards), sum(row["core15_touch"] == "YES" for row in events), sum(row["fully_core15"] == "YES" for row in cards), sum(next(card["fully_core15"] for card in cards if card["exact_card_id"] == row["exact_card_id"]) == "YES" for row in events)) == (161, 358, 76, 237),
        "whole_cards_exact": {(row["component_recipe"], row["whole_reading_de"]) for row in whole} == {("OS", "FACH"), ("RESUME_CARD", "WIEDERAUFNEHMEN"), ("TALAM", "VERWAHREN")},
        "predictions_unattested": all(row["attested_on_fixed_pages"] == "NO" and row["use_status"] == "PREDICTION_ONLY__KEEP_OUT_OF_381_EDITION" for row in predictions),
        "event_ids_complete": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)],
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for rows in (components, cards, events, statements, whole, predictions, renderer) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["decision"] == "SECOND_GRAMMAR_REPARSES_381_WITH_15_CORE_AXES_AND_THREE_WHOLE_COMMANDS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_NINETY_NINTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
