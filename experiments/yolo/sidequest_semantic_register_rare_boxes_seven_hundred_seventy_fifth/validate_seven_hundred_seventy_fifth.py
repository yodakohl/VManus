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
    boxes = read("SEVEN_HUNDRED_SEVENTY_FIFTH_5_REGISTER_RARE_BOX_CARDS.tsv")
    lsh = read("SEVEN_HUNDRED_SEVENTY_FIFTH_2_CARD_BIO_LSH_STRIP.tsv")
    specialists = read("SEVEN_HUNDRED_SEVENTY_FIFTH_2_SPECIALIST_ISOLATION_TESTS.tsv")
    master = read("SEVEN_HUNDRED_SEVENTY_FIFTH_381_MASTER_ACCESS_TRACE.tsv")
    lessons = read("SEVEN_HUNDRED_SEVENTY_FIFTH_17_SPECIALIZED_LESSONS.tsv")
    roles = read("SEVEN_HUNDRED_SEVENTY_FIFTH_4_FINAL_ROLE_LOADS.tsv")
    summary = json.loads((HERE / "SEVEN_HUNDRED_SEVENTY_FIFTH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    role = {row["role"]: row for row in roles}
    checks = {
        "counts_5_2_2_381_17_4": (len(boxes), len(lsh), len(specialists), len(master), len(lessons), len(roles)) == (5, 2, 2, 381, 17, 4),
        "box_split_3_2": (sum(row["register"] == "HERBAL" for row in boxes), sum(row["register"] == "BIO" for row in boxes)) == (3, 2),
        "specialist_events_100_281": [int(row["visible_events"]) for row in specialists] == [100, 281],
        "specialist_statements_19_97": [int(row["statements"]) for row in specialists] == [19, 97],
        "specialists_full_no_cross_box": all(row["full_register_reproduction"] == "YES" and row["unresolved_events"] == "0" and row["other_register_box_cards_visible"] == "0" for row in specialists),
        "master381": len(master) == 381 and all(row["reproduced"] == "YES" for row in master),
        "hours_111_68_80_24": (int(role["MASTER_CORRECTOR"]["curriculum_hours"]), int(role["HERBAL_SCRIBE"]["curriculum_hours"]), int(role["BIO_STATION_SCRIBE"]["curriculum_hours"]), int(role["ASTRO_TABLE_SCRIBE"]["curriculum_hours"])) == (111, 68, 80, 24),
        "specialist_components36": role["HERBAL_SCRIBE"]["components"] == role["BIO_STATION_SCRIBE"]["components"] == "36",
        "fixed_pages_only": all("f84" not in "\t".join(row.values()).lower() for rows in (boxes, lsh, specialists, master, lessons, roles) for row in rows),
        "summary_pass": summary["status"] == "PASS" and summary["master_events_reproduced"] == 381,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "SEVEN_HUNDRED_SEVENTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
