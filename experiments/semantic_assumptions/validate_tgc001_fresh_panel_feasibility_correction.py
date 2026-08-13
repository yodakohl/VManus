#!/usr/bin/env python3
"""Independent reconstruction of the TGC001 fresh-panel stop."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RES = BASE / "results"
METHOD = BASE / "TGC001_FRESH_PANEL_FEASIBILITY_CORRECTION.md"
BUILDER = BASE / "build_tgc001_fresh_panel_feasibility_correction.py"
SOURCE = RES / "source_sta_family_consensus_groups.tsv"
IGR1 = RES / "igr001_image_grounded_grapheme_selection.json"
PANEL = RES / "tgc001_whole_group_trace_capacity_panel.tsv"
CAPACITY = RES / "tgc001_whole_group_trace_capacity.json"
RESULT = RES / "tgc001_fresh_panel_feasibility_correction.json"
REPORT = RES / "tgc001_fresh_panel_feasibility_correction_report.md"
OUT = RES / "tgc001_fresh_panel_feasibility_correction_validation.json"
OUT_REPORT = RES / "tgc001_fresh_panel_feasibility_correction_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.match(r"^(f(?:Ros|[0-9]+))", page, re.I)
    if not match:
        raise ValueError(page)
    return match.group(1).lower()


def row_cell(row: dict[str, str]) -> tuple[str, str, str]:
    return row["family_surface"], row["currier"] or "BLANK", row["hand"] or "BLANK"


def patterns(row: dict[str, str]) -> list[tuple[str, str, str, str]]:
    values = zip(
        row["family_surface"], row["zl_sta_codes"].split(),
        row["it_sta_codes"].split(), row["rf_sta_codes"].split(),
    )
    return [(family, zl, it, rf) for family, zl, it, rf in values if len({zl, it, rf}) > 1]


def check(condition: bool, name: str, checks: list[str]) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {name}")
    checks.append(name)


def main() -> None:
    for path in (OUT, OUT_REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path.name}")
    checks: list[str] = []
    result = json.loads(RESULT.read_text())
    capacity = json.loads(CAPACITY.read_text())
    selection = json.loads(IGR1.read_text())
    panel = list(csv.DictReader(PANEL.open(newline=""), delimiter="\t"))
    closed = {(row["family"], row["zl_code"], row["it_code"], row["rf_code"]) for row in selection["targets"]}
    keys = {
        (row["family_surface"], row["currier"], row["hand"]): row["cell_index"]
        for row in capacity["private_controlled_cell_metadata"]
    }
    check(len(keys) == 5 and len(panel) == 30, "published_geometry_5_cells_30_rows", checks)
    published_ids = {row["consensus_group_id"] for row in panel}
    published_folios = {row["physical_folio"] for row in panel}
    check(len(published_ids) == 30 and len(published_folios) == 28, "published_ids_and_folios_unique_counts", checks)

    eligible: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    with SOURCE.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            ps = patterns(row)
            if (
                row["strict_zero_alternative"] == "1"
                and row["grammar_scope"] == "CONFIRMED_PROSE"
                and 1 <= int(row["symbol_count"]) <= 8
                and ps and all(value not in closed for value in ps)
                and row_cell(row) in keys
            ):
                eligible[row_cell(row)].append(row)

    rebuilt_cells = []
    rebuilt_residual = []
    for key, index in sorted(keys.items(), key=lambda item: item[1]):
        rows = eligible[key]
        unused = [row for row in rows if row["consensus_group_id"] not in published_ids]
        fresh = [row for row in rows if physical_folio(row["page"]) not in published_folios]
        rebuilt_cells.append({
            "cell_index": index, "family_surface": key[0], "currier": key[1], "hand": key[2],
            "eligible_rows": len(rows),
            "published_rows": sum(row["consensus_group_id"] in published_ids for row in rows),
            "unused_rows": len(unused),
            "unused_distinct_folios": len({physical_folio(row["page"]) for row in unused}),
            "whole_folio_fresh_rows": len(fresh),
            "whole_folio_fresh_distinct_folios": len({physical_folio(row["page"]) for row in fresh}),
        })
        rebuilt_residual.extend({
            "cell_index": index,
            "consensus_group_id": row["consensus_group_id"],
            "physical_folio": physical_folio(row["page"]),
        } for row in unused)
    rebuilt_residual.sort(key=lambda row: row["consensus_group_id"])
    check([row["eligible_rows"] for row in rebuilt_cells] == [7, 7, 6, 6, 6], "eligible_rows_7_7_6_6_6", checks)
    check([row["published_rows"] for row in rebuilt_cells] == [6, 6, 6, 6, 6], "published_rows_6_each", checks)
    check([row["unused_rows"] for row in rebuilt_cells] == [1, 1, 0, 0, 0], "unused_rows_1_1_0_0_0", checks)
    check(all(row["whole_folio_fresh_rows"] == 0 for row in rebuilt_cells), "zero_whole_folio_fresh_rows", checks)
    check(rebuilt_cells == result["cells"], "result_cells_exact", checks)
    check(rebuilt_residual == result["residual_rows"], "result_residual_rows_exact", checks)
    check(result["counts"] == {
        "eligible_rows_in_five_cells": 32,
        "minimum_required_distinct_folios_per_cell": 6,
        "minimum_required_rows": 30,
        "published_rows_permanently_image_ineligible": 30,
        "unused_cells": 2,
        "unused_distinct_folios": 2,
        "unused_exact_rows": 2,
        "whole_folio_fresh_rows": 0,
    }, "result_counts_exact", checks)
    check(result["decision"] == "STOP_BEFORE_SYNTHETIC_CALIBRATION_AND_IMAGE_ACCESS", "stop_decision", checks)
    check(result["status"] == "STOP_FRESH_PANEL_IMPOSSIBLE_2_ROWS_ZERO_WHOLE_FOLIO_FRESH", "stop_status", checks)
    expected_inputs = {
        str(path.relative_to(BASE.parents[1])): sha(path)
        for path in (SOURCE, IGR1, PANEL, CAPACITY, METHOD, BUILDER)
    }
    check(result["inputs"] == expected_inputs, "input_hashes_exact", checks)
    check(result["access"] == {
        "image_bodies_opened": False,
        "synthetic_calibration_run": False,
        "trace_graphs_created": False,
        "zl_it_rf_target_score_opened": False,
    }, "access_closed", checks)
    check(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n" == RESULT.read_text(), "result_canonical", checks)
    report_text = REPORT.read_text()
    check("cannot be formed" in report_text and "no preferred reading" in report_text.lower(), "report_ceiling", checks)

    payload = {
        "checks": checks,
        "checks_passed": len(checks),
        "decision": result["decision"],
        "inputs": {str(path.relative_to(BASE.parents[1])): sha(path) for path in (METHOD, BUILDER, RESULT, REPORT)},
        "status": "PASS_INDEPENDENT_FRESH_PANEL_STOP_RECONSTRUCTION",
    }
    OUT.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    OUT_REPORT.write_text(
        "# TGC001 fresh-panel correction validation\n\n"
        f"Status: **{payload['status']}**.\n\n"
        f"Independent source-only reconstruction passes {len(checks)} checks. The five cells contain 32 eligible rows, the 30 published image-ineligible rows leave only two exact rows, and zero rows remain on wholly fresh folios. The proposed fresh 30-row panel is impossible.\n\n"
        "No image, trace, preferred reading, glyph identity, sound, language, plaintext, meaning, or translation follows.\n"
    )
    print(json.dumps({"status": payload["status"], "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
