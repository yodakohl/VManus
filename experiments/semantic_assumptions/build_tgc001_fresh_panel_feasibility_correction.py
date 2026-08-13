#!/usr/bin/env python3
"""Reconstruct the fresh-panel capacity that TGC001 requires."""
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
SOURCE = RES / "source_sta_family_consensus_groups.tsv"
IGR1 = RES / "igr001_image_grounded_grapheme_selection.json"
PANEL = RES / "tgc001_whole_group_trace_capacity_panel.tsv"
CAPACITY = RES / "tgc001_whole_group_trace_capacity.json"
OUT = RES / "tgc001_fresh_panel_feasibility_correction.json"
REPORT = RES / "tgc001_fresh_panel_feasibility_correction_report.md"

EXPECTED = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    IGR1: "6837ed894969452dc138f433fd52e3399d468de48bb654e805ebab6b8ded96aa",
    PANEL: "1b5393da5c246acfc7a61a9d555241dcd37ed8f593286776696544d2c0a17d97",
    CAPACITY: "45887681c67c1e0b7973ab39c18e94e1f3ff4682e1a1b3cb851ad5fcd71abce6",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.match(r"^(f(?:Ros|[0-9]+))", page, re.I)
    if not match:
        raise ValueError(page)
    return match.group(1).lower()


def cell(row: dict[str, str]) -> tuple[str, str, str]:
    return row["family_surface"], row["currier"] or "BLANK", row["hand"] or "BLANK"


def disagreement_patterns(row: dict[str, str]) -> list[tuple[str, str, str, str]]:
    return [
        (family, zl, it, rf)
        for family, zl, it, rf in zip(
            row["family_surface"], row["zl_sta_codes"].split(),
            row["it_sta_codes"].split(), row["rf_sta_codes"].split(),
        )
        if len({zl, it, rf}) > 1
    ]


def main() -> None:
    for path in (OUT, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path.name}")
    for path, expected in EXPECTED.items():
        if digest(path) != expected:
            raise SystemExit(f"input drift: {path.name}")

    capacity = json.loads(CAPACITY.read_text())
    panel = list(csv.DictReader(PANEL.open(newline=""), delimiter="\t"))
    igr1 = json.loads(IGR1.read_text())
    closed = {
        (row["family"], row["zl_code"], row["it_code"], row["rf_code"])
        for row in igr1["targets"]
    }
    keys = {
        (row["family_surface"], row["currier"], row["hand"]): row["cell_index"]
        for row in capacity["private_controlled_cell_metadata"]
    }
    if len(keys) != 5 or len(panel) != 30:
        raise SystemExit("published geometry drift")
    published_ids = {row["consensus_group_id"] for row in panel}
    published_folios = {row["physical_folio"] for row in panel}

    eligible: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in csv.DictReader(SOURCE.open(newline=""), delimiter="\t"):
        patterns = disagreement_patterns(row)
        if (
            row["strict_zero_alternative"] == "1"
            and row["grammar_scope"] == "CONFIRMED_PROSE"
            and 1 <= int(row["symbol_count"]) <= 8
            and patterns
            and all(pattern not in closed for pattern in patterns)
            and cell(row) in keys
        ):
            eligible[cell(row)].append(row)

    cells = []
    residual_rows = []
    for key, cell_index in sorted(keys.items(), key=lambda item: item[1]):
        rows = eligible[key]
        unused = [row for row in rows if row["consensus_group_id"] not in published_ids]
        whole_folio_fresh = [row for row in rows if folio(row["page"]) not in published_folios]
        for row in unused:
            residual_rows.append({
                "cell_index": cell_index,
                "consensus_group_id": row["consensus_group_id"],
                "physical_folio": folio(row["page"]),
            })
        cells.append({
            "cell_index": cell_index,
            "family_surface": key[0], "currier": key[1], "hand": key[2],
            "eligible_rows": len(rows),
            "published_rows": sum(row["consensus_group_id"] in published_ids for row in rows),
            "unused_rows": len(unused),
            "unused_distinct_folios": len({folio(row["page"]) for row in unused}),
            "whole_folio_fresh_rows": len(whole_folio_fresh),
            "whole_folio_fresh_distinct_folios": len({folio(row["page"]) for row in whole_folio_fresh}),
        })

    if [row["unused_rows"] for row in cells] != [1, 1, 0, 0, 0]:
        raise SystemExit("fresh-row count drift")
    if any(row["whole_folio_fresh_rows"] for row in cells):
        raise SystemExit("whole-folio freshness drift")
    if sorted((row["consensus_group_id"], row["physical_folio"]) for row in residual_rows) != [
        ("f104r.19|C010", "f104"), ("f85r1.32|C007", "f85")
    ]:
        raise SystemExit("residual identity drift")

    result = {
        "access": {
            "image_bodies_opened": False,
            "synthetic_calibration_run": False,
            "trace_graphs_created": False,
            "zl_it_rf_target_score_opened": False,
        },
        "cells": cells,
        "claim_ceiling": "Stops only the proposed same-five-cell fresh TGC001 panel. No physical trace, preferred reading, glyph identity, sound, language, plaintext, meaning, or translation follows.",
        "counts": {
            "eligible_rows_in_five_cells": sum(row["eligible_rows"] for row in cells),
            "published_rows_permanently_image_ineligible": len(published_ids),
            "unused_exact_rows": sum(row["unused_rows"] for row in cells),
            "unused_cells": sum(row["unused_rows"] > 0 for row in cells),
            "unused_distinct_folios": len({row["physical_folio"] for row in residual_rows}),
            "whole_folio_fresh_rows": sum(row["whole_folio_fresh_rows"] for row in cells),
            "minimum_required_rows": 30,
            "minimum_required_distinct_folios_per_cell": 6,
        },
        "decision": "STOP_BEFORE_SYNTHETIC_CALIBRATION_AND_IMAGE_ACCESS",
        "experiment": "TGC001_FRESH_PANEL_FEASIBILITY_CORRECTION",
        "inputs": {
            str(path.relative_to(BASE.parents[1])): digest(path)
            for path in (*EXPECTED, METHOD, Path(__file__).resolve())
        },
        "residual_rows": sorted(residual_rows, key=lambda row: row["consensus_group_id"]),
        "status": "STOP_FRESH_PANEL_IMPOSSIBLE_2_ROWS_ZERO_WHOLE_FOLIO_FRESH",
        "supersedes_decision": capacity["decision"],
    }
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# TGC001 fresh-panel feasibility correction\n\n"
        f"Status: **{result['status']}**.\n\n"
        "The five frozen cells contain only 32 eligible rows. The public geometry permanently consumed 30 for image blinding, leaving one unused row in AC/B/2, one in AQAC/B/3, and none in the other three cells. Both residual rows lie on folios already exposed by the public panel, so whole-folio-fresh capacity is zero.\n\n"
        "The promised fresh five-cell by six-folio image panel cannot be formed. TGC001 stops before target-free synthetic calibration, image access, trace annotation, or manuscript scoring. This supplies no preferred reading, glyph identity, sound, language, plaintext, meaning, or translation.\n"
    )
    print(json.dumps({"status": result["status"], **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
