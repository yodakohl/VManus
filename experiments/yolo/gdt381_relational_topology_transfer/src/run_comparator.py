#!/usr/bin/env python3
"""Run GDT381 comparator-local clustering and topology transfer; no Voynich."""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
import multiprocessing as mp
import os
from collections import Counter, defaultdict
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt381_relational_topology_transfer"
ART = BASE / "artifacts"
G378 = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer/artifacts"
OBS = G378 / "gdt378_comparator_observation_layer.tsv.gz"
ORACLE = G378 / "gdt378_hidden_oracle.tsv.gz"
CONTRACT = G378 / "gdt378_oracle_contract.json"
DESIGN = ART / "gdt381_comparator_topology_freeze.json"

FAMILIES = [
    ("CMP_TOPOLOGY_01", "UNTIL_STATE_GATE", "PERSISTENT_STATE_GATE_EXIT"),
    ("CMP_TOPOLOGY_02", "ALTERNATIVE_OR", "BRANCH_ALTERNATIVES_RECONVERGENCE"),
    ("CMP_TOPOLOGY_03", "POLARITY_EXCLUSION", "MARKED_COUNTERPART_INVERSE_DELTA"),
    ("CMP_TOPOLOGY_04", "COORDINATOR", "HOMOGENEOUS_LINK_VARIABLE_ARITY"),
    ("CMP_TOPOLOGY_05", "NEXT_RESUME", "LOCAL_RESET_RESUME_NEXT"),
]
PROCEDURAL = {"CURIOUS_CURES", "HARLEIAN_COOKERY", "QUINTE_ESSENCE"}
HORIZONS = (1, 2, 4, 8)
_KX = None


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content(obj: dict) -> str:
    clone = dict(obj); clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_tsv(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict]) -> None:
    if path.suffix == ".gz":
        raw = path.open("wb"); gz = gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0)
        handle = io.TextIOWrapper(gz, encoding="utf-8", newline="")
    else:
        handle = path.open("w", encoding="utf-8", newline="")
    with handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def write_json(path: Path, obj: dict) -> None:
    obj["content_hash"] = content(obj)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def distance_matrix(X: np.ndarray, centers: np.ndarray) -> np.ndarray:
    return np.maximum(0.0, np.sum(X * X, axis=1)[:, None] + np.sum(centers * centers, axis=1)[None, :] - 2 * X @ centers.T)


def kmeans_one(task):
    k, seed = task
    X = _KX
    rng = np.random.default_rng(seed)
    centers = np.empty((k, X.shape[1]), dtype=float)
    centers[0] = X[rng.integers(len(X))]
    closest = np.sum((X - centers[0]) ** 2, axis=1)
    for c in range(1, k):
        total = float(closest.sum())
        idx = int(rng.integers(len(X))) if total <= 0 else int(rng.choice(len(X), p=closest / total))
        centers[c] = X[idx]
        closest = np.minimum(closest, np.sum((X - centers[c]) ** 2, axis=1))
    previous = None
    for _ in range(20):
        distances = distance_matrix(X, centers)
        labels = np.argmin(distances, axis=1)
        if previous is not None and np.array_equal(labels, previous):
            break
        previous = labels.copy()
        new = centers.copy()
        for c in range(k):
            ids = np.where(labels == c)[0]
            if len(ids): new[c] = X[ids].mean(axis=0)
            else: new[c] = X[int(np.argmax(np.min(distances, axis=1)))]
        if np.max(np.abs(new - centers)) < 1e-6:
            centers = new; break
        centers = new
    distances = distance_matrix(X, centers)
    labels = np.argmin(distances, axis=1)
    inertia = float(distances[np.arange(len(X)), labels].sum())
    return k, seed, inertia, labels


