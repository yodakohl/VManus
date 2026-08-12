#!/usr/bin/env python3
"""Independent reconstruction of the FPR001 target-masked capacity result."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
METHOD = BASE / "FPR001_FIFTH_RELATION_ORDERED_ROOT_CAPACITY_METHOD.md"
INTERLINEAR = BASE / "results/pre_grounding_interlinear.tsv"
LOCI = BASE / "results/pre_grounding_locus_atlas.tsv"
OWNERSHIP = BASE / "results/f102r1_fifth_repeated_plant_label_native_visual_ownership.json"
CAPACITY5 = BASE / "results/five_pair_ordered_multiroot_capacity.json"
RESULT = BASE / "results/fpr001_fifth_relation_ordered_root_capacity.json"
REPORT = BASE / "results/fpr001_fifth_relation_ordered_root_capacity_report.md"
OUT = BASE / "results/fpr001_fifth_relation_ordered_root_capacity_validation.json"
OUT_MD = BASE / "results/fpr001_fifth_relation_ordered_root_capacity_validation_report.md"
QUERY = ("ot", "od", "e", "od", "or")
EDITIONS = ("ZL3b", "IT2a", "RF1b")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def lcs(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, x in enumerate(a, 1):
        for j, y in enumerate(b, 1):
            table[i][j] = table[i - 1][j - 1] + 1 if x == y else max(table[i - 1][j], table[i][j - 1])
    return table[-1][-1]


def main() -> None:
    checks: list[str] = []
    with LOCI.open(newline="", encoding="utf-8") as handle:
        target = next(row for row in csv.DictReader(handle, delimiter="\t") if row["locus"] == "f37v.1")
    assert (target["page"], target["section"], target["currier"], target["hand"], target["readings_present"]) == (
        "f37v", "H", "A", "1", "ZL3b;IT2a;RF1b"
    )
    checks.append("target_metadata_only")

    page_edges = {e: defaultdict(Counter) for e in EDITIONS}
    maxima = {e: defaultdict(int) for e in EDITIONS}
    skipped = 0
    with INTERLINEAR.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] == "f37v":
                skipped += 1
                continue
            if (row["section"], row["currier"], row["hand"], row["grammar_scope"]) != (
                "H", "A", "1", "CONFIRMED_PROSE"
            ):
                continue
            e = row["edition"]
            for word in row["root_sequence"].split():
                atoms = tuple(word.split("+"))
                maxima[e][row["page"]] = max(maxima[e][row["page"]], lcs(QUERY, atoms))
                for edge in zip(QUERY, QUERY[1:]):
                    page_edges[e][row["page"]][edge] += sum(atoms[i:i + 2] == edge for i in range(len(atoms) - 1))
    assert skipped == 69
    checks.append("all_target_rows_skipped_before_formal_index")

    supports = {}
    nonzero = {}
    histograms = {}
    for e in EDITIONS:
        pages = set(page_edges[e]) | set(maxima[e])
        assert len(pages) == 94
        supports[e] = [sum(page_edges[e][page][edge] > 0 for page in pages) for edge in zip(QUERY, QUERY[1:])]
        nonzero[e] = sum(any(page_edges[e][page].values()) for page in pages)
        histograms[e] = Counter(maxima[e][page] for page in pages)
    assert supports == {"ZL3b": [16, 3, 18, 6], "IT2a": [15, 2, 17, 6], "RF1b": [16, 3, 15, 4]}
    assert nonzero == {"ZL3b": 30, "IT2a": 30, "RF1b": 29}
    assert histograms == {"ZL3b": Counter({2: 55, 1: 39}), "IT2a": Counter({2: 56, 1: 38}), "RF1b": Counter({2: 53, 1: 41})}
    checks.append("background_support_and_variability")

    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    assert stored["capacity"] == {
        "minimum_inclusive_rank_p": 1 / 95,
        "target_plus_background_pages": 95,
        "target_rows_skipped_before_formal_field_index": 69,
    }
    checks.append("rank_floor_and_counts")
    assert all(stored["gates"].values()) and stored["status"] == "PASS_TARGET_PAGE_MASKED_CAPACITY"
    checks.append("six_gates_and_decision")
    assert stored["target_access"] == {
        "alternate_readings_treated_as_replicates": False,
        "f37v_formal_interlinear_indexed": False,
        "f37v_metadata_accessed_from_locus_atlas": True,
        "f37v_query_match_computed": False,
        "f37v_rank_computed": False,
        "f37v_root_sequence_indexed": False,
        "f37v_score_computed": False,
        "f37v_surface_indexed": False,
    }
    checks.append("target_access_contract")
    assert stored["inputs"] == {str(p.relative_to(ROOT)): sha(p) for p in (METHOD, INTERLINEAR, LOCI, OWNERSHIP, CAPACITY5)}
    checks.append("input_bindings")
    expected_report = (
        "# FPR001 fifth-relation ordered-root capacity\n\n"
        "Status: **PASS — TARGET PAGE MASKED**.\n\n"
        "The new fixed f102r1.2→f37v relation supplies an exposed five-root query while f37v formal content remains "
        "unopened. Every reading has 94 exact H/Currier-A/hand-1 background pages. The four adjacent query edges "
        "occur on 16/15/16, 3/2/3, 18/17/15, and 6/6/4 pages in ZL3b/IT2a/RF1b; 30/30/29 pages have at least "
        "one edge. Background page maxima vary between ordered-root LCS 1 and 2, and no background word reaches "
        "LCS 3. The inclusive target-plus-background rank floor is 1/95=.010526, so the registered ceiling is .02, "
        "not .01.\n\n"
        "All six gates pass. This authorizes only a compact target-blind synthetic calibration and no f37v score. "
        "It supplies no plant name, word, plaintext, meaning, or translation.\n"
    )
    assert REPORT.read_text(encoding="utf-8") == expected_report
    checks.append("report_bytes_reconstructed")
    assert len(checks) == 8
    validation = {
        "experiment": "FPR001_FIFTH_RELATION_ORDERED_ROOT_CAPACITY_VALIDATION",
        "schema": "FPR001_FIFTH_RELATION_ORDERED_ROOT_CAPACITY_VALIDATION_V1",
        "status": "PASS_8_CHECK_INDEPENDENT_TARGET_MASKED_RECONSTRUCTION",
        "check_count": 8,
        "checks": checks,
        "validated_result_sha256": sha(RESULT),
        "validated_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only target-masked capacity and supplies no translation.",
    }
    OUT.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# FPR001 fifth-relation ordered-root capacity validation\n\n"
        "Status: **PASS — 8 independent target-masked checks**.\n\n"
        "Independent code reconstructs target metadata, the pre-formal-field f37v exclusion, all background edge "
        "supports and LCS histograms, exact rank floor, gates, access contract, bindings, and report. No f37v score, "
        "plant name, plaintext, meaning, or translation is supplied.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
