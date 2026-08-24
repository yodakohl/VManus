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
    events = read("FOUR_HUNDRED_FORTY_FIFTH_B5_B6_20_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_FORTY_FIFTH_FOUR_STATEMENTS.tsv")
    transfers = read("FOUR_HUNDRED_FORTY_FIFTH_EIGHT_PRIOR_TRANSFERS.tsv")
    new = read("FOUR_HUNDRED_FORTY_FIFTH_EIGHT_NEW_CARDS.tsv")
    checks = {
        "events_20": len(events) == 20,
        "event_ids_e362_e381": [row["event_id"] for row in events] == [f"E{n}" for n in range(362, 382)],
        "records_b5_b6": {row["record_unit_id"] for row in events} == {"B5", "B6"},
        "record_counts_11_9": [sum(row["record_unit_id"] == record for row in events) for record in ("B5", "B6")] == [11, 9],
        "statements_4": len(statements) == 4,
        "statement_counts_3_1": [sum(row["record_unit_id"] == record for row in statements) for record in ("B5", "B6")] == [3, 1],
        "unique_cards_16": len({row["joint_tuple_id"] for row in events}) == 16,
        "prior_cards_8": len(transfers) == 8,
        "prior_events_12": sum(int(row["events"]) for row in transfers) == 12,
        "new_cards_8": len(new) == 8,
        "new_events_8": sum(row["lexicon_source"].endswith("LOCAL_UNANALYSED_CARD") for row in events) == 8,
        "one_restart": [row["event_id"] for row in events if row["record_restart_before"] == "YES"] == ["E373"],
        "b6_statement_restart": [row["statement_id"] for row in statements if row["record_restart_before"] == "YES"] == ["B6-S001"],
        "no_empty_values": all(row["small_value_de"].strip() for row in events),
        "sealed_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_FORTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
