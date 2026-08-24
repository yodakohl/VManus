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
    deck = read("THREE_HUNDRED_NINETIETH_16_CARD_FUNCTIONAL_DECK.tsv")
    drawers = read("THREE_HUNDRED_NINETIETH_THREE_FUNCTIONAL_DRAWERS.tsv")
    edges = read("THREE_HUNDRED_NINETIETH_FUNCTIONAL_PROCESS_EDGES.tsv")
    checks = {
        "sixteen_cards": len(deck) == 16,
        "thirty_occurrences": sum(int(row["occurrences"]) for row in deck) == 30,
        "three_drawers": len(drawers) == 3,
        "drawer_partition": Counter(row["functional_family"] for row in deck) == {"TARGET_RESULT": 4, "SEPARATION": 6, "RECEIVE_STORE": 6},
        "drawer_counts_match": all(int(row["member_cards"]) == Counter(card["functional_family"] for card in deck)[row["functional_family"]] for row in drawers),
        "ten_edges": len(edges) == 10,
        "no_spelling_requirement": all(row["surface_segmentation_required_for_family_membership"] == "NO" for row in deck),
        "all_short_values": all(row["short_value_de"] for row in deck),
        "whole_and_composed_mix": {row["architecture"] for row in deck} == {"WHOLE_CARD", "COMPONENT_CARD", "COMPOUND_CARD"},
        "core_rest_present": {row["surface_family"] for row in deck} >= {"lcheey", "cphy", "talam"},
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"status": status, "checks": checks, "check_count": len(checks)}
    (HERE / "THREE_HUNDRED_NINETIETH_VALIDATION.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if status != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
