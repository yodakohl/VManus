#!/usr/bin/env python3
"""GDT165: exact opaque PAGE_HOST directed relation graph."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
DESIGN = ROOT / "gdt165_design.json"
METHOD = ROOT / "GDT165_OPAQUE_PAGE_HOST_RELATION_GRAPH_METHOD.md"
REPORT = ROOT / "GDT165_OPAQUE_PAGE_HOST_RELATION_GRAPH_REPORT.md"
HOSTS = ROOT / "gdt165_host_manifest.tsv"
EDGES = ROOT / "gdt165_edge_inventory.tsv"
FOLDS = ROOT / "gdt165_fold_scores.tsv"
RELATIONS = ROOT / "gdt165_directed_relations.tsv"
COMMUNITIES = ROOT / "gdt165_community_stability.tsv"
NULLS = ROOT / "gdt165_null_results.tsv"
COUNTER = ROOT / "gdt165_counterexamples.tsv"
VARIANTS = ROOT / "gdt165_variant_log.tsv"
RESULT = ROOT / "gdt165_result.json"

ALPHA = 32.0
BETA = 16.0
PANEL_N = 128
K = 8
WORLDS = 1024
MIN_REL = 8
MIN_REL_FOLIOS = 3
FEATURES = ("section", "currier", "hand", "source_frequency_bin", "position_quartile", "line_count_bin")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def opaque(value: str) -> str:
    return "H" + hashlib.sha256(value.encode()).hexdigest()[:16]


def seed(label: str) -> int:
    return int(hashlib.sha256(label.encode()).hexdigest()[:16], 16)


def write(path: Path, rows: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if "claim_state" in fields:
        fields.remove("claim_state")
        fields.append("claim_state")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def freq_bin(n: int) -> str:
    return "F1" if n == 1 else "F2_4" if n <= 4 else "F5_15" if n <= 15 else "F16_63" if n <= 63 else "F64P"


def line_bin(n: int) -> str:
    return str(n) if n <= 4 else "5_7" if n <= 7 else "8P"


def load_events():
    rows = []
    rejected = 0
    total = 0
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        for source_row in csv.DictReader(handle, delimiter="\t"):
            total += 1
            if source_row["page"].startswith("f84") or source_row["locus"].startswith("f84"):
                rejected += 1
                continue
            rows.append({"host": source_row["page_host"], "locus": source_row["locus"],
                         "folio": source_row["physical_folio"], "section": source_row["section"],
                         "currier": source_row["currier"], "hand": source_row["hand"],
                         "index": int(source_row["group_index"]), "group_count": int(source_row["group_count"])})
    assert total == 15592 and rejected == 228 and len(rows) == 15364
    by_line = defaultdict(dict)
    for row in rows:
        by_line[row["locus"]][row["index"]] = row
    events = []
    event_id = 0
    for locus in sorted(by_line, key=lambda x: (x.split(".")[0], int(x.split(".")[-1]))):
        line = by_line[locus]
        lo, hi = min(line), max(line)
        for index in sorted(line):
            if index + 1 not in line:
                continue
            source = line[index]
            target = line[index + 1]
            quartile = min(3, int(4 * (index - lo) / max(1, hi - lo)))
            events.append({"event_id": event_id, "source": source["host"], "target": target["host"],
                           "locus": locus, "folio": source["folio"], "section": source["section"],
                           "currier": source["currier"], "hand": source["hand"],
                           "source_index": index, "target_index": index + 1,
                           "position_quartile": f"Q{quartile}", "line_count_bin": line_bin(source["group_count"])})
            event_id += 1
    counts = Counter(row["source"] for row in events)
    for row in events:
        row["source_frequency_bin"] = freq_bin(counts[row["source"]])
        row["nuisance_key"] = tuple(row[key] for key in FEATURES)
    assert len(events) == 12467 and len({r["folio"] for r in events}) == 92
    return rows, events, rejected, total


def cluster_graph(events, panel):
    nodes = list(panel)
    index = {node: i for i, node in enumerate(nodes)}
    matrix = np.zeros((len(nodes), len(nodes)), dtype=float)
    for row in events:
        a = index.get(row["source"])
        b = index.get(row["target"])
        if a is None or b is None or a == b:
            continue
        matrix[a, b] += 1.0
        matrix[b, a] += 1.0
    degree = matrix.sum(axis=1)
    active = degree > 0
    scale = np.zeros_like(degree)
    scale[active] = 1.0 / np.sqrt(degree[active])
    normalized = scale[:, None] * matrix * scale[None, :]
    values, vectors = np.linalg.eigh(normalized)
    embedding = vectors[:, np.argsort(values)[-K:]]
    norm = np.linalg.norm(embedding, axis=1)
    embedding[active] /= norm[active, None]

    active_ids = [i for i in range(len(nodes)) if active[i]]
    if not active_ids:
        return {node: -1 for node in nodes}, set()
    first = max(active_ids, key=lambda i: (degree[i], opaque(nodes[i])))
    centers = [embedding[first].copy()]
    chosen = {first}
    while len(centers) < K:
        candidate = max((i for i in active_ids if i not in chosen),
                        key=lambda i: (min(float(np.sum((embedding[i] - c) ** 2)) for c in centers), opaque(nodes[i])))
        centers.append(embedding[candidate].copy())
        chosen.add(candidate)
    centers = np.stack(centers)
    assignment = np.full(len(nodes), -1, dtype=int)
    for _ in range(50):
        distances = ((embedding[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        new = np.argmin(distances, axis=1)
        new[~active] = -1
        if np.array_equal(new, assignment):
            break
        assignment = new
        for k in range(K):
            members = embedding[assignment == k]
            if len(members):
                centers[k] = members.mean(axis=0)
    return {node: int(assignment[i]) for i, node in enumerate(nodes)}, {nodes[i] for i in active_ids}


def train_model(train, target_vocab, panel):
    global_target = Counter(r["target"] for r in train)
    feature_target = [Counter() for _ in FEATURES]
    feature_total = [Counter() for _ in FEATURES]
    host_target = Counter()
    host_total = Counter()
    for row in train:
        for j, feature in enumerate(FEATURES):
            value = row[feature]
            feature_target[j][value, row["target"]] += 1
            feature_total[j][value] += 1
        host_target[row["source"], row["target"]] += 1
        host_total[row["source"]] += 1
    community, active = cluster_graph(train, panel)
    community_target = Counter()
    community_total = Counter()
    for row in train:
        group = community.get(row["source"], -1) if row["source"] in panel else -1
        community_target[group, row["target"]] += 1
        community_total[group] += 1
    return {"global": global_target, "n": len(train), "v": len(target_vocab),
            "feature_target": feature_target, "feature_total": feature_total,
            "host_target": host_target, "host_total": host_total,
            "community": community, "community_active": active,
            "community_target": community_target, "community_total": community_total,
            "target_vocab": target_vocab}


def probabilities(model, event, target):
    q = (model["global"][target] + .5) / (model["n"] + .5 * model["v"])
    pieces = []
    for j, feature in enumerate(FEATURES):
        value = event[feature]
        pieces.append((model["feature_target"][j][value, target] + ALPHA * q) /
                      (model["feature_total"][j][value] + ALPHA))
    nuisance = sum(pieces) / len(pieces)
    host = ((model["host_target"][event["source"], target] + BETA * nuisance) /
            (model["host_total"][event["source"]] + BETA))
    group = model["community"].get(event["source"], -1) if event["source"] in model["community"] else -1
    community = ((model["community_target"][group, target] + BETA * nuisance) /
                 (model["community_total"][group] + BETA))
    return q, nuisance, host, community


def rank_targets(model, event):
    scored = []
    for target in model["target_vocab"]:
        q, nuisance, host, community = probabilities(model, event, target)
        scored.append((target, q, nuisance, host, community))
    order_key = lambda item, column: (-item[column], opaque(item[0]))
    result = {}
    for name, column in (("unigram", 1), ("nuisance", 2), ("host", 3), ("community", 4)):
        ordered = sorted(scored, key=lambda x: order_key(x, column))
        result[name] = (ordered[0][0], frozenset(x[0] for x in ordered[:5]))
    return result


def score_mode(events, mode, target_vocab, panel):
    held_key = {"HELD_FOLIO": "folio", "HELD_SECTION": "section", "HELD_HAND": "hand"}[mode]
    folds = []
    contributions = []
    artifacts = {}
    for held in sorted({r[held_key] for r in events}):
        train = [r for r in events if r[held_key] != held]
        test = [r for r in events if r[held_key] == held]
        model = train_model(train, target_vocab, panel)
        artifacts[held] = model, test
        totals = Counter()
        rank_cache = {}
        seen = 0
        for event in test:
            q, nuisance, host, community = probabilities(model, event, event["target"])
            values = {"unigram": q, "nuisance": nuisance, "host": host, "community": community}
            for name, value in values.items():
                totals[name + "_bits"] -= math.log2(value)
            seen += int(model["host_total"][event["source"]] > 0)
            cache_key = (event["source"],) + tuple(event[f] for f in FEATURES)
            if cache_key not in rank_cache:
                rank_cache[cache_key] = rank_targets(model, event)
            for name, (top1, top5) in rank_cache[cache_key].items():
                totals[name + "_top1"] += int(event["target"] == top1)
                totals[name + "_top5"] += int(event["target"] in top5)
            contributions.append({"mode": mode, "held": held, "event_id": event["event_id"],
                                  "source": event["source"], "target": event["target"], "folio": event["folio"],
                                  "host_gain_bits": math.log2(host / nuisance),
                                  "community_gain_bits": math.log2(community / nuisance)})
        row = {"mode": mode, "held": held, "events": len(test), "training_events": len(train),
               "source_seen_events": seen, "source_seen_fraction": seen / len(test) if test else 0.0}
        for key, value in totals.items():
            row[key] = value
        row["host_gain_vs_nuisance_bits"] = totals["nuisance_bits"] - totals["host_bits"]
        row["community_gain_vs_nuisance_bits"] = totals["nuisance_bits"] - totals["community_bits"]
        row["host_gain_vs_community_bits"] = totals["community_bits"] - totals["host_bits"]
        row["claim_state"] = "OPAQUE_IDENTITY_HELD_CONTEXT_NO_LEXEME_OR_MEANING"
        folds.append(row)
    return folds, contributions, artifacts


def aggregate_folds(rows):
    total = sum(r["events"] for r in rows)
    out = {"folds": len(rows), "events": total,
           "nuisance_bits": sum(r["nuisance_bits"] for r in rows),
           "host_bits": sum(r["host_bits"] for r in rows),
           "community_bits": sum(r["community_bits"] for r in rows),
           "host_gain_vs_nuisance_bits": sum(r["host_gain_vs_nuisance_bits"] for r in rows),
           "community_gain_vs_nuisance_bits": sum(r["community_gain_vs_nuisance_bits"] for r in rows),
           "host_gain_vs_community_bits": sum(r["host_gain_vs_community_bits"] for r in rows),
           "positive_host_folds": sum(r["host_gain_vs_nuisance_bits"] > 0 for r in rows),
           "positive_community_folds": sum(r["community_gain_vs_nuisance_bits"] > 0 for r in rows),
           "source_seen_fraction": sum(r["source_seen_events"] for r in rows) / total}
    out["host_gain_per_event"] = out["host_gain_vs_nuisance_bits"] / total
    out["community_gain_per_event"] = out["community_gain_vs_nuisance_bits"] / total
    for model in ("unigram", "nuisance", "host", "community"):
        out[model + "_top1"] = sum(r[model + "_top1"] for r in rows) / total
        out[model + "_top5"] = sum(r[model + "_top5"] for r in rows) / total
    return out


def coassign(mapping, nodes):
    ordered = sorted(nodes, key=opaque)
    return {(ordered[i], ordered[j]) for i in range(len(ordered)) for j in range(i + 1, len(ordered))
            if mapping.get(ordered[i], -1) >= 0 and mapping.get(ordered[i]) == mapping.get(ordered[j])}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 0.0


def community_stability(events, panel):
    reference, ref_active = cluster_graph(events, panel)
    rows = []
    for axis, key in (("HELD_SECTION", "section"), ("HELD_HAND", "hand")):
        for held in sorted({r[key] for r in events}):
            split, active = cluster_graph([r for r in events if r[key] != held], panel)
            common = ref_active & active
            ref_pairs = coassign(reference, common)
            split_pairs = coassign(split, common)
            observed = jaccard(ref_pairs, split_pairs)
            nodes = sorted(common, key=opaque)
            labels = [split[n] for n in nodes]
            rng = random.Random(seed("GDT165_COMMUNITY_" + axis + "_" + held))
            null = []
            for _ in range(WORLDS):
                shuffled = labels[:]
                rng.shuffle(shuffled)
                mapping = dict(zip(nodes, shuffled))
                null.append(jaccard(ref_pairs, coassign(mapping, common)))
            ordered = sorted(null)
            q95 = ordered[int(.95 * (WORLDS - 1))]
            p = (1 + sum(x >= observed - 1e-12 for x in null)) / (WORLDS + 1)
            rows.append({"axis": axis, "held": held, "common_active_hosts": len(common),
                         "reference_coassigned_pairs": len(ref_pairs), "split_coassigned_pairs": len(split_pairs),
                         "coassignment_jaccard": observed, "null_mean": sum(null) / WORLDS,
                         "null_q95": q95, "inclusive_p": p, "above_null_q95": int(observed > q95),
                         "claim_state": "ANONYMOUS_GRAPH_PARTITION_NO_SEMANTIC_CLASS"})
    return rows, reference


def relation_atlas(events, contributions):
    modes = defaultdict(lambda: defaultdict(float))
    folio_gain = defaultdict(lambda: defaultdict(float))
    for row in contributions:
        pair = row["source"], row["target"]
        modes[pair][row["mode"]] += row["host_gain_bits"]
        if row["mode"] == "HELD_FOLIO":
            folio_gain[pair][row["held"]] += row["host_gain_bits"]
    counts = Counter((r["source"], r["target"]) for r in events)
    folios = defaultdict(set)
    sections = defaultdict(set)
    hands = defaultdict(set)
    for row in events:
        pair = row["source"], row["target"]
        folios[pair].add(row["folio"])
        sections[pair].add(row["section"])
        hands[pair].add(row["hand"])
    rows = []
    for pair, count in counts.items():
        if count < MIN_REL or len(folios[pair]) < MIN_REL_FOLIOS:
            continue
        gains = modes[pair]
        stable = all(gains[mode] > 0 for mode in ("HELD_FOLIO", "HELD_SECTION", "HELD_HAND"))
        label = "STABLE_DIRECTED_RELATION" if stable else "LOCAL_OR_UNSTABLE" if gains["HELD_FOLIO"] > 0 else "NO_GAIN"
        rows.append({"source_host_id": opaque(pair[0]), "target_host_id": opaque(pair[1]),
                     "source_host": pair[0], "target_host": pair[1], "occurrences": count,
                     "folios": len(folios[pair]), "sections": len(sections[pair]), "hands": len(hands[pair]),
                     "held_folio_gain_bits": gains["HELD_FOLIO"],
                     "held_section_gain_bits": gains["HELD_SECTION"],
                     "held_hand_gain_bits": gains["HELD_HAND"],
                     "positive_held_folios": sum(x > 0 for x in folio_gain[pair].values()),
                     "eligible_held_folios": len(folio_gain[pair]), "label": label,
                     "claim_state": "OPAQUE_DIRECTED_RELATION_NO_LEXEME_OR_MEANING"})
    return sorted(rows, key=lambda r: (-r["held_folio_gain_bits"], r["source_host_id"], r["target_host_id"]))


def held_alignment_null(events, artifacts, relation_rows):
    observed_total = sum(r["held_folio_gain_bits"] for r in relation_rows)  # not used for primary
    real_total = 0.0
    for held, (model, test) in artifacts.items():
        for event in test:
            _, nuisance, host, _ = probabilities(model, event, event["target"])
            real_total += math.log2(host / nuisance)
    observed_top = max((r["held_folio_gain_bits"] for r in relation_rows), default=0.0)
    rng = random.Random(seed("GDT165_HELD_ALIGNMENT_NULL"))
    rows = []
    gains = []
    tops = []
    swappable = 0
    variable = 0
    prepared = {}
    for held, (model, test) in artifacts.items():
        groups = defaultdict(list)
        for event in test:
            groups[event["nuisance_key"]].append(event)
        prepared_groups = {}
        for key, group in groups.items():
            unique_sources = {event["source"] for event in group}
            unique_targets = {event["target"] for event in group}
            lookup = {}
            exemplar = group[0]
            for source in unique_sources:
                probe = dict(exemplar)
                probe["source"] = source
                for target in unique_targets:
                    _, nuisance, host, _ = probabilities(model, probe, target)
                    lookup[source, target] = math.log2(host / nuisance)
            prepared_groups[key] = group, lookup
        prepared[held] = prepared_groups
        swappable += sum(len(group) for group in groups.values() if len(group) >= 2)
        variable += sum(len(group) for group in groups.values() if len({r["target"] for r in group}) >= 2)
    for world in range(WORLDS):
        total = 0.0
        pair_gain = defaultdict(float)
        pair_count = Counter()
        pair_folios = defaultdict(set)
        for held in sorted(prepared):
            groups = prepared[held]
            for key in sorted(groups, key=str):
                group, lookup = groups[key]
                targets = [r["target"] for r in group]
                rng.shuffle(targets)
                for event, target in zip(group, targets):
                    gain = lookup[event["source"], target]
                    total += gain
                    pair = event["source"], target
                    pair_gain[pair] += gain
                    pair_count[pair] += 1
                    pair_folios[pair].add(held)
        eligible = [pair_gain[pair] for pair in pair_gain
                    if pair_count[pair] >= MIN_REL and len(pair_folios[pair]) >= MIN_REL_FOLIOS]
        top = max(eligible, default=0.0)
        rows.append({"world": world, "total_host_gain_bits": total,
                     "top_eligible_relation_gain_bits": top, "eligible_relations": len(eligible),
                     "claim_state": "HELD_TARGET_ALIGNMENT_NULL"})
        gains.append(total)
        tops.append(top)
    summary = {"observed_total_host_gain_bits": real_total,
               "observed_top_relation_gain_bits": observed_top,
               "total_gain_p": (1 + sum(x >= real_total - 1e-12 for x in gains)) / (WORLDS + 1),
               "top_relation_maxT_p": (1 + sum(x >= observed_top - 1e-12 for x in tops)) / (WORLDS + 1),
               "null_total_mean": sum(gains) / WORLDS, "null_top_mean": sum(tops) / WORLDS,
               "swappable_test_events": swappable, "target_variable_test_events": variable}
    for relation in relation_rows:
        gain = relation["held_folio_gain_bits"]
        relation["maxT_p"] = (1 + sum(x >= gain - 1e-12 for x in tops)) / (WORLDS + 1)
        if relation["label"] == "STABLE_DIRECTED_RELATION" and relation["maxT_p"] > .05:
            relation["label"] = "STABLE_DIRECTION_UNCORRECTED_ONLY"
    return rows, summary


def main() -> None:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    assert design["status"] == "FROZEN_BEFORE_SCORING" and design["community_k"] == K
    source_rows, events, rejected, source_total = load_events()
    target_vocab = sorted({r["target"] for r in events}, key=opaque)
    endpoint = Counter()
    for row in events:
        endpoint[row["source"]] += 1
        endpoint[row["target"]] += 1
    panel = tuple(x for x, _ in sorted(endpoint.items(), key=lambda item: (-item[1], opaque(item[0])))[:PANEL_N])

    host_manifest = []
    source_count = Counter(r["source"] for r in events)
    target_count = Counter(r["target"] for r in events)
    host_folios = defaultdict(set)
    for row in events:
        host_folios[row["source"]].add(row["folio"])
        host_folios[row["target"]].add(row["folio"])
    for host in sorted(set(source_count) | set(target_count), key=opaque):
        host_manifest.append({"host_id": opaque(host), "page_host": host,
                              "source_events": source_count[host], "target_events": target_count[host],
                              "endpoint_events": endpoint[host], "physical_folios": len(host_folios[host]),
                              "community_panel": int(host in panel),
                              "claim_state": "OPAQUE_IDENTITY_NO_LEXEME_OR_MEANING"})
    edge_rows = [{"event_id": r["event_id"], "source_host_id": opaque(r["source"]),
                  "target_host_id": opaque(r["target"]), "source_host": r["source"], "target_host": r["target"],
                  "locus": r["locus"], "physical_folio": r["folio"], "section": r["section"],
                  "currier": r["currier"], "hand": r["hand"], "source_index": r["source_index"],
                  "target_index": r["target_index"], "source_frequency_bin": r["source_frequency_bin"],
                  "position_quartile": r["position_quartile"], "line_count_bin": r["line_count_bin"],
                  "claim_state": "PHYSICAL_ADJACENCY_NO_WORD_BOUNDARY_OR_MEANING"} for r in events]

    all_folds = []
    contributions = []
    artifacts = None
    summaries = {}
    for mode in ("HELD_FOLIO", "HELD_SECTION", "HELD_HAND"):
        fold_rows, contrib, mode_artifacts = score_mode(events, mode, target_vocab, panel)
        all_folds += fold_rows
        contributions += contrib
        summaries[mode] = aggregate_folds(fold_rows)
        if mode == "HELD_FOLIO":
            artifacts = mode_artifacts
    assert artifacts is not None

    community_rows, reference_community = community_stability(events, panel)
    relation_rows = relation_atlas(events, contributions)
    null_rows, null_summary = held_alignment_null(events, artifacts, relation_rows)

    section_comm = [r for r in community_rows if r["axis"] == "HELD_SECTION"]
    hand_comm = [r for r in community_rows if r["axis"] == "HELD_HAND"]
    section_median = float(np.median([r["coassignment_jaccard"] for r in section_comm]))
    section_q95 = float(np.median([r["null_q95"] for r in section_comm]))
    hand_median = float(np.median([r["coassignment_jaccard"] for r in hand_comm]))
    hand_q95 = float(np.median([r["null_q95"] for r in hand_comm]))
    community_predictive = all(summaries[mode]["community_gain_vs_nuisance_bits"] > 0 for mode in summaries)
    community_stable = section_median > section_q95 and hand_median > hand_q95 and community_predictive
    exact_all_positive = all(summaries[mode]["host_gain_vs_nuisance_bits"] > 0 for mode in summaries)
    relation_pass = any(r["label"] == "STABLE_DIRECTED_RELATION" and r["maxT_p"] <= .05 for r in relation_rows)
    null_pass = null_summary["total_gain_p"] <= .05
    if exact_all_positive and null_pass and relation_pass and community_stable:
        status = "OPAQUE_HOST_RELATION_GRAPH_TRANSFER_SUPPORTED"
    elif exact_all_positive and null_pass:
        status = "EXACT_HOST_TRANSFER_WITHOUT_STABLE_COMMUNITIES"
    elif summaries["HELD_FOLIO"]["host_gain_vs_nuisance_bits"] > 0:
        status = "OPAQUE_HOST_RELATIONS_LOCAL_ONLY"
    else:
        status = "OPAQUE_HOST_RELATIONS_NOT_TRANSFERABLE"

    counterexamples = []
    for row in sorted(relation_rows, key=lambda r: r["held_folio_gain_bits"])[:15]:
        counterexamples.append({"counterexample_type": "NEGATIVE_DIRECTED_RELATION", "item": f"{row['source_host_id']}->{row['target_host_id']}",
                                "evidence": f"folio/section/hand gains {row['held_folio_gain_bits']:+.6f}/{row['held_section_gain_bits']:+.6f}/{row['held_hand_gain_bits']:+.6f}",
                                "impact": "Recurrent exact adjacency does not guarantee transferable directional gain."})
    counterexamples += [
        {"counterexample_type": "PRIOR_TRANSITION_NEGATIVES", "item": "GDT060/GDT111",
         "evidence": "Prior suffix/full-transition models did not establish a compositional pre-host to post-host algebra.",
         "impact": "Any GDT165 gain is exact opaque identity structure, not a resurrection of glyph-edge transition semantics."},
        {"counterexample_type": "COMMUNITY_RESOLUTION", "item": "K8_TOP128",
         "evidence": "One fixed K and frequency-only 128-node panel were tested.",
         "impact": "Failure does not exclude every graph resolution; success would remain anonymous."}
    ]
    variants = [
        {"variant_id": "V00", "status": "PRIMARY", "description": "Exact opaque source-host next-host code versus six-component nuisance, held folio."},
        {"variant_id": "V01", "status": "RUN_TRANSFER", "description": "Held section."},
        {"variant_id": "V02", "status": "RUN_TRANSFER", "description": "Held hand."},
        {"variant_id": "V03", "status": "RUN_MODEL", "description": "Fixed K8 spectral community backoff on top128 frequency-only panel."},
        {"variant_id": "V04", "status": "RUN_ATLAS", "description": "Directed pair support>=8 and >=3 folios with three transfer gains."},
        {"variant_id": "V05", "status": "RUN_NULL", "description": "1024 held-folio target permutations within exact joint nuisance strata."},
        {"variant_id": "V06", "status": "FORBIDDEN", "description": "No glyph/substitution/edit/substring/same-group HPR2/semantic/f84 feature."}
    ]

    def fmt(rows):
        return [{k: (f"{v:.12f}" if isinstance(v, float) else v) for k, v in row.items()} for row in rows]
    write(HOSTS, fmt(host_manifest))
    write(EDGES, fmt(edge_rows))
    write(FOLDS, fmt(all_folds))
    write(RELATIONS, fmt(relation_rows))
    write(COMMUNITIES, fmt(community_rows))
    write(NULLS, fmt(null_rows))
    write(COUNTER, counterexamples)
    write(VARIANTS, variants)

    stable_rel = [r for r in relation_rows if r["label"] == "STABLE_DIRECTED_RELATION"]
    top_rel = relation_rows[:15]
    report = f"""# GDT165 — opaque PAGE_HOST relation graph report

