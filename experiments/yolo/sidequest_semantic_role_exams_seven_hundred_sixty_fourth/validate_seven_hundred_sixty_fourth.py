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
    exams = read("SEVEN_HUNDRED_SIXTY_FOURTH_4_ROLE_EXAMS.tsv")
    errors = read("SEVEN_HUNDRED_SIXTY_FOURTH_5_ERROR_CASES.tsv")
    attempts = read("SEVEN_HUNDRED_SIXTY_FOURTH_8_ATTEMPTS.tsv")
    sources = read("SEVEN_HUNDRED_SIXTY_FOURTH_SOURCE_BINDINGS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SIXTY_FOURTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    by_exam = {row["exam_id"]: row for row in exams}
    after = [row for row in attempts if row["stage"] == "AFTER_CORRECTION"]
    before = [row for row in attempts if row["stage"] == "BEFORE_CORRECTION"]
    checks = {
        "four_roles": {row["role"] for row in exams} == {"HERBAL_SCRIBE", "BIO_STATION_SCRIBE", "MASTER_CORRECTOR", "ASTRO_TABLE_SCRIBE"},
        "four_exams_five_errors_eight_attempts": (len(exams), len(errors), len(attempts), len(sources)) == (4, 5, 8, 4),
        "five_distinct_error_types": len({row["error_type"] for row in errors}) == 5,
        "all_errors_caught": all(row["caught"] == "YES" for row in errors),
        "all_before_fail": len(before) == 4 and all(row["exact_match"] == "NO" and int(row["errors_remaining"]) > 0 for row in before),
        "all_after_exact": len(after) == 4 and all(row["exact_match"] == "YES" and int(row["errors_remaining"]) == 0 and row["output"] == by_exam[row["exam_id"]]["expected_output"] for row in after),
        "planted_outputs_differ": all(row["planted_output"] != row["expected_output"] for row in exams),
        "herbal_close_removed": len(by_exam["X01_HERBAL_CLOSE"]["expected_output"].split(" | ")) == len(by_exam["X01_HERBAL_CLOSE"]["planted_output"].split(" | ")) + 1,
        "bio_two_errors": by_exam["X02_BIO_GRADE_CARRY"]["planted_errors"].count(";") == 1,
        "astro_owner_not_rotation": "SLOT_01" in by_exam["X04_ASTRO_OWNER_COPY"]["prompt_de"] and "A3:G108" in by_exam["X04_ASTRO_OWNER_COPY"]["expected_output"] and "A3:G110" in by_exam["X04_ASTRO_OWNER_COPY"]["planted_output"],
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (exams, errors, attempts, sources) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["after_exact"] == 4,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SIXTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
