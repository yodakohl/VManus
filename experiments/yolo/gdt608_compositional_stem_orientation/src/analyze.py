#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


HERE = Path(__file__).resolve().parent.parent
ROOT = find_repo_root(HERE)
G605 = ROOT / "experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts"
G606 = ROOT / "experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts"
OUT = HERE / "artifacts"
ALPHA = 0.5
SEED = 60560620260828
TARGET_PAIRS = {"ol", "or", "ok", "ot", "dy", "aN"}
EXPECTED = {
    G605 / "gdt605_bpe_merges.tsv": "4625c9389ead390907e4ac74e65bc158236f02b439c69cf3b09157f0cd6ca539",
    G605 / "gdt605_unit_inventory.tsv": "ade74733200e941ddc66285988eb1498ac98e87ad374cad11ac412ce42893e82",
    G605 / "gdt605_unit_result.json": "c2d293c121f1ee01fe0ddcbe4647c77f5f94796b4ecc4b1adc554cc2f740c3d9",
    G606 / "guarded_rows.tsv": "d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9",
    G606 / "unit_sequences.json": "3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf",
    G606 / "complete_mappings.tsv": "005ddec8e5b67763c9ccfd1d3244e44c1e68d8c0c6c46a2c7d7edcc36fa4aabe",
    G606 / "category_stability_all_configs_latin.tsv": "2a43d309b78392781ab9111c00dcead82424d648ad820fd02f1479dbb33e7997",
    G606 / "category_stability_all_configs_old_italian.tsv": "069023255a729b0918f7298ca5482f9bfa6fa1815541098f801db7ddc4704169",
    G606 / "category_stability_all_configs_middle_high_german.tsv": "998a6f093584f26321bc4e4ef2f88171ff245383eecb786adde7fe98733e81b5",
}
BINARY = (
    "standalone", "chunk_initial", "chunk_final", "line_initial",
    "line_final", "paragraph_initial", "paragraph_final",
)
PRIMARY_BINARY = (
    "chunk_initial", "chunk_final", "line_initial", "line_final",
    "paragraph_initial", "paragraph_final",
)
PRIMARY = ("left", "right") + PRIMARY_BINARY
CATEGORICAL = ("left", "right", "section", "hand", "currier")
INITIAL_SIDE = {"chunk_initial", "line_initial", "paragraph_initial"}
FINAL_SIDE = {"chunk_final", "line_final", "paragraph_final"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows, fields=None):
    rows = list(rows)
    if fields is None:
        fields = []
        for row in rows:
            for field in row:
                if field not in fields:
                    fields.append(field)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "<NA>") if row.get(field, "") != "" else "<NA>" for field in fields} for row in rows)


def entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    return -sum((value / total) * math.log(value / total) for value in counter.values() if value)


def js_divergence(a: Counter, b: Counter) -> float:
    # Stable accumulation order keeps floating-point artifacts byte-identical
    # across process hash seeds.
    keys = sorted(set(a) | set(b))
    sa, sb = sum(a.values()), sum(b.values())
    if not sa or not sb:
        return 1.0
    value = 0.0
    for key in keys:
        pa, pb = a.get(key, 0) / sa, b.get(key, 0) / sb
        mean = (pa + pb) / 2
        if pa:
            value += 0.5 * pa * math.log2(pa / mean)
        if pb:
            value += 0.5 * pb * math.log2(pb / mean)
    return value


def average_ranks(values):
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][1] == ordered[index][1]:
            end += 1
        rank = (index + 1 + end) / 2
        for cursor in range(index, end):
            ranks[ordered[cursor][0]] = rank
        index = end
    return ranks


def correlation(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) < 2 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x, y):
    return correlation(average_ranks(list(x)), average_ranks(list(y)))


def sigmoid(value):
    if value >= 0:
        return 1 / (1 + math.exp(-value))
    exp = math.exp(value)
    return exp / (1 + exp)


def logit(value):
    value = min(1 - 1e-12, max(1e-12, value))
    return math.log(value / (1 - value))


def paragraph_metadata(guarded):
    metadata = {}
    page_active = {}
    page_counter = Counter()
    paragraph_loci = defaultdict(list)
    for row in guarded:
        page = row["page"]
        raw = row["ivtff_raw"]
        starts = "<%>" in raw[:32]
        ends = "<$>" in raw
        if starts or page not in page_active:
            page_counter[page] += 1
            page_active[page] = f"{page}:p{page_counter[page]}"
        pid = page_active[page]
        paragraph_loci[pid].append(row["locus"])
        metadata[row["locus"]] = {**row, "paragraph_id": pid}
        if ends:
            page_active.pop(page, None)
    for pid, loci in paragraph_loci.items():
        for index, locus in enumerate(loci):
            metadata[locus]["paragraph_line_index"] = index
            metadata[locus]["paragraph_line_count"] = len(loci)
    return metadata


