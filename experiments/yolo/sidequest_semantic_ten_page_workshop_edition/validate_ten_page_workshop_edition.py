#!/usr/bin/env python3
"""Validate the unified ten-page workshop edition."""

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
    surfaces = read("TEN_PAGE_487_SURFACE_DICTIONARY.tsv")
    ledger = read("TEN_PAGE_776_SPEAKABLE_LEDGER.tsv")
    units = read("TEN_PAGE_258_READING_UNITS.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    add("surface_count", len(surfaces) == 487, len(surfaces))
    add("surface_ids", [row["surface_id"] for row in surfaces] == [f"SF{i:04d}" for i in range(1, 488)], "SF0001..SF0487")
    add("surface_unique", len({row["visible_surface"] for row in surfaces}) == 487, "487 expected")
    register_counts = {key: sum(row["register_status"] == key for row in surfaces) for key in {"PROSE_AND_ASTRO", "PROSE_ONLY", "ASTRO_ONLY"}}
    add("surface_register_counts", register_counts == {"PROSE_AND_ASTRO": 44, "PROSE_ONLY": 186, "ASTRO_ONLY": 257}, register_counts)
    add("ledger_count", len(ledger) == 776, len(ledger))
    add("ledger_serial", [int(row["unified_serial"]) for row in ledger] == list(range(1, 777)), "1..776")
    add("prose_groups", sum(row["register"] == "PROSE" for row in ledger) == 381, sum(row["register"] == "PROSE" for row in ledger))
    add("astro_groups", sum(row["register"] == "ASTRO" for row in ledger) == 395, sum(row["register"] == "ASTRO" for row in ledger))
    add("surface_links_exist", all(row["surface_id"] in {surface["surface_id"] for surface in surfaces} for row in ledger), "all linked")
    add("unit_count", len(units) == 258, len(units))
    add("unit_serial", [int(row["unit_serial"]) for row in units] == list(range(1, 259)), "1..258")
    add("prose_units", sum(row["register"] == "PROSE" for row in units) == 116, sum(row["register"] == "PROSE" for row in units))
    add("astro_units", sum(row["register"] == "ASTRO" for row in units) == 142, sum(row["register"] == "ASTRO" for row in units))
    add("unit_group_sum", sum(int(row["group_count"]) for row in units) == 776, sum(int(row["group_count"]) for row in units))
    add("all_groups_read", all(row["short_value_de"].strip() and row["unit_reading_de"].strip() for row in ledger), "nonempty")
    add("all_units_read", all(row["speakable_reading_de"].strip() for row in units), "nonempty")
    add("fixed_pages", {row["page"] for row in ledger} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}, sorted({row["page"] for row in ledger}))
    add("common_stems", summary["common_stems"] == 25, summary["common_stems"])
    add("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for table in (surfaces, ledger, units) for row in table), "sealed tokens absent")

    products = ["TEN_PAGE_487_SURFACE_DICTIONARY.tsv", "TEN_PAGE_776_SPEAKABLE_LEDGER.tsv", "TEN_PAGE_258_READING_UNITS.tsv", "TEN_PAGE_POCKET_CODEBOOK.md", "COMPLETE_TEN_PAGE_WORKSHOP_EDITION.md", "TEN_PAGE_WORKSHOP_REPORT.md", "BUILD_SUMMARY.json"]
    before = {name: (HERE / name).read_bytes() for name in products}
    subprocess.run([sys.executable, str(HERE / "build_ten_page_workshop_edition.py")], check=True, cwd=HERE.parents[3])
    after = {name: (HERE / name).read_bytes() for name in products}
    add("deterministic_rebuild", before == after, "all bytes identical")

    failures = [row for row in checks if not row["pass"]]
    result = {"status": "PASS" if not failures else "FAIL", "pass_count": len(checks) - len(failures), "fail_count": len(failures), "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {result['pass_count']}/{len(checks)} checks")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
