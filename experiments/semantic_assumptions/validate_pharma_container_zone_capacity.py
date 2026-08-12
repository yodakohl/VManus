#!/usr/bin/env python3
"""Independent compact validation of the container-zone source-capacity stop."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
METHOD = BASE / "PHARMA_CONTAINER_ZONE_CAPACITY_METHOD.md"
SOURCE = BASE / "results/existing_human_exact_locus_annotations.tsv"
RESULT = BASE / "results/pharma_container_zone_capacity.json"
REPORT = BASE / "results/pharma_container_zone_capacity_report.md"
OUT_JSON = BASE / "results/pharma_container_zone_capacity_validation.json"
OUT_MD = BASE / "results/pharma_container_zone_capacity_validation_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main() -> None:
    checks: list[str] = []
    selected: list[tuple[str, str, str, str]] = []
    bottom = re.compile(
        r"^(?:On body of container, bottom \(wider\) section\.|On container, bottom half\.|"
        r"On container, bottom \((?:wider|widest|smaller)\) (?:section|part)(?:, line [123])?\.|"
        r"Label on container, bottom \(wider\) part\.|On container, bottom bulge\.)"
    )
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["certainty"] != "UNHEDGED" or not row["normalized_code"].endswith("Lc"):
                continue
            comment = row["local_comment"]
            state = None
            if comment.startswith(("On top lid.", "On container, top (bigger) part.")):
                state = "T"
            elif bottom.match(comment):
                state = "B"
            if state:
                physical_folio = re.match(r"f\d+", row["page"])
                assert physical_folio
                selected.append((row["page"], physical_folio.group(0), row["unit"], state))
    assert Counter(item[3] for item in selected) == Counter({"B": 13, "T": 2})
    checks.append("exact_conservative_source_rows")

    units = set(selected)
    assert Counter(item[3] for item in units) == Counter({"B": 11, "T": 2})
    checks.append("numbered_lower_lines_collapsed")
    folios = defaultdict(set)
    pages = defaultdict(set)
    unit_states = defaultdict(set)
    for page, physical_folio, unit, state in units:
        folios[state].add(physical_folio)
        pages[page].add(state)
        unit_states[(page, unit)].add(state)
    assert folios == {"T": {"f99", "f102"}, "B": {"f99", "f102"}}
    assert {page for page, states in pages.items() if len(states) == 2} == {"f99r", "f102v2"}
    assert {key for key, states in unit_states.items() if len(states) == 2} == {("f102v2", "C1")}
    checks.append("folio_page_and_container_support")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["counts"] == {
        "balanced_page_opportunities": 2,
        "bottom_physical_folios": 2,
        "bottom_source_rows": 13,
        "bottom_unit_state_observations": 11,
        "minimum_one_sided_mixed_folio_sign_p": 0.25,
        "mixed_individual_container_units": 1,
        "mixed_pages": 2,
        "mixed_physical_folios": 2,
        "physical_unit_state_observations": 13,
        "selected_source_rows": 15,
        "top_physical_folios": 2,
        "top_source_rows": 2,
        "top_unit_state_observations": 2,
    }
    checks.append("aggregate_counts_reconstructed")
    assert result["gates"] == {
        "at_least_20_balanced_page_opportunities": False,
        "at_least_3_mixed_individual_container_units": False,
        "at_least_5_mixed_pages": False,
        "both_states_on_at_least_5_physical_folios": False,
    }
    assert result["status"] == "STOP_TWO_FOLIOS_TWO_MIXED_PAGES_ONE_MIXED_CONTAINER"
    checks.append("four_failed_gates_and_stop")
    assert result["source_access"] == {
        "allowed_fields": ["certainty", "local_comment", "locus", "normalized_code", "page", "unit"],
        "alternate_readings_treated_as_replicates": False,
        "family_surface_accessed": False,
        "member_code_accessed": False,
        "root_or_role_accessed": False,
        "voynich_transcription_accessed": False,
    }
    checks.append("source_only_access_contract")
    assert result["inputs"] == {
        "experiments/semantic_assumptions/PHARMA_CONTAINER_ZONE_CAPACITY_METHOD.md": sha(METHOD),
        "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv": sha(SOURCE),
    }
    checks.append("input_bindings")
    expected_report = (
        "# Pharmaceutical container-zone capacity\n\n"
        "Status: **STOP — TWO FOLIOS, TWO MIXED PAGES, ONE MIXED CONTAINER**.\n\n"
        "The conservative source-only rule finds 15 directly annotated label rows: two on an upper physical "
        "container part and 13 on a lower part. Collapsing the three numbered lines on one lower container part "
        "leaves 13 physical unit-state observations (2 TOP, 11 BOTTOM). TOP occurs only on f99 and f102. Only "
        "f99r and f102v2 contain both states, and only f102v2.C1 places separate TOP and BOTTOM inscriptions on "
        "the same individual container. There are two balanced page opportunities, and the best two-folio "
        "one-sided sign orbit has minimum p=1/4=.25.\n\n"
        "All four worth gates fail. No Voynich transcription, family, member, root, role, or formal feature was "
        "opened. This does not establish a lid/top/bottom/container word, plaintext, meaning, or translation.\n"
    )
    assert REPORT.read_text(encoding="utf-8") == expected_report
    checks.append("report_bytes_reconstructed")

    assert len(checks) == 8
    validation = {
        "experiment": "PHARMA_CONTAINER_ZONE_CAPACITY_VALIDATION",
        "schema": "PHARMA_CONTAINER_ZONE_CAPACITY_VALIDATION_V1",
        "status": "PASS_8_CHECK_INDEPENDENT_SOURCE_ONLY_RECONSTRUCTION",
        "check_count": 8,
        "checks": checks,
        "validated_result_sha256": sha(RESULT),
        "validated_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only the source-capacity stop and supplies no translation.",
    }
    OUT_JSON.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# Pharmaceutical container-zone capacity validation\n\n"
        "Status: **PASS — 8 independent source-only checks**.\n\n"
        "Independent code reconstructs the conservative TOP/BOTTOM rows, physical-unit collapse, folio/page/unit "
        "support, counts, four failed gates, access contract, bindings, and exact report. It supplies no part word, "
        "meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
