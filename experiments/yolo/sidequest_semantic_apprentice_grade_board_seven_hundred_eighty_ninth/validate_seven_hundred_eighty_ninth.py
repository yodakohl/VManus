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
    cards = read("SEVEN_HUNDRED_EIGHTY_NINTH_6_BOARD_CARDS.tsv")
    traces = read("SEVEN_HUNDRED_EIGHTY_NINTH_12_FORWARD_BACKWARD_TRACES.tsv")
    surfaces = read("SEVEN_HUNDRED_EIGHTY_NINTH_8_SURFACE_COLLISION_AUDIT.tsv")
    rules = read("SEVEN_HUNDRED_EIGHTY_NINTH_6_WRITING_RULES.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_EIGHTY_NINTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "counts_6_12_8_6": (len(cards), len(traces), len(surfaces), len(rules)) == (6, 12, 8, 6),
        "two_hands_per_card": all(sum(row["selected_card"] == card["predicted_card"] for row in traces) == 2 for card in cards),
        "roundtrip_12_of_12": all(row["prompt_roundtrip"] == "PASS" and row["input_prompt_de"] == row["readback_de"] and row["selected_recipe"] == row["readback_recipe"] for row in traces),
        "two_hand_specific_pairs": sum(row["hand_1_surface"] != row["hand_2_surface"] for row in cards) == 2,
        "only_ok_sh_hand_specific": {row["ladder_signature"] for row in cards if row["hand_1_surface"] != row["hand_2_surface"]} == {"OK+Y", "SH+Y"},
        "all_predicted_surfaces_unseen": all(row["fixed_page_occurrences"] == "0" and row["collision_status"] == "UNSEEN_SAFE_PREDICTION" for row in surfaces),
        "no_attested_claim": all(row["status"] == "WORKSHOP_BOARD_ONLY__NOT_MANUSCRIPT_ATTESTED" for row in cards),
        "fixed_pages_sealed": all("f84" not in "\t".join(row.values()).lower() for rows in (cards, traces, surfaces, rules) for row in rows),
        "summary_pass": summary == {
            "status": "PASS",
            "board_cards": 6,
            "forward_backward_traces": 12,
            "unique_predicted_surfaces": 8,
            "fixed_page_collisions": 0,
            "hand_specific_card_pairs": 2,
            "roundtrip_passes": 12,
            "decision": "SIX_GRADE_CARDS_TEACHABLE_WITH_TWO_HAND_ALLOGRAPHS_AND_MASTER_COPY",
        },
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_EIGHTY_NINTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