def build_events(sequences, metadata):
    events = []
    for split in ("train", "held"):
        by_locus = defaultdict(list)
        for record in sequences["sequences"][split]:
            by_locus[record["locus"]].append(record)
        for locus, chunks in by_locus.items():
            chunks.sort(key=lambda row: int(row["chunk_index"]))
            meta = metadata[locus]
            line_total = sum(len(row["units"]) for row in chunks)
            line_offset = 0
            for chunk in chunks:
                units = chunk["units"]
                for index, unit in enumerate(units):
                    line_index = line_offset + index
                    events.append({
                        "split": split,
                        "page": chunk["page"],
                        "physical_folio": chunk["physical_folio"],
                        "locus": locus,
                        "section": chunk["section"],
                        "hand": meta["hand"],
                        "currier": meta["language"],
                        "unit": unit,
                        "left": units[index - 1] if index else "<BOS>",
                        "right": units[index + 1] if index + 1 < len(units) else "<EOS>",
                        "standalone": int(len(units) == 1),
                        "chunk_initial": int(index == 0),
                        "chunk_final": int(index == len(units) - 1),
                        "line_initial": int(line_index == 0),
                        "line_final": int(line_index == line_total - 1),
                        "paragraph_initial": int(meta["paragraph_line_index"] == 0 and line_index == 0),
                        "paragraph_final": int(
                            meta["paragraph_line_index"] == meta["paragraph_line_count"] - 1
                            and line_index == line_total - 1
                        ),
                    })
                line_offset += len(units)
    return events


def build_stats(events, inventory):
    stats = {split: {} for split in ("train", "held")}
    for split in stats:
        for unit in inventory:
            stats[split][unit] = {
                "n": 0,
                "binary": {field: 0 for field in BINARY},
                "categorical": {field: Counter() for field in CATEGORICAL},
                "folios": Counter(),
            }
    global_train = {
        "n": 0,
        "binary": {field: 0 for field in BINARY},
        "categorical": {field: Counter() for field in CATEGORICAL},
        "folios": Counter(),
    }
    for event in events:
        cell = stats[event["split"]][event["unit"]]
        cell["n"] += 1
        for field in BINARY:
            cell["binary"][field] += event[field]
        for field in CATEGORICAL:
            cell["categorical"][field][event[field]] += 1
        cell["folios"][event["physical_folio"]] += 1
        if event["split"] == "train":
            global_train["n"] += 1
            for field in BINARY:
                global_train["binary"][field] += event[field]
            for field in CATEGORICAL:
                global_train["categorical"][field][event[field]] += 1
            global_train["folios"][event["physical_folio"]] += 1
    return stats, global_train


def subset_cell(events):
    cell = {
        "n": 0,
        "binary": {field: 0 for field in BINARY},
        "categorical": {field: Counter() for field in CATEGORICAL},
        "folios": Counter(),
    }
    for event in events:
        cell["n"] += 1
        for field in BINARY:
            cell["binary"][field] += event[field]
        for field in CATEGORICAL:
            cell["categorical"][field][event[field]] += 1
        cell["folios"][event["physical_folio"]] += 1
    return cell


def binary_probability(cell, field):
    return (cell["binary"][field] + ALPHA) / (cell["n"] + 2 * ALPHA)


def categorical_probability(cell, field, vocab):
    denom = cell["n"] + ALPHA * len(vocab)
    return {value: (cell["categorical"][field].get(value, 0) + ALPHA) / denom for value in vocab}


def normalize_geometric(a, b):
    values = {key: math.sqrt(a[key] * b[key]) for key in a}
    total = sum(values.values())
    return {key: value / total for key, value in values.items()}


def binary_cross_entropy(cell, field, probability):
    yes, total = cell["binary"][field], cell["n"]
    no = total - yes
    probability = min(1 - 1e-15, max(1e-15, probability))
    return -(yes * math.log2(probability) + no * math.log2(1 - probability)) / total


def categorical_cross_entropy(cell, field, probability, vocab):
    total = cell["n"]
    unknown = set(cell["categorical"][field]) - set(vocab)
    counts = Counter(cell["categorical"][field])
    if unknown:
        counts["<UNK>"] += sum(counts.pop(value) for value in unknown)
    return -sum(count * math.log2(max(1e-300, probability[value])) for value, count in counts.items()) / total


def model_prediction(model, merged, left, right, stats, global_train, vocab):
    if model == "SWAPPED":
        left, right = right, left
        model = "DIRECT"
    prediction = {"binary": {}, "categorical": {}}
    if model == "GLOBAL":
        for field in BINARY:
            prediction["binary"][field] = binary_probability(global_train, field)
        for field in CATEGORICAL:
            prediction["categorical"][field] = categorical_probability(global_train, field, vocab[field])
        return prediction
    if model == "ATOMIC":
        cell = stats["train"][merged]
        for field in BINARY:
            prediction["binary"][field] = binary_probability(cell, field)
        for field in CATEGORICAL:
            prediction["categorical"][field] = categorical_probability(cell, field, vocab[field])
        return prediction
    if model != "DIRECT":
        raise ValueError(model)
    left_cell, right_cell = stats["train"][left], stats["train"][right]
    for field in BINARY:
        lp = binary_probability(left_cell, field)
        rp = binary_probability(right_cell, field)
        if field in INITIAL_SIDE:
            prediction["binary"][field] = lp
        elif field in FINAL_SIDE:
            prediction["binary"][field] = rp
        else:
            prediction["binary"][field] = math.sqrt(lp * rp)
    for field in CATEGORICAL:
        lp = categorical_probability(left_cell, field, vocab[field])
        rp = categorical_probability(right_cell, field, vocab[field])
        if field == "left":
            prediction["categorical"][field] = lp
        elif field == "right":
            prediction["categorical"][field] = rp
        else:
            prediction["categorical"][field] = normalize_geometric(lp, rp)
    return prediction