Decision: **{status}**.

## Capacity

The parser-firewalled inventory contains {len(events):,} directed within-line
adjacencies on {len(set(r['folio'] for r in events))} physical folios,
{len(source_count):,} source identities, and {len(target_vocab):,} target identities.
The fixed 128-host community panel contains
{sum(1 for r in events if r['source'] in panel or r['target'] in panel)/len(events):.2%}
of edges at at least one endpoint.

## Held prediction

| split | events/folds | exact-host gain | bits/event | positive folds | community gain | exact over community | source seen | host top1/top5 | nuisance top1/top5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
""" + "".join(f"| `{mode}` | {s['events']}/{s['folds']} | {s['host_gain_vs_nuisance_bits']:+.3f} | {s['host_gain_per_event']:+.5f} | {s['positive_host_folds']}/{s['folds']} | {s['community_gain_vs_nuisance_bits']:+.3f} | {s['host_gain_vs_community_bits']:+.3f} | {s['source_seen_fraction']:.3f} | {s['host_top1']:.4f}/{s['host_top5']:.4f} | {s['nuisance_top1']:.4f}/{s['nuisance_top5']:.4f} |\n" for mode, s in summaries.items()) + f"""

The held-folio alignment null gives p={null_summary['total_gain_p']:.6f};
the directed-relation maxT p is {null_summary['top_relation_maxT_p']:.6f}.
The null has {null_summary['swappable_test_events']:,} swappable and
{null_summary['target_variable_test_events']:,} target-variable held events.
The total-gain p-value is an upper-tail alignment diagnostic: the observed
{null_summary['observed_total_host_gain_bits']:+.3f}-bit gain is less negative
than the shuffled mean {null_summary['null_total_mean']:+.3f}, but it remains
far below zero.  It therefore does not reverse the failed predictive result.

