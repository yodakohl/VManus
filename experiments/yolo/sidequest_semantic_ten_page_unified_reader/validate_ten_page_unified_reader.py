#!/usr/bin/env python3
"""Validate the creative 776-group, ten-page reader."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    key = rows(OUT / "TEN_PAGE_607_READER_KEY.tsv")
    bridge = rows(OUT / "CROSS_REGISTER_44_SURFACE_BRIDGE.tsv")
    trace = rows(OUT / "TEN_PAGE_776_READER_TRACE.tsv")
    units = rows(OUT / "TEN_PAGE_258_READING_UNITS.tsv")

    registers = Counter(row["register"] for row in key)
    check("607_reader_keys", len(key) == 607, len(key))
    check("230_prose_keys", registers["PROSE"] == 230, registers)
    check("377_astro_owner_surface_keys", registers["ASTRO"] == 377, registers)
    check("lookup_ids_unique", len({row["lookup_id"] for row in key}) == 607, "unique")
    check("all_readings_nonempty", all(row["short_workshop_reading_de"].strip() for row in key), "all")
    check("prose_owner_not_required", all(row["visible_owner"] == "NOT_REQUIRED" for row in key if row["register"] == "PROSE"), "all")
    check("astro_owner_required", all(row["visible_owner"] != "NOT_REQUIRED" for row in key if row["register"] == "ASTRO"), "all")

    check("44_cross_register_surfaces", len(bridge) == 44, len(bridge))
    check("bridge_rule_fixed", all(row["bridge_rule"] == "SAME_VISIBLE_FORM__REGISTER_AND_VISIBLE_OWNER_SUPPLY_EXPANSION" for row in bridge), "all")

    trace_registers = Counter(row["register"] for row in trace)
    check("776_group_trace", len(trace) == 776, len(trace))
    check("381_prose_events", trace_registers["PROSE"] == 381, trace_registers)
    check("395_astro_groups", trace_registers["ASTRO"] == 395, trace_registers)
    check("unified_serials", [row["unified_serial"] for row in trace] == [f"U{i:03d}" for i in range(1, 777)], "continuous")
    key_ids = {row["lookup_id"] for row in key}
    check("all_trace_lookups_exist", all(row["lookup_id"] in key_ids for row in trace), "all")
    check("all_lookup_status_pass", all(row["lookup_status"].endswith("PASS") for row in trace), "all")

    unit_kinds = Counter(row["unit_kind"] for row in units)
    check("258_reading_units", len(units) == 258, len(units))
    check("116_prose_statements", unit_kinds["PROSE_STATEMENT"] == 116, unit_kinds)
    check("142_astro_loci", unit_kinds["ASTRO_VISIBLE_LOCUS"] == 142, unit_kinds)
    check("all_unit_readings_nonempty", all(row["literal_reading_sequence_de"].strip() and row["fluent_workshop_reading_de"].strip() for row in units), "all")
    check("ten_pages_exact", {row["page"] for row in trace} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}, sorted({row["page"] for row in trace}))

    astro_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    astro_by_owner_surface: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in trace:
        if row["register"] == "ASTRO":
            astro_by_surface[row["visible_surface"]].append(row)
            astro_by_owner_surface[(row["visible_owner"], row["visible_surface"])].append(row)
    surface_conflicts = sum(len({row["resolved_reading_de"] for row in group}) > 1 for group in astro_by_surface.values())
    owner_conflicts = sum(len({row["resolved_reading_de"] for row in group}) > 1 for group in astro_by_owner_surface.values())
    check("42_astro_surface_conflicts_without_owner", surface_conflicts == 42, surface_conflicts)
    check("zero_astro_owner_surface_conflicts", owner_conflicts == 0, owner_conflicts)

    manual = (OUT / "APPRENTICE_TEN_PAGE_READER_MANUAL.md").read_text(encoding="utf-8")
    check("manual_no_circle_order", "Beginne nicht automatisch oben und laufe nicht im Kreis" in manual, "present")
    check("manual_no_crosspage_key", "Verbinde f68 und f69 nicht" in manual, "present")
    readable = (OUT / "COMPLETE_TEN_PAGE_READER.md").read_text(encoding="utf-8")
    check("all_units_in_readable_book", all(f"### {row['unit_id']}" in readable for row in units), "all")
    report = (OUT / "TEN_PAGE_UNIFIED_READER_REPORT.md").read_text(encoding="utf-8")
    check("creative_caveat", "kreative zehnseitige Arbeitstheorie" in report, "present")

    content_names = [
        "TEN_PAGE_607_READER_KEY.tsv", "CROSS_REGISTER_44_SURFACE_BRIDGE.tsv",
        "TEN_PAGE_776_READER_TRACE.tsv", "TEN_PAGE_258_READING_UNITS.tsv",
        "APPRENTICE_TEN_PAGE_READER_MANUAL.md", "COMPLETE_TEN_PAGE_READER.md",
        "TEN_PAGE_UNIFIED_READER_REPORT.md",
    ]
    content = "\n".join((OUT / name).read_text(encoding="utf-8", errors="replace") for name in content_names)
    sealed = re.compile(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])")
    check("sealed_pages_absent", sealed.search(content) is None, "absent")
    before = {name: digest(OUT / name) for name in content_names}
    subprocess.run([sys.executable, str(OUT / "build_ten_page_unified_reader.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    after = {name: digest(OUT / name) for name in content_names}
    check("deterministic_rebuild", before == after, "byte identical")

    passed = all(bool(row["pass"]) for row in checks)
    result = {
        "status": "PASS" if passed else "FAIL",
        "checks_passed": sum(bool(row["pass"]) for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "counts": {
            "reader_keys": len(key), "prose_keys": registers["PROSE"], "astro_owner_surface_keys": registers["ASTRO"],
            "groups": len(trace), "prose_events": trace_registers["PROSE"], "astro_groups": trace_registers["ASTRO"],
            "reading_units": len(units), "shared_surfaces": len(bridge),
            "astro_surface_conflicts_without_owner": surface_conflicts, "astro_owner_surface_conflicts": owner_conflicts,
        },
    }
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        for row in checks:
            if not row["pass"]:
                print(f"FAIL {row['check']}: {row['detail']}")
        raise SystemExit(1)
    print(f"PASS {result['checks_passed']}/{result['checks_total']}")


if __name__ == "__main__":
    main()
