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
    events = read("FOUR_HUNDRED_THIRTY_NINTH_FINAL_B2_62_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_THIRTY_NINTH_FINAL_B2_22_STATEMENTS.tsv")
    dictionary = read("FOUR_HUNDRED_THIRTY_NINTH_FINAL_B2_46_CARD_DICTIONARY.tsv")
    revised = read("FOUR_HUNDRED_THIRTY_NINTH_FIVE_FINAL_COMPOSITIONS.tsv")
    local = read("FOUR_HUNDRED_THIRTY_NINTH_EIGHT_LOCAL_WHOLE_CARDS.tsv")
    trace = read("FOUR_HUNDRED_THIRTY_NINTH_B2_62_EVENT_APPRENTICE_TRACE.tsv")
    drawers = read("FOUR_HUNDRED_THIRTY_NINTH_FOUR_B2_DRAWERS.tsv")
    checks = {
        "events_62": len(events) == 62,
        "statements_22": len(statements) == 22,
        "dictionary_46": len(dictionary) == 46,
        "revisions_5": len(revised) == 5,
        "local_8": len(local) == 8,
        "trace_62": len(trace) == 62,
        "drawers_4": len(drawers) == 4,
        "B1_transfer_14": [row["cards"] for row in drawers if row["drawer"] == "B1_TRANSFER"] == ["14"],
        "B2_productive_23": [row["cards"] for row in drawers if row["drawer"] == "B2_PRODUCTIVE_COMPOSITION"] == ["23"],
        "portable_1": [row["cards"] for row in drawers if row["drawer"] == "PORTABLE_RECURRENT_WHOLE_CARD"] == ["1"],
        "local_8_again": [row["cards"] for row in drawers if row["drawer"] == "B2_LOCAL_WHOLE_CARD"] == ["8"],
        "drawer_card_sum": sum(int(row["cards"]) for row in drawers) == 46,
        "drawer_event_sum": sum(int(row["events"]) for row in drawers) == 62,
        "every_value": all(row["small_value_de"] for row in events),
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_THIRTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
