#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    primitives = read("FIVE_HUNDRED_THIRTY_SIXTH_EIGHT_PRIMITIVE_WORKSHOP_WORDS.tsv")
    cards = read("FIVE_HUNDRED_THIRTY_SIXTH_ONE_HUNDRED_SEVENTY_THREE_COMMON_CARD_GRAMMAR.tsv")
    events = read("FIVE_HUNDRED_THIRTY_SIXTH_THREE_HUNDRED_EIGHTY_ONE_COMMON_GRAMMAR_INTERLINEAR.tsv")
    statements = read("FIVE_HUNDRED_THIRTY_SIXTH_ONE_HUNDRED_SIXTEEN_STATEMENT_GRAMMAR.tsv")
    transitions = read("FIVE_HUNDRED_THIRTY_SIXTH_ATTESTED_LANE_TRANSITIONS.tsv")
    owners = read("FIVE_HUNDRED_THIRTY_SIXTH_TWENTY_IMAGE_SUPPLIED_OWNER_NOUNS.tsv")
    by_card = defaultdict(set)
    for row in events:
        by_card[row["card_no"]].add(row["card_reading_de"])
    checks = {
        "primitives8": len(primitives) == 8 and sum(int(row["total_atoms"]) for row in primitives) == 470,
        "primitive_counts": {row["primitive"]: int(row["total_atoms"]) for row in primitives} == {"ACTIVATE_CHARGE": 85, "CONTINUE_USE": 46, "SOURCE_DRAW": 21, "METER_CHECK": 42, "TARGET_HANDOFF": 33, "MOVE_PASS": 49, "HOLD_STATE": 105, "CLOSE": 89},
        "all_primitives_cross_sections": all(row["portable_across_sections"] == "YES" for row in primitives),
        "cards173": len(cards) == 173 and len({row["card_no"] for row in cards}) == 173,
        "shared_cards17": sum(row["shared_herbal_biological"] == "YES" for row in cards) == 17,
        "events381": len(events) == 381 and [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(1, 382)],
        "section_counts100_281": Counter("HERBAL" if row["record"].startswith("H") else "BIOLOGICAL" for row in events) == Counter({"HERBAL": 100, "BIOLOGICAL": 281}),
        "statements116": len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116,
        "statement_event_partition": sum(len(row["event_ids"].split("|")) for row in statements) == 381,
        "closed89_open27": Counter(row["terminal"] for row in statements) == Counter({"YES": 89, "NO": 27}),
        "owners20": len(owners) == 20 and sum(int(row["events"]) for row in owners) == 381,
        "owner_sections4_16": Counter(row["section"] for row in owners) == Counter({"HERBAL": 4, "BIOLOGICAL": 16}),
        "transition_use_total586": sum(int(row["total_uses"]) for row in transitions) == 586,
        "invariant_card_values": all(len(values) == 1 for values in by_card.values()),
        "all_events_parsed": all(row["grammar_lanes"] and row["workshop_words_de"] for row in events),
        "no_card_claims_noun": all(row["semantic_noun_carried_by_card"] == "NO__OPERATION_OR_CONTROL_ONLY" for row in cards),
        "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["locus"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_THIRTY_SIXTH_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
