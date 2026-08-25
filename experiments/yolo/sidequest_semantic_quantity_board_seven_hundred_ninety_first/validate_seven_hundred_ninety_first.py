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
    cards = read("SEVEN_HUNDRED_NINETY_FIRST_14_QUANTITY_BOARD_CARDS.tsv")
    traces = read("SEVEN_HUNDRED_NINETY_FIRST_28_TWO_HAND_TRACES.tsv")
    substitutions = read("SEVEN_HUNDRED_NINETY_FIRST_14_SENTENCE_SUBSTITUTIONS.tsv")
    rules = read("SEVEN_HUNDRED_NINETY_FIRST_5_QUANTITY_RULES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_NINETY_FIRST_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_14_28_14_5": (len(cards), len(traces), len(substitutions), len(rules)) == (14, 28, 14, 5),
        "two_hands_each": all(sum(row["selected_card"] == card["predicted_card"] for row in traces) == 2 for card in cards),
        "roundtrip_28": all(row["roundtrip"] == "PASS" and row["input_reading_de"] == row["readback_reading_de"] for row in traces),
        "master_copy_only": all(row["access"] == "COPY_NEW_MASTER_CARD" for row in traces),
        "one_surface_change_per_sentence": all("→" in row["changed_surface_only"] and "→" in row["changed_meaning_only"] for row in substitutions),
        "both_quantity_values": {row["quantity_value"] for row in cards} == {"SOLLMASS", "PORTION"},
        "no_attested_claim": all(row["status"] == "WORKSHOP_BOARD_ONLY__NOT_MANUSCRIPT_ATTESTED" for row in cards),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for rows in (cards, traces, substitutions, rules) for row in rows),
        "summary_pass": summary == {
            "status": "PASS",
            "board_cards": 14,
            "two_hand_traces": 28,
            "sentence_substitutions": 14,
            "roundtrip_passes": 28,
            "hand_specific_variants_invented": 0,
            "decision": "AIIN_AIN_COUNTERPARTS_REWRITE_ONE_QUANTITY_SLOT_INTACT",
        },
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_NINETY_FIRST_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
