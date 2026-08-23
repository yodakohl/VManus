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
    tokens = read("HUNDRED_SEVENTY_EIGHTH_13_TOKEN_FORWARD_ENCODING.tsv")
    fields = read("HUNDRED_SEVENTY_EIGHTH_5_FIELD_WRITING_EXERCISE.tsv")
    ambiguities = read("HUNDRED_SEVENTY_EIGHTH_7_ROUNDTRIP_AMBIGUITIES.tsv")
    rebuilt = " | ".join(" ".join(row["chosen_visible_surface"] for row in tokens if int(row["field"]) == field) for field in range(1, 6))
    expected = " | ".join(row["visible_card_sequence"] for row in fields)
    checks = {
        "thirteen_tokens": len(tokens) == 13 and [int(row["token_order"]) for row in tokens] == list(range(1, 14)),
        "twelve_distinct_cards": len({row["master_card_id"] for row in tokens}) == 12,
        "all_surfaces_registered": {row["surface_is_registered"] for row in tokens} == {"YES"},
        "five_fields": len(fields) == 5 and [int(row["field"]) for row in fields] == list(range(1, 6)),
        "field_rebuild_exact": rebuilt == expected,
        "three_new_two_exemplar_fields": [sum(row["sequence_source"] == status for row in fields) for status in ["NEW_COMPOSITION", "KNOWN_CADENCE_EXEMPLAR"]] == [3, 2],
        "four_closed_one_open": [sum(row["field_status"] == status for row in fields) for status in ["CLOSED", "OPEN"]] == [4, 1],
        "seven_ambiguities": len(ambiguities) == 7,
        "all_steps_decode": all(row["source_instruction_de"] == row["decoded_step_de"] for row in tokens),
        "no_sealed_tokens": all("f84" not in "\t".join(row.values()).lower() for row in tokens),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "visible_sequence": rebuilt}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
