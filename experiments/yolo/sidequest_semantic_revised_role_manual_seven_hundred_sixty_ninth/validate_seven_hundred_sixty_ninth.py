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
    lessons = read("SEVEN_HUNDRED_SIXTY_NINTH_15_LESSON_CURRICULUM.tsv")
    roles = read("SEVEN_HUNDRED_SIXTY_NINTH_4_REVISED_SCRIBE_ROLES.tsv")
    permissions = read("SEVEN_HUNDRED_SIXTY_NINTH_9_ROLE_PERMISSIONS.tsv")
    tests = read("SEVEN_HUNDRED_SIXTY_NINTH_9_PERMISSION_TESTS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SIXTY_NINTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    role = {row["role"]: row for row in roles}
    edge_permission = next(row for row in permissions if row["permission"] == "L_EDGE_01_F82R_READ_ONCE")
    checks = {
        "counts_15_4_9_9": (len(lessons), len(roles), len(permissions), len(tests)) == (15, 4, 9, 9),
        "hours_115_74_85_24": (int(role["MASTER_CORRECTOR"]["curriculum_hours"]), int(role["HERBAL_SCRIBE"]["curriculum_hours"]), int(role["BIO_STATION_SCRIBE"]["curriculum_hours"]), int(role["ASTRO_TABLE_SCRIBE"]["curriculum_hours"])) == (115, 74, 85, 24),
        "edge_only_master_bio": (edge_permission["MASTER_CORRECTOR"], edge_permission["HERBAL_SCRIBE"], edge_permission["BIO_STATION_SCRIBE"], edge_permission["ASTRO_TABLE_SCRIBE"]) == ("YES", "NO", "YES", "NO"),
        "five_positive_exact": sum(row["result"] == "PASS_EXACT" and row["output"] == row["expected"] for row in tests) == 5,
        "four_negative_blocked": sum(row["result"] == "PASS_BLOCKED" and row["authorized"] == "NO" for row in tests) == 4,
        "edge_render_exact": next(row for row in tests if row["test_id"] == "T_BIO_EDGE_RENDER")["output"].endswith("E180|E181"),
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (lessons, roles, permissions, tests) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["bio_hours"] == 85,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SIXTY_NINTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
