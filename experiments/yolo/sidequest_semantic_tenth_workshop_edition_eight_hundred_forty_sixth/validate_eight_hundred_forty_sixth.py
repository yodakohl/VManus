#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FORTY_SIXTH"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_forty_sixth.py")], check=True)
    components = read("39_COMPONENT_MANUAL.tsv")
    cards = read("173_CARD_DICTIONARY.tsv")
    events = read("381_EVENT_INTERLINEAR.tsv")
    statements = read("116_STATEMENT_EDITION.tsv")
    rules = read("12_APPRENTICE_RULES.tsv")
    exceptions = read("6_EXCEPTION_CARDS.tsv")
    active = read("30_ACTIVE_PREDICTION_SURFACES.tsv")
    supplement = read("5_SUPPLEMENTAL_PREDICTIONS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_card = {row["exact_card_id"]: row for row in cards}
    event_counts = Counter(row["exact_card_id"] for row in events)
    checks = {
        "complete_inventory": len(components) == 39 and len(cards) == 173 and len(events) == 381 and len(statements) == 116 and len(rules) == 12,
        "unique_ids": len({row["exact_card_id"] for row in cards}) == 173 and len({row["event_id"] for row in events}) == 381 and len({row["statement_id"] for row in statements}) == 116,
        "card_event_counts": all(event_counts[row["exact_card_id"]] == int(row["events"]) for row in cards),
        "event_dictionary_match": all(row["tenth_edition_reading_de"] == by_card[row["exact_card_id"]]["tenth_edition_reading_de"] and row["learning_mode"] == by_card[row["exact_card_id"]]["learning_mode"] for row in events),
        "learning_mode_cards": Counter(row["learning_mode"] for row in cards) == Counter({"COMPOSE_COMPONENTS": 167, "MEMORIZE_BOUND_FRAME": 3, "MEMORIZE_WHOLE_CARD": 3}),
        "learning_mode_events": Counter(row["learning_mode"] for row in events) == Counter({"COMPOSE_COMPONENTS": 374, "MEMORIZE_BOUND_FRAME": 3, "MEMORIZE_WHOLE_CARD": 4}),
        "exception_inventory": len(exceptions) == 6,
        "water_alignment": all("fluessigkeit" not in row["working_reading_de"].lower() for row in statements) and sum("AIR" in [token for recipe in row["component_sequence"].split(" | ") for token in recipe.split("+")] for row in statements) == 5 and sum("wasser" in row["working_reading_de"].lower() and "AIR" in [token for recipe in row["component_sequence"].split(" | ") for token in recipe.split("+")] for row in statements) == 5,
        "core_values": next(row for row in components if row["component"] == "O")["short_value_de"] == "ARBEITSGANG" and next(row for row in components if row["component"] == "Y")["short_value_de"] == "POSTEN" and next(row for row in components if row["component"] == "AIR")["short_value_de"] == "WASSER",
        "record_inventory": len({row["record"] for row in statements}) == 11,
        "prediction_inventory": len(active) == 30 and len({row["component_recipe"] for row in active}) == 24 and len(supplement) == 5,
        "supplement_identity": {row["predicted_surface"] for row in supplement} == {"aiiin", "qokaiiin", "ykaiiin", "cheeeky", "solkeeey"},
        "allowed_pages": {row["page"] for row in events + statements} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
