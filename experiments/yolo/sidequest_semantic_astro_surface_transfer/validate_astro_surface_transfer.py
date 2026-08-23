#!/usr/bin/env python3
"""Validate fixed-page Astro transfer coverage and forward-cell accounting."""

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
    groups = read("ASTRO_395_SURFACE_PARSE.tsv")
    types = read("ASTRO_301_TYPE_PARSE.tsv")
    hits = read("FORWARD_CELL_ASTRO_HITS.tsv")
    candidates = read("NEW_MULTI_ATOM_CANDIDATES.tsv")
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    add("group_count", len(groups) == 395, len(groups))
    add("group_serial", [int(row["group_serial"]) for row in groups] == list(range(1, 396)), "1..395")
    add("group_ids_unique", len({row["opaque_local_id"] for row in groups}) == 395, "395 expected")
    add("surface_type_count", len(types) == 301, len(types))
    add("surface_type_unique", len({row["visible_surface"] for row in types}) == 301, "301 expected")
    add("type_occurrence_sum", sum(int(row["occurrences"]) for row in types) == 395, sum(int(row["occurrences"]) for row in types))
    add("forward_cell_count", len(hits) == 18, len(hits))
    filled = {row["predicted_atom_sequence"]: row for row in hits if int(row["astro_exact_hit_count"]) > 0}
    add("three_exact_fills", set(filled) == {"OL+AR", "OT+AIR", "CHD+AIIN"}, sorted(filled))
    add("qotair_exact", filled["OT+AIR"]["astro_surfaces"] == "qotair", filled["OT+AIR"])
    add("olar_exact", filled["OL+AR"]["astro_surfaces"] == "olar", filled["OL+AR"])
    add("chedaiin_exact", filled["CHD+AIIN"]["astro_surfaces"] == "chedaiin", filled["CHD+AIIN"])
    qotair = next(row for row in types if row["visible_surface"] == "qotair")
    add("qotair_parse", qotair["detected_literal_atoms"] == "OT+AIR" and qotair["covered_characters"] == "5/6", qotair)
    add("exact_prose_surface_types", sum(row["transfer_class"] == "EXACT_PROSE_SURFACE" for row in types) == 44, sum(row["transfer_class"] == "EXACT_PROSE_SURFACE" for row in types))
    add("exact_prose_surface_groups", sum(row["transfer_class"] == "EXACT_PROSE_SURFACE" for row in groups) == 89, sum(row["transfer_class"] == "EXACT_PROSE_SURFACE" for row in groups))
    add("candidate_rows", len(candidates) == 53, len(candidates))
    add("fixed_pages", {row["page"] for row in groups} == {"f67r2", "f68r1", "f69v"}, sorted({row["page"] for row in groups}))
    add("no_orientation_inference", all("NO_START_OR_DIRECTION" in row["orientation_rule"] for row in groups), "all local-owner only")
    add("no_crosspage_key", all("NO_F68_F69_KEY" in row["crosspage_rule"] for row in groups), "all no-key")
    add("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for table in (groups, types, hits, candidates) for row in table), "sealed tokens absent")

    products = ["ASTRO_395_SURFACE_PARSE.tsv", "ASTRO_301_TYPE_PARSE.tsv", "FORWARD_CELL_ASTRO_HITS.tsv", "NEW_MULTI_ATOM_CANDIDATES.tsv", "ASTRO_SURFACE_TRANSFER_REPORT.md", "BUILD_SUMMARY.json"]
    before = {name: (HERE / name).read_bytes() for name in products}
    subprocess.run([sys.executable, str(HERE / "build_astro_surface_transfer.py")], check=True, cwd=HERE.parents[3])
    after = {name: (HERE / name).read_bytes() for name in products}
    add("deterministic_rebuild", before == after, "all bytes identical")

    failures = [row for row in checks if not row["pass"]]
    result = {"status": "PASS" if not failures else "FAIL", "pass_count": len(checks) - len(failures), "fail_count": len(failures), "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {result['pass_count']}/{len(checks)} checks")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
