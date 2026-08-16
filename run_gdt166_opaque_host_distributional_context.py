#!/usr/bin/env python3
"""GDT166: opaque PAGE_HOST distributional context without fixed order."""
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
FRAMES = ROOT / "gdt046_line_frames.tsv"
DESIGN = ROOT / "gdt166_design.json"
METHOD = ROOT / "GDT166_OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_METHOD.md"
REPORT = ROOT / "GDT166_OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_REPORT.md"
INVENTORY = ROOT / "gdt166_context_inventory.tsv"
SCORES = ROOT / "gdt166_context_scores.tsv"
FOLDS = ROOT / "gdt166_context_fold_scores.tsv"
NEIGHBORS = ROOT / "gdt166_neighbor_relations.tsv"
NEIGHBOR_STABILITY = ROOT / "gdt166_neighbor_stability.tsv"
NULLS = ROOT / "gdt166_context_null.tsv"
NEIGHBOR_NULL = ROOT / "gdt166_neighbor_null.tsv"
COUNTER = ROOT / "gdt166_counterexamples.tsv"
VARIANTS = ROOT / "gdt166_variant_log.tsv"
RESULT = ROOT / "gdt166_result.json"

MODES = ("WINDOW_PM2", "WHOLE_LINE", "PARAGRAPH_BAG")
AXES = (("HELD_FOLIO", "folio"), ("HELD_SECTION", "section"), ("HELD_HAND", "hand"))
FEATURES = ("section", "currier", "hand", "frequency_bin", "position_quartile", "line_count_bin")
ALPHA = 32.0
BETA = 16.0
WORLDS = 1024
FOCAL_PANEL_N = 64
CONTEXT_PANEL_N = 256
TRAIN_MASS = 16.0
HELD_MASS = 4.0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                     separators=(",", ":")).encode()).hexdigest()


def opaque(value: str) -> str:
    return "H" + hashlib.sha256(value.encode()).hexdigest()[:16]


def seed(label: str) -> int:
    return int(hashlib.sha256(label.encode()).hexdigest()[:16], 16)


def fbin(n: int) -> str:
    return "F1" if n == 1 else "F2_4" if n <= 4 else "F5_15" if n <= 15 else "F16_63" if n <= 63 else "F64P"


def lbin(n: int) -> str:
    return str(n) if n <= 4 else "5_7" if n <= 7 else "8P"


def locus_key(value: str):
    page, line = value.split(".")
    return page, int(line)


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


