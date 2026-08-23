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
    tokens = read("HUNDRED_EIGHTY_FIFTH_25_TOKEN_ZERO_OVERLAP_ENCODING.tsv")
    fields = read("HUNDRED_EIGHTY_FIFTH_5_FIELD_FOURTH_EXERCISE.tsv")
    ambiguities = read("HUNDRED_EIGHTY_FIFTH_6_LOCAL_AMBIGUITIES.tsv")
    cards = read("HUNDRED_EIGHTY_FIFTH_20_CARD_LOW_OVERLAP_INVENTORY.tsv")
    rebuilt = " | ".join(
        " ".join(row["surface"] for row in tokens if int(row["field"]) == field)
        for field in range(1, 6)
    )
    expected = " | ".join(row["visible_sequence"] for row in fields)
    terminal_rows = [row for row in tokens if row["observed_finality_rule"] == "ALWAYS_FIELD_FINAL"]
    checks = {
        "twenty_five_tokens": len(tokens) == 25 and [int(row["token_order"]) for row in tokens] == list(range(1, 26)),
        "twenty_distinct_cards": len(cards) == 20 and len({row["master_card_id"] for row in tokens}) == 20,
        "all_from_shortlist": {row["on_24_card_shortlist"] for row in tokens} == {"YES"},
        "zero_old_palette_overlap": {row["in_previous_25_card_palette"] for row in tokens} == {"NO"} and {row["previous_palette_overlap"] for row in cards} == {"NO"},
        "all_surfaces_registered": {row["surface_is_registered"] for row in tokens} == {"YES"},
        "five_new_fields": len(fields) == 5 and {row["sequence_source"] for row in fields} == {"NEW_COMPOSITION_FROM_UNUSED_SHORTLIST"},
        "one_open_four_closed": Counter(row["field_status"] for row in fields) == Counter({"CLOSED": 4, "OPEN": 1}),
        "field_rebuild_exact": rebuilt == expected,
        "all_terminal_cards_field_final": terminal_rows and {row["field_final"] for row in terminal_rows} == {"YES"},
        "all_six_slots_used": {row["grammar_slot"] for row in tokens} == {f"G{i}" for i in range(1, 7)},
        "all_steps_roundtrip": all(row["source_instruction_de"] == row["decoded_step_de"] for row in tokens),
        "six_ambiguities": len(ambiguities) == 6,
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for table in [tokens, fields, ambiguities, cards] for row in table),
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "visible_sequence": rebuilt,
        "decision": "FOURTH_INSTRUCTION_ROUNDTRIPS_WITH_ZERO_OLD_PALETTE_OVERLAP",
    }
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