def choose_clusters(X: np.ndarray, domain_ordinal: int, k_grid: list[int]):
    global _KX
    mu = X.mean(axis=0); sd = X.std(axis=0); sd[sd < 1e-8] = 1.0
    Z = (X - mu) / sd
    i1 = float(np.sum((Z - Z.mean(axis=0)) ** 2))
    _KX = Z
    tasks = []
    for k in k_grid:
        if k <= len(Z):
            for restart in range(20): tasks.append((k, 381001 + domain_ordinal * 10000 + k * 100 + restart))
    context = mp.get_context("fork")
    with context.Pool(processes=min(24, os.cpu_count() or 1)) as pool:
        results = pool.map(kmeans_one, tasks)
    best = {}
    for k, seed, inertia, labels in results:
        if k not in best or (inertia, seed) < (best[k][0], best[k][1]): best[k] = (inertia, seed, labels)
    max_k = max(best); max_reduction = max(i1 - best[max_k][0], 1e-9)
    selected = max_k
    for k in sorted(best):
        if (i1 - best[k][0]) / max_reduction >= 0.80:
            selected = k; break
    inertia, seed, labels = best[selected]
    return labels, selected, seed, i1, {k: best[k][0] for k in sorted(best)}


def js_divergence(left: list[int], right: list[int]) -> float:
    if not left or not right: return 0.0
    keys = sorted(set(left) | set(right)); lc = Counter(left); rc = Counter(right)
    p = np.array([lc[k] / len(left) for k in keys]); q = np.array([rc[k] / len(right) for k in keys]); m = (p + q) / 2
    def kl(a, b):
        mask = a > 0
        return float(np.sum(a[mask] * np.log2(a[mask] / b[mask])))
    return (kl(p, m) + kl(q, m)) / 2


def jaccard(left: set[int], right: set[int]) -> float:
    return len(left & right) / max(1, len(left | right))


def build_type_profiles(obs: list[dict], indices: list[int]):
    records = defaultdict(list)
    for i in indices: records[(obs[i]["collection_id"], obs[i]["record_id"])].append(i)
    forms = sorted({obs[i]["opaque_form_id"] for i in indices})
    fi = {form: j for j, form in enumerate(forms)}
    profile = np.zeros((len(forms), 22), float); counts = np.zeros(len(forms), int)
    record_sets = defaultdict(set); collection_sets = defaultdict(set); prev_sets = defaultdict(set); next_sets = defaultdict(set)
    equal_count = Counter(); repeat_left = Counter(); repeat_right = Counter()
    for record, ids in records.items():
        ids.sort(key=lambda i: int(obs[i]["element_ordinal"])); seq = [obs[i]["opaque_form_id"] for i in ids]; cnt = Counter(seq)
        for j, idx in enumerate(ids):
            form = seq[j]; q = fi[form]; counts[q] += 1; row = obs[idx]
            pbin = min(4, int(float(row["relative_position"]) * 5)); profile[q, pbin] += 1
            m = len(seq); lbin = 0 if m <= 8 else 1 if m <= 16 else 2 if m <= 32 else 3; profile[q, 5 + lbin] += 1
            profile[q, 9] += int(row["boundary_before"] == "1"); profile[q, 10] += int(row["boundary_after"] == "1")
            profile[q, 11] += math.log1p(cnt[form]); profile[q, 12] += float(j == 0); profile[q, 13] += float(j == m - 1)
            record_sets[form].add(record); collection_sets[form].add(record[0])
            if j: prev_sets[form].add(seq[j - 1])
            if j + 1 < m: next_sets[form].add(seq[j + 1])
            equal_count[form] += int(j > 0 and j + 1 < m and seq[j - 1] == seq[j + 1])
            repeat_left[form] += int(form in seq[max(0, j - 4):j]); repeat_right[form] += int(form in seq[j + 1:min(m, j + 5)])
    total_records = len(records); total_collections = len({key[0] for key in records})
    for form, q in fi.items():
        n = max(1, counts[q]); profile[q, :14] /= n
        profile[q, 14] = math.log1p(len(record_sets[form])) / math.log1p(max(1, total_records))
        profile[q, 15] = len(collection_sets[form]) / max(1, total_collections)
        profile[q, 16] = math.log1p(len(prev_sets[form])) / math.log1p(n + 1)
        profile[q, 17] = math.log1p(len(next_sets[form])) / math.log1p(n + 1)
        profile[q, 18] = equal_count[form] / n; profile[q, 19] = repeat_left[form] / n; profile[q, 20] = repeat_right[form] / n
        profile[q, 21] = math.log1p(n)
    return forms, profile, records