def load() -> tuple[list[dict[str, object]], dict[str, list[dict[str, object]]], dict[str, int]]:
    rows = []
    source_total = source_rejected = 0
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle, delimiter="\t"):
            source_total += 1
            page, locus = raw["page"], raw["locus"]
            if page.startswith("f84") or locus.startswith("f84"):
                source_rejected += 1
                continue
            rows.append({"host": raw["page_host"], "locus": locus, "page": page,
                         "folio": raw["physical_folio"], "section": raw["section"],
                         "currier": raw["currier"], "hand": raw["hand"],
                         "index": int(raw["group_index"]), "group_count": int(raw["group_count"]),
                         "position_quartile": raw["position_quartile"]})
    assert (source_total, source_rejected, len(rows)) == (15592, 228, 15364)
    counts = Counter(row["host"] for row in rows)
    for row in rows:
        row["frequency_bin"] = fbin(counts[row["host"]])
        row["line_count_bin"] = lbin(row["group_count"])
        row["occurrence_id"] = f"{row['locus']}:{row['index']}"
        row["nuisance_key"] = tuple(row[f] for f in FEATURES)
    by_line = defaultdict(list)
    for row in rows:
        by_line[row["locus"]].append(row)
    for line in by_line.values():
        line.sort(key=lambda x: x["index"])

    contexts: dict[str, list[dict[str, object]]] = {mode: [] for mode in MODES}
    for locus in sorted(by_line, key=locus_key):
        line = by_line[locus]
        whole = Counter(r["host"] for r in line)
        for i, row in enumerate(line):
            window = Counter(line[j]["host"] for j in range(max(0, i - 2), min(len(line), i + 3)) if j != i)
            line_context = whole.copy()
            line_context[row["host"]] -= 1
            if not line_context[row["host"]]:
                del line_context[row["host"]]
            if window:
                contexts["WINDOW_PM2"].append({**row, "context": window})
            if line_context:
                contexts["WHOLE_LINE"].append({**row, "context": line_context})

    frames = {}
    frame_total = frame_rejected = 0
    with FRAMES.open(encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle, delimiter="\t"):
            frame_total += 1
            if raw["page"].startswith("f84") or raw["locus"].startswith("f84"):
                frame_rejected += 1
                continue
            frames[raw["locus"]] = {"page": raw["page"], "start": int(raw["paragraph_start"])}
    assert (frame_total, frame_rejected, len(frames)) == (1164, 21, 1143)
    page_current: dict[str, str] = {}
    page_number = Counter()
    paragraph_of = {}
    for locus in sorted(frames, key=locus_key):
        page = frames[locus]["page"]
        if page not in page_current or frames[locus]["start"]:
            page_number[page] += 1
            page_current[page] = f"{page}:P{page_number[page]}"
        paragraph_of[locus] = page_current[page]
    paragraphs = defaultdict(list)
    for locus, paragraph in paragraph_of.items():
        paragraphs[paragraph].extend(by_line.get(locus, []))
    for paragraph in sorted(paragraphs):
        items = paragraphs[paragraph]
        bag = Counter(r["host"] for r in items)
        for row in items:
            context = bag.copy()
            context[row["host"]] -= 1
            if not context[row["host"]]:
                del context[row["host"]]
            if context:
                contexts["PARAGRAPH_BAG"].append({**row, "context": context, "paragraph_id": paragraph})
    capacity = {"source_total": source_total, "source_rejected": source_rejected,
                "frame_total": frame_total, "frame_rejected": frame_rejected,
                "lines": len(by_line), "paragraphs": len(paragraphs)}
    assert len(contexts["WINDOW_PM2"]) == len(contexts["WHOLE_LINE"]) == 15203
    assert len(contexts["PARAGRAPH_BAG"]) == 8447 and len(paragraphs) == 288
    return rows, contexts, capacity


def train_model(events: list[dict[str, object]], vocab: tuple[str, ...]):
    target = Counter()
    feature_target = [Counter() for _ in FEATURES]
    feature_total = [Counter() for _ in FEATURES]
    host_target = Counter()
    host_total = Counter()
    for event in events:
        size = sum(event["context"].values())
        for context, count in event["context"].items():
            weight = count / size
            target[context] += weight
            for j, feature in enumerate(FEATURES):
                feature_target[j][event[feature], context] += weight
            host_target[event["host"], context] += weight
        for j, feature in enumerate(FEATURES):
            feature_total[j][event[feature]] += 1.0
        host_total[event["host"]] += 1.0
    return {"target": target, "n": float(len(events)), "v": len(vocab),
            "feature_target": feature_target, "feature_total": feature_total,
            "host_target": host_target, "host_total": host_total}


def probabilities(model, event, target):
    q = (model["target"][target] + .5) / (model["n"] + .5 * model["v"])
    pieces = []
    for j, feature in enumerate(FEATURES):
        value = event[feature]
        pieces.append((model["feature_target"][j][value, target] + ALPHA * q) /
                      (model["feature_total"][j][value] + ALPHA))
    nuisance = sum(pieces) / len(pieces)
    host = (model["host_target"][event["host"], target] + BETA * nuisance) / (model["host_total"][event["host"]] + BETA)
    return q, nuisance, host


def score_event(model, event):
    total = sum(event["context"].values())
    out = Counter()
    for target, count in event["context"].items():
        weight = count / total
        q, nuisance, host = probabilities(model, event, target)
        out["unigram_bits"] -= weight * math.log2(q)
        out["nuisance_bits"] -= weight * math.log2(nuisance)
        out["host_bits"] -= weight * math.log2(host)
        if event["host"] == "ok" and target == "y":
            out["ok_y_weight"] += weight
            out["ok_y_gain_bits"] += weight * math.log2(host / nuisance)
    out["gain_bits"] = out["nuisance_bits"] - out["host_bits"]
    return out


