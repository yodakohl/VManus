#!/usr/bin/env python3
"""Validate Pass 703 existing-card phrasebook."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    phrases = read("SEVEN_HUNDRED_THIRD_24_PROMPT_PHRASEBOOK.tsv")
    missing = read("SEVEN_HUNDRED_THIRD_8_MISSING_CARD_PARAPHRASES.tsv")
    checks = {
        "prompts_24": len(phrases) == 24,
        "prompt_ids_unique": len({row["prompt_id"] for row in phrases}) == 24,
        "missing_8": len(missing) == 8,
        "direct_16": sum(row["encoding_mode"] == "DIRECT_EXISTING_CARD" for row in phrases) == 16,
        "expanded_one_1": sum(row["encoding_mode"] == "EXPANDED_EXISTING_CARD" for row in phrases) == 1,
        "two_card_7": sum(row["encoding_mode"] == "TWO_EXISTING_CARD_PARAPHRASE" for row in phrases) == 7,
        "all_requested_components_covered": all(row["requested_components_covered"] == "YES" for row in phrases),
        "no_new_cards_or_surfaces": all(row["new_card_or_surface_invented"] == "NO" for row in phrases),
        "one_or_two_cards": all(int(row["card_count"]) in {1, 2} for row in phrases),
        "all_have_surfaces": all(bool(row["selected_surface_families"]) for row in phrases),
        "all_have_fluent_reading": all(bool(row["fluent_paraphrase_de"]) for row in phrases),
        "seven_new_pairings_split_or_licensed": all(row["boundary_rule"] in {"NEW_STATEMENT_RESET", "ATTESTED_COMPONENT_JUNCTION"} for row in phrases if row["card_count"] == "2"),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_THIRD_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
