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
    components = rows("TWO_HUNDRED_SIXTY_FOURTH_40_COMPONENTS.tsv")
    whole = rows("TWO_HUNDRED_SIXTY_FOURTH_23_WHOLE_SIGNS.tsv")
    closure = rows("TWO_HUNDRED_SIXTY_FOURTH_32_LOCAL_CORE_CLOSURES.tsv")
    generation = rows("TWO_HUNDRED_SIXTY_FOURTH_173_COMPLETE_GENERATION.tsv")
    deck = rows("TWO_HUNDRED_SIXTY_FOURTH_63_ENTRY_COMPLETE_DECK.tsv")
    classes = Counter(r["new_generation_class"] for r in generation)
    events = Counter()
    for row in generation:
        events[row["new_generation_class"]] += int(row["prose_event_count"])
    checks = {
        "40_components": len(components) == 40 and len({r["component_id"] for r in components}) == 40,
        "30_shared_10_local": sum(r["component_tier"] == "SHARED_PRODUCTIVE" for r in components) == 30 and sum(r["component_tier"] == "LICENSED_LOCAL_CORE" for r in components) == 10,
        "23_whole": len(whole) == 23 and len({r["master_card_id"] for r in whole}) == 23,
        "32_closures": len(closure) == 32 and len({r["master_card_id"] for r in closure}) == 32,
        "63_deck": len(deck) == 63 and len({r["deck_order"] for r in deck}) == 63,
        "173_generation": len(generation) == 173 and len({r["master_card_id"] for r in generation}) == 173,
        "card_split_150_23": classes == {"GENERATED_FROM_FORTY_COMPONENTS": 150, "MEMORIZED_WHOLE_SIGN": 23},
        "event_split_353_28": events == {"GENERATED_FROM_FORTY_COMPONENTS": 353, "MEMORIZED_WHOLE_SIGN": 28},
        "all_old_mixed_closed": all(r["closure_route"] in {"NEW_LICENSED_CORE", "ALREADY_COVERED_BY_SHARED_COMPONENTS"} for r in closure),
        "ten_new_component_ids": {r["component_id"] for r in components if r["component_tier"] == "LICENSED_LOCAL_CORE"} == {"CHO_INPUT", "O_WITHDRAW", "OS_RECEIVER", "CH_POUR", "TCH_PREPARATION", "OYK_VESSEL", "K_BINDER", "YTY_PART", "SHFY_DURATION", "D_PREVIOUS"},
        "no_uncounted_residual": all(r["new_generation_class"] == "MEMORIZED_WHOLE_SIGN" or r["generation_rule"].strip() for r in generation),
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
