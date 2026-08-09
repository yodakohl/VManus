#!/usr/bin/env python3
"""Target-blind core for cho/che local-scope calibration and scoring."""

from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np


MASK64 = (1 << 64) - 1
READINGS = ("ZL3b", "IT2a", "RF1b")
MASKED_FIELDS = (
    "event_id", "edition", "source_group_id", "physical_event_key", "locus",
    "source_group_index", "source_group_count", "collapsed_page", "panel_page",
    "physical_folio", "section", "currier", "paragraph_id", "paragraph_number",
    "line_index_side", "line_count_side", "line_fraction", "line_quartile",
    "group_index_line", "group_count_line", "group_fraction", "masked_template",
    "primary_query", "common_primary_query",
)
FORBIDDEN_FIELDS = {
    "outcome", "target_value", "raw_surface", "surface", "page_state", "score",
    "effect", "p_value", "english_gloss",
}


def stable_u64(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "little")


def splitmix64(values: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore"):
        z = values.astype(np.uint64, copy=True) + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        return z ^ (z >> np.uint64(31))


@dataclass
class EditionPanel:
    edition: str
    rows: list[dict]
    event_ids: tuple[str, ...]
    physical_keys: tuple[str, ...]
    folios: tuple[str, ...]
    rotation_strata: tuple[tuple[np.ndarray, str, str], ...]
    query_same: tuple[np.ndarray, ...]
    query_other: tuple[np.ndarray, ...]
    query_paragraph_groups: tuple[np.ndarray, ...]
    paragraph_page_groups: tuple[np.ndarray, ...]
    page_folio_groups: tuple[np.ndarray, ...]
    query_folios: tuple[str, ...]
    pair_left: np.ndarray
    pair_right: np.ndarray
    pair_same: np.ndarray
    pair_stratum_groups: tuple[np.ndarray, ...]
    pair_stratum_pages: tuple[str, ...]
    pair_page_groups: tuple[np.ndarray, ...]
    pair_page_folio_groups: tuple[np.ndarray, ...]
    pair_folios: tuple[str, ...]


def _groups(values: list[str]) -> tuple[tuple[np.ndarray, ...], tuple[str, ...]]:
    mapping: dict[str, list[int]] = defaultdict(list)
    for index, value in enumerate(values):
        mapping[value].append(index)
    keys = tuple(sorted(mapping))
    return tuple(np.asarray(mapping[key], dtype=np.int64) for key in keys), keys


def load_panels(path: Path) -> dict[str, EditionPanel]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != MASKED_FIELDS:
            raise ValueError("masked event schema drift")
        if FORBIDDEN_FIELDS.intersection(reader.fieldnames or ()):
            raise ValueError("forbidden target field in masked event schema")
        all_rows = list(reader)
    if len(all_rows) != 30160:
        raise ValueError("masked event total drift")
    panels = {}
    for edition in READINGS:
        rows = [row for row in all_rows if row["edition"] == edition]
        rows.sort(key=lambda row: row["event_id"])
        index = {row["event_id"]: i for i, row in enumerate(rows)}
        if len(index) != len(rows):
            raise ValueError(f"duplicate event ID in {edition}")

        strata: dict[tuple[str, str, int], list[int]] = defaultdict(list)
        for i, row in enumerate(rows):
            strata[(row["collapsed_page"], row["masked_template"], int(row["line_quartile"]))].append(i)
        rotation_strata = []
        for key in sorted(strata):
            positions = sorted(strata[key], key=lambda i: (
                int(rows[i]["line_index_side"]), int(rows[i]["group_index_line"]), rows[i]["event_id"],
            ))
            rotation_strata.append((np.asarray(positions, dtype=np.int64), key[0], "|".join(map(str, key))))

        query_indices = [i for i, row in enumerate(rows) if row["primary_query"] == "1"]
        query_same = []
        query_other = []
        query_paragraphs = []
        query_pages = []
        query_folio_values = []
        for query_index in query_indices:
            query = rows[query_index]
            candidates = strata[(query["collapsed_page"], query["masked_template"], int(query["line_quartile"]))]
            same = [i for i in candidates if i != query_index and rows[i]["paragraph_id"] == query["paragraph_id"]]
            other = [i for i in candidates if rows[i]["paragraph_id"] != query["paragraph_id"]]
            if not same or not other:
                raise ValueError(f"frozen primary query lost support: {query['event_id']}")
            query_same.append(np.asarray(same, dtype=np.int64))
            query_other.append(np.asarray(other, dtype=np.int64))
            query_paragraphs.append(query["paragraph_id"])
            query_pages.append(query["collapsed_page"])
            query_folio_values.append(query["physical_folio"])

        paragraph_groups, paragraph_keys = _groups(query_paragraphs)
        paragraph_pages = [next(query_pages[i] for i in group) for group in paragraph_groups]
        page_groups, page_keys = _groups(paragraph_pages)
        page_folios = [next(rows[i]["physical_folio"] for i, row in enumerate(rows) if row["collapsed_page"] == page) for page in page_keys]
        page_folio_groups, query_folios = _groups(page_folios)

        raw_pairs: list[tuple[int, int, bool, tuple[str, str, int, int], str]] = []
        by_page_template: dict[tuple[str, str], list[int]] = defaultdict(list)
        for i, row in enumerate(rows):
            by_page_template[(row["collapsed_page"], row["masked_template"])].append(i)
        candidate_counts: dict[tuple[str, str, int, int], list[int]] = defaultdict(lambda: [0, 0])
        candidate_pairs = []
        for (page, template), positions in sorted(by_page_template.items()):
            for a_offset, left in enumerate(positions):
                for right in positions[a_offset + 1:]:
                    distance = abs(int(rows[left]["line_index_side"]) - int(rows[right]["line_index_side"]))
                    if not 1 <= distance <= 12:
                        continue
                    midpoint_half = 0
                    key = (page, template, distance, midpoint_half)
                    same = rows[left]["paragraph_id"] == rows[right]["paragraph_id"]
                    candidate_counts[key][0 if same else 1] += 1
                    candidate_pairs.append((left, right, same, key, rows[left]["physical_folio"]))
        eligible_pair_keys = {key for key, counts in candidate_counts.items() if counts[0] and counts[1]}
        raw_pairs = [pair for pair in candidate_pairs if pair[3] in eligible_pair_keys]
        raw_pairs.sort(key=lambda pair: (pair[3], pair[0], pair[1]))
        pair_left = np.asarray([pair[0] for pair in raw_pairs], dtype=np.int64)
        pair_right = np.asarray([pair[1] for pair in raw_pairs], dtype=np.int64)
        pair_same = np.asarray([pair[2] for pair in raw_pairs], dtype=bool)
        pair_key_values = ["|".join(map(str, pair[3])) for pair in raw_pairs]
        pair_stratum_groups, pair_stratum_keys = _groups(pair_key_values)
        pair_stratum_pages = tuple(key.split("|", 1)[0] for key in pair_stratum_keys)
        pair_page_groups, pair_page_keys = _groups(list(pair_stratum_pages))
        pair_page_folios = [next(pair[4] for pair in raw_pairs if pair[3][0] == page) for page in pair_page_keys]
        pair_page_folio_groups, pair_folios = _groups(pair_page_folios)

        panels[edition] = EditionPanel(
            edition=edition, rows=rows,
            event_ids=tuple(row["event_id"] for row in rows),
            physical_keys=tuple(row["physical_event_key"] for row in rows),
            folios=tuple(row["physical_folio"] for row in rows),
            rotation_strata=tuple(rotation_strata),
            query_same=tuple(query_same), query_other=tuple(query_other),
            query_paragraph_groups=paragraph_groups,
            paragraph_page_groups=page_groups, page_folio_groups=page_folio_groups,
            query_folios=query_folios,
            pair_left=pair_left, pair_right=pair_right, pair_same=pair_same,
            pair_stratum_groups=pair_stratum_groups,
            pair_stratum_pages=pair_stratum_pages,
            pair_page_groups=pair_page_groups,
            pair_page_folio_groups=pair_page_folio_groups,
            pair_folios=pair_folios,
        )
    return panels


def _mean_groups(values: np.ndarray, groups: tuple[np.ndarray, ...]) -> np.ndarray:
    return np.stack([values[:, group].mean(axis=1) for group in groups], axis=1)


def score_batch(panel: EditionPanel, labels: np.ndarray) -> dict[str, np.ndarray]:
    """Score a rows-by-events label matrix; returns rowwise and folio effects."""
    y = labels.astype(np.float64, copy=False)
    query_values = np.empty((len(y), len(panel.query_same)), dtype=np.float64)
    query_indices = [i for i, row in enumerate(panel.rows) if row["primary_query"] == "1"]
    for column, (query_index, same, other) in enumerate(zip(query_indices, panel.query_same, panel.query_other)):
        p_same = (y[:, same].sum(axis=1) + 0.5) / (len(same) + 1.0)
        p_other = (y[:, other].sum(axis=1) + 0.5) / (len(other) + 1.0)
        target = y[:, query_index]
        query_values[:, column] = target * np.log(p_same / p_other) + (1.0 - target) * np.log((1.0 - p_same) / (1.0 - p_other))
    paragraph = _mean_groups(query_values, panel.query_paragraph_groups)
    page = _mean_groups(paragraph, panel.paragraph_page_groups)
    local_folio = _mean_groups(page, panel.page_folio_groups)

    pair_match = (labels[:, panel.pair_left] == labels[:, panel.pair_right]).astype(np.float64)
    stratum_values = np.empty((len(y), len(panel.pair_stratum_groups)), dtype=np.float64)
    for column, group in enumerate(panel.pair_stratum_groups):
        same = group[panel.pair_same[group]]
        different = group[~panel.pair_same[group]]
        stratum_values[:, column] = pair_match[:, same].mean(axis=1) - pair_match[:, different].mean(axis=1)
    pair_page = _mean_groups(stratum_values, panel.pair_page_groups)
    boundary_folio = _mean_groups(pair_page, panel.pair_page_folio_groups)

    return {
        "local_T": local_folio.mean(axis=1),
        "local_folio": local_folio,
        "boundary_T": boundary_folio.mean(axis=1),
        "boundary_folio": boundary_folio,
    }


def rotated_batch(panel: EditionPanel, base_labels: np.ndarray, assignments: np.ndarray, ensemble: str, seed: str) -> np.ndarray:
    if ensemble not in {"INDEPENDENT_STRATUM", "COUPLED_PAGE"}:
        raise ValueError(f"unknown rotation ensemble: {ensemble}")
    assignments = assignments.astype(np.uint64, copy=False)
    output = np.empty((len(assignments), len(base_labels)), dtype=np.uint8)
    seed_value = np.uint64(stable_u64(seed))
    assignment_mix = splitmix64(assignments ^ seed_value)
    for positions, page, stratum_key in panel.rotation_strata:
        key = page if ensemble == "COUPLED_PAGE" else stratum_key
        phase = splitmix64(assignment_mix ^ np.uint64(stable_u64(key)))
        shifts = phase % np.uint64(len(positions))
        source = (np.arange(len(positions), dtype=np.uint64)[None, :] - shifts[:, None]) % np.uint64(len(positions))
        output[:, positions] = base_labels[positions[source.astype(np.int64)]]
    return output


def permutation_summary(panel: EditionPanel, labels: np.ndarray, assignments: int, seed: str, chunk: int = 256) -> dict:
    observed = score_batch(panel, labels[None, :])
    null = {ensemble: {"local": [], "boundary": []} for ensemble in ("INDEPENDENT_STRATUM", "COUPLED_PAGE")}
    for ensemble in null:
        for start in range(1, assignments + 1, chunk):
            ids = np.arange(start, min(assignments + 1, start + chunk), dtype=np.uint64)
            rotated = rotated_batch(panel, labels, ids, ensemble, seed)
            scored = score_batch(panel, rotated)
            null[ensemble]["local"].append(scored["local_T"])
            null[ensemble]["boundary"].append(scored["boundary_T"])
        null[ensemble]["local"] = np.concatenate(null[ensemble]["local"])
        null[ensemble]["boundary"] = np.concatenate(null[ensemble]["boundary"])

    def scalar_record(name: str, folio: np.ndarray) -> dict:
        value = float(observed[f"{name}_T"][0])
        effects = observed[f"{name}_folio"][0]
        total_abs = float(np.abs(effects).sum())
        deletion = (effects.sum() - effects) / max(1, len(effects) - 1)
        return {
            "effect": value,
            "positive_folios": int((effects > 0).sum()),
            "folios": len(effects),
            "max_abs_contribution_fraction": float(np.abs(effects).max() / total_abs) if total_abs else 1.0,
            "minimum_leave_one_folio_out": float(deletion.min()),
            "p_by_ensemble": {
                ensemble: float((1 + np.count_nonzero(null[ensemble][name] >= value)) / (assignments + 1))
                for ensemble in null
            },
        }

    return {
        "edition": panel.edition,
        "assignments_per_ensemble": assignments,
        "local": scalar_record("local", observed["local_folio"]),
        "boundary": scalar_record("boundary", observed["boundary_folio"]),
    }


def synthetic_labels(panel: EditionPanel, world: int, mode: str, amplitude: float = 1.0, planted_folio: str | None = None) -> np.ndarray:
    """Generate deterministic target-blind binary fixtures on frozen geometry."""
    logits = np.empty(len(panel.rows), dtype=np.float64)
    uniforms = np.empty(len(panel.rows), dtype=np.float64)
    paragraph_sign = {}
    for i, row in enumerate(panel.rows):
        page_hash = stable_u64(f"WORLD|{world}|PAGE|{row['collapsed_page']}")
        template_hash = stable_u64(f"WORLD|{world}|TEMPLATE|{row['masked_template']}")
        base = -1.6 if page_hash & 1 else 0.8
        base += ((template_hash % 2001) / 2000.0 - 0.5) * 0.8
        base += (float(row["line_fraction"]) - 0.5) * 0.6
        if mode in {"PARAGRAPH", "ONE_FOLIO"} and (mode != "ONE_FOLIO" or row["physical_folio"] == planted_folio):
            key = (row["collapsed_page"], row["masked_template"], row["paragraph_id"])
            if key not in paragraph_sign:
                paragraph_sign[key] = 1.0 if stable_u64(f"WORLD|{world}|PARAGRAPH|{'|'.join(key)}") & 1 else -1.0
            base += amplitude * paragraph_sign[key]
        logits[i] = base
        uniforms[i] = (stable_u64(f"WORLD|{world}|EVENT|{row['physical_event_key']}") + 0.5) / (1 << 64)
    labels = (uniforms < 1.0 / (1.0 + np.exp(-logits))).astype(np.uint8)
    if mode == "SEQUENTIAL":
        for positions, page, stratum_key in panel.rotation_strata:
            previous = labels[positions[0]]
            for position in positions[1:]:
                copy_u = (stable_u64(f"WORLD|{world}|COPY|{panel.rows[position]['physical_event_key']}") + 0.5) / (1 << 64)
                if copy_u < amplitude:
                    labels[position] = previous
                previous = labels[position]
    if mode not in {"NULL", "PARAGRAPH", "ONE_FOLIO", "SEQUENTIAL"}:
        raise ValueError(f"unknown synthetic mode: {mode}")
    return labels


def panel_capacity(panel: EditionPanel) -> dict:
    return {
        "events": len(panel.rows),
        "queries": len(panel.query_same),
        "local_folios": len(panel.query_folios),
        "boundary_pairs": len(panel.pair_left),
        "boundary_strata": len(panel.pair_stratum_groups),
        "boundary_folios": len(panel.pair_folios),
    }
