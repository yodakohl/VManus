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
    subprocess.run(["python", str(HERE / "build_eight_hundred_twenty_sixth.py")], check=True)
    candidates = read("EIGHT_HUNDRED_TWENTY_SIXTH_6_SOLK_CANDIDATES.tsv")
    events = read("EIGHT_HUNDRED_TWENTY_SIXTH_7_SOLK_EVENTS.tsv")
    grid = read("EIGHT_HUNDRED_TWENTY_SIXTH_5_SOLK_GRID.tsv")
    statements = read("EIGHT_HUNDRED_TWENTY_SIXTH_7_REVISED_STATEMENTS.tsv")
    roles = read("EIGHT_HUNDRED_TWENTY_SIXTH_4_PLACE_OPERATION_ROLES.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_TWENTY_SIXTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "five_cards_seven_events": len(events) == 7 and len({row["exact_card_id"] for row in events}) == 5,
        "five_recipes_cover_seven": len(grid) == 5 and sum(int(row["events"]) for row in grid) == 7,
        "all_literals_revised": all("SAMMELN" in row["revised_literal_de"] and "SAMMELSTELLE" not in row["revised_literal_de"] for row in events),
        "no_hidden_verb": all(row["hidden_verb_needed"] == "NO" for row in grid) and summary["hidden_holding_verbs_after_revision"] == 0,
        "seven_statements_revised": len(statements) == 7 and all("sammel" in row["revised_reading_de"].lower() and "Sammelstelle" not in row["revised_reading_de"] for row in statements),
        "candidate_selected": len(candidates) == 6 and next(row for row in candidates if row["decision"] == "SELECT_CORE_VALUE")["candidate"] == "SAMMELN",
        "solk_reclassified": next(row for row in roles if row["component"] == "SOLK")["category"] == "OPERATION_COLLECTION" and Counter(row["category"] for row in roles)["OPERATION_COLLECTION"] == 1,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_TWENTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
