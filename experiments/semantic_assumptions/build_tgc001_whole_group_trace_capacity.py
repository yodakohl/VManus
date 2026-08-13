#!/usr/bin/env python3
"""Build the score-blind TGC001 whole-group trace capacity panel."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RES = BASE / "results"
METHOD = BASE / "TGC001_WHOLE_GROUP_TRACE_GRAPH_CAPACITY_METHOD.md"
SOURCE = RES / "source_sta_family_consensus_groups.tsv"
SOURCE_VALIDATION = RES / "source_sta_family_consensus_validation.json"
IGR1_SELECTION = RES / "igr001_image_grounded_grapheme_selection.json"
OUT_PANEL = RES / "tgc001_whole_group_trace_capacity_panel.tsv"
OUT = RES / "tgc001_whole_group_trace_capacity.json"
REPORT = RES / "tgc001_whole_group_trace_capacity_report.md"

EXPECTED = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    IGR1_SELECTION: "6837ed894969452dc138f433fd52e3399d468de48bb654e805ebab6b8ded96aa",
}
PANEL_FIELDS = [
    "opaque_group_id", "cell_index", "physical_folio", "page", "locus",
    "consensus_group_id", "consensus_group_index", "consensus_group_count",
    "symbol_count", "selection_rank_sha256",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.match(r"^(f(?:Ros|[0-9]+))", page, re.I)
    if not match:
        raise ValueError(page)
    return match.group(1).lower()


def triplet(row: dict[str, str]) -> tuple[str, str, str]:
    return row["zl_sta_codes"], row["it_sta_codes"], row["rf_sta_codes"]


def cell(row: dict[str, str]) -> tuple[str, str, str]:
    return row["family_surface"], row["currier"] or "BLANK", row["hand"] or "BLANK"


def rank(row: dict[str, str]) -> str:
    return hashlib.sha256(("TGC001_GROUP_V1|" + row["consensus_group_id"]).encode()).hexdigest()


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
    for output in (OUT_PANEL, OUT, REPORT):
        if output.exists():
            raise SystemExit(f"refusing overwrite: {output.name}")
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f"input drift: {path.name}")
    validation = json.loads(SOURCE_VALIDATION.read_text())
    if not validation["status"].startswith("PASS_"):
        raise SystemExit("source consensus validation is not PASS")
    igr1 = json.loads(IGR1_SELECTION.read_text())
    closed = {
        (row["family"], row["zl_code"], row["it_code"], row["rf_code"])
        for row in igr1["targets"]
    }
    if len(closed) != 8:
        raise SystemExit("IGR001/2 closed-type registry drift")

    source = list(csv.DictReader(SOURCE.open(newline=""), delimiter="\t"))
    base = [
        row for row in source
        if row["strict_zero_alternative"] == "1"
        and row["grammar_scope"] == "CONFIRMED_PROSE"
        and 1 <= int(row["symbol_count"]) <= 8
    ]
    disagreement = [row for row in base if len(set(triplet(row))) > 1]
    if len(base) != 21841 or len({folio(row["page"]) for row in base}) != 94:
        raise SystemExit("base count drift")
    if len(disagreement) != 2997 or len({folio(row["page"]) for row in disagreement}) != 93:
        raise SystemExit("disagreement count drift")

    shell_folios: dict[str, set[str]] = defaultdict(set)
    triplet_folios: dict[tuple[str, str, str, str], set[str]] = defaultdict(set)
    by_cell: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in disagreement:
        pf = folio(row["page"])
        shell_folios[row["family_surface"]].add(pf)
        triplet_folios[(row["family_surface"], *triplet(row))].add(pf)
        by_cell[cell(row)].append(row)

    nonduplicate = [row for row in disagreement if all(pattern not in closed for pattern in disagreement_patterns(row))]
    qualifying = []
    for key, rows in by_cell.items():
        rows = [row for row in rows if row in nonduplicate]
        cell_folios = {folio(row["page"]) for row in rows}
        variants = {triplet(row) for row in rows}
        if len(cell_folios) >= 6:
            qualifying.append({
                "key": key, "rows": rows, "folios": cell_folios,
                "variants": len(variants),
            })
    if len(nonduplicate) != 676 or len({folio(row["page"]) for row in nonduplicate}) != 91:
        raise SystemExit("nonduplicate count drift")
    if len(qualifying) != 5 or sum(len(item["rows"]) for item in qualifying) != 32:
        raise SystemExit("controlled-cell count drift")
    qualifying.sort(key=lambda item: (
        -len(item["folios"]), -len(item["rows"]),
        tuple(value.encode("utf-8") for value in item["key"]),
    ))
    retained = qualifying

    panel = []
    private_cells = []
    for cell_index, item in enumerate(retained, 1):
        selected, used = [], set()
        for row in sorted(item["rows"], key=rank):
            pf = folio(row["page"])
            if pf in used:
                continue
            used.add(pf)
            selected.append(row)
            if len(selected) == 6:
                break
        if len(selected) != 6:
            raise SystemExit("six-folio selection failure")
        private_cells.append({
            "cell_index": cell_index,
            "family_surface": item["key"][0], "currier": item["key"][1],
            "hand": item["key"][2], "groups": len(item["rows"]),
            "folios": len(item["folios"]), "triplet_variants": item["variants"],
        })
        for row in selected:
            digest = rank(row)
            panel.append({
                "opaque_group_id": "TGC" + hashlib.sha256(("TGC001_OPAQUE_V1|" + row["consensus_group_id"]).encode()).hexdigest()[:16].upper(),
                "cell_index": cell_index,
                "physical_folio": folio(row["page"]), "page": row["page"],
                "locus": row["locus"], "consensus_group_id": row["consensus_group_id"],
                "consensus_group_index": int(row["consensus_group_index"]),
                "consensus_group_count": int(row["consensus_group_count"]),
                "symbol_count": int(row["symbol_count"]),
                "selection_rank_sha256": digest,
            })
    if len(panel) != 30 or any(count != 6 for count in Counter(row["cell_index"] for row in panel).values()):
        raise SystemExit("panel cardinality drift")

    with OUT_PANEL.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PANEL_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(panel)

    counts = {
        "base_groups": len(base),
        "base_folios": len({folio(row["page"]) for row in base}),
        "disagreement_groups": len(disagreement),
        "symbol_positions_in_disagreement_groups": sum(int(row["symbol_count"]) for row in disagreement),
        "disagreeing_symbol_positions": sum(len(disagreement_patterns(row)) for row in disagreement),
        "disagreement_folios": len({folio(row["page"]) for row in disagreement}),
        "family_shells": len(shell_folios),
        "family_shells_five_folios": sum(len(value) >= 5 for value in shell_folios.values()),
        "groups_in_five_folio_shells": sum(len(shell_folios[row["family_surface"]]) >= 5 for row in disagreement),
        "ordered_triplet_types": len(triplet_folios),
        "ordered_triplet_types_five_folios": sum(len(value) >= 5 for value in triplet_folios.values()),
        "groups_in_five_folio_triplets": sum(len(triplet_folios[(row["family_surface"], *triplet(row))]) >= 5 for row in disagreement),
        "nonduplicate_disagreement_groups": len(nonduplicate),
        "nonduplicate_disagreement_folios": len({folio(row["page"]) for row in nonduplicate}),
        "qualifying_controlled_cells": len(qualifying),
        "groups_in_qualifying_cells": sum(len(item["rows"]) for item in qualifying),
        "folios_in_qualifying_cells": len({folio(row["page"]) for item in qualifying for row in item["rows"]}),
        "retained_cells": len(retained), "maximum_selected_groups": len(panel),
        "selected_physical_folios": len({row["physical_folio"] for row in panel}),
    }
    result = {
        "access": {
            "image_bodies_opened": False, "manual_internal_symbol_target_selected": False,
            "trace_graphs_created": False, "zl_it_rf_target_score_opened": False,
        },
        "calibration_required": {
            "geometry_cells": 5, "folios_per_cell": 6,
            "null_worlds": 128, "distributed_plant_worlds": 100,
            "minimum_plant_recovery_rate": 0.9, "maximum_null_full_passes": 1,
        },
        "claim_ceiling": "Source-only nonduplicate 30-group geometry for target-free calibration. No physical trace, preferred reading, glyph identity, allography, sound, alphabet, word, language, cipher, plaintext, meaning, or translation follows.",
        "counts": counts,
        "decision": "AUTHORIZE_TARGET_FREE_SYNTHETIC_GEOMETRY_CALIBRATION_ONLY_PUBLISHED_ROWS_IMAGE_INELIGIBLE",
        "experiment": "TGC001_WHOLE_GROUP_TRACE_GRAPH_CAPACITY",
        "inputs": {str(path.relative_to(BASE.parents[1])): sha(path) for path in (*EXPECTED, METHOD, Path(__file__).resolve())},
        "private_controlled_cell_metadata": private_cells,
        "published_panel_image_eligibility": "PERMANENTLY_INELIGIBLE_FUTURE_IMAGE_PANEL_MUST_EXCLUDE_ALL_30_ROWS",
        "selection_rule": "all nonduplicate cells with six folios; first six distinct folios per cell by TGC001_GROUP_V1 SHA256 rank",
        "status": "HOLD_5_CELL_30_GROUP_GEOMETRY_PENDING_TARGET_FREE_CALIBRATION",
        "outputs": {str(OUT_PANEL.relative_to(BASE.parents[1])): sha(OUT_PANEL)},
    }
    OUT.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    REPORT.write_text(
        "# TGC001 whole-group trace-graph capacity\n\n"
        f"Status: **{result['status']}**.\n\n"
        f"The source-only universe contains {counts['disagreement_groups']:,} short confirmed-prose disagreement groups on {counts['disagreement_folios']} physical folios. After deleting every group containing any of the eight IGR001-selected types carried into IGR002, {counts['nonduplicate_disagreement_groups']} groups remain. Five exact family/Currier/hand cells reach six folios, yielding a 30-group geometry on {counts['selected_physical_folios']} physical folios.\n\n"
        "This geometry now requires target-free synthetic power calibration; it is not yet authorized for image access. No manuscript image, trace graph, internal-symbol box, preferred reading, glyph identity, sound, language, plaintext, meaning, or translation was opened.\n"
    )
    print(json.dumps({"status": result["status"], **counts}, sort_keys=True))


if __name__ == "__main__":
    main()
