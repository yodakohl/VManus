#!/usr/bin/env python3
"""Build the exhaustive f57 quality-position cross-page label inventory."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INTERLINEAR = Path(
    "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
)
ANNOTATIONS = Path(
    "experiments/semantic_assumptions/results/"
    "existing_human_exact_locus_annotations.tsv"
)
DESIGN = Path(
    "experiments/semantic_assumptions/f57_quality_label_neighbors/DESIGN.md"
)
EDITIONS = ("ZL3b", "IT2a", "RF1b")
TARGETS = {
    "HOT_POSITION": "f57v.6",
    "MOIST_POSITION": "f57v.7",
    "COLD_POSITION": "f57v.8",
    "DRY_POSITION": "f57v.9",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def compact_surface(value: str) -> str:
    return "".join(value.split())


def edit_distance(left: list[str] | str, right: list[str] | str) -> int:
    previous = list(range(len(right) + 1))
    for row_number, left_item in enumerate(left, 1):
        current = [row_number]
        for column_number, right_item in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[column_number] + 1,
                    previous[column_number - 1] + (left_item != right_item),
                )
            )
        previous = current
    return previous[-1]


def normalized_edit_similarity(left: list[str] | str, right: list[str] | str) -> float:
    denominator = max(len(left), len(right), 1)
    return 1.0 - edit_distance(left, right) / denominator


def bigrams(value: str) -> set[str]:
    compact = compact_surface(value)
    return {compact[index : index + 2] for index in range(len(compact) - 1)}


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def longest_common_substring(left: str, right: str) -> int:
    previous = [0] * (len(right) + 1)
    best = 0
    for left_item in left:
        current = [0]
        for column_number, right_item in enumerate(right, 1):
            value = previous[column_number - 1] + 1 if left_item == right_item else 0
            current.append(value)
            best = max(best, value)
        previous = current
    return best


def root_components(value: str) -> list[str]:
    return [component for word in value.split() for component in word.split("+")]


def summarize(values: list[float]) -> dict[str, object]:
    return {
        "by_edition": {
            edition: round(value, 12)
            for edition, value in zip(EDITIONS, values, strict=True)
        },
        "minimum": round(min(values), 12),
        "mean": round(sum(values) / len(values), 12),
    }


def competition_rank(ordered: list[dict[str, object]], locus: str) -> int | None:
    last_key: tuple[float, float] | None = None
    current_rank = 0
    for index, row in enumerate(ordered, 1):
        surface = row["surface_edit"]
        assert isinstance(surface, dict)
        key = (float(surface["minimum"]), float(surface["mean"]))
        if key != last_key:
            current_rank = index
            last_key = key
        if row["locus"] == locus:
            return current_rank
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    interlinear_path = ROOT / INTERLINEAR
    annotation_path = ROOT / ANNOTATIONS
    design_path = ROOT / DESIGN
    rows = read_tsv(interlinear_path)
    annotations = read_tsv(annotation_path)

    by_locus: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_locus[row["locus"]][row["edition"]] = row

    annotation_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in annotations:
        annotation_by_locus[row["locus"]].append(row)

    candidates = []
    for locus, edition_rows in by_locus.items():
        if locus.startswith("f57v."):
            continue
        if set(edition_rows) != set(EDITIONS):
            continue
        if edition_rows["ZL3b"]["kind"] != "L":
            continue
        candidates.append(locus)
    candidates.sort()

    target_results: dict[str, object] = {}
    for role, target_locus in TARGETS.items():
        comparisons = []
        exact_by_edition = {edition: [] for edition in EDITIONS}
        exact_all_readings = []
        for candidate_locus in candidates:
            surface_edit = []
            bigram_scores = []
            substring_coverage = []
            root_edit = []
            surfaces: dict[str, str] = {}
            roots: dict[str, str] = {}
            exact_flags = []
            for edition in EDITIONS:
                target = by_locus[target_locus][edition]
                candidate = by_locus[candidate_locus][edition]
                target_surface = compact_surface(target["surface"])
                candidate_surface = compact_surface(candidate["surface"])
                target_roots = root_components(target["root_sequence"])
                candidate_roots = root_components(candidate["root_sequence"])
                surfaces[edition] = candidate["surface"]
                roots[edition] = candidate["root_sequence"]
                surface_edit.append(
                    normalized_edit_similarity(target_surface, candidate_surface)
                )
                bigram_scores.append(
                    jaccard(bigrams(target_surface), bigrams(candidate_surface))
                )
                substring_coverage.append(
                    longest_common_substring(target_surface, candidate_surface)
                    / max(len(target_surface), 1)
                )
                root_edit.append(
                    normalized_edit_similarity(target_roots, candidate_roots)
                )
                exact = target_surface == candidate_surface
                exact_flags.append(exact)
                if exact:
                    exact_by_edition[edition].append(candidate_locus)
            if all(exact_flags):
                exact_all_readings.append(candidate_locus)

            human_rows = annotation_by_locus.get(candidate_locus, [])
            comparisons.append(
                {
                    "locus": candidate_locus,
                    "page": by_locus[candidate_locus]["ZL3b"]["page"],
                    "section": by_locus[candidate_locus]["ZL3b"]["section"],
                    "surfaces": surfaces,
                    "root_sequences": roots,
                    "surface_edit": summarize(surface_edit),
                    "bigram_jaccard": summarize(bigram_scores),
                    "substring_target_coverage": summarize(substring_coverage),
                    "root_component_edit": summarize(root_edit),
                    "human_annotations": [
                        {
                            "unit_description": row["unit_description"],
                            "local_comment": row["local_comment"],
                            "object_tags": row["object_tags"],
                            "local_relation_tags": row["local_relation_tags"],
                            "unit_relation_tags": row["unit_relation_tags"],
                            "certainty": row["certainty"],
                            "relation_scope": row["relation_scope"],
                        }
                        for row in human_rows
                    ],
                }
            )

        ordered = sorted(
            comparisons,
            key=lambda row: (
                -float(row["surface_edit"]["minimum"]),
                -float(row["surface_edit"]["mean"]),
                str(row["locus"]),
            ),
        )
        target_results[role] = {
            "target_locus": target_locus,
            "target_surfaces": {
                edition: by_locus[target_locus][edition]["surface"]
                for edition in EDITIONS
            },
            "candidate_count": len(candidates),
            "exact_surface_matches_by_edition": exact_by_edition,
            "exact_surface_matches_all_readings": exact_all_readings,
            "f77v_3_primary_competition_rank": competition_rank(ordered, "f77v.3"),
            "top_20_primary": ordered[:20],
        }

    result = {
        "status": "POSTHOC_DESCRIPTIVE_LABEL_REGISTER_INVENTORY",
        "inputs": {
            str(INTERLINEAR): sha256(interlinear_path),
            str(ANNOTATIONS): sha256(annotation_path),
            str(DESIGN): sha256(design_path),
        },
        "candidate_universe": {
            "kind": "L",
            "all_three_readings_required": True,
            "other_page_required": True,
            "count": len(candidates),
        },
        "primary_order": (
            "decreasing minimum corresponding-reading normalized surface "
            "edit similarity, then decreasing mean, then locus"
        ),
        "targets": target_results,
        "decision": {
            "retain": (
                "f77v.3 is the first primary surface neighbour of the f57v.8 "
                "COLD-position form in the exhaustive other-page label inventory"
            ),
            "qualification": (
                "the four nearest-neighbour lists have heterogeneous human "
                "contexts and therefore first diagnose label/register morphology"
            ),
            "forbid": (
                "no HOT MOIST COLD DRY figure star plant container tube outlet "
                "lexeme plaintext or translation"
            ),
        },
    }

    # Frozen reconstruction guards from the disclosed pilot.
    assert len(candidates) == 868
    expected_first = {
        "HOT_POSITION": "f89r2.34",
        "MOIST_POSITION": "f71v.9",
        "COLD_POSITION": "f77v.3",
        "DRY_POSITION": "f67r2.57",
    }
    # DRY has a five-way score tie; locus ID is the fixed final ordering key.
    for role, expected_locus in expected_first.items():
        assert target_results[role]["top_20_primary"][0]["locus"] == expected_locus
    assert target_results["COLD_POSITION"]["f77v_3_primary_competition_rank"] == 1
    assert target_results["COLD_POSITION"]["exact_surface_matches_by_edition"] == {
        "ZL3b": ["f77v.3"],
        "IT2a": [],
        "RF1b": [],
    }
    assert all(
        not target_results[role]["exact_surface_matches_all_readings"]
        for role in TARGETS
    )

    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
