#!/usr/bin/env python3
"""Independent reconstruction of the masked Taurus-repeat context audit."""

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
PRODUCER = B / "audit_zodiac_taurus_repeat_context.py"
RESULT = R / "zodiac_taurus_repeat_context.json"
PRODUCER_REPORT = R / "zodiac_taurus_repeat_context_report.md"
OUT = R / "zodiac_taurus_repeat_context_validation.json"
REPORT = R / "zodiac_taurus_repeat_context_validation_report.md"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
LOCI = ("f71v.1", "f72r1.1")
TARGET = "AQJABABA"
RADII = (1, 2, 3, 5, 8)
VIEWS = ("FAMILY_N2", "FAMILY_N3", "FAMILY_N4", "MEMBER_N1", "MEMBER_N2", "MEMBER_N3")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def fingerprint(sequence: list[dict[str, object]], origin: int, radius: int, view: str) -> Counter[str]:
    out: Counter[str] = Counter()
    width = int(view[-1])
    use_family = view[0] == "F"
    for offset in range(1, radius + 1):
        for position in ((origin - offset) % len(sequence), (origin + offset) % len(sequence)):
            record = sequence[position]
            if record["family"] == TARGET:
                continue
            atoms = list(str(record["family"])) if use_family else list(record["members"])
            for start in range(0, len(atoms) - width + 1):
                key = "".join(atoms[start:start+width]) if use_family else "-".join(atoms[start:start+width])
                out[key] += 1
    return out


def weighted_overlap(left: Counter[str], right: Counter[str]) -> float:
    keys = sorted(set(left) | set(right))
    union = sum(max(left[key], right[key]) for key in keys)
    return sum(min(left[key], right[key]) for key in keys) / union if union else 0.0


