#!/usr/bin/env python3
"""Test GDT748 whole-role leads away from the serial frames that found them.

Every EVA surface is treated as an opaque complete written form. The sixteen
recurrent GDT748 targets, plus the deliberately conflicted qochey diagnostic,
are followed through the existing 179-page cache. GDT748 discovery positions
are removed before comparison with GDT746's fixed forty-six-whole deck.
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
BASE_REL = Path("experiments/yolo/gdt749_outside_frame_whole_role_distribution")
EXP = ROOT / BASE_REL
DEFAULT_ARTIFACTS = EXP / "artifacts"

G746_RUN_REL = Path(
    "experiments/yolo/gdt746_whole_analogy_distribution_test/src/run.py"
)
G746_CALIBRATION_REL = Path(
    "experiments/yolo/gdt746_whole_analogy_distribution_test/artifacts/"
    "CALIBRATION_782_CANDIDATE_KNOWN_SCORES.tsv"
)
G748_SURFACE_REL = Path(
    "experiments/yolo/gdt748_complete_whole_serial_paradigm_census/artifacts/"
    "SURFACE_PREDICTION_CENSUS.tsv"
)
G748_EVIDENCE_REL = Path(
    "experiments/yolo/gdt748_complete_whole_serial_paradigm_census/artifacts/"
    "FORM_BRIDGED_POSITION_EVIDENCE.tsv"
)

OUTPUT_NAMES = (
    "TARGET_17_FIXED_DECK.tsv",
    "TARGET_OCCURRENCE_AUDIT.tsv",
    "REFERENCE_DISTRIBUTION_SCORES.tsv",
    "KNOWN_46_LEAVE_SELF_CALIBRATION.tsv",
    "TARGET_OUTSIDE_ROLE_CENSUS.tsv",
    "QOCHEY_HYPOTHESIS_SPLIT.tsv",
    "GDT749_OUTSIDE_FRAME_READER.md",
    "GDT749_GDT388_OUTSIDE_EDGE_PACKET.tsv",
    "GDT749_GDT388_EDGE_INTAKE.json",
    "RESULT.json",
)

AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "BEGIN_STAGE", "MIDDLE_STAGE",
    "END_STAGE", "LEVEL_II", "LEVEL_III", "AMOUNT", "PART", "MATERIAL",
    "PREPARATION", "PROCESS", "PASS", "CLOSE",
)
DIMENSIONS = {
    "THERMAL": ("HOT", "COLD"),
    "MOISTURE": ("DRY", "MOIST"),
    "STAGE": ("BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE"),
}
QUALITY_STAGE_AXES = tuple(
    axis for dimension in DIMENSIONS.values() for axis in dimension
)
QOCHEY_HYPOTHESES = (
    ("QH1_STRONGEST_SERIAL", ("DRY", "MIDDLE_STAGE")),
    ("QH2_END_ONLY", ("END_STAGE",)),
    ("QH3_HOT_END_RIVAL", ("HOT", "END_STAGE")),
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g746 = load_module("gdt746_builder_for_gdt749", ROOT / G746_RUN_REL)


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
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def split_axes(value: object) -> tuple[str, ...]:
    text = str(value)
    return () if text in {"", "NONE"} else tuple(text.split("|"))


def joined(values: Iterable[str]) -> str:
    ordered = set(values)
    return "|".join(axis for axis in AXIS_ORDER if axis in ordered) or "NONE"


def count_string(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def axis_count_string(counts: Counter[str]) -> str:
    return "|".join(
        f"{axis}:{counts[axis]}" for axis in AXIS_ORDER if counts[axis]
    ) or "NONE"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hypergeom_tail(population: int, successes: int, draws: int, observed: int) -> float:
    """Descriptive P(X >= observed) for a top draw without replacement."""
    denominator = math.comb(population, draws)
    maximum = min(successes, draws)
    return sum(
        math.comb(successes, value)
        * math.comb(population - successes, draws - value)
        / denominator
        for value in range(observed, maximum + 1)
        if 0 <= draws - value <= population - successes
    )


def rival_axes(expected: Iterable[str]) -> tuple[str, ...]:
    wanted = set(expected)
    rivals: set[str] = set()
    for members in DIMENSIONS.values():
        if wanted.intersection(members):
            rivals.update(set(members) - wanted)
    return tuple(axis for axis in AXIS_ORDER if axis in rivals)


def reference_specs() -> list[dict[str, str]]:
    rows = read_tsv(ROOT / G746_CALIBRATION_REL)
    by_surface: dict[str, dict[str, str]] = {}
    for row in rows:
        surface = row["known_surface"]
        spec = {
            "known_neighbor_surface": surface,
            "known_surface": surface,
            "known_axes": row["known_surface_core_axes"],
            "known_gloss_de": row["known_surface_best_gloss_de"],
        }
        if surface in by_surface and by_surface[surface] != spec:
            raise AssertionError(f"reference card changed within deck: {surface}")
        by_surface[surface] = spec
    output = [by_surface[surface] for surface in sorted(by_surface)]
    if len(output) != 46:
        raise AssertionError("GDT746 fixed reference deck is no longer forty-six wholes")
    return output


def build_targets() -> list[dict[str, object]]:
    surfaces = read_tsv(ROOT / G748_SURFACE_REL)
    selected = [
        row for row in surfaces
        if row["serial_status"].startswith(("S2_", "S3_"))
    ]
    if len(selected) != 16:
        raise AssertionError("GDT748 recurrent role deck is no longer sixteen forms")
    output: list[dict[str, object]] = []
    for row in selected:
        output.append({
            "gdt749_target_id": f"G749-T{len(output) + 1:02d}",
            "target_surface": row["target_surface"],
            "target_class": "GDT748_RECURRENT_S2_S3_ROLE",
            "gdt748_serial_status": row["serial_status"],
            "gdt748_role_decision": row["role_decision"],
            "discovery_position_evidence_units": row["position_evidence_units"],
            "discovery_pages": row["pages"],
            "prior_role_axes": row["serial_consensus_axes"],
            "prior_rival_axes": "NONE",
            "prior_working_default_de": row["automatic_working_default_de"],
            "gdt747_prior_axes": row["gdt747_prior_axes"],
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    qochey = next(row for row in surfaces if row["target_surface"] == "qochey")
    output.append({
        "gdt749_target_id": "G749-T17",
        "target_surface": "qochey",
        "target_class": "GDT748_CONFLICTED_SPLIT_DIAGNOSTIC",
        "gdt748_serial_status": qochey["serial_status"],
        "gdt748_role_decision": qochey["role_decision"],
        "discovery_position_evidence_units": qochey["position_evidence_units"],
        "discovery_pages": qochey["pages"],
        "prior_role_axes": "DRY|MIDDLE_STAGE",
        "prior_rival_axes": "HOT|END_STAGE",
        "prior_working_default_de": (
            "stärkster Serienlead trocken/Mittelstufe; End-/Heißrivalen offen"
        ),
        "gdt747_prior_axes": qochey["gdt747_prior_axes"],
        "literal_identity": "OPEN",
        "confirmed_lexeme": 0,
        "component_export_credit": 0,
    })
    if len({str(row["target_surface"]) for row in output}) != 17:
        raise AssertionError("target surfaces are not unique")
    return output


def discovery_keys() -> tuple[set[tuple[str, str, int]], dict[str, list[str]]]:
    rows = read_tsv(ROOT / G748_EVIDENCE_REL)
    keys: set[tuple[str, str, int]] = set()
    loci: defaultdict[str, list[str]] = defaultdict(list)
    for row in rows:
        key = (row["target_surface"], row["locus"], int(row["target_ordinal"]))
        if key in keys:
            raise AssertionError(f"duplicate GDT748 physical target position: {key}")
        keys.add(key)
        loci[row["target_surface"]].append(
            f"{row['locus']}@{row['target_ordinal']}"
        )
    return keys, loci


def build_occurrence_audit(
    targets: list[dict[str, object]], references: list[dict[str, str]]
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    target_surfaces = {str(row["target_surface"]) for row in targets}
    feature_rows, guard = g746.occurrence_features(
        [{"candidate_surface": surface} for surface in sorted(target_surfaces)],
        references,
    )
    keys, loci = discovery_keys()
    by_line, _, _ = g746.g745.g739.g738.token_context()
    target_map = {str(row["target_surface"]): row for row in targets}
    audit: list[dict[str, object]] = []
    for row in feature_rows:
        surface = str(row["surface"])
        if surface not in target_surfaces:
            continue
        key = (surface, str(row["locus"]), int(row["token_ordinal"]))
        discovery = int(key in keys)
        immediate_axes = set(split_axes(row["left_whole_axes"])) | set(
            split_axes(row["right_whole_axes"])
        )
        immediate_axes -= {"OPEN", "EDGE"}
        target = target_map[surface]
        expected = set(split_axes(target["prior_role_axes"]))
        rivals = set(rival_axes(expected))
        line = " ".join(token["eva"] for token in by_line[str(row["locus"])])
        audit.append({
            "gdt749_occurrence_id": f"G749-O{len(audit) + 1:04d}",
            "target_surface": surface,
            "cell_id": row["cell_id"],
            "page": row["page"],
            "physical_folio": row["physical_folio"],
            "locus": row["locus"],
            "token_ordinal": row["token_ordinal"],
            "reader_exact": row["reader_exact"],
            "gdt748_discovery_position": discovery,
            "outside_discovery_primary": int(not discovery and int(row["reader_exact"])),
            "section": row["section"],
            "language": row["language"],
            "hand": row["hand"],
            "line_token_count": row["line_token_count"],
            "line_position": row["line_position"],
            "line_third": row["line_third"],
            "left_whole_surface": row["left_whole_surface"],
            "left_whole_axes": row["left_whole_axes"],
            "right_whole_surface": row["right_whole_surface"],
            "right_whole_axes": row["right_whole_axes"],
            "immediate_known_axis_union": joined(immediate_axes),
            "immediate_prior_axis_hits": joined(immediate_axes & expected),
            "immediate_rival_axis_hits": joined(immediate_axes & rivals),
            "nearest_close_signature": row["nearest_close_signature"],
            "left_close_distance_le5": row["left_close_distance_le5"],
            "right_close_distance_le5": row["right_close_distance_le5"],
            "written_line_eva": line,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    actual = Counter(
        str(row["target_surface"]) for row in audit
        if row["gdt748_discovery_position"]
    )
    expected = {
        str(row["target_surface"]): int(row["discovery_position_evidence_units"])
        for row in targets
    }
    if dict(actual) != expected:
        raise AssertionError(f"discovery exclusion mismatch: {dict(actual)} != {expected}")
    for row in targets:
        row["discovery_loci"] = "|".join(loci[str(row["target_surface"])])
    return audit, feature_rows, guard


def score_references(
    targets: list[dict[str, object]],
    references: list[dict[str, str]],
    audit: list[dict[str, object]],
    feature_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    target_exact: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    target_all: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in audit:
        if int(row["gdt748_discovery_position"]):
            continue
        surface = str(row["target_surface"])
        target_all[surface].append(row)
        if int(row["reader_exact"]):
            target_exact[surface].append(row)

    reference_exact: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    reference_all: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    reference_surfaces = {row["known_surface"] for row in references}
    for row in feature_rows:
        surface = str(row["surface"])
        if surface not in reference_surfaces:
            continue
        reference_all[surface].append(row)
        if int(row["reader_exact"]):
            reference_exact[surface].append(row)

    output: list[dict[str, object]] = []
    for target in targets:
        surface = str(target["target_surface"])
        expected = set(split_axes(target["prior_role_axes"]))
        rivals = set(rival_axes(expected))
        candidate_rows: list[dict[str, object]] = []
        for reference in references:
            known = reference["known_surface"]
            if known == surface:
                continue
            exact_score = g746.distribution_score(
                target_exact[surface], reference_exact[known]
            )
            all_score = g746.distribution_score(
                target_all[surface], reference_all[known]
            )
            known_axes = set(split_axes(reference["known_axes"]))
            candidate_rows.append({
                "target_surface": surface,
                "prior_role_axes": target["prior_role_axes"],
                "reference_surface": known,
                "reference_axes": reference["known_axes"],
                "reference_gloss_de": reference["known_gloss_de"],
                "outside_occurrences_reader_exact": len(target_exact[surface]),
                "outside_occurrences_all_readings": len(target_all[surface]),
                "reference_occurrences_reader_exact": len(reference_exact[known]),
                "section_similarity": f"{exact_score['section']:.6f}",
                "line_position_similarity": f"{exact_score['line_position']:.6f}",
                "left_axis_context_similarity": f"{exact_score['left_axes']:.6f}",
                "right_axis_context_similarity": f"{exact_score['right_axes']:.6f}",
                "closure_proximity_similarity": f"{exact_score['closure']:.6f}",
                "left_exact_whole_similarity": f"{exact_score['left_whole']:.6f}",
                "right_exact_whole_similarity": f"{exact_score['right_whole']:.6f}",
                "hybrid_distribution_similarity": f"{exact_score['hybrid']:.6f}",
                "section_removed_local_similarity": f"{exact_score['local_hybrid']:.6f}",
                "all_reading_hybrid_similarity": f"{all_score['hybrid']:.6f}",
                "expected_axis_overlap": joined(known_axes & expected),
                "contains_all_prior_axes": int(expected <= known_axes),
                "same_dimension_rival_overlap": joined(known_axes & rivals),
                "literal_identity_credit": 0,
                "confirmed_lexeme": 0,
                "component_export_credit": 0,
            })
        ranked = sorted(
            candidate_rows,
            key=lambda row: (
                -float(row["hybrid_distribution_similarity"]),
                str(row["reference_surface"]),
            ),
        )
        universe = [float(row["hybrid_distribution_similarity"]) for row in ranked]
        local_universe = [float(row["section_removed_local_similarity"]) for row in ranked]
        for rank, row in enumerate(ranked, start=1):
            value = float(row["hybrid_distribution_similarity"])
            local = float(row["section_removed_local_similarity"])
            row["reference_rank"] = rank
            row["reference_rank_percentile"] = f"{g746.percentile(value, universe):.6f}"
            row["section_removed_rank_percentile"] = f"{g746.percentile(local, local_universe):.6f}"
            row["top_five_reference"] = int(rank <= 5)
            row["gdt749_score_id"] = ""
        output.extend(ranked)
    output.sort(key=lambda row: (str(row["target_surface"]), int(row["reference_rank"])))
    for number, row in enumerate(output, start=1):
        row["gdt749_score_id"] = f"G749-S{number:04d}"
    return output


def axis_metrics(
    axis: str,
    candidate_rows: list[dict[str, object]],
    top_five: list[dict[str, object]],
) -> dict[str, object]:
    universe_hits = sum(axis in split_axes(row["reference_axes"]) for row in candidate_rows)
    top_hits = sum(axis in split_axes(row["reference_axes"]) for row in top_five)
    expected_slots = 5 * universe_hits / len(candidate_rows)
    enrichment = top_hits / expected_slots if expected_slots else 0.0
    tail = hypergeom_tail(len(candidate_rows), universe_hits, 5, top_hits)
    ranks = [
        int(row["reference_rank"]) for row in candidate_rows
        if axis in split_axes(row["reference_axes"])
    ]
    return {
        "universe": universe_hits,
        "top": top_hits,
        "expected": expected_slots,
        "enrichment": enrichment,
        "tail": tail,
        "best_rank": min(ranks) if ranks else 999,
    }


def local_polarity_tally(
    rows: list[dict[str, object]],
    expected: set[str],
    rivals: set[str],
) -> tuple[int, int, int, int]:
    expected_only = rival_only = both = neither = 0
    for row in rows:
        axes = set(split_axes(row["left_whole_axes"])) | set(
            split_axes(row["right_whole_axes"])
        )
        expected_hit = bool(axes & expected)
        rival_hit = bool(axes & rivals)
        if expected_hit and rival_hit:
            both += 1
        elif expected_hit:
            expected_only += 1
        elif rival_hit:
            rival_only += 1
        else:
            neither += 1
    return expected_only, rival_only, both, neither


def build_known_calibration(
    references: list[dict[str, str]],
    feature_rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Apply the target rule to known wholes while excluding self-comparison."""
    exact_by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    reference_surfaces = {row["known_surface"] for row in references}
    reference_exact = [
        row for row in feature_rows
        if row["surface"] in reference_surfaces and int(row["reader_exact"])
    ]
    for row in reference_exact:
        exact_by_surface[str(row["surface"])].append(row)

    output: list[dict[str, object]] = []
    total_tp = total_fp = total_fn = 0
    local_positive = local_tied = local_negative = 0
    local_true_hits = local_rival_hits = 0
    quality_stage = set(QUALITY_STAGE_AXES)
    for reference in references:
        surface = reference["known_surface"]
        comparison: list[dict[str, object]] = []
        for other in references:
            other_surface = other["known_surface"]
            if other_surface == surface:
                continue
            score = g746.distribution_score(
                exact_by_surface[surface], exact_by_surface[other_surface]
            )
            comparison.append({
                "reference_surface": other_surface,
                "reference_axes": other["known_axes"],
                "hybrid_distribution_similarity": score["hybrid"],
            })
        comparison.sort(
            key=lambda row: (
                -float(row["hybrid_distribution_similarity"]),
                str(row["reference_surface"]),
            )
        )
        for rank, row in enumerate(comparison, start=1):
            row["reference_rank"] = rank
        top = comparison[:5]
        predicted = {
            axis for axis in QUALITY_STAGE_AXES
            if (
                int(axis_metrics(axis, comparison, top)["top"]) >= 2
                and float(axis_metrics(axis, comparison, top)["enrichment"]) >= 1.35
                and int(axis_metrics(axis, comparison, top)["best_rank"]) <= 5
            )
        }
        truth = set(split_axes(reference["known_axes"])) & quality_stage
        recovered = predicted & truth
        false = predicted - truth
        missed = truth - predicted
        total_tp += len(recovered)
        total_fp += len(false)
        total_fn += len(missed)

        rivals = set(rival_axes(truth))
        expected_only, rival_only, both, neither = local_polarity_tally(
            exact_by_surface[surface], truth, rivals
        ) if truth else (0, 0, 0, len(exact_by_surface[surface]))
        local_true_hits += expected_only + both
        local_rival_hits += rival_only + both
        if truth:
            if expected_only + both > rival_only + both:
                local_positive += 1
            elif expected_only + both == rival_only + both:
                local_tied += 1
            else:
                local_negative += 1
        output.append({
            "gdt749_calibration_id": f"G749-K{len(output) + 1:02d}",
            "known_surface": surface,
            "reader_exact_occurrences": len(exact_by_surface[surface]),
            "true_quality_stage_axes": joined(truth),
            "predicted_quality_stage_axes": joined(predicted),
            "recovered_true_axes": joined(recovered),
            "false_predicted_axes": joined(false),
            "missed_true_axes": joined(missed),
            "top5_reference_surfaces": "|".join(
                str(row["reference_surface"]) for row in top
            ),
            "local_true_only_positions": expected_only,
            "local_rival_only_positions": rival_only,
            "local_both_positions": both,
            "local_neither_positions": neither,
            "literal_identity_credit": 0,
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    precision = total_tp / (total_tp + total_fp)
    recall = total_tp / (total_tp + total_fn)
    summary = {
        "known_wholes": len(output),
        "quality_stage_true_positive_labels": total_tp,
        "quality_stage_false_positive_labels": total_fp,
        "quality_stage_false_negative_labels": total_fn,
        "quality_stage_precision": precision,
        "quality_stage_recall": recall,
        "known_wholes_with_quality_or_stage_axis": (
            local_positive + local_tied + local_negative
        ),
        "local_true_context_exceeds_rival_forms": local_positive,
        "local_true_context_ties_rival_forms": local_tied,
        "local_rival_context_exceeds_true_forms": local_negative,
        "local_true_axis_position_hits": local_true_hits,
        "local_rival_axis_position_hits": local_rival_hits,
        "reference_exact_occurrences": len(reference_exact),
    }
    return output, summary


def role_outcome(
    outside_exact: int,
    expected_metrics: dict[str, dict[str, object]],
    rival_metrics: dict[str, dict[str, object]],
    local_support: int,
    local_rival: int,
) -> str:
    if outside_exact < 3:
        return "X1_TWO_POSITION_OUTSIDE_CHECK_OPEN"
    reinforced = [
        axis for axis, item in expected_metrics.items()
        if int(item["top"]) >= 2
        and float(item["enrichment"]) >= 1.35
        and int(item["best_rank"]) <= 5
    ]
    strong_rivals = [
        axis for axis, item in rival_metrics.items()
        if int(item["top"]) >= 2
        and float(item["enrichment"]) >= 1.35
        and int(item["best_rank"]) <= 5
    ]
    if len(reinforced) == len(expected_metrics) and outside_exact >= 5 and not strong_rivals:
        return "X3_OUTSIDE_DISTRIBUTION_REINFORCES_ROLE"
    if reinforced and not strong_rivals:
        return "X2_OUTSIDE_DISTRIBUTION_SUPPORTS_PART_OF_ROLE"
    if local_support >= 2 and local_support > local_rival:
        return "X2_IMMEDIATE_OUTSIDE_CONTEXT_REINFORCES_ROLE"
    if (
        strong_rivals and not reinforced and outside_exact >= 5
        and local_rival >= local_support
    ):
        return "X0_OUTSIDE_DISTRIBUTION_FAVORS_RIVAL"
    if reinforced and strong_rivals:
        return "X1_OUTSIDE_DISTRIBUTION_MIXED_BY_DIMENSION"
    return "X1_OUTSIDE_DISTRIBUTION_COMPATIBLE_OR_OPEN"


def calibrated_outside_status(
    surface: str,
    raw_status: str,
    expected_only: int,
    rival_only: int,
    local_share_delta: float,
) -> str:
    """Conservative working tier after the known-whole calibration failure."""
    if surface == "qochey":
        return "K1_QOCHEY_END_RIVAL_LEAD"
    if surface == "okechy":
        return "K1_SPARSE_OUTSIDE_OPEN_WITH_COLD_END_RIVAL"
    if surface == "kchdy":
        return "K1_SPARSE_COLD_DRY_RIVAL"
    polarized = expected_only + rival_only
    if (
        raw_status == "X0_OUTSIDE_DISTRIBUTION_FAVORS_RIVAL"
        and local_share_delta <= -0.15 and polarized >= 5
    ):
        return "K1_OUTSIDE_RIVAL_LEAD_NOT_REJECTION"
    if polarized >= 8 and expected_only >= 5 and local_share_delta >= 0.10:
        return "K2_LOCAL_AXIS_COMPATIBILITY_LEAD"
    if expected_only >= 3 and local_share_delta >= 0.0:
        return "K1_WEAK_LOCAL_COMPATIBILITY"
    return "K1_OPEN_OR_BASELINE_LIKE"


def build_census(
    targets: list[dict[str, object]],
    references: list[dict[str, str]],
    audit: list[dict[str, object]],
    scores: list[dict[str, object]],
    feature_rows: list[dict[str, object]],
    calibration_summary: dict[str, object],
) -> list[dict[str, object]]:
    audit_by_target: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    score_by_target: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in audit:
        audit_by_target[str(row["target_surface"])].append(row)
    for row in scores:
        score_by_target[str(row["target_surface"])].append(row)
    reference_surfaces = {row["known_surface"] for row in references}
    reference_exact = [
        row for row in feature_rows
        if row["surface"] in reference_surfaces and int(row["reader_exact"])
    ]

    output: list[dict[str, object]] = []
    for target in targets:
        surface = str(target["target_surface"])
        occurrences = audit_by_target[surface]
        outside = [row for row in occurrences if not int(row["gdt748_discovery_position"])]
        exact = [row for row in outside if int(row["reader_exact"])]
        candidate_scores = score_by_target[surface]
        top = [row for row in candidate_scores if int(row["top_five_reference"])]
        expected = split_axes(target["prior_role_axes"])
        rivals = rival_axes(expected)
        expected_metrics = {
            axis: axis_metrics(axis, candidate_scores, top) for axis in expected
        }
        rival_metrics = {
            axis: axis_metrics(axis, candidate_scores, top) for axis in rivals
        }
        top_axis_counts = Counter(
            axis for row in top for axis in split_axes(row["reference_axes"])
        )
        top_consensus = {axis for axis, count in top_axis_counts.items() if count >= 3}
        local_axis_counts = Counter(
            axis for row in exact for axis in split_axes(row["immediate_known_axis_union"])
        )
        local_support = sum(
            bool(set(expected) & set(split_axes(row["immediate_known_axis_union"])))
            for row in exact
        )
        local_rival = sum(
            bool(set(rivals) & set(split_axes(row["immediate_known_axis_union"])))
            for row in exact
        )
        raw_status = role_outcome(
            len(exact), expected_metrics, rival_metrics, local_support, local_rival
        )
        expected_only, rival_only, both_local, neither_local = local_polarity_tally(
            exact, set(expected), set(rivals)
        )
        base_expected_only, base_rival_only, base_both, base_neither = (
            local_polarity_tally(reference_exact, set(expected), set(rivals))
        )
        local_denominator = expected_only + rival_only
        base_denominator = base_expected_only + base_rival_only
        local_share = expected_only / local_denominator if local_denominator else 0.0
        base_share = (
            base_expected_only / base_denominator if base_denominator else 0.0
        )
        local_delta = local_share - base_share
        status = calibrated_outside_status(
            surface, raw_status, expected_only, rival_only, local_delta
        )
        supporting = [row for row in candidate_scores if int(row["contains_all_prior_axes"])]
        best_supporting = min(supporting, key=lambda row: int(row["reference_rank"]))
        expected_text = "|".join(
            f"{axis}:top{item['top']}/base{item['expected']:.2f}/"
            f"x{item['enrichment']:.2f}/rank{item['best_rank']}"
            for axis, item in expected_metrics.items()
        )
        rival_text = "|".join(
            f"{axis}:top{item['top']}/base{item['expected']:.2f}/"
            f"x{item['enrichment']:.2f}/rank{item['best_rank']}"
            for axis, item in rival_metrics.items()
        ) or "NONE"
        if surface == "okechy":
            decision = (
                "HOT bleibt explorativer Serienlead, wird außen aber nicht reproduziert; "
                "COLD und END_STAGE kommen als neue Verteilungsrivalen hinzu."
            )
        elif surface == "qochey":
            decision = (
                "Neue Arbeitsbasis: eher End-/Übergangsrolle; trocken/Mittelstufe bleibt "
                "der stärkste Einzelrahmen, ist außerhalb aber nicht reproduziert."
            )
        elif status == "K1_OUTSIDE_RIVAL_LEAD_NOT_REJECTION":
            decision = (
                "Die GDT748-Vorrolle bleibt als Möglichkeit stehen, erhält aber einen "
                "stärkeren Außenrivalen und wird nicht mehr als Standard gesprochen."
            )
        elif status == "K2_LOCAL_AXIS_COMPATIBILITY_LEAD":
            decision = (
                "Die Vorrolle bleibt der beste Arbeitswert und erhält schwache, "
                "grundratenbereinigte Außenkompatibilität; keine Bestätigung als Wort."
            )
        elif target["gdt748_role_decision"] == "REPLACE_RETIRED_LITERAL_WITH_AXIS_ROLE_LEAD":
            decision = (
                "Die alte Stoffidentität bleibt gestrichen; nur die getestete Achsenrolle "
                "darf je nach Außenstatus weitergeführt werden."
            )
        else:
            decision = (
                "Die vorhandene schwache Ganzwortkarte wird nach Außenstatus beibehalten, "
                "verengt oder als gemischt markiert; keine neue Stoffidentität."
            )
        output.append({
            "gdt749_census_id": f"G749-C{len(output) + 1:02d}",
            "target_surface": surface,
            "target_class": target["target_class"],
            "prior_role_axes": target["prior_role_axes"],
            "discovery_occurrences_excluded": sum(int(row["gdt748_discovery_position"]) for row in occurrences),
            "outside_occurrences_all_readings": len(outside),
            "outside_occurrences_reader_exact": len(exact),
            "outside_pages_reader_exact": len({str(row["page"]) for row in exact}),
            "outside_sections": count_string(str(row["section"]) for row in exact),
            "outside_line_positions": count_string(str(row["line_position"]) for row in exact),
            "immediate_known_axis_counts": axis_count_string(local_axis_counts),
            "outside_positions_with_any_prior_axis_immediate": local_support,
            "outside_positions_with_any_same_dimension_rival_immediate": local_rival,
            "outside_prior_only_positions": expected_only,
            "outside_rival_only_positions": rival_only,
            "outside_both_polarities_positions": both_local,
            "outside_neither_polarity_positions": neither_local,
            "reference_prior_only_positions": base_expected_only,
            "reference_rival_only_positions": base_rival_only,
            "reference_both_polarities_positions": base_both,
            "reference_neither_polarity_positions": base_neither,
            "outside_prior_share_excluding_conflicts": f"{local_share:.6f}",
            "reference_prior_share_excluding_conflicts": f"{base_share:.6f}",
            "local_prior_share_delta_over_reference": f"{local_delta:.6f}",
            "top5_reference_surfaces": "|".join(str(row["reference_surface"]) for row in top),
            "top5_reference_axis_counts": axis_count_string(top_axis_counts),
            "top5_reference_consensus_axes": joined(top_consensus),
            "prior_axes_in_top5_consensus": joined(set(expected) & top_consensus),
            "rival_axes_in_top5_consensus": joined(set(rivals) & top_consensus),
            "prior_axis_enrichment_summary": expected_text,
            "rival_axis_enrichment_summary": rival_text,
            "best_all_prior_axes_reference": best_supporting["reference_surface"],
            "best_all_prior_axes_reference_rank": best_supporting["reference_rank"],
            "best_all_prior_axes_similarity": best_supporting["hybrid_distribution_similarity"],
            "raw_distribution_status": raw_status,
            "known_calibration_precision": f"{float(calibration_summary['quality_stage_precision']):.6f}",
            "known_calibration_recall": f"{float(calibration_summary['quality_stage_recall']):.6f}",
            "outside_role_status": status,
            "working_decision_de": decision,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
            "unseen_form_export": 0,
        })
    return output


def qochey_split(
    audit: list[dict[str, object]], scores: list[dict[str, object]]
) -> list[dict[str, object]]:
    outside = [
        row for row in audit
        if row["target_surface"] == "qochey"
        and not int(row["gdt748_discovery_position"])
        and int(row["reader_exact"])
    ]
    candidate_scores = [row for row in scores if row["target_surface"] == "qochey"]
    top = [row for row in candidate_scores if int(row["top_five_reference"])]
    output: list[dict[str, object]] = []
    for hypothesis_id, axes_tuple in QOCHEY_HYPOTHESES:
        axes = set(axes_tuple)
        pool = [
            row for row in candidate_scores
            if axes <= set(split_axes(row["reference_axes"]))
        ]
        top_matches = [
            row for row in top if axes <= set(split_axes(row["reference_axes"]))
        ]
        best = min(pool, key=lambda row: int(row["reference_rank"]))
        direct_all = sum(
            axes <= set(split_axes(row["immediate_known_axis_union"]))
            for row in outside
        )
        direct_any = sum(
            bool(axes & set(split_axes(row["immediate_known_axis_union"])))
            for row in outside
        )
        output.append({
            "gdt749_qochey_hypothesis_id": hypothesis_id,
            "hypothesis_axes": joined(axes),
            "outside_reader_exact_positions": len(outside),
            "reference_pool_with_all_axes": len(pool),
            "top5_references_with_all_axes": len(top_matches),
            "random_deck_expected_top5_slots": f"{5 * len(pool) / len(candidate_scores):.6f}",
            "best_matching_reference": best["reference_surface"],
            "best_matching_reference_axes": best["reference_axes"],
            "best_matching_reference_rank": best["reference_rank"],
            "best_matching_similarity": best["hybrid_distribution_similarity"],
            "mean_matching_similarity": f"{statistics.mean(float(row['hybrid_distribution_similarity']) for row in pool):.6f}",
            "outside_positions_with_all_hypothesis_axes_immediate": direct_all,
            "outside_positions_with_any_hypothesis_axis_immediate": direct_any,
            "interpretation": (
                "POSITIONAL_SUPPORT_ONLY" if direct_all or top_matches
                else "NO_OUTSIDE_SUPPORT_IN_THIS_TEST"
            ),
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def write_reader(
    path: Path,
    census: list[dict[str, object]],
    scores: list[dict[str, object]],
    audit: list[dict[str, object]],
    qochey: list[dict[str, object]],
    calibration_summary: dict[str, object],
) -> None:
    score_map: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    audit_map: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in scores:
        score_map[str(row["target_surface"])].append(row)
    for row in audit:
        if not int(row["gdt748_discovery_position"]) and int(row["reader_exact"]):
            audit_map[str(row["target_surface"])].append(row)
    lines = [
        "# GDT749 Außenstellenleser", "",
        "Die entdeckenden GDT748-Stellen sind vollständig ausgeschlossen. Die Tabelle",
        "spricht Rollen vollständiger Schreibformen, keine EVA-Buchstabenwerte und keine",
        "historischen Wortidentitäten.", "",
        "Der globale Verteilungsklassifikator ist nur ein Rohprofil: im Leave-self-out-",
        f"Test der 46 bekannten Karten erreicht er {calibration_summary['quality_stage_true_positive_labels']} richtige, "
        f"{calibration_summary['quality_stage_false_positive_labels']} falsche und "
        f"{calibration_summary['quality_stage_false_negative_labels']} verpasste Qualitäts-/Stufenachsen "
        f"(Precision {100 * float(calibration_summary['quality_stage_precision']):.1f} %, "
        f"Recall {100 * float(calibration_summary['quality_stage_recall']):.1f} %). "
        "Darum bestätigt kein Top-5-Rang allein eine Rolle.", "",
        "| Ganzform | Außenstellen/Seiten | Vorrolle | Top-5-Kern | direkte Rolle/Rivale | Ergebnis |",
        "|---|---:|---|---|---:|---|",
    ]
    for row in census:
        lines.append(
            f"| `{row['target_surface']}` | {row['outside_occurrences_reader_exact']}/"
            f"{row['outside_pages_reader_exact']} | {row['prior_role_axes']} | "
            f"{row['top5_reference_consensus_axes']} | "
            f"{row['outside_positions_with_any_prior_axis_immediate']}/"
            f"{row['outside_positions_with_any_same_dimension_rival_immediate']} | "
            f"{row['outside_role_status']} |"
        )
    lines.extend(["", "## Einzelkarten", ""])
    for row in census:
        surface = str(row["target_surface"])
        best = sorted(score_map[surface], key=lambda item: int(item["reference_rank"]))[:5]
        samples = audit_map[surface][:3]
        lines.extend([
            f"### `{surface}`", "",
            f"- Außenstatus: `{row['outside_role_status']}`",
            f"- Unkalibriertes Rohprofil: `{row['raw_distribution_status']}`",
            f"- Vorrolle: `{row['prior_role_axes']}`; Top-5-Achsen: "
            f"`{row['top5_reference_axis_counts']}`",
            f"- Direkter Polaritätsvergleich außen/Basis: "
            f"{row['outside_prior_only_positions']}:{row['outside_rival_only_positions']} "
            f"gegen {row['reference_prior_only_positions']}:{row['reference_rival_only_positions']}; "
            f"Anteilsdelta {float(row['local_prior_share_delta_over_reference']):+.3f}",
            f"- Grundratenbereinigte Kurzbilanz: `{row['prior_axis_enrichment_summary']}`",
            f"- Rivalen: `{row['rival_axis_enrichment_summary']}`",
            f"- Entscheidung: {row['working_decision_de']}",
            "- Nächste vollständige Referenzformen: "
            + "; ".join(
                f"`{item['reference_surface']}` ({float(item['hybrid_distribution_similarity']):.3f}; "
                f"{item['reference_axes']})" for item in best
            ),
        ])
        if samples:
            lines.append("- Außenbeispiele:")
            for sample in samples:
                lines.append(
                    f"  - `{sample['locus']}`: `{sample['written_line_eva']}` "
                    f"[direkt {sample['immediate_known_axis_union']}]"
                )
        lines.append("")
    lines.extend(["## `qochey`-Spaltung", ""])
    for row in qochey:
        lines.append(
            f"- `{row['hypothesis_axes']}`: bester Referenzrang "
            f"{row['best_matching_reference_rank']} (`{row['best_matching_reference']}`), "
            f"Top-5-Treffer {row['top5_references_with_all_axes']}, direkte Voll-/Teiltreffer "
            f"{row['outside_positions_with_all_hypothesis_axes_immediate']}/"
            f"{row['outside_positions_with_any_hypothesis_axis_immediate']}."
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def edge_packet(
    output_dir: Path,
    scores: list[dict[str, object]],
    audit: list[dict[str, object]],
    feature_rows: list[dict[str, object]],
) -> dict[str, object]:
    target_map: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    reference_map: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in audit:
        if int(row["outside_discovery_primary"]):
            target_map[str(row["target_surface"])].append(row)
    for row in feature_rows:
        if int(row["reader_exact"]):
            reference_map[str(row["surface"])].append(row)
    selected = None
    ranked = sorted(
        (
            row for row in scores
            if int(row["top_five_reference"])
            and int(row["contains_all_prior_axes"])
        ),
        key=lambda row: (
            -float(row["hybrid_distribution_similarity"]),
            -int(row["outside_occurrences_reader_exact"]),
        ),
    )
    for score in ranked:
        for target_row in target_map[str(score["target_surface"])]:
            matches = [
                row for row in reference_map[str(score["reference_surface"])]
                if row["page"] == target_row["page"]
            ]
            if matches:
                selected = (score, target_row, matches[0])
                break
        if selected:
            break
    if selected is None:
        raise AssertionError("no same-page outside/reference edge is available")
    best, target, reference = selected
    packet = [{
        "edge_id": "G749E001",
        "batch_id": "GDT749_OUTSIDE_FRAME_WHOLE_ROLE",
        "page": target["page"],
        "physical_folio": target["physical_folio"],
        "diagram_unit_id": "CACHED_TEXT_OUTSIDE_DISCOVERY_CONTEXT",
        "pivot_visual_id": f"TARGET_WHOLE_{target['target_surface']}",
        "pivot_locus": f"{target['locus']}@{target['token_ordinal']}",
        "target_visual_id": f"REFERENCE_WHOLE_{reference['surface']}_{reference['page']}",
        "target_locus": f"{reference['locus']}@{reference['token_ordinal']}",
        "relation_type": "OUTSIDE_FRAME_COMPLETE_WHOLE_DISTRIBUTION",
        "direction_basis": "SECTION_POSITION_FLANKS_CLOSURE_AFTER_DISCOVERY_EXCLUSION",
        "ownership_basis": "COMPLETE_WHOLE_NO_COMPONENT_EXPORT",
        "geometry_only_selection": "FALSE",
        "source_manifest_id": "GDT749",
        "page_crop_sha256": "NONE",
        "pivot_crop_sha256": "NONE",
        "target_crop_sha256": "NONE",
        "source_aware_localizer": "GDT749_BUILDER",
        "relation_reviewer": "PENDING_EXTERNAL",
        "relation_confidence": "EXPLORATORY_OUTSIDE_DISTRIBUTION",
        "ambiguity_state": "ROLE_AXIS_ONLY_LITERAL_IDENTITY_OPEN",
        "formal_access_state": "FORMAL_ACCESSED",
        "fold_assignment": "NONE",
        "eligibility_status": "INELIGIBLE_FORMAL_CONTEXT_RELATION",
    }]
    packet_path = output_dir / "GDT749_GDT388_OUTSIDE_EDGE_PACKET.tsv"
    write_tsv(packet_path, packet, list(packet[0]))
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)],
        cwd=ROOT, check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode not in {0, 1} or not completed.stdout:
        raise AssertionError(f"edge intake failed: {completed.stderr}")
    intake = json.loads(completed.stdout)
    if intake["status"] != "INVALID_PACKET" or intake["score_ready"]:
        raise AssertionError("outside-frame packet unexpectedly score-ready")
    (output_dir / "GDT749_GDT388_EDGE_INTAKE.json").write_text(
        json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return intake


def build(output_dir: Path) -> dict[str, object]:
    targets = build_targets()
    references = reference_specs()
    audit, feature_rows, guard = build_occurrence_audit(targets, references)
    scores = score_references(targets, references, audit, feature_rows)
    calibration, calibration_summary = build_known_calibration(
        references, feature_rows
    )
    census = build_census(
        targets, references, audit, scores, feature_rows, calibration_summary
    )
    qochey = qochey_split(audit, scores)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(output_dir / "TARGET_17_FIXED_DECK.tsv", targets, list(targets[0]))
    write_tsv(output_dir / "TARGET_OCCURRENCE_AUDIT.tsv", audit, list(audit[0]))
    write_tsv(output_dir / "REFERENCE_DISTRIBUTION_SCORES.tsv", scores, list(scores[0]))
    write_tsv(
        output_dir / "KNOWN_46_LEAVE_SELF_CALIBRATION.tsv",
        calibration,
        list(calibration[0]),
    )
    write_tsv(output_dir / "TARGET_OUTSIDE_ROLE_CENSUS.tsv", census, list(census[0]))
    write_tsv(output_dir / "QOCHEY_HYPOTHESIS_SPLIT.tsv", qochey, list(qochey[0]))
    write_reader(
        output_dir / "GDT749_OUTSIDE_FRAME_READER.md",
        census,
        scores,
        audit,
        qochey,
        calibration_summary,
    )
    intake = edge_packet(output_dir, scores, audit, feature_rows)

    status_counts = Counter(str(row["outside_role_status"]) for row in census)
    result = {
        "schema": "GDT749_RESULT_V1",
        "status": (
            "PARTIAL__16_RECURRENT_PLUS_QOCHEY__"
            f"{sum(int(row['outside_occurrences_reader_exact']) for row in census)}_"
            "READER_EXACT_OUTSIDE_OCCURRENCES__"
            f"CALIBRATION_{calibration_summary['quality_stage_true_positive_labels']}_TP_"
            f"{calibration_summary['quality_stage_false_positive_labels']}_FP_"
            f"{calibration_summary['quality_stage_false_negative_labels']}_FN__"
            f"{status_counts['K2_LOCAL_AXIS_COMPATIBILITY_LEAD']}_LOCAL_COMPATIBILITY__"
            f"{status_counts['K1_OUTSIDE_RIVAL_LEAD_NOT_REJECTION']}_RIVAL_LEADS__"
            "QOCHEY_THREE_OUTSIDE_POSITIONS__ZERO_LITERAL_IDENTITIES__"
            "ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
        ),
        "question": (
            "Do GDT748's sixteen recurrent complete-whole roles, and qochey's "
            "split rivals, recur outside the serial frames that discovered them?"
        ),
        "scope": {
            "recurrent_targets": 16,
            "qochey_split_diagnostic": 1,
            "fixed_reference_wholes": len(references),
            "target_occurrences_all": len(audit),
            "discovery_occurrences_excluded": sum(int(row["gdt748_discovery_position"]) for row in audit),
            "outside_occurrences_all_readings": sum(not int(row["gdt748_discovery_position"]) for row in audit),
            "outside_occurrences_reader_exact": sum(int(row["outside_discovery_primary"]) for row in audit),
            "outside_pages": len({row["page"] for row in audit if int(row["outside_discovery_primary"])}),
            "reference_comparisons": len(scores),
        },
        "outside_role_status_counts": dict(sorted(status_counts.items())),
        "known_whole_leave_self_calibration": calibration_summary,
        "target_summary": {
            str(row["target_surface"]): {
                "prior_axes": row["prior_role_axes"],
                "outside_exact": int(row["outside_occurrences_reader_exact"]),
                "top5_consensus": row["top5_reference_consensus_axes"],
                "status": row["outside_role_status"],
            }
            for row in census
        },
        "qochey_hypotheses": [
            {
                "axes": row["hypothesis_axes"],
                "best_rank": int(row["best_matching_reference_rank"]),
                "top5_matches": int(row["top5_references_with_all_axes"]),
                "direct_all": int(row["outside_positions_with_all_hypothesis_axes_immediate"]),
                "direct_any": int(row["outside_positions_with_any_hypothesis_axis_immediate"]),
            }
            for row in qochey
        ],
        "guard": guard,
        "edge_intake": {
            "status": intake["status"],
            "score_ready": intake["score_ready"],
            "errors": intake["errors"],
        },
        "claim_ceiling": (
            "Complete-whole role axes only. No EVA component, substring, language, "
            "sound, lexeme, literal ingredient, plant, disease, cure, person, vessel, "
            "unit, plaintext, unseen form, image, transcription, new page, f84 or f84r."
        ),
        "inputs": {
            str(G746_CALIBRATION_REL): sha256(ROOT / G746_CALIBRATION_REL),
            str(G748_SURFACE_REL): sha256(ROOT / G748_SURFACE_REL),
            str(G748_EVIDENCE_REL): sha256(ROOT / G748_EVIDENCE_REL),
        },
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
