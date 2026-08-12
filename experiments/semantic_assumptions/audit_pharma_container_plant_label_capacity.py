#!/usr/bin/env python3
"""Filler-blind capacity audit for container- vs plant-associated pharma labels."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
METHOD = BASE / "PHARMA_CONTAINER_PLANT_LABEL_CAPACITY_METHOD.md"
SOURCE = BASE / "results/source_sta_family_consensus_groups.tsv"
RESULT = BASE / "results/pharma_container_plant_label_capacity.json"
REPORT = BASE / "results/pharma_container_plant_label_capacity_report.md"
ALLOWED = {
    "locus", "page", "code", "strict_zero_alternative", "consensus_group_index",
    "consensus_group_count", "symbol_count",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def folio(page: str) -> str:
    match = re.match(r"f\d+", page)
    if not match:
        raise RuntimeError(("nonnumeric page", page))
    return match.group(0)


def build() -> tuple[dict[str, object], str]:
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not ALLOWED.issubset(reader.fieldnames or []):
            raise RuntimeError("source schema")
        for source_row in reader:
            code = source_row["code"]
            if not (code.endswith("Lc") or code.endswith("Lf")):
                continue
            row = {key: source_row[key] for key in ALLOWED}
            by_locus[row["locus"]].append(row)

    loci: list[dict[str, object]] = []
    excluded_alternative = 0
    for locus, groups in by_locus.items():
        groups.sort(key=lambda row: int(row["consensus_group_index"]))
        if any(row["strict_zero_alternative"] != "1" for row in groups):
            excluded_alternative += 1
            continue
        first = groups[0]
        expected = int(first["consensus_group_count"])
        if len(groups) != expected or [int(row["consensus_group_index"]) for row in groups] != list(range(1, expected + 1)):
            raise RuntimeError(("group order", locus))
        if any(row["page"] != first["page"] or row["code"] != first["code"] for row in groups):
            raise RuntimeError(("locus metadata", locus))
        loci.append({
            "locus": locus,
            "page": first["page"],
            "folio": folio(first["page"]),
            "class": "CONTAINER_ASSOCIATED" if first["code"].endswith("Lc") else "PLANT_FRAGMENT_ASSOCIATED",
            "length_signature": tuple(int(row["symbol_count"]) for row in groups),
        })

    cells: dict[tuple[str, tuple[int, ...]], list[dict[str, object]]] = defaultdict(list)
    for row in loci:
        cells[(str(row["page"]), tuple(row["length_signature"]))].append(row)
    mixed = {key: rows for key, rows in cells.items() if len({str(row["class"]) for row in rows}) == 2}

    retained_by_folio: Counter[str] = Counter()
    pairs_by_folio: Counter[str] = Counter()
    orbit_log2 = 0.0
    cell_rows: list[dict[str, object]] = []
    for (page, signature), rows in sorted(mixed.items()):
        counts = Counter(str(row["class"]) for row in rows)
        pair_count = min(counts.values())
        physical_folio = folio(page)
        retained_by_folio[physical_folio] += len(rows)
        pairs_by_folio[physical_folio] += pair_count
        orbit_log2 += math.log2(math.comb(len(rows), counts["CONTAINER_ASSOCIATED"]))
        cell_rows.append({
            "page": page,
            "physical_folio": physical_folio,
            "length_signature": list(signature),
            "container_loci": counts["CONTAINER_ASSOCIATED"],
            "plant_fragment_loci": counts["PLANT_FRAGMENT_ASSOCIATED"],
            "balanced_pair_opportunities": pair_count,
        })

    retained_total = sum(retained_by_folio.values())
    pair_total = sum(pairs_by_folio.values())
    folio_count = len(retained_by_folio)
    max_retained_share = max(retained_by_folio.values()) / retained_total
    max_pair_share = max(pairs_by_folio.values()) / pair_total
    gates = {
        "at_least_20_balanced_pair_opportunities": pair_total >= 20,
        "at_least_6_physical_folios": folio_count >= 6,
        "maximum_retained_locus_folio_share_at_most_0_35": max_retained_share <= 0.35,
        "maximum_balanced_pair_folio_share_at_most_0_35": max_pair_share <= 0.35,
        "whole_folio_sign_orbit_can_attain_p_at_most_0_05": folio_count >= 5,
    }
    status = (
        "PASS_SCORE_BLIND_CAPACITY" if all(gates.values())
        else "STOP_FOUR_FOLIOS_NINETEEN_PAIRS_AND_F89_CONCENTRATION"
    )

    result: dict[str, object] = {
        "experiment": "PHARMA_CONTAINER_PLANT_LABEL_CAPACITY",
        "schema": "PHARMA_CONTAINER_PLANT_LABEL_CAPACITY_V1",
        "status": status,
        "decision": "DO_NOT_OPEN_CONTAINER_VERSUS_PLANT_LABEL_FEATURE_ASSOCIATION",
        "source_projection": {
            "allowed_fields": sorted(ALLOWED),
            "family_surface_accessed": False,
            "member_codes_accessed": False,
            "literal_transcription_accessed": False,
            "root_or_role_sequence_accessed": False,
            "alternate_readings_treated_as_replicates": False,
        },
        "counts": {
            "eligible_zero_alternative_loci": len(loci),
            "excluded_loci_with_alternatives": excluded_alternative,
            "eligible_container_loci": sum(row["class"] == "CONTAINER_ASSOCIATED" for row in loci),
            "eligible_plant_fragment_loci": sum(row["class"] == "PLANT_FRAGMENT_ASSOCIATED" for row in loci),
            "mixed_page_length_cells": len(mixed),
            "retained_mixed_loci": retained_total,
            "retained_pages": len({page for page, _ in mixed}),
            "physical_folios": folio_count,
            "balanced_pair_opportunities": pair_total,
            "product_orbit_log2": round(orbit_log2, 12),
            "minimum_one_sided_whole_folio_sign_p": 1 / (2 ** folio_count),
        },
        "retained_loci_by_folio": dict(sorted(retained_by_folio.items())),
        "balanced_pair_opportunities_by_folio": dict(sorted(pairs_by_folio.items())),
        "maximum_retained_locus_folio_share": max_retained_share,
        "maximum_balanced_pair_folio_share": max_pair_share,
        "cells": cell_rows,
        "gates": gates,
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(SOURCE.relative_to(ROOT)): sha(SOURCE),
        },
        "claim_ceiling": (
            "The exact page-and-length matched container-associated versus plant-fragment-associated label panel is too "
            "small and folio-concentrated for a transferable formal-marker test. No container word, plant word, owner, "
            "name, identifier, noun, sound, language, cipher, plaintext, meaning, or translation follows."
        ),
    }
    report = (
        "# Pharmaceutical container/plant-label capacity\n\n"
        "Status: **STOP — FOUR FOLIOS, 19 BALANCED PAIRS, F89 CONCENTRATION**.\n\n"
        "A filler-blind projection of the validated consensus-group table retains 194 zero-alternative `Lc`/`Lf` loci. "
        "Exact page and ordered group-length matching leaves 15 mixed cells, 53 loci, and 19 balanced pair opportunities "
        "on four physical folios. f89 supplies 27/53 retained loci and 10/19 balanced pairs; maximum shares are 0.509434 "
        "and 0.526316. A one-sided four-folio sign orbit cannot attain p <= .05 (minimum 1/16=.0625).\n\n"
        "The 29.2419-bit within-cell assignment orbit is numerically large but cannot manufacture independent folios. "
        "All five frozen transfer gates fail, so no family, member, literal, root, role, or formal-feature association "
        "was opened. No container word, plant word, owner, identifier, meaning, plaintext, or translation follows.\n"
    )
    return result, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result, report = build()
    if args.write:
        RESULT.write_bytes(canonical(result))
        REPORT.write_text(report, encoding="utf-8")
    else:
        print(canonical(result).decode(), end="")


if __name__ == "__main__":
    main()
