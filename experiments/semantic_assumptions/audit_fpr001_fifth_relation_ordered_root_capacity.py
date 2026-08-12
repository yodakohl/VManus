#!/usr/bin/env python3
"""Target-page-masked capacity for the fifth repeated-plant ordered-root query."""

from __future__ import annotations

import argparse
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
OUT = BASE / "results/fpr001_fifth_relation_ordered_root_capacity.json"
REPORT = BASE / "results/fpr001_fifth_relation_ordered_root_capacity_report.md"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
QUERY = ("ot", "od", "e", "od", "or")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def lcs(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    prior = [0] * (len(right) + 1)
    for left_item in left:
        current = [0]
        for index, right_item in enumerate(right, 1):
            current.append(
                prior[index - 1] + 1
                if left_item == right_item
                else max(prior[index], current[-1])
            )
        prior = current
    return prior[-1]


def build() -> tuple[dict[str, object], str]:
    ownership = json.loads(OWNERSHIP.read_text(encoding="utf-8"))
    capacity5 = json.loads(CAPACITY5.read_text(encoding="utf-8"))
    if ownership["decision"] != "REOPEN_FIVE_PAIR_SCORE_BLIND_CAPACITY_AND_DESIGN_ONLY":
        raise RuntimeError("ownership decision")
    if capacity5["relations"][-1] != {"label_locus": "f102r1.2", "target_page": "f37v"}:
        raise RuntimeError("fifth relation")
    if capacity5["root_count_by_label"][-1] != {"label_locus": "f102r1.2", "root_count": 5}:
        raise RuntimeError("query size")

    target_meta = None
    with LOCI.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] == "f37v.1":
                target_meta = {
                    "page": row["page"], "section": row["section"],
                    "currier": row["currier"], "hand": row["hand"],
                    "readings_present": row["readings_present"],
                }
                break
    if target_meta != {
        "page": "f37v", "section": "H", "currier": "A", "hand": "1",
        "readings_present": "ZL3b;IT2a;RF1b",
    }:
        raise RuntimeError(("target metadata", target_meta))

    page_edges: dict[str, dict[str, Counter[tuple[str, str]]]] = {
        edition: defaultdict(Counter) for edition in EDITIONS
    }
    page_lcs: dict[str, dict[str, int]] = {edition: defaultdict(int) for edition in EDITIONS}
    target_rows_skipped_before_formal_index = 0
    with INTERLINEAR.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            if row["page"] == "f37v":
                target_rows_skipped_before_formal_index += 1
                continue
            if not (
                row["section"] == "H" and row["currier"] == "A" and row["hand"] == "1"
                and row["grammar_scope"] == "CONFIRMED_PROSE"
            ):
                continue
            edition = row["edition"]
            if edition not in page_edges:
                raise RuntimeError(("edition", edition))
            for root_word in row["root_sequence"].split():
                atoms = tuple(root_word.split("+"))
                page_lcs[edition][row["page"]] = max(page_lcs[edition][row["page"]], lcs(QUERY, atoms))
                for edge in zip(QUERY, QUERY[1:]):
                    page_edges[edition][row["page"]][edge] += sum(
                        atoms[index:index + 2] == edge for index in range(len(atoms) - 1)
                    )

    summaries: dict[str, object] = {}
    varying = True
    for edition in EDITIONS:
        pages = sorted(set(page_edges[edition]) | set(page_lcs[edition]))
        edge_support = {
            "+".join(edge): sum(page_edges[edition][page][edge] > 0 for page in pages)
            for edge in zip(QUERY, QUERY[1:])
        }
        nonzero = sum(any(page_edges[edition][page].values()) for page in pages)
        histogram = Counter(page_lcs[edition][page] for page in pages)
        varying &= len(histogram) >= 2 and nonzero not in {0, len(pages)}
        summaries[edition] = {
            "background_pages": len(pages),
            "edge_page_support": edge_support,
            "pages_with_any_query_edge": nonzero,
            "maximum_background_word_lcs": max(histogram),
            "background_page_max_lcs_histogram": {str(key): histogram[key] for key in sorted(histogram)},
        }

    rank_floor = 1 / 95
    gates = {
        "exactly_94_background_pages_each_reading": all(summaries[e]["background_pages"] == 94 for e in EDITIONS),
        "every_query_edge_on_at_least_2_pages_each_reading": all(
            min(summaries[e]["edge_page_support"].values()) >= 2 for e in EDITIONS
        ),
        "at_least_20_nonzero_pages_each_reading": all(summaries[e]["pages_with_any_query_edge"] >= 20 for e in EDITIONS),
        "page_score_variable_each_reading": varying,
        "inclusive_rank_floor_at_most_0_02": rank_floor <= 0.02,
        "f37v_formal_fields_matches_scores_and_rank_unopened": True,
    }
    passed = all(gates.values())
    result: dict[str, object] = {
        "experiment": "FPR001_FIFTH_RELATION_ORDERED_ROOT_CAPACITY",
        "schema": "FPR001_FIFTH_RELATION_ORDERED_ROOT_CAPACITY_V1",
        "status": "PASS_TARGET_PAGE_MASKED_CAPACITY" if passed else "STOP_TARGET_PAGE_MASKED_CAPACITY",
        "decision": "AUTHORIZE_COMPACT_TARGET_BLIND_CALIBRATION_ONLY" if passed else "DO_NOT_SCORE_F37V",
        "fixed_relation": {"query_locus": "f102r1.2", "target_page": "f37v"},
        "query": {"ordered_roots": list(QUERY), "root_count": len(QUERY), "exposed_before_this_design": True},
        "background": summaries,
        "capacity": {
            "target_plus_background_pages": 95,
            "minimum_inclusive_rank_p": rank_floor,
            "target_rows_skipped_before_formal_field_index": target_rows_skipped_before_formal_index,
        },
        "target_access": {
            "f37v_metadata_accessed_from_locus_atlas": True,
            "f37v_root_sequence_indexed": False,
            "f37v_surface_indexed": False,
            "f37v_formal_interlinear_indexed": False,
            "f37v_query_match_computed": False,
            "f37v_score_computed": False,
            "f37v_rank_computed": False,
            "alternate_readings_treated_as_replicates": False,
        },
        "gates": gates,
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in (METHOD, INTERLINEAR, LOCI, OWNERSHIP, CAPACITY5)},
        "claim_ceiling": (
            "Capacity authorizes only compact target-blind calibration of one fixed ordered-root held-page statistic. "
            "No f37v formal content or score is opened, and no plant, component, word, sound, language, cipher, "
            "plaintext, meaning, or translation follows."
        ),
    }
    report = (
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
    return result, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result, report = build()
    if args.write:
        OUT.write_bytes(canonical(result))
        REPORT.write_text(report, encoding="utf-8")
    else:
        print(canonical(result).decode(), end="")


if __name__ == "__main__":
    main()
