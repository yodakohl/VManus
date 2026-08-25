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
    duplicates = read("SEVEN_HUNDRED_SIXTY_SIXTH_3_ADJACENT_DUPLICATES.tsv")
    opens = read("SEVEN_HUNDRED_SIXTY_SIXTH_27_OPEN_STATEMENTS.tsv")
    grades = read("SEVEN_HUNDRED_SIXTY_SIXTH_8_GRADE_PARADIGMS.tsv")
    resets = read("SEVEN_HUNDRED_SIXTY_SIXTH_4_MID_STATEMENT_OWNER_RESETS.tsv")
    decisions = read("SEVEN_HUNDRED_SIXTY_SIXTH_5_DECISIONS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SIXTY_SIXTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    read_once = [row for row in duplicates if row["logical_source_tokens"] == "1"]
    checks = {
        "counts_3_27_8_4_5": (len(duplicates), len(opens), len(grades), len(resets), len(decisions)) == (3, 27, 8, 4, 5),
        "only_e180_e181_read_once": len(read_once) == 1 and read_once[0]["pair"] == "E180->E181",
        "other_duplicates_retained": all(row["correction_action"] == "NONE" for row in duplicates if row["pair"] != "E180->E181"),
        "open_split_15_12": (sum(row["statement_id"].startswith("H") for row in opens), sum(row["statement_id"].startswith("B") for row in opens)) == (15, 12),
        "no_close_insertions": all(row["correction_action"] == "DO_NOT_INSERT_CLOSE" for row in opens),
        "all_grade_families_retained": all(row["decision"] == "PRODUCTIVE_GRADE_CHOICES_RETAIN" for row in grades),
        "four_owner_resets_retained": all(row["decision"] == "VISIBLE_OWNER_RESET_RETAIN" for row in resets),
        "visible381_source380": summary["visible_cards"] == 381 and summary["logical_source_cards"] == 380,
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (duplicates, opens, grades, resets, decisions) for row in rows),
        "summary_pass": summary["status"] == "PASS",
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SIXTY_SIXTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
