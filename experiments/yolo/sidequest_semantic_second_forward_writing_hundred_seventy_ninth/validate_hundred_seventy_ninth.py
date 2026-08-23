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
    tokens = read("HUNDRED_SEVENTY_NINTH_16_TOKEN_STOCK_ENCODING.tsv")
    fields = read("HUNDRED_SEVENTY_NINTH_4_FIELD_STOCK_EXERCISE.tsv")
    ambiguities = read("HUNDRED_SEVENTY_NINTH_6_STOCK_AMBIGUITIES.tsv")
    rebuilt = " | ".join(" ".join(row["chosen_visible_surface"] for row in tokens if int(row["field"]) == field) for field in range(1, 5))
    expected = " | ".join(row["visible_card_sequence"] for row in fields)
    checks = {
        "sixteen_tokens": len(tokens) == 16 and [int(row["token_order"]) for row in tokens] == list(range(1, 17)),
        "fifteen_distinct_cards": len({row["master_card_id"] for row in tokens}) == 15,
        "all_surfaces_registered": {row["surface_is_registered"] for row in tokens} == {"YES"},
        "four_new_fields": len(fields) == 4 and {row["sequence_source"] for row in fields} == {"NEW_COMPOSITION"},
        "field_rebuild_exact": rebuilt == expected,
        "three_closed_one_open": [sum(row["field_status"] == status for row in fields) for status in ["CLOSED", "OPEN"]] == [3, 1],
        "only_three_cards_overlap_first": len({row["master_card_id"] for row in tokens if row["also_used_in_first_exercise"] == "YES"}) == 3,
        "six_ambiguities": len(ambiguities) == 6,
        "all_steps_roundtrip": all(row["source_instruction_de"] == row["decoded_step_de"] for row in tokens),
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in tokens),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "visible_sequence": rebuilt}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
