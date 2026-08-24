#!/usr/bin/env python3

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


events = rows("THREE_HUNDRED_THIRTY_NINTH_1524_RENDERED_EVENTS.tsv")
statements = rows("THREE_HUNDRED_THIRTY_NINTH_464_RENDERED_STATEMENTS.tsv")
profiles = rows("THREE_HUNDRED_THIRTY_NINTH_FOUR_CORPUS_PROFILES.tsv")
hands = {row["hand_id"] for row in profiles}
checks = {
    "four_hands": len(hands) == 4 and len(profiles) == 4,
    "one_thousand_five_hundred_twenty_four_events": len(events) == 1524,
    "three_hundred_eighty_one_per_hand": all(sum(row["hand_id"] == hand for row in events) == 381 for hand in hands),
    "four_hundred_sixty_four_statements": len(statements) == 464,
    "one_hundred_sixteen_statements_per_hand": all(sum(row["hand_id"] == hand for row in statements) == 116 for hand in hands),
    "all_identities_match": all(row["identity_match"] == "YES" for row in events),
    "all_values_preserved": all(row["value_preserved"] == "YES" for row in events),
    "all_slots_preserved": all(row["slot_preserved"] == "YES" for row in events),
    "all_boundaries_preserved": all(row["boundary_preserved"] == "YES" for row in events),
    "all_173_surfaces_per_hand": all(int(row["unique_surface_types"]) == 173 for row in profiles),
    "four_distinct_profiles": len({row["corpus_surface_sha256"] for row in profiles}) == 4,
    "profile_metrics_differ": len({(row["q_initial_events"], row["s_sh_initial_events"], row["ch_t_initial_events"], row["mean_surface_length"]) for row in profiles}) == 4,
    "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
    "sealed_absent": all(row["page"] not in {"f84", "f84r"} for row in events),
}
result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
(HERE / "THREE_HUNDRED_THIRTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if result["status"] != "PASS":
    raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
print("PASS", len(checks), "checks")
