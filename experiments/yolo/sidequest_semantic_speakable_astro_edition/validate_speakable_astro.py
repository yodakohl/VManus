#!/usr/bin/env python3
"""Validate the complete speakable Astro edition."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    groups = read("COMPLETE_395_SPEAKABLE_ASTRO_GROUPS.tsv")
    loci = read("COMPLETE_142_SPEAKABLE_ASTRO_LOCI.tsv")
    pages = read("PAGE_SUMMARY.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    add("group_count", len(groups) == 395, len(groups))
    add("group_serial", [int(row["group_serial"]) for row in groups] == list(range(1, 396)), "1..395")
    add("group_unique", len({row["opaque_local_id"] for row in groups}) == 395, "395 expected")
    add("locus_count", len(loci) == 142, len(loci))
    add("locus_serial", [int(row["locus_serial"]) for row in loci] == list(range(1, 143)), "1..142")
    add("locus_group_sum", sum(int(row["group_count"]) for row in loci) == 395, sum(int(row["group_count"]) for row in loci))
    add("page_count", len(pages) == 3, len(pages))
    add("page_loci", {row["page"]: int(row["locus_count"]) for row in pages} == {"f67r2": 74, "f68r1": 37, "f69v": 31}, {row["page"]: row["locus_count"] for row in pages})
    add("page_groups", {row["page"]: int(row["group_count"]) for row in pages} == {"f67r2": 190, "f68r1": 65, "f69v": 140}, {row["page"]: row["group_count"] for row in pages})
    add("all_groups_spoken", all(row["speakable_value_de"].strip() for row in groups), "nonempty")
    add("all_loci_spoken", all(row["speakable_locus_reading_de"].strip() for row in loci), "nonempty")
    add("source_modes_sum", sum(summary["reading_source_counts"].values()) == 395, summary["reading_source_counts"])
    add("enriched_groups", summary["reading_source_counts"]["ENRICHED_COMPONENT_READING"] == 29, summary["reading_source_counts"])
    add("no_orientation", all("NO_START_OR_DIRECTION" in row["orientation_rule"] for row in groups), "no start/direction")
    add("no_crosspage_key", all("NO_F68_F69_KEY" in row["crosspage_rule"] for row in groups), "no key")
    add("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for table in (groups, loci, pages) for row in table), "sealed tokens absent")

    products = ["COMPLETE_395_SPEAKABLE_ASTRO_GROUPS.tsv", "COMPLETE_142_SPEAKABLE_ASTRO_LOCI.tsv", "PAGE_SUMMARY.tsv", "THREE_SPEAKABLE_ASTRO_PAGES.md", "SPEAKABLE_ASTRO_REPORT.md", "BUILD_SUMMARY.json"]
    before = {name: (HERE / name).read_bytes() for name in products}
    subprocess.run([sys.executable, str(HERE / "build_speakable_astro.py")], check=True, cwd=HERE.parents[3])
    after = {name: (HERE / name).read_bytes() for name in products}
    add("deterministic_rebuild", before == after, "all bytes identical")

    failures = [row for row in checks if not row["pass"]]
    result = {"status": "PASS" if not failures else "FAIL", "pass_count": len(checks) - len(failures), "fail_count": len(failures), "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {result['pass_count']}/{len(checks)} checks")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