def score_splits(events, mode, vocab):
    fold_rows = []
    artifacts = {}
    for axis, key in AXES:
        for held in sorted({str(r[key]) for r in events}):
            train_events = [r for r in events if str(r[key]) != held]
            test_events = [r for r in events if str(r[key]) == held]
            model = train_model(train_events, vocab)
            totals = Counter()
            seen = 0
            for event in test_events:
                totals.update(score_event(model, event))
                seen += int(model["host_total"][event["host"]] > 0)
            row = {"context_mode": mode, "axis": axis, "held": held,
                   "focal_occurrences": len(test_events), "training_occurrences": len(train_events),
                   "source_seen_occurrences": seen, "source_seen_fraction": seen / len(test_events)}
            for field in ("unigram_bits", "nuisance_bits", "host_bits", "gain_bits", "ok_y_weight", "ok_y_gain_bits"):
                row[field] = totals[field]
            row["gain_without_ok_y_bits"] = totals["gain_bits"] - totals["ok_y_gain_bits"]
            row["gain_per_focal"] = totals["gain_bits"] / len(test_events)
            row["claim_state"] = "OPAQUE_CONTEXT_DISTRIBUTION_NO_LEXEME_OR_MEANING"
            fold_rows.append(row)
            if axis == "HELD_FOLIO":
                artifacts[held] = model, test_events
    return fold_rows, artifacts


def alignment_null(mode, events, artifacts):
    prepared = {}
    swappable = variable = 0
    for held, (model, test_events) in artifacts.items():
        groups = defaultdict(list)
        for event in test_events:
            groups[event["nuisance_key"]].append(event)
        packed = {}
        for key, group in groups.items():
            sources = sorted({e["host"] for e in group}, key=opaque)
            targets = {target for e in group for target in e["context"]}
            exemplar = group[0]
            log_lookup = {}
            for source in sources:
                probe = dict(exemplar)
                probe["host"] = source
                for target in targets:
                    _, nuisance, host = probabilities(model, probe, target)
                    log_lookup[source, target] = math.log2(host / nuisance)
            event_lookup = {}
            for event in group:
                size = sum(event["context"].values())
                for source in sources:
                    event_lookup[event["occurrence_id"], source] = sum(
                        count / size * log_lookup[source, target] for target, count in event["context"].items())
            packed[key] = group, event_lookup
        prepared[held] = packed
        swappable += sum(len(g) for g in groups.values() if len(g) >= 2)
        variable += sum(len(g) for g in groups.values() if len({e["host"] for e in g}) >= 2)
    rng = random.Random(seed("GDT166_CONTEXT_NULL_" + mode))
    totals = []
    for _ in range(WORLDS):
        gain = 0.0
        for held in sorted(prepared):
            for key in sorted(prepared[held], key=str):
                group, lookup = prepared[held][key]
                sources = [e["host"] for e in group]
                rng.shuffle(sources)
                gain += sum(lookup[event["occurrence_id"], source] for event, source in zip(group, sources))
        totals.append(gain / len(events))
    return totals, swappable, variable


