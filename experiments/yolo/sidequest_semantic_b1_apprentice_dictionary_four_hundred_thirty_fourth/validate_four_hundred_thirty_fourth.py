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
    dictionary = read("FOUR_HUNDRED_THIRTY_FOURTH_B1_43_CARD_DICTIONARY.tsv")
    trace = read("FOUR_HUNDRED_THIRTY_FOURTH_B1_66_EVENT_APPRENTICE_TRACE.tsv")
    drawers = read("FOUR_HUNDRED_THIRTY_FOURTH_THREE_DRAWERS.tsv")
    cells = read("FOUR_HUNDRED_THIRTY_FOURTH_B1_21_CELL_EDITION.tsv")
    checks = {
        "dictionary_43": len(dictionary) == 43,
        "unique_cards": len({row["joint_tuple_id"] for row in dictionary}) == 43,
        "trace_66": len(trace) == 66,
        "event_range": [row["event_id"] for row in trace] == [f"E{i:03d}" for i in range(101, 167)],
        "cells_21": len(cells) == 21,
        "three_drawers": len(drawers) == 3,
        "drawer_cards_sum": sum(int(row["cards"]) for row in drawers) == 43,
        "drawer_events_sum": sum(int(row["B1_events"]) for row in drawers) == 66,
        "productive_27": [row["cards"] for row in drawers if row["drawer"] == "PRODUCTIVE_COMPOSITION"] == ["27"],
        "portable_whole_4": [row["cards"] for row in drawers if row["drawer"] == "PORTABLE_RECURRENT_WHOLE_CARD"] == ["4"],
        "local_whole_12": [row["cards"] for row in drawers if row["drawer"] == "POOL_LOCAL_LEARNED_CARD"] == ["12"],
        "no_sentence_values": max(len(row["small_value_de"].replace(";", "").split()) for row in dictionary) <= 5,
        "every_trace_value": all(row["small_value_de"] for row in trace),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in trace),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_THIRTY_FOURTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
