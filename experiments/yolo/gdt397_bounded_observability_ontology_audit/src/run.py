#!/usr/bin/env python3
"""Run the bounded GDT397 observability/ontology audit.

This program reads only the already exposed GDT396 qualification block. It
never invokes a generator, opens a confirmation seed, or reads Voynich data.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import random
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt397_bounded_observability_ontology_audit"
G396 = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
CORPORA = G396 / ".work/corpora"
CLAIMS = G396 / ".work/claims"
OUTPUT = EXP / "artifacts/gdt397_observability_results.tsv"

SEEDS = tuple(range(3961000, 3961005))
MEANINGFUL_WORLDS = ("W02", "W09")
AUDIT_WORLDS = ("W02", "W09", "W10")
VIEWS = ("FREE_RAW", "VOYNICH_RAW", "VOYNICH_ATOM_DECODED")
FLEX_D = 256
BASE_D = 64
RIDGE = 10.0
MAGIC = b"GDT396VS1\0"

DECODERS = (
    "d396s01_multiview_graph",
    "d396s02_mdl_components",
    "d396s03_relation_topology",
    "d396s04_contrastive_roles",
    "d396s05_multiconstraint_function",
)
SURFACE_DIRS = ("FREE_SURFACE", "VOYNICH_SURFACE")

DECISIONS = {
    "OBSERVABLE_AND_CURRENT_DECODER_LIMITED",
    "STRUCTURAL_ROLE_RECOVERABLE_SEMANTIC_LABEL_NOT_IDENTIFIABLE",
    "NOT_OBSERVABLE_UNDER_CURRENT_CHANNEL",
    "CAPACITY_INSUFFICIENT",
    "CURRENT_GDT396_RESULT_WAS_GATE_CONTAMINATION",
    "NONIDENTIFIABLE_BY_OBSERVATIONAL_EQUIVALENCE",
}

FIELDS = (
    "row_type", "endpoint", "world", "surface", "model", "n", "n_positive",
    "metric_1", "value_1", "baseline_1", "metric_2", "value_2", "baseline_2",
    "metric_3", "value_3", "baseline_3", "strong_folds", "total_folds",
    "capacity", "decision", "observation_sha256", "interpretation_sha256",
    "details_json", "note",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def read_tsv_gz(path: Path) -> list[dict[str, str]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def read_atom_stream(path: Path) -> list[tuple[int, ...]]:
    with gzip.open(path, "rb") as fh:
        if fh.read(len(MAGIC)) != MAGIC:
            raise ValueError(f"{path}: bad constrained-surface magic")
        count_raw = fh.read(4)
        if len(count_raw) != 4:
            raise ValueError(f"{path}: truncated count")
        count = struct.unpack(">I", count_raw)[0]
        result = []
        for _ in range(count):
            size_raw = fh.read(2)
            if len(size_raw) != 2:
                raise ValueError(f"{path}: truncated length")
            size = struct.unpack(">H", size_raw)[0]
            payload = fh.read(size)
            if len(payload) != size or not payload or any(atom >= 24 for atom in payload):
                raise ValueError(f"{path}: invalid atom payload")
            result.append(tuple(payload))
        if fh.read(1):
            raise ValueError(f"{path}: trailing bytes")
    return result


def load_manifest() -> dict[tuple[str, int], dict[str, str]]:
    path = CORPORA / "gdt396_qualification_paired_manifest_v2.tsv"
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    selected: dict[tuple[str, int], dict[str, str]] = {}
    for row in rows:
        world = row["world_id"]
        seed = int(row["corpus_seed"])
        if world not in AUDIT_WORLDS or seed not in SEEDS:
            continue
        if row["seed_block"] != "qualification" or "396200" in json.dumps(row):
            raise RuntimeError("forbidden seed or phase in selected manifest row")
        selected[(world, seed)] = row
    expected = {(world, seed) for world in AUDIT_WORLDS for seed in SEEDS}
    if set(selected) != expected:
        raise RuntimeError("qualification manifest does not contain exact selected panel")
    return selected


def checked_input(relpath: str, expected_hash: str) -> Path:
    if "396200" in relpath or "confirmation" in relpath.lower():
        raise RuntimeError(f"forbidden path: {relpath}")
    path = CORPORA / relpath
    if sha256(path) != expected_hash:
        raise RuntimeError(f"input hash mismatch: {relpath}")
    return path


def load_world(world: str, manifest: dict[tuple[str, int], dict[str, str]]) -> dict[str, dict[int, list[dict]]]:
    data: dict[str, dict[int, list[dict]]] = {view: {} for view in VIEWS}
    for seed in SEEDS:
        m = manifest[(world, seed)]
        free_path = checked_input(m["free_observation_relpath"], m["free_observation_sha256"])
        meta_path = checked_input(m["voynich_metadata_relpath"], m["voynich_metadata_sha256"])
        atom_path = checked_input(m["voynich_surface_relpath"], m["voynich_surface_sha256"])
        oracle_path = checked_input(m["oracle_relpath"], m["oracle_sha256"])
        free = read_tsv_gz(free_path)
        meta = read_tsv_gz(meta_path)
        atoms = read_atom_stream(atom_path)
        oracle = {row["event_id"]: row for row in read_tsv_gz(oracle_path)}
        if not (len(free) == len(meta) == len(atoms) == len(oracle) == int(m["events"])):
            raise RuntimeError(f"{world}/{seed}: paired length mismatch")
        for index, (frow, mrow, payload) in enumerate(zip(free, meta, atoms)):
            if frow["event_id"] != mrow["event_id"] or int(frow["event_index"]) != index:
                raise RuntimeError(f"{world}/{seed}: paired event mismatch")
            if len(payload) % 2:
                raise RuntimeError(f"{world}/{seed}: odd fixed-width atom payload")
            common = dict(frow)
            common.pop("visible_group")
            common["event_index"] = int(common["event_index"])
            common["group_index"] = int(common["group_index"])
            common["oracle"] = oracle[frow["event_id"]]
            free_row = dict(common)
            free_row["tokens_raw"] = tuple(frow["visible_group"])
            raw_row = dict(common)
            raw_row["tokens_raw"] = tuple(f"A{atom:02d}" for atom in payload)
            decoded_row = dict(common)
            decoded_row["tokens_raw"] = tuple(f"P{payload[j]:02d}_{payload[j+1]:02d}" for j in range(0, len(payload), 2))
            data["FREE_RAW"].setdefault(seed, []).append(free_row)
            data["VOYNICH_RAW"].setdefault(seed, []).append(raw_row)
            data["VOYNICH_ATOM_DECODED"].setdefault(seed, []).append(decoded_row)

    for view in VIEWS:
        token_map: dict[str, str] = {}
        for seed in SEEDS:
            for row in data[view][seed]:
                normalized = []
                for token in row["tokens_raw"]:
                    if token not in token_map:
                        token_map[token] = f"T{len(token_map):03d}"
                    normalized.append(token_map[token])
                row["tokens"] = tuple(normalized)
                row["surface_key"] = ".".join(normalized)
                del row["tokens_raw"]
    for seed in SEEDS:
        for free, decoded in zip(data["FREE_RAW"][seed], data["VOYNICH_ATOM_DECODED"][seed]):
            if free["event_id"] != decoded["event_id"] or free["tokens"] != decoded["tokens"]:
                raise RuntimeError(f"{world}/{seed}: atom decode does not restore native token algebra")
    for view in VIEWS:
        for seed in SEEDS:
            enrich(data[view][seed])
    return data


def enrich(rows: list[dict]) -> None:
    rows.sort(key=lambda row: row["event_index"])
    counts = Counter(row["surface_key"] for row in rows)
    record_rows: dict[str, list[int]] = defaultdict(list)
    line_rows: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        record_rows[row["record_id"]].append(i)
        line_rows[row["line_id"]].append(i)
    record_surface_counts = {
        record: Counter(rows[i]["surface_key"] for i in indices) for record, indices in record_rows.items()
    }
    record_positions = {i: pos for indices in record_rows.values() for pos, i in enumerate(indices)}
    line_positions = {i: pos for indices in line_rows.values() for pos, i in enumerate(indices)}
    for i, row in enumerate(rows):
        rec = record_rows[row["record_id"]]
        line = line_rows[row["line_id"]]
        rec_pos = record_positions[i]
        line_pos = line_positions[i]
        row["ctx_frequency"] = counts[row["surface_key"]]
        row["ctx_record_frequency"] = record_surface_counts[row["record_id"]][row["surface_key"]]
        row["ctx_record_length"] = len(rec)
        row["ctx_line_length"] = len(line)
        row["ctx_record_ordinal"] = rec_pos
        row["ctx_line_ordinal"] = line_pos
        row["ctx_record_fraction"] = rec_pos / max(1, len(rec) - 1)
        row["ctx_line_fraction"] = line_pos / max(1, len(line) - 1)
        row["ctx_record_indices"] = rec
        prev = rows[i - 1] if i and rows[i - 1]["record_id"] == row["record_id"] else None
        nxt = rows[i + 1] if i + 1 < len(rows) and rows[i + 1]["record_id"] == row["record_id"] else None
        row["ctx_prev_surface"] = prev["surface_key"] if prev else "<RECORD_START>"
        row["ctx_next_surface"] = nxt["surface_key"] if nxt else "<RECORD_END>"


def hashed_index(feature: str, dimension: int) -> tuple[int, float]:
    digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8, person=b"GDT397F").digest()
    number = int.from_bytes(digest, "big")
    return 1 + number % (dimension - 1), 1.0 if number & 1 else -1.0


def add_feature(vector: np.ndarray, feature: str, value: float = 1.0) -> None:
    index, sign = hashed_index(feature, len(vector))
    vector[index] += sign * value


def event_features(row: dict, flexible: bool) -> list[str]:
    features = [
        f"SB={row['separator_before']}", f"SA={row['separator_after']}",
        f"SP={row['separator_before']}->{row['separator_after']}",
        f"REG={row['register_id']}", f"HAND={row['hand_id']}", f"LAY={row['layout_role']}",
        f"LP={row['line_position_bin']}", f"RP={row['record_position_bin']}",
        f"AMB={row['ambiguous_boundary']}", f"LEN={min(len(row['tokens']), 16)}",
        f"FREQ={min(int(math.log2(row['ctx_frequency'])), 12)}",
        f"RFREQ={min(row['ctx_record_frequency'], 8)}",
        f"RLEN={min(row['ctx_record_length'], 20)}", f"LLEN={min(row['ctx_line_length'], 12)}",
        f"RQ={min(4, int(row['ctx_record_fraction'] * 5))}",
        f"LQ={min(4, int(row['ctx_line_fraction'] * 5))}",
    ]
    if not flexible:
        return features
    tokens = row["tokens"]
    features.extend((f"SURF={row['surface_key']}", f"PREV={row['ctx_prev_surface']}", f"NEXT={row['ctx_next_surface']}"))
    features.append(f"EQPREV={row['surface_key'] == row['ctx_prev_surface']}")
    features.append(f"EQNEXT={row['surface_key'] == row['ctx_next_surface']}")
    for n in (1, 2, 3):
        for i in range(max(0, len(tokens) - n + 1)):
            features.append(f"N{n}=" + ".".join(tokens[i:i+n]))
    for n in (1, 2):
        if len(tokens) >= n:
            features.append(f"P{n}=" + ".".join(tokens[:n]))
            features.append(f"S{n}=" + ".".join(tokens[-n:]))
    return features


def event_matrix(rows: list[dict], flexible: bool) -> np.ndarray:
    dimension = FLEX_D if flexible else BASE_D
    matrix = np.zeros((len(rows), dimension), dtype=np.float64)
    matrix[:, 0] = 1.0
    for i, row in enumerate(rows):
        for feature in event_features(row, flexible):
            add_feature(matrix[i], feature)
        norm = np.linalg.norm(matrix[i, 1:])
        if norm:
            matrix[i, 1:] /= norm
    return matrix


def ridge_coefficients(x: np.ndarray, y: np.ndarray, weights: np.ndarray | None = None) -> np.ndarray:
    if y.ndim == 1:
        y = y[:, None]
    if weights is None:
        xtx = x.T @ x
        xty = x.T @ y
    else:
        root_w = np.sqrt(weights)[:, None]
        wx = x * root_w
        wy = y * root_w
        xtx = wx.T @ wx
        xty = wx.T @ wy
    penalty = np.eye(x.shape[1]) * RIDGE
    penalty[0, 0] = 1e-6
    return np.linalg.solve(xtx + penalty, xty)


def balanced_weights(y: np.ndarray) -> np.ndarray:
    positive = int(np.sum(y == 1))
    negative = len(y) - positive
    if not positive or not negative:
        return np.ones(len(y))
    return np.where(y == 1, len(y) / (2 * positive), len(y) / (2 * negative)).astype(np.float64)


def contingency_metrics(truth: Iterable[str], prediction: Iterable[str]) -> tuple[float, float, float]:
    truth = list(truth); prediction = list(prediction)
    n = len(truth)
    if not n:
        return float("nan"), float("nan"), float("nan")
    joint = Counter(zip(truth, prediction)); tc = Counter(truth); pc = Counter(prediction)
    mi = sum(count / n * math.log((count * n) / (tc[a] * pc[b])) for (a, b), count in joint.items())
    ht = -sum(count / n * math.log(count / n) for count in tc.values())
    hp = -sum(count / n * math.log(count / n) for count in pc.values())
    nmi = mi / math.sqrt(ht * hp) if ht and hp else float(ht == hp)
    choose2 = lambda value: value * (value - 1) / 2
    tp = sum(choose2(count) for count in joint.values())
    true_pairs = sum(choose2(count) for count in tc.values())
    pred_pairs = sum(choose2(count) for count in pc.values())
    total_pairs = choose2(n)
    expected = true_pairs * pred_pairs / total_pairs if total_pairs else 0.0
    maximum = (true_pairs + pred_pairs) / 2
    ari = (tp - expected) / (maximum - expected) if maximum != expected else 1.0
    precision = tp / pred_pairs if pred_pairs else 0.0
    recall = tp / true_pairs if true_pairs else 0.0
    pair_f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return nmi, ari, pair_f1


def auc_ap(y: Iterable[int], score: Iterable[float]) -> tuple[float, float, float]:
    y = np.asarray(list(y), dtype=np.int8); score = np.asarray(list(score), dtype=np.float64)
    npos = int(y.sum()); nneg = len(y) - npos
    prevalence = npos / len(y) if len(y) else float("nan")
    if not npos or not nneg:
        return float("nan"), float("nan"), prevalence
    order = np.argsort(score, kind="mergesort")
    ranks = np.empty(len(score), dtype=np.float64)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and score[order[j]] == score[order[i]]:
            j += 1
        ranks[order[i:j]] = (i + 1 + j) / 2
        i = j
    auc = (ranks[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg)
    descending = np.argsort(-score, kind="mergesort")
    seen = 0; precision_sum = 0.0
    for rank, index in enumerate(descending, 1):
        if y[index]:
            seen += 1
            precision_sum += seen / rank
    return float(auc), precision_sum / npos, prevalence


def lexical_folds(data: dict[int, list[dict]]) -> list[dict]:
    matrices = {seed: (event_matrix(data[seed], True), event_matrix(data[seed], False)) for seed in SEEDS}
    folds = []
    for held in SEEDS:
        train_rows = [row for seed in SEEDS if seed != held for row in data[seed]]
        held_rows = data[held]
        xflex = np.vstack([matrices[seed][0] for seed in SEEDS if seed != held])
        xbase = np.vstack([matrices[seed][1] for seed in SEEDS if seed != held])
        hflex, hbase = matrices[held]
        train_truth = [row["oracle"]["lexical_id"] for row in train_rows]
        held_truth = [row["oracle"]["lexical_id"] for row in held_rows]
        classes = sorted(set(train_truth)); class_index = {value: i for i, value in enumerate(classes)}
        y = np.zeros((len(train_truth), len(classes)), dtype=np.float64)
        y[np.arange(len(y)), [class_index[value] for value in train_truth]] = 1.0
        flex_pred = [classes[i] for i in np.argmax(hflex @ ridge_coefficients(xflex, y), axis=1)]
        base_pred = [classes[i] for i in np.argmax(hbase @ ridge_coefficients(xbase, y), axis=1)]
        fm = contingency_metrics(held_truth, flex_pred)
        bm = contingency_metrics(held_truth, base_pred)
        em = contingency_metrics(held_truth, [row["surface_key"] for row in held_rows])
        strong = fm[0] >= .70 and fm[1] >= .55 and fm[2] >= .65 and all(f-b >= .10 for f, b in zip(fm, bm))
        folds.append({"seed": held, "n": len(held_rows), "flex": fm, "base": bm, "equality": em, "strong": bool(strong)})
    return folds


def role_truth(world: str, row: dict) -> int:
    oracle = row["oracle"]
    if world == "W02":
        return int(oracle["semantic_category"] == "FUNCTION")
    if world == "W09":
        return int(oracle["function_class"] in {"relator", "schema_marker", "quantifier"})
    raise ValueError(world)


def role_folds(world: str, data: dict[int, list[dict]]) -> list[dict]:
    matrices = {seed: (event_matrix(data[seed], True), event_matrix(data[seed], False)) for seed in SEEDS}
    folds = []
    for held in SEEDS:
        train_rows = [row for seed in SEEDS if seed != held for row in data[seed]]
        held_rows = data[held]
        ytrain = np.asarray([role_truth(world, row) for row in train_rows], dtype=np.float64)
        yheld = np.asarray([role_truth(world, row) for row in held_rows], dtype=np.int8)
        xflex = np.vstack([matrices[seed][0] for seed in SEEDS if seed != held])
        xbase = np.vstack([matrices[seed][1] for seed in SEEDS if seed != held])
        flex_score = matrices[held][0] @ ridge_coefficients(xflex, ytrain, balanced_weights(ytrain))
        base_score = matrices[held][1] @ ridge_coefficients(xbase, ytrain, balanced_weights(ytrain))
        fa = auc_ap(yheld, flex_score[:, 0]); ba = auc_ap(yheld, base_score[:, 0])
        strong = fa[0] >= .75 and fa[1] >= fa[2] + .15 and fa[0] >= ba[0] + .05 and fa[1] >= ba[1] + .05
        margin = min((fa[0]-.75)/.05, (fa[1]-fa[2]-.15)/.05, (fa[0]-ba[0]-.05)/.05, (fa[1]-ba[1]-.05)/.05)
        folds.append({"seed": held, "n": len(yheld), "positive": int(yheld.sum()), "flex": fa, "base": ba, "strong": bool(strong), "margin": margin})
    return folds


def token_jaccard(a: tuple[str, ...], b: tuple[str, ...]) -> float:
    sa, sb = set(a), set(b)
    return len(sa & sb) / len(sa | sb) if sa or sb else 0.0


def pair_features(source: dict, candidate: dict) -> np.ndarray:
    distance = max(1, source["event_index"] - candidate["event_index"])
    a, b = source["tokens"], candidate["tokens"]
    return np.asarray([
        1.0, -math.log1p(distance) / 10, float(source["surface_key"] == candidate["surface_key"]),
        float(a[:1] == b[:1]), float(a[-1:] == b[-1:]), token_jaccard(a, b),
        float(len(a) == len(b)), -abs(len(a)-len(b))/10,
        float(source["record_id"] == candidate["record_id"]), float(source["line_id"] == candidate["line_id"]),
        float(source["paragraph_id"] == candidate["paragraph_id"]), float(source["page_id"] == candidate["page_id"]),
        float(source["register_id"] == candidate["register_id"]), float(source["hand_id"] == candidate["hand_id"]),
        float(source["layout_role"] == candidate["layout_role"]),
        math.log1p(candidate["ctx_frequency"])/10, math.log1p(source["ctx_frequency"])/10,
        candidate["ctx_record_fraction"], source["ctx_record_fraction"],
        float(candidate["separator_after"] not in {"JOIN", "SPACE"}),
        float(source["separator_before"] not in {"JOIN", "SPACE"}),
        float(source["ctx_prev_surface"] == candidate["ctx_prev_surface"]),
        float(source["ctx_next_surface"] == candidate["ctx_next_surface"]),
        float((source["separator_before"], source["separator_after"]) == (candidate["separator_before"], candidate["separator_after"])),
    ], dtype=np.float64)


def deterministic_negatives(candidates: list[int], true_index: int, source: dict, rows: list[dict], limit: int = 24) -> list[int]:
    available = [i for i in candidates if i != true_index]
    if len(available) <= limit:
        return available
    chosen = {available[-1]}
    same_form = [i for i in available if rows[i]["surface_key"] == source["surface_key"]]
    same_record = [i for i in available if rows[i]["record_id"] == source["record_id"]]
    if same_form: chosen.add(same_form[-1])
    if same_record: chosen.add(same_record[-1])
    rng = random.Random(int(hashlib.sha256((source["event_id"] + "|GDT397").encode()).hexdigest()[:16], 16))
    remainder = [i for i in available if i not in chosen]
    rng.shuffle(remainder)
    chosen.update(remainder[:max(0, limit-len(chosen))])
    return sorted(chosen)


def fit_pair_ranker(training_queries: list[tuple[list[dict], int, int, list[int]]]) -> np.ndarray:
    xrows = []; y = []; weights = []
    for rows, source_index, true_index, candidates in training_queries:
        source = rows[source_index]
        negatives = deterministic_negatives(candidates, true_index, source, rows)
        xrows.append(pair_features(source, rows[true_index])); y.append(1.0); weights.append(max(1, len(negatives)))
        for candidate in negatives:
            xrows.append(pair_features(source, rows[candidate])); y.append(0.0); weights.append(1.0)
    if not xrows:
        raise RuntimeError("pair ranker has no training queries")
    return ridge_coefficients(np.vstack(xrows), np.asarray(y), np.asarray(weights))[:, 0]


def rank_of(scores: np.ndarray, candidates: list[int], true_index: int) -> int:
    order = sorted(range(len(candidates)), key=lambda j: (-scores[j], -candidates[j]))
    return 1 + order.index(candidates.index(true_index))


def reference_queries(world: str, rows: list[dict]) -> list[tuple[list[dict], int, int, list[int]]]:
    event_index = {row["event_id"]: i for i, row in enumerate(rows)}
    relation = "PREVIOUS_MENTION" if world == "W02" else "REFERENCE"
    result = []
    for i, row in enumerate(rows):
        oracle = row["oracle"]
        target = event_index.get(oracle["relation_target_event_id"])
        if oracle["relation_type"] == relation and target is not None and target < i:
            result.append((rows, i, target, list(range(i))))
    return result


def reference_folds(world: str, data: dict[int, list[dict]]) -> list[dict]:
    query_sets = {seed: reference_queries(world, data[seed]) for seed in SEEDS}
    folds = []
    for held in SEEDS:
        model = fit_pair_ranker([q for seed in SEEDS if seed != held for q in query_sets[seed]])
        reciprocal = []; hits = []
        base_rr = {name: [] for name in ("recency", "same_form", "same_record")}
        base_hit = {name: [] for name in base_rr}
        for rows, source_index, true_index, candidates in query_sets[held]:
            source = rows[source_index]
            scores = np.asarray([pair_features(source, rows[candidate]) @ model for candidate in candidates])
            rank = rank_of(scores, candidates, true_index)
            reciprocal.append(1/rank); hits.append(rank == 1)
            baseline_scores = {
                "recency": np.asarray(candidates, dtype=float),
                "same_form": np.asarray([1e9*int(rows[c]["surface_key"] == source["surface_key"]) + c for c in candidates]),
                "same_record": np.asarray([1e9*int(rows[c]["record_id"] == source["record_id"]) + c for c in candidates]),
            }
            for name, values in baseline_scores.items():
                brank = rank_of(values, candidates, true_index)
                base_rr[name].append(1/brank); base_hit[name].append(brank == 1)
        mrr = float(np.mean(reciprocal)); hit = float(np.mean(hits))
        bmrr = {name: float(np.mean(values)) for name, values in base_rr.items()}
        bhit = {name: float(np.mean(values)) for name, values in base_hit.items()}
        strong = all(mrr >= value + .05 for value in bmrr.values()) and all(hit >= value + .03 for value in bhit.values())
        margin = min((mrr-max(bmrr.values())-.05)/.05, (hit-max(bhit.values())-.03)/.03)
        folds.append({"seed": held, "n": len(reciprocal), "mrr": mrr, "hits1": hit, "baseline_mrr": bmrr, "baseline_hits1": bhit, "strong": bool(strong), "margin": margin})
    return folds


def scope_queries(rows: list[dict]) -> list[tuple[list[dict], int, int, list[int]]]:
    event_index = {row["event_id"]: i for i, row in enumerate(rows)}
    pairs = set()
    for row in rows:
        oracle = row["oracle"]
        start = event_index.get(oracle["scope_start_event_id"])
        end = event_index.get(oracle["scope_end_event_id"])
        if start is not None and end is not None and end > start and rows[start]["record_id"] == rows[end]["record_id"]:
            pairs.add((start, end))
    result = []
    for start, end in sorted(pairs):
        candidates = [i for i in rows[start]["ctx_record_indices"] if i > start]
        if end in candidates:
            result.append((rows, start, end, candidates))
    return result


def span_iou(start: int, predicted: int, truth: int) -> float:
    return (min(predicted, truth) - start + 1) / (max(predicted, truth) - start + 1)


def scope_folds(data: dict[int, list[dict]]) -> list[dict]:
    query_sets = {seed: scope_queries(data[seed]) for seed in SEEDS}
    folds = []
    for held in SEEDS:
        model = fit_pair_ranker([q for seed in SEEDS if seed != held for q in query_sets[seed]])
        accuracy = []; iou = []; end_accuracy = []; end_iou = []; fixed_accuracy = []; fixed_iou = []
        for rows, start, truth, candidates in query_sets[held]:
            source = rows[start]
            scores = np.asarray([pair_features(source, rows[candidate]) @ model for candidate in candidates])
            predicted = candidates[int(np.argmax(scores))]
            record_end = candidates[-1]
            fixed = min(start + 3, record_end)
            accuracy.append(predicted == truth); iou.append(span_iou(start, predicted, truth))
            end_accuracy.append(record_end == truth); end_iou.append(span_iou(start, record_end, truth))
            fixed_accuracy.append(fixed == truth); fixed_iou.append(span_iou(start, fixed, truth))
        acc = float(np.mean(accuracy)); miou = float(np.mean(iou))
        bacc = {"record_end": float(np.mean(end_accuracy)), "fixed_3": float(np.mean(fixed_accuracy))}
        biou = {"record_end": float(np.mean(end_iou)), "fixed_3": float(np.mean(fixed_iou))}
        strong = all(acc >= value + .10 for value in bacc.values()) and all(miou >= value + .05 for value in biou.values())
        margin = min((acc-max(bacc.values())-.10)/.10, (miou-max(biou.values())-.05)/.05)
        folds.append({"seed": held, "n": len(accuracy), "accuracy": acc, "iou": miou, "baseline_accuracy": bacc, "baseline_iou": biou, "strong": bool(strong), "margin": margin})
    return folds


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return float(np.mean(values)) if values else float("nan")


def fmt(value: float | int | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "NA"
    return f"{float(value):.6f}"


def result_row(**kwargs: object) -> dict[str, str]:
    row = {field: "" for field in FIELDS}
    for key, value in kwargs.items():
        if key not in row:
            raise KeyError(key)
        row[key] = str(value)
    return row


def summary_row(endpoint: str, world: str, view: str, folds: list[dict], kind: str) -> dict[str, str]:
    if kind == "lexical":
        flex = [fold["flex"] for fold in folds]; base = [fold["base"] for fold in folds]
        metrics = ("NMI", "ARI", "PAIR_F1")
        values = [mean(item[i] for item in flex) for i in range(3)]
        bases = [mean(item[i] for item in base) for i in range(3)]
    elif kind == "role":
        metrics = ("AUROC", "AVERAGE_PRECISION", "PREVALENCE")
        values = [mean(fold["flex"][i] for fold in folds) for i in range(3)]
        bases = [mean(fold["base"][0] for fold in folds), mean(fold["base"][1] for fold in folds), values[2]]
    elif kind == "reference":
        metrics = ("MRR", "HITS_AT_1", "MAX_BASELINE_MRR")
        values = [mean(fold["mrr"] for fold in folds), mean(fold["hits1"] for fold in folds), mean(max(fold["baseline_mrr"].values()) for fold in folds)]
        bases = [values[2], mean(max(fold["baseline_hits1"].values()) for fold in folds), values[2]]
    elif kind == "scope":
        metrics = ("ENDPOINT_ACCURACY", "SPAN_IOU", "MAX_BASELINE_ACCURACY")
        values = [mean(fold["accuracy"] for fold in folds), mean(fold["iou"] for fold in folds), mean(max(fold["baseline_accuracy"].values()) for fold in folds)]
        bases = [values[2], mean(max(fold["baseline_iou"].values()) for fold in folds), values[2]]
    else:
        raise ValueError(kind)
    return result_row(
        row_type="CEILING", endpoint=endpoint, world=world, surface=view, model="FIXED_RIDGE_OBSERVATION_CEILING",
        n=sum(fold["n"] for fold in folds), n_positive=sum(fold.get("positive", fold["n"]) for fold in folds),
        metric_1=metrics[0], value_1=fmt(values[0]), baseline_1=fmt(bases[0]),
        metric_2=metrics[1], value_2=fmt(values[1]), baseline_2=fmt(bases[1]),
        metric_3=metrics[2], value_3=fmt(values[2]), baseline_3=fmt(bases[2]),
        strong_folds=sum(fold["strong"] for fold in folds), total_folds=5, capacity="POWERED",
        details_json=json.dumps(folds, sort_keys=True, separators=(",", ":")),
    )


def checked_claim_rows(relative: str, claim_bindings: dict[str, str]) -> list[dict[str, str]]:
    if "396200" in relative or "/W10/" not in relative:
        raise RuntimeError(f"forbidden claim path: {relative}")
    expected = claim_bindings.get(relative)
    if expected is None:
        raise RuntimeError(f"unfrozen claim path: {relative}")
    path = CLAIMS / relative
    if sha256(path) != expected:
        raise RuntimeError(f"claim hash mismatch: {relative}")
    return read_tsv_gz(path)


def w10_audit(w10_data: dict[str, dict[int, list[dict]]]) -> list[dict[str, str]]:
    freeze = json.loads((G396 / "artifacts/gdt396_qualification_claim_freeze.json").read_text())
    bindings = freeze["claim_bindings"]
    formal = {}
    for seed in SEEDS:
        rows = w10_data["FREE_RAW"][seed]
        for row in rows:
            oracle = row["oracle"]
            if oracle["relation_type"] != "NONE" or oracle["relation_target_event_id"] != "NONE":
                raise RuntimeError("W10 unexpectedly contains a relation edge")
        formal[seed] = {row["event_id"]: row["oracle"] for row in rows}

    partition_route: dict[tuple, dict[int, dict[str, tuple[float, float, float]]]] = defaultdict(dict)
    gate_route: dict[tuple, dict[int, tuple[float, float, float]]] = defaultdict(dict)
    invented = Counter(); attempted = Counter()
    for decoder in DECODERS:
        for surface in SURFACE_DIRS:
            for seed in SEEDS:
                seed_dir = CLAIMS / "qualification" / decoder / surface / "W10" / str(seed)
                if not seed_dir.is_dir():
                    raise RuntimeError(f"missing frozen W10 claims: {seed_dir}")
                for rep_dir in sorted(path for path in seed_dir.iterdir() if path.is_dir()):
                    route = (decoder, surface, rep_dir.name)
                    base_rel = f"qualification/{decoder}/{surface}/W10/{seed}/{rep_dir.name}"
                    parts = checked_claim_rows(f"{base_rel}/partition_claims.tsv.gz", bindings)
                    selected = [row for row in parts if row["property_id"] == "FUNCTION_OPERATOR_CLASS" and row["claim_status"] == "RESOLVED"]
                    if selected:
                        by_event = {row["unit_id"]: row["cluster_id"] for row in selected if row["unit_id"] in formal[seed]}
                        ids = sorted(by_event)
                        clusters = [by_event[event_id] for event_id in ids]
                        targets = {
                            "CONSTRUCTION": [formal[seed][event_id]["construction_id"] for event_id in ids],
                            "RECORD_SCHEMA": [formal[seed][event_id]["record_schema_id"] for event_id in ids],
                            "STATE_TRANSITION": [formal[seed][event_id]["state_before"] + ">" + formal[seed][event_id]["state_after"] for event_id in ids],
                        }
                        partition_route[route][seed] = {name: contingency_metrics(values, clusters) for name, values in targets.items()}

                    binaries = checked_claim_rows(f"{base_rel}/binary_claims.tsv.gz", bindings)
                    selected_binary = [row for row in binaries if row["property_id"] == "TEMPORAL_STATE_GATE" and row["claim_status"] == "RESOLVED" and row["unit_id"] in formal[seed]]
                    if selected_binary:
                        truth = [int(formal[seed][row["unit_id"]]["scope_end_event_id"] == row["unit_id"]) for row in selected_binary]
                        score = [float(row["confidence"]) if row["predicted_bool"] == "TRUE" else 1-float(row["confidence"]) for row in selected_binary]
                        gate_route[route][seed] = auc_ap(truth, score)

                    queries = checked_claim_rows(f"{base_rel}/target_queries.tsv.gz", bindings)
                    for row in queries:
                        if row["property_id"] not in {"REFERENCE_ANAPHORA", "ALTERNATIVE_RELATION"} or row["claim_status"] != "RESOLVED":
                            continue
                        key = (row["property_id"], surface)
                        attempted[key] += 1
                        if int(row["predicted_target_count"]) > 0:
                            invented[key] += 1

    rows = []
    aligned_routes = 0; best_alignment = None
    for route, seeds in partition_route.items():
        for target in ("CONSTRUCTION", "RECORD_SCHEMA", "STATE_TRANSITION"):
            values = [(seed, metrics[target]) for seed, metrics in seeds.items() if target in metrics]
            strong = sum(metric[0] >= .25 and metric[1] >= .10 for _, metric in values)
            record = (strong, mean(metric[0] for _, metric in values), mean(metric[1] for _, metric in values), route, target)
            if strong >= 4:
                aligned_routes += 1
            if best_alignment is None or record[:3] > best_alignment[:3]:
                best_alignment = record
    if best_alignment:
        strong, nmi, ari, route, target = best_alignment
        rows.append(result_row(row_type="W10_AUDIT", endpoint="ANONYMOUS_CONTROL_ROLE", world="W10", surface=route[1], model=route[0]+"/"+route[2],
            metric_1="FORMAL_PARTITION_NMI", value_1=fmt(nmi), metric_2="FORMAL_PARTITION_ARI", value_2=fmt(ari),
            strong_folds=strong, total_folds=5, capacity="FORMAL_TRUTH_PRESENT", details_json=json.dumps({"aligned_routes": aligned_routes, "formal_target": target}, sort_keys=True),
            note="Existing semantic-labeled claim rescored only as anonymous formal-partition alignment."))
    best_gate = None
    for route, seeds in gate_route.items():
        record = (mean(value[0] for value in seeds.values()), mean(value[1] for value in seeds.values()), route, len(seeds), mean(value[2] for value in seeds.values()))
        if best_gate is None or record[:2] > best_gate[:2]:
            best_gate = record
    if best_gate:
        auc, ap, route, count, prevalence = best_gate
        rows.append(result_row(row_type="W10_AUDIT", endpoint="STATE_GATE_OR_SCOPE_ENDPOINT", world="W10", surface=route[1], model=route[0]+"/"+route[2],
            metric_1="FORMAL_SCOPE_END_AUROC", value_1=fmt(auc), baseline_1="0.500000",
            metric_2="FORMAL_SCOPE_END_AP", value_2=fmt(ap), baseline_2=fmt(prevalence), total_folds=count,
            capacity="FORMAL_SCOPE_PRESENT", note="Existing semantic-labeled gate claim rescored only against actual formal scope ends."))
    for property_id in ("REFERENCE_ANAPHORA", "ALTERNATIVE_RELATION"):
        for surface in SURFACE_DIRS:
            key = (property_id, surface); n = attempted[key]; fp = invented[key]
            rows.append(result_row(row_type="W10_AUDIT", endpoint=("REFERENCE_OR_REUSE_EDGE" if property_id == "REFERENCE_ANAPHORA" else "ALTERNATIVE_OR_BRANCH_TOPOLOGY"),
                world="W10", surface=surface, model="FROZEN_GDT396_CLAIMS", n=n, n_positive=fp,
                metric_1="INVENTED_EDGE_RATE", value_1=fmt(fp/n if n else float("nan")), baseline_1="0.000000",
                capacity="FORMAL_EDGE_ABSENT", note="Every positive ranked edge is an invented formal relation because W10 oracle contains no edge."))
    return rows


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT}")
    if any(seed >= 3962000 for seed in SEEDS):
        raise RuntimeError("confirmation seed prohibited")
    manifest = load_manifest()
    all_data = {world: load_world(world, manifest) for world in AUDIT_WORLDS}
    output_rows: list[dict[str, str]] = []
    fold_store: dict[tuple[str, str, str], list[dict]] = {}

    for world in MEANINGFUL_WORLDS:
        for view in VIEWS:
            data = all_data[world][view]
            lex = lexical_folds(data); role = role_folds(world, data)
            reference = reference_folds(world, data); scope = scope_folds(data)
            fold_store[("LEXICAL_IDENTITY", world, view)] = lex
            fold_store[("ANONYMOUS_CONTROL_ROLE", world, view)] = role
            fold_store[("REFERENCE_OR_REUSE_EDGE", world, view)] = reference
            fold_store[("STATE_GATE_OR_SCOPE_ENDPOINT", world, view)] = scope
            output_rows.extend((
                summary_row("LEXICAL_IDENTITY", world, view, lex, "lexical"),
                summary_row("ANONYMOUS_CONTROL_ROLE", world, view, role, "role"),
                summary_row("REFERENCE_OR_REUSE_EDGE", world, view, reference, "reference"),
                summary_row("STATE_GATE_OR_SCOPE_ENDPOINT", world, view, scope, "scope"),
            ))

    for world in MEANINGFUL_WORLDS:
        counts = []
        for seed in SEEDS:
            rows = all_data[world]["FREE_RAW"][seed]
            counts.append(sum(row["oracle"]["relation_type"] in {"ALTERNATIVE", "ALTERNATIVE_TO", "SUBSTITUTE"} for row in rows))
        output_rows.append(result_row(row_type="CAPACITY", endpoint="ALTERNATIVE_OR_BRANCH_TOPOLOGY", world=world, surface="ALL",
            model="NOT_FIT", n=sum(counts), n_positive=sum(counts), metric_1="MIN_POSITIVES_PER_SEED", value_1=min(counts),
            strong_folds=sum(count >= 25 for count in counts), total_folds=5,
            capacity="POWERED" if min(counts) >= 25 else "INSUFFICIENT", details_json=json.dumps(counts)))

    for endpoint in ("LEXICAL_IDENTITY", "ANONYMOUS_CONTROL_ROLE", "REFERENCE_OR_REUSE_EDGE", "STATE_GATE_OR_SCOPE_ENDPOINT"):
        for world in MEANINGFUL_WORLDS:
            free = fold_store[(endpoint, world, "FREE_RAW")]
            decoded = fold_store[(endpoint, world, "VOYNICH_ATOM_DECODED")]
            if canonical_hash(free) != canonical_hash(decoded):
                raise RuntimeError(f"atom-decoded ceiling does not restore FREE result: {endpoint}/{world}")

    def endpoint_pass(endpoint: str) -> bool:
        return all(sum(fold["strong"] for fold in fold_store[(endpoint, world, "VOYNICH_ATOM_DECODED")]) >= 4 for world in MEANINGFUL_WORLDS)

    lexical_pass = endpoint_pass("LEXICAL_IDENTITY")
    passes = {
        endpoint: endpoint_pass(endpoint) for endpoint in
        ("ANONYMOUS_CONTROL_ROLE", "REFERENCE_OR_REUSE_EDGE", "STATE_GATE_OR_SCOPE_ENDPOINT")
    }
    decisions = {
        "LEXICAL_IDENTITY": "CURRENT_GDT396_RESULT_WAS_GATE_CONTAMINATION" if lexical_pass else "NOT_OBSERVABLE_UNDER_CURRENT_CHANNEL",
        "ANONYMOUS_CONTROL_ROLE": "STRUCTURAL_ROLE_RECOVERABLE_SEMANTIC_LABEL_NOT_IDENTIFIABLE" if passes["ANONYMOUS_CONTROL_ROLE"] else "NOT_OBSERVABLE_UNDER_CURRENT_CHANNEL",
        "REFERENCE_OR_REUSE_EDGE": "STRUCTURAL_ROLE_RECOVERABLE_SEMANTIC_LABEL_NOT_IDENTIFIABLE" if passes["REFERENCE_OR_REUSE_EDGE"] else "NOT_OBSERVABLE_UNDER_CURRENT_CHANNEL",
        "ALTERNATIVE_OR_BRANCH_TOPOLOGY": "CAPACITY_INSUFFICIENT",
        "STATE_GATE_OR_SCOPE_ENDPOINT": "STRUCTURAL_ROLE_RECOVERABLE_SEMANTIC_LABEL_NOT_IDENTIFIABLE" if passes["STATE_GATE_OR_SCOPE_ENDPOINT"] else "NOT_OBSERVABLE_UNDER_CURRENT_CHANNEL",
        "REFERENTIAL_SEMANTICS": "NONIDENTIFIABLE_BY_OBSERVATIONAL_EQUIVALENCE",
    }
    modeled_endpoints = {"LEXICAL_IDENTITY", *passes}
    for endpoint, decision in decisions.items():
        strong = "NA"
        total = "NA"
        if endpoint in modeled_endpoints:
            strong = min(sum(fold["strong"] for fold in fold_store[(endpoint, world, "VOYNICH_ATOM_DECODED")]) for world in MEANINGFUL_WORLDS)
            total = 5
        output_rows.append(result_row(row_type="ENDPOINT_DECISION", endpoint=endpoint, world="ALL", surface="VOYNICH_ATOM_DECODED" if endpoint != "REFERENTIAL_SEMANTICS" else "IDENTICAL_PACKET",
            model="FROZEN_DECISION_RULE", capacity="POWERED" if decision != "CAPACITY_INSUFFICIENT" else "INSUFFICIENT", decision=decision,
            strong_folds=strong, total_folds=total))

    witness_manifest = manifest[("W09", 3961000)]
    obs_path = checked_input(witness_manifest["free_observation_relpath"], witness_manifest["free_observation_sha256"])
    oracle_path = checked_input(witness_manifest["oracle_relpath"], witness_manifest["oracle_sha256"])
    oracle_rows = read_tsv_gz(oracle_path)
    formal_fields = ("event_id", "relation_target_event_id", "state_before", "state_after", "construction_id", "scope_start_event_id", "scope_end_event_id", "record_schema_id", "register_realization_id")
    formal_projection = [{field: row[field] for field in formal_fields} for row in oracle_rows]
    for interpretation, ihash, note in (
        ("A_ORIGINAL_SEMANTIC_ORACLE", sha256(oracle_path), "Original exposed semantic interpretation."),
        ("B_FORMAL_ONLY", canonical_hash(formal_projection), "External entities and readable semantic/function/relation labels removed; formal edges retained anonymously."),
    ):
        output_rows.append(result_row(row_type="OBSERVATIONAL_EQUIVALENCE_WITNESS", endpoint="REFERENTIAL_SEMANTICS", world="W09", surface="FREE_RAW", model=interpretation,
            n=len(oracle_rows), capacity="LOGICAL_PROOF", decision="NONIDENTIFIABLE_BY_OBSERVATIONAL_EQUIVALENCE",
            observation_sha256=sha256(obs_path), interpretation_sha256=ihash, note=note))

    output_rows.extend(w10_audit(all_data["W10"]))

    passing = [endpoint for endpoint, value in passes.items() if value]
    nominee = "NONE"
    if passing:
        margins = {}
        for endpoint in passing:
            world_margins = []
            for world in MEANINGFUL_WORLDS:
                ordered = sorted((fold["margin"] for fold in fold_store[(endpoint, world, "VOYNICH_ATOM_DECODED")]), reverse=True)
                world_margins.append(ordered[3])
            margins[endpoint] = min(world_margins)
        nominee = max(sorted(passing), key=lambda endpoint: margins[endpoint])
    output_rows.append(result_row(row_type="HARD_STOP", endpoint="OPERATOR_DECODER_DEVELOPMENT", world="ALL", surface="VOYNICH_ATOM_DECODED", model="REGISTERED_HARD_STOP",
        capacity="PASS" if nominee != "NONE" else "STOP", details_json=json.dumps({"passing_operator_endpoints": passing, "single_future_nominee": nominee}, sort_keys=True),
        note=("Only the named endpoint may justify a future targeted decoder; GDT397 starts nothing." if nominee != "NONE" else "Close further internal operator-decoder development under the current observations.")))

    for row in output_rows:
        if row["decision"] and row["decision"] not in DECISIONS:
            raise RuntimeError(f"unregistered decision: {row['decision']}")
        if "396200" in json.dumps(row) or "f84" in json.dumps(row).lower():
            raise RuntimeError("forbidden seed/page token in output")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(output_rows)
    print(OUTPUT)
    print("rows", len(output_rows), "sha256", sha256(OUTPUT), "nominee", nominee)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
