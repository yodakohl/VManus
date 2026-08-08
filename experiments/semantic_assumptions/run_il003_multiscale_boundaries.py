#!/usr/bin/env python3
"""IL003: locate root coherence across manual manuscript boundaries."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
from scipy.spatial import cKDTree


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
sys.path.insert(0, str(HERE))

from run_il001_information_location import (  # noqa: E402
    Line,
    Root,
    SOURCES,
    bootstrap_ci,
    load_lines,
    page_groups,
    select_split,
    sha256_path,
    sign_flip_p,
    stable_int,
)
from run_il002_matched_line_pairs import (  # noqa: E402
    holm_adjust,
    preliminary_weights,
    weighted_jaccard,
)


PREREG = HERE / "hypotheses" / "IL003_MULTISCALE_BOUNDARY_PREREGISTRATION.md"
DEPENDENCIES = (
    HERE / "run_il001_information_location.py",
    HERE / "run_il002_matched_line_pairs.py",
)
METADATA = BASE / "transcription" / "voynich_zl3b_lines.tsv"
RESULTS = HERE / "results"
FROZEN = RESULTS / "il003_multiscale_validation_frozen.json"
DISCOVERY = RESULTS / "il003_multiscale_discovery_frozen.json"
OUTPUT_JSON = RESULTS / "il003_multiscale_confirmation_results.json"
OUTPUT_REPORT = RESULTS / "il003_multiscale_confirmation_report.md"
SCALES = ("P_PAGE", "L_LEAF", "O_OPENING", "Q_QUIRE")
SIMPLE_FOLIO = re.compile(r"^f(\d+)([rv])$", re.I)
SEED = 3_300_003


@dataclass(frozen=True)
class ManualMetadata:
    quire_by_page: dict[str, str]
    paragraph_start_by_locus: dict[str, bool]
    page_order: dict[str, int]


@dataclass(frozen=True)
class Unit:
    uid: str
    kind: str
    page: str
    quire: str
    stratum: tuple[str, str, str]
    roots: frozenset[Root]
    forms: frozenset[tuple[Any, ...]]
    token_count: int
    paragraph: int | None
    folio: int | None
    side: str

    @property
    def key(self) -> tuple[str, str]:
        return self.page, self.uid


@dataclass(frozen=True)
class Pair:
    left: Unit
    right: Unit
    root_similarity: float
    form_similarity: float
    total_tokens: int
    token_imbalance: int

    @property
    def key(self) -> tuple[str, str, str, str]:
        first, second = sorted((self.left.key, self.right.key))
        return first[0], first[1], second[0], second[1]


@dataclass(frozen=True)
class TargetPair:
    pair: Pair
    group: str
    match_key: tuple[Any, ...]


@dataclass(frozen=True)
class Match:
    target: TargetPair
    control: Pair


def read_metadata() -> ManualMetadata:
    with METADATA.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    quire_by_page: dict[str, str] = {}
    paragraph_start: dict[str, bool] = {}
    page_order: dict[str, int] = {}
    for row in rows:
        page = row["page"].lower()
        quire = row["quire"]
        if page in quire_by_page and quire_by_page[page] != quire:
            raise RuntimeError(f"inconsistent quire on {page}")
        quire_by_page[page] = quire
        paragraph_start[row["locus"]] = bool(int(row["paragraph_start"]))
        page_order[page] = int(row["page_order"])
    return ManualMetadata(quire_by_page, paragraph_start, page_order)


def root_partition(root: Root) -> str:
    value = hashlib.sha256(("IL003-ROOT|" + repr(root)).encode("utf-8")).digest()[0]
    return "C" if value & 1 else "D"


def weight_maps() -> tuple[dict[Root, float], dict[Root, float], dict[tuple[Any, ...], float]]:
    zl_lines = load_lines(SOURCES["ZL3b"])
    roots, forms = preliminary_weights(select_split(zl_lines, "train"))
    discovery = {root: weight for root, weight in roots.items() if root_partition(root) == "D"}
    confirmation = {root: weight for root, weight in roots.items() if root_partition(root) == "C"}
    if not discovery or not confirmation:
        raise RuntimeError("empty root partition")
    return discovery, confirmation, forms


def map_signature(
    discovery: dict[Root, float], confirmation: dict[Root, float],
    forms: dict[tuple[Any, ...], float],
) -> str:
    rows = [
        *(f"D\t{root!r}\t{weight:.17g}" for root, weight in sorted(discovery.items())),
        *(f"C\t{root!r}\t{weight:.17g}" for root, weight in sorted(confirmation.items())),
        *(f"F\t{form!r}\t{weight:.17g}" for form, weight in sorted(forms.items(), key=lambda row: repr(row[0]))),
    ]
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def simple_folio(page: str) -> tuple[int | None, str]:
    match = SIMPLE_FOLIO.fullmatch(page)
    return (int(match.group(1)), match.group(2).lower()) if match else (None, "")


def build_units(
    lines: Sequence[Line], roots: dict[Root, float], metadata: ManualMetadata,
) -> tuple[list[Unit], list[Unit]]:
    paragraph_units: list[Unit] = []
    page_units: list[Unit] = []
    for page, selected in page_groups(lines):
        quire = metadata.quire_by_page.get(page, "")
        folio, side = simple_folio(page)
        paragraph_index = -1
        paragraph_data: dict[tuple[int, tuple[str, str, str]], dict[str, Any]] = {}
        page_data: dict[tuple[str, str, str], dict[str, Any]] = {}
        for line_index, line in enumerate(selected):
            starts = metadata.paragraph_start_by_locus.get(
                line.locus, line.paragraph_start
            )
            if line_index == 0 or starts:
                paragraph_index += 1
            stratum = line.stratum
            p_data = paragraph_data.setdefault(
                (paragraph_index, stratum),
                {"roots": set(), "forms": set(), "tokens": 0},
            )
            g_data = page_data.setdefault(
                stratum, {"roots": set(), "forms": set(), "tokens": 0}
            )
            for token in line.tokens:
                if token.root in roots:
                    p_data["roots"].add(token.root)
                    g_data["roots"].add(token.root)
                p_data["forms"].add(token.shell)
                g_data["forms"].add(token.shell)
                p_data["tokens"] += 1
                g_data["tokens"] += 1
        for (paragraph, stratum), data in paragraph_data.items():
            if len(data["roots"]) < 2:
                continue
            paragraph_units.append(Unit(
                uid=f"{page}:p{paragraph}:{stratum!r}", kind="PARAGRAPH",
                page=page, quire=quire, stratum=stratum,
                roots=frozenset(data["roots"]), forms=frozenset(data["forms"]),
                token_count=data["tokens"], paragraph=paragraph,
                folio=folio, side=side,
            ))
        for stratum, data in page_data.items():
            if len(data["roots"]) < 2:
                continue
            page_units.append(Unit(
                uid=f"{page}:{stratum!r}", kind="PAGE",
                page=page, quire=quire, stratum=stratum,
                roots=frozenset(data["roots"]), forms=frozenset(data["forms"]),
                token_count=data["tokens"], paragraph=None,
                folio=folio, side=side,
            ))
    paragraph_units.sort(key=lambda unit: unit.key)
    page_units.sort(key=lambda unit: unit.key)
    return paragraph_units, page_units


def make_pair(
    left: Unit, right: Unit, root_weights: dict[Root, float],
    form_weights: dict[tuple[Any, ...], float],
) -> Pair:
    if right.key < left.key:
        left, right = right, left
    return Pair(
        left, right,
        weighted_jaccard(left.roots, right.roots, root_weights),
        weighted_jaccard(left.forms, right.forms, form_weights),
        left.token_count + right.token_count,
        abs(left.token_count - right.token_count),
    )


def pair_vector(pair: Pair) -> np.ndarray:
    return np.asarray([
        pair.form_similarity,
        math.log1p(pair.total_tokens),
        math.log1p(pair.token_imbalance),
    ], dtype=np.float64)


def nonlocal_pair(left: Unit, right: Unit) -> bool:
    return bool(
        left.folio is not None and right.folio is not None
        and abs(left.folio - right.folio) >= 2
    )


def same_leaf(left: Unit, right: Unit) -> bool:
    return bool(
        left.folio is not None and left.folio == right.folio
        and {left.side, right.side} == {"r", "v"}
    )


def successive_opening(left: Unit, right: Unit) -> bool:
    if left.folio is None or right.folio is None:
        return False
    pairs = {
        (left.folio, left.side, right.folio, right.side),
        (right.folio, right.side, left.folio, left.side),
    }
    return any(
        first_side == "v" and second_side == "r" and second_folio == first_folio + 1
        for first_folio, first_side, second_folio, second_side in pairs
    )


def relation_pairs(
    scale: str, paragraph_units: Sequence[Unit], page_units: Sequence[Unit],
    root_weights: dict[Root, float], form_weights: dict[tuple[Any, ...], float],
) -> tuple[list[TargetPair], dict[tuple[Any, ...], list[Pair]]]:
    targets: list[TargetPair] = []
    candidates: dict[tuple[Any, ...], list[Pair]] = defaultdict(list)
    units = paragraph_units if scale == "P_PAGE" else page_units
    for left_index, left in enumerate(units):
        for right in units[left_index + 1:]:
            if left.stratum != right.stratum:
                continue
            pair = make_pair(left, right, root_weights, form_weights)
            if scale == "P_PAGE":
                key = (left.quire, left.stratum)
                if left.page == right.page and left.paragraph != right.paragraph:
                    targets.append(TargetPair(pair, left.page, key))
                elif left.page != right.page and left.quire and left.quire == right.quire:
                    candidates[key].append(pair)
            elif scale == "L_LEAF":
                key = (left.quire, left.stratum)
                if left.quire and left.quire == right.quire and same_leaf(left, right):
                    targets.append(TargetPair(pair, f"leaf:{left.folio}", key))
                elif left.quire and left.quire == right.quire and nonlocal_pair(left, right):
                    candidates[key].append(pair)
            elif scale == "O_OPENING":
                key = (left.quire, left.stratum)
                if left.quire and left.quire == right.quire and successive_opening(left, right):
                    low = min(left.folio or 0, right.folio or 0)
                    targets.append(TargetPair(pair, f"opening:{low}-{low + 1}", key))
                elif left.quire and left.quire == right.quire and nonlocal_pair(left, right):
                    candidates[key].append(pair)
            elif scale == "Q_QUIRE":
                key = (left.stratum,)
                if left.quire and left.quire == right.quire and nonlocal_pair(left, right):
                    targets.append(TargetPair(pair, f"quire:{left.quire}", key))
                elif left.quire and right.quire and left.quire != right.quire:
                    candidates[key].append(pair)
            else:
                raise ValueError(scale)
    for key in candidates:
        candidates[key].sort(key=lambda pair: pair.key)
    targets.sort(key=lambda target: (target.group, target.pair.key))
    return targets, dict(candidates)


def match_targets(
    targets: Sequence[TargetPair], candidates: dict[tuple[Any, ...], list[Pair]]
) -> tuple[list[Match], int]:
    tree_cache: dict[tuple[Any, ...], tuple[cKDTree, np.ndarray]] = {}
    for key, pairs in candidates.items():
        if pairs:
            matrix = np.stack([pair_vector(pair) for pair in pairs])
            tree_cache[key] = cKDTree(matrix), matrix
    matches: list[Match] = []
    for target in targets:
        if target.match_key not in tree_cache:
            continue
        tree, matrix = tree_cache[target.match_key]
        vector = pair_vector(target.pair)
        distance, nearest = tree.query(vector, k=1)
        tied = tree.query_ball_point(vector, r=float(distance) + 1e-12)
        pool = candidates[target.match_key]
        index = min(
            tied,
            key=lambda candidate: (
                float(np.dot(matrix[candidate] - vector, matrix[candidate] - vector)),
                pool[candidate].key,
            ),
        ) if tied else int(nearest)
        matches.append(Match(target, pool[index]))
    return matches, len(targets)


def summarize_matches(
    matches: Sequence[Match], possible: int, seed: int,
    target_similarities: Sequence[float] | None = None,
) -> dict[str, Any]:
    by_group: dict[str, list[tuple[float, float]]] = defaultdict(list)
    form_mismatch = []
    relative_length_mismatch = []
    for index, match in enumerate(matches):
        target_similarity = (
            target_similarities[index]
            if target_similarities is not None else match.target.pair.root_similarity
        )
        by_group[match.target.group].append((target_similarity, match.control.root_similarity))
        form_mismatch.append(abs(
            match.target.pair.form_similarity - match.control.form_similarity
        ))
        relative_length_mismatch.append(
            abs(match.target.pair.total_tokens - match.control.total_tokens)
            / max(match.target.pair.total_tokens, 1)
        )
    group_differences = []
    group_targets = []
    group_controls = []
    for group in sorted(by_group):
        rows = by_group[group]
        target = float(np.mean([row[0] for row in rows]))
        control = float(np.mean([row[1] for row in rows]))
        group_differences.append(target - control)
        group_targets.append(target)
        group_controls.append(control)
    effect = float(np.mean(group_differences)) if group_differences else float("nan")
    control_mean = float(np.mean(group_controls)) if group_controls else float("nan")
    low, high = bootstrap_ci(group_differences, seed)
    return {
        "possible_pairs": possible,
        "matched_pairs": len(matches),
        "coverage": len(matches) / possible if possible else 0.0,
        "independent_groups": len(by_group),
        "effect": effect,
        "target_mean": float(np.mean(group_targets)) if group_targets else float("nan"),
        "control_mean": control_mean,
        "relative_effect": effect / control_mean if control_mean > 0 else float("inf"),
        "raw_p": sign_flip_p(group_differences, seed + 1),
        "group_bootstrap_95_ci": [low, high],
        "median_form_mismatch": float(np.median(form_mismatch)) if form_mismatch else float("nan"),
        "median_relative_token_mismatch": (
            float(np.median(relative_length_mismatch)) if relative_length_mismatch else float("nan")
        ),
    }


def run_scale(
    scale: str, lines: Sequence[Line], root_weights: dict[Root, float],
    form_weights: dict[tuple[Any, ...], float], metadata: ManualMetadata,
) -> tuple[dict[str, Any], list[Match]]:
    paragraphs, pages = build_units(lines, root_weights, metadata)
    targets, candidates = relation_pairs(
        scale, paragraphs, pages, root_weights, form_weights
    )
    matches, possible = match_targets(targets, candidates)
    return summarize_matches(matches, possible, SEED + SCALES.index(scale) * 100), matches


def rotated(values: Sequence[Root], marker: int) -> list[Root]:
    if not values:
        return []
    selected = sorted(values, key=repr)
    start = marker % len(selected)
    return selected[start:] + selected[:start]


def planted_similarities(
    matches: Sequence[Match], weights: dict[Root, float], intended: bool,
) -> tuple[list[float], int, int]:
    output: list[float] = []
    replacements = 0
    opportunities = 0
    for index, match in enumerate(matches):
        left = set(match.target.pair.left.roots)
        right = set(match.target.pair.right.roots)
        donor = (
            left
            if intended else set(match.control.left.roots) - left
        )
        additions = donor - right
        removals = right - left
        count = min(
            max(1, math.ceil(0.10 * len(right))),
            len(additions), len(removals),
        )
        opportunities += len(right)
        if count:
            marker = stable_int(
                f"IL003-PLANT|{intended}|{match.target.group}|{match.target.pair.key}|{index}"
            )
            add = rotated(tuple(additions), marker)[:count]
            remove = rotated(tuple(removals), marker // 7)[:count]
            right.difference_update(remove)
            right.update(add)
            replacements += count
        output.append(weighted_jaccard(left, right, weights))
    return output, replacements, opportunities


def matching_gate(scale: str, result: dict[str, Any]) -> bool:
    required_groups = 8 if scale == "Q_QUIRE" else 20
    return bool(
        result["independent_groups"] >= required_groups
        and result["coverage"] >= 0.80
        and result["median_form_mismatch"] <= 0.05
        and result["median_relative_token_mismatch"] <= 0.10
        and math.isfinite(result["effect"])
    )


def plant_criteria(result: dict[str, Any], unplanted_effect: float) -> bool:
    return bool(
        result["effect"] - unplanted_effect >= 0.005
        and result["relative_effect"] >= 0.05
        and result["raw_p"] <= 0.01
    )


def provenance() -> dict[str, Any]:
    return {
        "runner_sha256": sha256_path(Path(__file__)),
        "dependency_sha256": {path.name: sha256_path(path) for path in DEPENDENCIES},
        "preregistration_sha256": sha256_path(PREREG),
        "metadata_sha256": sha256_path(METADATA),
        "source_sha256": {name: sha256_path(path) for name, path in SOURCES.items()},
    }


def verify_provenance(frozen: dict[str, Any]) -> None:
    current = provenance()
    for key in (
        "runner_sha256", "dependency_sha256", "preregistration_sha256",
        "metadata_sha256", "source_sha256",
    ):
        if current[key] != frozen[key]:
            raise RuntimeError(f"IL003 provenance changed after freeze: {key}")


def validation_phase() -> None:
    started = time.perf_counter()
    metadata = read_metadata()
    discovery, confirmation, forms = weight_maps()
    lines = load_lines(SOURCES["ZL3b"])
    results: dict[str, Any] = {}
    gates: dict[str, bool] = {}
    for scale in SCALES:
        observed, matches = run_scale(scale, lines, discovery, forms, metadata)
        repeated_observed, _ = run_scale(scale, lines, discovery, forms, metadata)
        deterministic = repeated_observed == observed
        intended_values, intended_replacements, opportunities = planted_similarities(
            matches, discovery, True
        )
        decoy_values, decoy_replacements, _ = planted_similarities(
            matches, discovery, False
        )
        intended = summarize_matches(
            matches, observed["possible_pairs"], SEED + 500 + SCALES.index(scale),
            intended_values,
        )
        decoy = summarize_matches(
            matches, observed["possible_pairs"], SEED + 600 + SCALES.index(scale),
            decoy_values,
        )
        match_pass = matching_gate(scale, observed)
        intended_pass = (
            intended_replacements > 0
            and plant_criteria(intended, observed["effect"])
        )
        decoy_passes = (
            decoy_replacements > 0
            and plant_criteria(decoy, observed["effect"])
        )
        gates[f"{scale}_matching"] = match_pass
        gates[f"{scale}_deterministic"] = deterministic
        gates[f"{scale}_plant"] = (
            intended_pass and decoy_replacements > 0 and not decoy_passes
        )
        results[scale] = {
            "observed_development_only": observed,
            "intended_plant": {
                "replacements": intended_replacements,
                "opportunities": opportunities,
                "result": intended,
                "passed": intended_pass,
            },
            "root_disjoint_decoy": {
                "replacements": decoy_replacements,
                "result": decoy,
                "valid": decoy_replacements > 0,
                "incorrectly_passed": decoy_passes,
            },
        }
    passed = all(gates.values())
    result = {
        "experiment": "IL003",
        "phase": "VALIDATION_FROZEN" if passed else "VALIDATION_FAILED",
        "created": "2026-08-06",
        **provenance(),
        "weight_signature": map_signature(discovery, confirmation, forms),
        "root_partition_counts": {"D": len(discovery), "C": len(confirmation)},
        "manual_metadata_counts": {
            "pages": len(metadata.quire_by_page),
            "quires": len(set(metadata.quire_by_page.values())),
            "paragraph_starts": sum(metadata.paragraph_start_by_locus.values()),
        },
        "gates": gates,
        "scales": results,
        "elapsed_seconds": time.perf_counter() - started,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    FROZEN.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(2)


def discovery_phase() -> None:
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    if frozen.get("phase") != "VALIDATION_FROZEN":
        raise RuntimeError("IL003 validation did not pass")
    verify_provenance(frozen)
    raw = {
        scale: frozen["scales"][scale]["observed_development_only"]["raw_p"]
        for scale in SCALES
    }
    adjusted = holm_adjust(raw)
    results = {}
    eligible = []
    for scale in SCALES:
        row = dict(frozen["scales"][scale]["observed_development_only"])
        row["holm_p"] = adjusted[scale]
        row["eligible"] = bool(
            frozen["gates"][f"{scale}_matching"]
            and row["effect"] >= 0.005
            and row["relative_effect"] >= 0.05
            and adjusted[scale] <= 0.05
        )
        results[scale] = row
        if row["eligible"]:
            eligible.append(scale)
    selected = max(
        eligible,
        key=lambda scale: (results[scale]["relative_effect"], -SCALES.index(scale)),
    ) if eligible else ""
    result = {
        "experiment": "IL003",
        "phase": "DISCOVERY_SELECTED" if selected else "DISCOVERY_NO_SELECTION",
        "created": "2026-08-06",
        **provenance(),
        "validation_sha256": sha256_path(FROZEN),
        "weight_signature": frozen["weight_signature"],
        "root_partition": "D",
        "results": results,
        "selected_scale": selected,
        "selected_direction": "POSITIVE" if selected else "",
    }
    DISCOVERY.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not selected:
        raise SystemExit(3)


def confirmation_edition(
    edition: str, scale: str, confirmation: dict[Root, float],
    forms: dict[tuple[Any, ...], float], metadata: ManualMetadata,
) -> dict[str, Any]:
    result, _matches = run_scale(
        scale, load_lines(SOURCES[edition]), confirmation, forms, metadata
    )
    result["matching_gate"] = matching_gate(scale, result)
    return result


def confirmation_phase() -> None:
    started = time.perf_counter()
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    discovery_result = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    if discovery_result.get("phase") != "DISCOVERY_SELECTED":
        raise RuntimeError("IL003 has no frozen discovery selection")
    verify_provenance(frozen)
    verify_provenance(discovery_result)
    if sha256_path(FROZEN) != discovery_result["validation_sha256"]:
        raise RuntimeError("IL003 validation file changed after discovery")
    selected = discovery_result["selected_scale"]
    metadata = read_metadata()
    discovery_weights, confirmation, forms = weight_maps()
    if map_signature(discovery_weights, confirmation, forms) != frozen["weight_signature"]:
        raise RuntimeError("IL003 root/form weight map changed")
    editions = {
        edition: confirmation_edition(edition, selected, confirmation, forms, metadata)
        for edition in SOURCES
    }
    primary = editions["ZL3b"]
    same_sign = all(editions[edition]["effect"] > 0 for edition in ("IT2a", "RF1b"))
    confirmed = bool(
        primary["matching_gate"]
        and primary["effect"] >= 0.005
        and primary["relative_effect"] >= 0.05
        and primary["raw_p"] <= 0.05
        and same_sign
    )
    interpretations = {
        "P_PAGE": (
            "Page-root coherence crosses manually marked paragraph boundaries, "
            "but remains compatible with page-local content, register, copying, or generation."
        ),
        "L_LEAF": (
            "Root coherence crosses from recto to verso of a leaf, weakening a "
            "strictly page-confined mechanism."
        ),
        "O_OPENING": (
            "Root coherence crosses a successive verso-to-recto opening, weakening "
            "a strictly page-confined mechanism."
        ),
        "Q_QUIRE": (
            "A broader quire-level root register/content effect is supported."
        ),
    }
    interpretation = (
        interpretations[selected] if confirmed else
        f"Discovery-selected {selected} did not confirm in the sealed C-root partition; "
        "IL002 remains valid but this scale claim is not established."
    )
    result = {
        "experiment": "IL003",
        "status": "CONFIRMED" if confirmed else "CONFIRMATION_FAILED",
        "created": "2026-08-06",
        **provenance(),
        "validation_sha256": sha256_path(FROZEN),
        "discovery_sha256": sha256_path(DISCOVERY),
        "selected_scale": selected,
        "root_partition": "C",
        "editions": editions,
        "alternate_readings_same_sign": same_sign,
        "confirmed": confirmed,
        "interpretation": interpretation,
        "elapsed_seconds": time.perf_counter() - started,
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_REPORT.write_text(report_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def report_markdown(result: dict[str, Any]) -> str:
    selected = result["selected_scale"]
    rows = []
    for edition in SOURCES:
        row = result["editions"][edition]
        rows.append(
            f"| {edition} | {row['effect']:.5f} | {100 * row['relative_effect']:.2f}% | "
            f"{row['raw_p']:.6g} | {row['independent_groups']} |"
        )
    return "\n".join([
        "# IL003 — multiscale independent-root confirmation",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Discovery-selected scale: `{selected}`.",
        "",
        result["interpretation"],
        "",
        "| Reading | C-root effect | relative | p | groups |",
        "|---|---:|---:|---:|---:|",
        *rows,
        "",
        "ZL3b/IT2a/RF1b are alternate readings of one manuscript, not replications.",
        "The confirmation root vocabulary was not used for scale selection.",
        "No word meaning, topic, language, cipher, or plaintext is inferred.",
        "No OCR, image, embedding, or automated visual input was used.",
        "",
    ])


def selftest() -> None:
    roots = [(letter,) for letter in "abcdefgh"]
    partitions = Counter(root_partition(root) for root in roots)
    assert set(partitions) <= {"D", "C"} and sum(partitions.values()) == len(roots)
    assert simple_folio("f12r") == (12, "r")
    assert simple_folio("f68r1") == (None, "")
    root_weights = {root: 1.0 for root in roots}
    form_a = ((0, "NONE", "NONE", "NONE", "NONE"),)
    form_b = ((0, "NONE", "NONE", "A", "NONE"),)
    form_weights = {form_a: 1.0, form_b: 1.0}
    paragraphs: list[Unit] = []
    pages: list[Unit] = []
    stratum = ("A", "H", "1")
    for quire_index, (quire, start) in enumerate((("A", 1), ("B", 5), ("C", 9))):
        for folio in range(start, start + 4):
            for side_index, side in enumerate(("r", "v")):
                page = f"f{folio}{side}"
                offset = (quire_index * 3 + folio + 2 * side_index) % len(roots)
                selected = frozenset(roots[(offset + index) % len(roots)] for index in range(4))
                pages.append(Unit(
                    page, "PAGE", page, quire, stratum, selected,
                    frozenset((form_a, form_b)), 12, None, folio, side,
                ))
                for paragraph in (0, 1):
                    p_roots = frozenset(
                        roots[(offset + paragraph + index) % len(roots)]
                        for index in range(3)
                    )
                    paragraphs.append(Unit(
                        f"{page}:p{paragraph}", "PARAGRAPH", page, quire,
                        stratum, p_roots, frozenset((form_a, form_b)), 6,
                        paragraph, folio, side,
                    ))
    synthetic_counts = {}
    for scale in SCALES:
        targets, candidates = relation_pairs(
            scale, paragraphs, pages, root_weights, form_weights
        )
        matches, possible = match_targets(targets, candidates)
        assert possible > 0 and matches
        planted, replacements, _ = planted_similarities(matches, root_weights, True)
        assert replacements > 0 and all(math.isfinite(value) for value in planted)
        synthetic_counts[scale] = {"targets": possible, "matches": len(matches)}
    print(json.dumps({
        "status": "PASS",
        "test_root_partitions": dict(partitions),
        "simple_folio": simple_folio("f12r"),
        "synthetic_scales": synthetic_counts,
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase", choices=("selftest", "validate", "discover", "confirm"),
        required=True,
    )
    args = parser.parse_args()
    if args.phase == "selftest":
        selftest()
    elif args.phase == "validate":
        validation_phase()
    elif args.phase == "discover":
        discovery_phase()
    else:
        confirmation_phase()


if __name__ == "__main__":
    main()
