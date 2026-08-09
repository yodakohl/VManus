#!/usr/bin/env python3
"""Build the target-masked source-native edge-coupling capacity panel."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
CONSENSUS_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
EDGE_VALIDATION = RESULTS / "source_native_edge_grammar_validation.json"
ORDER_VALIDATION = RESULTS / "source_native_internal_order_validation.json"
SPEC = BASE / "SOURCE_NATIVE_EDGE_COUPLING_CAPACITY_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT = RESULTS / "source_native_edge_coupling_capacity.json"
PANEL = RESULTS / "source_native_edge_coupling_masked.tsv"
REPORT = RESULTS / "source_native_edge_coupling_capacity_report.md"

FROZEN = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    CONSENSUS_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    EDGE_VALIDATION: "0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712",
    ORDER_VALIDATION: "f41e44fda5d05fbd44a4fabdcfbec077dccdf045cdbbd6c90dad30794c5cf53a",
}
FIELDS = [
    "unit_id", "consensus_group_id", "locus", "page", "physical_folio",
    "section", "currier", "hand", "kind", "locus_position", "symbol_count",
    "length_bin", "opening_family", "core_first_family", "core_last_family",
    "baseline_cell", "full_cell", "masked_family_surface",
    "outside_folio_baseline_support", "outside_folio_full_support", "target_eligible",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def main() -> None:
    if any(path.exists() for path in (OUT, PANEL, REPORT)):
        raise SystemExit("refusing to overwrite edge-coupling capacity")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    if json.loads(CONSENSUS_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION":
        raise SystemExit("consensus validation is not PASS")
    if json.loads(EDGE_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_SOURCE_NATIVE_EDGE_RECONSTRUCTION":
        raise SystemExit("edge validation is not PASS")
    if json.loads(ORDER_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_INTERNAL_ORDER_NONCONFIRM_RECONSTRUCTION":
        raise SystemExit("internal-order validation is not PASS")

    with GROUPS.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    rows = []
    for source in source_rows:
        surface = source["family_surface"]
        if source["strict_zero_alternative"] != "1" or source["grammar_scope"] != "CONFIRMED_PROSE" or len(surface) < 3:
            continue
        folio = re.match(r"f\d+", source["page"])
        if folio is None:
            continue
        index = int(source["consensus_group_index"])
        count = int(source["consensus_group_count"])
        position = "SINGLE" if count == 1 else ("FIRST" if index == 1 else ("LAST" if index == count else "MIDDLE"))
        length_bin = min(len(surface), 8)
        baseline = (surface[1], surface[-2], length_bin, position, source["currier"])
        full = (*baseline, surface[0])
        rows.append({
            "unit_id": source["consensus_group_id"],
            "consensus_group_id": source["consensus_group_id"],
            "locus": source["locus"], "page": source["page"],
            "physical_folio": folio.group(), "section": source["section"],
            "currier": source["currier"], "hand": source["hand"], "kind": source["kind"],
            "locus_position": position, "symbol_count": len(surface), "length_bin": length_bin,
            "opening_family": surface[0], "core_first_family": surface[1],
            "core_last_family": surface[-2],
            "baseline_cell": "|".join(map(str, baseline)),
            "full_cell": "|".join(map(str, full)),
            "masked_family_surface": surface[:-1] + "#",
        })
    rows.sort(key=lambda row: row["unit_id"])
    if len({row["unit_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate unit ID")

    total_baseline = Counter(row["baseline_cell"] for row in rows)
    total_full = Counter(row["full_cell"] for row in rows)
    folio_baseline = Counter((row["physical_folio"], row["baseline_cell"]) for row in rows)
    folio_full = Counter((row["physical_folio"], row["full_cell"]) for row in rows)
    for row in rows:
        base_support = total_baseline[row["baseline_cell"]] - folio_baseline[row["physical_folio"], row["baseline_cell"]]
        full_support = total_full[row["full_cell"]] - folio_full[row["physical_folio"], row["full_cell"]]
        row["outside_folio_baseline_support"] = base_support
        row["outside_folio_full_support"] = full_support
        row["target_eligible"] = int(base_support >= 20 and full_support >= 5)
    if len(rows) != 19203 or sum(row["target_eligible"] for row in rows) != 14955:
        raise ValueError("edge-coupling capacity count drift")
    PANEL.write_bytes(render(rows))

    eligible = [row for row in rows if row["target_eligible"]]
    result = {
        "experiment": "SOURCE_NATIVE_EDGE_COUPLING_CAPACITY",
        "status": "PASS_TARGET_MASKED_EDGE_COUPLING_CAPACITY",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, BUILDER)},
        "all_masked_groups": len(rows),
        "all_physical_folios": len({row["physical_folio"] for row in rows}),
        "eligible_groups": len(eligible),
        "eligible_physical_folios": len({row["physical_folio"] for row in eligible}),
        "eligible_by_currier": dict(sorted(Counter(row["currier"] for row in eligible).items())),
        "eligible_opening_families": len({row["opening_family"] for row in eligible}),
        "eligible_baseline_cells": len({row["baseline_cell"] for row in eligible}),
        "panel_sha256": sha(PANEL),
        "schema": FIELDS,
        "gates": {
            "exact_all_groups": len(rows) == 19203,
            "exact_eligible_groups": len(eligible) == 14955,
            "all_94_folios": len({row["physical_folio"] for row in rows}) == len({row["physical_folio"] for row in eligible}) == 94,
            "both_curriers": set(row["currier"] for row in eligible) == {"A", "B"},
            "at_least_10_opening_families": len({row["opening_family"] for row in eligible}) >= 10,
            "at_least_100_baseline_cells": len({row["baseline_cell"] for row in eligible}) >= 100,
            "every_eligible_supports": all(row["outside_folio_baseline_support"] >= 20 and row["outside_folio_full_support"] >= 5 for row in eligible),
            "one_mask_per_row": all(row["masked_family_surface"].count("#") == 1 for row in rows),
            "target_fields_absent": not ({"closing_family", "final_family", "outcome", "complete_surface", "score", "p_value", "english_gloss"} & set(FIELDS)),
        },
        "target_outcomes_stored": 0, "target_scores_computed": 0, "english_glosses": 0,
        "claim_ceiling": "Target-masked capacity for a leave-folio-out opening-to-closing family proper-score test. No edge coupling, affix, circumfix, agreement, sound, word, language, cipher operation, meaning, plaintext, or translation follows.",
    }
    if not all(result["gates"].values()):
        raise ValueError("capacity gate failure")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Source-native opening/closing edge-coupling capacity

Status: **{result['status']}**

The target-masked panel contains **{len(rows):,}** synchronized prose groups on
**94** physical folios. Exact immediate-core, length, locus-position, Currier,
and leave-folio support gates retain **{len(eligible):,}** groups on all 94
folios, spanning both Currier registers, **{result['eligible_opening_families']}**
opening families, and **{result['eligible_baseline_cells']}** baseline cells.

The final STA family is replaced by `#`; no target outcome, complete surface,
score, p-value, or English gloss is stored. This authorizes synthetic
calibration only and establishes no affix, circumfix, word, language, meaning,
plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "all": len(rows), "eligible": len(eligible), "folios": 94}, sort_keys=True))


if __name__ == "__main__":
    main()
