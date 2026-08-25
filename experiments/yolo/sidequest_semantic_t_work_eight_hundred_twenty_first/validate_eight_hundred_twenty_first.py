#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_twenty_first.py")], check=True)
    candidates = read("EIGHT_HUNDRED_TWENTY_FIRST_6_T_CANDIDATES.tsv")
    events = read("EIGHT_HUNDRED_TWENTY_FIRST_10_T_EVENTS.tsv")
    cards = read("EIGHT_HUNDRED_TWENTY_FIRST_9_T_CARDS.tsv")
    statements = read("EIGHT_HUNDRED_TWENTY_FIRST_7_REVISED_STATEMENTS.tsv")
    distinctions = read("EIGHT_HUNDRED_TWENTY_FIRST_3_ACTION_DISTINCTIONS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_TWENTY_FIRST_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    statement_counts = Counter(row["statement_id"] for row in events)
    checks = {
        "ten_events_nine_cards": len(events) == 10 and len(cards) == 9 and len({row["event_id"] for row in events}) == 10,
        "all_are_t_cards": all("T" in row["component_recipe"].split("+") for row in events),
        "all_literals_revised": all("BEARBEITEN" in row["revised_literal_de"] and "ANWENDEN" not in row["revised_literal_de"] for row in events),
        "seven_complete_statements": len(statements) == 7 and all(len(row["t_events"].split(",")) == statement_counts[row["statement_id"]] for row in statements),
        "no_anwenden_in_revisions": all("anwenden" not in row["revised_reading_de"].lower() for row in statements),
        "bearbeiten_in_revisions": all("bearbeit" in row["revised_reading_de"].lower() for row in statements),
        "candidate_selected_once": len(candidates) == 6 and sum(row["decision"] == "SELECT_CORE_VALUE" for row in candidates) == 1,
        "three_action_distinctions": len(distinctions) == 3 and {row["component"] for row in distinctions} == {"OK", "T", "CHD"},
        "page_scope": {row["page"] for row in events} == {"f10r", "f11r", "f55v", "f81v", "f83r"},
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_TWENTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
