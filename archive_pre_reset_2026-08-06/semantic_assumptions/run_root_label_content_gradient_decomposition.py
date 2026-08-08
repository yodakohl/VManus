#!/usr/bin/env python3
"""Decompose the confirmed root-label-content line gradient.

Every endpoint of a broad D/E-bound -> q-dependent visible-word edge is
removed before scoring.  The residual continuous gradient is fixed.  A second
stage lets odd ZL choose EARLY->MIDDLE or MIDDLE->LATE and freezes that
transition for even ZL/IT/RF.  Scores retain the source-axis and root-free-form
controls of the confirming parent test.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import multiprocessing
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import cupy as cp
import numpy as np

from common import folio_number
from run_bidirectional_context_controls import timm_tokens
from run_construction_label_semantics import control_paths
from run_internal_utterance_grammar import line_nodes
from run_root_label_content_line_profile import (
    form_residual, page_correlations, sign_flip,
)
from run_section_content_bridge import SOURCES
from run_star_d_select_label_slot import (
    normalized_score, root_normalization, source_validation, train_root_axis,
)
from run_star_entry_label_gradient import (
    LabelCorpus, label_corpus, relaid_label_corpus,
)


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUTPUT_JSON = RESULTS / "root_label_content_gradient_decomposition_results.json"
OUTPUT_REPORT = RESULTS / "root_label_content_gradient_decomposition_report.md"
TRANSITIONS = ("MIDDLE_MINUS_EARLY", "LATE_MINUS_MIDDLE")
SEED = 2_608_059
DEFAULT_PERMUTATIONS = 200_000


def broad_selector_edge(left: Any, right: Any) -> bool:
    return (
        left.last_role in {"BOUND_D", "Q_BOUND_D", "BOUND_E", "Q_BOUND_E"}
        and right.first_role.startswith("Q_")
    )


def filtered_events(
    corpus: LabelCorpus, weights: dict[str, float],
    normalization: tuple[float, float],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    output = []
    counts = {"eligible_interior_words": 0, "removed_edge_endpoints": 0, "retained_words": 0}
    for row in corpus.rows:
        if row.kind != "P" or row.section == "P":
            continue
        nodes = line_nodes(row)
        if len(nodes) < 6:
            continue
        removed = set()
        for index, (left, right) in enumerate(zip(nodes, nodes[1:])):
            if broad_selector_edge(left, right):
                removed.update((index, index + 1))
        for index, node in enumerate(nodes):
            if index in {0, len(nodes) - 1}:
                continue
            counts["eligible_interior_words"] += 1
            if index in removed:
                counts["removed_edge_endpoints"] += 1
                continue
            values = [normalized_score(root, weights, normalization) for root in node.roots]
            output.append({
                "page": row.page, "locus": row.locus,
                "position": index / (len(nodes) - 1),
                "score": float(np.mean(values)) if values else 0.0,
                "unit_count": len(node.units), "form": tuple(node.roles),
            })
            counts["retained_words"] += 1
    return output, counts


def centered_values(rows: list[dict[str, Any]], values: np.ndarray) -> np.ndarray:
    output = values.copy()
    by_line: defaultdict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        by_line[row["locus"]].append(index)
    for indices in by_line.values():
        selected = np.asarray(indices, dtype=np.int32)
        output[selected] -= output[selected].mean()
    return output


def stage_pages(
    rows: list[dict[str, Any]], residual: np.ndarray,
) -> dict[str, dict[str, float]]:
    values = centered_values(rows, residual)
    by_page: defaultdict[str, dict[int, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row, value in zip(rows, values, strict=True):
        position = row["position"]
        zone = 0 if position < 1 / 3 else (1 if position <= 2 / 3 else 2)
        by_page[row["page"]][zone].append(float(value))
    output = {name: {} for name in TRANSITIONS}
    for page, zones in by_page.items():
        if any(len(zones[zone]) < 3 for zone in (0, 1, 2)):
            continue
        means = [float(np.mean(zones[zone])) for zone in (0, 1, 2)]
        output["MIDDLE_MINUS_EARLY"][page] = means[1] - means[0]
        output["LATE_MINUS_MIDDLE"][page] = means[2] - means[1]
    return output


def corpus_result(corpus: LabelCorpus) -> dict[str, Any]:
    weights = train_root_axis(corpus, lambda _folio: True)
    normalization = root_normalization(corpus, weights)
    rows, counts = filtered_events(corpus, weights, normalization)
    residual = form_residual(rows)
    gradient = page_correlations(rows, residual)
    stages = stage_pages(rows, residual)
    return {"counts": counts, "gradient_pages": gradient, "stage_pages": stages}


def t_stat(values: list[float]) -> float:
    array = np.asarray(values, dtype=np.float64)
    if len(array) < 2 or array.std(ddof=1) < 1e-12:
        return 0.0
    return float(array.mean() / (array.std(ddof=1) / np.sqrt(len(array))))


def family_stage_test(
    stage_pages_map: dict[str, dict[str, float]], parity: int,
    permutations: int, seed: int,
) -> dict[str, Any]:
    pages = sorted(set.intersection(*(
        set(stage_pages_map[name]) for name in TRANSITIONS
    )))
    pages = [page for page in pages if folio_number(page) % 2 == parity]
    matrix = np.asarray([
        [stage_pages_map[name][page] for page in pages] for name in TRANSITIONS
    ], dtype=np.float64)
    observed = np.asarray([t_stat(row.tolist()) for row in matrix])
    selected_index = int(np.argmax(observed))
    gpu = cp.asarray(matrix, dtype=cp.float32)
    rng = cp.random.RandomState(seed)
    raw_exceed = 0
    family_exceed = 0
    threshold = float(observed[selected_index])
    for start in range(0, permutations, 20_000):
        count = min(20_000, permutations - start)
        signs = cp.where(
            rng.random_sample((count, len(pages)), dtype=cp.float32) < 0.5,
            -1.0, 1.0,
        )
        signed = gpu[:, None, :] * signs[None, :, :]
        means = signed.mean(axis=2)
        variance = cp.maximum(
            (cp.sum(gpu * gpu, axis=1)[:, None] - len(pages) * means * means)
            / max(len(pages) - 1, 1), 0,
        )
        null_t = means / cp.maximum(cp.sqrt(variance / len(pages)), 1e-12)
        raw_exceed += int(cp.count_nonzero(null_t[selected_index] >= threshold - 1e-12).get())
        family_exceed += int(cp.count_nonzero(null_t.max(axis=0) >= threshold - 1e-12).get())
    selected = TRANSITIONS[selected_index]
    return {
        "selected": selected, "pages": len(pages),
        "tests": {
            name: {
                "mean": float(matrix[index].mean()),
                "t": float(observed[index]),
                "positive_pages": int(np.count_nonzero(matrix[index] > 0)),
            } for index, name in enumerate(TRANSITIONS)
        },
        "selected_raw_p": (raw_exceed + 1) / (permutations + 1),
        "selected_family_p": (family_exceed + 1) / (permutations + 1),
    }


def fixed_stage_test(
    stage_pages_map: dict[str, dict[str, float]], selected: str, parity: int,
    permutations: int, seed: int,
) -> dict[str, Any]:
    pages = [
        page for page in sorted(stage_pages_map[selected])
        if folio_number(page) % 2 == parity
    ]
    result = sign_flip(
        [stage_pages_map[selected][page] for page in pages], permutations, seed
    )
    return {**result, "pages": len(pages), "positive_pages": int(sum(
        stage_pages_map[selected][page] > 0 for page in pages
    ))}


def control_job(job: tuple[str, LabelCorpus]) -> dict[str, Any]:
    path_text, template = job
    path = Path(path_text)
    corpus = relaid_label_corpus(template, timm_tokens(path))
    result = corpus_result(corpus)
    gradient = result["gradient_pages"]
    odd_tests = {
        name: t_stat([
            value for page, value in result["stage_pages"][name].items()
            if folio_number(page) % 2 == 1
        ]) for name in TRANSITIONS
    }
    selected = max(TRANSITIONS, key=lambda name: odd_tests[name])
    held_values = [
        value for page, value in result["stage_pages"][selected].items()
        if folio_number(page) % 2 == 0
    ]
    return {
        "file": path.name,
        "gradient_mean": float(np.mean(list(gradient.values()))),
        "selected_transition": selected,
        "odd_selected_t": odd_tests[selected],
        "even_selected_t": t_stat(held_values),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--permutations", type=int, default=DEFAULT_PERMUTATIONS)
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--control-dir", type=Path, default=Path("/tmp/timm-extended.QbsuS8"))
    args = parser.parse_args()
    if args.permutations < 1 or args.workers < 1:
        parser.error("permutations/workers must be positive")
    started = time.perf_counter()
    corpora = {edition: label_corpus(path) for edition, path in SOURCES.items()}
    source = {edition: source_validation(corpus) for edition, corpus in corpora.items()}
    raw = {edition: corpus_result(corpus) for edition, corpus in corpora.items()}
    gradients = {}
    for edition_index, result in enumerate(raw.values()):
        pages = result["gradient_pages"]
        gradients[list(raw)[edition_index]] = {
            "all": sign_flip(list(pages.values()), args.permutations, SEED + edition_index * 20),
            "even": sign_flip([
                value for page, value in pages.items() if folio_number(page) % 2 == 0
            ], args.permutations, SEED + edition_index * 20 + 1),
            "odd": sign_flip([
                value for page, value in pages.items() if folio_number(page) % 2 == 1
            ], args.permutations, SEED + edition_index * 20 + 2),
            "pages": len(pages), "positive_pages": int(sum(value > 0 for value in pages.values())),
        }
    discovery = family_stage_test(raw["ZL3b"]["stage_pages"], 1, args.permutations, SEED + 100)
    selected = discovery["selected"]
    held = {
        edition: fixed_stage_test(
            raw[edition]["stage_pages"], selected, 0, args.permutations,
            SEED + 200 + index,
        ) for index, edition in enumerate(SOURCES)
    }

    paths = control_paths(args.control_dir)
    jobs = [(str(path), corpora["ZL3b"]) for path in paths]
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=min(32, args.workers),
        mp_context=multiprocessing.get_context("spawn"),
    ) as pool:
        controls = list(pool.map(control_job, jobs, chunksize=1))
    controls.sort(key=lambda row: row["file"])
    real_gradient = gradients["ZL3b"]["all"]["observed"]
    gradient_exceed = sum(row["gradient_mean"] >= real_gradient - 1e-12 for row in controls)
    gradient_process_p = (gradient_exceed + 1) / (len(controls) + 1)
    real_stage_process = min(
        discovery["tests"][selected]["t"],
        min(t_stat([
            value for page, value in raw[edition]["stage_pages"][selected].items()
            if folio_number(page) % 2 == 0
        ]) for edition in SOURCES),
    )
    stage_exceed = sum(
        min(row["odd_selected_t"], row["even_selected_t"]) >= real_stage_process - 1e-12
        for row in controls
    )
    stage_process_p = (stage_exceed + 1) / (len(controls) + 1)

    gradient_pass = all(
        gradients[edition][panel]["observed"] > 0
        and gradients[edition][panel]["p"] <= 0.01
        for edition in gradients for panel in ("all", "even", "odd")
    ) and gradient_process_p <= 0.05
    stage_pass = (
        discovery["tests"][selected]["mean"] > 0
        and discovery["selected_family_p"] <= 0.01
        and all(row["observed"] > 0 and row["p"] <= 0.01 for row in held.values())
        and stage_process_p <= 0.05
    )
    decision = (
        "ROOT_LABEL_CONTENT_RESIDUAL_GRADIENT_AND_STAGE_CONFIRMED" if gradient_pass and stage_pass
        else "ROOT_LABEL_CONTENT_RESIDUAL_GRADIENT_CONFIRMED_STAGE_UNRESOLVED" if gradient_pass
        else "ROOT_LABEL_CONTENT_GRADIENT_EXPLAINED_BY_SELECTOR_EDGES"
    )
    runtime = time.perf_counter() - started
    payload = {
        "decision": decision,
        "protocol": {
            "removed": "both endpoints of every visible BOUND_D/Q_BOUND_D/BOUND_E/Q_BOUND_E -> Q_* edge",
            "remaining_controls": "same line-edge exclusion and cross-fitted unit-count + complete role-form residual as parent",
            "primary": "continuous within-line gradient in every reading/parity",
            "stage_discovery": "odd ZL maximum over middle-minus-early and late-minus-middle",
            "stage_holdout": "selected transition fixed on even ZL/IT/RF",
            "process": "each relaid Timm text retrains axis, reselects odd transition, and tests even",
        },
        "source_validation": source,
        "endpoint_counts": {edition: raw[edition]["counts"] for edition in raw},
        "gradients": gradients,
        "stage_discovery": discovery, "stage_held": held,
        "process_tails": {
            "gradient": {"exceedances": gradient_exceed, "controls": len(controls), "p": gradient_process_p},
            "stage": {"real_min_t": real_stage_process, "exceedances": stage_exceed, "controls": len(controls), "p": stage_process_p},
        },
        "controls": controls,
        "meta": {"permutations": args.permutations, "workers": min(32, args.workers), "runtime_seconds": runtime},
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Root-label-content gradient decomposition", "",
        "Both endpoints of every broad D/E-bound -> q-dependent edge are removed before the confirmed line profile is retested.", "",
        "| reading | retained / eligible words | all r / p | even r / p | odd r / p |",
        "|---|---:|---:|---:|---:|",
    ]
    for edition in SOURCES:
        count = raw[edition]["counts"]
        row = gradients[edition]
        lines.append(
            f"| {edition} | {count['retained_words']} / {count['eligible_interior_words']} | "
            f"{row['all']['observed']:+.5f} / {row['all']['p']:.6f} | "
            f"{row['even']['observed']:+.5f} / {row['even']['p']:.6f} | "
            f"{row['odd']['observed']:+.5f} / {row['odd']['p']:.6f} |"
        )
    lines += [
        "", "## Frozen stage localization", "",
        f"Odd ZL selects `{selected}`: mean {discovery['tests'][selected]['mean']:+.5f}, t={discovery['tests'][selected]['t']:+.2f}, family p={discovery['selected_family_p']:.6f}.",
        "Held even: " + "; ".join(
            f"{edition} {held[edition]['observed']:+.5f}/p={held[edition]['p']:.6f}"
            for edition in SOURCES
        ) + ".", "",
        f"**{decision}**", "",
        (
            "The low-to-high content profile persists without known selector/dependent endpoints. The selected stage also transfers, locating a reproducible specificity transition."
            if gradient_pass and stage_pass else
            "The low-to-high content profile persists without known selector/dependent endpoints, but the two-stage split does not transfer cleanly. Treat the rise as distributed, not as a fixed field boundary."
            if gradient_pass else
            "Removing known selector/dependent endpoints removes the profile; the parent result is explained by those local edges."
        ), "",
        f"Process tails: gradient {gradient_exceed}/{len(controls)} (p={gradient_process_p:.6f}); selected-stage full process {stage_exceed}/{len(controls)} (p={stage_process_p:.6f}).", "",
        "No individual root, POS, noun/verb order, or English value is assigned.", "",
        f"Runtime {runtime:.2f} s; 32 workers + RTX 3090, cached transcription only.", "",
    ]
    OUTPUT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(OUTPUT_REPORT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
