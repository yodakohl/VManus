#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    events = read("FOUR_HUNDRED_FORTY_THIRD_B4_47_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_FORTY_THIRD_B4_16_STATEMENTS.tsv")
    transfer = read("FOUR_HUNDRED_FORTY_THIRD_NINETEEN_B1_B2_B3_TRANSFERS.tsv")
    local = read("FOUR_HUNDRED_FORTY_THIRD_FIFTEEN_B4_LOCAL_CARDS.tsv")
    zones = read("FOUR_HUNDRED_FORTY_THIRD_TWO_B4_OWNER_ZONES.tsv")
    checks = {
        "events_47": len(events) == 47,
        "event_range": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(315, 362)],
        "statements_16": len(statements) == 16,
        "statement_event_sum": sum(int(row["events"]) for row in statements) == 47,
        "cards_34": len({row["joint_tuple_id"] for row in events}) == 34,
        "transfer_cards_19": len(transfer) == 19,
        "transfer_events_32": sum(int(row["events"]) for row in transfer) == 32,
        "local_cards_15": len(local) == 15,
        "local_events_15": sum(int(row["events"]) for row in local) == 15,
        "zones_2": len(zones) == 2,
        "one_owner_break": [row["statement_id"] for row in statements if row["owner_break_inside_statement"] == "YES"] == ["B4-S015"],
        "every_value": all(row["small_value_de"] for row in events),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FORTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
