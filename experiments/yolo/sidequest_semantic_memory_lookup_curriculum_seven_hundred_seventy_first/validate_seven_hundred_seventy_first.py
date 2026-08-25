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
    lessons = read("SEVEN_HUNDRED_SEVENTY_FIRST_16_LESSON_CURRICULUM.tsv")
    roles = read("SEVEN_HUNDRED_SEVENTY_FIRST_4_ROLE_LOADS.tsv")
    trace = read("SEVEN_HUNDRED_SEVENTY_FIRST_21_EXAM_MEMORY_LOOKUP_TRACE.tsv")
    retests = read("SEVEN_HUNDRED_SEVENTY_FIRST_5_RETESTS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SEVENTY_FIRST_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    role = {row["role"]: row for row in roles}
    checks = {
        "counts_16_4_21_5": (len(lessons), len(roles), len(trace), len(retests)) == (16, 4, 21, 5),
        "hours_114_73_84_24": (int(role["MASTER_CORRECTOR"]["curriculum_hours"]), int(role["HERBAL_SCRIBE"]["curriculum_hours"]), int(role["BIO_STATION_SCRIBE"]["curriculum_hours"]), int(role["ASTRO_TABLE_SCRIBE"]["curriculum_hours"])) == (114, 73, 84, 24),
        "trace_partition_7_11_1_2": (sum(row["knowledge_source"] == "COMMON_12_ACTIVE_MEMORY" for row in trace), sum(row["knowledge_source"] == "ROLE_SPECIALIST_CARD_MEMORY" for row in trace), sum(row["knowledge_source"] == "SHARED_5_REFERENCE_LOOKUP" for row in trace), sum(row["knowledge_source"] == "ASTRO_LOCAL_MODEL_LOOKUP" for row in trace)) == (7, 11, 1, 2),
        "proc004_is_only_shared_lookup": [row["unit_id"] for row in trace if row["knowledge_source"] == "SHARED_5_REFERENCE_LOOKUP"] == ["PROC004"],
        "all_trace_pass": all(row["result"] == "PASS" for row in trace),
        "all_retests_exact": all(row["exact_output"] == "YES" for row in retests),
        "roles_have_12_plus_5_except_astro": all((row["active_common_cards"], row["shared_reference_cards"]) == (("0", "0") if row["role"] == "ASTRO_TABLE_SCRIBE" else ("12", "5")) for row in roles),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (lessons, roles, trace, retests) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["exam_units"] == 21,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SEVENTY_FIRST_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
