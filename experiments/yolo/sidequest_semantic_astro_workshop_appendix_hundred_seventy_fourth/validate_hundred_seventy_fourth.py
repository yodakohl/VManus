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
    groups = read("HUNDRED_SEVENTY_FOURTH_395_GROUP_WORKSHOP_APPENDIX.tsv")
    loci = read("HUNDRED_SEVENTY_FOURTH_142_LOCUS_JOB_EDITION.tsv")
    pages = read("HUNDRED_SEVENTY_FOURTH_3_ASTRO_PAGE_JOBS.tsv")
    no_key = read("HUNDRED_SEVENTY_FOURTH_6_NO_KEY_RULES.tsv")
    checks = {
        "all_395_groups": len(groups) == 395 and len({row["source_group_id"] for row in groups}) == 395,
        "page_group_counts": [sum(row["page"] == page for row in groups) for page in ["f67r2", "f68r1", "f69v"]] == [190, 65, 140],
        "all_142_loci": len(loci) == 142 and sum(int(row["member_group_count"]) for row in loci) == 395,
        "locus_page_counts": [sum(row["page"] == page for row in loci) for page in ["f67r2", "f68r1", "f69v"]] == [74, 37, 31],
        "three_distinct_page_jobs": len(pages) == 3 and len({row["selected_page_job"] for row in pages}) == 3,
        "all_modules_assigned": len({row["source_module"] for row in groups}) == 14 and all(row["local_job_id"] for row in groups),
        "source_order_not_direction": {row["ordering_rule"] for row in groups} == {"SOURCE_ORDER_ONLY_NOT_CIRCLE_DIRECTION"},
        "no_crosspage_keys": {row["crosspage_key"] for row in groups} == {"NONE"} and len(no_key) == 6,
        "f68_28_star_addresses": sum(row["source_module"] == "M68_STAR_STATIONS" for row in groups) == 28,
        "f69_28_local_loci": sum(row["source_module"] == "M69_LEFT_28_SLOTS" for row in loci) == 28,
        "fixed_pages_only": {row["page"] for row in groups} == {"f67r2", "f68r1", "f69v"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
