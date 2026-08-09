#!/usr/bin/env python3
"""Audit exact-remainder capacity for bare DA inside public f67--f73."""

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
SOURCE_VALIDATION = RES / "source_sta_family_consensus_validation.json"
CIRCLE = RES / "source_native_circle_block_diagnostic.json"
CIRCLE_VALIDATION = RES / "source_native_circle_block_diagnostic_validation.json"
SPEC = BASE / "SOURCE_NATIVE_CIRCLE_QO_CAPACITY_SPEC.md"
OUT = RES / "source_native_circle_qo_capacity.json"
REPORT = RES / "source_native_circle_qo_capacity_report.md"
FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    CIRCLE: "72c5f85616898256746b72f1d88bbad4dfb5edb2b2711bd660285b7a0ebea2a8",
    CIRCLE_VALIDATION: "c79cfe72741883e6e469b51687f8c8fca14f5379cdbaaa0b0718157a7ae83c17",
}
PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
FOLIOS = tuple(f"f{i}" for i in range(67, 74))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if not match:
        raise ValueError("invalid page")
    return match.group(1)


def operation(surface: str) -> tuple[str, str]:
    for prefix in PREFIXES:
        if surface.startswith(prefix):
            return prefix, surface[len(prefix):]
    return "NONE", surface


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    for path, digest in FROZEN.items():
        if sha(path) != digest:
            raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(SOURCE_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION":
        raise SystemExit("source validation")
    circle = json.loads(CIRCLE.read_text())
    if circle["public_folios"] != list(FOLIOS) or circle["public_page_rows"] != 26:
        raise SystemExit("public circle scope")
    if json.loads(CIRCLE_VALIDATION.read_text())["status"] != "PASS_AUDITOR_FREE_18_ROW_PUBLIC_CIRCLE_BLOCK_RECONSTRUCTION":
        raise SystemExit("circle validation")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        all_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(all_rows) != 26184 or len({row["consensus_group_id"] for row in all_rows}) != 26184:
        raise SystemExit("source identity")
    rows = [row for row in all_rows if row["strict_zero_alternative"] == "1" and folio(row["page"]) in FOLIOS]
    operation_counts = Counter(operation(row["family_surface"])[0] for row in rows)
    folio_counts = Counter(folio(row["page"]) for row in rows)
    kind_counts = Counter(row["kind"] for row in rows)
    first_counts = Counter((row["kind"], operation(row["family_surface"])[0]) for row in rows if row["consensus_group_index"] == "1")
    later_counts = Counter((row["kind"], operation(row["family_surface"])[0]) for row in rows if row["consensus_group_index"] != "1")
    cells: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in rows:
        state, remainder = operation(row["family_surface"])
        if remainder and state in {"NONE", "DA"}:
            cells[(remainder, folio(row["page"]))][state] += 1
            cells[(remainder, folio(row["page"]))][f"{state}_{'FIRST' if row['consensus_group_index'] == '1' else 'LATER'}"] += 1
    mixed = {key: value for key, value in cells.items() if value["NONE"] and value["DA"]}
    mobile = {key: value for key, value in mixed.items() if all(value[f"{state}_{position}"] for state in ("NONE", "DA") for position in ("FIRST", "LATER"))}
    da_rows = [row for row in rows if operation(row["family_surface"])[0] == "DA"]
    da_prefix_consensus = sum(
        all(tuple(row[field].split()[:2]) == ("D1", "A1") for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes"))
        for row in da_rows
    )
    gates = {
        "complete_f67_through_f73_including_f71": tuple(sorted(set(map(lambda row: folio(row["page"]), rows)))) == FOLIOS,
        "exact_26_public_pages": len({row["page"] for row in rows}) == 26,
        "all_rows_diagnostic_nonprose": {row["grammar_scope"] for row in rows} == {"DIAGNOSTIC_NONPROSE"},
        "all_bare_DA_is_all_reading_D1_A1": da_prefix_consensus == len(da_rows),
        "at_least_one_exact_remainder_folio_NONE_DA_cell": bool(mixed),
        "mixed_cells_span_at_least_three_folios": len({key[1] for key in mixed}) >= 3,
        "at_least_three_position_mobile_cells": len(mobile) >= 3,
        "association_score_computed": False,
    }
    result = {
        "experiment": "SOURCE_NATIVE_CIRCLE_QO_CAPACITY",
        "status": "STOP_THREE_MIXED_CELLS_ONE_FOLIO_ZERO_POSITION_MOBILITY",
        "decision": "DO_NOT_SCORE_UNTRANSFERABLE_CIRCLE_QO_LOCUS_START",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, Path(__file__).resolve())},
        "physical_folios": list(FOLIOS),
        "source_pages": len({row["page"] for row in rows}),
        "strict_groups": len(rows),
        "strict_loci": len({row["locus"] for row in rows}),
        "folio_group_counts": dict(sorted(folio_counts.items())),
        "kind_group_counts": {kind: kind_counts[kind] for kind in "CLPR"},
        "operation_counts": {state: operation_counts[state] for state in ("NONE", "DA", "DAQ", "DAQK", "DAQKJ")},
        "first_counts_by_kind_operation": {f"{kind}|{state}": first_counts[kind, state] for kind in "CLPR" for state in ("NONE", "DA", "DAQ", "DAQK", "DAQKJ")},
        "later_counts_by_kind_operation": {f"{kind}|{state}": later_counts[kind, state] for kind in "CLPR" for state in ("NONE", "DA", "DAQ", "DAQK", "DAQKJ")},
        "bare_DA_all_reading_D1_A1_rows": da_prefix_consensus,
        "exact_remainder_folio_NONE_DA_cells": len(mixed),
        "mixed_cell_physical_folios": sorted({key[1] for key in mixed}),
        "mixed_cell_family_remainders": sorted({key[0] for key in mixed}),
        "exact_remainder_folio_position_mobile_cells": len(mobile),
        "rows_in_mixed_cells": sum(sum(value[state] for state in ("NONE", "DA")) for value in mixed.values()),
        "gates": gates,
        "claim_ceiling": "Capacity stop only: public f67-f73 has three exact-remainder/folio NONE-versus-bare-DA cells, all on f68, with zero first/later-mobile cells. Locus-first is not graphical-record-first; no circle marker, word, sound, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Circle-block literal-`qo` capacity audit

Status: **{result['status']}**

The complete public f67--f73 block (including f71) contributes **{len(rows)}**
strict source groups across **{result['source_pages']}** pages and **{len(FOLIOS)}**
physical folios. Longest-opening states are `NONE/DA/DAQ/DAQK/DAQKJ` =
**{operation_counts['NONE']}/{operation_counts['DA']}/{operation_counts['DAQ']}/{operation_counts['DAQK']}/{operation_counts['DAQKJ']}**.
All **{len(da_rows)}** bare-`DA` rows begin all-reading `D1 A1`, the literal
transcription-level `qo` construction.

There are **{len(mixed)}** exact-remainder/physical-folio cells containing both
`NONE` and bare `DA`, but all three are on **f68**, and **{len(mobile)}** have
first/later mobility in both states. Therefore no transferable matched
circle-specific locus-start test is identifiable and no association score was
computed. `consensus_group_index=1` denotes only a
source-transcription locus/line start, not a graphical record or authorial
circular start.

This stop supplies no circle marker, wordhood, detachment, sound, language,
cipher, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "strict_groups": len(rows), "mixed_cells": len(mixed)}, sort_keys=True))


if __name__ == "__main__":
    main()