def build_topology(obs: list[dict], domain_indices: dict[str, list[int]], design: dict):
    event_class = np.full(len(obs), -1, int); class_rows = []; cluster_meta = {}
    for dord, domain in enumerate(sorted(domain_indices)):
        forms, profile, _ = build_type_profiles(obs, domain_indices[domain])
        labels, k, seed, i1, inertias = choose_clusters(profile, dord, design["latent_classes"]["k_grid"])
        mapping = dict(zip(forms, labels.tolist())); cluster_meta[domain] = {"k": k, "seed": seed, "i1": i1, "inertias": inertias}
        token_counts = Counter(); type_counts = Counter(labels.tolist())
        for idx in domain_indices[domain]:
            cls = mapping[obs[idx]["opaque_form_id"]]; event_class[idx] = cls; token_counts[cls] += 1
        for cls in range(k):
            class_rows.append({"domain": domain, "local_class": cls, "type_count": type_counts[cls], "token_count": token_counts[cls], "token_fraction": f"{token_counts[cls] / len(domain_indices[domain]):.9f}", "cross_domain_alignment": 0, "semantic_state": "UNASSIGNED"})
    assert np.all(event_class >= 0)

    records = defaultdict(list)
    for i, row in enumerate(obs): records[(row["domain"], row["collection_id"], row["record_id"])].append(i)
    graph = {}
    for domain in domain_indices:
        edges = Counter(); class_count = Counter(); out = defaultdict(set); inn = defaultdict(set)
        for record, ids in records.items():
            if record[0] != domain: continue
            ids.sort(key=lambda i: int(obs[i]["element_ordinal"])); seq = [event_class[i] for i in ids]; class_count.update(seq)
            for a, b in zip(seq, seq[1:]): edges[a, b] += 1; out[a].add(b); inn[b].add(a)
        graph[domain] = (edges, class_count, out, inn)

    nuisance_names = ["INTERCEPT", "LOG_RECORD_LENGTH", "RELATIVE_POSITION", "RELATIVE_POSITION_SQ", "BOUNDARY_BEFORE", "BOUNDARY_AFTER", "LOG_WITHIN_RECORD_RECURRENCE", "IS_RECORD_START", "IS_RECORD_END"]
    trivial_names = ["PREV_EQUALS_NEXT", "PREV_CLASS_CHANGE", "NEXT_CLASS_CHANGE", "LOG_CURRENT_CLASS_SIZE", "CURRENT_CLASS_SIZE_RANK", "LOG_PREV_OUTDEGREE", "LOG_NEXT_INDEGREE", "LOG_PREV_CURRENT_EDGE", "LOG_CURRENT_NEXT_EDGE"]
    full_names = ["ALT_TWO_EDGE_MIDDLE_COUNT", "ALT_TWO_EDGE_MIDDLE_LOG", "DELETE_BRIDGE_LOG_SUPPORT", "CHAIN_A_C_A_C", "CHAIN_C_A_C_A"]
    for h in HORIZONS:
        full_names.extend([f"H{h}_CLASS_SET_JACCARD", f"H{h}_CLASS_JS_DIVERGENCE", f"H{h}_RECONVERGENCE", f"H{h}_CURRENT_RETURN_LEFT", f"H{h}_CURRENT_RETURN_RIGHT", f"H{h}_PREVIOUS_CLASS_RESUME", f"H{h}_PERSISTENT_PRE_EXIT", f"H{h}_POST_NOVELTY", f"H{h}_UNIQUE_CLASS_DELTA"])
    nuisance = np.zeros((len(obs), len(nuisance_names))); trivial = np.zeros((len(obs), len(trivial_names))); full = np.zeros((len(obs), len(full_names)))
    class_size_quartile = np.zeros(len(obs), int)
    for record, ids in records.items():
        ids.sort(key=lambda i: int(obs[i]["element_ordinal"])); seq = [event_class[i] for i in ids]; cnt = Counter(seq); m = len(seq)
        edges, class_count, out, inn = graph[record[0]]; sizes = np.array([class_count[c] for c in sorted(class_count)]); cuts = np.quantile(sizes, [.25, .5, .75])
        for j, idx in enumerate(ids):
            row = obs[idx]; cur = seq[j]; prev = seq[j - 1] if j else -1; nxt = seq[j + 1] if j + 1 < m else -2
            nuisance[idx] = [1, math.log1p(m), float(row["relative_position"]), float(row["relative_position"]) ** 2, int(row["boundary_before"] == "1"), int(row["boundary_after"] == "1"), math.log1p(cnt[cur]), int(j == 0), int(j == m - 1)]
            rank = sum(v <= class_count[cur] for v in sizes) / len(sizes); class_size_quartile[idx] = int(np.searchsorted(cuts, class_count[cur], side="right"))
            trivial[idx] = [int(prev == nxt and j > 0 and j + 1 < m), int(prev != cur and j > 0), int(nxt != cur and j + 1 < m), math.log1p(class_count[cur]), rank, math.log1p(len(out[prev])) if j else 0, math.log1p(len(inn[nxt])) if j + 1 < m else 0, math.log1p(edges[prev, cur]) if j else 0, math.log1p(edges[cur, nxt]) if j + 1 < m else 0]
            mids = set(out[prev]) & set(inn[nxt]) if j > 0 and j + 1 < m else set(); alt = max(0, len(mids) - 1)
            fv = [alt, math.log1p(alt), math.log1p(edges[prev, nxt]) if j > 0 and j + 1 < m else 0, int(j >= 2 and j + 1 < m and seq[j - 2] == cur and prev == nxt), int(j > 0 and j + 2 < m and prev == nxt and cur == seq[j + 2])]
            for h in HORIZONS:
                left = seq[max(0, j - h):j]; right = seq[j + 1:min(m, j + 1 + h)]; ls, rs = set(left), set(right)
                persistent = Counter(left).most_common(1)[0][0] if left else None
                fv.extend([jaccard(ls, rs), js_divergence(left, right), int(bool(ls & rs) and bool(left) and bool(right)), int(cur in ls), int(cur in rs), int(prev in rs) if j else 0, int(persistent is not None and persistent not in rs), len([x for x in right if x not in ls]) / max(1, len(right)), len(rs) / max(1, len(right)) - len(ls) / max(1, len(left))])
            full[idx] = fv
    one_step_delete = {"PREV_EQUALS_NEXT", "PREV_CLASS_CHANGE", "NEXT_CLASS_CHANGE", "CHAIN_A_C_A_C", "CHAIN_C_A_C_A"}
    reduced_trivial_ids = [i for i, name in enumerate(trivial_names) if name not in one_step_delete]
    reduced_full_ids = [i for i, name in enumerate(full_names) if name not in one_step_delete]
    return event_class, class_size_quartile, nuisance, trivial, full, nuisance_names, trivial_names, full_names, reduced_trivial_ids, reduced_full_ids, class_rows, cluster_meta


