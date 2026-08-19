#!/usr/bin/env python3
"""GDT346: nested sparse compatibility graph over frozen GDT345 marginals."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists(): return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
import sys
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt346_compositional_operator_manifold"; ART = EXP / "artifacts"
METHOD = EXP / "METHOD.md"; AUDIT = EXP / "SOURCE_AUDIT.md"; DESIGN = ART / "gdt346_design.json"
G345 = ROOT / "experiments/yolo/gdt345_productive_operator_transfer/artifacts/gdt345_transition_inventory.tsv"
G345_RESULT = ROOT / "experiments/yolo/gdt345_productive_operator_transfer/artifacts/gdt345_result.json"
G345_DESIGN = ROOT / "experiments/yolo/gdt345_productive_operator_transfer/artifacts/gdt345_design.json"
G345_CORRECTION = ROOT / "experiments/yolo/gdt345_productive_operator_transfer/CORRECTION.md"
GRAPH_EDGES = ART / "gdt346_graph_edges.tsv"; FOLDS = ART / "gdt346_folds.tsv"; TRANSFER = ART / "gdt346_transfer.tsv"
PREDICTIONS = ART / "gdt346_predictions.tsv"; MODELS_OUT = ART / "gdt346_models.tsv"; NULL = ART / "gdt346_null.tsv"
HERBAL = ART / "gdt346_herbal_a.tsv"; COUNTER = ART / "gdt346_counterexamples.tsv"; RESULT = ART / "gdt346_result.json"; REPORT = EXP / "REPORT.md"

COMP = ("local_frame", "inner_d", "right_family", "dy_closure", "b3", "canonical_wrapper")
PAIRS = tuple(itertools.combinations(range(6), 2))
BASE_MODELS = ("PLACEMENT", "EXACT_PREDECESSOR", "SOURCE_STATE_TABLE", "INDEPENDENT_MARGINAL")
ALL_MODELS = (*BASE_MODELS, "PAIR_GRAPH_NONWRAPPER", "PAIR_GRAPH_FULL", "EXACT_OPERATOR_LEXICON")


def sha(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as h:
        for chunk in iter(lambda: h.read(1 << 20), b""): d.update(chunk)
    return d.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def content_hash(doc: dict[str, object]) -> str:
    x = dict(doc); x.pop("content_sha256", None); return hashlib.sha256(canonical(x)).hexdigest()


def hid(domain: str, value: object, length: int = 20) -> str:
    return hashlib.sha256((domain + "\0" + json.dumps(value, sort_keys=True, separators=(",", ":"))).encode()).hexdigest()[:length]


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows: raise ValueError(path)
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fields, delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)


def load_edges() -> list[dict[str, object]]:
    reader = GuardedTSV(G345, selector_column="page", forbidden_prefixes=("f84",), forbidden_action="error")
    edges = []
    for row in reader:
        source = tuple(json.loads(row["source_state_json"])); target = tuple(json.loads(row["target_state_json"])); change = tuple(json.loads(row["delta_json"])); layout = tuple(json.loads(row["layout_context_json"]))
        if len(source) != 6 or len(target) != 6 or len(change) != 6: raise AssertionError("state width")
        if tuple(a if d == "KEEP" else d[4:] for a, d in zip(source, change)) != target: raise AssertionError("delta application")
        edges.append({
            "edge_id": row["edge_id"], "page": row["page"], "physical_folio": row["physical_folio"], "section": row["section"], "register": row["register"], "hand": row["hand"],
            "source_tuple": row["source_tuple_id"], "source_state_id": row["source_state_id"], "target_state_id": row["target_state_id"], "operator_id": row["operator_id"], "text_operator_id": row["text_operator_id"],
            "source": source, "target": target, "delta": change, "layout": layout, "scope": row["boundary_scope"],
        })
    if len(edges) != 8268 or any(str(e["page"]).startswith("f84") for e in edges): raise AssertionError("source census/seal")
    return edges


def context(edge: dict[str, object], model: str, index: int) -> tuple[object, ...] | None:
    layout = tuple(edge["layout"])
    if model == "PLACEMENT": return None
    if model == "EXACT_PREDECESSOR": return (*layout, "TUPLE", edge["source_tuple"])
    if model == "SOURCE_STATE_TABLE": return (*layout, "STATE", edge["source_state_id"])
    if model == "INDEPENDENT_MARGINAL": return (*layout, f"C{index}", edge["source"][index])
    raise ValueError(model)


def build_tables(train: list[dict[str, object]], model: str, design: dict[str, object]) -> dict[str, object]:
    global_ = [Counter() for _ in COMP]; layout = [defaultdict(Counter) for _ in COMP]; ctx = [defaultdict(Counter) for _ in COMP]
    for e in train:
        for i, y in enumerate(e["target"]):
            global_[i][y] += 1; layout[i][tuple(e["layout"])][y] += 1
            key = context(e, model, i)
            if key is not None: ctx[i][key][y] += 1
    return {"global": global_, "layout": layout, "context": ctx, "model": model, "design": design}


def target_probs(edge: dict[str, object], tables: dict[str, object], i: int) -> dict[str, float]:
    g: Counter[str] = tables["global"][i]; labels = tuple(sorted(g)); n = sum(g.values()); jf = float(tables["design"]["marginals"]["global_jeffreys"])
    if not labels: return {}
    pg = {y: (g[y] + jf) / (n + jf * len(labels)) for y in labels}
    lc: Counter[str] = tables["layout"][i].get(tuple(edge["layout"]), Counter()); ln = sum(lc.values()); al = float(tables["design"]["marginals"]["layout_to_global"])
    pl = {y: (lc[y] + al * pg[y]) / (ln + al) for y in labels}
    if tables["model"] == "PLACEMENT": return pl
    cc: Counter[str] = tables["context"][i].get(context(edge, str(tables["model"]), i), Counter()); cn = sum(cc.values()); ac = float(tables["design"]["marginals"]["source_to_layout"])
    return {y: (cc[y] + ac * pl[y]) / (cn + ac) for y in labels}


def delta_probs(edge: dict[str, object], tables: dict[str, object], i: int) -> dict[str, float]:
    out: dict[str, float] = {}
    for y, p in target_probs(edge, tables, i).items():
        label = "KEEP" if y == edge["source"][i] else f"SET:{y}"; out[label] = out.get(label, 0.0) + p
    return out


def fit_potential(train: list[dict[str, object]], pair: tuple[int, int], tables: dict[str, object], design: dict[str, object]) -> dict[tuple[str, str, str], float]:
    i, j = pair; obs: Counter[tuple[str, str, str]] = Counter(); expected: defaultdict[tuple[str, str, str], float] = defaultdict(float); scope_n = Counter()
    for e in train:
        scope = str(e["scope"]); scope_n[scope] += 1; obs[(scope, e["delta"][i], e["delta"][j])] += 1
        pi, pj = delta_probs(e, tables, i), delta_probs(e, tables, j)
        for di, vi in pi.items():
            for dj, vj in pj.items(): expected[(scope, di, dj)] += vi * vj
    alpha = float(design["graph"]["edge_potential_shrinkage"]); phi = {}
    for key, exp in expected.items():
        q = exp / max(1, scope_n[key[0]]); prior = alpha * q
        phi[key] = (obs[key] + prior) / max(1e-300, exp + prior)
    return phi


def pair_gain(test: list[dict[str, object]], pair: tuple[int, int], phi: dict[tuple[str, str, str], float], tables: dict[str, object]) -> float:
    i, j = pair; gain = 0.0
    for e in test:
        pi, pj = delta_probs(e, tables, i), delta_probs(e, tables, j); scope = str(e["scope"])
        z = sum(vi * vj * phi.get((scope, di, dj), 1.0) for di, vi in pi.items() for dj, vj in pj.items())
        gain += math.log2(max(1e-300, phi.get((scope, e["delta"][i], e["delta"][j]), 1.0) / z))
    return gain


def select_graph(train: list[dict[str, object]], env_keys: tuple[str, ...], design: dict[str, object], fold_tag: str) -> tuple[list[tuple[int, int]], list[dict[str, object]]]:
    minimum = int(design["gate"]["minimum_powered_events"]); fraction = float(design["graph"]["transfer_environment_fraction"]); need_env = int(design["graph"]["transfer_environment_minimum"])
    evidence = {pair: {"families": {}, "eligible": True, "score": float("inf")} for pair in PAIRS}
    for env_key in env_keys:
        counts = Counter(str(e[env_key]) for e in train); categories = sorted(k for k, n in counts.items() if n >= minimum)
        family_gain = {pair: 0.0 for pair in PAIRS}; family_pos = Counter(); family_n = 0
        for held in categories:
            inner_train = [e for e in train if str(e[env_key]) != held]; inner_test = [e for e in train if str(e[env_key]) == held]
            if not inner_train or not inner_test: continue
            tables = build_tables(inner_train, "INDEPENDENT_MARGINAL", design); family_n += 1
            for pair in PAIRS:
                phi = fit_potential(inner_train, pair, tables, design); gain = pair_gain(inner_test, pair, phi, tables)
                family_gain[pair] += gain; family_pos[pair] += int(gain > 0)
        for pair in PAIRS:
            passes = family_n >= need_env and family_gain[pair] > 0 and family_pos[pair] >= math.ceil(fraction * family_n)
            evidence[pair]["families"][env_key] = (family_n, family_pos[pair], family_gain[pair], passes)
            evidence[pair]["eligible"] = bool(evidence[pair]["eligible"] and passes)
            evidence[pair]["score"] = min(float(evidence[pair]["score"]), family_gain[pair] / max(1, sum(counts[k] for k in categories)))
    selected = sorted([pair for pair in PAIRS if evidence[pair]["eligible"]], key=lambda p: (-float(evidence[p]["score"]), p))[:int(design["graph"]["max_edges"])]
    rows = []
    for pair in PAIRS:
        fam = evidence[pair]["families"]
        rows.append({
            "fold_tag": fold_tag, "coordinate_a": COMP[pair[0]], "coordinate_b": COMP[pair[1]], "pair_id": f"{pair[0]}-{pair[1]}",
            "selected": int(pair in selected), "eligible": int(bool(evidence[pair]["eligible"])), "selection_score_bits_per_event": f"{float(evidence[pair]['score']):.12f}",
            "environment_evidence_json": json.dumps({k: {"powered": v[0], "positive": v[1], "gain": v[2], "passes": v[3]} for k, v in fam.items()}, sort_keys=True, separators=(",", ":")),
            "nonwrapper_pair": int(pair[0] < 5 and pair[1] < 5), "semantic_state": "UNASSIGNED",
        })
    return selected, rows


def selector_bits(k: int) -> float:
    return math.log2(math.comb(15, k)) if k else 0.0


def all_target_combos(tables: dict[str, object]) -> tuple[tuple[str, ...], ...]:
    if "_combos" not in tables:
        tables["_combos"] = tuple(itertools.product(*(tuple(sorted(tables["global"][i])) for i in range(6))))
    return tables["_combos"]


def graph_distribution(edge: dict[str, object], tables: dict[str, object], potentials: dict[tuple[int, int], dict], selected: list[tuple[int, int]], train_states: set[tuple[str, ...]], train_ops: set[tuple[str, ...]], need_rank: bool) -> dict[str, object] | None:
    probs = [target_probs(edge, tables, i) for i in range(6)]
    if any(edge["target"][i] not in probs[i] for i in range(6)): return None
    combos = all_target_combos(tables); weights = [] if need_rank else None; z = truth_w = illegal_state = illegal_op = 0.0; best_w = -1.0; best_combo = None
    for target in combos:
        base = math.prod(probs[i][target[i]] for i in range(6)); ds = tuple("KEEP" if target[i] == edge["source"][i] else f"SET:{target[i]}" for i in range(6)); energy = 1.0
        for pair in selected: energy *= potentials[pair].get((str(edge["scope"]), ds[pair[0]], ds[pair[1]]), 1.0)
        w = base * energy; z += w
        if target == edge["target"]: truth_w = w
        if target not in train_states: illegal_state += w
        if ds not in train_ops: illegal_op += w
        if w > best_w or (w == best_w and (best_combo is None or target < best_combo)): best_w, best_combo = w, target
        if need_rank: weights.append((w, target))
    if truth_w <= 0 or z <= 0: return None
    rank = top5 = "NA"
    if need_rank:
        ordered = sorted(weights, key=lambda x: (-x[0], x[1])); rank = 1 + next(i for i, (_, target) in enumerate(ordered) if target == edge["target"]); top5 = int(rank <= 5)
    pred_delta = tuple("KEEP" if best_combo[i] == edge["source"][i] else f"SET:{best_combo[i]}" for i in range(6))
    truth_energy = math.prod(potentials[p].get((str(edge["scope"]), edge["delta"][p[0]], edge["delta"][p[1]]), 1.0) for p in selected)
    return {"bits": -math.log2(truth_w / z), "rank": rank, "top1": int(best_combo == edge["target"]), "top5": top5, "exact": int(best_combo == edge["target"]),
            "illegal_state": illegal_state / z, "illegal_op": illegal_op / z, "predicted_operator": hid("GDT345_TEXT_OPERATOR_V1", pred_delta), "gain_term": math.log2(max(1e-300, truth_energy / z))}


def independent_distribution(edge: dict[str, object], tables: dict[str, object], train_states: set[tuple[str, ...]], train_ops: set[tuple[str, ...]], need_rank: bool) -> dict[str, object] | None:
    if not need_rank:
        probs = [target_probs(edge, tables, i) for i in range(6)]
        if any(edge["target"][i] not in probs[i] for i in range(6)): return None
        truth = math.prod(probs[i][edge["target"][i]] for i in range(6)); best = tuple(min(p, key=lambda y: (-p[y], y)) for p in probs); pred_delta = tuple("KEEP" if best[i] == edge["source"][i] else f"SET:{best[i]}" for i in range(6))
        return {"bits": -math.log2(max(1e-300, truth)), "rank": "NA", "top1": int(best == edge["target"]), "top5": "NA", "exact": int(best == edge["target"]), "illegal_state": 0.0, "illegal_op": 0.0, "predicted_operator": hid("GDT345_TEXT_OPERATOR_V1", pred_delta), "gain_term": 0.0}
    return graph_distribution(edge, tables, {}, [], train_states, train_ops, need_rank)


def build_lexicon(train: list[dict[str, object]], design: dict[str, object]):
    global_ = Counter(e["delta"] for e in train); layout = defaultdict(Counter)
    for e in train: layout[tuple(e["layout"])][e["delta"]] += 1
    return global_, layout, design


def lexicon_distribution(edge: dict[str, object], lexicon, train_states: set[tuple[str, ...]], need_rank: bool) -> dict[str, object] | None:
    global_, layouts, design = lexicon; labels = tuple(sorted(global_)); truth = edge["delta"]
    if truth not in global_: return None
    n = sum(global_.values()); pg = {op: (global_[op] + 0.5) / (n + 0.5 * len(labels)) for op in labels}; lc = layouts.get(tuple(edge["layout"]), Counter()); ln = sum(lc.values()); alpha = float(design["marginals"]["layout_to_global"])
    p = {op: (lc[op] + alpha * pg[op]) / (ln + alpha) for op in labels}; ordered = sorted(p, key=lambda op: (-p[op], op)); best = ordered[0]; target = tuple(edge["source"][i] if best[i] == "KEEP" else best[i][4:] for i in range(6)); rank = 1 + ordered.index(truth) if need_rank else "NA"
    illegal_state = sum(prob for op, prob in p.items() if tuple(edge["source"][i] if op[i] == "KEEP" else op[i][4:] for i in range(6)) not in train_states)
    return {"bits": -math.log2(p[truth]), "rank": rank, "top1": int(rank == 1) if need_rank else int(best == truth), "top5": int(rank <= 5) if need_rank else "NA", "exact": int(target == edge["target"]), "illegal_state": illegal_state, "illegal_op": 0.0, "predicted_operator": hid("GDT345_TEXT_OPERATOR_V1", best), "gain_term": 0.0}


def decisive(edge: dict[str, object], train: list[dict[str, object]]) -> bool:
    states = {e["source_state_id"] for e in train}; ops = {e["operator_id"] for e in train}; combos = {(e["source_state_id"], e["operator_id"]) for e in train}
    if edge["source_state_id"] not in states or edge["operator_id"] not in ops or (edge["source_state_id"], edge["operator_id"]) in combos: return False
    for i in range(6):
        if (edge["source"][i], edge["delta"][i]) not in {(e["source"][i], e["delta"][i]) for e in train}: return False
    return True


def run_fold(train: list[dict[str, object]], test: list[dict[str, object]], selected: list[tuple[int, int]], design: dict[str, object], fold_tag: str, predictions: list[dict[str, object]], null_events: list[dict[str, object]]) -> list[dict[str, object]]:
    base_tables = {m: build_tables(train, m, design) for m in BASE_MODELS}; independent = base_tables["INDEPENDENT_MARGINAL"]
    potentials = {pair: fit_potential(train, pair, independent, design) for pair in selected}; nonwrap = [p for p in selected if p[0] < 5 and p[1] < 5]
    train_states = {e["source"] for e in train} | {e["target"] for e in train}; train_ops = {e["delta"] for e in train}; lexicon = build_lexicon(train, design)
    source_state_ids = {e["source_state_id"] for e in train}; registered_ops = {e["operator_id"] for e in train}; state_op_pairs = {(e["source_state_id"], e["operator_id"]) for e in train}; component_pairs = [{(e["source"][i], e["delta"][i]) for e in train} for i in range(6)]
    agg = {m: {"all_n": 0, "all_bits": 0.0, "all_exact": 0, "n": 0, "bits": 0.0, "rank": 0, "top1": 0, "top5": 0, "exact": 0, "is": 0.0, "io": 0.0} for m in ALL_MODELS}
    for e in test:
        is_decisive = e["source_state_id"] in source_state_ids and e["operator_id"] in registered_ops and (e["source_state_id"], e["operator_id"]) not in state_op_pairs and all((e["source"][i], e["delta"][i]) in component_pairs[i] for i in range(6))
        values = {}
        for model in BASE_MODELS:
            values[model] = independent_distribution(e, base_tables[model], train_states, train_ops, is_decisive)
        values["PAIR_GRAPH_NONWRAPPER"] = graph_distribution(e, independent, potentials, nonwrap, train_states, train_ops, is_decisive)
        values["PAIR_GRAPH_FULL"] = graph_distribution(e, independent, potentials, selected, train_states, train_ops, is_decisive)
        values["EXACT_OPERATOR_LEXICON"] = lexicon_distribution(e, lexicon, train_states, is_decisive)
        for model, value in values.items():
            if value is None: continue
            a = agg[model]; a["all_n"] += 1; a["all_bits"] += value["bits"]; a["all_exact"] += value["exact"]
            if is_decisive:
                a["n"] += 1; a["bits"] += value["bits"]; a["rank"] += int(value["rank"]); a["top1"] += value["top1"]; a["top5"] += value["top5"]; a["exact"] += value["exact"]; a["is"] += value["illegal_state"]; a["io"] += value["illegal_op"]
                predictions.append({"fold_tag": fold_tag, "edge_id": e["edge_id"], "physical_folio": e["physical_folio"], "section": e["section"], "register": e["register"], "hand": e["hand"], "model": model, "bits": f"{value['bits']:.9f}", "true_operator_rank": value["rank"], "top1": value["top1"], "top5": value["top5"], "exact_next_state": value["exact"], "training_unlicensed_state_mass": f"{value['illegal_state']:.9f}", "training_unlicensed_operator_mass": f"{value['illegal_op']:.9f}", "predicted_operator_id": value["predicted_operator"], "true_operator_id": e["text_operator_id"]})
        if is_decisive and values["PAIR_GRAPH_FULL"] and values["PAIR_GRAPH_NONWRAPPER"]:
            null_events.append({"held": e["physical_folio"], "layout": e["layout"], "scope": e["scope"], "source": e["source"], "delta": e["delta"], "full_pairs": selected, "non_pairs": nonwrap, "potentials": potentials, "full_logz": math.log2(max(1e-300, math.prod(1 for _ in [0]))) - values["PAIR_GRAPH_FULL"]["gain_term"] + sum(math.log2(max(1e-300, potentials[p].get((str(e["scope"]), e["delta"][p[0]], e["delta"][p[1]]), 1.0))) for p in selected), "non_logz": -values["PAIR_GRAPH_NONWRAPPER"]["gain_term"] + sum(math.log2(max(1e-300, potentials[p].get((str(e["scope"]), e["delta"][p[0]], e["delta"][p[1]]), 1.0))) for p in nonwrap)})
    rows = []
    for model in ALL_MODELS:
        a = agg[model]; k = len(nonwrap) if model == "PAIR_GRAPH_NONWRAPPER" else (len(selected) if model == "PAIR_GRAPH_FULL" else 0); cost = selector_bits(k)
        rows.append({"fold_tag": fold_tag, "model": model, "selected_edges": k, "selector_bits": f"{cost:.9f}", "all_events": a["all_n"], "all_bits": f"{a['all_bits']:.9f}", "all_selector_paid_bits": f"{a['all_bits'] + cost:.9f}", "all_exact_next_state": a["all_exact"], "decisive_events": a["n"], "decisive_bits": f"{a['bits']:.9f}", "decisive_selector_paid_bits": f"{a['bits'] + cost:.9f}", "rank_sum": a["rank"], "mean_rank": f"{a['rank']/max(1,a['n']):.9f}", "top1": a["top1"], "top5": a["top5"], "exact_next_state": a["exact"], "mean_unlicensed_state_mass": f"{a['is']/max(1,a['n']):.9f}", "mean_unlicensed_operator_mass": f"{a['io']/max(1,a['n']):.9f}"})
    return rows


def run_split(edges: list[dict[str, object]], split: str, key: str, env_keys: tuple[str, ...], design: dict[str, object], edge_rows: list[dict[str, object]], predictions: list[dict[str, object]], null_events: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for held in sorted({str(e[key]) for e in edges}):
        train = [e for e in edges if str(e[key]) != held]; test = [e for e in edges if str(e[key]) == held]; tag = f"{split}:{held}"
        selected, evidence = select_graph(train, env_keys, design, tag); edge_rows.extend(evidence)
        fold_rows = run_fold(train, test, selected, design, tag, predictions if split == "PHYSICAL_FOLIO" else [], null_events if split == "PHYSICAL_FOLIO" else [])
        for row in fold_rows: row["split"] = split; row["held_value"] = held
        rows.extend(fold_rows)
    return rows


def aggregate(folds: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for model in ALL_MODELS:
        fs = [r for r in folds if r["model"] == model]; n = sum(int(r["decisive_events"]) for r in fs); bits = sum(float(r["decisive_bits"]) for r in fs); paid = sum(float(r["decisive_selector_paid_bits"]) for r in fs)
        rows.append({"model": model, "decisive_events": n, "decisive_bits": f"{bits:.9f}", "decisive_selector_paid_bits": f"{paid:.9f}", "mean_rank": f"{sum(int(r['rank_sum']) for r in fs)/max(1,n):.9f}", "top1": sum(int(r["top1"]) for r in fs), "top5": sum(int(r["top5"]) for r in fs), "exact_next_state": sum(int(r["exact_next_state"]) for r in fs), "mean_unlicensed_state_mass": f"{sum(float(r['mean_unlicensed_state_mass'])*int(r['decisive_events']) for r in fs)/max(1,n):.9f}", "mean_unlicensed_operator_mass": f"{sum(float(r['mean_unlicensed_operator_mass'])*int(r['decisive_events']) for r in fs)/max(1,n):.9f}", "positive_folios_vs_independent": "NA", "raw_gain_over_independent": "NA", "paid_gain_over_independent": "NA", "inclusive_p": "NA", "max_two_p": "NA"})
    by = {r["model"]: r for r in rows}; base = by["INDEPENDENT_MARGINAL"]
    for row in rows:
        row["raw_gain_over_independent"] = f"{float(base['decisive_bits']) - float(row['decisive_bits']):.9f}"; row["paid_gain_over_independent"] = f"{float(base['decisive_bits']) - float(row['decisive_selector_paid_bits']):.9f}"
        if row["model"].startswith("PAIR_GRAPH"):
            row["positive_folios_vs_independent"] = sum(float(next(x for x in folds if x["fold_tag"] == f["fold_tag"] and x["model"] == "INDEPENDENT_MARGINAL")["decisive_bits"]) > float(f["decisive_selector_paid_bits"]) for f in folds if f["model"] == row["model"])
    return rows


def coupling_null(events: list[dict[str, object]], design: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, float]]:
    observed = {"full": 0.0, "non": 0.0}
    for e in events:
        for name, pairs, logz in (("full", e["full_pairs"], e["full_logz"]), ("non", e["non_pairs"], e["non_logz"])):
            observed[name] += sum(math.log2(max(1e-300, e["potentials"][p].get((str(e["scope"]), e["delta"][p[0]], e["delta"][p[1]]), 1.0))) for p in pairs) - logz
    groups = [defaultdict(list) for _ in range(6)]
    for idx, e in enumerate(events):
        for i in range(6): groups[i][(e["held"], *tuple(e["layout"]), e["source"][i])].append(idx)
    rows = []; exceed = Counter(); obsmax = max(observed.values())
    for world in range(int(design["null"]["worlds"])):
        rng = random.Random(int(design["null"]["seed"]) + world); labels = [[e["delta"][i] for e in events] for i in range(6)]
        for i in range(6):
            for indices in groups[i].values():
                local = [labels[i][j] for j in indices]; rng.shuffle(local)
                for j, value in zip(indices, local): labels[i][j] = value
        gains = {"full": 0.0, "non": 0.0}
        for idx, e in enumerate(events):
            for name, pairs, logz in (("full", e["full_pairs"], e["full_logz"]), ("non", e["non_pairs"], e["non_logz"])):
                gains[name] += sum(math.log2(max(1e-300, e["potentials"][p].get((str(e["scope"]), labels[p[0]][idx], labels[p[1]][idx]), 1.0))) for p in pairs) - logz
        exceed["full"] += int(gains["full"] >= observed["full"]); exceed["non"] += int(gains["non"] >= observed["non"]); maximum = max(gains.values()); exceed["max"] += int(maximum >= obsmax)
        rows.append({"world": world, "nonwrapper_gain": f"{gains['non']:.9f}", "full_gain": f"{gains['full']:.9f}", "max_two_gain": f"{maximum:.9f}"})
    p = {k: (1 + exceed[k]) / (1 + len(rows)) for k in ("non", "full", "max")}; return rows, p


def herbal_a(edges: list[dict[str, object]], design: dict[str, object], edge_rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], str]:
    ha = [e for e in edges if e["register"] == "HERBAL_A"]; foreign = [e for e in edges if e["register"] != "HERBAL_A"]
    foreign_sel, evidence = select_graph(foreign, ("section", "hand"), design, "HERBAL_A_FOREIGN_GRAPH"); edge_rows.extend(evidence)
    foreign_base = build_tables(foreign, "INDEPENDENT_MARGINAL", design); foreign_phi = {p: fit_potential(foreign, p, foreign_base, design) for p in foreign_sel}
    rows = []
    for hold in sorted({str(e["physical_folio"]) for e in ha}):
        train = [e for e in ha if e["physical_folio"] != hold]; test = [e for e in ha if e["physical_folio"] == hold]
        base = build_tables(train, "INDEPENDENT_MARGINAL", design); local_sel, local_ev = select_graph(train, ("physical_folio",), design, f"HERBAL_A_LOCAL:{hold}"); edge_rows.extend(local_ev); local_phi = {p: fit_potential(train, p, base, design) for p in local_sel}
        train_states = {e["source"] for e in train} | {e["target"] for e in train}; train_ops = {e["delta"] for e in train}
        sums = {"INDEPENDENT": 0.0, "FOREIGN_GRAPH": 0.0, "LOCAL_GRAPH": 0.0}; n = 0
        for e in test:
            ind = independent_distribution(e, base, train_states, train_ops, False); fg = graph_distribution(e, base, foreign_phi, foreign_sel, train_states, train_ops, False); lg = graph_distribution(e, base, local_phi, local_sel, train_states, train_ops, False)
            if not ind or not fg or not lg: continue
            n += 1; sums["INDEPENDENT"] += ind["bits"]; sums["FOREIGN_GRAPH"] += fg["bits"]; sums["LOCAL_GRAPH"] += lg["bits"]
        for model in sums:
            k = len(foreign_sel) if model == "FOREIGN_GRAPH" else (len(local_sel) if model == "LOCAL_GRAPH" else 0)
            rows.append({"held_folio": hold, "model": model, "events": n, "bits": f"{sums[model]:.9f}", "selector_bits": f"{selector_bits(k):.9f}", "selector_paid_bits": f"{sums[model] + selector_bits(k):.9f}", "selected_pairs": "|".join(f"{a}-{b}" for a,b in (foreign_sel if model == 'FOREIGN_GRAPH' else (local_sel if model == 'LOCAL_GRAPH' else [])))})
    totals = {m: sum(float(r["selector_paid_bits"]) for r in rows if r["model"] == m) for m in ("INDEPENDENT", "FOREIGN_GRAPH", "LOCAL_GRAPH")}; foreign_gain = totals["INDEPENDENT"] - totals["FOREIGN_GRAPH"]; local_gain = totals["INDEPENDENT"] - totals["LOCAL_GRAPH"]
    foreign_set = set(foreign_sel); local_set = {tuple(map(int,p.split("-"))) for r in rows if r["model"] == "LOCAL_GRAPH" for p in r["selected_pairs"].split("|") if p}
    if foreign_gain > 0 and totals["LOCAL_GRAPH"] >= totals["FOREIGN_GRAPH"] - 1.0: status = "SAME_GRAPH_DIFFERENT_PRIORS"
    elif foreign_gain <= 0 and local_gain > 0 and bool(local_set - foreign_set): status = "NEW_COMPATIBILITY_EDGES_REQUIRED"
    elif len(ha) < 50: status = "INSUFFICIENT_HERBAL_A_CAPACITY"
    else: status = "NO_TRANSFERABLE_HERBAL_A_GRAPH"
    return rows, status


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True); design = json.loads(DESIGN.read_text()); edges = load_edges(); graph_rows = []; predictions = []; null_events = []
    folds = run_split(edges, "PHYSICAL_FOLIO", "physical_folio", ("register", "hand"), design, graph_rows, predictions, null_events); write_tsv(FOLDS, folds)
    transfer = []
    for split, key, env in (("SECTION", "section", ("register", "hand")), ("REGISTER", "register", ("section", "hand")), ("HAND", "hand", ("section", "register"))):
        transfer.extend(run_split(edges, split, key, env, design, graph_rows, [], []))
    write_tsv(TRANSFER, transfer); models = aggregate(folds); null_rows, p = coupling_null(null_events, design); write_tsv(NULL, null_rows)
    by_model = {r["model"]: r for r in models}
    by_model["PAIR_GRAPH_NONWRAPPER"]["inclusive_p"] = f"{p['non']:.9f}"; by_model["PAIR_GRAPH_NONWRAPPER"]["max_two_p"] = f"{p['max']:.9f}"; by_model["PAIR_GRAPH_FULL"]["inclusive_p"] = f"{p['full']:.9f}"; by_model["PAIR_GRAPH_FULL"]["max_two_p"] = f"{p['max']:.9f}"
    write_tsv(MODELS_OUT, models); write_tsv(PREDICTIONS, predictions); herbal_rows, herbal_status = herbal_a(edges, design, graph_rows); write_tsv(HERBAL, herbal_rows); write_tsv(GRAPH_EDGES, graph_rows)
    base = by_model["INDEPENDENT_MARGINAL"]; full = by_model["PAIR_GRAPH_FULL"]; non = by_model["PAIR_GRAPH_NONWRAPPER"]
    transfer_summary = {}
    for split in ("SECTION", "REGISTER", "HAND"):
        selected = [r for r in transfer if r["split"] == split and r["model"] == "PAIR_GRAPH_FULL" and int(r["decisive_events"]) >= int(design["gate"]["minimum_powered_events"])]
        gains = []
        for r in selected:
            b = next(x for x in transfer if x["split"] == split and x["held_value"] == r["held_value"] and x["model"] == "INDEPENDENT_MARGINAL"); gains.append(float(b["decisive_bits"]) - float(r["decisive_selector_paid_bits"]))
        transfer_summary[split] = {"powered": len(gains), "positive": sum(g > 0 for g in gains), "gain": sum(gains), "passes": bool(gains and sum(gains)>0 and sum(g>0 for g in gains)>=math.ceil(float(design["gate"]["positive_category_fraction"])*len(gains)))}
    selected_nonwrapper_folds = sum(any(r["fold_tag"] == f"PHYSICAL_FOLIO:{h}" and int(r["selected"]) == 1 and int(r["nonwrapper_pair"]) == 1 for r in graph_rows) for h in {e["physical_folio"] for e in edges})
    gates = {
        "full_paid_over_independent": float(full["paid_gain_over_independent"]) > 0,
        "full_paid_over_exact": float(by_model["EXACT_PREDECESSOR"]["decisive_bits"]) > float(full["decisive_selector_paid_bits"]),
        "full_paid_over_state": float(by_model["SOURCE_STATE_TABLE"]["decisive_bits"]) > float(full["decisive_selector_paid_bits"]),
        "rank_top5_exact": float(full["mean_rank"]) < float(base["mean_rank"]) and int(full["top5"]) > int(base["top5"]) and int(full["exact_next_state"]) > int(base["exact_next_state"]),
        "nonwrapper_gain": float(non["paid_gain_over_independent"]) > 0 and selected_nonwrapper_folds >= math.ceil(float(design["gate"]["nonwrapper_edge_fold_fraction"])*91),
        "positive_folios": int(full["positive_folios_vs_independent"]) >= math.ceil(float(design["gate"]["positive_folio_fraction"])*91),
        "transfer": all(x["passes"] for x in transfer_summary.values()), "max_two_p": float(full["max_two_p"]) <= float(design["gate"]["inclusive_max_two_p"]),
    }
    status = "COMPOSITIONAL_OPERATOR_MANIFOLD_SUPPORTED" if all(gates.values()) else ("LOCAL_COMPATIBILITY_WITHOUT_TRANSFER" if float(full["raw_gain_over_independent"]) > 0 else "MARGINAL_TRANSITION_SMOOTHING_ONLY")
    counter = [
        {"code":"GDT345_MARGIN","detail":"corrected coordinate-wise target-value marginals are frozen as INDEPENDENT_MARGINAL","effect":"GRAPH_MUST_ADD_CROSS_COORDINATE_INFORMATION"},
        {"code":"DECISIVE_PANEL","detail":f"{full['decisive_events']} unseen full source-state×operator events with every component separately observed","effect":"PRODUCTIVE_RECOMBINATION_ONLY"},
        {"code":"EXACT_OPERATOR_LEXICON","detail":"complete operator frequencies used only as a separate ceiling","effect":"NO_TARGET_OPERATOR_FEATURE"},
        {"code":"HERBAL_A", "detail":herbal_status, "effect":"SAME_GRAPH_PRIOR_TEST_OR_NEW_EDGE_TEST"},
        {"code":"SEMANTICS","detail":"not run", "effect":"NO_ALIGNMENT_OR_GLOSS"}, {"code":"F84","detail":"sole input is validated f84-free GDT345 inventory", "effect":"NO_ACCESS"},
    ]; write_tsv(COUNTER, counter)
    report = f"""# GDT346 — compositional operator manifold