def score_prediction(prediction, held_cell, vocab):
    scores = {}
    for field in BINARY:
        scores[field] = binary_cross_entropy(held_cell, field, prediction["binary"][field])
    for field in CATEGORICAL:
        scores[field] = categorical_cross_entropy(held_cell, field, prediction["categorical"][field], vocab[field])
    scores["primary_joint"] = statistics.fmean(scores[field] for field in PRIMARY)
    scores["metadata_joint"] = statistics.fmean(scores[field] for field in ("section", "hand", "currier"))
    scores["all_joint"] = statistics.fmean(scores[field] for field in BINARY + CATEGORICAL)
    return scores


def effective_folio_fraction(cell, folio_count):
    return math.exp(entropy(cell["folios"])) / folio_count if cell["folios"] else 0.0


def ridge_fit(raw_x, y, lam=1.0):
    raw_x = np.asarray(raw_x, dtype=float)
    y = np.asarray(y, dtype=float)
    mean = raw_x.mean(axis=0)
    scale = raw_x.std(axis=0)
    scale[scale == 0] = 1
    standardized = (raw_x - mean) / scale
    x = np.column_stack((np.ones(len(raw_x)), standardized))
    penalty = np.eye(x.shape[1]) * lam
    penalty[0, 0] = 0
    beta = np.linalg.solve(x.T @ x + penalty, x.T @ y)
    return beta, mean, scale


def ridge_predict(raw_x, fitted):
    beta, mean, scale = fitted
    vector = np.concatenate(([1.0], (np.asarray(raw_x) - mean) / scale))
    return float(vector @ beta)


def lomo_analysis(merges, stats):
    output = []
    coefficient_rows = []
    predictors = {}
    responses = {}
    for field in BINARY:
        raw_x, y = [], []
        for merge in merges:
            left, right, merged = merge["left"], merge["right"], merge["merged"]
            values = [
                logit(binary_probability(stats["train"][left], field)),
                logit(binary_probability(stats["train"][right], field)),
                math.log(stats["train"][left]["n"]),
                math.log(stats["train"][right]["n"]),
                math.log(stats["train"][merged]["n"]),
            ]
            raw_x.append(values)
            y.append(logit(binary_probability(stats["train"][merged], field)))
        predictors[field], responses[field] = raw_x, y
        full_fit = ridge_fit(raw_x, y)
        for name, value in zip(
            ("intercept", "left_rate_logit", "right_rate_logit", "left_log_frequency", "right_log_frequency", "merged_log_frequency"),
            full_fit[0],
        ):
            coefficient_rows.append({"metric": field, "coefficient": name, "standardized_value": value})

    for index, merge in enumerate(merges):
        for field in BINARY:
            train_indices = [i for i in range(len(merges)) if i != index]
            fitted = ridge_fit([predictors[field][i] for i in train_indices], [responses[field][i] for i in train_indices])
            prediction = sigmoid(ridge_predict(predictors[field][index], fitted))
            merged = merge["merged"]
            held_cell = stats["held"][merged]
            held_rate = held_cell["binary"][field] / held_cell["n"]
            atomic = binary_probability(stats["train"][merged], field)
            left = binary_probability(stats["train"][merge["left"]], field)
            right = binary_probability(stats["train"][merge["right"]], field)
            direct = left if field in INITIAL_SIDE else right if field in FINAL_SIDE else math.sqrt(left * right)
            output.append({
                "rank": merge["rank"], "left": merge["left"], "right": merge["right"],
                "merged": merged, "metric": field, "train_n": stats["train"][merged]["n"],
                "held_n": held_cell["n"], "held_rate": held_rate,
                "atomic_prediction": atomic, "direct_prediction": direct,
                "lomo_prediction": prediction,
                "atomic_abs_error": abs(held_rate - atomic),
                "direct_abs_error": abs(held_rate - direct),
                "lomo_abs_error": abs(held_rate - prediction),
                "atomic_logloss": binary_cross_entropy(held_cell, field, atomic),
                "direct_logloss": binary_cross_entropy(held_cell, field, direct),
                "lomo_logloss": binary_cross_entropy(held_cell, field, prediction),
            })
    return output, coefficient_rows


def signflip_p(values, rng, reps=10000):
    observed = abs(statistics.fmean(values))
    exceed = 0
    for _ in range(reps):
        candidate = abs(statistics.fmean(value * (-1 if rng.random() < 0.5 else 1) for value in values))
        exceed += candidate >= observed
    return (exceed + 1) / (reps + 1)