def sigmoid(x):
    z = np.clip(x, -40, 40); return np.where(z >= 0, 1 / (1 + np.exp(-z)), np.exp(z) / (1 + np.exp(z)))


def fit(X, y, domains, l2=4.0):
    X = np.asarray(X, float); y = np.asarray(y, float); counts = Counter(domains); weights = np.array([len(domains) / (len(counts) * counts[d]) for d in domains])
    mu = np.average(X[:, 1:], axis=0, weights=weights); sd = np.sqrt(np.average((X[:, 1:] - mu) ** 2, axis=0, weights=weights)); sd[sd < 1e-8] = 1
    Z = X.copy(); Z[:, 1:] = (Z[:, 1:] - mu) / sd; beta = np.zeros(Z.shape[1]); penalty = np.ones(len(beta)) * l2; penalty[0] = 0
    for _ in range(35):
        p = sigmoid(Z @ beta); work = np.maximum(p * (1 - p), 1e-6) * weights; hessian = (Z.T * work) @ Z + np.diag(penalty); gradient = Z.T @ ((y - p) * weights) - penalty * beta
        try: step = np.linalg.solve(hessian, gradient)
        except np.linalg.LinAlgError: step = np.linalg.lstsq(hessian, gradient, rcond=None)[0]
        beta += step
        if np.max(np.abs(step)) < 1e-7: break
    return beta, mu, sd


def predict(model, X):
    beta, mu, sd = model; Z = np.asarray(X, float).copy(); Z[:, 1:] = (Z[:, 1:] - mu) / sd
    return np.clip(sigmoid(Z @ beta), 1e-7, 1 - 1e-7)


