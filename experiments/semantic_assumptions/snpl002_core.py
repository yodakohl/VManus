#!/usr/bin/env python3
"""Frozen local source-STA query scorer shared by SNPL002 preflight/target."""

from __future__ import annotations

import csv
import hashlib
import itertools
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


READINGS = ("ZL3b", "IT2a", "RF1b")
COLUMNS = {"ZL3b": "zl_sta_codes", "IT2a": "it_sta_codes", "RF1b": "rf_sta_codes"}
LABEL_LOCI = ("f89v2.6", "f102r2.21", "f102r2.22", "f102v1.17")
TARGET_PAGES = ("f48v", "f18v", "f23r", "f19r")
STRATA = (("B", "5"), ("A", "1"), ("A", "1"), ("A", "1"))
EXPLICIT_INDICES = (1, 2, 3)


@dataclass(frozen=True)
class Panel:
    labels: dict[str, dict[str, tuple[str, ...]]]
    background: dict[tuple[str, str], dict[str, dict[str, tuple[tuple[str, ...], ...]]]]
    member_inventory: dict[str, tuple[str, ...]]
    source_sha256: str


def load_panel(path: Path) -> Panel:
    data = path.read_bytes()
    labels: dict[str, dict[str, tuple[str, ...]]] = {}
    mutable = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    members = defaultdict(set)
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in LABEL_LOCI:
                if row["locus"] in labels:
                    raise ValueError(("duplicate label", row["locus"]))
                if not (
                    row["kind"] == "L" and row["code"] == "@Lf"
                    and row["strict_zero_alternative"] == "1"
                    and row["consensus_group_count"] == "1"
                ):
                    raise ValueError(("label metadata", row["locus"]))
                labels[row["locus"]] = {
                    reading: tuple(row[column].split()) for reading, column in COLUMNS.items()
                }
                continue
            if row["page"] in TARGET_PAGES:
                continue
            if not (
                row["section"] == "H" and row["grammar_scope"] == "CONFIRMED_PROSE"
                and row["strict_zero_alternative"] == "1"
            ):
                continue
            key = (row["currier"], row["hand"])
            for reading, column in COLUMNS.items():
                sequence = tuple(row[column].split())
                mutable[key][reading][row["page"]].append(sequence)
                for code in sequence:
                    members[code[0]].add(code)
    if set(labels) != set(LABEL_LOCI):
        raise ValueError((set(labels), set(LABEL_LOCI)))
    background = {
        key: {
            reading: {page: tuple(groups) for page, groups in pages.items()}
            for reading, pages in by_reading.items()
        }
        for key, by_reading in mutable.items()
    }
    if (len(background[("A", "1")]["ZL3b"]), len(background[("B", "5")]["ZL3b"])) != (92, 5):
        raise ValueError("background size")
    return Panel(
        labels=labels,
        background=background,
        member_inventory={key: tuple(sorted(value)) for key, value in members.items()},
        source_sha256=hashlib.sha256(data).hexdigest(),
    )


