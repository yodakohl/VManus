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
    components = rows("TWO_HUNDRED_FIFTY_EIGHTH_30_PRODUCTIVE_COMPONENTS.tsv")
    whole = rows("TWO_HUNDRED_FIFTY_EIGHTH_23_WHOLE_SIGNS.tsv")
    generation = rows("TWO_HUNDRED_FIFTY_EIGHTH_173_CARD_GENERATION.tsv")
    deck = rows("TWO_HUNDRED_FIFTY_EIGHTH_53_ENTRY_APPRENTICE_DECK.tsv")
    card_counts = Counter(r["construction_class"] for r in generation)
    event_counts = Counter()
    for row in generation:
        event_counts[row["construction_class"]] += int(row["prose_event_count"])
    checks = {
        "30_components": len(components) == 30 and len({r["component"] for r in components}) == 30,
        "23_whole_signs": len(whole) == 23 and len({r["master_card_id"] for r in whole}) == 23,
        "53_deck_entries": len(deck) == 53 and len({r["deck_order"] for r in deck}) == 53,
        "173_cards": len(generation) == 173 and len({r["master_card_id"] for r in generation}) == 173,
        "card_split": card_counts == {"PRODUCTIVE_COMPOSITION": 118, "FRAME_PLUS_LOCAL_CORE": 32, "WHOLE_SIGN": 23},
        "event_split": event_counts == {"PRODUCTIVE_COMPOSITION": 194, "FRAME_PLUS_LOCAL_CORE": 159, "WHOLE_SIGN": 28},
        "353_component_help_events": event_counts["PRODUCTIVE_COMPOSITION"] + event_counts["FRAME_PLUS_LOCAL_CORE"] == 353,
        "four_lexical_blockers": sum(r["whole_sign_role"] == "LEXICAL_BLOCKER" for r in whole) == 4,
        "quantity_triplet_present": {"AIN", "AN", "AIIN"} <= {r["component"] for r in components},
        "six_relations_present": {"AR", "AL", "OL", "OT", "OR", "Y"} <= {r["component"] for r in components},
        "no_empty_values": all(r["short_value_de"].strip() for r in deck),
        "sealed_pages_absent": all("f84" not in "\t".join(r.values()).lower() for r in generation),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(1)
    print(f"PASS {sum(checks.values())}/{len(checks)}")


if __name__ == "__main__":
    main()
