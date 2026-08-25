#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FORTY_SECOND"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_forty_second.py")], check=True)
    cards = read("10_THIRD_TIER_CARDS.tsv")
    events = read("31_THIRD_TIER_EVENTS.tsv")
    statements = read("29_THIRD_TIER_STATEMENTS.tsv")
    boundary = read("5_WHOLE_CARD_BOUNDARY_ROWS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    counts = Counter(row["exact_card_id"] for row in events)
    checks = {
        "tier_card_inventory": len(cards) == 10 and [int(row["frequency_rank"]) for row in cards] == list(range(21, 31)),
        "tier_fully_compositional": all(row["card_tier"] == "FULLY_CORE33_RECIPE" for row in cards),
        "tier_event_inventory": len(events) == 31 and len({row["event_id"] for row in events}) == 31 and all(counts[row["exact_card_id"]] == int(row["events"]) for row in cards),
        "tier_statement_inventory": len(statements) == 29 and len({row["statement_id"] for row in statements}) == 29,
        "tier_scope": len({row["page"] for row in events}) == 5 and len({row["record"] for row in events}) == 7,
        "portable_values_constant": all(len({row["portable_workshop_paraphrase_de"] for row in events if row["exact_card_id"] == card["exact_card_id"]}) == 1 for card in cards),
        "boundary_inventory": len(boundary) == 5 and [int(row["frequency_rank"]) for row in boundary] == list(range(31, 36)),
        "first_whole_card": sum(row["learned_whole_card_required"] == "YES" for row in boundary) == 1 and next(row for row in boundary if row["learned_whole_card_required"] == "YES")["frequency_rank"] == "35" and next(row for row in boundary if row["learned_whole_card_required"] == "YES")["surfaces"] == "dchol|schol",
        "cumulative_coverage": summary["cumulative_top30_events"] == 217,
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
