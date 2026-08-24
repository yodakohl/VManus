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
    transitions = read("FOUR_HUNDRED_EIGHTY_EIGHTH_TEN_OBJECT_TRANSITIONS.tsv")
    atlas = read("FOUR_HUNDRED_EIGHTY_EIGHTH_59_LOCAL_ITEM_OBJECT_ATLAS.tsv")
    merges = read("FOUR_HUNDRED_EIGHTY_EIGHTH_THREE_ABSTRACT_MERGE_CANDIDATES.tsv")
    priorities = read("FOUR_HUNDRED_EIGHTY_EIGHTH_TEN_LONG_NOMENCLATOR_PRIORITIES.tsv")
    chains = read("FOUR_HUNDRED_EIGHTY_EIGHTH_26_OBJECT_TRANSITION_CHAINS.tsv")
    checks = {
        "transitions_10": len(transitions) == 10,
        "transition_event_sum_381": sum(int(row["all_prose_events"]) for row in transitions) == 381,
        "atlas_59": len(atlas) == 59,
        "atlas_ids_unique": len({row["local_item_id"] for row in atlas}) == 59,
        "active_carried_only_31": sum(row["object_transition_chain"] == "ACTIVE_CARRIED" for row in atlas) == 31,
        "object_change_items_28": sum(row["object_changes"] != "NONE" for row in atlas) == 28,
        "chains_26": len(chains) == 26,
        "chain_items_59": sum(int(row["local_items"]) for row in chains) == 59,
        "merge_candidates_3": len(merges) == 3,
        "safe_new_merges_zero": sum(row["decision"] == "MERGE" for row in merges) == 0,
        "long_priorities_10": len(priorities) == 10,
        "largest_19": int(priorities[0]["events"]) == 19,
        "sealed_pages_absent": all("f84" not in row["owner_codes"] for row in atlas),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_EIGHTY_EIGHTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
