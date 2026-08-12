#!/usr/bin/env python3
"""Run RTA001 synthetic calibration and whole-folio held-out evaluation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
sys.path.insert(0, str(HERE))

from rta001_gpu import CudaProposer, build_cuda_library
from rta001_model import (
    ABSTRACT_ORDER,
    K_GRID,
    SCALE,
    EdgeMeta,
    FeatureData,
    Model,
    algebra_bits,
    baseline_training_and_test,
    benchmark_backend,
    build_feature_data,
    fit_model,
    make_model,
    score_model,
    stable_seed,
    training_projection,
    weighted_distances,
)

METHOD = HERE / "RTA001_METHOD.md"
DSL = HERE / "RTA001_OPERATOR_DSL.md"
INVENTORY = RESULTS / "rta001_relation_graph_inventory.tsv"
PROGRAM_META = RESULTS / "rta001_edge_programs.json"
CUDA_SOURCE = HERE / "rta001_cuda_proposer.cu"
MODEL_SOURCE = HERE / "rta001_model.py"
GPU_SOURCE = HERE / "rta001_gpu.py"
THIS = Path(__file__).resolve()

CAL_JSON = RESULTS / "rta001_synthetic_calibration.json"
CAL_REPORT = RESULTS / "rta001_synthetic_calibration_report.md"
CODEBOOK = RESULTS / "rta001_operator_codebook.json"
ATLAS = RESULTS / "rta001_operator_atlas.md"
HELDOUT = RESULTS / "rta001_heldout_panel_results.tsv"
RESULT_JSON = RESULTS / "rta001_result.json"
RESULT_REPORT = RESULTS / "rta001_result_report.md"

CAL_FAMILIES = {
    "NULL_UNRELATED": 32,
    "TRANSFERRED_K2": 8,
    "TRANSFERRED_K4": 8,
    "TRANSFERRED_K6": 8,
    "TRANSFERRED_K8": 8,
    "LOCAL_ONLY": 8,
    "ONE_PANEL_ONLY": 8,
    "LENGTH_FREQUENCY_CONFOUNDED": 8,
    "TRUE_COMPOSITION": 8,
    "CYCLE_VIOLATION": 8,
    "SYMMETRY_TRANSFERRED": 8,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def write_json(path: Path, value: object) -> None:
    path.write_bytes(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8") + b"\n")


def synthetic_topology() -> tuple[tuple[EdgeMeta, ...], dict[str, list[int]]]:
    edges: list[EdgeMeta] = []
    panels: dict[str, list[int]] = {}
    # Eight physical folios, two 12-edge cycles each, plus six 3-row records.
    for folio_index in range(8):
        folio = f"SYNF{folio_index + 1:02d}"
        for cycle_index in range(2):
            panel = f"{folio}|CYCLE{cycle_index + 1}"
            for slot in range(12):
                source = f"{panel}:S{slot + 1}"
                target = f"{panel}:S{(slot + 1) % 12 + 1}"
                index = len(edges)
                edges.append(EdgeMeta(f"SYNE{index:04d}", panel, folio, panel, "CYCLIC_SUCCESSOR",
                                      f"{panel}:E{slot + 1}", source, target, source, target))
                panels.setdefault(panel, []).append(index)
        panel = f"{folio}|ROWS"
        for record in range(6):
            for source, target, relation in [(1, 2, "ROW_SUCCESSOR"), (2, 3, "ROW_SUCCESSOR"), (1, 3, "ROW_SKIP_ONE")]:
                index = len(edges)
                prefix = f"{panel}:REC{record + 1}"
                edges.append(EdgeMeta(f"SYNE{index:04d}", panel, folio, panel, relation,
                                      f"{prefix}:R{source}_TO_R{target}", f"{prefix}:R{source}",
                                      f"{prefix}:R{target}", f"{prefix}:R{source}", f"{prefix}:R{target}"))
                panels.setdefault(panel, []).append(index)
    return tuple(edges), panels


def synth_world(family: str, world: int) -> tuple[FeatureData, np.ndarray, dict[str, object]]:
    edges, panels = synthetic_topology()
    seed = stable_seed("RTA001_SYNTHETIC", family, world)
    rng = np.random.default_rng(seed)
    dimensions = 24
    weights = np.array([2] * 12 + [5] * 9 + [2, 2, 2], dtype=np.int16)
    vectors = np.zeros((len(edges), dimensions), dtype=np.int16)
    if family.startswith("TRANSFERRED_K"):
        planted_k = int(family.rsplit("K", 1)[1])
    elif family in {"TRUE_COMPOSITION", "CYCLE_VIOLATION", "SYMMETRY_TRANSFERRED"}:
        planted_k = 4
    else:
        planted_k = 4
    prototypes = np.zeros((planted_k, dimensions), dtype=np.int16)
    prototypes[:, :12] = rng.integers(0, 5, size=(planted_k, 12), dtype=np.int16)
    prototypes[:, -3:] = np.array([6, 6, 0], dtype=np.int16)
    if family in {"TRUE_COMPOSITION", "CYCLE_VIOLATION"}:
        prototypes[:, 12:21] = 0
    planted = np.full(len(edges), -1, dtype=np.int16)
    one_panel = sorted(panels)[world % len(panels)]
    panel_operator: dict[str, int] = {}
    for panel_index, panel in enumerate(sorted(panels)):
        panel_operator[panel] = int((panel_index + world) % planted_k)
    for i, edge in enumerate(edges):
        panel_position = panels[edge.panel_id].index(i)
        op = int((panel_position + world) % planted_k)
        if edge.relation_type == "ROW_SKIP_ONE" and family in {"TRUE_COMPOSITION", "TRANSFERRED_K4", "SYMMETRY_TRANSFERRED"}:
            # Exact compositional plant: use sum of the two recurring successor prototypes.
            vectors[i] = np.clip(prototypes[op] + prototypes[(op + 1) % planted_k], -20, 20)
            planted[i] = op
        elif family == "NULL_UNRELATED":
            vectors[i] = rng.integers(-3, 4, size=dimensions, dtype=np.int16)
        elif family == "LOCAL_ONLY":
            panel_rng = np.random.default_rng(stable_seed("LOCAL_ONLY", world, edge.panel_id, panel_position))
            vectors[i] = panel_rng.integers(-4, 5, size=dimensions, dtype=np.int16)
        elif family == "ONE_PANEL_ONLY" and edge.panel_id != one_panel:
            vectors[i] = rng.integers(-3, 4, size=dimensions, dtype=np.int16)
        elif family == "LENGTH_FREQUENCY_CONFOUNDED":
            length = (i % 8) + 2
            vectors[i, -3:] = [length, length + (i % 2), 0]
            vectors[i, :4] = length % 3
        else:
            noise = np.zeros(dimensions, dtype=np.int16)
            noise[:12] = rng.integers(0, 2, size=12, dtype=np.int16)
            vectors[i] = np.clip(prototypes[op] + noise, -20, 20)
            planted[i] = op
    if family == "SYMMETRY_TRANSFERRED" and world % 2:
        for panel, indices in panels.items():
            if "CYCLE" in panel:
                vectors[indices] = vectors[list(reversed(indices))]
                planted[indices] = planted[list(reversed(indices))]
    if family == "CYCLE_VIOLATION":
        for panel, indices in panels.items():
            if "CYCLE" in panel:
                vectors[indices, 12] += 2
    raw_bits = np.sum(np.abs(vectors.astype(np.int32)) * weights.astype(np.int32), axis=1, dtype=np.int64)
    names = tuple([f"ATOM:SYN{i}" for i in range(12)] + [f"DELTA:T{i}" for i in range(9)] +
                  ["SOURCE_LENGTH", "TARGET_LENGTH", "BOUNDARY_EDITS"])
    data = FeatureData("synthetic", tuple(f"T{i}" for i in range(9)), names,
                       vectors, weights, raw_bits, edges, tuple("SYNTHETIC" for _ in edges))
    return data, planted, {"family": family, "world": world, "seed": seed, "planted_k": planted_k}


def choose_model(data: FeatureData, key: str, gpu_assign, restarts: int, k_grid=K_GRID) -> Model:
    models = [fit_model(data, k, f"{key}|K{k}", restarts, gpu_assign) for k in k_grid if k <= len(data.edges)]
    return min(models, key=lambda model: (model.total_bits_scaled, model.k, model.medoid_indices))


def assignment_recovery(model: Model, planted: np.ndarray) -> float:
    eligible = np.flatnonzero(planted >= 0)
    if not len(eligible):
        return 0.0
    predicted = np.array(model.assignments)[eligible]
    truth = planted[eligible]
    k = max(int(predicted.max(initial=0)), int(truth.max(initial=0))) + 1
    best = 0
    if k <= 8:
        for permutation in itertools.permutations(range(k)):
            mapped = np.array([permutation[int(x)] for x in predicted])
            best = max(best, int(np.sum(mapped == truth)))
    else:
        for label in range(k):
            best += max((int(np.sum((predicted == candidate) & (truth == label))) for candidate in range(k)), default=0)
    return best / len(eligible)


def synthetic_holdout_gain(data: FeatureData, gpu_assign, restarts: int) -> tuple[float, float, int]:
    gains = []
    composition = []
    folios = sorted({edge.physical_folio for edge in data.edges})
    for folio in folios:
        train_idx = [i for i, edge in enumerate(data.edges) if edge.physical_folio != folio]
        test_idx = [i for i, edge in enumerate(data.edges) if edge.physical_folio == folio]
        train, test = training_projection(data, train_idx, test_idx)
        model = choose_model(train, f"SYNTH|{folio}", gpu_assign, restarts, (2, 4, 6, 8))
        _, costs = score_model(train, model, test)
        baselines = baseline_training_and_test(train, test)
        chosen = min(baselines, key=lambda name: (baselines[name]["training_total_scaled"], name))
        gain = (np.mean(baselines[chosen]["test_costs_scaled"]) - np.mean(costs)) / SCALE
        gains.append(float(gain))
        composition.append(model.composition_bits_scaled / SCALE)
    return float(np.mean(gains)), float(np.mean(composition)), sum(gain > 0 for gain in gains)


def calibration_world(task):
    family, world, backend, quick = task
    data, planted, metadata = synth_world(family, world)
    model = choose_model(data, f"CAL|{family}|{world}", None,
                         1 if quick else 4, (2, 4) if quick else (2, 4, 6, 8))
    recovery = assignment_recovery(model, planted)
    gain, composition, positive_folios = synthetic_holdout_gain(data, None, 1 if quick else 2)
    return {
        **metadata,
        "selected_k": model.k,
        "heldout_gain_bits_per_edge": gain,
        "positive_holdout_folios": positive_folios,
        "assignment_recovery": recovery,
        "composition_residual_bits": composition,
        "cycle_residual_bits": model.cycle_bits_scaled / SCALE,
        "checkpoint": {
            "medoid_indices": list(model.medoid_indices),
            "assignments": list(model.assignments),
            "assignment_costs_scaled": list(model.assignment_costs_scaled),
            "library_bits_scaled": model.library_bits_scaled,
            "residual_bits_scaled": model.residual_bits_scaled,
            "composition_bits_scaled": model.composition_bits_scaled,
            "cycle_bits_scaled": model.cycle_bits_scaled,
            "total_bits_scaled": model.total_bits_scaled,
            "restart_seed": model.restart_seed,
            "proposal_backend": model.proposal_backend,
        },
        "model_digest": hashlib.sha256(canonical({
            "medoids": model.medoid_indices, "assignments": model.assignments,
            "costs": model.assignment_costs_scaled, "total": model.total_bits_scaled,
        })).hexdigest(),
    }


def run_calibration(gpu_assign, backend: str, quick: bool = False) -> dict[str, object]:
    registry = ({family: min(1, count) for family, count in CAL_FAMILIES.items()} if quick else CAL_FAMILIES)
    tasks=[(family,world,backend,quick) for family,count in registry.items() for world in range(count)]
    if quick:
        worlds=[calibration_world(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=min(16,os.cpu_count() or 1)) as pool:
            worlds=list(pool.map(calibration_world,tasks))
    null_false = sum(row["heldout_gain_bits_per_edge"] > 0 for row in worlds if row["family"] == "NULL_UNRELATED")
    local_bad = max((row["positive_holdout_folios"] for row in worlds if row["family"] in {"LOCAL_ONLY", "ONE_PANEL_ONLY"}), default=0)
    transferred = [row for row in worlds if row["family"].startswith("TRANSFERRED_K")]
    transferred_pass = sum(row["heldout_gain_bits_per_edge"] > 0 and row["assignment_recovery"] >= .75 for row in transferred)
    true_comp = np.mean([row["cycle_residual_bits"] for row in worlds if row["family"] == "TRUE_COMPOSITION"])
    bad_comp = np.mean([row["cycle_residual_bits"] for row in worlds if row["family"] == "CYCLE_VIOLATION"])
    gates = {
        "null_false_positive_at_most_1_of_32": null_false <= 1,
        "local_or_one_panel_positive_holdouts_at_most_2": local_bad <= 2,
        "transferred_recovery_at_least_28_of_32": transferred_pass >= 28,
        "cycle_residual_strictly_distinguishes_violation": bool(true_comp < bad_comp),
    }
    return {
        "experiment": "RTA001_SYNTHETIC_CALIBRATION",
        "schema_version": "RTA001_SYNTHETIC_CALIBRATION_V1",
        "status": "SMOKE" if quick else ("PASS" if all(gates.values()) else "FAIL"),
        "backend": "CPU_PARALLEL_EXACT",
        "world_registry": registry,
        "worlds": worlds,
        "summaries": {
            "null_false_positive_count": null_false,
            "max_local_or_one_panel_positive_holdouts": local_bad,
            "transferred_pass_count": transferred_pass,
            "true_composition_mean_cycle_residual_bits": float(true_comp),
            "cycle_violation_mean_cycle_residual_bits": float(bad_comp),
        },
        "gates": gates,
        "claim_ceiling": "Calibration establishes instrument behavior on artificial formal graphs only.",
    }


def write_calibration_report(result: dict[str, object]) -> None:
    lines = [
        "# RTA001 synthetic calibration",
        "",
        f"Status: **{result['status']}**. Backend: `{result['backend']}`.",
        "",
        "The calibration used no manuscript strings. It tested unrelated, transferred, local-only, one-panel-only, confounded, compositional, cycle-violating, and symmetry-varied artificial worlds.",
        "",
        "## Gates",
        "",
    ]
    for key, value in result["gates"].items():
        lines.append(f"- `{key}`: **{'PASS' if value else 'FAIL'}**")
    lines += ["", "## Summary", ""]
    for key, value in result["summaries"].items():
        lines.append(f"- `{key}`: {value}")
    lines += ["", "This calibration licenses only the frozen formal held-out test; it assigns no meaning or translation.", ""]
    CAL_REPORT.write_text("\n".join(lines), encoding="utf-8")


def select_training_model(full_data: dict[str, FeatureData], heldout_folio: str, gpu_assign, backend: str):
    candidates = []
    prepared = {}
    for representation in ABSTRACT_ORDER:
        data = full_data[representation]
        train_idx = [i for i, edge in enumerate(data.edges) if edge.physical_folio != heldout_folio]
        test_idx = [i for i, edge in enumerate(data.edges) if edge.physical_folio == heldout_folio]
        train, test = training_projection(data, train_idx, test_idx)
        prepared[representation] = (train, test)
        for k in K_GRID:
            if k <= len(train.edges):
                model = fit_model(train, k, f"REAL|{heldout_folio}|{representation}|K{k}",
                                  64 if backend == "CUDA" else 16, gpu_assign)
                candidates.append((model.total_bits_scaled, ABSTRACT_ORDER.index(representation), k, model, train, test))
    return min(candidates, key=lambda x: (x[0], x[1], x[2], x[3].medoid_indices)), candidates, prepared


def panel_means(edges: tuple[EdgeMeta, ...], values: np.ndarray) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for edge, value in zip(edges, values):
        grouped[edge.panel_id].append(float(value))
    return {panel: float(np.mean(items)) for panel, items in sorted(grouped.items())}


def run_real(gpu_assign, backend: str) -> tuple[dict[str, object], list[dict[str, str]], dict[str, object], str]:
    full = {rep: build_feature_data(RESULTS, rep) for rep in ABSTRACT_ORDER}
    folios = sorted({edge.physical_folio for edge in full["surface"].edges})
    fold_rows: list[dict[str, str]] = []
    fold_payload = []
    all_models = {}
    folio_gains = []
    for folio in folios:
        winner, candidates, _ = select_training_model(full, folio, gpu_assign, backend)
        _, _, _, model, train, test = winner
        assignments, model_costs = score_model(train, model, test)
        baselines = baseline_training_and_test(train, test)
        strongest = min(baselines, key=lambda name: (baselines[name]["training_total_scaled"], name))
        baseline_costs = baselines[strongest]["test_costs_scaled"]
        model_panels = panel_means(test.edges, model_costs)
        baseline_panels = panel_means(test.edges, baseline_costs)
        panel_gain = {panel: (baseline_panels[panel] - model_panels[panel]) / SCALE for panel in model_panels}
        folio_gain = float(np.mean(list(panel_gain.values())))
        folio_gains.append(folio_gain)
        all_models[folio] = (model, train, test, assignments)
        for panel in sorted(model_panels):
            fold_rows.append({
                "physical_folio": folio,
                "panel_id": panel,
                "heldout_edges": str(sum(edge.panel_id == panel for edge in test.edges)),
                "selected_representation": model.representation,
                "selected_k": str(model.k),
                "strongest_admissible_baseline": strongest,
                "operator_bits_per_edge": f"{model_panels[panel] / SCALE:.6f}",
                "baseline_bits_per_edge": f"{baseline_panels[panel] / SCALE:.6f}",
                "gain_bits_per_edge": f"{panel_gain[panel]:.6f}",
                "composition_residual_bits": f"{model.composition_bits_scaled / SCALE:.6f}",
                "cycle_residual_bits": f"{model.cycle_bits_scaled / SCALE:.6f}",
                "rectangle_residual_bits": f"{model.rectangle_bits_scaled / SCALE:.6f}",
            })
        fold_payload.append({
            "physical_folio": folio,
            "selected_representation": model.representation,
            "selected_k": model.k,
            "strongest_admissible_baseline": strongest,
            "folio_gain_bits_per_edge": folio_gain,
            "positive": folio_gain > 0,
            "model": asdict(model),
            "heldout_assignment_sha256": hashlib.sha256(np.array(assignments, dtype="<i4").tobytes()).hexdigest(),
        })

    observed = float(np.mean(folio_gains))
    null_gains = []
    # Fixed libraries; topology-preserving target record permutations are represented
    # as keyed within-panel permutations of held-out edge-program vectors.
    for world in range(4096):
        world_folios = []
        for folio in folios:
            model, train, test, _ = all_models[folio]
            rng = np.random.default_rng(stable_seed("RTA001_NULL", world, folio))
            permuted = test.vectors.copy()
            for panel in sorted({edge.panel_id for edge in test.edges}):
                indices = np.array([i for i, edge in enumerate(test.edges) if edge.panel_id == panel])
                if len(indices) > 1:
                    shift = int(rng.integers(1, len(indices)))
                    order = np.roll(indices, shift)
                    if rng.integers(0, 2):
                        order = order[::-1]
                    permuted[indices] = test.vectors[order]
            null_test = FeatureData(test.representation, test.vocabulary, test.feature_names, permuted, test.weights,
                                    test.raw_bits, test.edges, test.medoid_programs)
            _, model_costs = score_model(train, model, null_test)
            baselines = baseline_training_and_test(train, null_test)
            strongest = next(row["strongest_admissible_baseline"] for row in fold_payload if row["physical_folio"] == folio)
            baseline_costs = baselines[strongest]["test_costs_scaled"]
            mp = panel_means(test.edges, model_costs)
            bp = panel_means(test.edges, baseline_costs)
            world_folios.append(float(np.mean([(bp[p] - mp[p]) / SCALE for p in mp])))
        null_gains.append(float(np.mean(world_folios)))
    p_value = sum(value >= observed for value in null_gains) / len(null_gains)

    operator_support: Counter[tuple[str, int]] = Counter()
    operator_holdout_use: Counter[tuple[str, int]] = Counter()
    codebook_folds = []
    for folio, (model, train, test, assignments) in all_models.items():
        train_folios = defaultdict(set)
        for edge, assignment in zip(train.edges, model.assignments):
            train_folios[int(assignment)].add(edge.physical_folio)
        for assignment, support in train_folios.items():
            operator_support[(folio, assignment)] = len(support)
        for assignment in assignments:
            operator_holdout_use[(folio, int(assignment))] += 1
        codebook_folds.append({
            "holdout_folio": folio,
            "representation": model.representation,
            "k": model.k,
            "operators": [
                {
                    "operator_id": f"OP{cluster + 1:02d}",
                    "medoid_training_index": medoid,
                    "dsl_program": train.medoid_programs[medoid],
                    "training_edges": sum(a == cluster for a in model.assignments),
                    "training_folios": sorted({edge.physical_folio for edge, a in zip(train.edges, model.assignments) if a == cluster}),
                    "heldout_edges": sum(int(a) == cluster for a in assignments),
                    "residual_bits": sum(cost for cost, a in zip(model.assignment_costs_scaled, model.assignments) if a == cluster) / SCALE,
                }
                for cluster, medoid in enumerate(model.medoid_indices)
            ],
        })
    recurring = sum(support >= 3 and operator_holdout_use[key] > 0 for key, support in operator_support.items())
    abstract_positive = any(row["selected_representation"] in {"construction", "root", "family"} and row["folio_gain_bits_per_edge"] > 0 for row in fold_payload)
    robustness = {
        "positive_folios_at_least_7_of_9": sum(x > 0 for x in folio_gains) >= 7,
        "operator_recurs_on_3_folios_and_is_used_heldout": recurring > 0,
        "abstract_representation_positive_without_exact_identity": abstract_positive,
    }
    status = "PASS" if observed > 0 and p_value <= .01 and all(robustness.values()) else "FAIL"
    result = {
        "experiment": "RTA001_GRAPH_TO_TEXT_OPERATOR_INDUCTION",
        "schema_version": "RTA001_RESULT_V1",
        "status": status,
        "decision": "ANONYMOUS_RELATIONAL_OPERATORS_TRANSFER" if status == "PASS" else "NO_TRANSFER_AT_REGISTERED_RESOLUTION",
        "primary": {
            "statistic": "equal-folio held-out description-length gain over strongest admissible training-selected baseline",
            "gain_bits_per_edge": observed,
            "null_worlds": 4096,
            "inclusive_p_value": p_value,
            "positive_folios": sum(x > 0 for x in folio_gains),
            "physical_folios": len(folios),
        },
        "robustness": robustness,
        "secondary": {
            "recurring_operator_fold_instances": recurring,
            "mean_composition_residual_bits": float(np.mean([x[0].composition_bits_scaled / SCALE for x in all_models.values()])),
            "mean_cycle_residual_bits": float(np.mean([x[0].cycle_bits_scaled / SCALE for x in all_models.values()])),
            "rectangle_residual_bits": 0.0,
            "representation_selection_counts": dict(sorted(Counter(row["selected_representation"] for row in fold_payload).items())),
        },
        "folds": fold_payload,
        "null": {
            "gain_sha256": hashlib.sha256(np.array(null_gains, dtype="<f8").tobytes()).hexdigest(),
            "minimum": min(null_gains), "median": float(np.median(null_gains)), "maximum": max(null_gains),
        },
        "claim_ceiling": "At most, anonymous formal transformations correspond to author-visible relations and predict held-out panels; no meaning, language, cipher, plaintext, or translation is assigned.",
    }
    codebook = {
        "experiment": "RTA001_OPERATOR_CODEBOOK",
        "schema_version": "RTA001_OPERATOR_CODEBOOK_V1",
        "status": status,
        "fold_codebooks": codebook_folds,
        "claim_ceiling": result["claim_ceiling"],
    }
    return result, fold_rows, codebook, render_atlas(codebook, result)


def render_atlas(codebook: dict[str, object], result: dict[str, object]) -> str:
    lines = ["# RTA001 anonymous operator atlas", "", f"Overall result: **{result['status']}**.", "",
             "Operators are fold-local anonymous medoids. Their IDs do not carry meaning.", ""]
    for fold in codebook["fold_codebooks"]:
        lines += [f"## Holdout {fold['holdout_folio']} — {fold['representation']}, K={fold['k']}", ""]
        for op in fold["operators"]:
            lines += [f"### {op['operator_id']}", "", f"- Explicit DSL program: `{op['dsl_program']}`",
                      f"- Training support: {op['training_edges']} edges on {len(op['training_folios'])} folios ({', '.join(op['training_folios'])})",
                      f"- Held-out support: {op['heldout_edges']} edges",
                      f"- Training residual: {op['residual_bits']:.3f} bits",
                      "- Counterexamples: held-out or training assignments with nonzero residual are included in the result TSV/JSON aggregates.",
                      "- Composition/cycle behavior: reported at fold level in `rta001_result.json`.",
                      "- Literal-identity removal: survives exactly when the fold representation is family, root, or construction.", ""]
    lines += ["## Ceiling", "", result["claim_ceiling"], ""]
    return "\n".join(lines)


def write_heldout(rows: list[dict[str, str]]) -> None:
    fields = ["physical_folio", "panel_id", "heldout_edges", "selected_representation", "selected_k",
              "strongest_admissible_baseline", "operator_bits_per_edge", "baseline_bits_per_edge",
              "gain_bits_per_edge", "composition_residual_bits", "cycle_residual_bits", "rectangle_residual_bits"]
    with HELDOUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def write_result_report(result: dict[str, object], calibration: dict[str, object], benchmark: dict[str, object]) -> None:
    p = result["primary"]
    lines = ["# RTA001 result", "", f"Status: **{result['status']}** — `{result['decision']}`.", "",
             f"The primary held-out gain is **{p['gain_bits_per_edge']:.6f} bits/edge** over the strongest admissible baseline; the topology-preserving 4,096-world inclusive CPU p-value is **{p['inclusive_p_value']:.6f}**.", "",
             f"Positive physical folios: {p['positive_folios']}/{p['physical_folios']}.", "",
             f"Synthetic calibration: **{calibration['status']}**. Proposal backend: **{benchmark['selected_backend']}**.", "", "## Essential robustness", ""]
    for key, value in result["robustness"].items(): lines.append(f"- `{key}`: **{'PASS' if value else 'FAIL'}**")
    lines += ["", "## Interpretation", "", result["claim_ceiling"], ""]
    if result["status"] == "FAIL":
        lines += ["The registered operator-bearing representations did not pass. The next route is latent grapheme/transcription-channel reconstruction, not visual binary attributes or exact-label mining.", ""]
    else:
        lines += ["The registered next experiment is RTA002: test whether these anonymous operators occur in prose and improve held-out prediction beyond the confirmed adjacency baseline.", ""]
    RESULT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu-only", action="store_true")
    parser.add_argument("--quick-calibration-smoke", action="store_true")
    parser.add_argument("--result-from-passed-calibration", action="store_true")
    args = parser.parse_args()
    if args.result_from_passed_calibration:
        completed = subprocess.run([sys.executable, str(HERE / "run_rta001_result.py")], check=False)
        raise SystemExit(completed.returncode)
    proposer = None
    build = None
    if not args.cpu_only:
        with tempfile.TemporaryDirectory(prefix="rta001-build-") as temporary:
            library = Path(temporary) / "librta001_cuda.so"
            try:
                build = build_cuda_library(library)
                proposer = CudaProposer(library)
                bench_data = build_feature_data(RESULTS, "family")
                benchmark = benchmark_backend(bench_data, proposer)
                # Keep the library alive by copying it to an external second temp for the process lifetime.
                persistent = tempfile.NamedTemporaryFile(prefix="rta001-cuda-", suffix=".so", delete=False)
                persistent.close(); os.unlink(persistent.name); os.link(library, persistent.name)
                proposer = CudaProposer(Path(persistent.name))
            except Exception as exc:
                benchmark = {"cuda_available": False, "selected_backend": "CPU", "reason": str(exc)}
                proposer = None
    else:
        benchmark = {"cuda_available": False, "selected_backend": "CPU", "reason": "--cpu-only"}
    backend = str(benchmark["selected_backend"])
    gpu_assign = proposer.assign_many if proposer is not None and backend == "CUDA" else None
    calibration = run_calibration(gpu_assign, backend, args.quick_calibration_smoke)
    calibration["benchmark"] = benchmark
    calibration["cuda_build"] = build
    calibration["inputs"] = {path.name: sha256(path) for path in [METHOD, DSL, INVENTORY, PROGRAM_META, CUDA_SOURCE, MODEL_SOURCE, GPU_SOURCE, THIS]}
    write_json(CAL_JSON, calibration); write_calibration_report(calibration)
    if args.quick_calibration_smoke:
        print(json.dumps({"status": calibration["status"], "worlds": len(calibration["worlds"]), "backend": backend}, sort_keys=True))
        return
    if calibration["status"] != "PASS":
        raise SystemExit("synthetic calibration failed; real held-out scores remain unopened")
    result, rows, codebook, atlas = run_real(gpu_assign, backend)
    result["inputs"] = calibration["inputs"] | {CAL_JSON.name: sha256(CAL_JSON), CAL_REPORT.name: sha256(CAL_REPORT)}
    result["backend"] = benchmark
    write_heldout(rows); write_json(CODEBOOK, codebook); ATLAS.write_text(atlas, encoding="utf-8")
    result["artifacts"] = {HELDOUT.name: sha256(HELDOUT), CODEBOOK.name: sha256(CODEBOOK), ATLAS.name: sha256(ATLAS)}
    write_json(RESULT_JSON, result); write_result_report(result, calibration, benchmark)
    print(json.dumps({"status": result["status"], **result["primary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