def query_motifs(sequence: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    values = {
        sequence[start:start + width]
        for width in (4, 5)
        for start in range(max(0, len(sequence) - width + 1))
    }
    return tuple(sorted(values, key=lambda value: (len(value), value)))


def contains(group: tuple[str, ...], motif: tuple[str, ...]) -> bool:
    width = len(motif)
    return any(group[index:index + width] == motif for index in range(len(group) - width + 1))


def page_raw(groups: tuple[tuple[str, ...], ...], motifs, weights) -> float:
    denominator = sum(weights)
    if not denominator > 0:
        raise ValueError("zero query weight")
    return max(
        (sum(weight for motif, weight in zip(motifs, weights) if contains(group, motif)) / denominator
         for group in groups),
        default=0.0,
    )


def calibrated_score(
    query: tuple[str, ...],
    candidate_groups: tuple[tuple[str, ...], ...],
    reference_pages: dict[str, tuple[tuple[str, ...], ...]],
) -> dict:
    motifs = query_motifs(query)
    count = len(reference_pages)
    if count < 4:
        raise ValueError(("reference capacity", count))
    frequencies = [
        sum(any(contains(group, motif) for group in groups) for groups in reference_pages.values())
        for motif in motifs
    ]
    weights = [math.log((count + 1) / (frequency + 1)) for frequency in frequencies]
    raw = page_raw(candidate_groups, motifs, weights)
    references = [page_raw(groups, motifs, weights) for groups in reference_pages.values()]
    less = sum(value < raw for value in references)
    equal = sum(value == raw for value in references)
    midrank = (less + 0.5 * equal + 0.5) / (count + 1)
    if not (math.isfinite(raw) and math.isfinite(midrank) and 0 <= midrank <= 1):
        raise ValueError((raw, midrank))
    return {
        "raw": raw,
        "midrank": midrank,
        "reference_pages": count,
        "motif_df": frequencies,
        "motif_weights": weights,
    }


def alternative_code(code: str, inventory: dict[str, tuple[str, ...]]) -> str:
    alternatives = [value for value in inventory.get(code[0], ()) if value != code]
    return alternatives[0] if alternatives else code


def edge_mutation(sequence: tuple[str, ...], inventory: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    values = list(sequence)
    for index in list(range(len(values))) + list(range(len(values) - 1, -1, -1)):
        replacement = alternative_code(values[index], inventory)
        if replacement != values[index]:
            values[index] = replacement
            return tuple(values)
    raise ValueError(("no member alternative", sequence))


def family_only(sequence: tuple[str, ...], inventory: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    return tuple(alternative_code(code, inventory) for code in sequence)


def assignment_summary(matrix: list[list[float]]) -> dict:
    permutations = list(itertools.permutations(range(4)))
    scores = [sum(matrix[label][page] for label, page in enumerate(permutation)) for permutation in permutations]
    diagonal = scores[permutations.index((0, 1, 2, 3))]
    tolerance = 1e-15
    exceed = sum(score >= diagonal - tolerance for score in scores)
    wrong = [score for permutation, score in zip(permutations, scores) if permutation != (0, 1, 2, 3)]
    return {
        "diagonal": diagonal,
        "best_wrong": max(wrong),
        "margin": diagonal - max(wrong),
        "exceed_or_tie": exceed,
        "p": exceed / 24,
        "unique_top": exceed == 1,
        "scores_sha256": hashlib.sha256(
            b"".join(float(value).hex().encode("ascii") + b"\n" for value in scores)
        ).hexdigest(),
    }


def score_world(
    panel: Panel,
    selected_pages: tuple[str, str, str, str],
    inserts: dict[str, dict[int, tuple[str, ...]]],
) -> dict:
    if len(set(selected_pages[1:])) != 3:
        raise ValueError("A1 candidates not distinct")
    if selected_pages[0] not in panel.background[("B", "5")]["ZL3b"]:
        raise ValueError("B5 candidate")
    for page in selected_pages[1:]:
        if page not in panel.background[("A", "1")]["ZL3b"]:
            raise ValueError(("A1 candidate", page))

    reading_matrices = {}
    diagnostics = {}
    for reading in READINGS:
        matrix = [[0.0] * 4 for _ in range(4)]
        detail = {}
        for page_index, (page, stratum) in enumerate(zip(selected_pages, STRATA)):
            candidate = panel.background[stratum][reading][page]
            if page_index in inserts.get(reading, {}):
                candidate = candidate + (inserts[reading][page_index],)
            excluded = {candidate_page for candidate_page, candidate_stratum in zip(selected_pages, STRATA) if candidate_stratum == stratum}
            references = {
                key: groups for key, groups in panel.background[stratum][reading].items() if key not in excluded
            }
            for label_index, locus in enumerate(LABEL_LOCI):
                scored = calibrated_score(panel.labels[locus][reading], candidate, references)
                matrix[label_index][page_index] = scored["midrank"]
                detail[f"{label_index}:{page_index}"] = scored
        reading_matrices[reading] = matrix
        diagnostics[reading] = detail

    pooled = [
        [sum(reading_matrices[reading][i][j] for reading in READINGS) / 3 for j in range(4)]
        for i in range(4)
    ]
    assignments = {reading: assignment_summary(reading_matrices[reading]) for reading in READINGS}
    assignments["POOLED"] = assignment_summary(pooled)
    explicit_best = []
    for index in EXPLICIT_INDICES:
        true_value = pooled[index][index]
        competitors = [pooled[label][index] for label in range(4) if label != index]
        explicit_best.append(true_value > max(competitors) + 1e-15)
    gates = {
        "pooled_unique_top": assignments["POOLED"]["unique_top"],
        "every_reading_unique_top": all(assignments[reading]["unique_top"] for reading in READINGS),
        "three_explicit_true_labels_unique_page_best": all(explicit_best),
        "three_explicit_true_midranks_at_least_075": all(pooled[index][index] >= 0.75 for index in EXPLICIT_INDICES),
        "ambiguous_f89_true_midrank_at_least_050": pooled[0][0] >= 0.50,
    }
    return {
        "selected_pages": list(selected_pages),
        "matrix": {**reading_matrices, "POOLED": pooled},
        "matrix_sha256": hashlib.sha256(
            b"".join(float(value).hex().encode("ascii") + b"\n" for row in pooled for value in row)
        ).hexdigest(),
        "assignments": assignments,
        "gates": gates,
        "passes": all(gates.values()),
        "diagnostics": diagnostics,
    }