## Community stability

Held-section median coassignment Jaccard is {section_median:.4f} versus median
null q95 {section_q95:.4f}; held-hand is {hand_median:.4f} versus
{hand_q95:.4f}.  Community prediction is
`{'POSITIVE_ALL_SPLITS' if community_predictive else 'NOT_POSITIVE_ALL_SPLITS'}`.

| axis | held | hosts | Jaccard | null q95 | p | above q95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
""" + "".join(f"| `{r['axis']}` | `{r['held']}` | {r['common_active_hosts']} | {r['coassignment_jaccard']:.4f} | {r['null_q95']:.4f} | {r['inclusive_p']:.4f} | {r['above_null_q95']} |\n" for r in community_rows) + f"""

## Strongest eligible directed relations

| source -> target | occurrences/folios | held-folio | held-section | held-hand | maxT p | label |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
""" + "".join(f"| `{r['source_host_id']}->{r['target_host_id']}` | {r['occurrences']}/{r['folios']} | {r['held_folio_gain_bits']:+.3f} | {r['held_section_gain_bits']:+.3f} | {r['held_hand_gain_bits']:+.3f} | {r['maxT_p']:.4f} | `{r['label']}` |\n" for r in top_rel) + f"""

Exact display identities are retained in the machine atlas for reproducible
joins, but neither their characters nor apparent similarity entered any model.

