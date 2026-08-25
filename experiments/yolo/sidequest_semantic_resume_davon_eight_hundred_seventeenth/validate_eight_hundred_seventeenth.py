#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_seventeenth.py")], check=True)
    candidates = read("EIGHT_HUNDRED_SEVENTEENTH_5_RESUME_CANDIDATES.tsv")
    events = read("EIGHT_HUNDRED_SEVENTEENTH_2_DAVON_OCCURRENCES.tsv")
    statements = read("EIGHT_HUNDRED_SEVENTEENTH_2_REVISED_STATEMENTS.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_SEVENTEENTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "one_exact_card_two_surfaces": len(events) == 2 and len({row["exact_card_id"] for row in events}) == 1 and {row["surface"] for row in events} == {"dchol", "schol"},
        "two_pages_two_statements": {row["page"] for row in events} == {"f11r", "f56r"} and len(statements) == 2,
        "davon_selected_everywhere": all(row["selected_reading_de"] == "DAVON" for row in events),
        "old_value_removed": all("wiederaufnehmen" not in row["revised_reading_de"].lower() for row in statements),
        "new_value_inserted": all("Davon" in row["revised_reading_de"] for row in statements),
        "candidate_comparison_complete": len(candidates) == 5 and sum(row["decision"] == "SELECT_MEMORIZED_ANAPHOR" for row in candidates) == 1,
        "architecture_unchanged": summary["core_size"] == 33 and summary["bound_components"] == 3 and summary["whole_forms"] == 3,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_SEVENTEENTH_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
