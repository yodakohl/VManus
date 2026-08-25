#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FORTIETH"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_fortieth.py")], check=True)
    components = read("39_COMPONENT_CONSTRUCTION_MANUAL.tsv")
    cards = read("10_HIGH_FREQUENCY_CARDS.tsv")
    events = read("127_HIGH_FREQUENCY_EVENTS.tsv")
    statements = read("68_STATEMENT_PORTABLE_SEQUENCES.tsv")
    rules = read("12_APPRENTICE_RULES.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    counts = Counter(row["exact_card_id"] for row in events)
    checks = {
        "component_manual": len(components) == 39 and len({row["component"] for row in components}) == 39 and all(row["short_value_de"] and row["construction_slot"] for row in components),
        "top_card_inventory": len(cards) == 10 and [int(row["frequency_rank"]) for row in cards] == list(range(1, 11)),
        "event_inventory": len(events) == 127 and len({row["event_id"] for row in events}) == 127 and all(counts[row["exact_card_id"]] == int(row["events"]) for row in cards),
        "statement_inventory": len(statements) == 68 and len({row["statement_id"] for row in statements}) == 68,
        "full_scope": len({row["record"] for row in events}) == 11 and len({row["page"] for row in events}) == 7,
        "portable_values_constant": all(len({row["portable_workshop_paraphrase_de"] for row in events if row["exact_card_id"] == card["exact_card_id"]}) == 1 for card in cards),
        "no_page_specific_values": all(row["page_specific_noun"] == "NONE" for row in cards) and all(row["owner_independent"] == "YES" for row in events),
        "exact_y_before_surface": any("dy" in row["surfaces"].split("|") and row["component_recipe"] == "Y" and row["portable_workshop_paraphrase_de"] == "den aktuellen Posten" for row in cards),
        "rule_inventory": len(rules) == 12 and [int(row["priority"]) for row in rules] == list(range(1, 13)),
        "summary": summary["top_events"] == 127 and summary["covered_statements"] == 68 and summary["page_specific_values_added"] == 0 and summary["component_changes"] == 0,
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