Status: **{status}**. Herbal-A diagnosis: **{herbal_status}**.

The decisive panel contains {full['decisive_events']} held events whose full source state and operator were each known in training, whose combination was unseen, and whose six component deltas were individually licensed. The independent marginal model uses {float(base['decisive_bits']):.3f} bits. The sparse full graph uses {float(full['decisive_bits']):.3f} raw and {float(full['decisive_selector_paid_bits']):.3f} selector-paid bits, a paid gain of {float(full['paid_gain_over_independent']):+.3f}. Its mean true-operator rank is {full['mean_rank']} versus {base['mean_rank']}; top-5 is {full['top5']} versus {base['top5']}; exact recovery is {full['exact_next_state']} versus {base['exact_next_state']}.

The non-wrapper graph's selector-paid gain is {float(non['paid_gain_over_independent']):+.3f} bits. At least one non-wrapper pair is selected in {selected_nonwrapper_folds}/91 folds. Full-graph max-two p={full['max_two_p']} under the marginal-preserving coupling-destruction null. Transfer: {json.dumps(transfer_summary, sort_keys=True)}. Gates: {json.dumps(gates, sort_keys=True)}.

Training-unlicensed operator mass is {full['mean_unlicensed_operator_mass']} for the full graph versus {base['mean_unlicensed_operator_mass']} independently; these are empirical training licenses, not authorial impossibility.

