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
    marks = read("SEVEN_HUNDRED_SIXTY_FIFTH_6_CORRECTION_MARKS.tsv")
    functions = read("SEVEN_HUNDRED_SIXTY_FIFTH_8_FUNCTION_CROSSWALK.tsv")
    corrections = read("SEVEN_HUNDRED_SIXTY_FIFTH_5_MARKED_CORRECTIONS.tsv")
    proofs = read("SEVEN_HUNDRED_SIXTY_FIFTH_4_PROOF_SHEETS.tsv")
    sources = read("SEVEN_HUNDRED_SIXTY_FIFTH_HISTORICAL_MECHANISMS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SIXTY_FIFTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "six_marks_eight_functions": (len(marks), len(functions)) == (6, 8),
        "unique_mark_ids": len({row["mark_id"] for row in marks}) == 6,
        "five_errors_four_proofs": (len(corrections), len(proofs)) == (5, 4),
        "all_corrections_unambiguous": all(row["unambiguous"] == "YES" for row in corrections),
        "no_full_line_recopy": all(row["full_line_recopy"] == "NO" for row in proofs),
        "six_of_seventeen_units_touched": (sum(int(row["units_touched"]) for row in corrections), sum(int(row["local_units_total"]) for row in proofs)) == (6, 17),
        "all_eight_functions_mapped": {row["correction_function"] for row in functions} == {"DELETE", "INSERT", "TRANSPOSE", "REPEAT_OR_CURRENT_ITEM_CARRY", "GRADE", "CLOSE", "LOCAL_TAIL", "PICTURE_OWNER"},
        "historical_sources_present": len(sources) == 3 and all(row["url"].startswith("https://") for row in sources),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (marks, functions, corrections, proofs) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["mark_primitives"] == 6,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SIXTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
