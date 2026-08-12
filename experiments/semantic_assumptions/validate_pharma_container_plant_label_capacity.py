#!/usr/bin/env python3
"""Independent minimal reconstruction of pharma container/plant-label capacity."""

from __future__ import annotations

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
OUT_JSON = BASE / "results/pharma_container_plant_label_capacity_validation.json"
OUT_MD = BASE / "results/pharma_container_plant_label_capacity_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def folio(page: str) -> str:
    return re.match(r"f\d+", page).group(0)  # type: ignore[union-attr]


def main() -> None:
    checks: list[str] = []
    by_locus: dict[str, list[tuple[str, str, int, int, int, str]]] = defaultdict(list)
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["code"].endswith(("Lc", "Lf")):
                by_locus[row["locus"]].append((
                    row["page"], row["code"], int(row["consensus_group_index"]),
                    int(row["consensus_group_count"]), int(row["symbol_count"]),
                    row["strict_zero_alternative"],
                ))
    loci: list[tuple[str, str, tuple[int, ...]]] = []
    excluded = 0
    for groups in by_locus.values():
        groups.sort(key=lambda item: item[2])
        if any(item[5] != "1" for item in groups):
            excluded += 1
            continue
        assert len(groups) == groups[0][3] and [item[2] for item in groups] == list(range(1, len(groups) + 1))
        loci.append((groups[0][0], "C" if groups[0][1].endswith("Lc") else "F", tuple(item[4] for item in groups)))
    assert len(loci) == 194 and excluded == 8 and Counter(item[1] for item in loci) == Counter({"F": 167, "C": 27})
    checks.append("exact_zero_alternative_projection")

    cells: dict[tuple[str, tuple[int, ...]], list[str]] = defaultdict(list)
    for page, label_class, signature in loci:
        cells[(page, signature)].append(label_class)
    mixed = {key: values for key, values in cells.items() if set(values) == {"C", "F"}}
    assert len(mixed) == 15 and sum(len(values) for values in mixed.values()) == 53
    assert len({key[0] for key in mixed}) == 9
    checks.append("exact_page_length_cells")

    retained: Counter[str] = Counter()
    pairs: Counter[str] = Counter()
    orbit = 0.0
    for (page, _), values in mixed.items():
        counts = Counter(values)
        retained[folio(page)] += len(values)
        pairs[folio(page)] += min(counts.values())
        orbit += math.log2(math.comb(len(values), counts["C"]))
    assert retained == Counter({"f89": 27, "f99": 15, "f88": 7, "f102": 4})
    assert pairs == Counter({"f89": 10, "f99": 5, "f88": 3, "f102": 1})
    assert abs(orbit - 29.24194242999032) < 1e-12
    checks.append("folio_counts_pairs_and_orbit")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["counts"] == {
        "balanced_pair_opportunities": 19,
        "eligible_container_loci": 27,
        "eligible_plant_fragment_loci": 167,
        "eligible_zero_alternative_loci": 194,
        "excluded_loci_with_alternatives": 8,
        "minimum_one_sided_whole_folio_sign_p": 0.0625,
        "mixed_page_length_cells": 15,
        "physical_folios": 4,
        "product_orbit_log2": 29.24194242999,
        "retained_mixed_loci": 53,
        "retained_pages": 9,
    }
    checks.append("aggregate_counts_reconstructed")
    assert result["gates"] == {
        "at_least_20_balanced_pair_opportunities": False,
        "at_least_6_physical_folios": False,
        "maximum_balanced_pair_folio_share_at_most_0_35": False,
        "maximum_retained_locus_folio_share_at_most_0_35": False,
        "whole_folio_sign_orbit_can_attain_p_at_most_0_05": False,
    }
    checks.append("five_failed_transfer_gates")
    assert result["source_projection"] == {
        "allowed_fields": ["code", "consensus_group_count", "consensus_group_index", "locus", "page", "strict_zero_alternative", "symbol_count"],
        "alternate_readings_treated_as_replicates": False,
        "family_surface_accessed": False,
        "literal_transcription_accessed": False,
        "member_codes_accessed": False,
        "root_or_role_sequence_accessed": False,
    }
    checks.append("filler_blind_access_contract")
    assert result["inputs"] == {
        "experiments/semantic_assumptions/PHARMA_CONTAINER_PLANT_LABEL_CAPACITY_METHOD.md": sha(METHOD),
        "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv": sha(SOURCE),
    }
    assert result["status"] == "STOP_FOUR_FOLIOS_NINETEEN_PAIRS_AND_F89_CONCENTRATION"
    checks.append("bindings_and_stop_reconstructed")
    expected_report = (
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
    assert REPORT.read_text(encoding="utf-8") == expected_report
    checks.append("report_bytes_reconstructed")

    assert len(checks) == 8
    validation = {
        "experiment": "PHARMA_CONTAINER_PLANT_LABEL_CAPACITY_VALIDATION",
        "schema": "PHARMA_CONTAINER_PLANT_LABEL_CAPACITY_VALIDATION_V1",
        "status": "PASS_8_CHECK_INDEPENDENT_FILLER_BLIND_RECONSTRUCTION",
        "check_count": 8,
        "checks": checks,
        "validated_result_sha256": sha(RESULT),
        "validated_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only the filler-blind capacity stop and supplies no translation.",
    }
    OUT_JSON.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# Pharmaceutical container/plant-label capacity validation\n\n"
        "Status: **PASS — 8 independent filler-blind checks**.\n\n"
        "Independent code reconstructs the zero-alternative projection, exact page/length cells, folio opportunities, "
        "orbit, counts, five failed transfer gates, filler-blind access contract, bindings, stop, and report bytes. It "
        "supplies no owner class marker, word, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