def residual_correlation(x, y, control):
    design = np.column_stack((np.ones(len(control)), np.asarray(control, dtype=float)))
    rx = np.asarray(x, dtype=float) - design @ np.linalg.lstsq(design, np.asarray(x, dtype=float), rcond=None)[0]
    ry = np.asarray(y, dtype=float) - design @ np.linalg.lstsq(design, np.asarray(y, dtype=float), rcond=None)[0]
    return correlation(rx, ry)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    observed = {str(path.relative_to(ROOT)): sha(path) for path in EXPECTED}
    expected_relative = {str(path.relative_to(ROOT)): value for path, value in EXPECTED.items()}
    if observed != expected_relative:
        raise RuntimeError(f"input drift: {observed}")

    merge_rows = read_tsv(G605 / "gdt605_bpe_merges.tsv")
    merges = [{**row, "rank": int(row["rank"]), "train_occurrences": int(row["train_occurrences"])} for row in merge_rows]
    if len(merges) != 64 or len({row["merged"] for row in merges}) != 64:
        raise RuntimeError("merge inventory mismatch")
    guarded = read_tsv(G606 / "guarded_rows.tsv")
    if any(row["page"].lower().startswith("f84") for row in guarded):
        raise RuntimeError("forbidden selector")
    sequences = json.loads((G606 / "unit_sequences.json").read_text())
    inventory = sequences["inventory"]
    metadata = paragraph_metadata(guarded)
    events = build_events(sequences, metadata)
    stats, global_train = build_stats(events, inventory)

    vocab = {
        "left": sorted(set(inventory) | {"<BOS>", "<EOS>"}),
        "right": sorted(set(inventory) | {"<BOS>", "<EOS>"}),
        "section": sorted(global_train["categorical"]["section"]) + ["<UNK>"],
        "hand": sorted(global_train["categorical"]["hand"]) + ["<UNK>"],
        "currier": sorted(global_train["categorical"]["currier"]) + ["<UNK>"],
    }

    # Recursive merge tree, respecting only the registered direct rules.
    rule_by_output = {row["merged"]: (row["left"], row["right"]) for row in merges}
    def leaves(unit):
        if unit not in rule_by_output:
            return [unit]
        left, right = rule_by_output[unit]
        return leaves(left) + leaves(right)
    def depth(unit):
        if unit not in rule_by_output:
            return 0
        left, right = rule_by_output[unit]
        return 1 + max(depth(left), depth(right))
    tree_rows = [{
        **row, "leaf_sequence": " ".join(leaves(row["merged"])),
        "leaf_count": len(leaves(row["merged"])), "tree_depth": depth(row["merged"]),
    } for row in merges]

    predictions = {}
    scores = defaultdict(dict)
    feature_rows = []
    for merge in merges:
        merged, left, right = merge["merged"], merge["left"], merge["right"]
        for model in ("GLOBAL", "ATOMIC", "DIRECT", "SWAPPED"):
            prediction = model_prediction(model, merged, left, right, stats, global_train, vocab)
            predictions[merged, model] = prediction
            result = score_prediction(prediction, stats["held"][merged], vocab)
            scores[merged][model] = result
            for feature, value in result.items():
                feature_rows.append({
                    "rank": merge["rank"], "left": left, "right": right, "merged": merged,
                    "held_n": stats["held"][merged]["n"], "model": model,
                    "feature": feature, "held_bits_per_event": value,
                })

    # Frequency/mobility matched donor pairs, defined entirely from train.
    train_folios = len({event["physical_folio"] for event in events if event["split"] == "train"})
    descriptors = []
    for merge in merges:
        cell = stats["train"][merge["merged"]]
        descriptors.append((math.log(cell["n"]), effective_folio_fraction(cell, train_folios)))
    descriptor_array = np.asarray(descriptors)
    descriptor_mean = descriptor_array.mean(axis=0)
    descriptor_sd = descriptor_array.std(axis=0)
    descriptor_sd[descriptor_sd == 0] = 1
    descriptor_z = (descriptor_array - descriptor_mean) / descriptor_sd
    nearest = {}
    for i, merge in enumerate(merges):
        ranked = sorted(
            (float(np.linalg.norm(descriptor_z[i] - descriptor_z[j])), j)
            for j in range(len(merges)) if j != i
        )
        nearest[merge["merged"]] = [index for _distance, index in ranked[:8]]

    donor_scores = defaultdict(dict)
    donor_side_scores = {"left": defaultdict(dict), "right": defaultdict(dict)}
    left_fields = ("left", "chunk_initial", "line_initial", "paragraph_initial")
    right_fields = ("right", "chunk_final", "line_final", "paragraph_final")
    for target in merges:
        merged = target["merged"]
        held_cell = stats["held"][merged]
        for donor in merges:
            prediction = model_prediction("DIRECT", merged, donor["left"], donor["right"], stats, global_train, vocab)
            result = score_prediction(prediction, held_cell, vocab)
            donor_scores[merged][donor["merged"]] = result["primary_joint"]
            donor_side_scores["left"][merged][donor["merged"]] = statistics.fmean(result[field] for field in left_fields)
            donor_side_scores["right"][merged][donor["merged"]] = statistics.fmean(result[field] for field in right_fields)

    rng = random.Random(SEED)
    total_held = sum(stats["held"][row["merged"]]["n"] for row in merges)
    real_direct = sum(stats["held"][row["merged"]]["n"] * scores[row["merged"]]["DIRECT"]["primary_joint"] for row in merges) / total_held
    mobile_null = []
    donor_draws = []
    for replicate in range(1000):
        weighted = 0.0
        draw_record = []
        for merge in merges:
            donor_index = rng.choice(nearest[merge["merged"]])
            donor = merges[donor_index]["merged"]
            draw_record.append(donor)
            weighted += stats["held"][merge["merged"]]["n"] * donor_scores[merge["merged"]][donor]
        score = weighted / total_held
        mobile_null.append(score)
        donor_draws.append(draw_record)
    mobile_p = (1 + sum(value <= real_direct for value in mobile_null)) / 1001
    null_rows = [{"replicate": i, "primary_joint_bits": value} for i, value in enumerate(mobile_null, 1)]

    merge_score_rows = []
    for merge in merges:
        merged = merge["merged"]
        local_null = [donor_scores[merged][merges[index]["merged"]] for index in nearest[merged]]
        held_cell = stats["held"][merged]
        row = {
            "rank": merge["rank"], "left": merge["left"], "right": merge["right"], "merged": merged,
            "train_n": stats["train"][merged]["n"], "held_n": held_cell["n"],
            "train_folio_effective_fraction": effective_folio_fraction(stats["train"][merged], train_folios),
            "global_primary_bits": scores[merged]["GLOBAL"]["primary_joint"],
            "atomic_primary_bits": scores[merged]["ATOMIC"]["primary_joint"],
            "direct_primary_bits": scores[merged]["DIRECT"]["primary_joint"],
            "swapped_primary_bits": scores[merged]["SWAPPED"]["primary_joint"],
            "direct_gain_vs_global_bits": scores[merged]["GLOBAL"]["primary_joint"] - scores[merged]["DIRECT"]["primary_joint"],
            "direction_gain_vs_swapped_bits": scores[merged]["SWAPPED"]["primary_joint"] - scores[merged]["DIRECT"]["primary_joint"],
            "atomic_gain_vs_direct_bits": scores[merged]["DIRECT"]["primary_joint"] - scores[merged]["ATOMIC"]["primary_joint"],
            "matched_mobile_mean_bits": statistics.fmean(local_null),
            "direct_gain_vs_matched_mobile_bits": statistics.fmean(local_null) - scores[merged]["DIRECT"]["primary_joint"],
            "local_mobile_p_le": (1 + sum(value <= scores[merged]["DIRECT"]["primary_joint"] for value in local_null)) / 9,
        }
        for field in BINARY:
            row[f"train_{field}_rate"] = stats["train"][merged]["binary"][field] / stats["train"][merged]["n"]
            row[f"held_{field}_rate"] = held_cell["binary"][field] / held_cell["n"]
            row[f"direct_{field}_prediction"] = predictions[merged, "DIRECT"]["binary"][field]
        merge_score_rows.append(row)

    # LOMO train-only composition regression.
    lomo_rows, coefficient_rows = lomo_analysis(merges, stats)
    lomo_primary = [row for row in lomo_rows if row["metric"] in PRIMARY_BINARY]
    lomo_weight = sum(row["held_n"] for row in lomo_primary)
    lomo_summary = {
        name: sum(row["held_n"] * row[f"{name}_logloss"] for row in lomo_primary) / lomo_weight
        for name in ("atomic", "direct", "lomo")
    }
    lomo_mae = {
        name: statistics.fmean(row[f"{name}_abs_error"] for row in lomo_rows)
        for name in ("atomic", "direct", "lomo")
    }

    # Matched-frequency atomic stability controls.
    outputs = {row["merged"] for row in merges}
    nonoutputs = [unit for unit in inventory if unit not in outputs and stats["held"][unit]["n"]]
    def drift(unit):
        edge_mae = statistics.fmean(
            abs(stats["train"][unit]["binary"][field] / stats["train"][unit]["n"] -
                stats["held"][unit]["binary"][field] / stats["held"][unit]["n"])
            for field in BINARY
        )
        neighbor_js = statistics.fmean(
            js_divergence(stats["train"][unit]["categorical"][field], stats["held"][unit]["categorical"][field])
            for field in ("left", "right")
        )
        return edge_mae, neighbor_js
    control_rows = []
    for merge in merges:
        unit = merge["merged"]
        control = min(nonoutputs, key=lambda value: (abs(math.log(stats["train"][unit]["n"]) - math.log(stats["train"][value]["n"])), value))
        merge_drift, merge_js = drift(unit)
        control_drift, control_js = drift(control)
        control_rows.append({
            "rank": merge["rank"], "merged": unit, "merge_train_n": stats["train"][unit]["n"],
            "merge_held_n": stats["held"][unit]["n"], "control": control,
            "control_train_n": stats["train"][control]["n"], "control_held_n": stats["held"][control]["n"],
            "merge_edge_rate_mae": merge_drift, "control_edge_rate_mae": control_drift,
            "merge_minus_control_edge_mae": merge_drift - control_drift,
            "merge_neighbor_js": merge_js, "control_neighbor_js": control_js,
            "merge_minus_control_neighbor_js": merge_js - control_js,
        })
    control_edge_diffs = [row["merge_minus_control_edge_mae"] for row in control_rows]
    control_js_diffs = [row["merge_minus_control_neighbor_js"] for row in control_rows]
    control_summary = {
        "merge_edge_mae_mean": statistics.fmean(row["merge_edge_rate_mae"] for row in control_rows),
        "control_edge_mae_mean": statistics.fmean(row["control_edge_rate_mae"] for row in control_rows),
        "edge_difference_signflip_p": signflip_p(control_edge_diffs, random.Random(SEED + 1)),
        "merge_neighbor_js_mean": statistics.fmean(row["merge_neighbor_js"] for row in control_rows),
        "control_neighbor_js_mean": statistics.fmean(row["control_neighbor_js"] for row in control_rows),
        "neighbor_difference_signflip_p": signflip_p(control_js_diffs, random.Random(SEED + 2)),
    }

    # Repeated direct stem-side families.
    left_groups = defaultdict(list)
    right_groups = defaultdict(list)
    for merge in merges:
        left_groups[merge["left"]].append(merge)
        right_groups[merge["right"]].append(merge)
    family_rows = []
    family_child_rows = []
    for side, groups, fields in (("left", left_groups, left_fields), ("right", right_groups, right_fields)):
        for stem, children in sorted(groups.items()):
            if len(children) < 3:
                continue
            child_n = sum(stats["held"][child["merged"]]["n"] for child in children)
            direct_score = sum(
                stats["held"][child["merged"]]["n"] * statistics.fmean(scores[child["merged"]]["DIRECT"][field] for field in fields)
                for child in children
            ) / child_n
            swapped_score = sum(
                stats["held"][child["merged"]]["n"] * statistics.fmean(scores[child["merged"]]["SWAPPED"][field] for field in fields)
                for child in children
            ) / child_n
            child_gains = []
            for child in children:
                merged = child["merged"]
                gain = statistics.fmean(scores[merged]["SWAPPED"][field] - scores[merged]["DIRECT"][field] for field in fields)
                child_gains.append(gain)
                family_child_rows.append({
                    "side": side, "stem": stem, "child": merged, "other_component": child["right"] if side == "left" else child["left"],
                    "held_n": stats["held"][merged]["n"], "direction_gain_vs_swapped_bits": gain,
                })
            null_values = []
            child_indices = {child["merged"]: merges.index(child) for child in children}
            for replicate in range(1000):
                weighted = 0.0
                for child in children:
                    merged = child["merged"]
                    donor = donor_draws[replicate][child_indices[merged]]
                    weighted += stats["held"][merged]["n"] * donor_side_scores[side][merged][donor]
                null_values.append(weighted / child_n)
            p_value = (1 + sum(value <= direct_score for value in null_values)) / 1001
            held_initial_or_final = {}
            side_metrics = ("chunk_initial", "line_initial", "paragraph_initial") if side == "left" else ("chunk_final", "line_final", "paragraph_final")
            for metric in side_metrics:
                held_initial_or_final[metric] = sum(
                    stats["held"][child["merged"]]["binary"][metric] for child in children
                ) / child_n
            family_rows.append({
                "side": side, "stem": stem, "children": len(children),
                "child_outputs": ";".join(child["merged"] for child in children), "held_events": child_n,
                "direct_side_bits": direct_score, "swapped_side_bits": swapped_score,
                "direction_gain_vs_swapped_bits": swapped_score - direct_score,
                "children_positive_direction": sum(value > 0 for value in child_gains),
                "children_positive_fraction": sum(value > 0 for value in child_gains) / len(child_gains),
                "mobile_null_mean_bits": statistics.fmean(null_values),
                "direct_gain_vs_mobile_bits": statistics.fmean(null_values) - direct_score,
                "mobile_empirical_p_le": p_value,
                "stable_stem_side_role": int(
                    swapped_score > direct_score
                    and sum(value > 0 for value in child_gains) / len(child_gains) >= 0.75
                    and p_value <= 0.05
                ),
                **{f"held_weighted_{metric}_rate": value for metric, value in held_initial_or_final.items()},
            })

    # Existing GDT606 real/destroyed W diagnostic, never exact outputs.
    mappings = read_tsv(G606 / "complete_mappings.tsv")
    real_categories = defaultdict(list)
    destroyed_categories = defaultdict(list)
    for row in mappings:
        target = real_categories if row["model_kind"] == "real" else destroyed_categories
        target[row["unit"]].append(row["category"])
    score_by_output = {row["merged"]: row for row in merge_score_rows}
    w_rows = []
    for merge in merges:
        unit = merge["merged"]
        real_w = sum(value == "W" for value in real_categories[unit]) / len(real_categories[unit])
        destroyed_w = sum(value == "W" for value in destroyed_categories[unit]) / len(destroyed_categories[unit])
        score = score_by_output[unit]
        w_rows.append({
            "merged": unit, "train_n": stats["train"][unit]["n"],
            "real_W_fraction_36": real_w, "destroyed_W_fraction_12": destroyed_w,
            "direct_gain_vs_global_bits": score["direct_gain_vs_global_bits"],
            "direct_gain_vs_mobile_bits": score["direct_gain_vs_matched_mobile_bits"],
            "direction_gain_vs_swapped_bits": score["direction_gain_vs_swapped_bits"],
        })
    log_frequency = [math.log(row["train_n"]) for row in w_rows]
    composition_gain = [row["direct_gain_vs_mobile_bits"] for row in w_rows]
    real_w_values = [row["real_W_fraction_36"] for row in w_rows]
    destroyed_w_values = [row["destroyed_W_fraction_12"] for row in w_rows]
    w_summary = {
        "composition_gain_vs_real_W_spearman": spearman(composition_gain, real_w_values),
        "composition_gain_vs_destroyed_W_spearman": spearman(composition_gain, destroyed_w_values),
        "frequency_vs_real_W_spearman": spearman(log_frequency, real_w_values),
        "composition_gain_vs_real_W_residual_pearson_controlling_log_frequency": residual_correlation(composition_gain, real_w_values, log_frequency),
        "composition_gain_vs_destroyed_W_residual_pearson_controlling_log_frequency": residual_correlation(composition_gain, destroyed_w_values, log_frequency),
    }

    # Profiles and nominated pair output.
    profile_rows = []
    for split in ("train", "held"):
        folio_count = len({event["physical_folio"] for event in events if event["split"] == split})
        for unit in inventory:
            cell = stats[split][unit]
            if not cell["n"]:
                continue
            profile_rows.append({
                "split": split, "unit": unit, "occurrences": cell["n"],
                **{f"{field}_rate": cell["binary"][field] / cell["n"] for field in BINARY},
                "left_neighbor_entropy_nats": entropy(cell["categorical"]["left"]),
                "right_neighbor_entropy_nats": entropy(cell["categorical"]["right"]),
                "effective_folio_fraction": effective_folio_fraction(cell, folio_count),
                "distinct_folios": len(cell["folios"]),
            })
    nominated_rows = [row for row in merge_score_rows if row["merged"] in TARGET_PAIRS]

    aggregate_model_scores = {}
    for model in ("GLOBAL", "ATOMIC", "DIRECT", "SWAPPED"):
        aggregate_model_scores[model] = {
            field: sum(stats["held"][row["merged"]]["n"] * scores[row["merged"]][model][field] for row in merges) / total_held
            for field in list(BINARY) + list(CATEGORICAL) + ["primary_joint", "metadata_joint", "all_joint"]
        }

    # Physical-folio stability of the frozen train predictions.
    merge_outputs = {row["merged"] for row in merges}
    held_by_folio_unit = defaultdict(list)
    for event in events:
        if event["split"] == "held" and event["unit"] in merge_outputs:
            held_by_folio_unit[event["physical_folio"], event["unit"]].append(event)
    held_folios = sorted({folio for folio, _unit in held_by_folio_unit})
    folio_model_rows = []
    for folio in held_folios:
        cells = {
            unit: subset_cell(held_by_folio_unit.get((folio, unit), []))
            for unit in sorted(merge_outputs)
        }
        folio_n = sum(cell["n"] for cell in cells.values())
        model_values = {}
        for model in ("GLOBAL", "ATOMIC", "DIRECT", "SWAPPED"):
            total = 0.0
            for unit, cell in cells.items():
                if cell["n"]:
                    total += cell["n"] * score_prediction(predictions[unit, model], cell, vocab)["primary_joint"]
            model_values[model] = total / folio_n
        folio_model_rows.append({
            "physical_folio": folio, "merge_output_events": folio_n,
            "global_primary_bits": model_values["GLOBAL"],
            "atomic_primary_bits": model_values["ATOMIC"],
            "direct_primary_bits": model_values["DIRECT"],
            "swapped_primary_bits": model_values["SWAPPED"],
            "direct_gain_vs_global_bits": model_values["GLOBAL"] - model_values["DIRECT"],
            "direction_gain_vs_swapped_bits": model_values["SWAPPED"] - model_values["DIRECT"],
            "atomic_gain_vs_direct_bits": model_values["DIRECT"] - model_values["ATOMIC"],
        })

    # Descriptive tree-depth stratification; this does not alter the frozen decision gate.
    depth_by_output = {row["merged"]: row["tree_depth"] for row in tree_rows}
    depth_rows = []
    for tree_depth in sorted(set(depth_by_output.values())):
        subset = [row for row in merge_score_rows if depth_by_output[row["merged"]] == tree_depth]
        weight = sum(row["held_n"] for row in subset)
        depth_rows.append({
            "tree_depth": tree_depth, "merge_types": len(subset), "held_events": weight,
            "weighted_direct_gain_vs_global_bits": sum(row["held_n"] * row["direct_gain_vs_global_bits"] for row in subset) / weight,
            "weighted_direction_gain_vs_swapped_bits": sum(row["held_n"] * row["direction_gain_vs_swapped_bits"] for row in subset) / weight,
            "weighted_atomic_gain_vs_direct_bits": sum(row["held_n"] * row["atomic_gain_vs_direct_bits"] for row in subset) / weight,
            "direct_beats_atomic_types": sum(row["atomic_gain_vs_direct_bits"] < 0 for row in subset),
        })
    atomic_gap = aggregate_model_scores["DIRECT"]["primary_joint"] - aggregate_model_scores["ATOMIC"]["primary_joint"]
    decision = (
        "STRONG_COMPOSITIONAL_CODE" if
        aggregate_model_scores["DIRECT"]["primary_joint"] < aggregate_model_scores["GLOBAL"]["primary_joint"]
        and aggregate_model_scores["DIRECT"]["primary_joint"] < aggregate_model_scores["SWAPPED"]["primary_joint"]
        and mobile_p <= 0.05 and atomic_gap <= 0.02
        else "PARTIAL_COMPOSITIONAL_BACKOFF" if
        aggregate_model_scores["DIRECT"]["primary_joint"] < aggregate_model_scores["GLOBAL"]["primary_joint"]
        and mobile_p <= 0.05 and atomic_gap > 0.02
        else "ATOMIC_OR_RESIDUAL_CODE"
    )
    result = {
        "schema": "gdt608-compositional-stem-orientation-v1",
        "decision": decision,
        "claim_ceiling": "collapsed-unit structural composition only; no morphology, lexeme, sound, language, plaintext, or meaning",
        "sealed_data": {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"},
        "input_hashes": observed,
        "counts": {
            "guarded_rows": len(guarded), "merge_rules": len(merges), "inventory": len(inventory),
            "train_events": sum(cell["n"] for cell in stats["train"].values()),
            "held_events": sum(cell["n"] for cell in stats["held"].values()),
            "merge_output_train_events": sum(stats["train"][row["merged"]]["n"] for row in merges),
            "merge_output_held_events": total_held,
            "stem_side_families": len(family_rows),
            "stable_stem_side_families": sum(row["stable_stem_side_role"] for row in family_rows),
        },
        "aggregate_model_scores": aggregate_model_scores,
        "direct_minus_atomic_primary_bits": atomic_gap,
        "mobile_null": {
            "replicates": 1000, "seed": SEED, "nearest_donors": 8,
            "real_direct_primary_bits": real_direct,
            "mean_primary_bits": statistics.fmean(mobile_null),
            "sd_primary_bits": statistics.stdev(mobile_null),
            "minimum_primary_bits": min(mobile_null), "maximum_primary_bits": max(mobile_null),
            "empirical_p_null_le_real": mobile_p,
        },
        "lomo_binary_edge_logloss": lomo_summary,
        "lomo_all_seven_rate_mae": lomo_mae,
        "matched_frequency_control": control_summary,
        "w_category_diagnostic": w_summary,
        "held_folio_stability": {
            "folios": len(folio_model_rows),
            "direct_beats_global": sum(row["direct_gain_vs_global_bits"] > 0 for row in folio_model_rows),
            "direct_beats_swapped": sum(row["direction_gain_vs_swapped_bits"] > 0 for row in folio_model_rows),
            "atomic_beats_direct": sum(row["atomic_gain_vs_direct_bits"] > 0 for row in folio_model_rows),
            "minimum_direct_gain_vs_global_bits": min(row["direct_gain_vs_global_bits"] for row in folio_model_rows),
            "maximum_direct_gain_vs_global_bits": max(row["direct_gain_vs_global_bits"] for row in folio_model_rows),
        },
        "tree_depth_diagnostic": depth_rows,
        "known_held_exposure": "exploratory: prior GDT606 role attack exposed some requested-unit held profiles before this freeze",
    }

    write_tsv(OUT / "merge_tree.tsv", tree_rows)
    write_tsv(OUT / "unit_profiles.tsv", profile_rows)
    write_tsv(OUT / "model_feature_scores.tsv", feature_rows)
    write_tsv(OUT / "merge_composition_scores.tsv", merge_score_rows)
    write_tsv(OUT / "nominated_pairs.tsv", nominated_rows)
    write_tsv(OUT / "lomo_predictions.tsv", lomo_rows)
    write_tsv(OUT / "lomo_coefficients.tsv", coefficient_rows)
    write_tsv(OUT / "matched_frequency_controls.tsv", control_rows)
    write_tsv(OUT / "stem_family_roles.tsv", family_rows)
    write_tsv(OUT / "stem_family_children.tsv", family_child_rows)
    write_tsv(OUT / "w_composition_diagnostic.tsv", w_rows)
    write_tsv(OUT / "mobile_null_scores.tsv", null_rows)
    write_tsv(OUT / "held_folio_model_scores.tsv", folio_model_rows)
    write_tsv(OUT / "tree_depth_summary.tsv", depth_rows)
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    generated = (
        "merge_tree.tsv", "unit_profiles.tsv", "model_feature_scores.tsv",
        "merge_composition_scores.tsv", "nominated_pairs.tsv", "lomo_predictions.tsv",
        "lomo_coefficients.tsv", "matched_frequency_controls.tsv", "stem_family_roles.tsv",
        "stem_family_children.tsv", "w_composition_diagnostic.tsv", "mobile_null_scores.tsv",
        "held_folio_model_scores.tsv", "tree_depth_summary.tsv",
        "RESULT.json",
    )
    manifest = {
        "schema": "gdt608-composition-artifact-manifest-v1",
        "analysis_source_sha256": sha(Path(__file__)),
        "inputs": observed,
        "outputs": {name: sha(OUT / name) for name in generated},
    }
    (OUT / "ARTIFACT_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "decision": decision, "result": result,
        "manifest_sha256": sha(OUT / "ARTIFACT_MANIFEST.json"),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
