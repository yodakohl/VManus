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
    events = read("FOUR_HUNDRED_THIRTY_FIFTH_B2_62_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_THIRTY_FIFTH_B2_22_STATEMENTS.tsv")
    transfer = read("FOUR_HUNDRED_THIRTY_FIFTH_FOURTEEN_B1_TRANSFERS.tsv")
    local = read("FOUR_HUNDRED_THIRTY_FIFTH_B2_LOCAL_DECK.tsv")
    zones = read("FOUR_HUNDRED_THIRTY_FIFTH_FIVE_OWNER_ZONES.tsv")
    checks = {
        "events_62": len(events) == 62,
        "event_range": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(167, 229)],
        "statements_22": len(statements) == 22,
        "statement_event_sum": sum(int(row["events"]) for row in statements) == 62,
        "exact_cards_46": len({row["joint_tuple_id"] for row in events}) == 46,
        "B1_transfer_cards_14": len(transfer) == 14,
        "B1_transfer_events_24": sum(int(row["events"]) for row in transfer) == 24,
        "local_cards_32": len(local) == 32,
        "five_owner_zones": len(zones) == 5,
        "sheckhy_predicted": [row["small_value_de"] for row in events if row["surface"] == "sheckhy"] == ["dies kurz durchführen"],
        "carry_marked_once": [row["cross_line_carry"] for row in statements].count("E180_E181_READ_ONCE") == 1,
        "all_values": all(row["small_value_de"] for row in events),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_THIRTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
