#!/usr/bin/env python3
"""Deterministic core for LTG001 anonymous latent transcription channels."""

from __future__ import annotations

import csv
import hashlib
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


ALPHA = 0.25
K_GRID = (2, 3, 4, 6, 8)
RESTARTS = 8
MAX_ITER = 500
RTOL = 1e-10
FOLD_DOMAIN = "LTG001_FOLD_V1|"
EDITION_NAMES = ("ZL", "IT", "RF")


@dataclass(frozen=True)
class Panel:
    family: np.ndarray
    observations: np.ndarray
    folio: tuple[str, ...]
    fold: np.ndarray
    currier: tuple[str, ...]
    triplet: tuple[tuple[str, str, str, str], ...]
    family_names: tuple[str, ...]
    symbol_names: tuple[str, ...]


@dataclass(frozen=True)
class ChannelFit:
    k: int
    pi: np.ndarray
    emissions: np.ndarray
    log_likelihood: float
    bic: float
    iterations: int
    restart: int


def physical_folio(page: str) -> str:
    match = re.match(r"^(f(?:Ros|[0-9]+))", page, re.IGNORECASE)
    if match is None:
        raise ValueError(page)
    return match.group(1).lower()


def folio_fold(folio: str) -> int:
    digest = hashlib.sha256((FOLD_DOMAIN + folio).encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % 5


def load_panel(path: Path) -> Panel:
    raw: list[tuple[str, tuple[str, str, str], str, str, tuple[str, str, str, str]]] = []
    families: set[str] = set()
    symbols: set[str] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["strict_zero_alternative"] != "1":
                continue
            folio = physical_folio(row["page"])
            editions = tuple(row[field].split() for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes"))
            if not all(len(values) == len(row["family_surface"]) for values in editions):
                raise ValueError(f"length drift {row['consensus_group_id']}")
            for fam, z, i, r in zip(row["family_surface"], *editions):
                if z[0] != fam or i[0] != fam or r[0] != fam:
                    raise ValueError(f"family drift {row['consensus_group_id']}")
                observation = (z[1:], i[1:], r[1:])
                families.add(fam)
                symbols.update(observation)
                raw.append((fam, observation, folio, row["currier"] or "BLANK", (fam, z, i, r)))
    family_names = tuple(sorted(families))
    symbol_names = tuple(sorted(symbols, key=lambda value: value.encode("utf-8")))
    family_index = {value: index for index, value in enumerate(family_names)}
    symbol_index = {value: index for index, value in enumerate(symbol_names)}
    return Panel(
        family=np.asarray([family_index[row[0]] for row in raw], dtype=np.int16),
        observations=np.asarray([[symbol_index[x] for x in row[1]] for row in raw], dtype=np.int16),
        folio=tuple(row[2] for row in raw),
        fold=np.asarray([folio_fold(row[2]) for row in raw], dtype=np.int8),
        currier=tuple(row[3] for row in raw),
        triplet=tuple(row[4] for row in raw),
        family_names=family_names,
        symbol_names=symbol_names,
    )


def _aggregate(family: np.ndarray, observations: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    matrix = np.column_stack((family.astype(np.int64), observations.astype(np.int64)))
    unique, counts = np.unique(matrix, axis=0, return_counts=True)
    return unique, counts.astype(np.float64)


def _logsumexp(values: np.ndarray, axis: int) -> np.ndarray:
    maximum = np.max(values, axis=axis, keepdims=True)
    return np.squeeze(maximum, axis=axis) + np.log(np.sum(np.exp(values - maximum), axis=axis))


def _seed(label: str) -> int:
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest()[:8], "big")


def fit_channel(
    family: np.ndarray,
    observations: np.ndarray,
    family_count: int,
    symbol_count: int,
    k: int,
    seed_label: str,
) -> ChannelFit:
    cells, counts = _aggregate(family, observations)
    cell_family = cells[:, 0].astype(np.int64)
    cell_obs = cells[:, 1:].astype(np.int64)
    n = float(np.sum(counts))
    best: ChannelFit | None = None
    for restart in range(RESTARTS):
        rng = np.random.default_rng(_seed(f"{seed_label}|K{k}|R{restart}"))
        pi = rng.gamma(shape=1.0, scale=1.0, size=(family_count, k)) + ALPHA
        pi /= pi.sum(axis=1, keepdims=True)
        emissions = rng.gamma(shape=1.0, scale=1.0, size=(3, k, symbol_count)) + ALPHA
        emissions /= emissions.sum(axis=2, keepdims=True)
        previous = -math.inf
        iterations = 0
        for iteration in range(1, MAX_ITER + 1):
            log_joint = np.log(pi[cell_family])
            for edition in range(3):
                log_joint += np.log(emissions[edition, :, cell_obs[:, edition]])
            norm = _logsumexp(log_joint, axis=1)
            responsibilities = np.exp(log_joint - norm[:, None])
            weighted = counts[:, None] * responsibilities

            pi_counts = np.full((family_count, k), ALPHA, dtype=np.float64)
            np.add.at(pi_counts, cell_family, weighted)
            pi = pi_counts / pi_counts.sum(axis=1, keepdims=True)
            emission_counts = np.full((3, k, symbol_count), ALPHA, dtype=np.float64)
            for edition in range(3):
                for state in range(k):
                    np.add.at(emission_counts[edition, state], cell_obs[:, edition], weighted[:, state])
            emissions = emission_counts / emission_counts.sum(axis=2, keepdims=True)

            updated = np.log(pi[cell_family])
            for edition in range(3):
                updated += np.log(emissions[edition, :, cell_obs[:, edition]])
            likelihood = float(np.dot(counts, _logsumexp(updated, axis=1)))
            iterations = iteration
            if math.isfinite(previous) and abs(likelihood - previous) <= RTOL * (1.0 + abs(previous)):
                break
            previous = likelihood
        parameters = family_count * (k - 1) + 3 * k * (symbol_count - 1)
        bic = -2.0 * likelihood + parameters * math.log(n)
        candidate = ChannelFit(k, pi, emissions, likelihood, bic, iterations, restart)
        if best is None or candidate.log_likelihood > best.log_likelihood + 1e-12 or (
            abs(candidate.log_likelihood - best.log_likelihood) <= 1e-12 and restart < best.restart
        ):
            best = candidate
    assert best is not None
    return best


def select_channel(
    family: np.ndarray,
    observations: np.ndarray,
    family_count: int,
    symbol_count: int,
    seed_label: str,
    grid: tuple[int, ...] = K_GRID,
) -> tuple[ChannelFit, tuple[ChannelFit, ...]]:
    fits = tuple(
        fit_channel(family, observations, family_count, symbol_count, k, seed_label)
        for k in grid
    )
    selected = min(fits, key=lambda fit: (fit.bic, fit.k))
    return selected, fits


def channel_probability(
    fit: ChannelFit,
    family: int,
    target: int,
    left_edition: int,
    right_edition: int,
    left: int,
    right: int,
    outcome: int,
) -> float:
    weights = (
        fit.pi[family]
        * fit.emissions[left_edition, :, left]
        * fit.emissions[right_edition, :, right]
    )
    denominator = float(np.sum(weights))
    numerator = float(np.sum(weights * fit.emissions[target, :, outcome]))
    return numerator / denominator


class DirectModel:
    def __init__(self, family_count: int, symbol_count: int):
        self.family_count = family_count
        self.symbol_count = symbol_count
        self.context: dict[tuple[int, int, int, int], np.ndarray] = {}
        self.backoff: dict[tuple[int, int], np.ndarray] = {}


def fit_direct(family: np.ndarray, observations: np.ndarray, family_count: int, symbol_count: int) -> DirectModel:
    model = DirectModel(family_count, symbol_count)
    context = defaultdict(lambda: np.zeros(symbol_count, dtype=np.float64))
    backoff = defaultdict(lambda: np.zeros(symbol_count, dtype=np.float64))
    for fam, triple in zip(family.tolist(), observations.tolist()):
        for target, left, right in ((0, 1, 2), (1, 0, 2), (2, 0, 1)):
            context[(target, fam, triple[left], triple[right])][triple[target]] += 1.0
            backoff[(target, fam)][triple[target]] += 1.0
    model.context = dict(context)
    model.backoff = dict(backoff)
    return model


def direct_probability(
    model: DirectModel,
    family: int,
    target: int,
    left: int,
    right: int,
    outcome: int,
) -> tuple[float, bool]:
    key = (target, family, left, right)
    seen = key in model.context
    counts = model.context[key] if seen else model.backoff[(target, family)]
    return float((counts[outcome] + ALPHA) / (np.sum(counts) + ALPHA * model.symbol_count)), seen


def sign_tail(positive: int, total: int) -> float:
    return sum(math.comb(total, value) for value in range(positive, total + 1)) / (2 ** total)


def _event_specs(triple: np.ndarray) -> Iterable[tuple[int, int, int]]:
    for target, left, right in ((0, 1, 2), (1, 0, 2), (2, 0, 1)):
        if triple[left] != triple[right]:
            yield target, left, right


def evaluate_panel(panel: Panel, seed_label: str) -> dict:
    event_rows: list[dict] = []
    fold_models = []
    for held in range(5):
        train = panel.fold != held
        selected, fits = select_channel(
            panel.family[train], panel.observations[train], len(panel.family_names),
            len(panel.symbol_names), f"{seed_label}|FOLD{held}",
        )
        direct = fit_direct(panel.family[train], panel.observations[train], len(panel.family_names), len(panel.symbol_names))
        fold_models.append({
            "fold": held,
            "selected_k": selected.k,
            "selected_bic": selected.bic,
            "selected_log_likelihood": selected.log_likelihood,
            "iterations": selected.iterations,
            "restart": selected.restart,
            "candidate_bic": {str(fit.k): fit.bic for fit in fits},
        })
        for index in np.flatnonzero(panel.fold == held):
            triple = panel.observations[index]
            for target, left, right in _event_specs(triple):
                p_channel = channel_probability(
                    selected, int(panel.family[index]), target, left, right,
                    int(triple[left]), int(triple[right]), int(triple[target]),
                )
                p_direct, seen = direct_probability(
                    direct, int(panel.family[index]), target,
                    int(triple[left]), int(triple[right]), int(triple[target]),
                )
                event_rows.append({
                    "index": int(index),
                    "folio": panel.folio[index],
                    "currier": panel.currier[index],
                    "target": EDITION_NAMES[target],
                    "gain": math.log2(p_channel) - math.log2(p_direct),
                    "seen_context": seen,
                    "dominant_policy": panel.triplet[index] == ("B", "B1", "B1", "Ba"),
                })
    folio_values = defaultdict(list)
    currier_values = defaultdict(list)
    for event in event_rows:
        folio_values[event["folio"]].append(event["gain"])
        currier_values[event["currier"]].append(event["gain"])
    folio_gain = {key: math.fsum(values) / len(values) for key, values in sorted(folio_values.items())}
    equal_folio = math.fsum(folio_gain.values()) / len(folio_gain)
    positive = sum(value > 0.0 for value in folio_gain.values())

    def mean_where(predicate) -> float | None:
        values = [row["gain"] for row in event_rows if predicate(row)]
        return math.fsum(values) / len(values) if values else None

    deletion = []
    keys = list(folio_gain)
    for removed in keys:
        values = [value for folio, value in folio_gain.items() if folio != removed]
        deletion.append(math.fsum(values) / len(values))
    summary = {
        "event_count": len(event_rows),
        "folio_count": len(folio_gain),
        "equal_folio_gain_bits": equal_folio,
        "positive_folios": positive,
        "folio_sign_p": sign_tail(positive, len(folio_gain)),
        "currier_gain_bits": {
            key: math.fsum(values) / len(values) for key, values in sorted(currier_values.items())
        },
        "dominant_policy_deleted_gain_bits": mean_where(lambda row: not row["dominant_policy"]),
        "unseen_context_gain_bits": mean_where(lambda row: not row["seen_context"]),
        "unseen_context_events": sum(not row["seen_context"] for row in event_rows),
        "minimum_leave_one_folio_gain_bits": min(deletion),
    }
    summary["gates"] = {
        "gain_at_least_0_020": equal_folio >= 0.020,
        "sign_p_at_most_0_01": summary["folio_sign_p"] <= 0.01,
        "currier_A_B_at_least_0_010": all(summary["currier_gain_bits"].get(key, -math.inf) >= 0.010 for key in ("A", "B")),
        "dominant_policy_deleted_positive": (summary["dominant_policy_deleted_gain_bits"] or -math.inf) > 0.0,
        "unseen_context_positive": (summary["unseen_context_gain_bits"] or -math.inf) > 0.0,
        "every_leave_one_folio_positive": summary["minimum_leave_one_folio_gain_bits"] > 0.0,
    }
    summary["decision"] = "PASS_REUSABLE_LATENT_CHANNEL" if all(summary["gates"].values()) else "FINAL_NONCONFIRMATION"
    return {"fold_models": fold_models, "summary": summary, "folio_gain": folio_gain, "events": event_rows}


def panel_from_arrays(
    family: np.ndarray,
    observations: np.ndarray,
    folios: tuple[str, ...],
    currier: tuple[str, ...],
    family_count: int,
    symbol_count: int,
) -> Panel:
    names_f = tuple(f"F{index:02d}" for index in range(family_count))
    names_s = tuple(str(index) for index in range(symbol_count))
    return Panel(
        family=np.asarray(family, dtype=np.int16), observations=np.asarray(observations, dtype=np.int16),
        folio=folios, fold=np.asarray([folio_fold(value) for value in folios], dtype=np.int8), currier=currier,
        triplet=tuple((names_f[int(fam)], *(names_s[int(x)] for x in obs)) for fam, obs in zip(family, observations)),
        family_names=names_f, symbol_names=names_s,
    )
