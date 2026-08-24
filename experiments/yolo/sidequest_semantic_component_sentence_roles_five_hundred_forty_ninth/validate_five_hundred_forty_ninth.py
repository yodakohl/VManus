#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    components = read("FIVE_HUNDRED_FORTY_NINTH_THIRTY_EIGHT_COMPONENT_ROLES.tsv")
    cards = read("FIVE_HUNDRED_FORTY_NINTH_ONE_HUNDRED_SEVENTY_THREE_CARD_ROLE_PROFILES.tsv")
    events = read("FIVE_HUNDRED_FORTY_NINTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_ROLE_EDITION.tsv")
    card_by_id = {row["card_no"]: row for row in cards}
    checks = {
        "components38": len(components) == 38 and len({row["component"] for row in components}) == 38,
        "cards173": len(cards) == 173 and len(card_by_id) == 173,
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "all_components_known": all(all(component in {row["component"] for row in components} for component in card["component_parse"].split("+")) for card in cards),
        "all_roles_present": all(row["role_signature"] and row["clause_type"] for row in cards),
        "card_event_agreement": all(row["clause_type"] == card_by_id[row["card_no"]]["clause_type"] and row["role_based_reading_de"] == card_by_id[row["card_no"]]["role_based_reading_de"] for row in events),
        "action_events237": Counter(row["clause_type"] for row in events)["ACTION_CLAUSE"] == 237,
        "non_action_events144": sum(row["clause_type"] != "ACTION_CLAUSE" for row in events) == 144,
        "item_not_verb": next(row for row in components if row["component"] == "Y")["is_independent_full_verb"] == "NO",
        "quantity_not_verb": all(next(row for row in components if row["component"] == c)["is_independent_full_verb"] == "NO" for c in ("AIIN", "AIN")),
        "components_unchanged": all(row["component_values_unchanged"] == "YES" for row in events),
        "fixed_pages_only": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FORTY_NINTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