## Interpretation

This test concerns opaque exact-identity dependence in physical source-group
order.  It is distinct from GDT060/GDT111's suffix, DY, and edge-state models
and from GDT163/GDT164 substitution tests.  Stable directed relations found here
would remain anonymous distributional dependencies, not words or meanings.

All f84-prefix rows were rejected before retention.  No f84r material was
opened, queried, retained, joined, or scored.
"""
    REPORT.write_text(report, encoding="utf-8")

    result = {"schema": "GDT165_OPAQUE_PAGE_HOST_RELATION_GRAPH_RESULT_V1", "status": status,
              "source_total_rows": source_total, "source_retained_rows": len(source_rows), "rejected_f84_rows": rejected,
              "events": len(events), "physical_folios": len({r["folio"] for r in events}),
              "source_identities": len(source_count), "target_identities": len(target_vocab),
              "community_panel_size": len(panel), "community_reference": {opaque(host): reference_community[host] for host in panel},
              "summaries": summaries, "community_summary": {"section_median_jaccard": section_median,
                  "section_median_null_q95": section_q95, "hand_median_jaccard": hand_median,
                  "hand_median_null_q95": hand_q95, "predictive_all_splits": community_predictive,
                  "stable": community_stable},
              "directed_relations": {"eligible": len(relation_rows), "stable_maxT": len(stable_rel),
                                     "top_maxT_p": null_summary["top_relation_maxT_p"]},
              "null": null_summary,
              "null_interpretation": "Observed identity alignment is less negative than the shuffled alignment but remains below zero; this is sparse-order evidence, not positive global held prediction.",
              "decision_inputs": {"exact_all_splits_positive": exact_all_positive, "held_folio_null_pass": null_pass,
                                  "stable_maxT_relation": relation_pass, "community_gate": community_stable},
              "interpretation": "Opaque exact PAGE_HOST identity prediction and anonymous graph structure only; no character features or same-group HPR2 fields enter.",
              "claim_ceiling": "No word, lexeme, code value, morpheme, POS, language, semantic role, meaning, plaintext, or translation.",
              "f84r": {"opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
              "inputs": {SOURCE.name: sha(SOURCE), DESIGN.name: sha(DESIGN), "gdt164_result.json": sha(ROOT / "gdt164_result.json"),
                         "gdt111_result.json": sha(ROOT / "gdt111_result.json"), "gdt060_result.json": sha(ROOT / "gdt060_result.json")},
              "implementation": {Path(__file__).name: sha(Path(__file__))},
              "outputs": {p.name: sha(p) for p in (HOSTS,EDGES,FOLDS,RELATIONS,COMMUNITIES,NULLS,COUNTER,VARIANTS)},
              "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}}
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "held_folio_gain": summaries["HELD_FOLIO"]["host_gain_vs_nuisance_bits"],
                      "held_section_gain": summaries["HELD_SECTION"]["host_gain_vs_nuisance_bits"],
                      "held_hand_gain": summaries["HELD_HAND"]["host_gain_vs_nuisance_bits"],
                      "null_p": null_summary["total_gain_p"], "stable_relations": len(stable_rel)}, sort_keys=True))


if __name__ == "__main__":
    main()
