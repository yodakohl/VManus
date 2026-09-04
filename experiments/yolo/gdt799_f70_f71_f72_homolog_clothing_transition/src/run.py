#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt799_f70_f71_f72_homolog_clothing_transition"
SRC = BASE / "src"
ART = BASE / "artifacts"
GDT796 = ROOT / "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/artifacts/GDT796_OUTER10_BOUNDARY_POSITION_CONTRIBUTIONS.tsv"

KEY = SRC / "BLIND_CROP_KEY.tsv"
R1 = SRC / "VISUAL_REVIEW_R1.tsv"
R2 = SRC / "VISUAL_REVIEW_R2.tsv"
ADJ = SRC / "SOURCE_AWARE_ADJUDICATION.tsv"
F71 = SRC / "FROZEN_F71_F9_STATES.tsv"
EDGE_PACKET = SRC / "GDT388_EMPTY_EDGE_PACKET.tsv"

ACQUISITION = ART / "GDT799_18_BLIND_VISUAL_ACQUISITION.tsv"
TRANSITIONS = ART / "GDT799_9_FIXED_HOMOLOG_TRANSITIONS.tsv"
RANKINGS = ART / "GDT799_400_CLOTHING_TRANSFORM_RANKINGS.tsv"
TESTS = ART / "GDT799_EXACT_TESTS.tsv"
CANDIDATES = ART / "GDT799_CANDIDATE_ADJUDICATION.tsv"
EDGE_AUDIT = ART / "GDT799_GDT388_EDGE_PACKET_AUDIT.json"
RESULT = ART / "RESULT.json"
REPORT = BASE / "REPORT.md"

COVERED = "TORSO_COVERED"
UNCOVERED = "TORSO_UNCOVERED"
UNCERTAIN = "UNCERTAIN"
DECISIVE = {COVERED, UNCOVERED}
TARGET_MEMBERS = (6, 7, 8, 9, 10, 11, 12, 13, 15)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, Any]], fields: Sequence[str]) -> None:
    materialized = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fields})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def f6(value: float) -> str:
    return f"{value:.6f}"


def transforms() -> list[tuple[str, tuple[int, ...]]]:
    return [
        (("R" if orientation == 1 else "F") + str(shift), tuple((orientation * coordinate + shift) % 10 for coordinate in range(10)))
        for orientation in (1, -1)
        for shift in range(10)
    ]


def pair_score(left: Sequence[str | None], right: Sequence[str | None]) -> tuple[int, int]:
    pairs = [(a, b) for a, b in zip(left, right, strict=True) if a in DECISIVE and b in DECISIVE]
    return sum(a == b for a, b in pairs), len(pairs)


