#!/usr/bin/env python3
"""Run the guarded GDT352 singular-fragment query."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt352_singular_fragment_query"
ART = EXP / "artifacts"
BASE = ROOT / "experiments/semantic_assumptions/results"
EXACT = BASE / "existing_human_exact_locus_annotations.tsv"
PAGE = BASE / "existing_human_page_annotations.tsv"
LOCI = BASE / "source_sta_family_consensus_loci.tsv"
GROUPS = BASE / "source_sta_family_consensus_groups.tsv"
ALIGN = BASE / "source_sta_group_alignment.tsv"
PAGES = {"f96v", "f99r", "f100r"}


def stable(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def digest_rows(rows: list[dict[str, str]]) -> str:
    return hashlib.sha256(stable(rows)).hexdigest()


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    exact_guard = GuardedTSV(EXACT, selector_column="page", allowed_values=PAGES)
    page_guard = GuardedTSV(PAGE, selector_column="page", allowed_values=PAGES)
    loci_guard = GuardedTSV(LOCI, selector_column="page", allowed_values=PAGES)
    groups_guard = GuardedTSV(GROUPS, selector_column="page", allowed_values=PAGES)
    exact = list(exact_guard)
    pages = {r["page"]: r for r in page_guard}
    loci_rows = list(loci_guard)
    group_rows = list(groups_guard)

    # Source assertions and fixed ownership states.
    r46 = next(r for r in exact if r["locus"] == "f99r.46")
    assert "only one plant and one label" in r46["local_comment"].lower()
    assert "fragment #94" in pages["f96v"]["illustrations"].lower()
    assert "fragment 116" in pages["f100r"]["illustrations"].lower()
    r2 = next(r for r in exact if r["locus"] == "f100r.2")
    r3 = next(r for r in exact if r["locus"] == "f100r.3")
    assert "5 plants and 6 label words" in r2["local_comment"]
    assert "perhaps associated with plant <f100r>[1,2]" in r3["local_comment"].lower()

    selected_loci = {r["locus"] for r in loci_rows}
    align_guard = GuardedTSV(ALIGN, selector_column="locus", allowed_values=selected_loci)
    align_rows = list(align_guard)

    inventory = [
        {
            "relation_id": "F96V_TO_F99R_FRAGMENT94",
            "herbal_page": "f96v",
            "pharma_page": "f99r",
            "catalogue_fragment": "94",
            "ownership_state": "SINGULAR_ONE_PLANT_ONE_LABEL",
            "candidate_loci": "f99r.46",
            "certainty": "UNHEDGED",
            "scoring_role": "PRIMARY_POST_EXPOSURE_QUERY",
        },
        {
            "relation_id": "F96V_TO_F100R_FRAGMENT116",
            "herbal_page": "f96v",
            "pharma_page": "f100r",
            "catalogue_fragment": "116",
            "ownership_state": "AMBIGUOUS_SHIFTED_ROW",
            "candidate_loci": "f100r.2|f100r.3",
            "certainty": "HEDGED",
            "scoring_role": "DESCRIPTIVE_UNCERTAINTY_SET",
        },
    ]
    inventory_path = ART / "gdt352_query_inventory.tsv"
    write_tsv(inventory_path, inventory)

    label_loci = {
        r["locus"] for r in exact
        if r["page"] == "f99r" and r["normalized_code"] == "@Lf"
    }
    family_by_locus = {r["locus"]: r["family_sequence"] for r in loci_rows}
    f96_families = [r["family_surface"] for r in group_rows if r["page"] == "f96v"]
    scores: list[dict[str, object]] = []

    for edition in ("ZL3b", "IT2a", "RF1b"):
        surfaces: dict[str, list[str]] = {}
        for row in align_rows:
            if row["edition"] != edition:
                continue
            surfaces.setdefault(row["locus"], []).append(row["nearest_basic_eva_primary"].replace(" ", ""))
        target = [token for locus, tokens in surfaces.items() if locus.startswith("f96v.") for token in tokens]
        comparisons = []
        for locus in sorted(label_loci):
            if locus not in surfaces:
                continue
            source = "|".join(surfaces[locus])
            best_ratio, best_target = max((SequenceMatcher(None, source, token).ratio(), token) for token in target)
            comparisons.append((best_ratio, locus, source, best_target, source in target))
        q = next(row for row in comparisons if row[1] == "f99r.46")
        scores.append({
            "relation_id": "F96V_TO_F99R_FRAGMENT94",
            "query_locus": "f99r.46",
            "representation": "DIPLOMATIC_SURFACE",
            "edition": edition,
            "query_value": q[2],
            "exact_match": int(q[4]),
            "best_target_value": q[3],
            "best_similarity": f"{q[0]:.12f}",
            "matched_rank": 1 + sum(row[0] > q[0] for row in comparisons),
            "matched_denominator": len(comparisons),
            "ownership_state": "SINGULAR",
            "interpretation": "NEGATIVE",
        })

    family_comparisons = []
    for locus in sorted(label_loci):
        source = family_by_locus.get(locus)
        if not source:
            continue
        best_ratio, best_target = max((SequenceMatcher(None, source, value).ratio(), value) for value in f96_families)
        family_comparisons.append((best_ratio, locus, source, best_target, source in f96_families))
    fq = next(row for row in family_comparisons if row[1] == "f99r.46")
    scores.append({
        "relation_id": "F96V_TO_F99R_FRAGMENT94",
        "query_locus": "f99r.46",
        "representation": "CONSENSUS_FAMILY",
        "edition": "ALL_READING_CONSENSUS",
        "query_value": fq[2],
        "exact_match": int(fq[4]),
        "best_target_value": fq[3],
        "best_similarity": f"{fq[0]:.12f}",
        "matched_rank": 1 + sum(row[0] > fq[0] for row in family_comparisons),
        "matched_denominator": len(family_comparisons),
        "ownership_state": "SINGULAR",
        "interpretation": "NEGATIVE",
    })

    # The fragment-116 uncertainty set is kept intact. Rank only within its
    # complete five-plant top row, never choose an owner after seeing a score.
    top_row = {f"f100r.{index}" for index in range(1, 6)}
    for edition in ("ZL3b", "IT2a", "RF1b"):
        surfaces: dict[str, list[str]] = {}
        for row in align_rows:
            if row["edition"] == edition:
                surfaces.setdefault(row["locus"], []).append(row["nearest_basic_eva_primary"].replace(" ", ""))
        target = [token for locus, tokens in surfaces.items() if locus.startswith("f96v.") for token in tokens]
        ranked = []
        for locus in top_row:
            if locus not in surfaces:
                continue
            source = "|".join(surfaces[locus])
            best_ratio, best_target = max((SequenceMatcher(None, source, token).ratio(), token) for token in target)
            ranked.append((best_ratio, locus, source, best_target, source in target))
        for locus in ("f100r.2", "f100r.3"):
            q = next(row for row in ranked if row[1] == locus)
            scores.append({
                "relation_id": "F96V_TO_F100R_FRAGMENT116",
                "query_locus": locus,
                "representation": "DIPLOMATIC_SURFACE",
                "edition": edition,
                "query_value": q[2],
                "exact_match": int(q[4]),
                "best_target_value": q[3],
                "best_similarity": f"{q[0]:.12f}",
                "matched_rank": 1 + sum(row[0] > q[0] for row in ranked),
                "matched_denominator": len(ranked),
                "ownership_state": "AMBIGUOUS_CANDIDATE",
                "interpretation": "DESCRIPTIVE_ONLY",
            })

    top_family = []
    for locus in top_row:
        if locus not in family_by_locus:
            continue
        source = family_by_locus[locus]
        best_ratio, best_target = max((SequenceMatcher(None, source, value).ratio(), value) for value in f96_families)
        top_family.append((best_ratio, locus, source, best_target, source in f96_families))
    for locus in ("f100r.2", "f100r.3"):
        q = next(row for row in top_family if row[1] == locus)
        scores.append({
            "relation_id": "F96V_TO_F100R_FRAGMENT116",
            "query_locus": locus,
            "representation": "CONSENSUS_FAMILY",
            "edition": "ALL_READING_CONSENSUS",
            "query_value": q[2],
            "exact_match": int(q[4]),
            "best_target_value": q[3],
            "best_similarity": f"{q[0]:.12f}",
            "matched_rank": 1 + sum(row[0] > q[0] for row in top_family),
            "matched_denominator": len(top_family),
            "ownership_state": "AMBIGUOUS_CANDIDATE",
            "interpretation": "AMBIGUOUS_COMMON_FORM_LEAD" if q[4] else "DESCRIPTIVE_ONLY",
        })

    score_path = ART / "gdt352_scores.tsv"
    write_tsv(score_path, scores)

    # Count prevalence through a guard that drops f84 before parsing fields.
    prevalence_guard = GuardedTSV(GROUPS, selector_column="page", allowed_values=None)
    aqjac_rows = [r for r in prevalence_guard if r["family_surface"] == "AQJAC"]

    source_sets = {
        "human_exact_selected": exact,
        "human_page_selected": list(pages.values()),
        "consensus_loci_selected": loci_rows,
        "consensus_groups_selected": group_rows,
        "alignment_selected": align_rows,
    }
    digests = [
        {"source": name, "selected_rows": len(rows), "selected_content_sha256": digest_rows(rows)}
        for name, rows in source_sets.items()
    ]
    digest_path = ART / "gdt352_source_digests.tsv"
    write_tsv(digest_path, digests)

    primary = [r for r in scores if r["relation_id"] == "F96V_TO_F99R_FRAGMENT94"]
    status = "NEW_SINGULAR_QUERY_FORMALLY_SUPPORTED" if all(int(r["exact_match"]) for r in primary) else "SINGULAR_QUERY_NEGATIVE_WITH_AMBIGUOUS_COMMON_FORM_LEAD"
    result = {
        "experiment": "GDT352",
        "schema": "GDT352_SINGULAR_FRAGMENT_QUERY_V1",
        "status": status,
        "exposure": "POST_EXPOSURE_EXPLORATORY",
        "counts": {
            "new_singular_queries": 1,
            "ambiguous_uncertainty_sets": 1,
            "primary_exact_surface_readings": sum(int(r["exact_match"]) for r in primary if r["representation"] == "DIPLOMATIC_SURFACE"),
            "primary_exact_family": sum(int(r["exact_match"]) for r in primary if r["representation"] == "CONSENSUS_FAMILY"),
            "aqjac_non_f84_group_rows": len(aqjac_rows),
            "aqjac_non_f84_pages": len({r["page"] for r in aqjac_rows}),
        },
        "primary_query": {
            "relation": "f96v_to_f99r_fragment94",
            "locus": "f99r.46",
            "surface_ranks": {r["edition"]: f'{r["matched_rank"]}/{r["matched_denominator"]}' for r in primary if r["representation"] == "DIPLOMATIC_SURFACE"},
            "family_rank": next(f'{r["matched_rank"]}/{r["matched_denominator"]}' for r in primary if r["representation"] == "CONSENSUS_FAMILY"),
            "decision": "NO_EXACT_SURFACE_OR_FAMILY_INVARIANCE",
        },
        "secondary_lead": {
            "relation": "f96v_to_f100r_fragment116",
            "ownership": "AMBIGUOUS_F100R_2_OR_3",
            "candidate": "f100r.3",
            "surface_relation": "otear_near_ytear_yteor",
            "family_relation": "AQJAC_EXACT",
            "classification": "AMBIGUOUS_COMMON_FORM_LEAD",
        },
        "source_access": {
            "images_opened": False,
            "f84_rows_parsed_retained_displayed_joined_or_scored": False,
            "guard_stats": {
                "exact": exact_guard.stats.__dict__,
                "page": page_guard.stats.__dict__,
                "loci": loci_guard.stats.__dict__,
                "groups": groups_guard.stats.__dict__,
                "alignment": align_guard.stats.__dict__,
                "prevalence": prevalence_guard.stats.__dict__,
            },
        },
        "claim_ceiling": "One post-exposure source-bound formal query only; no plant identity, lexical identity, meaning, language, plaintext, or translation.",
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in (inventory_path, score_path, digest_path)},
        "documents": {str(path.relative_to(ROOT)): sha(path) for path in (EXP / "METHOD.md", EXP / "REPORT.md")},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
    }
    content = dict(result)
    result["result_content_sha256"] = hashlib.sha256(stable(content)).hexdigest()
    (ART / "gdt352_result.json").write_bytes(stable(result))


if __name__ == "__main__":
    main()
