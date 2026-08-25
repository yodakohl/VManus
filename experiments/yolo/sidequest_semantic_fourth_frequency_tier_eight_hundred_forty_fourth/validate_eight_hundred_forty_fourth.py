#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FORTY_FOURTH"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_forty_fourth.py")], check=True)
    cards = read("20_FOURTH_TIER_CARDS.tsv")
    events = read("31_FOURTH_TIER_EVENTS.tsv")
    statements = read("28_FOURTH_TIER_STATEMENTS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    counts = Counter(row["exact_card_id"] for row in events)
    checks = {
        "tier_inventory": len(cards) == 20 and len(events) == 31 and len(statements) == 28,
        "frequency_ranks": [int(row["frequency_rank"]) for row in cards] == list(range(41, 61)),
        "fully_compositional": all(row["card_tier"] == "FULLY_CORE33_RECIPE" and row["learning_mode"] == "COMPOSE_COMPONENTS" for row in cards),
        "event_counts": len({row["event_id"] for row in events}) == 31 and all(counts[row["exact_card_id"]] == int(row["events"]) for row in cards),
        "portable_values_constant": all(len({row["portable_workshop_paraphrase_de"] for row in events if row["exact_card_id"] == card["exact_card_id"]}) == 1 for card in cards),
        "long_card_composed": any(row["component_recipe"] == "CH+EE+CKH+O+DY" and row["portable_workshop_paraphrase_de"] == "lang durch den Durchlass im Arbeitsgang entnehmen und schliessen" for row in cards),
        "full_scope": len({row["page"] for row in events}) == 7 and len({row["record"] for row in events}) == 10,
        "cumulative_coverage": summary["cumulative_top60_events"] == 268,
        "no_exceptions": summary["bound_cards"] == 0 and summary["whole_cards"] == 0,
        "no_component_change": summary["component_changes"] == 0 and summary["page_specific_values_added"] == 0,
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