def aggregate_scores(fold_rows, null_by_mode):
    rows = []
    observed_rates = {}
    for mode in MODES:
        for axis, _ in AXES:
            subset = [r for r in fold_rows if r["context_mode"] == mode and r["axis"] == axis]
            n = sum(r["focal_occurrences"] for r in subset)
            row = {"context_mode": mode, "axis": axis, "focal_occurrences": n,
                   "folds": len(subset), "unigram_bits": sum(r["unigram_bits"] for r in subset),
                   "nuisance_bits": sum(r["nuisance_bits"] for r in subset),
                   "host_bits": sum(r["host_bits"] for r in subset),
                   "gain_bits": sum(r["gain_bits"] for r in subset),
                   "positive_folds": sum(r["gain_bits"] > 0 for r in subset),
                   "source_seen_fraction": sum(r["source_seen_occurrences"] for r in subset) / n,
                   "ok_y_weight": sum(r["ok_y_weight"] for r in subset),
                   "ok_y_gain_bits": sum(r["ok_y_gain_bits"] for r in subset),
                   "gain_without_ok_y_bits": sum(r["gain_without_ok_y_bits"] for r in subset)}
            row["gain_per_focal"] = row["gain_bits"] / n
            row["claim_state"] = "OPAQUE_CONTEXT_DISTRIBUTION_NO_LEXEME_OR_MEANING"
            if axis == "HELD_FOLIO":
                observed_rates[mode] = row["gain_per_focal"]
                null = null_by_mode[mode]
                row["null_mean_gain_per_focal"] = sum(null) / WORLDS
                row["alignment_excess_per_focal"] = row["gain_per_focal"] - row["null_mean_gain_per_focal"]
                row["local_p"] = (1 + sum(x >= row["gain_per_focal"] - 1e-12 for x in null)) / (WORLDS + 1)
            rows.append(row)
    null_means = {m: sum(null_by_mode[m]) / WORLDS for m in MODES}
    null_max = [max(null_by_mode[m][w] - null_means[m] for m in MODES) for w in range(WORLDS)]
    for row in rows:
        if row["axis"] == "HELD_FOLIO":
            observed_excess = row["gain_per_focal"] - null_means[row["context_mode"]]
            row["max3_p"] = (1 + sum(x >= observed_excess - 1e-12 for x in null_max)) / (WORLDS + 1)
    return rows, null_max


def ppmi_profiles(events, focal_panel, context_panel):
    counts = defaultdict(Counter)
    mass = Counter()
    global_context = Counter()
    for event in events:
        if event["host"] not in focal_panel:
            continue
        total = sum(event["context"].values())
        for target, count in event["context"].items():
            mapped = target if target in context_panel else "__OTHER__"
            weight = count / total
            counts[event["host"]][mapped] += weight
            global_context[mapped] += weight
        mass[event["host"]] += 1.0
    dimensions = tuple(sorted(set(context_panel) | {"__OTHER__"}, key=opaque))
    total_global = sum(global_context.values())
    vectors = {}
    for host in focal_panel:
        vector = np.zeros(len(dimensions), dtype=float)
        if mass[host] > 0 and total_global > 0:
            for j, target in enumerate(dimensions):
                if counts[host][target] > 0 and global_context[target] > 0:
                    ratio = (counts[host][target] / mass[host]) / (global_context[target] / total_global)
                    vector[j] = max(0.0, math.log2(ratio))
        norm = float(np.linalg.norm(vector))
        if norm:
            vector /= norm
        vectors[host] = vector
    return vectors, mass


