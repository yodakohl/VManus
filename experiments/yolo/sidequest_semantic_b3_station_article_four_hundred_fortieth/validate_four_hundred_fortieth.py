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
    events = read("FOUR_HUNDRED_FORTIETH_B3_86_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_FORTIETH_B3_34_STATEMENTS.tsv")
    transfer = read("FOUR_HUNDRED_FORTIETH_TWENTY_SIX_B1_B2_TRANSFERS.tsv")
    local = read("FOUR_HUNDRED_FORTIETH_B3_LOCAL_DECK.tsv")
    zones = read("FOUR_HUNDRED_FORTIETH_THREE_B3_OWNER_ZONES.tsv")
    checks = {
        "events_86": len(events) == 86,
        "event_range": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(229, 315)],
        "statements_34": len(statements) == 34,
        "statement_event_sum": sum(int(row["events"]) for row in statements) == 86,
        "exact_cards_52": len({row["joint_tuple_id"] for row in events}) == 52,
        "transfer_cards_26": len(transfer) == 26,
        "transfer_events_54": sum(int(row["events"]) for row in transfer) == 54,
        "local_cards_26": len(local) == 26,
        "local_events_32": sum(int(row["events"]) for row in local) == 32,
        "zones_3": len(zones) == 3,
        "two_owner_break_statements": sum(row["owner_break_inside_statement"] == "YES" for row in statements) == 2,
        "breaks_are_S016_S026": {row["statement_id"] for row in statements if row["owner_break_inside_statement"] == "YES"} == {"B3-S016", "B3-S026"},
        "all_values": all(row["small_value_de"] for row in events),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FORTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
