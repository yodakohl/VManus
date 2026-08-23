#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    tokens = read("HUNDRED_NINETY_FOURTH_25_TOKEN_MODE_INSTRUCTION.tsv")
    fields = read("HUNDRED_NINETY_FOURTH_5_FIELD_MODE_PLAN.tsv")
    readback = read("HUNDRED_NINETY_FOURTH_25_TOKEN_SURFACE_READBACK.tsv")
    repeated = read("HUNDRED_NINETY_FOURTH_REPEATED_CARD_MODE_ALLOMORPHS.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "25_tokens": len(tokens) == 25 and [int(row["token_order"]) for row in tokens] == list(range(1, 26)),
        "five_fields": len(fields) == 5 and {row["field_mode"] for row in fields} == {"CH", "D", "O", "Q", "S"},
        "two_open_three_closed": sum(row["closure"] == "OPEN" for row in fields) == 2 and sum(row["closure"] == "CLOSED" for row in fields) == 3,
        "all_mode_matching": all(row["surface_matches_mode"] == "YES" for row in tokens),
        "all_registered": all(row["surface_registered_for_card"] == "YES" for row in tokens),
        "all_unique_readback": all(row["card_readback_exact"] == "YES" and row["mode_readback_exact"] == "YES" for row in readback),
        "cross_mode_cards_preserve_values": len(repeated) >= 4 and all(row["same_card_value_preserved"] == "YES" for row in repeated),
        "field_lengths": all(int(row["token_end"]) - int(row["token_start"]) + 1 == 5 for row in fields),
        "sealed_absent": summary["sealed_pages_accessed"] is False,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "summary": summary}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
