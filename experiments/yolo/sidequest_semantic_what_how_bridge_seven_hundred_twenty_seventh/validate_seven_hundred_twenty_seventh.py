#!/usr/bin/env python3
"""Validate Pass 727 WHAT/HOW bridge."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = read("SEVEN_HUNDRED_TWENTY_SEVENTH_17_SHARED_CARDS.tsv")
    bigrams = read("SEVEN_HUNDRED_TWENTY_SEVENTH_6_SHARED_BIGRAMS.tsv")
    trigrams = read("SEVEN_HUNDRED_TWENTY_SEVENTH_1_SHARED_TRIGRAM.tsv")
    registers = read("SEVEN_HUNDRED_TWENTY_SEVENTH_11_REGISTER_BINDING.tsv")
    pairs = read("SEVEN_HUNDRED_TWENTY_SEVENTH_30_PAIRING_MATRIX.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_TWENTY_SEVENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "shared_cards_17": len(cards) == 17,
        "shared_bigrams_6": len(bigrams) == 6,
        "shared_trigram_one": len(trigrams) == 1,
        "trigram_is_y_aiin_y": len(trigrams) == 1 and trigrams[0]["component_sequence"] == "Y>AIIN>Y",
        "trigram_h2_b3_exact": "H2-S001:E021,E022,E023" in trigrams[0]["herbal_occurrence"] and "B3-S003:E232,E233,E234" in trigrams[0]["bio_occurrence"],
        "registers_5_plus_6": len(registers) == 11 and sum(row["register"] == "HERBAL_WHAT" for row in registers) == 5 and sum(row["register"] == "BIOLOGICAL_HOW" for row in registers) == 6,
        "events_100_plus_281": sum(int(row["events"]) for row in registers if row["register"] == "HERBAL_WHAT") == 100 and sum(int(row["events"]) for row in registers if row["register"] == "BIOLOGICAL_HOW") == 281,
        "pairings_30": len(pairs) == 30 and len({(row["herbal_record"], row["bio_record"]) for row in pairs}) == 30,
        "only_h2_b3_has_trigram": [(row["herbal_record"], row["bio_record"]) for row in pairs if int(row["shared_trigrams"])] == [("H2", "B3")],
        "no_fourgram": summary["shared_fourgrams"] == 0 and all(int(row["shared_fourgrams"]) == 0 for row in pairs),
        "no_direct_pointer": summary["direct_cross_references"] == 0 and all(row["direct_cross_reference"] == "NONE" for row in registers) and all("NO_DIRECT_CROSS_REFERENCE" in row["decision"] for row in pairs),
        "form_unchanged": summary["form_changes"] == 0,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_TWENTY_SEVENTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