def neighbor_tests(events, focal_panel, context_panel, frequency):
    predictions = []
    reference_vectors, reference_mass = ppmi_profiles(events, focal_panel, context_panel)
    reference_rows = []
    for host in focal_panel:
        candidates = [x for x in focal_panel if x != host and reference_mass[x] >= TRAIN_MASS]
        if reference_mass[host] < TRAIN_MASS or not candidates:
            continue
        ranked = sorted(candidates, key=lambda x: (-float(reference_vectors[host] @ reference_vectors[x]), opaque(x)))
        neighbor = ranked[0]
        reference_rows.append({"source_host_id": opaque(host), "source_host": host,
                               "neighbor_host_id": opaque(neighbor), "neighbor_host": neighbor,
                               "source_mass": reference_mass[host], "neighbor_mass": reference_mass[neighbor],
                               "cosine": float(reference_vectors[host] @ reference_vectors[neighbor]),
                               "frequency_bin": fbin(frequency[host]),
                               "claim_state": "OPAQUE_DISTRIBUTIONAL_NEIGHBOR_NO_LEXEME_OR_MEANING"})
    for axis, key in AXES:
        for held in sorted({str(r[key]) for r in events}):
            train_events = [r for r in events if str(r[key]) != held]
            held_events = [r for r in events if str(r[key]) == held]
            train_vectors, train_mass = ppmi_profiles(train_events, focal_panel, context_panel)
            held_vectors, held_mass = ppmi_profiles(held_events, focal_panel, context_panel)
            train_candidates = [h for h in focal_panel if train_mass[h] >= TRAIN_MASS]
            held_candidates = [h for h in focal_panel if held_mass[h] >= HELD_MASS]
            for host in focal_panel:
                if train_mass[host] < TRAIN_MASS or held_mass[host] < HELD_MASS:
                    continue
                candidates = [x for x in train_candidates if x != host]
                if not candidates:
                    continue
                ranked_train = sorted(candidates, key=lambda x: (-float(train_vectors[host] @ train_vectors[x]), opaque(x)))
                predicted = ranked_train[0]
                if predicted not in held_candidates:
                    continue
                held_ranked = sorted((x for x in held_candidates if x != host),
                                     key=lambda x: (-float(held_vectors[host] @ held_vectors[x]), opaque(x)))
                if predicted not in held_ranked:
                    continue
                rank = held_ranked.index(predicted) + 1
                rank_map = {x: i + 1 for i, x in enumerate(held_ranked)}
                predictions.append({"axis": axis, "held": held, "source": host,
                                    "predicted": predicted, "training_cosine": float(train_vectors[host] @ train_vectors[predicted]),
                                    "held_cosine": float(held_vectors[host] @ held_vectors[predicted]),
                                    "held_rank": rank, "candidate_count": len(held_ranked),
                                    "reciprocal_rank": 1.0 / rank, "top1": int(rank == 1), "top5": int(rank <= 5),
                                    "training_mass": train_mass[host], "held_mass": held_mass[host],
                                    "frequency_bin": fbin(frequency[host]), "rank_map": rank_map})
    return reference_rows, predictions


def neighbor_null(predictions):
    observed = {}
    for axis, _ in AXES:
        rows = [r for r in predictions if r["axis"] == axis]
        observed[axis] = sum(r["reciprocal_rank"] for r in rows) / len(rows) if rows else 0.0
    rng = random.Random(seed("GDT166_NEIGHBOR_NULL"))
    groups = defaultdict(list)
    for row in predictions:
        groups[row["axis"], row["held"], row["frequency_bin"]].append(row)
    swappable = {axis: sum(len(g) for (a, _, _), g in groups.items() if a == axis and len(g) >= 2) for axis, _ in AXES}
    worlds = []
    for world in range(WORLDS):
        sums = Counter()
        counts = Counter()
        for key in sorted(groups, key=str):
            group = groups[key]
            predicted = [r["predicted"] for r in group]
            rng.shuffle(predicted)
            for row, neighbor in zip(group, predicted):
                rank = row["rank_map"].get(neighbor)
                sums[row["axis"]] += 1.0 / rank if rank else 0.0
                counts[row["axis"]] += 1
        values = {axis: sums[axis] / counts[axis] if counts[axis] else 0.0 for axis, _ in AXES}
        worlds.append({"world": world, **values})
    null_means = {axis: sum(row[axis] for row in worlds) / WORLDS for axis, _ in AXES}
    null_max = [max(row[axis] - null_means[axis] for axis, _ in AXES) for row in worlds]
    summary_rows = []
    for axis, _ in AXES:
        rows = [r for r in predictions if r["axis"] == axis]
        values = [w[axis] for w in worlds]
        summary_rows.append({"axis": axis, "predictions": len(rows),
                             "eligible_folds": len({r["held"] for r in rows}),
                             "mean_reciprocal_rank": observed[axis],
                             "top1": sum(r["top1"] for r in rows), "top5": sum(r["top5"] for r in rows),
                             "null_mean": null_means[axis],
                             "excess_mrr": observed[axis] - null_means[axis],
                             "local_p": (1 + sum(x >= observed[axis] - 1e-12 for x in values)) / (WORLDS + 1),
                             "max3_p": (1 + sum(x >= observed[axis] - null_means[axis] - 1e-12 for x in null_max)) / (WORLDS + 1),
                             "swappable_predictions": swappable[axis],
                             "claim_state": "OPAQUE_DISTRIBUTIONAL_NEIGHBOR_NO_LEXEME_OR_MEANING"})
    return worlds, summary_rows