def transform_score(
    f70: Sequence[str | None],
    f71_native: Sequence[str | None],
    f72_native: Sequence[str | None],
    t71: Sequence[int],
    t72: Sequence[int],
) -> dict[str, int | float]:
    a = list(f70)
    b = [f71_native[index] for index in t71]
    c = [f72_native[index] for index in t72]
    m01, n01 = pair_score(a, b)
    m02, n02 = pair_score(a, c)
    m12, n12 = pair_score(b, c)
    matches = m01 + m02 + m12
    comparisons = n01 + n02 + n12
    return {
        "f70_f71_matches": m01,
        "f70_f71_comparisons": n01,
        "f70_f72_matches": m02,
        "f70_f72_comparisons": n02,
        "f71_f72_matches": m12,
        "f71_f72_comparisons": n12,
        "matches": matches,
        "comparisons": comparisons,
        "accuracy": matches / comparisons if comparisons else 0.0,
    }


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    key_rows = read_tsv(KEY)
    r1_rows = read_tsv(R1)
    r2_rows = read_tsv(R2)
    adj_rows = read_tsv(ADJ)
    f71_rows = read_tsv(F71)
    mapping_rows = read_tsv(GDT796)

    assert len(key_rows) == 18 and len({row["blind_id"] for row in key_rows}) == 18
    assert {row["blind_id"] for row in r1_rows} == {row["blind_id"] for row in key_rows}
    assert {row["blind_id"] for row in r2_rows} == {row["blind_id"] for row in key_rows}
    assert {row["blind_id"] for row in adj_rows} == {"X04", "X08", "X24"}
    assert {int(row["a_member"]) for row in key_rows} == set(TARGET_MEMBERS)

    by_r1 = {row["blind_id"]: row for row in r1_rows}
    by_r2 = {row["blind_id"]: row for row in r2_rows}
    by_adj = {row["blind_id"]: row for row in adj_rows}
    acquisition_rows: list[dict[str, Any]] = []
    exact_agreements = 0
    opposite_decisive = 0
    for key in sorted(key_rows, key=lambda row: row["blind_id"]):
        blind_id = key["blind_id"]
        first = by_r1[blind_id]
        second = by_r2[blind_id]
        s1, s2 = first["state"], second["state"]
        if s1 == s2:
            consensus = s1
            agreement = "BLIND_EXACT_AGREEMENT"
            exact_agreements += 1
        elif UNCERTAIN in {s1, s2} and len({s1, s2} & DECISIVE) == 1:
            consensus = next(iter({s1, s2} & DECISIVE))
            agreement = "ONE_DECISIVE_PLUS_ONE_UNCERTAIN"
            assert by_adj[blind_id]["adjudicated_state"] == consensus
        else:
            assert {s1, s2} == DECISIVE
            opposite_decisive += 1
            consensus = by_adj[blind_id]["adjudicated_state"]
            agreement = "OPPOSITE_DECISIVE__SOURCE_AWARE_ADJUDICATED"
        acquisition_rows.append(
            {
                **key,
                "r1_state": s1,
                "r1_confidence": first["confidence"],
                "r2_state": s2,
                "r2_confidence": second["confidence"],
                "consensus_state": consensus,
                "agreement_class": agreement,
                "semantic_ceiling": "VISIBLE_UPPER_TORSO_STATE_ONLY__NO_LABEL_MEANING",
            }
        )

    acquisition_fields = list(key_rows[0]) + [
        "r1_state", "r1_confidence", "r2_state", "r2_confidence",
        "consensus_state", "agreement_class", "semantic_ceiling",
    ]
    write_tsv(ACQUISITION, acquisition_rows, acquisition_fields)

    by_selector_member = {(row["selector"], int(row["a_member"])): row for row in acquisition_rows}
    map_by_member = {int(row["semantic_a_member"]): row for row in mapping_rows}
    f71_by_member = {int(row["a_member"]): row for row in f71_rows}
    transition_rows: list[dict[str, Any]] = []
    for member in TARGET_MEMBERS:
        source = map_by_member[member]
        r70 = by_selector_member[("f70v1", member)]
        r72 = by_selector_member[("f72r1", member)]
        r71 = f71_by_member[member]
        s70, s71, s72 = r70["consensus_state"], r71["state"], r72["consensus_state"]

        def match(a: str, b: str) -> str:
            return "NA" if a not in DECISIVE or b not in DECISIVE else ("1" if a == b else "0")

        transition_rows.append(
            {
                "a_member": member,
                "local_coordinate": source["local_coordinate"],
                "f70_locus": source["f70_locus"],
                "f70_surface": source["f70_surface"],
                "f70_boundary_family": source["f70_boundary_family"],
                "f70_state": s70,
                "f71_f9_locus": source["f71_f9_locus"],
                "f71_f9_surface": source["f71_f9_surface"],
                "f71_f9_boundary_family": source["f71_f9_boundary_family"],
                "f71_f9_state": s71,
                "f72_locus": source["f72_locus"],
                "f72_surface": source["f72_surface"],
                "f72_boundary_family": source["f72_boundary_family"],
                "f72_state": s72,
                "visual_pattern": "/".join((s70, s71, s72)),
                "f70_f71_match": match(s70, s71),
                "f70_f72_match": match(s70, s72),
                "f71_f72_match": match(s71, s72),
                "f70_f72_family_exact": "1" if source["f70_boundary_family"] == source["f72_boundary_family"] else "0",
                "f70_f72_state_exact": match(s70, s72),
                "claim_ceiling": "ANALYST_FIXED_HOMOLOG_DESCRIPTION__NOT_AUTHORIAL_EDGE",
            }
        )
    write_tsv(TRANSITIONS, transition_rows, list(transition_rows[0]))

    f70_array: list[str | None] = [None] * 10
    f72_array: list[str | None] = [None] * 10
    for row in acquisition_rows:
        target = f70_array if row["selector"] == "f70v1" else f72_array
        target[int(row["a_member"]) - 6] = row["consensus_state"]
    f71_native: list[str | None] = [None] * 10
    for row in f71_rows:
        f71_native[int(row["f71_native_a_member"]) - 6] = row["state"]
    assert f70_array[8] is None and f72_array[8] is None and all(value is not None for value in f71_native)

    transform_list = transforms()
    ranking_rows: list[dict[str, Any]] = []
    for name71, indices71 in transform_list:
        for name72, indices72 in transform_list:
            score = transform_score(f70_array, f71_native, f72_array, indices71, indices72)
            ranking_rows.append(
                {
                    "transform_f71": name71,
                    "transform_f72": name72,
                    **{key: value for key, value in score.items() if key != "accuracy"},
                    "accuracy": f6(float(score["accuracy"])),
                    "is_fixed_f9_r0": "1" if (name71, name72) == ("F9", "R0") else "0",
                    "is_identity_r0_r0": "1" if (name71, name72) == ("R0", "R0") else "0",
                }
            )
    exact_scores = [float(row["accuracy"]) for row in ranking_rows]
    for row in ranking_rows:
        value = float(row["accuracy"])
        row["accuracy_rank"] = 1 + sum(other > value + 1e-12 for other in exact_scores)
        row["accuracy_tie_count"] = sum(abs(other - value) <= 1e-12 for other in exact_scores)
    ranking_rows.sort(key=lambda row: (int(row["accuracy_rank"]), row["transform_f71"], row["transform_f72"]))
    write_tsv(RANKINGS, ranking_rows, list(ranking_rows[0]))
    fixed = next(row for row in ranking_rows if row["is_fixed_f9_r0"] == "1")
    identity = next(row for row in ranking_rows if row["is_identity_r0_r0"] == "1")

    page_counts = {
        selector: Counter(row["consensus_state"] for row in acquisition_rows if row["selector"] == selector)
        for selector in ("f70v1", "f72r1")
    }
    mobility = {
        selector: counts[COVERED] >= 2 and counts[UNCOVERED] >= 2
        for selector, counts in page_counts.items()
    }
    combined_mobile = all(mobility.values())

    fixed_f70_f71_matches = int(fixed["f70_f71_matches"])
    positions = tuple(range(9))
    f71_fixed_target = [f71_by_member[member]["state"] for member in TARGET_MEMBERS]
    permutation_matches: list[int] = []
    for covered_positions in itertools.combinations(positions, page_counts["f70v1"][COVERED]):
        candidate = [UNCOVERED] * 9
        for position in covered_positions:
            candidate[position] = COVERED
        score, _ = pair_score(candidate, f71_fixed_target)
        permutation_matches.append(score)
    fixed_margin_p = sum(value >= fixed_f70_f71_matches for value in permutation_matches) / len(permutation_matches)

    edge_run = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", rel(EDGE_PACKET)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    edge_audit = json.loads(edge_run.stdout)
    EDGE_AUDIT.write_text(json.dumps(edge_audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    same_family_contrasts = [row for row in transition_rows if row["f70_f72_family_exact"] == "1" and row["f70_f72_state_exact"] == "0"]
    acquisition_reliable = exact_agreements >= 14 and opposite_decisive <= 2
    fixed_gate = (
        combined_mobile
        and int(fixed["accuracy_rank"]) <= 40
        and int(fixed["accuracy_tie_count"]) <= 40
        and float(fixed["accuracy"]) > float(identity["accuracy"])
    )
    if not acquisition_reliable:
        status = "STOP_ACQUISITION_AMBIGUITY"
    elif not combined_mobile:
        status = "PARTIAL__18_NEW_STATES__F70_3C6U__F72_0C9U_PAGE_RING_FACIES_ONLY__FIXED_RELATION_NOT_MOBILE__ZERO_LEXEMES"
    elif fixed_gate:
        status = "PARTIAL__FIXED_F9_R0_POSITIONAL_IMAGE_GRAMMAR_C0__ZERO_LEXEMES"
    else:
        status = "PARTIAL__MOBILE_IMAGES__FIXED_F9_R0_NOT_SUPPORTED__ZERO_LEXEMES"

    test_rows = [
        {"test_id": "BLIND_EXACT_AGREEMENT", "observed": f"{exact_agreements}/18", "reference": ">=14/18", "result": "PASS" if exact_agreements >= 14 else "FAIL", "interpretation": "raw independent crop-state agreement"},
        {"test_id": "OPPOSITE_DECISIVE_CALLS", "observed": str(opposite_decisive), "reference": "<=2", "result": "PASS" if opposite_decisive <= 2 else "FAIL", "interpretation": "source-aware adjudication burden"},
        {"test_id": "F70_WITHIN_RING_MOBILITY", "observed": f"C={page_counts['f70v1'][COVERED]}|U={page_counts['f70v1'][UNCOVERED]}", "reference": "C>=2|U>=2", "result": "PASS" if mobility["f70v1"] else "FAIL", "interpretation": "position can in principle vary within f70"},
        {"test_id": "F72_WITHIN_RING_MOBILITY", "observed": f"C={page_counts['f72r1'][COVERED]}|U={page_counts['f72r1'][UNCOVERED]}", "reference": "C>=2|U>=2", "result": "PASS" if mobility["f72r1"] else "FAIL", "interpretation": "page/ring purity prevents position inference"},
        {"test_id": "FIXED_F70_F71_MATCH", "observed": f"{fixed['f70_f71_matches']}/{fixed['f70_f71_comparisons']}", "reference": "descriptive", "result": "REPORT", "interpretation": "fixed R0/F9 pair"},
        {"test_id": "FIXED_F70_F72_MATCH", "observed": f"{fixed['f70_f72_matches']}/{fixed['f70_f72_comparisons']}", "reference": "descriptive", "result": "REPORT", "interpretation": "invariantly inflated by f72 uncovered purity"},
        {"test_id": "FIXED_F71_F72_MATCH", "observed": f"{fixed['f71_f72_matches']}/{fixed['f71_f72_comparisons']}", "reference": "descriptive", "result": "REPORT", "interpretation": "invariantly determined by f72 margin"},
        {"test_id": "FIXED_400_TRANSFORM_RANK", "observed": f"rank={fixed['accuracy_rank']}/400|ties={fixed['accuracy_tie_count']}|accuracy={fixed['accuracy']}", "reference": "rank<=40|ties<=40 after mobility", "result": "NOT_ELIGIBLE" if not combined_mobile else ("PASS" if int(fixed["accuracy_rank"]) <= 40 and int(fixed["accuracy_tie_count"]) <= 40 else "FAIL"), "interpretation": "diagnostic only because f72 is nonmobile"},
        {"test_id": "IDENTITY_400_TRANSFORM_RANK", "observed": f"rank={identity['accuracy_rank']}/400|ties={identity['accuracy_tie_count']}|accuracy={identity['accuracy']}", "reference": "descriptive", "result": "REPORT", "interpretation": "R0/R0 comparator"},
        {"test_id": "F70_F71_MARGIN_EXACT", "observed": f"matches={fixed_f70_f71_matches}|p={fixed_margin_p:.6f}|worlds={len(permutation_matches)}", "reference": "within-nine-position margin null", "result": "REPORT", "interpretation": "not a rescue for failed three-ring mobility"},
        {"test_id": "EXACT_FAMILY_OPPOSITE_STATE", "observed": str(len(same_family_contrasts)), "reference": ">=1", "result": "PASS" if same_family_contrasts else "FAIL", "interpretation": "complete boundary family cannot portably denote upper-torso state"},
        {"test_id": "GDT388_EDGE_PACKET", "observed": edge_audit["status"], "reference": "VALID_ACQUISITION_NOT_SCORE_READY", "result": "PASS" if edge_audit["status"] == "VALID_ACQUISITION_NOT_SCORE_READY" and not edge_audit["score_ready"] else "FAIL", "interpretation": "analyst homologies are not authorial directed edges"},
    ]
    write_tsv(TESTS, test_rows, list(test_rows[0]))

    candidate_rows = [
        {
            "candidate_id": "FIXED_F9_R0_POSITIONAL_CLOTHING_GRAMMAR",
            "working_interpretation": "the fixed text-family alignment also carries a homolog-specific upper-garment state",
            "decision": "NOT_SELECTED__F72_NONMOBILE",
            "confidence": "C0_ONLY",
            "evidence": f"fixed combined matches {fixed['matches']}/{fixed['comparisons']} and transform rank {fixed['accuracy_rank']}/400",
            "counterevidence": "all nine f72 targets are TORSO_UNCOVERED, so the f72 contribution is position-invariant",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "PAGE_RING_UPPER_TORSO_FACIES",
            "working_interpretation": "upper-garment realization is strongly conditioned by page/ring workshop design",
            "decision": "SELECT_STRUCTURAL_DESCRIPTION",
            "confidence": "DIRECT_VISUAL_PANEL",
            "evidence": "f70 has 3 covered/6 uncovered targets while f72 has 0 covered/9 uncovered targets",
            "counterevidence": "only two pages and one ring on each page are newly acquired here",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "AQABAB_UPPER_GARMENT_FAMILY",
            "working_interpretation": "the exact complete boundary family AQABAB denotes covered versus uncovered torso state",
            "decision": "REJECT_PORTABLE_STATE_READING",
            "confidence": "EXACT_HOMOLOG_COUNTEREXAMPLE",
            "evidence": "none",
            "counterevidence": "A09 has AQABAB on both f70 and f72 but changes from TORSO_COVERED to TORSO_UNCOVERED",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "LEARNED_LABEL_PLUS_LOCAL_IMAGE_REALIZATION",
            "working_interpretation": "labels remain learned designations embedded in a page/ring-conditioned graphical field",
            "decision": "RETAIN_PRIMARY_ARCHITECTURE",
            "confidence": "BEST_CURRENT_WORKING_THEORY",
            "evidence": "fixed homology does not overcome page/ring state purity and an exact family crosses the visible state",
            "counterevidence": "the sample cannot distinguish exemplar copying from deliberate page-wide semantic class",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
    ]
    write_tsv(CANDIDATES, candidate_rows, list(candidate_rows[0]))

    report = f"""# GDT799 — label-blind homolog clothing transition

Status: **{status}**

## Result

The new information is visual, concrete, and negative for a positional
clothing key.  Two independent readers agreed exactly on **{exact_agreements}/18**
shuffled crops.  One decisive/uncertain split and two opposite decisive calls
were resolved under the frozen rule.  The final strict upper-torso endpoint is:

| new ring | covered | uncovered | uncertain | mobile? |
|---|---:|---:|---:|---|
| f70v1 outer | {page_counts['f70v1'][COVERED]} | {page_counts['f70v1'][UNCOVERED]} | {page_counts['f70v1'][UNCERTAIN]} | {'yes' if mobility['f70v1'] else 'no'} |
| f72r1 outer | {page_counts['f72r1'][COVERED]} | {page_counts['f72r1'][UNCOVERED]} | {page_counts['f72r1'][UNCERTAIN]} | {'yes' if mobility['f72r1'] else 'no'} |

All nine admitted f72r1 outer targets are uncovered.  Therefore their state
cannot distinguish one homologous position from another.  The fixed
f70-R0/f71-F9/f72-R0 alignment is **not** reusable as a position-specific
clothing relation, regardless of its numerical transform rank.

## Fixed alignment readout

On decisive comparisons, the fixed alignment matches f70--f71
**{fixed['f70_f71_matches']}/{fixed['f70_f71_comparisons']}**, f70--f72
**{fixed['f70_f72_matches']}/{fixed['f70_f72_comparisons']}**, and f71--f72
**{fixed['f71_f72_matches']}/{fixed['f71_f72_comparisons']}**.  Combined it is
**{fixed['matches']}/{fixed['comparisons']} = {fixed['accuracy']}** and ranks
**{fixed['accuracy_rank']}/400** with **{fixed['accuracy_tie_count']}** tied
transforms.  Identity is **{identity['matches']}/{identity['comparisons']} =
{identity['accuracy']}**, rank **{identity['accuracy_rank']}/400**.  These are
diagnostics, not a recovered image key, because the mandatory f72 mobility
gate fails.

The fixed f70--f71 positional match is {fixed_f70_f71_matches} under a
conditional 84-world nine-position margin diagnostic (`p={fixed_margin_p:.6f}`).
It does not rescue the three-ring relation.

## Concrete counterexample and surviving model

A09 is especially useful: f70 `okalal` and f72 `okalam` share the exact
source-native boundary family `AQABAB`, yet the strict torso state changes
from covered to uncovered.  Thus `AQABAB` cannot portably mean “covered” or
“uncovered.”  The final glyph difference remains a future whole-label rival;
this pass does not assign it a meaning.

The best current architecture remains **learned label plus page/ring-conditioned
graphical realization**.  Clothing is real visible information, but here it is
not a portable label dictionary.

## Relation and semantic ceilings

The GDT388 executable returns `{edge_audit['status']}` with zero eligible
directed edges.  The cross-page homologs are analyst-fixed alignment rows, not
authorial connector edges.  GDT799 establishes no clothing word, owner,
planetary or social status, sex class, morpheme, sound, language, cipher,
plaintext clause, or translation.  Component export remains zero.
"""
    REPORT.write_text(report, encoding="utf-8")

    output_paths = [ACQUISITION, TRANSITIONS, RANKINGS, TESTS, CANDIDATES, EDGE_AUDIT, REPORT]
    input_paths = [KEY, R1, R2, ADJ, F71, EDGE_PACKET, SRC / "SOURCE_LOCK.tsv", GDT796]
    result: dict[str, Any] = {
        "schema": "GDT799_RESULT_V1",
        "experiment": "GDT799",
        "status": status,
        "decision": "PAGE_RING_FACIES_ONLY__FIXED_POSITION_RELATION_NOT_REUSABLE" if not combined_mobile else ("FIXED_POSITIONAL_C0_RETAINED" if fixed_gate else "FIXED_ALIGNMENT_NOT_SUPPORTED"),
        "acquisition": {
            "new_crops": 18,
            "blind_exact_agreements": exact_agreements,
            "opposite_decisive_calls": opposite_decisive,
            "consensus_counts": {selector: dict(sorted(counts.items())) for selector, counts in page_counts.items()},
            "mobility": mobility,
        },
        "fixed_alignment": {
            "f70": "R0", "f71": "F9", "f72": "R0",
            "rank_of_400": int(fixed["accuracy_rank"]),
            "tie_count": int(fixed["accuracy_tie_count"]),
            "matches": int(fixed["matches"]),
            "comparisons": int(fixed["comparisons"]),
            "accuracy": float(fixed["accuracy"]),
            "eligible_for_relation_claim": fixed_gate,
        },
        "identity_comparator": {
            "rank_of_400": int(identity["accuracy_rank"]),
            "tie_count": int(identity["accuracy_tie_count"]),
            "matches": int(identity["matches"]),
            "comparisons": int(identity["comparisons"]),
            "accuracy": float(identity["accuracy"]),
        },
        "exact_family_opposite_state_counterexamples": len(same_family_contrasts),
        "gdt388": edge_audit,
        "semantic_exports": 0,
        "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0,
        "f84_or_f84r_accessed": False,
        "claim_ceiling": "VISIBLE_STATE_ACQUISITION_AND_FIXED_ALIGNMENT_DIAGNOSTIC_ONLY__NO_WORD_OR_TRANSLATION",
        "inputs": {rel(path): sha(path) for path in input_paths},
        "outputs": {rel(path): sha(path) for path in output_paths},
        "implementation": {rel(Path(__file__)): sha(Path(__file__))},
    }
    result["content_hash"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status)
    print(f"blind agreement {exact_agreements}/18; f70 {dict(page_counts['f70v1'])}; f72 {dict(page_counts['f72r1'])}")
    print(f"fixed rank {fixed['accuracy_rank']}/400 ties={fixed['accuracy_tie_count']} accuracy={fixed['accuracy']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
