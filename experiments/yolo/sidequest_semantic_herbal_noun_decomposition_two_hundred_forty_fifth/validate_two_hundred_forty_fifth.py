#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    cards = rows("TWO_HUNDRED_FORTY_FIFTH_24_NOUN_CARDS.tsv")
    occurrences = rows("TWO_HUNDRED_FORTY_FIFTH_28_NOUN_OCCURRENCES.tsv")
    lexemes = rows("TWO_HUNDRED_FORTY_FIFTH_13_LEARNED_NOUN_CORES.tsv")
    dictionary = rows("TWO_HUNDRED_FORTY_FIFTH_FINAL_66_CARD_HERBAL_DICTIONARY.tsv")
    cc, ec = Counter(r["composition_status"] for r in cards), Counter(r["composition_status"] for r in occurrences)
    checks = {
        "24_noun_cards": len(cards) == 24,
        "28_noun_occurrences": len(occurrences) == 28,
        "card_split_8_8_8": cc == {"FULL_COMPOSITION": 8, "PARTIAL_COMPOSITION": 8, "LEARNED_WHOLE_NOUN": 8},
        "event_split_9_8_11": ec == {"FULL_COMPOSITION": 9, "PARTIAL_COMPOSITION": 8, "LEARNED_WHOLE_NOUN": 11},
        "13_learned_cores": len(lexemes) == 13,
        "66_final_cards": len(dictionary) == 66,
        "all_values_concrete": all(r["revised_default_de"].strip() for r in dictionary),
        "all_noun_cards_mapped_once": len({r["master_card_id"] for r in cards}) == 24,
        "only_fixed_pages": {r["page"] for r in occurrences} <= {"f10r", "f11r", "f55v", "f56r"},
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in occurrences),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
