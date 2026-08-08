#!/usr/bin/env python3
"""IL002: form-matched line-pair topology in manual Voynich transcription."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
from scipy.spatial import cKDTree


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
sys.path.insert(0, str(HERE))

from run_il001_information_location import (  # noqa: E402
    GAIN_MODELS,
    Line,
    Root,
    SOURCES,
    Token,
    bootstrap_ci,
    corpus_inventory,
    holm_adjust,
    load_lines,
    page_groups,
    select_split,
    sha256_path,
    shuffle_lines_within_pages,
    sign_flip_p,
    stable_int,
)


PREREG = HERE / "hypotheses" / "IL002_MATCHED_LINE_PAIR_PREREGISTRATION.md"
DEPENDENCY = HERE / "run_il001_information_location.py"
RESULTS = HERE / "results"
FROZEN = RESULTS / "il002_matched_line_pair_validation_frozen.json"
OUTPUT_JSON = RESULTS / "il002_matched_line_pair_results.json"
OUTPUT_REPORT = RESULTS / "il002_matched_line_pair_report.md"
MIN_ROOT_DF = 5
SEED = 2_200_002


@dataclass(frozen=True)
class WeightModel:
    root_weights: dict[Root, float]
    form_weights: dict[tuple[Any, ...], float]
    total_length_scale: float
    imbalance_scale: float
    signature: str


@dataclass(frozen=True)
class Fingerprint:
    line: Line
    ordinal: int
    roots: frozenset[Root]
    forms: frozenset[tuple[Any, ...]]

    @property
    def length(self) -> int:
        return len(self.line.tokens)

    @property
    def key(self) -> tuple[str, str]:
        return self.line.page, self.line.locus


@dataclass(frozen=True)
class Pair:
    left: Fingerprint
    right: Fingerprint
    root_similarity: float
    form_similarity: float
    total_length: int
    imbalance: int

    @property
    def key(self) -> tuple[str, str, str, str]:
        first, second = sorted((self.left.key, self.right.key))
        return first[0], first[1], second[0], second[1]

    @property
    def page(self) -> str:
        return self.left.line.page


def weighted_jaccard(
    left: Iterable[Any], right: Iterable[Any], weights: dict[Any, float]
) -> float:
    left_set = set(left)
    right_set = set(right)
    union = left_set | right_set
    denominator = sum(weights.get(value, 0.0) for value in union)
    if denominator <= 0:
        return 0.0
    numerator = sum(weights.get(value, 0.0) for value in left_set & right_set)
    return numerator / denominator


def weight_signature(
    roots: dict[Root, float], forms: dict[tuple[Any, ...], float], scales: tuple[float, float]
) -> str:
    rows = [
        *(f"R\t{root!r}\t{weight:.17g}" for root, weight in sorted(roots.items())),
        *(f"F\t{form!r}\t{weight:.17g}" for form, weight in sorted(forms.items(), key=lambda row: repr(row[0]))),
        f"S\t{scales[0]:.17g}\t{scales[1]:.17g}",
    ]
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()


def preliminary_weights(train: Sequence[Line]) -> tuple[dict[Root, float], dict[tuple[Any, ...], float]]:
    root_df: Counter[Root] = Counter()
    form_df: Counter[tuple[Any, ...]] = Counter()
    for line in train:
        root_df.update({token.root for token in line.tokens})
        form_df.update({token.shell for token in line.tokens})
    count = len(train)
    roots = {
        root: math.log((count + 1) / (frequency + 1))
        for root, frequency in root_df.items() if frequency >= MIN_ROOT_DF
    }
    forms = {
        form: math.log((count + 1) / (frequency + 1))
        for form, frequency in form_df.items()
    }
    return roots, forms


def build_fingerprints(
    lines: Sequence[Line], root_weights: dict[Root, float]
) -> list[Fingerprint]:
    output: list[Fingerprint] = []
    for _page, selected in page_groups(lines):
        for ordinal, line in enumerate(selected):
            roots = frozenset(
                token.root for token in line.tokens if token.root in root_weights
            )
            if len(roots) < 2:
                continue
            output.append(Fingerprint(
                line=line,
                ordinal=ordinal,
                roots=roots,
                forms=frozenset(token.shell for token in line.tokens),
            ))
    return output


def training_scales(
    train: Sequence[Line], root_weights: dict[Root, float]
) -> tuple[float, float]:
    fingerprints = build_fingerprints(train, root_weights)
    totals: list[int] = []
    imbalances: list[int] = []
    by_page: dict[str, list[Fingerprint]] = defaultdict(list)
    for fingerprint in fingerprints:
        by_page[fingerprint.line.page].append(fingerprint)
    for selected in by_page.values():
        for left_index, left in enumerate(selected):
            for right in selected[left_index + 1:]:
                if left.line.stratum != right.line.stratum:
                    continue
                totals.append(left.length + right.length)
                imbalances.append(abs(left.length - right.length))
    total_scale = float(np.std(totals, ddof=1)) if len(totals) > 1 else 1.0
    imbalance_scale = float(np.std(imbalances, ddof=1)) if len(imbalances) > 1 else 1.0
    return max(total_scale, 1.0), max(imbalance_scale, 1.0)


def build_weight_model(train: Sequence[Line]) -> WeightModel:
    roots, forms = preliminary_weights(train)
    scales = training_scales(train, roots)
    return WeightModel(
        roots, forms, scales[0], scales[1],
        weight_signature(roots, forms, scales),
    )


def make_pair(left: Fingerprint, right: Fingerprint, weights: WeightModel) -> Pair:
    return Pair(
        left=left,
        right=right,
        root_similarity=weighted_jaccard(left.roots, right.roots, weights.root_weights),
        form_similarity=weighted_jaccard(left.forms, right.forms, weights.form_weights),
        total_length=left.length + right.length,
        imbalance=abs(left.length - right.length),
    )


def pair_vector(pair: Pair, weights: WeightModel) -> np.ndarray:
    return np.asarray([
        pair.form_similarity,
        pair.total_length / weights.total_length_scale,
        pair.imbalance / weights.imbalance_scale,
    ], dtype=np.float64)


def vector_distance(left: Pair, right: Pair, weights: WeightModel) -> float:
    difference = pair_vector(left, weights) - pair_vector(right, weights)
    return float(np.dot(difference, difference))


def page_fingerprints(fingerprints: Sequence[Fingerprint]) -> dict[str, list[Fingerprint]]:
    output: dict[str, list[Fingerprint]] = defaultdict(list)
    for fingerprint in fingerprints:
        output[fingerprint.line.page].append(fingerprint)
    for page in output:
        output[page].sort(key=lambda row: row.ordinal)
    return dict(output)


def adjacency_observations(
    fingerprints: Sequence[Fingerprint], weights: WeightModel
) -> tuple[list[dict[str, Any]], int]:
    observations: list[dict[str, Any]] = []
    possible = 0
    for page, selected in page_fingerprints(fingerprints).items():
        targets = []
        controls = []
        for left_index, left in enumerate(selected):
            for right in selected[left_index + 1:]:
                if left.line.stratum != right.line.stratum:
                    continue
                pair = make_pair(left, right, weights)
                distance = right.ordinal - left.ordinal
                if distance == 1:
                    targets.append(pair)
                elif distance >= 2:
                    controls.append(pair)
        possible += len(targets)
        for target in targets:
            if not controls:
                continue
            control = min(
                controls,
                key=lambda pair: (vector_distance(target, pair, weights), pair.key),
            )
            observations.append({
                "page": page,
                "difference": target.root_similarity - control.root_similarity,
                "target": target.root_similarity,
                "control": control.root_similarity,
                "form_mismatch": abs(target.form_similarity - control.form_similarity),
                "length_mismatch": abs(target.total_length - control.total_length),
            })
    return observations, possible


def cross_page_candidates(
    fingerprints: Sequence[Fingerprint], weights: WeightModel
) -> dict[tuple[str, str, str], list[Pair]]:
    by_stratum: dict[tuple[str, str, str], list[Fingerprint]] = defaultdict(list)
    for fingerprint in fingerprints:
        by_stratum[fingerprint.line.stratum].append(fingerprint)
    output: dict[tuple[str, str, str], list[Pair]] = {}
    for stratum, selected in by_stratum.items():
        pairs = []
        for left_index, left in enumerate(selected):
            for right in selected[left_index + 1:]:
                if left.line.page == right.line.page:
                    continue
                pairs.append(make_pair(left, right, weights))
        pairs.sort(key=lambda pair: pair.key)
        output[stratum] = pairs
    return output


def remote_page_observations(
    fingerprints: Sequence[Fingerprint], weights: WeightModel
) -> tuple[list[dict[str, Any]], int]:
    candidates = cross_page_candidates(fingerprints, weights)
    trees: dict[tuple[str, str, str], tuple[cKDTree, np.ndarray]] = {}
    for stratum, pairs in candidates.items():
        if pairs:
            matrix = np.stack([pair_vector(pair, weights) for pair in pairs])
            trees[stratum] = cKDTree(matrix), matrix

    observations: list[dict[str, Any]] = []
    possible = 0
    for page, selected in page_fingerprints(fingerprints).items():
        for left_index, left in enumerate(selected):
            for right in selected[left_index + 1:]:
                if (
                    left.line.stratum != right.line.stratum
                    or right.ordinal - left.ordinal < 2
                ):
                    continue
                possible += 1
                stratum = left.line.stratum
                if stratum not in trees:
                    continue
                target = make_pair(left, right, weights)
                tree, matrix = trees[stratum]
                vector = pair_vector(target, weights)
                nearest_distance, nearest_index = tree.query(vector, k=1)
                tied = tree.query_ball_point(vector, r=float(nearest_distance) + 1e-12)
                control_index = min(
                    tied,
                    key=lambda index: (
                        float(np.dot(matrix[index] - vector, matrix[index] - vector)),
                        candidates[stratum][index].key,
                    ),
                ) if tied else int(nearest_index)
                control = candidates[stratum][control_index]
                observations.append({
                    "page": page,
                    "difference": target.root_similarity - control.root_similarity,
                    "target": target.root_similarity,
                    "control": control.root_similarity,
                    "form_mismatch": abs(target.form_similarity - control.form_similarity),
                    "length_mismatch": abs(target.total_length - control.total_length),
                })
    return observations, possible


def summarize_observations(
    observations: Sequence[dict[str, Any]], possible: int, seed: int
) -> dict[str, Any]:
    by_page: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in observations:
        by_page[row["page"]].append(row)
    page_differences = [
        float(np.mean([row["difference"] for row in selected]))
        for _page, selected in sorted(by_page.items())
    ]
    page_targets = [
        float(np.mean([row["target"] for row in selected]))
        for _page, selected in sorted(by_page.items())
    ]
    page_controls = [
        float(np.mean([row["control"] for row in selected]))
        for _page, selected in sorted(by_page.items())
    ]
    effect = float(np.mean(page_differences)) if page_differences else float("nan")
    control = float(np.mean(page_controls)) if page_controls else float("nan")
    low, high = bootstrap_ci(page_differences, seed)
    form_mismatches = [row["form_mismatch"] for row in observations]
    length_mismatches = [row["length_mismatch"] for row in observations]
    return {
        "possible_pairs": possible,
        "matched_pairs": len(observations),
        "coverage": len(observations) / possible if possible else 0.0,
        "pages": len(by_page),
        "effect": effect,
        "target_mean": float(np.mean(page_targets)) if page_targets else float("nan"),
        "control_mean": control,
        "relative_effect": effect / control if control > 0 else float("inf"),
        "raw_p": sign_flip_p(page_differences, seed + 1),
        "page_bootstrap_95_ci": [low, high],
        "median_form_mismatch": float(np.median(form_mismatches)) if form_mismatches else float("nan"),
        "median_total_length_mismatch": float(np.median(length_mismatches)) if length_mismatches else float("nan"),
    }


def run_contrasts(lines: Sequence[Line], weights: WeightModel) -> dict[str, Any]:
    fingerprints = build_fingerprints(lines, weights.root_weights)
    adjacency, adjacency_possible = adjacency_observations(fingerprints, weights)
    remote, remote_possible = remote_page_observations(fingerprints, weights)
    return {
        "eligible_lines": len(fingerprints),
        "A_ADJACENCY": summarize_observations(adjacency, adjacency_possible, SEED + 10),
        "B_REMOTE_PAGE": summarize_observations(remote, remote_possible, SEED + 20),
    }


def run_one_contrast(
    lines: Sequence[Line], weights: WeightModel, name: str
) -> dict[str, Any]:
    fingerprints = build_fingerprints(lines, weights.root_weights)
    if name == "A_ADJACENCY":
        observations, possible = adjacency_observations(fingerprints, weights)
        seed = SEED + 10
    elif name == "B_REMOTE_PAGE":
        observations, possible = remote_page_observations(fingerprints, weights)
        seed = SEED + 20
    else:
        raise ValueError(name)
    return summarize_observations(observations, possible, seed)


def plant_copy_signal(
    lines: Sequence[Line], source: str, eligible: set[Root]
) -> tuple[list[Line], int]:
    output: list[Line] = []
    replacements = 0
    for page, selected in page_groups(lines):
        for line_index, line in enumerate(selected):
            donors: list[Line] = []
            if source == "A_ADJACENCY":
                if line_index > 0 and selected[line_index - 1].stratum == line.stratum:
                    donors = [selected[line_index - 1]]
            elif source == "B_REMOTE_PAGE":
                donors = [
                    candidate for candidate_index, candidate in enumerate(selected)
                    if abs(candidate_index - line_index) >= 2
                    and candidate.stratum == line.stratum
                ]
            else:
                raise ValueError(source)
            new_tokens: list[Token] = []
            for token_index, token in enumerate(line.tokens):
                marker = stable_int(
                    f"IL002-PLANT|{source}|{page}|{line.locus}|{token_index}"
                )
                if donors and marker % 10 == 0:
                    donor = donors[(marker // 10) % len(donors)]
                    candidates = [
                        candidate.root for candidate in donor.tokens
                        if candidate.root in eligible and candidate.root != token.root
                    ]
                    if candidates:
                        copied = candidates[(marker // 100) % len(candidates)]
                        new_tokens.append(replace(token, root=copied))
                        replacements += 1
                        continue
                new_tokens.append(token)
            output.append(replace(line, tokens=tuple(new_tokens)))
    return output, replacements


def matching_gate(result: dict[str, Any]) -> bool:
    return bool(
        result["coverage"] >= 0.80
        and result["pages"] > 0
        and result["median_form_mismatch"] <= 0.05
        and result["median_total_length_mismatch"] <= 2.0
    )


def planted_gate(result: dict[str, Any]) -> bool:
    return bool(
        result["effect"] >= 0.005
        and result["relative_effect"] >= 0.05
        and result["raw_p"] <= 0.01
    )


def validation_phase() -> None:
    started = time.perf_counter()
    lines = load_lines(SOURCES["ZL3b"])
    train = select_split(lines, "train")
    validation = select_split(lines, "validation")
    weights = build_weight_model(train)
    observed = run_contrasts(validation, weights)
    planted: dict[str, Any] = {}
    for name in ("A_ADJACENCY", "B_REMOTE_PAGE"):
        modified, replacements = plant_copy_signal(
            validation, name, set(weights.root_weights)
        )
        result = run_one_contrast(modified, weights, name)
        planted[name] = {
            "replacements": replacements,
            "replacement_fraction": replacements / sum(len(line.tokens) for line in validation),
            "result": result,
            "passed": replacements > 0 and planted_gate(result),
        }

    planted_a_lines, _ = plant_copy_signal(
        validation, "A_ADJACENCY", set(weights.root_weights)
    )
    planted_a = planted["A_ADJACENCY"]["result"]
    shuffled_a = run_one_contrast(
        shuffle_lines_within_pages(planted_a_lines), weights, "A_ADJACENCY"
    )
    shuffle_passed = bool(
        planted_a["effect"] - shuffled_a["effect"] >= 0.005
        and (shuffled_a["effect"] < 0.005 or shuffled_a["raw_p"] > 0.01)
    )
    inventory = corpus_inventory(lines)
    gates = {
        "split_nonempty": all(inventory[name]["pages"] and inventory[name]["targets"] for name in inventory),
        "matching_A": matching_gate(observed["A_ADJACENCY"]),
        "matching_B": matching_gate(observed["B_REMOTE_PAGE"]),
        "planted_A": planted["A_ADJACENCY"]["passed"],
        "planted_B": planted["B_REMOTE_PAGE"]["passed"],
        "shuffle_removes_planted_A": shuffle_passed,
    }
    passed = all(gates.values())
    result = {
        "experiment": "IL002",
        "phase": "VALIDATION_FROZEN" if passed else "VALIDATION_FAILED",
        "created": "2026-08-06",
        "runner_sha256": sha256_path(Path(__file__)),
        "dependency_sha256": sha256_path(DEPENDENCY),
        "preregistration_sha256": sha256_path(PREREG),
        "source_sha256": {name: sha256_path(path) for name, path in SOURCES.items()},
        "inventory": inventory,
        "weight_signature": weights.signature,
        "weight_counts": {
            "eligible_roots": len(weights.root_weights),
            "forms": len(weights.form_weights),
        },
        "scales": {
            "total_length": weights.total_length_scale,
            "imbalance": weights.imbalance_scale,
        },
        "development_observed_not_inferential": observed,
        "planted": planted,
        "shuffled_planted_A": shuffled_a,
        "gates": gates,
        "elapsed_seconds": time.perf_counter() - started,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    FROZEN.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(2)


def edition_result(edition: str) -> dict[str, Any]:
    lines = load_lines(SOURCES[edition])
    train = select_split(lines, "train")
    test = select_split(lines, "test")
    weights = build_weight_model(train)
    contrasts = run_contrasts(test, weights)
    return {
        "inventory": corpus_inventory(lines),
        "weight_signature": weights.signature,
        "eligible_roots": len(weights.root_weights),
        "forms": len(weights.form_weights),
        "scales": {
            "total_length": weights.total_length_scale,
            "imbalance": weights.imbalance_scale,
        },
        "contrasts": contrasts,
    }


def final_phase() -> None:
    started = time.perf_counter()
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    if frozen.get("phase") != "VALIDATION_FROZEN":
        raise RuntimeError("IL002 validation did not freeze a passing configuration")
    checks = {
        "runner": (sha256_path(Path(__file__)), frozen["runner_sha256"]),
        "dependency": (sha256_path(DEPENDENCY), frozen["dependency_sha256"]),
        "preregistration": (sha256_path(PREREG), frozen["preregistration_sha256"]),
    }
    for name, (actual, expected) in checks.items():
        if actual != expected:
            raise RuntimeError(f"{name} changed after validation freeze")
    for edition, path in SOURCES.items():
        if sha256_path(path) != frozen["source_sha256"][edition]:
            raise RuntimeError(f"manual source changed after validation: {edition}")

    editions = {edition: edition_result(edition) for edition in SOURCES}
    if editions["ZL3b"]["weight_signature"] != frozen["weight_signature"]:
        raise RuntimeError("ZL training representation changed after validation")

    raw_p = {
        name: editions["ZL3b"]["contrasts"][name]["raw_p"]
        for name in ("A_ADJACENCY", "B_REMOTE_PAGE")
    }
    adjusted = holm_adjust(raw_p)
    material: dict[str, bool] = {}
    for name in raw_p:
        primary = editions["ZL3b"]["contrasts"][name]
        direction = all(
            editions[edition]["contrasts"][name]["effect"] > 0
            for edition in ("IT2a", "RF1b")
        )
        primary["holm_p"] = adjusted[name]
        primary["alternate_readings_same_sign"] = direction
        material[name] = bool(
            primary["effect"] >= 0.005
            and primary["relative_effect"] >= 0.05
            and adjusted[name] <= 0.05
            and direction
        )

    if material["A_ADJACENCY"] and material["B_REMOTE_PAGE"]:
        interpretation = (
            "Mixed topology: exact roots carry both adjacency-specific sequential "
            "information and broader page-level coherence after form/length matching."
        )
    elif material["A_ADJACENCY"]:
        interpretation = (
            "Exact roots carry adjacency-specific sequential information beyond "
            "matched form structure; this is not by itself a natural-language result."
        )
    elif material["B_REMOTE_PAGE"]:
        interpretation = (
            "Exact roots carry nonadjacent page-level coherence without a material "
            "adjacency result, supporting topic/catalogue/mnemonic organization."
        )
    else:
        interpretation = (
            "Neither registered exact-root overlap contrast met the held materiality "
            "rule; these invariants do not discriminate manuscript-system class."
        )

    result = {
        "experiment": "IL002",
        "status": "FINAL_HELD_EVALUATED",
        "created": "2026-08-06",
        "runner_sha256": sha256_path(Path(__file__)),
        "preregistration_sha256": sha256_path(PREREG),
        "validation_gates": frozen["gates"],
        "editions": editions,
        "material": material,
        "interpretation": interpretation,
        "elapsed_seconds": time.perf_counter() - started,
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_REPORT.write_text(report_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def report_markdown(result: dict[str, Any]) -> str:
    rows = []
    for name in ("A_ADJACENCY", "B_REMOTE_PAGE"):
        primary = result["editions"]["ZL3b"]["contrasts"][name]
        rows.append(
            f"| {name} | {primary['effect']:.5f} | {100 * primary['relative_effect']:.2f}% | "
            f"{primary['holm_p']:.6g} | {primary['matched_pairs']}/{primary['possible_pairs']} | "
            f"{'yes' if result['material'][name] else 'no'} |"
        )
    sensitivity = []
    for edition in ("IT2a", "RF1b"):
        contrasts = result["editions"][edition]["contrasts"]
        sensitivity.append(
            f"| {edition} | {contrasts['A_ADJACENCY']['effect']:.5f} | "
            f"{contrasts['B_REMOTE_PAGE']['effect']:.5f} |"
        )
    return "\n".join([
        "# IL002 — matched line-pair root topology result",
        "",
        f"Status: **{result['status']}**",
        "",
        "## Outcome",
        "",
        result["interpretation"],
        "",
        "No word, POS, language, cipher, or plaintext meaning is inferred.",
        "",
        "## Frozen ZL3b contrasts",
        "",
        "| Contrast | effect | relative | Holm p | matched | material |",
        "|---|---:|---:|---:|---:|---|",
        *rows,
        "",
        "## Alternate-reading directional sensitivity",
        "",
        "| Reading | adjacency effect | remote-page effect |",
        "|---|---:|---:|",
        *sensitivity,
        "",
        "ZL3b, IT2a, and RF1b are alternate readings of one manuscript, not replications.",
        "",
        "## Method safeguards",
        "",
        "- Manual transcription and locked text parser only; no OCR or image-derived input.",
        "- Matching used form shells and line lengths only and never inspected root similarity.",
        "- Validation plants and matching-quality gates passed before the one held run.",
        "- Full numeric results and provenance hashes are in the accompanying JSON.",
        "",
    ])


def selftest() -> None:
    weights = {("a",): 1.0, ("b",): 2.0, ("c",): 3.0}
    assert abs(weighted_jaccard({("a",), ("b",)}, {("b",), ("c",)}, weights) - 2 / 6) < 1e-12
    assert weighted_jaccard(set(), set(), weights) == 0.0
    shell = ((0, "NONE", "NONE", "NONE", "NONE"),)
    synthetic: list[Line] = []
    patterns = (
        ("a", "b", "c"), ("a", "b", "d"),
        ("c", "d", "e"), ("c", "d", "f"),
    )
    for page_index, page in enumerate(("f1r", "f2r", "f3r")):
        for line_index, roots in enumerate(patterns):
            tokens = tuple(
                Token((root,), shell, min(4, position * 2), "2-4")
                for position, root in enumerate(roots)
            )
            synthetic.append(Line(
                page, f"{page}.{line_index + 1}", "A", "H", "1",
                line_index == 0, tokens,
            ))
    root_weights = {(root,): 1.0 for root in "abcdef"}
    form_weights = {shell: 1.0}
    model = WeightModel(
        root_weights, form_weights, 1.0, 1.0,
        weight_signature(root_weights, form_weights, (1.0, 1.0)),
    )
    result = run_contrasts(synthetic, model)
    assert result["A_ADJACENCY"]["matched_pairs"] > 0
    assert result["B_REMOTE_PAGE"]["matched_pairs"] > 0
    print(json.dumps({
        "status": "PASS",
        "weighted_jaccard": 2 / 6,
        "adjacency_pairs": result["A_ADJACENCY"]["matched_pairs"],
        "remote_pairs": result["B_REMOTE_PAGE"]["matched_pairs"],
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("selftest", "validate", "final"), required=True)
    args = parser.parse_args()
    if args.phase == "selftest":
        selftest()
    elif args.phase == "validate":
        validation_phase()
    else:
        final_phase()


if __name__ == "__main__":
    main()
