#!/usr/bin/env python3
import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    lessons = rows("HUNDRED_FORTY_SECOND_TEN_APPRENTICE_LESSONS.tsv")
    copies = rows("HUNDRED_FORTY_SECOND_40_OWNER_SUBSTITUTED_COPIES.tsv")
    checks = {
        "lessons_10": len(lessons) == 10,
        "moulds_10": len({r["mould_id"] for r in lessons}) == 10,
        "copies_40": len(copies) == 40,
        "four_hands": {r["renderer_id"] for r in copies} == {"R-A", "R-B", "R-C", "R-D"},
        "all_roundtrip": all(r["roundtrip"] == "PASS" for r in copies),
        "target_pages_fixed": {r["target_page"] for r in lessons} <= {"f10r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "owner_only_limit": all(r["interpretive_limit"] == "OWNER_CHANGED_ONLY__NO_NEW_CARD_MEANING" for r in lessons),
        "no_empty_cells": all(all(v for v in r.values()) for table in (lessons, copies) for r in table),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
