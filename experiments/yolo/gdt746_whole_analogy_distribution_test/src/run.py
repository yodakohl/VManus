#!/usr/bin/env python3
"""Test GDT745's strongest complete-whole analogies in real distributions.

EVA surfaces remain opaque complete labels. The experiment does not split a
surface or infer a character value. It asks whether the seventeen strongest
form-neighbour candidates occur in the same manuscript environments as their
fifty-two known edit-distance-one whole neighbours.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt746_whole_analogy_distribution_test")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

G745_RUN_REL = Path(
    "experiments/yolo/gdt745_exact_open_content_role_expansion/src/run.py"
)
G745_CENSUS_REL = Path(
    "experiments/yolo/gdt745_exact_open_content_role_expansion/artifacts/"
    "CONTENT_41_ROLE_CENSUS.tsv"
)
G745_ANALOGY_REL = Path(
    "experiments/yolo/gdt745_exact_open_content_role_expansion/artifacts/"
    "WHOLE_NEIGHBOR_ANALOGY_DECK.tsv"
)
MANUAL_REL = BASE_REL / "src" / "MANUAL_DISTRIBUTION_ASSESSMENTS.tsv"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g745 = load_module("gdt745_builder_for_gdt746", ROOT / G745_RUN_REL)

A3_TIER = "A3_DISTANCE1_MULTIWHOLE_CONSENSUS"
AXIS_ORDER = tuple(g745.ANALOGY_TAG_ORDER)
FEATURE_WEIGHTS = {
    "section": 0.25,
    "line_position": 0.20,
    "left_axes": 0.20,
    "right_axes": 0.20,
    "closure": 0.15,
}
PAIR_STATUS_ORDER = (
    "D3_DISTRIBUTION_REINFORCED",
    "D2_DISTRIBUTION_COMPATIBLE",
    "D1_SPARSE_COMPATIBLE",
    "D1_MIXED_OR_ORDINARY",
    "D0_DISTRIBUTION_MISMATCH",
)
OUTPUT_NAMES = (
    "A3_17_TARGETS.tsv",
    "SURFACE_63_OCCURRENCE_FEATURES.tsv",
    "CALIBRATION_782_CANDIDATE_KNOWN_SCORES.tsv",
    "PAIR_52_DISTRIBUTION_SCORES.tsv",
    "CANDIDATE_17_DISTRIBUTION_CENSUS.tsv",
    "GDT746_WHOLE_DISTRIBUTION_READER.md",
    "GDT746_GDT388_DISTRIBUTION_EDGE_PACKET.tsv",
    "GDT746_GDT388_EDGE_INTAKE.json",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]
) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=names,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def joined(values: Iterable[str]) -> str:
    members = sorted(set(values))
    return "|".join(members) or "NONE"


def count_string(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def weighted_count_string(values: dict[str, float]) -> str:
    return "|".join(
        f"{key}:{values[key]:.3f}" for key in sorted(values) if values[key]
    ) or "NONE"


def split_axes(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def line_position(ordinal: int, length: int) -> str:
    if length == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def line_third(ordinal: int, length: int) -> str:
    if length <= 1:
        return "SINGLE"
    progress = (ordinal - 1) / (length - 1)
    if progress < 1 / 3:
        return "FIRST_THIRD"
    if progress < 2 / 3:
        return "MIDDLE_THIRD"
    return "LAST_THIRD"


def clean_axes(
    cell: dict[str, str], reader_exact: int, patterns: dict[str, object]
) -> tuple[str, ...]:
    semantic = cell["v99r7_semantic_value_de"]
    if not reader_exact:
        return ()
    if cell["unknown_v99r7"] != "0":
        return ()
    if not cell["gdt734_confidence_level"].startswith(("W2", "W3")):
        return ()
    if cell["gdt734_composition_semantic_credit"] != "0":
        return ()
    if cell["component_export_credit"] != "0":
        return ()
    if g745.g739.retired_hits(semantic):
        return ()
    axes = set(g745.g739.axes_for(semantic, patterns))
    for name, pattern in g745.STAGE_PATTERNS.items():
        if pattern.search(semantic):
            axes.add(name)
    return tuple(axis for axis in AXIS_ORDER if axis in axes)


def neighbor_feature(
    locus: str,
    ordinal: int,
    by_line: dict[str, list[dict[str, str]]],
    exact: dict[tuple[str, int], int],
    cells: dict[tuple[str, int], dict[str, str]],
    patterns: dict[str, object],
) -> tuple[str, str]:
    line = by_line[locus]
    if ordinal < 1 or ordinal > len(line):
        return "EDGE", "EDGE"
    token = line[ordinal - 1]
    cell = cells[(locus, ordinal)]
    if token["eva"] != cell["surface"]:
        raise AssertionError(f"raw/cache mismatch at {locus}:{ordinal}")
    axes = clean_axes(
        cell, exact[(locus, int(token["token_index"]))], patterns
    )
    return cell["surface"], "|".join(axes) or "OPEN"


def closure_features(
    locus: str,
    center: int,
    by_line: dict[str, list[dict[str, str]]],
    exact: dict[tuple[str, int], int],
    cells: dict[tuple[str, int], dict[str, str]],
    patterns: dict[str, object],
) -> tuple[str, object, object]:
    line = by_line[locus]
    hits: list[int] = []
    for delta in (*range(-5, 0), *range(1, 6)):
        ordinal = center + delta
        if not 1 <= ordinal <= len(line):
            continue
        token = line[ordinal - 1]
        axes = clean_axes(
            cells[(locus, ordinal)],
            exact[(locus, int(token["token_index"]))],
            patterns,
        )
        if "CLOSE" in axes:
            hits.append(delta)
    left = min((-delta for delta in hits if delta < 0), default=None)
    right = min((delta for delta in hits if delta > 0), default=None)
    if left is None and right is None:
        return "NO_CLOSE_WITHIN_5", "NA", "NA"
    nearest = min(value for value in (left, right) if value is not None)
    sides = (
        "BOTH" if left == nearest and right == nearest
        else ("LEFT" if left == nearest else "RIGHT")
    )
    band = "D1" if nearest == 1 else ("D2" if nearest == 2 else "D3_5")
    return (
        f"{sides}_{band}",
        left if left is not None else "NA",
        right if right is not None else "NA",
    )


def occurrence_features(
    target_rows: list[dict[str, object]],
    pair_rows: list[dict[str, str]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    candidate_surfaces = {str(row["candidate_surface"]) for row in target_rows}
    known_surfaces = {row["known_neighbor_surface"] for row in pair_rows}
    selected_surfaces = candidate_surfaces | known_surfaces
    by_line, exact, guard = g745.g739.g738.token_context()
    cells = g745.g739.g738.compact_cells()
    _, patterns = g745.g739.load_axis_specs()
    selected = sorted(
        (cell for cell in cells.values() if cell["surface"] in selected_surfaces),
        key=lambda row: row["cell_id"],
    )
    if {cell["surface"] for cell in selected} != selected_surfaces:
        raise AssertionError("one or more selected complete surfaces absent from cache")
    if any(cell["page"].startswith(("f84", "f84r")) for cell in selected):
        raise AssertionError("forbidden folio entered selected cache")

    output: list[dict[str, object]] = []
    for number, cell in enumerate(selected, start=1):
        locus = cell["locus"]
        ordinal = int(cell["token_ordinal"])
        line = by_line[locus]
        token = line[ordinal - 1]
        if token["eva"] != cell["surface"]:
            raise AssertionError(f"selected raw/cache mismatch at {locus}:{ordinal}")
        reader_exact = exact[(locus, int(token["token_index"]))]
        left_surface, left_axes = neighbor_feature(
            locus, ordinal - 1, by_line, exact, cells, patterns
        )
        right_surface, right_axes = neighbor_feature(
            locus, ordinal + 1, by_line, exact, cells, patterns
        )
        closure, left_close, right_close = closure_features(
            locus, ordinal, by_line, exact, cells, patterns
        )
        roles = []
        if cell["surface"] in candidate_surfaces:
            roles.append("A3_CANDIDATE")
        if cell["surface"] in known_surfaces:
            roles.append("KNOWN_DISTANCE1_NEIGHBOR")
        output.append({
            "gdt746_occurrence_id": f"G746-O{number:04d}",
            "surface": cell["surface"],
            "surface_roles": "|".join(roles),
            "cell_id": cell["cell_id"],
            "page": cell["page"],
            "physical_folio": g745.physical_folio(cell["page"]),
            "locus": locus,
            "token_ordinal": ordinal,
            "reader_exact": reader_exact,
            "section": token["section"],
            "language": token["language"],
            "hand": token["hand"],
            "line_token_count": len(line),
            "line_position": line_position(ordinal, len(line)),
            "line_third": line_third(ordinal, len(line)),
            "left_whole_surface": left_surface,
            "left_whole_axes": left_axes,
            "right_whole_surface": right_surface,
            "right_whole_axes": right_axes,
            "nearest_close_signature": closure,
            "left_close_distance_le5": left_close,
            "right_close_distance_le5": right_close,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output, guard


def categorical_counts(rows: list[dict[str, object]], field: str) -> dict[str, float]:
    counter: Counter[str] = Counter(str(row[field]) for row in rows)
    return {key: float(value) for key, value in counter.items()}


def multilabel_counts(rows: list[dict[str, object]], field: str) -> dict[str, float]:
    counter: defaultdict[str, float] = defaultdict(float)
    for row in rows:
        labels = str(row[field]).split("|")
        share = 1.0 / len(labels)
        for label in labels:
            counter[label] += share
    return dict(counter)


def js_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) | set(right)
    left_total = sum(left.values())
    right_total = sum(right.values())
    if not keys or not left_total or not right_total:
        return 0.0
    p = {key: left.get(key, 0.0) / left_total for key in keys}
    q = {key: right.get(key, 0.0) / right_total for key in keys}
    middle = {key: (p[key] + q[key]) / 2 for key in keys}

    def divergence(source: dict[str, float]) -> float:
        return sum(
            value * math.log2(value / middle[key])
            for key, value in source.items()
            if value > 0
        )

    result = 1.0 - (divergence(p) + divergence(q)) / 2
    return min(1.0, max(0.0, result))


def support_jaccard(
    left_rows: list[dict[str, object]],
    right_rows: list[dict[str, object]],
    field: str,
) -> float:
    excluded = {"EDGE", "OPEN"}
    left = {str(row[field]) for row in left_rows} - excluded
    right = {str(row[field]) for row in right_rows} - excluded
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right)


def distribution_score(
    left_rows: list[dict[str, object]], right_rows: list[dict[str, object]]
) -> dict[str, float]:
    section = js_similarity(
        categorical_counts(left_rows, "section"),
        categorical_counts(right_rows, "section"),
    )
    position = js_similarity(
        categorical_counts(left_rows, "line_position"),
        categorical_counts(right_rows, "line_position"),
    )
    left_axes = js_similarity(
        multilabel_counts(left_rows, "left_whole_axes"),
        multilabel_counts(right_rows, "left_whole_axes"),
    )
    right_axes = js_similarity(
        multilabel_counts(left_rows, "right_whole_axes"),
        multilabel_counts(right_rows, "right_whole_axes"),
    )
    closure = js_similarity(
        categorical_counts(left_rows, "nearest_close_signature"),
        categorical_counts(right_rows, "nearest_close_signature"),
    )
    left_whole = js_similarity(
        categorical_counts(left_rows, "left_whole_surface"),
        categorical_counts(right_rows, "left_whole_surface"),
    )
    right_whole = js_similarity(
        categorical_counts(left_rows, "right_whole_surface"),
        categorical_counts(right_rows, "right_whole_surface"),
    )
    broad = (
        FEATURE_WEIGHTS["section"] * section
        + FEATURE_WEIGHTS["line_position"] * position
        + FEATURE_WEIGHTS["left_axes"] * left_axes
        + FEATURE_WEIGHTS["right_axes"] * right_axes
        + FEATURE_WEIGHTS["closure"] * closure
    )
    hybrid = 0.80 * broad + 0.10 * left_whole + 0.10 * right_whole
    local_core = 0.25 * (position + left_axes + right_axes + closure)
    local_hybrid = 0.80 * local_core + 0.10 * left_whole + 0.10 * right_whole
    return {
        "section": section,
        "line_position": position,
        "left_axes": left_axes,
        "right_axes": right_axes,
        "closure": closure,
        "left_whole": left_whole,
        "right_whole": right_whole,
        "left_whole_jaccard": support_jaccard(left_rows, right_rows, "left_whole_surface"),
        "right_whole_jaccard": support_jaccard(left_rows, right_rows, "right_whole_surface"),
        "broad": broad,
        "hybrid": hybrid,
        "local_core": local_core,
        "local_hybrid": local_hybrid,
    }


def percentile(value: float, values: list[float]) -> float:
    below = sum(item < value - 1e-12 for item in values)
    tied = sum(abs(item - value) <= 1e-12 for item in values)
    return (below + tied / 2) / len(values)


def pair_status(
    candidate_occurrences: int,
    neighbor_occurrences: int,
    score: float,
    rank_percentile: float,
    local_rank_percentile: float,
    components: list[float],
) -> str:
    balanced = sum(value >= 0.50 for value in components)
    if (
        candidate_occurrences >= 3
        and neighbor_occurrences >= 3
        and score >= 0.60
        and rank_percentile >= 0.80
        and local_rank_percentile >= 0.65
        and balanced >= 3
    ):
        return "D3_DISTRIBUTION_REINFORCED"
    if (
        candidate_occurrences >= 2
        and neighbor_occurrences >= 2
        and score >= 0.52
        and rank_percentile >= 0.55
        and local_rank_percentile >= 0.40
        and balanced >= 2
    ):
        return "D2_DISTRIBUTION_COMPATIBLE"
    if min(candidate_occurrences, neighbor_occurrences) < 2 and score >= 0.45:
        return "D1_SPARSE_COMPATIBLE"
    if (
        candidate_occurrences >= 3
        and neighbor_occurrences >= 3
        and score < 0.38
        and rank_percentile <= 0.20
    ):
        return "D0_DISTRIBUTION_MISMATCH"
    return "D1_MIXED_OR_ORDINARY"


def score_pairs(
    pair_sources: list[dict[str, str]],
    occurrences: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_surface_all: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        by_surface_all[str(row["surface"])].append(row)
    by_surface_exact = {
        surface: [row for row in rows if int(row["reader_exact"])]
        for surface, rows in by_surface_all.items()
    }
    known_surfaces = sorted({row["known_neighbor_surface"] for row in pair_sources})
    pairs_by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in pair_sources:
        pairs_by_candidate[row["candidate_surface"]].append(row)
    known_specs: dict[str, dict[str, str]] = {}
    for row in pair_sources:
        known = row["known_neighbor_surface"]
        if known in known_specs:
            if (
                known_specs[known]["known_neighbor_core_axes"]
                != row["known_neighbor_core_axes"]
                or known_specs[known]["known_neighbor_best_gloss_de"]
                != row["known_neighbor_best_gloss_de"]
            ):
                raise AssertionError(f"inconsistent known-whole card for {known}")
        known_specs[known] = row

    output: list[dict[str, object]] = []
    calibration: list[dict[str, object]] = []
    for candidate in sorted(pairs_by_candidate):
        candidate_exact = by_surface_exact[candidate]
        candidate_all = by_surface_all[candidate]
        comparison_exact: dict[str, dict[str, float]] = {}
        comparison_all: dict[str, dict[str, float]] = {}
        for known in known_surfaces:
            comparison_exact[known] = distribution_score(
                candidate_exact, by_surface_exact[known]
            )
            comparison_all[known] = distribution_score(
                candidate_all, by_surface_all[known]
            )
        exact_universe = [value["hybrid"] for value in comparison_exact.values()]
        all_universe = [value["hybrid"] for value in comparison_all.values()]
        exact_local_universe = [
            value["local_hybrid"] for value in comparison_exact.values()
        ]
        exact_median = statistics.median(exact_universe)
        all_median = statistics.median(all_universe)
        direct_surfaces = {
            row["known_neighbor_surface"] for row in pairs_by_candidate[candidate]
        }
        ranked_known = sorted(
            known_surfaces,
            key=lambda known: (
                -comparison_exact[known]["hybrid"], known
            ),
        )
        rank_by_known = {known: rank for rank, known in enumerate(ranked_known, 1)}
        candidate_axes = pairs_by_candidate[candidate][0]["candidate_consensus_axes"]
        for known in known_surfaces:
            exact_score = comparison_exact[known]
            all_score = comparison_all[known]
            spec = known_specs[known]
            known_axes = set(split_axes(spec["known_neighbor_core_axes"]))
            shared_axes = known_axes & set(split_axes(candidate_axes))
            calibration.append({
                "gdt746_calibration_id": f"G746-K{len(calibration) + 1:04d}",
                "candidate_surface": candidate,
                "known_surface": known,
                "selected_distance1_neighbor": int(known in direct_surfaces),
                "known_surface_core_axes": spec["known_neighbor_core_axes"],
                "known_surface_best_gloss_de": spec["known_neighbor_best_gloss_de"],
                "candidate_consensus_axes": candidate_axes,
                "shared_candidate_axes": joined(shared_axes),
                "candidate_occurrences_reader_exact": len(candidate_exact),
                "known_occurrences_reader_exact": len(by_surface_exact[known]),
                "hybrid_distribution_similarity": f"{exact_score['hybrid']:.6f}",
                "section_removed_local_similarity": f"{exact_score['local_hybrid']:.6f}",
                "known_whole_rank": rank_by_known[known],
                "known_whole_rank_percentile": f"{percentile(exact_score['hybrid'], exact_universe):.6f}",
                "section_removed_rank_percentile": f"{percentile(exact_score['local_hybrid'], exact_local_universe):.6f}",
                "top_five_distribution_neighbor": int(rank_by_known[known] <= 5),
                "all_occurrence_hybrid_similarity": f"{all_score['hybrid']:.6f}",
                "literal_identity_credit": 0,
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })
        for relation in sorted(
            pairs_by_candidate[candidate], key=lambda row: row["known_neighbor_surface"]
        ):
            known = relation["known_neighbor_surface"]
            exact_score = comparison_exact[known]
            all_score = comparison_all[known]
            exact_pct = percentile(exact_score["hybrid"], exact_universe)
            all_pct = percentile(all_score["hybrid"], all_universe)
            exact_local_pct = percentile(
                exact_score["local_hybrid"], exact_local_universe
            )
            exact_rank = 1 + sum(
                value > exact_score["hybrid"] + 1e-12 for value in exact_universe
            )
            status = pair_status(
                len(candidate_exact),
                len(by_surface_exact[known]),
                exact_score["hybrid"],
                exact_pct,
                exact_local_pct,
                [
                    exact_score["section"], exact_score["line_position"],
                    exact_score["left_axes"], exact_score["right_axes"],
                    exact_score["closure"],
                ],
            )
            output.append({
                "gdt746_pair_id": f"G746-P{len(output) + 1:03d}",
                "candidate_surface": candidate,
                "known_neighbor_surface": known,
                "levenshtein_distance": relation["levenshtein_distance"],
                "candidate_consensus_axes": relation["candidate_consensus_axes"],
                "known_neighbor_core_axes": relation["known_neighbor_core_axes"],
                "known_neighbor_best_gloss_de": relation["known_neighbor_best_gloss_de"],
                "candidate_occurrences_all": len(candidate_all),
                "candidate_occurrences_reader_exact": len(candidate_exact),
                "candidate_pages_reader_exact": len({row["page"] for row in candidate_exact}),
                "known_neighbor_occurrences_all": len(by_surface_all[known]),
                "known_neighbor_occurrences_reader_exact": len(by_surface_exact[known]),
                "known_neighbor_pages_reader_exact": len({row["page"] for row in by_surface_exact[known]}),
                "section_similarity": f"{exact_score['section']:.6f}",
                "line_position_similarity": f"{exact_score['line_position']:.6f}",
                "left_axis_context_similarity": f"{exact_score['left_axes']:.6f}",
                "right_axis_context_similarity": f"{exact_score['right_axes']:.6f}",
                "closure_proximity_similarity": f"{exact_score['closure']:.6f}",
                "left_exact_whole_similarity": f"{exact_score['left_whole']:.6f}",
                "right_exact_whole_similarity": f"{exact_score['right_whole']:.6f}",
                "left_exact_whole_support_jaccard": f"{exact_score['left_whole_jaccard']:.6f}",
                "right_exact_whole_support_jaccard": f"{exact_score['right_whole_jaccard']:.6f}",
                "broad_distribution_similarity": f"{exact_score['broad']:.6f}",
                "hybrid_distribution_similarity": f"{exact_score['hybrid']:.6f}",
                "section_removed_local_similarity": f"{exact_score['local_hybrid']:.6f}",
                "all_occurrence_hybrid_similarity": f"{all_score['hybrid']:.6f}",
                "reader_exact_sensitivity_delta": f"{exact_score['hybrid'] - all_score['hybrid']:.6f}",
                "comparison_universe_known_wholes": len(known_surfaces),
                "known_whole_rank": exact_rank,
                "known_whole_rank_percentile": f"{exact_pct:.6f}",
                "section_removed_rank_percentile": f"{exact_local_pct:.6f}",
                "all_occurrence_rank_percentile": f"{all_pct:.6f}",
                "comparison_universe_median_similarity": f"{exact_median:.6f}",
                "distribution_lift_over_median": f"{exact_score['hybrid'] - exact_median:.6f}",
                "all_occurrence_lift_over_median": f"{all_score['hybrid'] - all_median:.6f}",
                "distribution_status": status,
                "relation_scope": "COMPLETE_WHOLE_DISTRIBUTION_ANALOGY_ONLY",
                "literal_identity_credit": 0,
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })
    return output, calibration


def build_targets(
    census: list[dict[str, str]], pair_sources: list[dict[str, str]]
) -> list[dict[str, object]]:
    neighbors: dict[str, list[str]] = defaultdict(list)
    for row in pair_sources:
        neighbors[row["candidate_surface"]].append(row["known_neighbor_surface"])
    output = []
    for row in census:
        if row["analogy_confidence_level"] != A3_TIER:
            continue
        candidate = row["candidate_surface"]
        output.append({
            "gdt746_target_id": f"G746-T{len(output) + 1:02d}",
            "candidate_surface": candidate,
            "gdt745_cache_occurrences": row["cache_occurrences"],
            "gdt745_reader_exact_occurrences": row["reader_exact_occurrences"],
            "distance1_neighbor_wholes": len(neighbors[candidate]),
            "distance1_neighbor_surfaces": "|".join(sorted(neighbors[candidate])),
            "gdt745_consensus_axes": row["analogy_consensus_axes"],
            "gdt745_rival_axes": row["analogy_rival_axes"],
            "gdt745_functional_class": row["analogy_functional_class"],
            "gdt745_working_meaning_de": row["next_working_meaning_de"],
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def load_manual() -> dict[str, dict[str, str]]:
    path = ROOT / MANUAL_REL
    if not path.is_file():
        return {}
    rows = read_tsv(path)
    if len(rows) != 17 or len({row["candidate_surface"] for row in rows}) != 17:
        raise AssertionError("manual assessment deck must cover exactly 17 candidates")
    return {row["candidate_surface"]: row for row in rows}


def candidate_status(occurrence_count: int, statuses: Counter[str]) -> str:
    strong = statuses["D3_DISTRIBUTION_REINFORCED"]
    compatible = statuses["D2_DISTRIBUTION_COMPATIBLE"]
    mismatch = statuses["D0_DISTRIBUTION_MISMATCH"]
    if occurrence_count < 2:
        return "S1_SINGLETON_REMAINS_OPEN"
    if strong >= 2 and mismatch == 0:
        return "S3_MULTI_NEIGHBOR_DISTRIBUTION_REINFORCED"
    if strong + compatible >= 1 and mismatch == 0:
        return "S2_DISTRIBUTION_SUPPORTED"
    if strong + compatible >= 1 and mismatch:
        return "S2_MIXED_SUPPORT_AND_MISMATCH"
    if mismatch >= 2 and mismatch > strong + compatible:
        return "S0_NEIGHBOR_FAMILY_DISTRIBUTION_MISMATCH"
    return "S1_DISTRIBUTION_OPEN"


def build_candidate_census(
    targets: list[dict[str, object]],
    pair_rows: list[dict[str, object]],
    calibration_rows: list[dict[str, object]],
    occurrences: list[dict[str, object]],
) -> list[dict[str, object]]:
    pairs: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in pair_rows:
        pairs[str(row["candidate_surface"])].append(row)
    exact_counts = Counter(
        str(row["surface"]) for row in occurrences if int(row["reader_exact"])
    )
    calibration_by_candidate: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in calibration_rows:
        calibration_by_candidate[str(row["candidate_surface"])].append(row)
    manual = load_manual()
    output = []
    for target in targets:
        candidate = str(target["candidate_surface"])
        cards = pairs[candidate]
        statuses = Counter(str(row["distribution_status"]) for row in cards)
        status = candidate_status(exact_counts[candidate], statuses)
        supporting = [
            str(row["known_neighbor_surface"]) for row in cards
            if row["distribution_status"] in {
                "D3_DISTRIBUTION_REINFORCED", "D2_DISTRIBUTION_COMPATIBLE"
            }
        ]
        strong = [
            str(row["known_neighbor_surface"]) for row in cards
            if row["distribution_status"] == "D3_DISTRIBUTION_REINFORCED"
        ]
        mismatching = [
            str(row["known_neighbor_surface"]) for row in cards
            if row["distribution_status"] == "D0_DISTRIBUTION_MISMATCH"
        ]
        axis_counts: Counter[str] = Counter()
        for row in cards:
            if row["known_neighbor_surface"] not in supporting:
                continue
            axis_counts.update(split_axes(str(row["known_neighbor_core_axes"])))
        manual_row = manual.get(candidate, {})
        top_five = sorted(
            (
                row for row in calibration_by_candidate[candidate]
                if int(row["top_five_distribution_neighbor"])
            ),
            key=lambda row: int(row["known_whole_rank"]),
        )
        if len(top_five) != 5:
            raise AssertionError(f"top-five calibration changed for {candidate}")
        top_axis_counts: Counter[str] = Counter(
            axis
            for row in top_five
            for axis in split_axes(str(row["known_surface_core_axes"]))
        )
        top_consensus = {
            axis for axis, count in top_axis_counts.items() if count >= 3
        }
        form_axes = set(split_axes(str(target["gdt745_consensus_axes"])))
        default_action = (
            "RETAIN_AND_RAISE_DISTRIBUTIONAL_SUPPORT"
            if status.startswith("S3_") else
            "RETAIN_WITH_DISTRIBUTIONAL_SUPPORT"
            if status.startswith("S2_") and "MIXED" not in status else
            "RETAIN_BUT_MARK_MIXED"
            if "MIXED" in status else
            "RETAIN_FORM_ANALOGY_ONLY"
        )
        next_meaning = manual_row.get(
            "next_working_meaning_de", str(target["gdt745_working_meaning_de"])
        )
        action = manual_row.get("meaning_action", default_action)
        note = manual_row.get(
            "manual_note_de",
            "Automatische Verteilungsbilanz; konkrete Identität bleibt offen.",
        )
        scores = [float(row["hybrid_distribution_similarity"]) for row in cards]
        percentiles = [float(row["known_whole_rank_percentile"]) for row in cards]
        output.append({
            "gdt746_census_id": f"G746-C{len(output) + 1:02d}",
            "candidate_surface": candidate,
            "reader_exact_occurrences": exact_counts[candidate],
            "distance1_neighbor_wholes": len(cards),
            "pair_status_counts": count_string(
                str(row["distribution_status"]) for row in cards
            ),
            "mean_neighbor_hybrid_similarity": f"{statistics.mean(scores):.6f}",
            "median_neighbor_rank_percentile": f"{statistics.median(percentiles):.6f}",
            "strongly_reinforced_neighbors": joined(strong),
            "compatible_or_reinforced_neighbors": joined(supporting),
            "mismatching_neighbors": joined(mismatching),
            "distribution_supported_axis_counts": weighted_count_string(
                {key: float(value) for key, value in axis_counts.items()}
            ),
            "top5_distribution_surfaces": "|".join(
                str(row["known_surface"]) for row in top_five
            ),
            "top5_direct_distance1_neighbors": sum(
                int(row["selected_distance1_neighbor"]) for row in top_five
            ),
            "top5_distribution_axis_counts": weighted_count_string(
                {key: float(value) for key, value in top_axis_counts.items()}
            ),
            "top5_distribution_consensus_axes": joined(top_consensus),
            "form_and_top5_axis_agreement": joined(form_axes & top_consensus),
            "top5_axes_outside_form_consensus": joined(top_consensus - form_axes),
            "distribution_status": status,
            "gdt745_consensus_axes": target["gdt745_consensus_axes"],
            "gdt745_rival_axes": target["gdt745_rival_axes"],
            "gdt745_working_meaning_de": target["gdt745_working_meaning_de"],
            "meaning_action": action,
            "next_working_meaning_de": next_meaning,
            "manual_assessment_note_de": note,
            "positive_evidence": (
                f"{len(strong)} stark und {len(supporting) - len(strong)} kompatibel "
                f"von {len(cards)} direkten Ganzwortnachbarn; Medianrang "
                f"{statistics.median(percentiles):.3f} im 46-Wort-Vergleich"
            ),
            "counterevidence": (
                f"{len(mismatching)} klare Verteilungsgegenfälle; "
                f"{statuses['D1_MIXED_OR_ORDINARY']} gewöhnliche oder gemischte Paare; "
                "Formnähe benennt weiterhin keinen Stoff"
            ),
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
            "unseen_form_export": 0,
        })
    return output


def write_reader(
    path: Path,
    census: list[dict[str, object]],
    pairs: list[dict[str, object]],
) -> None:
    pair_map: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in pairs:
        pair_map[str(row["candidate_surface"])].append(row)
    lines = [
        "# GDT746 Ganzwort-Verteilungsleser", "",
        "Die Karten vergleichen vollständige EVA-Formen. Kein Buchstabe und kein",
        "Teilstring erhält einen Wert. `Rang` bezeichnet die Stellung des echten",
        "Distanz-1-Nachbarn unter 46 bekannten Vergleichswörtern.", "",
    ]
    for row in census:
        candidate = str(row["candidate_surface"])
        lines.extend([
            f"## `{candidate}` — {row['distribution_status']}", "",
            f"- Arbeitswert: {row['next_working_meaning_de']}",
            f"- Aktion: {row['meaning_action']}",
            f"- Evidenz: {row['positive_evidence']}",
            f"- Gegenbeleg: {row['counterevidence']}",
            f"- Top-5-Verteilungen: {row['top5_distribution_surfaces']}",
            f"- Unabhängige Achsen: {row['top5_distribution_consensus_axes']}; "
            f"Übereinstimmung mit Formfamilie: {row['form_and_top5_axis_agreement']}",
            f"- Manuelle Einordnung: {row['manual_assessment_note_de']}",
            "- Direkte Nachbarn:", "",
        ])
        for pair in sorted(
            pair_map[candidate],
            key=lambda item: (
                -float(item["known_whole_rank_percentile"]),
                str(item["known_neighbor_surface"]),
            ),
        ):
            lines.append(
                f"  - `{pair['known_neighbor_surface']}` — "
                f"{pair['distribution_status']}; Hybrid "
                f"{float(pair['hybrid_distribution_similarity']):.3f}; "
                f"Rang {pair['known_whole_rank']}/46; "
                f"{pair['known_neighbor_best_gloss_de']}"
            )
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def edge_packet(
    output_dir: Path,
    pairs: list[dict[str, object]],
    occurrences: list[dict[str, object]],
) -> dict[str, object]:
    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        if int(row["reader_exact"]):
            by_surface[str(row["surface"])].append(row)
    ranked = sorted(
        pairs,
        key=lambda row: (
            PAIR_STATUS_ORDER.index(str(row["distribution_status"])),
            -float(row["known_whole_rank_percentile"]),
            -float(row["hybrid_distribution_similarity"]),
            str(row["candidate_surface"]),
            str(row["known_neighbor_surface"]),
        ),
    )
    selected = None
    for pair in ranked:
        candidate_rows = by_surface[str(pair["candidate_surface"])]
        known_rows = by_surface[str(pair["known_neighbor_surface"])]
        for candidate_row in candidate_rows:
            matches = [row for row in known_rows if row["page"] == candidate_row["page"]]
            if matches:
                selected = (
                    pair,
                    candidate_row,
                    sorted(matches, key=lambda row: row["cell_id"])[0],
                )
                break
        if selected:
            break
    if selected is None:
        selected = (
            ranked[0],
            by_surface[str(ranked[0]["candidate_surface"])][0],
            by_surface[str(ranked[0]["known_neighbor_surface"])][0],
        )
    pair, candidate, known = selected
    packet = [{
        "edge_id": "G746E001",
        "batch_id": "GDT746_WHOLE_DISTRIBUTION_CONTEXT",
        "page": candidate["page"],
        "physical_folio": candidate["physical_folio"],
        "diagram_unit_id": "CACHED_TEXT_DISTRIBUTION_CONTEXT",
        "pivot_visual_id": f"UNKNOWN_WHOLE_{candidate['surface']}",
        "pivot_locus": f"{candidate['locus']}@{candidate['token_ordinal']}",
        "target_visual_id": f"KNOWN_WHOLE_{known['surface']}_{known['page']}",
        "target_locus": f"{known['locus']}@{known['token_ordinal']}",
        "relation_type": "COMPLETE_WHOLE_DISTRIBUTION_ANALOGY",
        "direction_basis": "SECTION_POSITION_FLANKS_CLOSURE_DISTRIBUTION",
        "ownership_basis": "COMPLETE_WHOLE_NO_COMPONENT_EXPORT",
        "geometry_only_selection": "FALSE",
        "source_manifest_id": "GDT746",
        "page_crop_sha256": "NONE",
        "pivot_crop_sha256": "NONE",
        "target_crop_sha256": "NONE",
        "source_aware_localizer": "GDT746_BUILDER",
        "relation_reviewer": "PENDING_EXTERNAL",
        "relation_confidence": pair["distribution_status"],
        "ambiguity_state": "DISTRIBUTION_ONLY_LITERAL_IDENTITY_OPEN",
        "formal_access_state": "FORMAL_ACCESSED",
        "fold_assignment": "NONE",
        "eligibility_status": "INELIGIBLE_FORMAL_CONTEXT_RELATION",
    }]
    packet_path = output_dir / "GDT746_GDT388_DISTRIBUTION_EDGE_PACKET.tsv"
    write_tsv(packet_path, packet, list(packet[0]))
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode not in {0, 1} or not completed.stdout:
        raise AssertionError(f"edge intake failed: {completed.stderr}")
    intake = json.loads(completed.stdout)
    if intake["status"] != "INVALID_PACKET" or intake["score_ready"]:
        raise AssertionError("distribution packet unexpectedly score-ready")
    (output_dir / "GDT746_GDT388_EDGE_INTAKE.json").write_text(
        json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return intake


def build(output_dir: Path) -> dict[str, object]:
    census_source = read_tsv(ROOT / G745_CENSUS_REL)
    analogy_source = read_tsv(ROOT / G745_ANALOGY_REL)
    a3_surfaces = {
        row["candidate_surface"]
        for row in census_source
        if row["analogy_confidence_level"] == A3_TIER
    }
    pair_sources = [
        row for row in analogy_source
        if row["candidate_surface"] in a3_surfaces
        and row["levenshtein_distance"] == "1"
        and row["within_closest_layer"] == "1"
    ]
    if len(a3_surfaces) != 17 or len(pair_sources) != 52:
        raise AssertionError("GDT745 A3 target/pair boundary changed")
    if len({row["known_neighbor_surface"] for row in pair_sources}) != 46:
        raise AssertionError("GDT745 known-neighbor comparison universe changed")

    targets = build_targets(census_source, pair_sources)
    occurrences, guard = occurrence_features(targets, pair_sources)
    if len(occurrences) != 1523:
        raise AssertionError("selected 63-surface occurrence universe changed")
    pairs, calibration = score_pairs(pair_sources, occurrences)
    candidate_census = build_candidate_census(
        targets, pairs, calibration, occurrences
    )
    if (
        len(targets) != 17 or len(pairs) != 52 or len(calibration) != 782
        or len(candidate_census) != 17
    ):
        raise AssertionError("GDT746 output cardinality changed")

    output_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(output_dir / "A3_17_TARGETS.tsv", targets, list(targets[0]))
    write_tsv(
        output_dir / "SURFACE_63_OCCURRENCE_FEATURES.tsv",
        occurrences,
        list(occurrences[0]),
    )
    write_tsv(
        output_dir / "CALIBRATION_782_CANDIDATE_KNOWN_SCORES.tsv",
        calibration,
        list(calibration[0]),
    )
    write_tsv(
        output_dir / "PAIR_52_DISTRIBUTION_SCORES.tsv", pairs, list(pairs[0])
    )
    write_tsv(
        output_dir / "CANDIDATE_17_DISTRIBUTION_CENSUS.tsv",
        candidate_census,
        list(candidate_census[0]),
    )
    write_reader(
        output_dir / "GDT746_WHOLE_DISTRIBUTION_READER.md",
        candidate_census,
        pairs,
    )
    intake = edge_packet(output_dir, pairs, occurrences)

    pair_counts = Counter(str(row["distribution_status"]) for row in pairs)
    candidate_counts = Counter(
        str(row["distribution_status"]) for row in candidate_census
    )
    top_five_direct_slots = sum(
        int(row["top5_direct_distance1_neighbors"]) for row in candidate_census
    )
    expected_top_five_direct_slots = 5 * len(pairs) / 46
    top_five_direct_candidates = sum(
        int(row["top5_direct_distance1_neighbors"]) > 0
        for row in candidate_census
    )
    form_distribution_axis_agreements = sum(
        row["form_and_top5_axis_agreement"] != "NONE"
        for row in candidate_census
    )
    strongest = sorted(
        pairs,
        key=lambda row: (
            -float(row["known_whole_rank_percentile"]),
            -float(row["hybrid_distribution_similarity"]),
            str(row["candidate_surface"]),
        ),
    )[:10]
    status = (
        f"PARTIAL__17_A3_COMPLETE_WHOLES__52_DISTANCE1_RELATIONS__"
        f"63_SURFACES__1523_OCCURRENCES__"
        f"{pair_counts['D3_DISTRIBUTION_REINFORCED']}_PAIR_REINFORCED__"
        f"{pair_counts['D2_DISTRIBUTION_COMPATIBLE']}_PAIR_COMPATIBLE__"
        f"{candidate_counts['S3_MULTI_NEIGHBOR_DISTRIBUTION_REINFORCED']}_CANDIDATE_MULTI_REINFORCED__"
        f"{top_five_direct_slots}_DIRECT_IN_85_TOP5_SLOTS__"
        f"{form_distribution_axis_agreements}_OF_17_FORM_DISTRIBUTION_AXIS_AGREEMENTS__"
        "ZERO_LITERAL_IDENTITIES__ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
    )
    result = {
        "schema": "GDT746_RESULT_V1",
        "status": status,
        "question": (
            "Do GDT745's seventeen strongest complete-whole edit analogies also "
            "share section, line-position, left/right whole context and closure "
            "proximity distributions with their fifty-two distance-one neighbors?"
        ),
        "scope": {
            "candidate_wholes": len(targets),
            "distance_one_relations": len(pairs),
            "candidate_known_calibration_relations": len(calibration),
            "known_neighbor_wholes": len({row["known_neighbor_surface"] for row in pairs}),
            "selected_surfaces": len({row["surface"] for row in occurrences}),
            "selected_occurrences": len(occurrences),
            "selected_pages": len({row["page"] for row in occurrences}),
            "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in occurrences),
        },
        "pair_status_counts": dict(sorted(pair_counts.items())),
        "candidate_status_counts": dict(sorted(candidate_counts.items())),
        "calibration_summary": {
            "top_five_slots": 85,
            "direct_distance_one_neighbors_in_top_five_slots": top_five_direct_slots,
            "expected_direct_slots_from_deck_share": expected_top_five_direct_slots,
            "direct_slot_enrichment_not_probability": (
                top_five_direct_slots / expected_top_five_direct_slots
            ),
            "candidates_with_direct_neighbor_in_top_five": top_five_direct_candidates,
            "candidates_with_form_top5_axis_agreement": form_distribution_axis_agreements,
        },
        "strongest_relation_cards": [
            {
                "candidate_surface": row["candidate_surface"],
                "known_neighbor_surface": row["known_neighbor_surface"],
                "distribution_status": row["distribution_status"],
                "hybrid_similarity": float(row["hybrid_distribution_similarity"]),
                "rank": int(row["known_whole_rank"]),
                "rank_percentile": float(row["known_whole_rank_percentile"]),
                "neighbor_gloss_de": row["known_neighbor_best_gloss_de"],
            }
            for row in strongest
        ],
        "candidate_cards": [
            {
                "candidate_surface": row["candidate_surface"],
                "distribution_status": row["distribution_status"],
                "meaning_action": row["meaning_action"],
                "next_working_meaning_de": row["next_working_meaning_de"],
                "positive_evidence": row["positive_evidence"],
                "counterevidence": row["counterevidence"],
            }
            for row in candidate_census
        ],
        "guard": guard,
        "edge_intake": intake,
        "method_note": (
            "All comparisons use complete observed surfaces. Primary scores use "
            "alternate-reader-exact occurrences; all-ZL3b scores are a sensitivity. "
            "The selected distance-one neighbor is ranked against the same 46 known "
            "whole distributions for that candidate."
        ),
        "claim_ceiling": {
            "confirmed_lexemes": 0,
            "literal_identifications": 0,
            "component_export_credit": 0,
            "unseen_form_predictions": 0,
        },
        "artifacts": {},
    }
    for name in OUTPUT_NAMES:
        result["artifacts"][name] = sha256(output_dir / name)
    result_path = output_dir / "RESULT.json"
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