def bits(y, p):
    p = np.clip(np.asarray(p), 1e-9, 1 - 1e-9); y = np.asarray(y)
    return float(-np.sum(y * np.log2(p) + (1 - y) * np.log2(1 - p)))


def rankdata(values):
    values = np.asarray(values); order = np.argsort(values, kind="stable"); ranks = np.empty(len(values), float); i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and values[order[j]] == values[order[i]]: j += 1
        ranks[order[i:j]] = (i + j + 1) / 2; i = j
    return ranks


def auc(y, score):
    y = np.asarray(y, int); n1 = int(y.sum()); n0 = len(y) - n1
    if not n1 or not n0: return float("nan")
    ranks = rankdata(score); return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def main() -> None:
    design = json.loads(DESIGN.read_text()); assert design["status"] == "FROZEN_BEFORE_HIDDEN_ORACLE_EVALUATION" and design["voynich_rows_read"] == 0
    obs = read_tsv(OBS); oracle = read_tsv(ORACLE); assert [r["element_key"] for r in obs] == [r["element_key"] for r in oracle]
    contract = json.loads(CONTRACT.read_text()); domains = np.array([r["domain"] for r in obs]); domain_indices = {d: np.where(domains == d)[0].tolist() for d in sorted(set(domains))}
    event_class, class_quartile, nuisance, trivial, relational, nuisance_names, trivial_names, relational_names, reduced_trivial_ids, reduced_relational_ids, class_rows, cluster_meta = build_topology(obs, domain_indices, design)
    Xn = nuisance; Xt = np.column_stack([nuisance, trivial]); Xf = np.column_stack([nuisance, trivial, relational]); Xr = np.column_stack([nuisance, trivial[:, reduced_trivial_ids], relational[:, reduced_relational_ids]])
    fold_rows = []; predictions = {}
    for family, endpoint, topology in FAMILIES:
        available = contract["availability"][endpoint]; y = np.array([int(r[endpoint]) for r in oracle]); pn = np.full(len(obs), np.nan); pt = pn.copy(); pf = pn.copy(); pr = pn.copy()
        for held in available:
            train = np.where(np.isin(domains, [d for d in available if d != held]))[0]; test = np.where(domains == held)[0]; td = domains[train].tolist()
            p0 = predict(fit(Xn[train], y[train], td), Xn[test]); p1 = predict(fit(Xt[train], y[train], td), Xt[test]); p2 = predict(fit(Xf[train], y[train], td), Xf[test]); p3 = predict(fit(Xr[train], y[train], td), Xr[test])
            pn[test], pt[test], pf[test], pr[test] = p0, p1, p2, p3; yy = y[test]
            fold_rows.append({"anonymous_topology": family, "held_domain": held, "n": len(test), "positives": int(yy.sum()), "auc_nuisance": f"{auc(yy,p0):.9f}", "auc_trivial": f"{auc(yy,p1):.9f}", "auc_full": f"{auc(yy,p2):.9f}", "auc_without_one_step_equality": f"{auc(yy,p3):.9f}", "gain_full_vs_nuisance_bits": f"{bits(yy,p0)-bits(yy,p2):.9f}", "gain_full_vs_trivial_bits": f"{bits(yy,p1)-bits(yy,p2):.9f}", "gain_reduced_vs_nuisance_bits": f"{bits(yy,p0)-bits(yy,p3):.9f}", "training_domains": "|".join(d for d in available if d != held)})
        predictions[family] = (y, pf, available)

    summary = []
    for family, endpoint, topology in FAMILIES:
        rows = [r for r in fold_rows if r["anonymous_topology"] == family]; aucs = {r["held_domain"]: float(r["auc_full"]) for r in rows}; gn = {r["held_domain"]: float(r["gain_full_vs_nuisance_bits"]) for r in rows}; gt = {r["held_domain"]: float(r["gain_full_vs_trivial_bits"]) for r in rows}; gr = {r["held_domain"]: float(r["gain_reduced_vs_nuisance_bits"]) for r in rows}; floor = sorted(aucs.values(), reverse=True)[2]
        proc = sorted(d for d in PROCEDURAL if aucs.get(d, 0) >= .62 and gn.get(d, 0) > 0 and gt.get(d, 0) > 0)
        summary.append({"anonymous_topology": family, "topology_family": topology, "available_domains": len(rows), "transfer_auc_floor": f"{floor:.9f}", "mean_domain_auc": f"{np.mean(list(aucs.values())):.9f}", "positive_gain_vs_nuisance_domains": sum(v > 0 for v in gn.values()), "positive_gain_vs_trivial_domains": sum(v > 0 for v in gt.values()), "positive_reduced_gain_domains": sum(v > 0 for v in gr.values()), "pceec2_auc": f"{aucs.get('PCEEC2',float('nan')):.9f}", "pceec2_gain_vs_nuisance_bits": f"{gn.get('PCEEC2',float('nan')):.9f}", "pceec2_gain_vs_trivial_bits": f"{gt.get('PCEEC2',float('nan')):.9f}", "procedural_domains_passing": "|".join(proc), "domain_aucs_json": json.dumps(aucs,sort_keys=True,separators=(",",":")), "domain_gain_nuisance_json": json.dumps(gn,sort_keys=True,separators=(",",":")), "domain_gain_trivial_json": json.dumps(gt,sort_keys=True,separators=(",",":"))})

    # Conditional held-score null. Class topology and sizes are fixed; only
    # hidden memberships move within the predeclared opportunity strata.
    strata = defaultdict(list)
    for i, row in enumerate(obs):
        n = int(row["record_element_count"]); lb = "1-8" if n <= 8 else "9-16" if n <= 16 else "17-32" if n <= 32 else "33+"; pb = min(4, int(float(row["relative_position"])*5)); boundary = row["boundary_before"] + "|" + row["boundary_after"]; f = int(row["within_record_frequency"]); fb = "1" if f <= 1 else "2" if f == 2 else "3+"
        strata[(row["domain"], row["collection_id"], lb, pb, boundary, fb, int(class_quartile[i]))].append(i)
    capacity_rows = []
    for family, endpoint, _ in FAMILIES:
        y, _, _ = predictions[family]; mixed = [ids for ids in strata.values() if len({int(y[i]) for i in ids}) > 1]
        capacity_rows.append({"anonymous_topology": family, "mobile_rows": sum(len(ids) for ids in mixed), "mobile_strata": len(mixed), "positive_rows_in_mobile": sum(int(y[i]) for ids in mixed for i in ids), "total_positive_rows": int(y.sum()), "status": "MOBILE" if mixed else "UNIDENTIFIABLE"})
    null_rows = []; local = {family: [] for family,_,_ in FAMILIES}
    for world in range(design["null"]["worlds"]):
        rng = np.random.default_rng(design["null"]["seed"] + world); perm = np.arange(len(obs))
        for ids in strata.values(): perm[ids] = rng.permutation(ids)
        values = {}
        for family, _, _ in FAMILIES:
            y, score, available = predictions[family]; yp = y[perm]; domain_aucs = [auc(yp[np.where(domains==held)[0]], score[np.where(domains==held)[0]]) for held in available]; value = sorted(domain_aucs, reverse=True)[2]; values[family] = value; local[family].append(value)
        mx = max(values.values()); null_rows.append({"world": world, **{family:f"{values[family]:.9f}" for family,_,_ in FAMILIES}, "world_max": f"{mx:.9f}"})
    maxima = [float(r["world_max"]) for r in null_rows]; eligible = []
    for row in summary:
        family = row["anonymous_topology"]; observed = float(row["transfer_auc_floor"]); lp = (1+sum(x>=observed for x in local[family]))/(1+len(local[family])); mpv = (1+sum(x>=observed for x in maxima))/(1+len(maxima)); row["local_p"] = f"{lp:.9f}"; row["max_family_p"] = f"{mpv:.9f}"
        passes = observed >= .62 and int(row["positive_gain_vs_nuisance_domains"]) >= 3 and int(row["positive_gain_vs_trivial_domains"]) >= 3 and float(row["pceec2_auc"]) >= .60 and float(row["pceec2_gain_vs_nuisance_bits"]) > 0 and float(row["pceec2_gain_vs_trivial_bits"]) > 0 and bool(row["procedural_domains_passing"]) and mpv <= .05 and int(row["positive_reduced_gain_domains"]) >= 3
        row["voynich_mapping_eligible"] = int(passes); row["status"] = "RELATIONAL_TOPOLOGY_TRANSFER_PASS" if passes else "NO_RELATIONAL_TOPOLOGY_TRANSFER"
        if passes: eligible.append(family)

    feature_rows = []
    for model, names in [("NUISANCE",nuisance_names),("TRIVIAL_MOTIF_BASELINE",trivial_names),("FULL_RELATIONAL_TOPOLOGY",relational_names)]:
        for i,name in enumerate(names,1): feature_rows.append({"model_block":model,"feature_ordinal":i,"feature":name,"class_label_invariant":1,"exact_identity_value_used":0,"semantic_state":"UNASSIGNED"})
    cluster_rows = []
    for domain, meta in cluster_meta.items():
        cluster_rows.append({"domain":domain,"selected_k":meta["k"],"winning_seed":meta["seed"],"k1_inertia":f"{meta['i1']:.9f}","candidate_inertias_json":json.dumps(meta["inertias"],sort_keys=True,separators=(",",":")),"oracle_labels_used":0,"cross_domain_alignment":0})
    write_tsv(ART/"gdt381_clustering_summary.tsv",cluster_rows); write_tsv(ART/"gdt381_latent_class_summary.tsv",class_rows); write_tsv(ART/"gdt381_topology_feature_manifest.tsv",feature_rows); write_tsv(ART/"gdt381_comparator_fold_scores.tsv",fold_rows); write_tsv(ART/"gdt381_comparator_family_summary.tsv",summary); write_tsv(ART/"gdt381_null_capacity.tsv",capacity_rows); write_tsv(ART/"gdt381_comparator_null.tsv.gz",null_rows)
    signature = {"schema":"GDT381_RELATIONAL_TOPOLOGY_SIGNATURE_FREEZE_V1","status":"TARGET_MAPPING_AUTHORIZED" if eligible else "NO_TARGET_MAPPING_AUTHORIZED","eligible_anonymous_topologies":eligible,"ineligible_anonymous_topologies":[f for f,_,_ in FAMILIES if f not in eligible],"class_alignment":False,"exact_identity_as_feature":False,"voynich_target_scored":False,"voynich_rows_read":0,"semantic_state":"UNASSIGNED","f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"claim_ceiling":"COMPARATOR_RELATION_TOPOLOGY_TRANSFER_ONLY"}; write_json(ART/"gdt381_topology_signature_freeze.json",signature)
    outputs=[ART/x for x in ["gdt381_clustering_summary.tsv","gdt381_latent_class_summary.tsv","gdt381_topology_feature_manifest.tsv","gdt381_comparator_fold_scores.tsv","gdt381_comparator_family_summary.tsv","gdt381_null_capacity.tsv","gdt381_comparator_null.tsv.gz","gdt381_topology_signature_freeze.json"]]
    result={"schema":"GDT381_COMPARATOR_RESULT_V1","status":"RELATIONAL_TOPOLOGIES_CALIBRATED" if eligible else "NO_RELATIONAL_TOPOLOGY_PASSED_COMPARATOR_GATE","rows":len(obs),"records":len({(r['domain'],r['collection_id'],r['record_id']) for r in obs}),"topologies_tested":5,"eligible_anonymous_topologies":eligible,"voynich_target_scored":False,"voynich_rows_read":0,"inputs":{str(p.relative_to(ROOT)):sha(p) for p in [OBS,ORACLE,CONTRACT,DESIGN]},"outputs":{str(p.relative_to(ROOT)):sha(p) for p in outputs},"implementation":{str((BASE/'src/run_comparator.py').relative_to(ROOT)):sha(BASE/'src/run_comparator.py')},"semantic_state":"UNASSIGNED","f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"claim_ceiling":"COMPARATOR_RELATION_TOPOLOGY_TRANSFER_ONLY"}; write_json(ART/"gdt381_comparator_result.json",result)
    print(json.dumps({"status":result["status"],"eligible":eligible,"selected_k":{d:m['k'] for d,m in cluster_meta.items()}}))


if __name__ == "__main__": main()
