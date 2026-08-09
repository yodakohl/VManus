#!/usr/bin/env python3
"""Masked local-context audit of the duplicated Taurus-page repeat."""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

B = Path(__file__).resolve().parent
R = B / "results"
ALIGN = R / "source_sta_group_alignment.tsv"
META = R / "source_separator_transcription.tsv"
SPECIFICITY = R / "zodiac_duplicate_candidate_specificity.json"
METHOD = B / "ZODIAC_TAURUS_REPEAT_CONTEXT_METHOD.md"
OUT = R / "zodiac_taurus_repeat_context.json"
REPORT = R / "zodiac_taurus_repeat_context_report.md"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
LOCI = ("f71v.1", "f72r1.1")
TARGET = "AQJABABA"
RADII = (1, 2, 3, 5, 8)
VIEWS = ("FAMILY_N2", "FAMILY_N3", "FAMILY_N4", "MEMBER_N1", "MEMBER_N2", "MEMBER_N3")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def context(sequence: list[dict[str, object]], center: int, radius: int, view: str) -> Counter[str]:
    result: Counter[str] = Counter()
    size = int(view.rsplit("N", 1)[1])
    family_view = view.startswith("FAMILY")
    for distance in range(1, radius + 1):
        for index in ((center - distance) % len(sequence), (center + distance) % len(sequence)):
            row = sequence[index]
            if row["family"] == TARGET:
                continue
            units = list(str(row["family"])) if family_view else list(row["members"])
            for start in range(len(units) - size + 1):
                result["".join(units[start:start+size]) if family_view else "-".join(units[start:start+size])] += 1
    return result


