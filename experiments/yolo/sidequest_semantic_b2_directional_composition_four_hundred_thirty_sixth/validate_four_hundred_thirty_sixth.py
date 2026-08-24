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
    events = read("FOUR_HUNDRED_THIRTY_SIXTH_REVISED_B2_62_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_THIRTY_SIXTH_REVISED_B2_22_STATEMENTS.tsv")
    substitution = read("FOUR_HUNDRED_THIRTY_SIXTH_DIRECTIONAL_SUBSTITUTION_TABLE.tsv")
    targets = read("FOUR_HUNDRED_THIRTY_SIXTH_SEVEN_NEW_COMPOSITIONS.tsv")
    dictionary = read("FOUR_HUNDRED_THIRTY_SIXTH_B2_46_CARD_DICTIONARY.tsv")
    checks = {
        "events_62": len(events) == 62,
        "statements_22": len(statements) == 22,
        "substitution_8": len(substitution) == 8,
        "new_compositions_7": len(targets) == 7,
        "dictionary_46": len(dictionary) == 46,
        "B1_transfer_14": sum(row["drawer"] == "B1_TRANSFER" for row in dictionary) == 14,
        "B2_productive_8": sum(row["drawer"] == "B2_PRODUCTIVE_COMPOSITION" for row in dictionary) == 8,
        "B2_local_24": sum(row["drawer"] == "B2_LOCAL_WHOLE_CARD" for row in dictionary) == 24,
        "rest_removed": all("Rest" not in row["small_value_de"] for row in events),
        "qokaly_current_target": [row["small_value_de"] for row in events if row["surface"] == "qokaly"] == ["dies an die Stelle setzen"],
        "lcheckhedy_out_strain": [row["small_value_de"] for row in events if row["surface"] == "lcheckhedy"] == ["hinaus seihen; Schluss"],
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_THIRTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