def score_grid(panel: dict[tuple[str, str], list[dict[str, object]]]) -> list[dict[str, object]]:
    output = []
    for edition in EDITIONS:
        first, second = panel[(LOCI[0], edition)], panel[(LOCI[1], edition)]
        first_target = next(i for i, row in enumerate(first) if row["family"] == TARGET)
        second_target = next(i for i, row in enumerate(second) if row["family"] == TARGET)
        for radius in RADII:
            for view in VIEWS:
                observed = weighted_overlap(fingerprint(first, first_target, radius, view), fingerprint(second, second_target, radius, view))
                orbit = []
                for left_index in range(len(first)):
                    left = fingerprint(first, left_index, radius, view)
                    for right_index in range(len(second)):
                        orbit.append(weighted_overlap(left, fingerprint(second, right_index, radius, view)))
                inclusive = 1 + sum(value > observed for value in orbit)
                ties = sum(value == observed for value in orbit)
                strict = inclusive + ties - 1
                output.append({
                    "edition": edition, "radius": radius, "view": view, "similarity": observed,
                    "reference_pairs": len(orbit), "inclusive_rank": inclusive, "strict_rank": strict,
                    "tied": ties, "midrank_percentile": ((inclusive + strict) / 2) / len(orbit),
                })
    return output


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    checks = []

    def check(value: bool, name: str) -> None:
        if not value:
            raise AssertionError(name)
        checks.append(name)

    meta_rows = table(META)
    meta = {row["source_group_id"]: row for row in meta_rows}
    check(len(meta) == len(meta_rows), "unique_metadata_ids")
    panel: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in table(ALIGN):
        info = meta.get(row["source_group_id"])
        check(info is not None, f"metadata_present:{row['source_group_id']}")
        if row["locus"] not in LOCI or int(row["alternative_site_count"]):
            continue
        check(info["kind"] == "C", f"circular_role:{row['source_group_id']}")
        panel[(row["locus"], row["edition"])].append({
            "index": int(row["source_group_index"]), "family": row["primary_sta_families"],
            "members": row["primary_sta_codes"].split(), "nearest_basic_eva": row["nearest_basic_eva_primary"],
            "source_group_id": row["source_group_id"],
        })
    check(set(panel) == {(locus, edition) for locus in LOCI for edition in EDITIONS}, "complete_six_sequence_panel")
    for key, sequence in panel.items():
        sequence.sort(key=lambda row: int(row["index"]))
        indices = [int(row["index"]) for row in sequence]
        check(indices == sorted(set(indices)), f"unique_ordered_indices:{key}")
        check(sum(row["family"] == TARGET for row in sequence) == 1, f"one_target:{key}")

    specificity = json.loads(SPECIFICITY.read_text())
    support = next(item for item in specificity["candidate_support"] if item["candidate_id"] == "TAURUS|FAMILY_GROUP|AQJABABA")
    check(support["page_count"] == support["physical_locus_count"] == 2, "global_support_two_pages_two_loci")

    grid = score_grid(panel)
    check(len(grid) == 90, "exact_90_cells")
    positions, neighbors = {}, {}
    for edition in EDITIONS:
        positions[edition], neighbors[edition] = {}, {}
        for locus in LOCI:
            sequence = panel[(locus, edition)]
            index = next(i for i, row in enumerate(sequence) if row["family"] == TARGET)
            positions[edition][locus] = {"ordinal": index + 1, "group_count": len(sequence)}
            neighbors[edition][locus] = {
                "previous": sequence[(index - 1) % len(sequence)]["nearest_basic_eva"],
                "next": sequence[(index + 1) % len(sequence)]["nearest_basic_eva"],
            }
    by_edition = {}
    for edition in EDITIONS:
        part = [row for row in grid if row["edition"] == edition]
        by_edition[edition] = {
            "cells": len(part), "median_midrank_percentile": statistics.median(float(row["midrank_percentile"]) for row in part),
            "top_decile_cells": sum(float(row["midrank_percentile"]) <= .10 for row in part),
            "top_quartile_cells": sum(float(row["midrank_percentile"]) <= .25 for row in part),
        }
    median = statistics.median(float(row["midrank_percentile"]) for row in grid)
    top10 = sum(float(row["midrank_percentile"]) <= .10 for row in grid)
    best = min(grid, key=lambda row: (float(row["midrank_percentile"]), str(row["edition"]), int(row["radius"]), str(row["view"])))
    expected = {
        "experiment": "ZODIAC_TAURUS_REPEAT_CONTEXT",
        "status": "POSTHOC_NO_CONSISTENT_HOMOLOGOUS_CONTEXT_SUPPORT",
        "decision": "DO_NOT_PROMOTE_REPEAT_TO_DIAGRAM_FIELD_OR_SIGN_NAME",
        "inputs": {path.name: digest(path) for path in (ALIGN, META, SPECIFICITY, METHOD, PRODUCER)},
        "target": TARGET, "loci": list(LOCI), "positions": positions, "immediate_neighbors": neighbors,
        "design": {"radii": list(RADII), "views": list(VIEWS), "target_masked_from_every_context": True, "cyclic_and_reversal_invariant": True},
        "grid": grid,
        "summary": {
            "cells": len(grid), "median_midrank_percentile": median, "top_decile_cells": top10,
            "top_quartile_cells": sum(float(row["midrank_percentile"]) <= .25 for row in grid),
            "best_cell": best, "by_edition": by_edition,
        },
        "gates": {
            "exact_one_target_per_locus_and_reading": True, "target_masked_from_reference_contexts": True,
            "median_midrank_at_most_one_tenth": median <= .10,
            "at_least_half_cells_top_decile_in_every_reading": all(item["top_decile_cells"] >= 15 for item in by_edition.values()),
            "homologous_context_supported": False, "zero_english_glosses": True,
        },
        "claim_ceiling": "Masked local circular-context compatibility only; no freely positioned content inference, sign name, word, meaning, sound, language, plaintext, or translation.",
    }
    check(json.loads(RESULT.read_text()) == expected, "complete_result_object")
    expected_report = (
        "# Taurus-repeat masked context\n\n"
        "Status: **POSTHOC_NO_CONSISTENT_HOMOLOGOUS_CONTEXT_SUPPORT**\n\n"
        f"After masking `AQJABABA` from every context, its two positions have median tie-aware rank percentile **{median:.4f}** across all 90 reading/radius/view cells. Only **{top10}/90** cells reach the top decile; ZL3b, IT2a, and RF1b contribute {by_edition['ZL3b']['top_decile_cells']}, {by_edition['IT2a']['top_decile_cells']}, and {by_edition['RF1b']['top_decile_cells']} respectively. The best isolated cell is {best['edition']} radius {best['radius']} {best['view']} at percentile {best['midrank_percentile']:.4f}.\n\n"
        "The exact repeat therefore does not occupy a consistently homologous local field in the two circular sequences under these representations. It remains possible as a freely positioned item, but it cannot be promoted to TAURUS, a sign name, a word, or a translation.\n"
    )
    check(PRODUCER_REPORT.read_text() == expected_report, "exact_report_bytes")

    # Full-grid invariance to arbitrary cyclic starts and simultaneous reversal.
    rotated = {}
    reversed_panel = {}
    for key, sequence in panel.items():
        shift = 7 if key[0] == LOCI[0] else 11
        rotated[key] = sequence[shift % len(sequence):] + sequence[:shift % len(sequence)]
        reversed_panel[key] = list(reversed(sequence))
    check(score_grid(rotated) == grid, "full_grid_rotation_invariant")
    check(score_grid(reversed_panel) == grid, "full_grid_simultaneous_reversal_invariant")

    validation = {
        "experiment": "ZODIAC_TAURUS_REPEAT_CONTEXT_VALIDATION", "status": "PASS",
        "checks": len(checks), "failures": 0,
        "reconstructed": {"sequences": 6, "cells": 90, "median_midrank_percentile": median, "top_decile_cells": top10},
        "bindings": {path.name: digest(path) for path in (ALIGN, META, SPECIFICITY, METHOD, PRODUCER, RESULT, PRODUCER_REPORT)},
        "claim_ceiling": expected["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Taurus-repeat context validation\n\n"
        f"Status: **PASS** ({len(checks)} checks, zero failures).\n\n"
        "A nonimporting implementation reconstructs all six circular sequences, 90 masked context cells, every score/rank/tie, the complete result object, and exact report. Full-grid rotation and simultaneous-reversal mutations leave the result unchanged.\n\n"
        "This validates only the lack of consistent homologous local-context support. It supplies no sign name, word, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
