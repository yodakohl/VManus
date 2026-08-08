#!/usr/bin/env python3
"""Held atlas of exact visible-space role transitions.

The earlier internal-utterance runner printed exact role pairs after selecting
them on the complete ZL corpus.  Those rows were useful clues, but were not a
held family.  This runner starts over with the complete fixed 14 x 14 role
family.  Odd ZL folios discover, even ZL folios confirm, IT/RF are reading
sensitivity panels, and complete words are permuted analytically inside their
physical line.  A second required view repeats the calculation only within
fixed early/middle/late thirds, preventing a broad position gradient from
masquerading as local adjacency.

No root, surface word, semantic tag, or European part of speech enters the
test.  Positive transitions can extend the abstract interpreter; depleted
transitions are exported only as ordering constraints.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import math
import multiprocessing
import time
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable, Sequence

import cupy as cp
import numpy as np

from common import RESULTS, Row, folio_number
from run_bidirectional_context_controls import TIMM_DIR, relayout_rows, timm_tokens
from run_d_dependent_core_link import control_paths
from run_detached_suffix_collapsed_order import collapse_rows
from run_internal_utterance_grammar import SPACE_RULES, WordNode, line_nodes
from run_typology_neutral_structure import SOURCES, prose_rows


SEED = 41_084_196
BASE_ROLES = ("BARE", "BOUND_D", "BOUND_E", "REL_I", "FREE_L", "FREE_R", "FREE_A")
ROLES = BASE_ROLES + tuple("Q_" + role for role in BASE_ROLES)
PAIRS = tuple((left, right) for left in ROLES for right in ROLES)
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
ACTIVE_RULES = ("D_SELECT_Q", "REL_TO_FREE", "L_SERIAL")
PRIOR_EXACT_RULES = {
    ("BOUND_E", "Q_BARE"): "E_SELECT_Q",
    ("BOUND_E", "Q_BOUND_E"): "E_SELECT_Q",
}

MIN_DISCOVERY_OBSERVED = 25
MIN_DISCOVERY_EXPECTED = 12.0
MIN_DISCOVERY_PAGES = 8
MIN_HELD_OBSERVED = 20
MIN_HELD_EXPECTED = 10.0
MIN_HELD_PAGES = 8
MIN_DEPLETION_DISCOVERY_EXPECTED = 25.0
MIN_DEPLETION_HELD_EXPECTED = 20.0
ALPHA = 0.05
POSITION_ZONES = 3
PLANTED_PAIR = ("BOUND_E", "BARE")

OUTPUT_JSON = RESULTS / "exact_role_transition_atlas_results.json"
OUTPUT_REPORT = RESULTS / "exact_role_transition_atlas_report.md"
OUTPUT_PAIRS = RESULTS / "exact_role_transition_atlas_pairs.tsv"
OUTPUT_CONTROLS = RESULTS / "exact_role_transition_atlas_controls.tsv"
OUTPUT_CONFIRMED = RESULTS / "exact_role_transition_atlas_confirmed.tsv"


CONTROL_TEMPLATE: list[Row] = []
CONTROL_COLLAPSE_MODE = "ORIGINAL"


def existing_rule(left: str, right: str) -> str:
    for name in ACTIVE_RULES:
        if SPACE_RULES[name](left, right):
            return name
    return PRIOR_EXACT_RULES.get((left, right), "")


def known_depletion_context(left: str, right: str) -> str:
    if left in {"FREE_A", "Q_FREE_A"}:
        return "FREE_A_CLOSE"
    if left in {"BOUND_D", "Q_BOUND_D"} and not right.startswith("Q_"):
        return "D_SELECT_Q_COMPLEMENT"
    return ""


def groups_for_nodes(nodes: Sequence[WordNode], zones: int) -> Iterable[Sequence[WordNode]]:
    if zones == 1:
        if len(nodes) >= 2:
            yield nodes
        return
    count = len(nodes)
    for zone in range(zones):
        group = [
            node for index, node in enumerate(nodes)
            if min(zones - 1, zones * index // count) == zone
        ]
        if len(group) >= 2:
            yield group


def add_group_counts(
    nodes: Sequence[WordNode], observed: np.ndarray, expected: np.ndarray, page_index: int,
) -> None:
    count = len(nodes)
    observed_pairs = Counter(
        (left.last_role, right.first_role) for left, right in zip(nodes, nodes[1:])
    )
    for pair, value in observed_pairs.items():
        observed[PAIR_INDEX[pair], page_index] += value

    left_counts = Counter(node.last_role for node in nodes)
    right_counts = Counter(node.first_role for node in nodes)
    self_counts = Counter((node.last_role, node.first_role) for node in nodes)
    for left, left_count in left_counts.items():
        for right, right_count in right_counts.items():
            compatible = left_count * right_count - self_counts[left, right]
            expected[PAIR_INDEX[left, right], page_index] += compatible / count


def panel(rows: Sequence[Row], parity: int, zones: int = 1) -> dict[str, Any]:
    selected = [row for row in rows if folio_number(row.page) % 2 == parity]
    pages = sorted({row.page for row in selected})
    page_index = {page: index for index, page in enumerate(pages)}
    observed = np.zeros((len(PAIRS), len(pages)), dtype=np.float64)
    expected = np.zeros_like(observed)
    lines = 0
    boundaries = 0
    for row in selected:
        nodes = line_nodes(row)
        if len(nodes) < 2:
            continue
        lines += 1
        for group in groups_for_nodes(nodes, zones):
            boundaries += len(group) - 1
            add_group_counts(group, observed, expected, page_index[row.page])
    residual = (observed - expected) / np.sqrt(expected + 1.0)
    return {
        "pages": pages,
        "lines": lines,
        "boundaries": boundaries,
        "observed": observed,
        "expected": expected,
        "residual": residual,
    }


def t_scores(values: np.ndarray) -> np.ndarray:
    if values.shape[1] < 2:
        return np.zeros(values.shape[0], dtype=np.float64)
    means = values.mean(axis=1)
    standard = values.std(axis=1, ddof=1)
    return np.divide(
        means,
        standard / math.sqrt(values.shape[1]),
        out=np.zeros_like(means),
        where=standard > 0,
    )


def metrics(task: dict[str, Any], pair_index: int) -> dict[str, Any]:
    observed = task["observed"][pair_index]
    expected = task["expected"][pair_index]
    total_observed = float(observed.sum())
    total_expected = float(expected.sum())
    return {
        "observed": int(round(total_observed)),
        "expected": total_expected,
        "ratio": total_observed / total_expected if total_expected else None,
        "active_pages": int(np.count_nonzero((observed + expected) > 0)),
        "t": float(t_scores(task["residual"][[pair_index]])[0]),
    }


def enrichment_eligible(task: dict[str, Any], held: bool = False) -> np.ndarray:
    observed = task["observed"].sum(axis=1)
    expected = task["expected"].sum(axis=1)
    active = np.count_nonzero((task["observed"] + task["expected"]) > 0, axis=1)
    if held:
        return (
            (observed >= MIN_HELD_OBSERVED)
            & (expected >= MIN_HELD_EXPECTED)
            & (active >= MIN_HELD_PAGES)
        )
    return (
        (observed >= MIN_DISCOVERY_OBSERVED)
        & (expected >= MIN_DISCOVERY_EXPECTED)
        & (active >= MIN_DISCOVERY_PAGES)
    )


def depletion_eligible(task: dict[str, Any], held: bool = False) -> np.ndarray:
    expected = task["expected"].sum(axis=1)
    active = np.count_nonzero((task["observed"] + task["expected"]) > 0, axis=1)
    threshold = MIN_DEPLETION_HELD_EXPECTED if held else MIN_DEPLETION_DISCOVERY_EXPECTED
    page_threshold = MIN_HELD_PAGES if held else MIN_DISCOVERY_PAGES
    return (expected >= threshold) & (active >= page_threshold)


def max_t_adjusted(
    residual: np.ndarray,
    indices: Sequence[int],
    repeats: int,
    seed: int,
    direction: int = 1,
) -> dict[str, Any]:
    """Shared-page sign-flip max-t adjustment for a frozen pair family."""
    index_array = np.asarray(indices, dtype=np.int32)
    if not len(index_array):
        return {"indices": [], "observed_t": [], "adjusted_p": [], "family_p": None}
    values = direction * residual[index_array].astype(np.float32)
    observed = t_scores(values.astype(np.float64))
    gpu = cp.asarray(values)
    observed_gpu = cp.asarray(observed.astype(np.float32))
    sum_squares = cp.sum(gpu * gpu, axis=1)
    rng = cp.random.RandomState(seed)
    exceed = cp.zeros(len(index_array), dtype=cp.int64)
    family_exceed = 0
    null_maxima: list[np.ndarray] = []
    done = 0
    batch = min(8192, repeats)
    n_pages = values.shape[1]
    while done < repeats:
        size = min(batch, repeats - done)
        signs = rng.randint(0, 2, size=(size, n_pages), dtype=cp.int8)
        signs = signs.astype(cp.float32) * 2.0 - 1.0
        means = (signs @ gpu.T) / n_pages
        variance = (sum_squares[None, :] - n_pages * means * means) / max(n_pages - 1, 1)
        null_t = means / cp.sqrt(cp.maximum(variance, 1e-12) / n_pages)
        maxima = cp.max(null_t, axis=1)
        exceed += cp.sum(maxima[:, None] >= observed_gpu[None, :], axis=0)
        family_exceed += int(cp.count_nonzero(maxima >= float(observed.max())).get())
        null_maxima.append(cp.asnumpy(maxima))
        done += size
    maxima_np = np.concatenate(null_maxima)
    adjusted = (cp.asnumpy(exceed) + 1) / (repeats + 1)
    return {
        "indices": index_array.tolist(),
        "observed_t": observed.tolist(),
        "adjusted_p": adjusted.tolist(),
        "family_p": (family_exceed + 1) / (repeats + 1),
        "critical_95": float(np.quantile(maxima_np, 0.95)),
        "null_maximum_mean": float(maxima_np.mean()),
        "repeats": repeats,
        "direction": "enrichment" if direction > 0 else "depletion",
    }


def aggregate_rule_residual(task: dict[str, Any], pair_indices: Sequence[int]) -> np.ndarray:
    observed = task["observed"][list(pair_indices)].sum(axis=0)
    expected = task["expected"][list(pair_indices)].sum(axis=0)
    return (observed - expected) / np.sqrt(expected + 1.0)


def aggregate_rule_metrics(task: dict[str, Any], pair_indices: Sequence[int]) -> dict[str, Any]:
    observed = task["observed"][list(pair_indices)].sum(axis=0)
    expected = task["expected"][list(pair_indices)].sum(axis=0)
    residual = (observed - expected) / np.sqrt(expected + 1.0)
    total_observed = float(observed.sum())
    total_expected = float(expected.sum())
    return {
        "observed": int(round(total_observed)),
        "expected": total_expected,
        "ratio": total_observed / total_expected if total_expected else None,
        "t": float(t_scores(residual[None, :])[0]),
        "pages": len(residual),
    }


def p_lookup(result: dict[str, Any]) -> dict[int, float]:
    return dict(zip(result["indices"], result["adjusted_p"]))


def all_panels(corpora: dict[str, list[Row]], zones: int) -> dict[str, dict[str, dict[str, Any]]]:
    return {
        edition: {
            "odd": panel(rows, 1, zones),
            "even": panel(rows, 0, zones),
        }
        for edition, rows in corpora.items()
    }


def support_pass(task: dict[str, Any], pair_index: int, held: bool, depletion: bool = False) -> bool:
    eligible = depletion_eligible(task, held) if depletion else enrichment_eligible(task, held)
    return bool(eligible[pair_index])


def direction_and_support(
    panels: dict[str, dict[str, dict[str, Any]]], pair_index: int, direction: int,
    depletion: bool = False,
) -> tuple[bool, bool]:
    direction_ok = True
    support_ok = True
    for edition in SOURCES:
        for split in ("odd", "even"):
            task = panels[edition][split]
            direction_ok &= direction * metrics(task, pair_index)["t"] > 0
            support_ok &= support_pass(task, pair_index, split == "even", depletion)
    return bool(direction_ok), bool(support_ok)


def plant_rows(rows: Sequence[Row], target: tuple[str, str]) -> tuple[list[Row], int]:
    """Reorder disjoint source/target word pairs while preserving each line inventory."""
    output: list[Row] = []
    planted_edges = 0
    for row in rows:
        nodes = line_nodes(row)
        if len(nodes) != len(row.words) or len(nodes) < 2:
            output.append(row)
            continue
        sources = [index for index, node in enumerate(nodes) if node.last_role == target[0]]
        targets = [index for index, node in enumerate(nodes) if node.first_role == target[1]]
        used: set[int] = set()
        blocks: list[list[int]] = []
        for source in sources:
            if source in used:
                continue
            chosen = next((candidate for candidate in targets if candidate not in used and candidate != source), None)
            if chosen is None:
                continue
            blocks.append([source, chosen])
            used.update((source, chosen))
            planted_edges += 1
        blocks.extend([[index] for index in range(len(nodes)) if index not in used])
        order = [index for block in blocks for index in block]
        output.append(replace(row, words=[row.words[index] for index in order]))
    return output, planted_edges


def strongest_novel_pipeline(rows: Sequence[Row]) -> dict[str, Any]:
    discovery = panel(rows, 1, 1)
    held = panel(rows, 0, 1)
    eligible = enrichment_eligible(discovery)
    novel_indices = [
        index for index, (left, right) in enumerate(PAIRS)
        if eligible[index] and not existing_rule(left, right)
    ]
    if not novel_indices:
        return {"pair": "", "discovery_t": None, "held_t": None, "pipeline_t": None}
    discovery_t = t_scores(discovery["residual"])
    selected = max(novel_indices, key=lambda index: discovery_t[index])
    held_task = metrics(held, selected)
    discovery_task = metrics(discovery, selected)
    held_support = support_pass(held, selected, True)
    pipeline = min(discovery_task["t"], held_task["t"]) if held_support else -math.inf
    return {
        "pair": f"{PAIRS[selected][0]}>{PAIRS[selected][1]}",
        "pair_index": selected,
        "discovery_t": discovery_task["t"],
        "held_t": held_task["t"],
        "pipeline_t": pipeline,
        "discovery_observed": discovery_task["observed"],
        "held_observed": held_task["observed"],
        "held_support": held_support,
    }


def control_pipeline(path_text: str) -> dict[str, Any]:
    rows = relayout_rows(CONTROL_TEMPLATE, timm_tokens(Path(path_text)))
    if CONTROL_COLLAPSE_MODE != "ORIGINAL":
        rows, _events, _inventory = collapse_rows(rows, CONTROL_COLLAPSE_MODE)
    return {"file": Path(path_text).name, **strongest_novel_pipeline(rows)}


def export_tsv(
    panels: dict[str, dict[str, dict[str, Any]]],
    zone_panels: dict[str, dict[str, dict[str, Any]]],
    positive: dict[str, Any],
    negative: dict[str, Any],
    confirmed_positive: set[int],
    confirmed_negative: set[int],
) -> None:
    disc_positive_p = p_lookup(positive["discovery"])
    held_positive_p = p_lookup(positive["held"])
    disc_zone_positive_p = p_lookup(positive["zone_discovery"])
    held_zone_positive_p = p_lookup(positive["zone_held"])
    disc_negative_p = p_lookup(negative["discovery"])
    held_negative_p = p_lookup(negative["held"])
    fields = [
        "left_role", "right_role", "existing_rule", "known_depletion_context",
        "discovery_adjusted_p", "held_adjusted_p", "zone_discovery_adjusted_p",
        "zone_held_adjusted_p", "depletion_discovery_adjusted_p",
        "depletion_held_adjusted_p", "confirmed_enrichment", "confirmed_depletion",
    ]
    for edition in SOURCES:
        for split in ("odd", "even"):
            fields.extend((
                f"{edition}_{split}_observed", f"{edition}_{split}_expected",
                f"{edition}_{split}_ratio", f"{edition}_{split}_t",
                f"{edition}_{split}_zone_t",
            ))
    rows = []
    for index, (left, right) in enumerate(PAIRS):
        row: dict[str, Any] = {
            "left_role": left,
            "right_role": right,
            "existing_rule": existing_rule(left, right),
            "known_depletion_context": known_depletion_context(left, right),
            "discovery_adjusted_p": disc_positive_p.get(index, ""),
            "held_adjusted_p": held_positive_p.get(index, ""),
            "zone_discovery_adjusted_p": disc_zone_positive_p.get(index, ""),
            "zone_held_adjusted_p": held_zone_positive_p.get(index, ""),
            "depletion_discovery_adjusted_p": disc_negative_p.get(index, ""),
            "depletion_held_adjusted_p": held_negative_p.get(index, ""),
            "confirmed_enrichment": int(index in confirmed_positive),
            "confirmed_depletion": int(index in confirmed_negative),
        }
        for edition in SOURCES:
            for split in ("odd", "even"):
                task = metrics(panels[edition][split], index)
                prefix = f"{edition}_{split}"
                row[f"{prefix}_observed"] = task["observed"]
                row[f"{prefix}_expected"] = f"{task['expected']:.6f}"
                row[f"{prefix}_ratio"] = "" if task["ratio"] is None else f"{task['ratio']:.6f}"
                row[f"{prefix}_t"] = f"{task['t']:.6f}"
                row[f"{prefix}_zone_t"] = f"{metrics(zone_panels[edition][split], index)['t']:.6f}"
        rows.append(row)
    with OUTPUT_PAIRS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def pair_summary(
    index: int,
    panels: dict[str, dict[str, dict[str, Any]]],
    zone_panels: dict[str, dict[str, dict[str, Any]]],
    p_disc: dict[int, float],
    p_held: dict[int, float],
    p_zone_disc: dict[int, float],
    p_zone_held: dict[int, float],
    passed: bool,
) -> dict[str, Any]:
    left, right = PAIRS[index]
    output: dict[str, Any] = {
        "pair_index": index,
        "left": left,
        "right": right,
        "pair": f"{left}>{right}",
        "existing_rule": existing_rule(left, right),
        "known_depletion_context": known_depletion_context(left, right),
        "discovery_adjusted_p": p_disc.get(index),
        "held_adjusted_p": p_held.get(index),
        "zone_discovery_adjusted_p": p_zone_disc.get(index),
        "zone_held_adjusted_p": p_zone_held.get(index),
        "passed": passed,
        "panels": {},
    }
    for edition in SOURCES:
        output["panels"][edition] = {}
        for split in ("odd", "even"):
            output["panels"][edition][split] = {
                **metrics(panels[edition][split], index),
                "zone": metrics(zone_panels[edition][split], index),
            }
    return output


def write_confirmed(rows: list[dict[str, Any]]) -> None:
    fields = ["direction", "left_role", "right_role", "scope", "status"]
    with OUTPUT_CONFIRMED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def report(payload: dict[str, Any]) -> str:
    collapse_mode = payload["protocol"].get("collapse_mode", "ORIGINAL")
    lines = [
        "# Exact role-transition atlas",
        "",
        f"**{payload['status']}**",
        "",
        f"Representation: **{collapse_mode}**. All 196 exact unit-boundary last-role -> first-role pairs competed. Odd ZL folios discovered candidates; even ZL folios were untouched confirmation. The analytic null permutes complete units within each physical line. A required three-zone view repeats the test within fixed early/middle/late thirds, so broad writing position cannot by itself create a pass.",
        "",
        f"Discovery enrichment family: {payload['families']['positive']['discovery']['eligible_pairs']} supported pairs; GPU max-t critical value {payload['families']['positive']['discovery']['critical_95']:.3f} over {payload['protocol']['permutations']:,} shared page sign flips.",
        "",
        "## Position-controlled audit of the existing aggregate rules",
        "",
        "| rule | odd ZL whole t | even ZL whole t | odd/even three-zone adjusted p | all six zone directions | current reading |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in payload["existing_rule_audit"]:
        lines.append(
            f"| `{row['rule']}` | {row['panels']['ZL3b']['odd']['whole']['t']:+.2f} | "
            f"{row['panels']['ZL3b']['even']['whole']['t']:+.2f} | "
            f"{row['zone_discovery_adjusted_p']:.6g}/{row['zone_held_adjusted_p']:.6g} | "
            f"{'yes' if row['all_six_zone_positive'] else 'no'} | {row['status']} |"
        )
    lines += [
        "",
        "The three-zone audit is a direct correction for the independently confirmed horizontal writing-position gradient. A rule that fails here may still describe where forms occur, but it is not retained as a local adjacency edge.",
        "",
        "## Held enriched transitions",
        "",
        "| pair | old rule | odd ZL obs/exp, t | even ZL obs/exp, t | adjusted p odd/even | zone p odd/even | six-panel direction | decision |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    positive_rows = payload["positive_candidates"]
    if not positive_rows:
        lines.append("| none | | | | | | | no discovery pair survived |")
    for row in positive_rows:
        odd = row["panels"]["ZL3b"]["odd"]
        even = row["panels"]["ZL3b"]["even"]
        lines.append(
            f"| `{row['pair']}` | {row['existing_rule'] or 'NEW'} | "
            f"{odd['observed']}/{odd['expected']:.1f}, {odd['t']:+.2f} | "
            f"{even['observed']}/{even['expected']:.1f}, {even['t']:+.2f} | "
            f"{row['discovery_adjusted_p']:.6g}/{row['held_adjusted_p']:.6g} | "
            f"{row['zone_discovery_adjusted_p']:.6g}/{row['zone_held_adjusted_p']:.6g} | "
            f"{'yes' if row['direction_pass'] else 'no'} | {'PASS' if row['passed'] else 'FAIL'} |"
        )
    lines += [
        "",
        "## Held depleted transitions",
        "",
        "These are constraints, not active parse edges. Closure/complement effects remain labeled as already explained.",
        "",
        "| pair | context | odd/even ZL t | adjusted p odd/even | decision |",
        "|---|---|---:|---:|---|",
    ]
    negative_rows = payload["negative_candidates"]
    if not negative_rows:
        lines.append("| none | | | | no held depletion |")
    for row in negative_rows:
        odd = row["panels"]["ZL3b"]["odd"]
        even = row["panels"]["ZL3b"]["even"]
        lines.append(
            f"| `{row['pair']}` | {row['known_depletion_context'] or 'new constraint'} | "
            f"{odd['t']:+.2f}/{even['t']:+.2f} | "
            f"{row['discovery_adjusted_p']:.6g}/{row['held_adjusted_p']:.6g} | "
            f"{'PASS' if row['passed'] else 'FAIL'} |"
        )
    tail = payload["generated_control_tail"]
    if tail["p"] is None:
        control_sentence = "Generated-process calibration was skipped for this diagnostic run."
    else:
        control_sentence = (
            f"Each generated text selected its own strongest novel odd-folio pair before its even score was read. "
            f"{tail['exceedances']}/{tail['controls']} controls meet both real thresholds "
            f"(empirical p={tail['p']:.6g})."
        )
    lines += [
        "",
        "## Calibration and scope",
        "",
        f"The strongest real novel discovery is `{payload['real_novel_pipeline']['pair']}` with odd/even t={payload['real_novel_pipeline']['discovery_t']:+.3f}/{payload['real_novel_pipeline']['held_t']:+.3f}. {control_sentence}",
        f"The planted `{payload['planted']['pair']}` adjacency contributes {payload['planted']['planted_edges']:,} inventory-preserving edges and is recovered at adjusted odd/even p={payload['planted']['discovery_adjusted_p']:.6g}/{payload['planted']['held_adjusted_p']:.6g}.",
        "",
        "A positive pass establishes only a local formal-state transition. It does not identify a verb, noun, case, sound, or plaintext language. Confirmed positive pairs may be added to the abstract interpreter; depleted pairs remain ordering constraints.",
        "",
        f"Runtime: {payload['elapsed_seconds']:.3f} seconds; cached transcription only, no image decoding.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    global OUTPUT_JSON, OUTPUT_REPORT, OUTPUT_PAIRS, OUTPUT_CONTROLS, OUTPUT_CONFIRMED
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--permutations", type=int, default=200_000)
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--control-dir", type=Path, default=Path("/tmp/timm-extended.QbsuS8"))
    parser.add_argument("--skip-controls", action="store_true")
    parser.add_argument(
        "--collapse-mode",
        choices=("ORIGINAL", "CORE_ISOLATED", "CORE_LEFT_MAX", "CORE_RIGHT_MAX", "ALL4_ISOLATED"),
        default="ORIGINAL",
        help="preprocess visible groups with the registered detached-suffix segmentation",
    )
    args = parser.parse_args()
    started = time.perf_counter()
    RESULTS.mkdir(parents=True, exist_ok=True)

    if args.collapse_mode != "ORIGINAL":
        prefix = f"{args.collapse_mode.lower()}_exact_role_transition_atlas"
        OUTPUT_JSON = RESULTS / f"{prefix}_results.json"
        OUTPUT_REPORT = RESULTS / f"{prefix}_report.md"
        OUTPUT_PAIRS = RESULTS / f"{prefix}_pairs.tsv"
        OUTPUT_CONTROLS = RESULTS / f"{prefix}_controls.tsv"
        OUTPUT_CONFIRMED = RESULTS / f"{prefix}_confirmed.tsv"

    raw_corpora = {edition: prose_rows(path) for edition, path in SOURCES.items()}
    collapse_inventory: dict[str, Any] = {}
    if args.collapse_mode == "ORIGINAL":
        corpora = raw_corpora
    else:
        corpora = {}
        for edition, rows in raw_corpora.items():
            collapsed, events, inventory = collapse_rows(rows, args.collapse_mode)
            corpora[edition] = collapsed
            collapse_inventory[edition] = {
                **inventory,
                "collapsed_events": len(events),
                "tokens_before": sum(len(row.words) for row in rows),
                "tokens_after": sum(len(row.words) for row in collapsed),
            }
    panels = all_panels(corpora, 1)
    zone_panels = all_panels(corpora, POSITION_ZONES)
    discovery = panels["ZL3b"]["odd"]
    held = panels["ZL3b"]["even"]

    rule_pair_indices = {
        name: [
            index for index, (left, right) in enumerate(PAIRS)
            if SPACE_RULES[name](left, right)
        ]
        for name in ACTIVE_RULES
    }
    rule_zone_discovery_values = np.stack([
        aggregate_rule_residual(zone_panels["ZL3b"]["odd"], rule_pair_indices[name])
        for name in ACTIVE_RULES
    ])
    rule_zone_held_values = np.stack([
        aggregate_rule_residual(zone_panels["ZL3b"]["even"], rule_pair_indices[name])
        for name in ACTIVE_RULES
    ])
    rule_zone_discovery_test = max_t_adjusted(
        rule_zone_discovery_values, range(len(ACTIVE_RULES)),
        args.permutations, SEED + 11, 1,
    )
    rule_zone_held_test = max_t_adjusted(
        rule_zone_held_values, range(len(ACTIVE_RULES)),
        args.permutations, SEED + 12, 1,
    )
    rule_zone_discovery_p = p_lookup(rule_zone_discovery_test)
    rule_zone_held_p = p_lookup(rule_zone_held_test)
    existing_rule_audit = []
    for rule_index, name in enumerate(ACTIVE_RULES):
        pair_indices = rule_pair_indices[name]
        panel_rows: dict[str, Any] = {}
        all_six_zone_positive = True
        for edition in SOURCES:
            panel_rows[edition] = {}
            for split in ("odd", "even"):
                whole_metrics = aggregate_rule_metrics(panels[edition][split], pair_indices)
                zone_metrics = aggregate_rule_metrics(zone_panels[edition][split], pair_indices)
                all_six_zone_positive &= zone_metrics["t"] > 0
                panel_rows[edition][split] = {"whole": whole_metrics, "zone": zone_metrics}
        position_local = bool(
            rule_zone_discovery_p[rule_index] <= ALPHA
            and rule_zone_held_p[rule_index] <= ALPHA
            and all_six_zone_positive
        )
        existing_rule_audit.append({
            "rule": name,
            "exact_cells": len(pair_indices),
            "zone_discovery_adjusted_p": rule_zone_discovery_p[rule_index],
            "zone_held_adjusted_p": rule_zone_held_p[rule_index],
            "all_six_zone_positive": bool(all_six_zone_positive),
            "status": "POSITION_LOCAL_RETAINED" if position_local else "POSITIONAL_ONLY_DOWNGRADED",
            "panels": panel_rows,
        })

    positive_indices = np.flatnonzero(enrichment_eligible(discovery)).tolist()
    positive_discovery = max_t_adjusted(
        discovery["residual"], positive_indices, args.permutations, SEED + 1, 1,
    )
    positive_discovery_p = p_lookup(positive_discovery)
    selected_positive = [
        index for index in positive_indices
        if positive_discovery_p[index] <= ALPHA and metrics(discovery, index)["t"] > 0
    ]
    positive_held = max_t_adjusted(
        held["residual"], selected_positive, args.permutations, SEED + 2, 1,
    )
    positive_zone_discovery = max_t_adjusted(
        zone_panels["ZL3b"]["odd"]["residual"], selected_positive,
        args.permutations, SEED + 3, 1,
    )
    positive_zone_held = max_t_adjusted(
        zone_panels["ZL3b"]["even"]["residual"], selected_positive,
        args.permutations, SEED + 4, 1,
    )
    positive_held_p = p_lookup(positive_held)
    positive_zone_discovery_p = p_lookup(positive_zone_discovery)
    positive_zone_held_p = p_lookup(positive_zone_held)

    negative_indices = np.flatnonzero(depletion_eligible(discovery)).tolist()
    negative_discovery = max_t_adjusted(
        discovery["residual"], negative_indices, args.permutations, SEED + 5, -1,
    )
    negative_discovery_p = p_lookup(negative_discovery)
    selected_negative = [
        index for index in negative_indices
        if negative_discovery_p[index] <= ALPHA and metrics(discovery, index)["t"] < 0
    ]
    negative_held = max_t_adjusted(
        held["residual"], selected_negative, args.permutations, SEED + 6, -1,
    )
    negative_zone_discovery = max_t_adjusted(
        zone_panels["ZL3b"]["odd"]["residual"], selected_negative,
        args.permutations, SEED + 7, -1,
    )
    negative_zone_held = max_t_adjusted(
        zone_panels["ZL3b"]["even"]["residual"], selected_negative,
        args.permutations, SEED + 8, -1,
    )
    negative_held_p = p_lookup(negative_held)
    negative_zone_discovery_p = p_lookup(negative_zone_discovery)
    negative_zone_held_p = p_lookup(negative_zone_held)

    real_pipeline = strongest_novel_pipeline(corpora["ZL3b"])
    controls: list[dict[str, Any]] = []
    if not args.skip_controls:
        global CONTROL_TEMPLATE, CONTROL_COLLAPSE_MODE
        CONTROL_TEMPLATE = raw_corpora["ZL3b"]
        CONTROL_COLLAPSE_MODE = args.collapse_mode
        jobs = [str(path) for path in control_paths(args.control_dir)]
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers,
            mp_context=multiprocessing.get_context("fork"),
        ) as pool:
            controls = list(pool.map(control_pipeline, jobs, chunksize=1))
        controls.sort(key=lambda row: row["file"])
    exceedances = sum(
        row["discovery_t"] is not None
        and row["held_t"] is not None
        and row["discovery_t"] >= real_pipeline["discovery_t"] - 1e-12
        and row["held_t"] >= real_pipeline["held_t"] - 1e-12
        for row in controls
    )
    control_tail = {
        "controls": len(controls),
        "exceedances": exceedances,
        "p": (exceedances + 1) / (len(controls) + 1) if controls else None,
    }
    if controls:
        fields = sorted({key for row in controls for key in row})
        with OUTPUT_CONTROLS.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            writer.writerows(controls)

    planted_rows, planted_edges = plant_rows(corpora["ZL3b"], PLANTED_PAIR)
    planted_discovery = panel(planted_rows, 1, 1)
    planted_held = panel(planted_rows, 0, 1)
    planted_index = PAIR_INDEX[PLANTED_PAIR]
    planted_family = np.flatnonzero(enrichment_eligible(planted_discovery)).tolist()
    planted_discovery_test = max_t_adjusted(
        planted_discovery["residual"], planted_family, args.permutations, SEED + 9, 1,
    )
    planted_held_test = max_t_adjusted(
        planted_held["residual"], [planted_index], args.permutations, SEED + 10, 1,
    )
    planted = {
        "pair": f"{PLANTED_PAIR[0]}>{PLANTED_PAIR[1]}",
        "planted_edges": planted_edges,
        "discovery": metrics(planted_discovery, planted_index),
        "held": metrics(planted_held, planted_index),
        "discovery_adjusted_p": p_lookup(planted_discovery_test).get(planted_index, 1.0),
        "held_adjusted_p": p_lookup(planted_held_test).get(planted_index, 1.0),
    }
    planted_pass = (
        planted["discovery_adjusted_p"] <= 0.0001
        and planted["held_adjusted_p"] <= 0.0001
    )
    controls_pass = bool(controls) and control_tail["p"] <= ALPHA

    positive_candidates = []
    confirmed_positive: set[int] = set()
    for index in selected_positive:
        direction_ok, support_ok = direction_and_support(panels, index, 1)
        zone_direction_ok, zone_support_ok = direction_and_support(zone_panels, index, 1)
        # The generated discovery tail selects only among genuinely novel
        # pairs.  Previously confirmed rules retain their original independent
        # process calibration and must not be failed merely because the next
        # novel candidate is generic.
        process_ok = controls_pass if not existing_rule(*PAIRS[index]) else True
        passed = bool(
            positive_held_p.get(index, 1.0) <= ALPHA
            and positive_zone_discovery_p.get(index, 1.0) <= ALPHA
            and positive_zone_held_p.get(index, 1.0) <= ALPHA
            and direction_ok and zone_direction_ok and support_ok and zone_support_ok
            and process_ok and planted_pass
        )
        if passed:
            confirmed_positive.add(index)
        row = pair_summary(
            index, panels, zone_panels,
            positive_discovery_p, positive_held_p,
            positive_zone_discovery_p, positive_zone_held_p, passed,
        )
        row.update({
            "direction_pass": direction_ok,
            "zone_direction_pass": zone_direction_ok,
            "support_pass": support_ok,
            "zone_support_pass": zone_support_ok,
        })
        positive_candidates.append(row)

    negative_candidates = []
    confirmed_negative: set[int] = set()
    for index in selected_negative:
        direction_ok, support_ok = direction_and_support(panels, index, -1, True)
        zone_direction_ok, zone_support_ok = direction_and_support(zone_panels, index, -1, True)
        passed = bool(
            negative_held_p.get(index, 1.0) <= ALPHA
            and negative_zone_discovery_p.get(index, 1.0) <= ALPHA
            and negative_zone_held_p.get(index, 1.0) <= ALPHA
            and direction_ok and zone_direction_ok and support_ok and zone_support_ok
            and planted_pass
        )
        if passed:
            confirmed_negative.add(index)
        row = pair_summary(
            index, panels, zone_panels,
            negative_discovery_p, negative_held_p,
            negative_zone_discovery_p, negative_zone_held_p, passed,
        )
        row.update({
            "direction_pass": direction_ok,
            "zone_direction_pass": zone_direction_ok,
            "support_pass": support_ok,
            "zone_support_pass": zone_support_ok,
        })
        negative_candidates.append(row)

    confirmed_rows = []
    for index in sorted(confirmed_positive):
        left, right = PAIRS[index]
        confirmed_rows.append({
            "direction": "ENRICHED", "left_role": left, "right_role": right,
            "scope": existing_rule(left, right) or "NEW_EXACT_SPACE_RULE",
            "status": "CONFIRMED",
        })
    for index in sorted(confirmed_negative):
        left, right = PAIRS[index]
        confirmed_rows.append({
            "direction": "DEPLETED", "left_role": left, "right_role": right,
            "scope": known_depletion_context(left, right) or "ORDERING_CONSTRAINT",
            "status": "CONFIRMED",
        })
    write_confirmed(confirmed_rows)

    new_positive = [index for index in confirmed_positive if not existing_rule(*PAIRS[index])]
    l_serial_downgraded = next(
        row["status"] == "POSITIONAL_ONLY_DOWNGRADED"
        for row in existing_rule_audit if row["rule"] == "L_SERIAL"
    )
    if new_positive and l_serial_downgraded:
        status = "EXACT_ROLE_ATLAS_NEW_E_RULES_CONFIRMED_L_SERIAL_DOWNGRADED"
    elif new_positive:
        status = "EXACT_ROLE_TRANSITION_ATLAS_NEW_RULES_CONFIRMED"
    else:
        status = "EXACT_ROLE_TRANSITION_ATLAS_NO_NEW_RULE"
    payload: dict[str, Any] = {
        "status": status,
        "protocol": {
            "roles": list(ROLES),
            "pair_family": len(PAIRS),
            "discovery": "odd ZL folios",
            "held": "even ZL folios",
            "alternate_readings": ["IT2a", "RF1b"],
            "primary_null": "permute complete visible words within physical line",
            "position_sensitivity": f"same null inside {POSITION_ZONES} fixed normalized line zones",
            "permutations": args.permutations,
            "workers": args.workers,
            "images_decoded": 0,
            "collapse_mode": args.collapse_mode,
        },
        "collapse_inventory": collapse_inventory,
        "families": {
            "positive": {
                "discovery": {**positive_discovery, "eligible_pairs": len(positive_indices)},
                "held": positive_held,
                "zone_discovery": positive_zone_discovery,
                "zone_held": positive_zone_held,
            },
            "negative": {
                "discovery": {**negative_discovery, "eligible_pairs": len(negative_indices)},
                "held": negative_held,
                "zone_discovery": negative_zone_discovery,
                "zone_held": negative_zone_held,
            },
        },
        "positive_candidates": positive_candidates,
        "negative_candidates": negative_candidates,
        "existing_rule_audit": existing_rule_audit,
        "confirmed_positive_pairs": [f"{PAIRS[index][0]}>{PAIRS[index][1]}" for index in sorted(confirmed_positive)],
        "confirmed_new_positive_pairs": [f"{PAIRS[index][0]}>{PAIRS[index][1]}" for index in sorted(new_positive)],
        "confirmed_negative_pairs": [f"{PAIRS[index][0]}>{PAIRS[index][1]}" for index in sorted(confirmed_negative)],
        "real_novel_pipeline": real_pipeline,
        "generated_control_tail": control_tail,
        "planted": planted,
        "gates": {
            "generated_controls_pass": controls_pass,
            "planted_pass": planted_pass,
            "alpha": ALPHA,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "outputs": {
            "pairs": OUTPUT_PAIRS.name,
            "controls": OUTPUT_CONTROLS.name,
            "confirmed": OUTPUT_CONFIRMED.name,
        },
    }
    export_tsv(
        panels, zone_panels,
        {
            "discovery": positive_discovery,
            "held": positive_held,
            "zone_discovery": positive_zone_discovery,
            "zone_held": positive_zone_held,
        },
        {
            "discovery": negative_discovery,
            "held": negative_held,
            "zone_discovery": negative_zone_discovery,
            "zone_held": negative_zone_held,
        },
        confirmed_positive, confirmed_negative,
    )
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    rendered = report(payload)
    OUTPUT_REPORT.write_text(rendered, encoding="utf-8")
    print(json.dumps({
        "status": status,
        "confirmed_new_positive_pairs": payload["confirmed_new_positive_pairs"],
        "confirmed_negative_pairs": payload["confirmed_negative_pairs"],
        "generated_control_tail": control_tail,
        "planted": planted,
        "elapsed_seconds": payload["elapsed_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
