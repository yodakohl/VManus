#!/usr/bin/env python3
"""Pure prefix-equivalence scorer for F69M001."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict

import numpy as np


ALPHABET = tuple("ABCDEFGHJKLMNPQTUVWXZ")
N = 28
DEPTHS = (1, 2, 3)
ASSIGNMENTS = 8192
TOL = 1e-15


def object_sha(value: object) -> str:
    return hashlib.sha256((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()


def normalize_name(name: str) -> str:
    token = name.lower().split()[0]
    if not token.isascii() or not token.isalpha() or len(token) < 3:
        raise ValueError("historical name")
    return token


def validate_sequences(sequences: list[str]) -> None:
    if len(sequences) != N or any(len(value) < 3 for value in sequences):
        raise ValueError("sequence shape")
    if any(any(char not in ALPHABET for char in value) for value in sequences):
        raise ValueError("unknown family")


def alignment_maps() -> tuple[list[tuple[str, int]], np.ndarray]:
    keys, maps = [], []
    for direction in ("FORWARD", "REVERSE"):
        for rotation in range(N):
            keys.append((direction, rotation))
            if direction == "FORWARD":
                maps.append([(i + rotation) % N for i in range(N)])
            else:
                maps.append([(rotation - i) % N for i in range(N)])
    return keys, np.asarray(maps, dtype=np.int16)


ALIGNMENT_KEYS, ALIGNMENT_MAPS = alignment_maps()


def _codes(values: list[str], depth: int) -> np.ndarray:
    prefixes = [value[:depth] for value in values]
    mapping = {value: index for index, value in enumerate(sorted(set(prefixes)))}
    return np.asarray([mapping[value] for value in prefixes], dtype=np.int16)


def _phi_from_n11(n11: np.ndarray, equal_x: int, equal_y: int) -> np.ndarray:
    total = N * (N - 1) // 2
    n10 = equal_x - n11
    n01 = equal_y - n11
    n00 = total - n11 - n10 - n01
    denominator = math.sqrt(equal_x * (total - equal_x) * equal_y * (total - equal_y))
    if denominator == 0:
        raise ValueError("degenerate prefix equality")
    return (n11 * n00 - n10 * n01) / denominator


def _alignment_phi(x_codes: np.ndarray, y_codes: np.ndarray, maps: np.ndarray = ALIGNMENT_MAPS) -> np.ndarray:
    pair_i, pair_j = np.triu_indices(N, 1)
    x_equal = x_codes[pair_i] == x_codes[pair_j]
    equal_x = int(x_equal.sum())
    equal_y = int((y_codes[pair_i] == y_codes[pair_j]).sum())
    aligned = y_codes[maps]
    n11 = (aligned[:, pair_i[x_equal]] == aligned[:, pair_j[x_equal]]).sum(axis=1)
    return _phi_from_n11(n11.astype(np.float64), equal_x, equal_y)


def observed_alignments(sequences: list[str], roster: list[str]) -> dict[str, object]:
    validate_sequences(sequences)
    names = [normalize_name(name) for name in roster]
    if len(names) != N:
        raise ValueError("roster")
    depth_phi = np.vstack([_alignment_phi(_codes(sequences, k), _codes(names, k)) for k in DEPTHS]).T
    means = depth_phi.mean(axis=1)
    best_index = min(range(56), key=lambda index: (-float(means[index]), index))
    second = max(float(value) for index, value in enumerate(means) if index != best_index)
    return {
        "keys": ALIGNMENT_KEYS,
        "depth_phi_matrix": depth_phi,
        "means": means,
        "best_index": best_index,
        "best_key": ALIGNMENT_KEYS[best_index],
        "best_phi": depth_phi[best_index],
        "S": float(means[best_index]),
        "second_best": second,
        "margin": float(means[best_index]) - second,
    }


def _keyed_order(domain: str, assignment: int, positions: list[int]) -> list[int]:
    return sorted(positions, key=lambda position: hashlib.sha256(f"F69M001|{domain}|{assignment}|{position}".encode()).digest())


def null_prefix_codes(roster: list[str], domain: str) -> dict[int, np.ndarray]:
    names = [normalize_name(name) for name in roster]
    if domain not in {"GLOBAL", "INITIAL_CONDITIONED"}:
        raise ValueError(domain)
    arrays = {depth: np.empty((ASSIGNMENTS, N), dtype=np.int16) for depth in DEPTHS}
    for assignment in range(ASSIGNMENTS):
        if domain == "GLOBAL":
            order = _keyed_order(domain, assignment, list(range(N)))
            permuted = [names[source] for source in order]
        else:
            permuted = list(names)
            groups: dict[str, list[int]] = defaultdict(list)
            for position, name in enumerate(names):
                groups[name[0]].append(position)
            for positions in groups.values():
                donors = _keyed_order(domain, assignment, positions)
                for destination, source in zip(sorted(positions), donors, strict=True):
                    permuted[destination] = names[source]
        for depth in DEPTHS:
            arrays[depth][assignment] = _codes(permuted, depth)
    return arrays


def null_max_scores(sequences: list[str], prepared: dict[int, np.ndarray], batch_size: int = 128) -> np.ndarray:
    validate_sequences(sequences)
    pair_i, pair_j = np.triu_indices(N, 1)
    total = N * (N - 1) // 2
    score_sum = np.zeros((ASSIGNMENTS, 56), dtype=np.float64)
    for depth in DEPTHS:
        x = _codes(sequences, depth)
        x_equal = x[pair_i] == x[pair_j]
        equal_x = int(x_equal.sum())
        y_all = prepared[depth]
        # The roster prefix margins are invariant under permutation.
        y0 = y_all[0]
        equal_y = int((y0[pair_i] == y0[pair_j]).sum())
        denominator = math.sqrt(equal_x * (total - equal_x) * equal_y * (total - equal_y))
        if denominator == 0:
            raise ValueError("degenerate prefix equality")
        for start in range(0, ASSIGNMENTS, batch_size):
            stop = min(start + batch_size, ASSIGNMENTS)
            aligned = y_all[start:stop, ALIGNMENT_MAPS]
            n11 = (aligned[:, :, pair_i[x_equal]] == aligned[:, :, pair_j[x_equal]]).sum(axis=2).astype(np.float64)
            n10 = equal_x - n11
            n01 = equal_y - n11
            n00 = total - n11 - n10 - n01
            score_sum[start:stop] += (n11 * n00 - n10 * n01) / denominator
    return (score_sum / 3.0).max(axis=1)


def deletion_scores(sequences: list[str], roster: list[str], best_index: int) -> list[float]:
    names = [normalize_name(name) for name in roster]
    mapping = ALIGNMENT_MAPS[best_index]
    values = []
    for deleted in range(N):
        keep = [index for index in range(N) if index != deleted]
        depth_values = []
        for depth in DEPTHS:
            x = [sequences[index][:depth] for index in keep]
            y = [names[int(mapping[index])][:depth] for index in keep]
            pair_i, pair_j = np.triu_indices(N - 1, 1)
            xb = np.asarray([x[i] == x[j] for i, j in zip(pair_i, pair_j, strict=True)], dtype=np.int8)
            yb = np.asarray([y[i] == y[j] for i, j in zip(pair_i, pair_j, strict=True)], dtype=np.int8)
            n11 = int(((xb == 1) & (yb == 1)).sum()); n10 = int(((xb == 1) & (yb == 0)).sum())
            n01 = int(((xb == 0) & (yb == 1)).sum()); n00 = int(((xb == 0) & (yb == 0)).sum())
            den = math.sqrt((n11+n10)*(n01+n00)*(n11+n01)*(n10+n00))
            if den == 0: raise ValueError("deletion degeneracy")
            depth_values.append((n11*n00-n10*n01)/den)
        values.append(math.fsum(depth_values) / 3)
    return values


def evaluate(sequences: list[str], roster: list[str], nulls: dict[str, dict[int, np.ndarray]]) -> dict[str, object]:
    observed = observed_alignments(sequences, roster)
    orbits = {domain: null_max_scores(sequences, nulls[domain]) for domain in ("GLOBAL", "INITIAL_CONDITIONED")}
    p = {domain: (1 + int((values >= observed["S"] - TOL).sum())) / (ASSIGNMENTS + 1) for domain, values in orbits.items()}
    deletions = deletion_scores(sequences, roster, observed["best_index"])
    best_phi = [float(value) for value in observed["best_phi"]]
    gates = {
        "S_at_least_025": observed["S"] >= .25 - TOL,
        "global_p_at_most_001": p["GLOBAL"] <= .01 + TOL,
        "initial_conditioned_p_at_most_005": p["INITIAL_CONDITIONED"] <= .05 + TOL,
        "all_depths_positive": all(value > 0 for value in best_phi),
        "depth2_and_depth3_at_least_025": best_phi[1] >= .25 - TOL and best_phi[2] >= .25 - TOL,
        "alignment_margin_at_least_003": observed["margin"] >= .03 - TOL,
        "all_deletions_at_least_015": min(deletions) >= .15 - TOL,
        "finite": all(math.isfinite(value) for value in [observed["S"], observed["margin"], *best_phi, *p.values(), *deletions, *orbits["GLOBAL"], *orbits["INITIAL_CONDITIONED"]]),
    }
    return {
        "sequence_sha256": object_sha(sequences),
        "best_direction": observed["best_key"][0], "best_rotation": observed["best_key"][1],
        "S": observed["S"], "best_depth_phi": best_phi,
        "second_best": observed["second_best"], "alignment_margin": observed["margin"],
        "p_global": p["GLOBAL"], "p_initial_conditioned": p["INITIAL_CONDITIONED"],
        "global_orbit_sha256": hashlib.sha256(orbits["GLOBAL"].astype("<f8").tobytes()).hexdigest(),
        "conditioned_orbit_sha256": hashlib.sha256(orbits["INITIAL_CONDITIONED"].astype("<f8").tobytes()).hexdigest(),
        "deletion_scores": deletions, "min_deletion": min(deletions),
        "gates": gates, "passes": all(gates.values()),
    }


def synthetic_sequences(roster: list[str], world: int, mode: str) -> list[str]:
    names = [normalize_name(name) for name in roster]
    chars = sorted(set("".join(name[:3] for name in names)))
    if len(chars) > len(ALPHABET):
        raise ValueError("encoding capacity")
    offset = world % len(ALPHABET)
    mapping = {char: ALPHABET[(index + offset) % len(ALPHABET)] for index, char in enumerate(chars)}
    order = [((world * 3 + i) % N) if world % 2 == 0 else ((world * 3 - i) % N) for i in range(N)]
    encoded = ["".join(mapping[char] for char in names[source][:3]) for source in order]
    if mode == "FULL_PLANT":
        return encoded
    if mode == "NULL":
        return [ALPHABET[(i+world)%21] + ALPHABET[(i*5+world+1)%21] + ALPHABET[(i*11+world+2)%21] for i in range(N)]
    if mode == "DOMINANT_INITIAL_ONLY":
        return [encoded[i][0] + ALPHABET[(i+world)%5] + ALPHABET[((i//5)+world)%3] for i in range(N)]
    if mode == "FOUR_BLOCK_ONLY":
        values = [ALPHABET[(i+world)%21] + ALPHABET[(i*5+2)%21] + ALPHABET[(i*11+4)%21] for i in range(N)]
        for index in range(21, 25): values[index] = "AAA"
        return values
    if mode == "SHALLOW_TWO_DEPTH_ONLY":
        return [encoded[i][:2] + ALPHABET[(i+world)%2] for i in range(N)]
    raise ValueError(mode)