def similarity(left: Counter[str], right: Counter[str]) -> float:
    inventory = sorted(set(left).union(right))
    denominator = sum(max(left[item], right[item]) for item in inventory)
    return sum(min(left[item], right[item]) for item in inventory) / denominator if denominator else 0.0


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    metadata_rows = read_tsv(META)
    metadata = {row["source_group_id"]: row for row in metadata_rows}
    if len(metadata) != len(metadata_rows):
        raise AssertionError("duplicate metadata group ID")

    sequences: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in read_tsv(ALIGN):
        info = metadata.get(row["source_group_id"])
        if info is None:
            raise AssertionError("alignment group missing metadata")
        if row["locus"] not in LOCI or int(row["alternative_site_count"]):
            continue
        if info["kind"] != "C":
            raise AssertionError("target locus is not circular text")
        sequences[(row["locus"], row["edition"])].append({
            "index": int(row["source_group_index"]),
            "family": row["primary_sta_families"],
            "members": row["primary_sta_codes"].split(),
            "nearest_basic_eva": row["nearest_basic_eva_primary"],
            "source_group_id": row["source_group_id"],
        })
    if set(sequences) != {(locus, edition) for locus in LOCI for edition in EDITIONS}:
        raise AssertionError("incomplete target sequence panel")
    for key, sequence in sequences.items():
        sequence.sort(key=lambda row: int(row["index"]))
        indices = [int(row["index"]) for row in sequence]
        if indices != sorted(set(indices)):
            raise AssertionError(f"nonunique or unordered group sequence: {key}")
        if sum(row["family"] == TARGET for row in sequence) != 1:
            raise AssertionError(f"target multiplicity changed: {key}")

    specificity = json.loads(SPECIFICITY.read_text())
    family_support = next(item for item in specificity["candidate_support"] if item["candidate_id"] == "TAURUS|FAMILY_GROUP|AQJABABA")
    if family_support["page_count"] != 2 or family_support["physical_locus_count"] != 2:
        raise AssertionError("frozen global target support changed")

    grid = []
    positions = {}
    neighbors = {}
    for edition in EDITIONS:
        left = sequences[(LOCI[0], edition)]
        right = sequences[(LOCI[1], edition)]
        li = next(index for index, row in enumerate(left) if row["family"] == TARGET)
        ri = next(index for index, row in enumerate(right) if row["family"] == TARGET)
        positions[edition] = {
            LOCI[0]: {"ordinal": li + 1, "group_count": len(left)},
            LOCI[1]: {"ordinal": ri + 1, "group_count": len(right)},
        }
        neighbors[edition] = {
            LOCI[0]: {"previous": left[(li - 1) % len(left)]["nearest_basic_eva"], "next": left[(li + 1) % len(left)]["nearest_basic_eva"]},
            LOCI[1]: {"previous": right[(ri - 1) % len(right)]["nearest_basic_eva"], "next": right[(ri + 1) % len(right)]["nearest_basic_eva"]},
        }
        for radius in RADII:
            for view in VIEWS:
                observed = similarity(context(left, li, radius, view), context(right, ri, radius, view))
                reference = [
                    similarity(context(left, i, radius, view), context(right, j, radius, view))
                    for i in range(len(left)) for j in range(len(right))
                ]
                inclusive = 1 + sum(value > observed for value in reference)
                tied = sum(value == observed for value in reference)
                strict = inclusive + tied - 1
                midrank = (inclusive + strict) / 2
                grid.append({
                    "edition": edition, "radius": radius, "view": view,
                    "similarity": observed, "reference_pairs": len(reference),
                    "inclusive_rank": inclusive, "strict_rank": strict,
                    "tied": tied, "midrank_percentile": midrank / len(reference),
                })

    edition_summary = {}
    for edition in EDITIONS:
        selected = [row for row in grid if row["edition"] == edition]
        edition_summary[edition] = {
            "cells": len(selected),
            "median_midrank_percentile": statistics.median(row["midrank_percentile"] for row in selected),
            "top_decile_cells": sum(row["midrank_percentile"] <= 0.10 for row in selected),
            "top_quartile_cells": sum(row["midrank_percentile"] <= 0.25 for row in selected),
        }
    median_midrank = statistics.median(row["midrank_percentile"] for row in grid)
    top_decile = sum(row["midrank_percentile"] <= 0.10 for row in grid)
    best = min(grid, key=lambda row: (row["midrank_percentile"], row["edition"], row["radius"], row["view"]))

    result = {
        "experiment": "ZODIAC_TAURUS_REPEAT_CONTEXT",
        "status": "POSTHOC_NO_CONSISTENT_HOMOLOGOUS_CONTEXT_SUPPORT",
        "decision": "DO_NOT_PROMOTE_REPEAT_TO_DIAGRAM_FIELD_OR_SIGN_NAME",
        "inputs": {path.name: sha(path) for path in (ALIGN, META, SPECIFICITY, METHOD, Path(__file__))},
        "target": TARGET, "loci": list(LOCI), "positions": positions, "immediate_neighbors": neighbors,
        "design": {"radii": list(RADII), "views": list(VIEWS), "target_masked_from_every_context": True, "cyclic_and_reversal_invariant": True},
        "grid": grid,
        "summary": {
            "cells": len(grid), "median_midrank_percentile": median_midrank,
            "top_decile_cells": top_decile, "top_quartile_cells": sum(row["midrank_percentile"] <= 0.25 for row in grid),
            "best_cell": best, "by_edition": edition_summary,
        },
        "gates": {
            "exact_one_target_per_locus_and_reading": True,
            "target_masked_from_reference_contexts": True,
            "median_midrank_at_most_one_tenth": median_midrank <= 0.10,
            "at_least_half_cells_top_decile_in_every_reading": all(item["top_decile_cells"] >= 15 for item in edition_summary.values()),
            "homologous_context_supported": False,
            "zero_english_glosses": True,
        },
        "claim_ceiling": "Masked local circular-context compatibility only; no freely positioned content inference, sign name, word, meaning, sound, language, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Taurus-repeat masked context\n\n"
        "Status: **POSTHOC_NO_CONSISTENT_HOMOLOGOUS_CONTEXT_SUPPORT**\n\n"
        f"After masking `AQJABABA` from every context, its two positions have median tie-aware rank percentile **{median_midrank:.4f}** across all 90 reading/radius/view cells. Only **{top_decile}/90** cells reach the top decile; ZL3b, IT2a, and RF1b contribute {edition_summary['ZL3b']['top_decile_cells']}, {edition_summary['IT2a']['top_decile_cells']}, and {edition_summary['RF1b']['top_decile_cells']} respectively. The best isolated cell is {best['edition']} radius {best['radius']} {best['view']} at percentile {best['midrank_percentile']:.4f}.\n\n"
        "The exact repeat therefore does not occupy a consistently homologous local field in the two circular sequences under these representations. It remains possible as a freely positioned item, but it cannot be promoted to TAURUS, a sign name, a word, or a translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "median_midrank": median_midrank, "top_decile": top_decile}, sort_keys=True))


if __name__ == "__main__":
    main()
