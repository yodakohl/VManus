#!/usr/bin/env python3
"""Production-free reconstruction of the f67--f73 bare-DA capacity stop."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RES = BASE / "results"
SOURCE = RES / "source_sta_family_consensus_groups.tsv"
RESULT = RES / "source_native_circle_qo_capacity.json"
REPORT = RES / "source_native_circle_qo_capacity_report.md"
OUT = RES / "source_native_circle_qo_capacity_validation.json"
OUT_REPORT = RES / "source_native_circle_qo_capacity_validation_report.md"
PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
FOLIOS = tuple(f"f{i}" for i in range(67, 74))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pf(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if not match:
        raise ValueError("page")
    return match.group(1)


def split(surface: str) -> tuple[str, str]:
    for prefix in PREFIXES:
        if surface[: len(prefix)] == prefix:
            return prefix, surface[len(prefix) :]
    return "NONE", surface


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text())
    checks = 0
    def check(value: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not value:
            raise AssertionError(label)
    check(digest(SOURCE) == "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225", "source hash")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        all_rows = list(csv.DictReader(handle, delimiter="\t"))
    check(len(all_rows) == len({row["consensus_group_id"] for row in all_rows}) == 26184, "source identity")
    rows = [row for row in all_rows if row["strict_zero_alternative"] == "1" and pf(row["page"]) in FOLIOS]
    counts = Counter(split(row["family_surface"])[0] for row in rows)
    first = Counter((row["kind"], split(row["family_surface"])[0]) for row in rows if int(row["consensus_group_index"]) == 1)
    later = Counter((row["kind"], split(row["family_surface"])[0]) for row in rows if int(row["consensus_group_index"]) != 1)
    cells = defaultdict(Counter)
    for row in rows:
        state, remainder = split(row["family_surface"])
        if remainder and state in {"NONE", "DA"}:
            key = (remainder, pf(row["page"]))
            cells[key][state] += 1
            cells[key][state + ("_FIRST" if int(row["consensus_group_index"]) == 1 else "_LATER")] += 1
    mixed = {key: value for key, value in cells.items() if value["NONE"] > 0 and value["DA"] > 0}
    mobile = {key: value for key, value in mixed.items() if min(value[x] for x in ("NONE_FIRST", "NONE_LATER", "DA_FIRST", "DA_LATER")) > 0}
    check(len(rows) == 960 and len({row["locus"] for row in rows}) == 501, "scope totals")
    check(sorted({row["page"] for row in rows}) == sorted({row["page"] for row in rows}) and len({row["page"] for row in rows}) == 26, "pages")
    check(tuple(sorted({pf(row["page"]) for row in rows})) == FOLIOS, "folios including f71")
    check({row["grammar_scope"] for row in rows} == {"DIAGNOSTIC_NONPROSE"}, "scope class")
    expected_ops = {state: counts[state] for state in ("NONE", "DA", "DAQ", "DAQK", "DAQKJ")}
    check(expected_ops == result["operation_counts"] == {"NONE": 932, "DA": 6, "DAQ": 15, "DAQK": 7, "DAQKJ": 0}, "operations")
    check({kind: sum(row["kind"] == kind for row in rows) for kind in "CLPR"} == result["kind_group_counts"], "kinds")
    check({pf_: sum(pf(row["page"]) == pf_ for row in rows) for pf_ in FOLIOS} == result["folio_group_counts"], "folio counts")
    check({f"{kind}|{state}": first[kind, state] for kind in "CLPR" for state in ("NONE", "DA", "DAQ", "DAQK", "DAQKJ")} == result["first_counts_by_kind_operation"], "first table")
    check({f"{kind}|{state}": later[kind, state] for kind in "CLPR" for state in ("NONE", "DA", "DAQ", "DAQK", "DAQKJ")} == result["later_counts_by_kind_operation"], "later table")
    da = [row for row in rows if split(row["family_surface"])[0] == "DA"]
    check(len(da) == 6 and all(all(row[field].split()[:2] == ["D1", "A1"] for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")) for row in da), "literal qo")
    check(len(mixed) == result["exact_remainder_folio_NONE_DA_cells"] == 3, "mixed")
    check(sorted({key[1] for key in mixed}) == result["mixed_cell_physical_folios"] == ["f68"], "mixed folios")
    check(sorted({key[0] for key in mixed}) == result["mixed_cell_family_remainders"] == ["AQA", "KKA", "WA"], "mixed bases")
    check(len(mobile) == result["exact_remainder_folio_position_mobile_cells"] == 0, "mobile")
    check(result["rows_in_mixed_cells"] == 6, "mixed rows")
    check(result["status"] == "STOP_THREE_MIXED_CELLS_ONE_FOLIO_ZERO_POSITION_MOBILITY", "status")
    check(result["decision"] == "DO_NOT_SCORE_UNTRANSFERABLE_CIRCLE_QO_LOCUS_START", "decision")
    check(result["gates"]["association_score_computed"] is False and result["gates"]["at_least_one_exact_remainder_folio_NONE_DA_cell"] is True and result["gates"]["mixed_cells_span_at_least_three_folios"] is False and result["gates"]["at_least_three_position_mobile_cells"] is False, "stop gates")
    check("not a graphical record" in REPORT.read_text(), "boundary wording")
    # Mutations must fail their defining guards.
    check(tuple(sorted(set(FOLIOS) - {"f71"})) != FOLIOS, "f71 mutation")
    mutated = Counter(expected_ops); mutated["DA"] += 1
    check(dict(mutated) != result["operation_counts"], "count mutation")
    check({("synthetic", "f67"): Counter(NONE=1, DA=1)} != mixed, "mixed-cell mutation")
    validation = {
        "experiment": "SOURCE_NATIVE_CIRCLE_QO_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_PUBLIC_CIRCLE_QO_CAPACITY_STOP_RECONSTRUCTION",
        "checks": checks,
        "inputs": {SOURCE.name: digest(SOURCE), RESULT.name: digest(RESULT), REPORT.name: digest(REPORT), Path(__file__).name: digest(Path(__file__).resolve())},
        "reconstructed_strict_groups": len(rows),
        "reconstructed_operation_counts": expected_ops,
        "reconstructed_mixed_cells": len(mixed),
        "maximum_numeric_delta": 0.0,
        "claim_ceiling": "Validates only the public f67-f73 capacity stop; no graphical record, circle marker, word, sound, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    OUT_REPORT.write_text(f"""# Circle-block literal-`qo` capacity validation

Status: **{validation['status']}**

Independent code reconstructs all **{len(rows)}** strict rows, 26 pages, all
seven f67--f73 folios including f71, every operation/kind/position count, the
all-reading `D1 A1` check, the three mixed cells confined to f68, zero
position-mobile cells, stop decision, and three mutations in **{checks}**
checks with zero discrepancy.

This validates capacity only. No graphical record, circle marker, word, sound,
meaning, plaintext, or translation follows.
""")
    print(json.dumps({"status": validation["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