def main() -> None:
    design = json.loads(DESIGN.read_text())
    assert design["status"] == "FROZEN_BEFORE_SCORING" and design["nearest_neighbor"]["context"] == "WHOLE_LINE"
    rows, contexts, capacity = load()
    vocabulary = tuple(sorted({r["host"] for r in rows}, key=opaque))
    occurrence_frequency = Counter(r["host"] for r in rows)

    inventory_rows = []
    for mode in MODES:
        for event in contexts[mode]:
            context_payload = sorted((opaque(k), v) for k, v in event["context"].items())
            inventory_rows.append({"context_mode": mode, "occurrence_id": event["occurrence_id"],
                                   "focal_host_id": opaque(event["host"]), "focal_host": event["host"],
                                   "locus": event["locus"], "physical_folio": event["folio"],
                                   "section": event["section"], "currier": event["currier"], "hand": event["hand"],
                                   "group_index": event["index"], "group_count": event["group_count"],
                                   "context_raw_count": sum(event["context"].values()),
                                   "context_unique_identities": len(event["context"]),
                                   "context_sha256": csha(context_payload),
                                   "claim_state": "OPAQUE_CONTEXT_INVENTORY_NO_LEXEME_OR_MEANING"})

    fold_rows = []
    artifacts = {}
    null_by_mode = {}
    null_capacity = {}
    for mode in MODES:
        scored, held_artifacts = score_splits(contexts[mode], mode, vocabulary)
        fold_rows.extend(scored)
        artifacts[mode] = held_artifacts
        null, swappable, variable = alignment_null(mode, contexts[mode], held_artifacts)
        null_by_mode[mode] = null
        null_capacity[mode] = {"swappable": swappable, "variable": variable}
    score_rows, context_null_max = aggregate_scores(fold_rows, null_by_mode)
    null_rows = []
    for world in range(WORLDS):
        row = {"world": world}
        for mode in MODES:
            row[mode + "_gain_per_focal"] = null_by_mode[mode][world]
        row["max3_null_centered_excess_per_focal"] = context_null_max[world]
        row["claim_state"] = "HELD_FOLIO_FOCAL_IDENTITY_ALIGNMENT_NULL"
        null_rows.append(row)

    focal_panel = tuple(h for h, _ in sorted(occurrence_frequency.items(), key=lambda x: (-x[1], opaque(x[0])))[:FOCAL_PANEL_N])
    context_mass = Counter()
    for event in contexts["WHOLE_LINE"]:
        size = sum(event["context"].values())
        for target, count in event["context"].items():
            context_mass[target] += count / size
    context_panel = tuple(h for h, _ in sorted(context_mass.items(), key=lambda x: (-x[1], opaque(x[0])))[:CONTEXT_PANEL_N])
    reference_neighbors, neighbor_predictions = neighbor_tests(contexts["WHOLE_LINE"], focal_panel, context_panel, occurrence_frequency)
    neighbor_worlds, neighbor_summary = neighbor_null(neighbor_predictions)
    neighbor_rows = [{k: v for k, v in row.items() if k != "rank_map"} | {
        "source_host_id": opaque(row["source"]), "predicted_neighbor_id": opaque(row["predicted"]),
        "source_host": row["source"], "predicted_neighbor": row["predicted"],
        "claim_state": "OPAQUE_DISTRIBUTIONAL_NEIGHBOR_NO_LEXEME_OR_MEANING"} for row in neighbor_predictions]
    neighbor_null_rows = [{"world": row["world"],
                           "held_folio_mrr": row["HELD_FOLIO"],
                           "held_section_mrr": row["HELD_SECTION"],
                           "held_hand_mrr": row["HELD_HAND"],
                           "max3_null_centered_excess": max(row[a] - next(x["null_mean"] for x in neighbor_summary if x["axis"] == a) for a, _ in AXES),
                           "claim_state": "NEIGHBOR_ASSIGNMENT_FREQUENCY_STRATIFIED_NULL"} for row in neighbor_worlds]

    exact_context_pass = []
    for mode in MODES:
        by_axis = {r["axis"]: r for r in score_rows if r["context_mode"] == mode}
        exact_context_pass.append(mode if all(by_axis[a]["gain_bits"] > 0 for a, _ in AXES)
                                  and by_axis["HELD_FOLIO"]["max3_p"] <= .05 else None)
    passing_modes = [x for x in exact_context_pass if x]
    neighbor_pass = all(r["max3_p"] <= .05 and r["mean_reciprocal_rank"] > r["null_mean"] for r in neighbor_summary)
    folio_positive = any(r["axis"] == "HELD_FOLIO" and r["gain_bits"] > 0 for r in score_rows)
    if passing_modes and neighbor_pass:
        status = "OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_SUPPORTED"
    elif passing_modes:
        status = "OPAQUE_HOST_CONTEXT_WITHOUT_STABLE_NEIGHBORS"
    elif folio_positive:
        status = "DISTRIBUTIONAL_CONTEXT_LOCAL_ONLY"
    else:
        status = "OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_NOT_TRANSFERABLE"

    counterexamples = []
    for row in score_rows:
        if row["gain_bits"] <= 0:
            counterexamples.append({"counterexample_type": "NONPOSITIVE_CONTEXT_TRANSFER",
                                    "item": f"{row['context_mode']}:{row['axis']}",
                                    "evidence": f"gain={row['gain_bits']:+.6f}; positive_folds={row['positive_folds']}/{row['folds']}",
                                    "impact": "Exact host identity does not improve this held unordered-context endpoint."})
    for row in neighbor_summary:
        if row["max3_p"] > .05:
            counterexamples.append({"counterexample_type": "NEIGHBOR_NOT_MAXT_STABLE", "item": row["axis"],
                                    "evidence": f"MRR={row['mean_reciprocal_rank']:.6f}; null={row['null_mean']:.6f}; max3_p={row['max3_p']:.6f}",
                                    "impact": "Nearest-context relation does not satisfy the frozen split-stability gate."})
    variants = [
        {"variant_id": "V00", "status": "PRIMARY", "description": "WINDOW_PM2 weighted opaque contexts."},
        {"variant_id": "V01", "status": "PRIMARY", "description": "WHOLE_LINE weighted opaque contexts."},
        {"variant_id": "V02", "status": "SECONDARY", "description": "Complete-line editorial PARAGRAPH_BAG contexts."},
        {"variant_id": "V03", "status": "RUN_CONTROL", "description": "Remove frozen focal ok to context y contribution."},
        {"variant_id": "V04", "status": "RUN_NEIGHBOR", "description": "WHOLE_LINE top64 by top256 PPMI-cosine neighbors."},
        {"variant_id": "V05", "status": "RUN_NULL", "description": "1024 focal-ID and 1024 neighbor-assignment worlds."},
        {"variant_id": "V06", "status": "FORBIDDEN", "description": "No same-group HPR2 field, glyph/string similarity, semantics, or f84."}
    ]

    def fmt(data):
        return [{k: (f"{v:.12f}" if isinstance(v, float) else v) for k, v in row.items()} for row in data]
    write(INVENTORY, inventory_rows)
    write(FOLDS, fmt(fold_rows))
    write(SCORES, fmt(score_rows))
    write(NEIGHBORS, fmt(reference_neighbors))
    write(NEIGHBOR_STABILITY, fmt(neighbor_rows + neighbor_summary))
    write(NULLS, fmt(null_rows))
    write(NEIGHBOR_NULL, fmt(neighbor_null_rows))
    write(COUNTER, counterexamples)
    write(VARIANTS, variants)

    def report_null(row):
        return (f"{row['null_mean_gain_per_focal']:+.5f} / {row['alignment_excess_per_focal']:+.5f}"
                if row["axis"] == "HELD_FOLIO" else "")

    def report_p(row):
        return f"{row['local_p']:.4f}/{row['max3_p']:.4f}" if row["axis"] == "HELD_FOLIO" else ""

    report = f"""# GDT166 — opaque PAGE_HOST distributional context report

Decision: **{status}**.

## Held unordered-context prediction

| context | split | focal/folds | gain bits | bits/focal | null mean / excess | positive folds | seen | without frozen ok->y | p/max3 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
""" + "".join(f"| `{r['context_mode']}` | `{r['axis']}` | {r['focal_occurrences']}/{r['folds']} | {r['gain_bits']:+.3f} | {r['gain_per_focal']:+.5f} | {report_null(r)} | {r['positive_folds']}/{r['folds']} | {r['source_seen_fraction']:.3f} | {r['gain_without_ok_y_bits']:+.3f} | {report_p(r)} |\n" for r in score_rows) + f"""

Every focal occurrence has total context weight one.  The frozen `ok -> y`
control was neither a feature nor a selection seed; the deletion column removes
only that focal/context mass.

## Whole-line distributional neighbor transfer

| split | predictions/folds | MRR | top1/top5 | null mean / excess | local/max3 p | swappable |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
""" + "".join(f"| `{r['axis']}` | {r['predictions']}/{r['eligible_folds']} | {r['mean_reciprocal_rank']:.4f} | {r['top1']}/{r['top5']} | {r['null_mean']:.4f} / {r['excess_mrr']:+.4f} | {r['local_p']:.4f}/{r['max3_p']:.4f} | {r['swappable_predictions']} |\n" for r in neighbor_summary) + f"""

Neighbor identities are exact opaque categories; PPMI profiles use only
unordered whole-line co-occurrence.  Alternate readings are not replications.

## Interpretation

This test asks whether exact PAGE_HOST identity has stable distributional
context without fixed word order.  It neither rescues GDT165's failed immediate
prediction nor assigns a lexical/code/semantic value.  Paragraph grouping is an
editorial-layout sensitivity and correlated bag members are weighted
descriptive events, not independent samples.

All f84-prefix rows were rejected before retention.  No f84r material was
opened, queried, retained, joined, or scored.
"""
    REPORT.write_text(report, encoding="utf-8")

    result = {"schema": "GDT166_OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_RESULT_V1", "status": status,
              "capacity": {**capacity, "retained_source_groups": len(rows),
                           "physical_folios": len({r['folio'] for r in rows}),
                           "exact_hosts": len(vocabulary),
                           "context_focals": {mode: len(contexts[mode]) for mode in MODES}},
              "scores": {f"{r['context_mode']}:{r['axis']}": r for r in score_rows},
              "null_capacity": null_capacity,
              "passing_context_modes": passing_modes,
              "neighbor": {"focal_panel": len(focal_panel), "context_panel": len(context_panel),
                           "summary": {r["axis"]: r for r in neighbor_summary},
                           "stable_all_splits": neighbor_pass},
              "decision_inputs": {"passing_context_modes": passing_modes,
                                  "neighbor_stable_all_splits": neighbor_pass,
                                  "any_held_folio_positive": folio_positive},
              "special_control": {"identity_pair": "ok->y", "use": "CONTRIBUTION_AND_EXCLUSION_ONLY"},
              "interpretation": "Parser-independent opaque exact-host distributional dependence only; no fixed-order assumption.",
              "claim_ceiling": "No word, lexeme, code value, morpheme, POS, language, semantic role, meaning, plaintext, or translation.",
              "f84r": {"opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
              "inputs": {p.name: sha(p) for p in (SOURCE, FRAMES, DESIGN, ROOT / "gdt165_result.json", ROOT / "gdt165_directed_relations.tsv")},
              "implementation": {Path(__file__).name: sha(Path(__file__))},
              "outputs": {p.name: sha(p) for p in (INVENTORY, SCORES, FOLDS, NEIGHBORS, NEIGHBOR_STABILITY, NULLS, NEIGHBOR_NULL, COUNTER, VARIANTS)},
              "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)}}
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passing_modes": passing_modes,
                      "held_folio_gains": {r['context_mode']: r['gain_bits'] for r in score_rows if r['axis']=='HELD_FOLIO'},
                      "neighbor_mrr": {r['axis']: r['mean_reciprocal_rank'] for r in neighbor_summary}}, sort_keys=True))


if __name__ == "__main__":
    main()
