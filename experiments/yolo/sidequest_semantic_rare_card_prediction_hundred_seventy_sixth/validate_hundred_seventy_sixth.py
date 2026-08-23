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
    rare = read("HUNDRED_SEVENTY_SIXTH_143_RARE_CARD_PREDICTIONS.tsv")
    atoms = read("HUNDRED_SEVENTY_SIXTH_29_ATOM_SUPPORT.tsv")
    exceptions = read("HUNDRED_SEVENTY_SIXTH_19_EXCEPTION_DECK.tsv")
    showcase = read("HUNDRED_SEVENTY_SIXTH_10_SHOWCASE_PREDICTIONS.tsv")
    status = Counter(row["prediction_status"] for row in rare)
    checks = {
        "rare_143": len(rare) == 143 and len({row["master_card_id"] for row in rare}) == 143,
        "rare_events_164": sum(int(row["event_count"]) for row in rare) == 164,
        "status_partition": status == Counter({"FULLY_COMPOSED_FROM_OTHER_CARDS": 124, "COMPOSED_FRAME_PLUS_MEMORIZED_BODY": 11, "MEMORIZED_WHOLE_CARD": 8}),
        "exception_deck_19": len(exceptions) == 19 and all(row["prediction_status"] != "FULLY_COMPOSED_FROM_OTHER_CARDS" for row in exceptions),
        "atoms_29": len(atoms) == 29 and all(int(row["card_support"]) >= 2 for row in atoms),
        "ten_showcases": len(showcase) == 10 and all(row["components"] != "NONE" for row in showcase),
        "full_cards_have_external_support": all("NONE" not in row["other_card_support_by_atom"] and all(int(pair.split(":")[1]) >= 1 for pair in row["other_card_support_by_atom"].split("|")) for row in rare if row["prediction_status"] == "FULLY_COMPOSED_FROM_OTHER_CARDS"),
        "no_empty_values": all(row["current_value_de"].strip() and row["predicted_component_gloss_de"].strip() for row in rare),
        "sealed_absent": all("f84" not in row["records"].lower() for row in rare),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