No exact target operator was a feature. Exact tuples remained atomic, PAGE_HOST was not factored, no semantic alignment was run, and f84 was not accessed.
"""; REPORT.write_text(report)
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in (METHOD,AUDIT,DESIGN,G345,G345_RESULT,G345_DESIGN,G345_CORRECTION)}
    outputs = {str(p.relative_to(ROOT)): sha(p) for p in (GRAPH_EDGES,FOLDS,TRANSFER,PREDICTIONS,MODELS_OUT,NULL,HERBAL,COUNTER,REPORT)}
    result = {"schema":"GDT346_RESULT_V1","date":"2026-08-19","status":status,"source":{"events":len(edges),"folios":len({e['physical_folio'] for e in edges}),"pages":len({e['page'] for e in edges})},"models":by_model,"transfer":transfer_summary,"herbal_a_status":herbal_status,"selected_nonwrapper_folds":selected_nonwrapper_folds,"gates":gates,"semantic_alignments":0,"tuple_merges":0,"page_host_factorizations":0,"f84":{"opened":False,"parsed":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Low-order formal delta compatibility only; no morphology semantics word language plaintext translation or f84 result.","inputs":inputs,"outputs":outputs,"implementation":{str(Path(__file__).resolve().relative_to(ROOT)):sha(Path(__file__).resolve())}}
    result["content_sha256"] = content_hash(result); RESULT.write_bytes(canonical(result)); print(f"{status} decisive={full['decisive_events']} paid_gain={full['paid_gain_over_independent']} max2={full['max_two_p']} herbal={herbal_status}"); return 0


if __name__ == "__main__": raise SystemExit(main())
