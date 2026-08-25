#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_FORTY_FIRST"


def read(suffix: str) -> list[dict[str, str]]:
    with (HERE / f"{PREFIX}_{suffix}").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_forty_first.py")], check=True)
    cards = read("10_SECOND_TIER_CARDS.tsv")
    events = read("59_SECOND_TIER_EVENTS.tsv")
    statements = read("40_SECOND_TIER_STATEMENTS.tsv")
    coverage = read("7_PAGE_TOP20_COVERAGE.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    counts = Counter(row["exact_card_id"] for row in events)
    checks = {
        "tier_card_inventory": len(cards) == 10 and [int(row["frequency_rank"]) for row in cards] == list(range(11, 21)),
        "tier_event_inventory": len(events) == 59 and len({row["event_id"] for row in events}) == 59 and all(counts[row["exact_card_id"]] == int(row["events"]) for row in cards),
        "tier_statement_inventory": len(statements) == 40 and len({row["statement_id"] for row in statements}) == 40,
        "tier_scope": len({row["page"] for row in events}) == 7 and len({row["record"] for row in events}) == 9,
        "portable_values_constant": all(len({row["portable_workshop_paraphrase_de"] for row in events if row["exact_card_id"] == card["exact_card_id"]}) == 1 for card in cards),
        "no_page_specific_values": all(row["page_specific_noun"] == "NONE" for row in cards) and all(row["owner_independent"] == "YES" for row in events),
        "ckh_ellipse_preserved": any(row["component_recipe"] == "CKH+Y" and row["portable_workshop_paraphrase_de"] == "Durchlass fuer den Posten" for row in cards),
        "cumulative_coverage": len(coverage) == 7 and sum(int(row["top20_events"]) for row in coverage) == 186 and summary["cumulative_top20_events"] == 186,
        "no_component_change": summary["component_changes"] == 0,
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
