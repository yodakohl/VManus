#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SIXTY_EIGHTH"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_sixty_eighth.py")], check=True)
    groups = read(f"{PREFIX}_395_GROUP_CONDITION_SHELF.tsv")
    loci = read(f"{PREFIX}_142_LOCUS_CONDITION_SHELF.tsv")
    shelves = read(f"{PREFIX}_7_CONDITION_SHELVES.tsv")
    menu = read(f"{PREFIX}_36_WHAT_HOW_WHEN_MENU.tsv")
    selected = read(f"{PREFIX}_6_ILLUSTRATIVE_WHEN_JOINS.tsv")
    manual = read(f"{PREFIX}_7_STEP_WHEN_MANUAL.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    page_groups = Counter(row["page"] for row in groups)
    page_loci = Counter(row["page"] for row in loci)
    checks = {
        "all_groups": len(groups) == 395 and page_groups == {"f67r2": 190, "f68r1": 65, "f69v": 140},
        "all_loci": len(loci) == 142 and page_loci == {"f67r2": 74, "f68r1": 37, "f69v": 31},
        "shelf_partition": len(shelves) == 7 and {row["condition_shelf"] for row in shelves} == {"C1", "C2", "C3", "C4", "C5", "C6", "Q67"},
        "shelf_totals": sum(int(row["groups"]) for row in shelves) == 395 and sum(int(row["loci"]) for row in shelves) == 142,
        "complete_menu": len(menu) == 36 and all(Counter(row["entry_id"] for row in menu)[entry] == 6 for entry in ["WH01", "WH02", "WH03", "WH04", "WH05", "WH06"]),
        "one_primary_each": len(selected) == 6 and all(sum(row["working_primary"] == "YES" for row in menu if row["entry_id"] == entry) == 1 for entry in ["WH01", "WH02", "WH03", "WH04", "WH05", "WH06"]),
        "manual": len(manual) == 7 and {int(row["step"]) for row in manual} == set(range(1, 8)),
        "no_orientation": all(row["orientation_status"] == "NONE" and row["crosspage_key"] == "NONE" for row in groups),
        "no_automatic_join": all(row["automatic_join"] == "NO" and row["selection_source"] == "MASTER_EXEMPLAR_ONLY" for row in menu),
        "no_condition_identity": summary["identified_condition_values"] == 0 and all(row["actual_condition_value"] == "UNNAMED_MASTER_VALUE" for row in selected),
        "no_new_words": summary["new_word_meanings"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"] and not any("f84" in " ".join(row.values()).lower() for row in groups + loci + shelves + menu + selected + manual),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
