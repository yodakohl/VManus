#!/usr/bin/env python3
"""Reconstruct the formal capacity of the f2r.15 under-paint record.

This is a descriptive, post-source audit.  It uses only the cached manual
transcription/grammar atlas and human-written locus descriptions.  It does not
score an English gloss and does not use manuscript pixels, OCR, or computer
vision.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
INTERLINEAR = REPO / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
ANNOTATIONS = REPO / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
COVERAGE = REPO / "experiments/semantic_assumptions/results/pre_grounding_surface_coverage_audit.json"
RESIDUAL = REPO / "experiments/semantic_assumptions/results/pre_grounding_surface_residual_atlas.tsv"
OUTPUT = REPO / "experiments/semantic_assumptions/results/col001_colour_record_structure.json"

EXPECTED_SHA256 = {
    "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv":
        "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv":
        "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
    "experiments/semantic_assumptions/results/pre_grounding_surface_coverage_audit.json":
        "ec1d427bb04a682b5cf2c6b8d622be835e37006e303bb0ee647d44d9cc6d2eae",
    "experiments/semantic_assumptions/results/pre_grounding_surface_residual_atlas.tsv":
        "43f145ae81ffbcb78fdb8217c3a45575d427d3211c2252ac94400928ef4f47f3",
}
EDITIONS = ("IT2a", "RF1b", "ZL3b")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def locus_support(rows: Iterable[dict[str, str]]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        result[row["locus"]].add(row["edition"])
    return dict(result)


def support_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    support = locus_support(rows)
    return {
        "edition_rows": len(rows),
        "physical_loci": len(support),
        "two_or_more_readings": sum(len(value) >= 2 for value in support.values()),
        "all_three_readings": sum(len(value) == 3 for value in support.values()),
    }


def root_rows(rows: list[dict[str, str]], root: str) -> list[dict[str, str]]:
    return [row for row in rows if root in row["root_sequence"].split()]


def atom_rows(rows: list[dict[str, str]], atom: str) -> list[dict[str, str]]:
    return [
        row for row in rows
        if any(atom in word.split("+") for word in row["root_sequence"].split())
    ]


def composite_rows(
    rows: list[dict[str, str]], predicate: Any
) -> tuple[list[dict[str, str]], set[str]]:
    selected = []
    forms: set[str] = set()
    for row in rows:
        hits = [word for word in row["root_sequence"].split() if predicate(word)]
        if hits:
            selected.append(row)
            forms.update(hits)
    return selected, forms


def adjacency_rows(
    rows: list[dict[str, str]], left: str, right: str
) -> list[dict[str, str]]:
    selected = []
    for row in rows:
        roots = row["root_sequence"].split()
        if any(roots[index:index + 2] == [left, right] for index in range(len(roots) - 1)):
            selected.append(row)
    return selected


def supported_locus_records(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["locus"]].append(row)
    records = []
    for locus in sorted(grouped):
        items = sorted(grouped[locus], key=lambda row: EDITIONS.index(row["edition"]))
        first = items[0]
        records.append({
            "locus": locus,
            "section": first["section"],
            "kind": first["kind"],
            "grammar_scope": first["grammar_scope"],
            "readings": [
                {
                    "edition": row["edition"],
                    "surface": row["surface"],
                    "root_sequence": row["root_sequence"],
                }
                for row in items
            ],
        })
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    observed_hashes = {
        str(path.relative_to(REPO)): sha256(path)
        for path in (INTERLINEAR, ANNOTATIONS, COVERAGE, RESIDUAL)
    }
    require(observed_hashes == EXPECTED_SHA256, "frozen input hash mismatch")

    rows = load_tsv(INTERLINEAR)
    annotations = load_tsv(ANNOTATIONS)
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    residuals = load_tsv(RESIDUAL)
    require(len(rows) == 15_960, f"unexpected interlinear row count: {len(rows)}")
    require(len(residuals) == 2_833, "surface-residual row-count drift")
    require(coverage["target_relevance"] == {
        "f2r_15_has_surface_residual": False,
        "omitted_token_occurrences_containing_i_or_o": 0,
        "col001_frozen_formal_counts_changed_by_residual_inventory": False,
    }, "COL001 surface-residual relevance drift")

    f2 = [row for row in rows if row["locus"] == "f2r.15"]
    require(len(f2) == 2, "f2r.15 must have exactly two available readings")
    require({row["edition"] for row in f2} == {"RF1b", "ZL3b"}, "f2r.15 reading set drift")
    require(all(row["surface"] == "ios an on" for row in f2), "f2r.15 surface drift")
    require(all(row["root_sequence"] == "i+os a o" for row in f2), "f2r.15 roots drift")
    require(all(row["role_sequence"] == "BARE+BARE BARE BARE" for row in f2), "f2r.15 role drift")

    f2_annotation = [row for row in annotations if row["locus"] == "f2r.15"]
    f67_annotation = [row for row in annotations if row["locus"] == "f67r2.40"]
    require(len(f2_annotation) == 1 and len(f67_annotation) == 1, "human locus annotation drift")

    shell = [row for row in rows if row["role_sequence"] == "BARE+BARE BARE BARE"]
    pair_ao = adjacency_rows(rows, "a", "o")
    pair_oa = adjacency_rows(rows, "o", "a")
    atom_i = atom_rows(rows, "i")
    atom_os = atom_rows(rows, "os")
    initial_i_composites, initial_i_forms = composite_rows(
        rows, lambda word: word.startswith("i+")
    )
    final_os_composites, final_os_forms = composite_rows(
        rows, lambda word: word.endswith("+os")
    )
    first_plus_os_final_o = []
    for row in rows:
        roots = row["root_sequence"].split()
        if len(roots) == 3 and roots[0].endswith("+os") and roots[2] == "o":
            first_plus_os_final_o.append(row)

    result = {
        "experiment": "COL001_FORMAL_RECORD_AUDIT",
        "status": "PASS_SLOT_NARROWING_STOP_LEXICAL",
        "method_status": "DESCRIPTIVE_POST_SOURCE_AUDIT",
        "input_sha256": observed_hashes,
        "f2r15": {
            "available_readings": [
                {
                    "edition": row["edition"],
                    "surface": row["surface"],
                    "root_sequence": row["root_sequence"],
                    "role_sequence": row["role_sequence"],
                }
                for row in sorted(f2, key=lambda row: EDITIONS.index(row["edition"]))
            ],
            "human_relation": f2_annotation[0]["unit_description"],
            "human_context": f2_annotation[0]["local_comment"],
        },
        "component_support": {
            "i_plus_os": support_summary(root_rows(rows, "i+os")),
            "a": support_summary(root_rows(rows, "a")),
            "o": support_summary(root_rows(rows, "o")),
        },
        "component_productivity": {
            "i_atom": {
                **support_summary(atom_i),
                "distinct_complete_root_forms": len({
                    word for row in atom_i for word in row["root_sequence"].split()
                    if "i" in word.split("+")
                }),
            },
            "os_atom": {
                **support_summary(atom_os),
                "distinct_complete_root_forms": len({
                    word for row in atom_os for word in row["root_sequence"].split()
                    if "os" in word.split("+")
                }),
            },
            "i_initial_composites": {
                **support_summary(initial_i_composites),
                "distinct_complete_root_forms": len(initial_i_forms),
                "two_or_more_reading_loci": [
                    record for record in supported_locus_records(initial_i_composites)
                    if len(record["readings"]) >= 2
                ],
            },
            "os_final_composites": {
                **support_summary(final_os_composites),
                "distinct_complete_root_forms": len(final_os_forms),
            },
        },
        "surface_coverage_qualification": {
            "formal_layer": "RETAINED_NODES_ONLY",
            "manuscript_omitted_surface_groups": coverage["totals"]["omitted_tokens"],
            "f2r15_has_surface_residual": False,
            "omitted_token_occurrences_containing_i_or_o": 0,
            "col001_component_counts_changed": False,
        },
        "adjacent_root_pairs": {
            "a_to_o": {
                **support_summary(pair_ao),
                "two_or_more_reading_loci": [
                    record for record in supported_locus_records(pair_ao)
                    if len(record["readings"]) >= 2
                ],
            },
            "o_to_a": {
                **support_summary(pair_oa),
                "two_or_more_reading_loci": [
                    record for record in supported_locus_records(pair_oa)
                    if len(record["readings"]) >= 2
                ],
            },
        },
        "formal_shell": {
            **support_summary(shell),
            "loci": supported_locus_records(shell),
        },
        "three_root_first_plus_os_final_o": {
            **support_summary(first_plus_os_final_o),
            "loci": supported_locus_records(first_plus_os_final_o),
            "f67r2_human_relation": f67_annotation[0]["unit_description"],
            "f67r2_human_context": f67_annotation[0]["local_comment"],
        },
        "gates": {
            "f2r15_i_plus_os_is_locus_unique": support_summary(root_rows(rows, "i+os"))["physical_loci"] == 1,
            "f2r15_a_to_o_repeats_outside_f2r": support_summary(pair_ao)["physical_loci"] > 1,
            "i_plus_os_components_are_productive_elsewhere": (
                support_summary(initial_i_composites)["physical_loci"] > 1
                and support_summary(final_os_composites)["physical_loci"] > 1
            ),
            "formal_shell_is_instruction_specific": False,
            "lexical_gloss_authorized": False,
        },
        "claim_ceiling": (
            "The final a-to-o pair belongs to a recurring manuscript construction. The complete i+os composite "
            "is locus-unique, but i and os are separately productive atoms in other composites. This narrows "
            "where record-specific information could reside but does not identify GREEN, pigment, action, "
            "language, plaintext, or translation."
        ),
        "prohibited_inputs": {
            "ocr": False,
            "automated_image_recognition": False,
            "pixel_features": False,
            "machine_generated_visual_labels": False,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "output": str(args.output.relative_to(REPO)),
        "i_plus_os_physical_loci": result["component_support"]["i_plus_os"]["physical_loci"],
        "a_physical_loci": result["component_support"]["a"]["physical_loci"],
        "o_physical_loci": result["component_support"]["o"]["physical_loci"],
        "a_to_o_physical_loci": result["adjacent_root_pairs"]["a_to_o"]["physical_loci"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
