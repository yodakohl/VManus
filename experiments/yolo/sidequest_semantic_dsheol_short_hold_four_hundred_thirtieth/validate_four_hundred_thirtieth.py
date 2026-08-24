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
    events = read("FOUR_HUNDRED_THIRTIETH_REVISED_B1_66_EVENT_INTERLINEAR.tsv")
    statements = read("FOUR_HUNDRED_THIRTIETH_REVISED_B1_21_STATEMENTS.tsv")
    candidates = read("FOUR_HUNDRED_THIRTIETH_DSHEOL_CANDIDATES.tsv")
    pocket = read("FOUR_HUNDRED_THIRTIETH_POCKET_RULE.tsv")
    target = [row for row in events if row["event_id"] == "E160"]
    checks = {
        "B1_events_66": len(events) == 66,
        "B1_statements_21": len(statements) == 21,
        "target_unique": len(target) == 1,
        "target_short_hold": target[0]["small_value_de"] == "kurz halten",
        "target_composed": target[0]["lexicon_source"] == "B1_COMPOSED_SH_HOLD+E_SHORT+OL_CONTINUE",
        "old_rub_absent": all("einreiben" not in row["small_value_de"].lower() for row in events),
        "candidate_selected": [row["value_de"] for row in candidates if row["decision"] == "SELECT"] == ["kurz halten"],
        "pocket_one": len(pocket) == 1,
        "statement_revised": "kurz halten" in [row for row in statements if row["statement_id"] == "B1-S018"][0]["continuous_reading_de"],
        "sealed_locus_absent": all("f84" not in row["locus"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_THIRTIETH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        raise SystemExit(result)


if __name__ == "__main__":
    main()
