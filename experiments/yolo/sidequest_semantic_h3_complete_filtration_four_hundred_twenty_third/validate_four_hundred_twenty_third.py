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
    events = read("FOUR_HUNDRED_TWENTY_THIRD_H3_17_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_TWENTY_THIRD_H3_FOUR_STATEMENTS.tsv")
    chain = read("FOUR_HUNDRED_TWENTY_THIRD_SEVEN_STAGE_FILTRATION_CHAIN.tsv")
    reserve = read("FOUR_HUNDRED_TWENTY_THIRD_RESERVE_PAIR.tsv")
    matrix = read("FOUR_HUNDRED_TWENTY_THIRD_H3_H4_H5_ARTICLE_MATRIX.tsv")
    checks = {
        "seventeen_events": len(events) == 17,
        "exact_event_range": [row["event_id"] for row in events] == [f"E{i:03d}" for i in range(39, 56)],
        "every_value_nonempty": all(row["selected_small_value_de"] for row in events),
        "four_statements": len(statements) == 4,
        "seven_stage_chain": len(chain) == 7,
        "chain_in_one_statement": all(row["statement_id"] == "H3-S001" for row in events[:7]),
        "reserve_pair": len(reserve) == 2 and [row["value_de"] for row in reserve] == ["Reserve setzen", "Reserve nehmen"],
        "three_article_matrix": len(matrix) == 3,
        "only_h5_application": [row["record"] for row in matrix if row["application_present"] == "YES"] == ["H5"],
        "wine_removed_from_values": all("Wein" not in row["selected_small_value_de"] for row in events),
        "sealed_pages_absent": all("f84" not in value.lower() for rows in (events, statements, chain, reserve, matrix) for row in rows for value in row.values()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_TWENTY_THIRD_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
