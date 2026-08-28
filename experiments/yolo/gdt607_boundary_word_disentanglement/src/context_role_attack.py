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
SOURCE = ROOT / "experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts"
OUT = HERE / "artifacts/role_attack"
TARGETS = ("ol", "y", "C", "d", "o")
LANGUAGES = ("latin", "old_italian", "middle_high_german")
EXPECTED = {
    "guarded_rows.tsv": "d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9",
    "unit_sequences.json": "3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf",
    "complete_mappings.tsv": "005ddec8e5b67763c9ccfd1d3244e44c1e68d8c0c6c46a2c7d7edcc36fa4aabe",
    "category_stability_all_configs_latin.tsv": "2a43d309b78392781ab9111c00dcead82424d648ad820fd02f1479dbb33e7997",
    "category_stability_all_configs_old_italian.tsv": "069023255a729b0918f7298ca5482f9bfa6fa1815541098f801db7ddc4704169",
    "category_stability_all_configs_middle_high_german.tsv": "998a6f093584f26321bc4e4ef2f88171ff245383eecb786adde7fe98733e81b5",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows, fields=None):
    rows = list(rows)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def entropy(counter: Counter) -> float:
    n = sum(counter.values())
    if not n:
        return 0.0
    return -sum((v / n) * math.log(v / n) for v in counter.values() if v)


def effective_fraction(counter: Counter) -> float:
    return math.exp(entropy(counter)) / len(counter) if counter else 0.0


def gini(values) -> float:
    values = sorted(float(x) for x in values)
    n = len(values)
    total = sum(values)
    if not n or total == 0:
        return 0.0
    return sum((2 * i - n - 1) * value for i, value in enumerate(values, 1)) / (n * total)


def js_divergence(a: Counter, b: Counter) -> float:
    # A sorted accumulation order is required for byte-identical floating-point
    # summaries across processes with different hash randomization.
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


def sorensen_counter(a: Counter, b: Counter) -> float:
    denom = sum(a.values()) + sum(b.values())
    return 2 * sum(min(a[k], b[k]) for k in set(a) | set(b)) / denom if denom else 0.0


def odds_ratio(a_yes, a_no, b_yes, b_no):
    return ((a_yes + 0.5) * (b_no + 0.5)) / ((a_no + 0.5) * (b_yes + 0.5))


def average_ranks(values):
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        rank = (i + 1 + j) / 2
        for k in range(i, j):
            ranks[indexed[k][0]] = rank
        i = j
    return ranks


def correlation(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) < 2 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x, y):
    return correlation(average_ranks(list(x)), average_ranks(list(y)))


def chi_square(rows, row_key, col_key):
    rvals = sorted({r[row_key] for r in rows})
    cvals = sorted({r[col_key] for r in rows})
    matrix = np.zeros((len(rvals), len(cvals)), dtype=float)
    ri, ci = {v: i for i, v in enumerate(rvals)}, {v: i for i, v in enumerate(cvals)}
    for row in rows:
        matrix[ri[row[row_key]], ci[row[col_key]]] += 1
    total = matrix.sum()
    expected = matrix.sum(1)[:, None] * matrix.sum(0)[None, :] / total
    statistic = float(np.sum(np.where(expected > 0, (matrix - expected) ** 2 / expected, 0)))
    denom = total * max(1, min(len(rvals) - 1, len(cvals) - 1))
    return statistic, math.sqrt(statistic / denom), matrix, rvals, cvals


def category(value, boundaries):
    for label, maximum in boundaries:
        if value <= maximum:
            return label
    return boundaries[-1][0]


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
        metadata[row["locus"]] = {
            **row,
            "paragraph_id": pid,
            "paragraph_marker_start": starts,
            "paragraph_marker_end": ends,
        }
        if ends:
            page_active.pop(page, None)
    for pid, loci in paragraph_loci.items():
        for index, locus in enumerate(loci):
            metadata[locus]["paragraph_line_index"] = index
            metadata[locus]["paragraph_line_count"] = len(loci)
            metadata[locus]["paragraph_line_pos"] = (
                "single" if len(loci) == 1 else
                "start" if index == 0 else
                "end" if index == len(loci) - 1 else "middle"
            )
    return metadata


def build_occurrences(sequences, metadata):
    records = sequences["sequences"]["train"] + sequences["sequences"]["held"]
    split_by_locus = {record["locus"]: split for split in ("train", "held")
                      for record in sequences["sequences"][split]}
    by_locus = defaultdict(list)
    for record in records:
        if record["locus"] not in metadata:
            raise RuntimeError(f"missing guarded locus {record['locus']}")
        by_locus[record["locus"]].append(record)
    occurrences = []
    for locus, chunks in by_locus.items():
        chunks.sort(key=lambda row: int(row["chunk_index"]))
        meta = metadata[locus]
        line_total = sum(len(row["units"]) for row in chunks)
        line_offset = 0
        for chunk_ord, record in enumerate(chunks):
            units = record["units"]
            for unit_index, unit in enumerate(units):
                line_index = line_offset + unit_index
                chunk_len = len(units)
                chunk_pos = (
                    "only" if chunk_len == 1 else
                    "initial" if unit_index == 0 else
                    "final" if unit_index == chunk_len - 1 else "interior"
                )
                line_chunk_pos = (
                    "only" if len(chunks) == 1 else
                    "initial" if chunk_ord == 0 else
                    "final" if chunk_ord == len(chunks) - 1 else "interior"
                )
                line_edge = (
                    "only" if line_total == 1 else
                    "initial" if line_index == 0 else
                    "final" if line_index == line_total - 1 else "interior"
                )
                masked = tuple("*" if i == unit_index else value for i, value in enumerate(units))
                occurrences.append({
                    "split": split_by_locus[locus],
                    "page": record["page"],
                    "physical_folio": record["physical_folio"],
                    "locus": locus,
                    "line_number": int(meta["line_number"]),
                    "section": record["section"],
                    "currier": meta["language"],
                    "hand": meta["hand"],
                    "paragraph_id": meta["paragraph_id"],
                    "paragraph_line_index": meta["paragraph_line_index"],
                    "paragraph_line_count": meta["paragraph_line_count"],
                    "paragraph_line_pos": meta["paragraph_line_pos"],
                    "paragraph_marker_start": int(meta["paragraph_marker_start"]),
                    "paragraph_marker_end": int(meta["paragraph_marker_end"]),
                    "chunk_index": int(record["chunk_index"]),
                    "chunk_ordinal": chunk_ord,
                    "line_chunk_count": len(chunks),
                    "line_chunk_pos": line_chunk_pos,
                    "chunk_length": chunk_len,
                    "unit_index": unit_index,
                    "chunk_pos": chunk_pos,
                    "chunk_fraction": unit_index / (chunk_len - 1) if chunk_len > 1 else 0.5,
                    "line_unit_index": line_index,
                    "line_unit_count": line_total,
                    "line_edge": line_edge,
                    "line_quartile": min(3, int(4 * line_index / max(1, line_total))),
                    "paragraph_initial_event": int(meta["paragraph_line_index"] == 0 and line_index == 0),
                    "paragraph_final_event": int(
                        meta["paragraph_line_index"] == meta["paragraph_line_count"] - 1
                        and line_index == line_total - 1
                    ),
                    "unit": unit,
                    "left": units[unit_index - 1] if unit_index else "<BOS>",
                    "right": units[unit_index + 1] if unit_index + 1 < chunk_len else "<EOS>",
                    "masked_frame": " ".join(masked),
                    "local_frame": "|".join((
                        units[unit_index - 1] if unit_index else "<BOS>",
                        "*",
                        units[unit_index + 1] if unit_index + 1 < chunk_len else "<EOS>",
                        chunk_pos,
                    )),
                })
            line_offset += len(units)
    return occurrences


def add_frame_flags(occurrences, group):
    by_split_unit_frame = Counter((r["split"], r["unit"], r["masked_frame"]) for r in occurrences)
    by_split_unit_line = Counter((r["split"], r["unit"], r["locus"]) for r in occurrences)
    by_split_unit_paragraph = Counter((r["split"], r["unit"], r["paragraph_id"]) for r in occurrences)
    frame_units = defaultdict(set)
    for row in occurrences:
        if row["unit"] in group:
            frame_units[row["split"], row["masked_frame"]].add(row["unit"])
    for row in occurrences:
        row["self_neighbor"] = int(row["left"] == row["unit"] or row["right"] == row["unit"])
        row["class_neighbor"] = int(row["left"] in group or row["right"] in group)
        row["repeated_frame"] = int(by_split_unit_frame[row["split"], row["unit"], row["masked_frame"]] >= 2)
        row["same_unit_line_repeat"] = int(by_split_unit_line[row["split"], row["unit"], row["locus"]] >= 2)
        row["same_unit_paragraph_repeat"] = int(by_split_unit_paragraph[row["split"], row["unit"], row["paragraph_id"]] >= 2)
        row["shared_class_frame"] = int(len(frame_units[row["split"], row["masked_frame"]]) >= 2)


def select_matched_controls(occurrences):
    counts = Counter(row["unit"] for row in occurrences)
    target_sorted = sorted(TARGETS, key=lambda value: counts[value])
    candidates = sorted((u for u in counts if u not in TARGETS), key=lambda value: counts[value])
    n, m = len(target_sorted), len(candidates)
    inf = float("inf")
    dp = [[inf] * (m + 1) for _ in range(n + 1)]
    take = [[False] * (m + 1) for _ in range(n + 1)]
    for j in range(m + 1):
        dp[0][j] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            skip = dp[i][j - 1]
            match = dp[i - 1][j - 1] + abs(math.log(counts[target_sorted[i - 1]]) - math.log(counts[candidates[j - 1]]))
            if match < skip:
                dp[i][j], take[i][j] = match, True
            else:
                dp[i][j] = skip
    selected = []
    i, j = n, m
    while i:
        if take[i][j]:
            selected.append((target_sorted[i - 1], candidates[j - 1]))
            i -= 1
        j -= 1
    selected.reverse()
    return selected, counts


def unit_summary(occurrences, units, split):
    subset = occurrences if split == "pooled" else [r for r in occurrences if r["split"] == split]
    all_folios = sorted({r["physical_folio"] for r in subset})
    all_sections = sorted({r["section"] for r in subset})
    rows = []
    frame_count = Counter((r["unit"], r["masked_frame"]) for r in subset)
    for unit in units:
        values = [r for r in subset if r["unit"] == unit]
        n = len(values)
        if not n:
            continue
        folio = Counter(r["physical_folio"] for r in values)
        section = Counter(r["section"] for r in values)
        neighbors = Counter(f"L:{r['left']}" for r in values) + Counter(f"R:{r['right']}" for r in values)
        rows.append({
            "split": split,
            "unit": unit,
            "occurrences": n,
            "frequency_rank": 0,
            "standalone_rate": sum(r["chunk_pos"] == "only" for r in values) / n,
            "chunk_initial_rate": sum(r["chunk_pos"] in {"only", "initial"} for r in values) / n,
            "chunk_final_rate": sum(r["chunk_pos"] in {"only", "final"} for r in values) / n,
            "line_initial_rate": sum(r["line_edge"] in {"only", "initial"} for r in values) / n,
            "line_final_rate": sum(r["line_edge"] in {"only", "final"} for r in values) / n,
            "paragraph_initial_rate": sum(r["paragraph_initial_event"] for r in values) / n,
            "paragraph_final_rate": sum(r["paragraph_final_event"] for r in values) / n,
            "mean_chunk_fraction": statistics.fmean(r["chunk_fraction"] for r in values),
            "mean_chunk_length": statistics.fmean(r["chunk_length"] for r in values),
            "neighbor_entropy_nats": entropy(neighbors),
            "effective_neighbor_types": math.exp(entropy(neighbors)),
            "folio_effective_fraction": math.exp(entropy(folio)) / len(all_folios),
            "folio_gini_including_zero": gini([folio.get(f, 0) for f in all_folios]),
            "top_folio_fraction": max(folio.values()) / n,
            "section_effective_fraction": math.exp(entropy(section)) / len(all_sections),
            "repeated_exact_frame_rate": sum(frame_count[unit, r["masked_frame"]] >= 2 for r in values) / n,
            "same_unit_line_repeat_rate": sum(r["same_unit_line_repeat"] for r in values) / n,
            "same_unit_paragraph_repeat_rate": sum(r["same_unit_paragraph_repeat"] for r in values) / n,
            "distinct_lines": len({r["locus"] for r in values}),
            "distinct_paragraphs": len({r["paragraph_id"] for r in values}),
        })
    ranks = {row["unit"]: i for i, row in enumerate(sorted(rows, key=lambda r: (-r["occurrences"], r["unit"])), 1)}
    for row in rows:
        row["frequency_rank"] = ranks[row["unit"]]
    return rows


def group_comparisons(occurrences, targets, controls):
    metrics = (
        ("standalone", lambda r: r["chunk_pos"] == "only"),
        ("chunk_initial", lambda r: r["chunk_pos"] in {"only", "initial"}),
        ("chunk_final", lambda r: r["chunk_pos"] in {"only", "final"}),
        ("line_initial", lambda r: r["line_edge"] in {"only", "initial"}),
        ("line_final", lambda r: r["line_edge"] in {"only", "final"}),
        ("paragraph_initial", lambda r: bool(r["paragraph_initial_event"])),
        ("paragraph_final", lambda r: bool(r["paragraph_final_event"])),
        ("self_neighbor", lambda r: bool(r["self_neighbor"])),
        ("repeated_exact_frame", lambda r: bool(r["repeated_frame"])),
        ("same_unit_line_repeat", lambda r: bool(r["same_unit_line_repeat"])),
        ("same_unit_paragraph_repeat", lambda r: bool(r["same_unit_paragraph_repeat"])),
    )
    out = []
    for split in ("train", "held", "pooled"):
        base = occurrences if split == "pooled" else [r for r in occurrences if r["split"] == split]
        a = [r for r in base if r["unit"] in targets]
        b = [r for r in base if r["unit"] in controls]
        for name, predicate in metrics:
            ay, by = sum(predicate(r) for r in a), sum(predicate(r) for r in b)
            out.append({
                "split": split, "metric": name,
                "target_yes": ay, "target_total": len(a), "target_rate": ay / len(a),
                "control_yes": by, "control_total": len(b), "control_rate": by / len(b),
                "target_vs_control_odds_ratio": odds_ratio(ay, len(a) - ay, by, len(b) - by),
            })
        target_adj = sum(r["left"] in targets or r["right"] in targets for r in a)
        control_adj = sum(r["left"] in controls or r["right"] in controls for r in b)
        out.append({
            "split": split, "metric": "class_neighbor_comparison",
            "target_yes": target_adj, "target_total": len(a), "target_rate": target_adj / len(a),
            "control_yes": control_adj, "control_total": len(b), "control_rate": control_adj / len(b),
            "target_vs_control_odds_ratio": odds_ratio(target_adj, len(a) - target_adj, control_adj, len(b) - control_adj),
        })
    return out


def individual_control_comparisons(occurrences, matches):
    metrics = (
        ("standalone", lambda r: r["chunk_pos"] == "only"),
        ("chunk_initial", lambda r: r["chunk_pos"] in {"only", "initial"}),
        ("chunk_final", lambda r: r["chunk_pos"] in {"only", "final"}),
        ("line_initial", lambda r: r["line_edge"] in {"only", "initial"}),
        ("line_final", lambda r: r["line_edge"] in {"only", "final"}),
        ("paragraph_initial", lambda r: bool(r["paragraph_initial_event"])),
        ("paragraph_final", lambda r: bool(r["paragraph_final_event"])),
        ("self_neighbor", lambda r: bool(r["self_neighbor"])),
        ("repeated_exact_frame", lambda r: bool(r["repeated_frame"])),
        ("same_unit_line_repeat", lambda r: bool(r["same_unit_line_repeat"])),
        ("same_unit_paragraph_repeat", lambda r: bool(r["same_unit_paragraph_repeat"])),
    )
    out = []
    for split in ("train", "held", "pooled"):
        base = occurrences if split == "pooled" else [r for r in occurrences if r["split"] == split]
        for target, control in matches:
            a = [r for r in base if r["unit"] == target]
            b = [r for r in base if r["unit"] == control]
            for name, predicate in metrics:
                ay, by = sum(predicate(r) for r in a), sum(predicate(r) for r in b)
                out.append({
                    "split": split, "target": target, "control": control, "metric": name,
                    "target_yes": ay, "target_total": len(a), "target_rate": ay / len(a),
                    "control_yes": by, "control_total": len(b), "control_rate": by / len(b),
                    "odds_ratio": odds_ratio(ay, len(a) - ay, by, len(b) - by),
                })
    return out


def pairwise_rows(occurrences):
    out = []
    for split in ("train", "held", "pooled"):
        base = occurrences if split == "pooled" else [r for r in occurrences if r["split"] == split]
        by = {unit: [r for r in base if r["unit"] == unit] for unit in TARGETS}
        for i, a in enumerate(TARGETS):
            for b in TARGETS[i + 1:]:
                av, bv = by[a], by[b]
                def dist(rows, field): return Counter(r[field] for r in rows)
                af, bf = dist(av, "masked_frame"), dist(bv, "masked_frame")
                common = set(af) & set(bf)
                out.append({
                    "split": split, "unit_a": a, "unit_b": b,
                    "left_js_bits": js_divergence(dist(av, "left"), dist(bv, "left")),
                    "right_js_bits": js_divergence(dist(av, "right"), dist(bv, "right")),
                    "position_js_bits": js_divergence(dist(av, "chunk_pos"), dist(bv, "chunk_pos")),
                    "section_js_bits": js_divergence(dist(av, "section"), dist(bv, "section")),
                    "hand_js_bits": js_divergence(dist(av, "hand"), dist(bv, "hand")),
                    "folio_js_bits": js_divergence(dist(av, "physical_folio"), dist(bv, "physical_folio")),
                    "masked_frame_sorensen": sorensen_counter(af, bf),
                    "shared_masked_frame_types": len(common),
                    "a_occurrence_in_shared_frame_rate": sum(af[k] for k in common) / len(av),
                    "b_occurrence_in_shared_frame_rate": sum(bf[k] for k in common) / len(bv),
                })
    return out


def category_trace(mapping_rows):
    out = []
    for language in LANGUAGES:
        for unit in TARGETS:
            relevant = [r for r in mapping_rows if r["language"] == language and r["unit"] == unit]
            groups = {
                "real_primary": [r for r in relevant if r["model_kind"] == "real" and r["config"].startswith("primary_")],
                "real_all_grids": [r for r in relevant if r["model_kind"] == "real"],
                "destroyed_primary": [r for r in relevant if r["model_kind"] == "destroyed" and r["config"].startswith("primary_")],
            }
            row = {"language": language, "unit": unit}
            for name, values in groups.items():
                row[f"{name}_runs"] = len(values)
                row[f"{name}_whole_word_fraction"] = sum(r["category"] == "W" for r in values) / len(values)
                row[f"{name}_category_counts"] = ";".join(f"{k}:{v}" for k, v in sorted(Counter(r["category"] for r in values).items()))
            out.append(row)
    return out


def architecture_rows(mapping_rows, summary):
    real = defaultdict(list)
    destroyed = defaultdict(list)
    for row in mapping_rows:
        if row["model_kind"] == "real":
            real[row["unit"]].append(row["category"])
        elif row["model_kind"] == "destroyed":
            destroyed[row["unit"]].append(row["category"])
    out = []
    for row in summary:
        if row["split"] != "pooled":
            continue
        unit = row["unit"]
        out.append({
            **row,
            "real_whole_word_fraction_36": sum(x == "W" for x in real[unit]) / len(real[unit]),
            "destroyed_whole_word_fraction_12": sum(x == "W" for x in destroyed[unit]) / len(destroyed[unit]),
            "is_target": int(unit in TARGETS),
        })
    return out


FEATURES = (
    "left", "right", "chunk_pos", "chunk_length_bin", "line_chunk_pos",
    "line_quartile", "line_edge", "paragraph_line_pos", "section", "hand", "currier",
)
FEATURE_SETS = {
    "local_neighbors": ("left", "right"),
    "position": (
        "chunk_pos", "chunk_length_bin", "line_chunk_pos", "line_quartile",
        "line_edge", "paragraph_line_pos",
    ),
    "metadata": ("section", "hand", "currier"),
    "full": FEATURES,
}


def classifier_feature(row, feature):
    if feature == "chunk_length_bin":
        return category(row["chunk_length"], (("1", 1), ("2", 2), ("3-4", 4), ("5+", 10**9)))
    return str(row[feature])


def fit_categorical_nb(train, features, alpha=0.5):
    classes = list(TARGETS)
    class_counts = Counter(r["unit"] for r in train)
    vocab = {f: sorted({classifier_feature(r, f) for r in train}) for f in features}
    counts = {f: Counter((r["unit"], classifier_feature(r, f)) for r in train) for f in features}
    total = len(train)
    def predict(rows):
        logp = np.zeros((len(rows), len(classes)), dtype=float)
        for j, cls in enumerate(classes):
            logp[:, j] = math.log((class_counts[cls] + alpha) / (total + alpha * len(classes)))
            for i, row in enumerate(rows):
                for feature in features:
                    value = classifier_feature(row, feature)
                    denom = class_counts[cls] + alpha * (len(vocab[feature]) + 1)
                    logp[i, j] += math.log((counts[feature][cls, value] + alpha) / denom)
        logp -= logp.max(axis=1, keepdims=True)
        prob = np.exp(logp)
        prob /= prob.sum(axis=1, keepdims=True)
        return prob
    priors = np.asarray([class_counts[c] / total for c in classes])
    return predict, classes, priors, {f: len(v) for f, v in vocab.items()}


def balanced_accuracy(y, pred, nclasses):
    recalls = []
    for value in range(nclasses):
        mask = y == value
        recalls.append(float(np.mean(pred[mask] == value)))
    return statistics.fmean(recalls)


def multiclass_metrics(y, prob, classes, priors):
    pred = prob.argmax(axis=1)
    confusion = np.zeros((len(classes), len(classes)), dtype=int)
    for actual, guess in zip(y, pred):
        confusion[actual, guess] += 1
    ll = -float(np.mean(np.log2(np.clip(prob[np.arange(len(y)), y], 1e-300, 1))))
    baseline = -float(np.mean(np.log2(priors[y])))
    return {
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": balanced_accuracy(y, pred, len(classes)),
        "log_loss_bits": ll,
        "train_prior_log_loss_bits": baseline,
        "gain_over_train_prior_bits_per_event": baseline - ll,
        "confusion": confusion,
        "prediction": pred,
    }


def auc_binary(labels, scores):
    labels = np.asarray(labels)
    ranks = np.asarray(average_ranks(list(scores)))
    n1 = int(np.sum(labels == 1))
    n0 = len(labels) - n1
    return (float(ranks[labels == 1].sum()) - n1 * (n1 + 1) / 2) / (n1 * n0)


def classifier_analysis(occurrences):
    train = [r for r in occurrences if r["split"] == "train" and r["unit"] in TARGETS]
    held = [r for r in occurrences if r["split"] == "held" and r["unit"] in TARGETS]
    predictions = {}
    ablations = {}
    for name, features in FEATURE_SETS.items():
        predict, classes, priors, vocab_sizes = fit_categorical_nb(train, features)
        candidate_prob = predict(held)
        candidate_y = np.asarray([classes.index(r["unit"]) for r in held], dtype=int)
        candidate_metrics = multiclass_metrics(candidate_y, candidate_prob, classes, priors)
        predictions[name] = (candidate_prob, classes, priors, vocab_sizes, candidate_metrics)
        ablations[name] = {
            "features": list(features),
            "held_accuracy": candidate_metrics["accuracy"],
            "held_balanced_accuracy": candidate_metrics["balanced_accuracy"],
            "held_log_loss_bits": candidate_metrics["log_loss_bits"],
            "held_gain_over_train_prior_bits_per_event": candidate_metrics["gain_over_train_prior_bits_per_event"],
        }
    prob, classes, priors, vocab_sizes, metrics = predictions["full"]
    cmap = {value: i for i, value in enumerate(classes)}
    y = np.asarray([cmap[r["unit"]] for r in held], dtype=int)
    rng = random.Random(60620260828)
    strata = defaultdict(list)
    for index, row in enumerate(held):
        strata[row["section"], row["hand"], row["chunk_pos"]].append(index)
    null_balanced, null_logloss = [], []
    for _ in range(200):
        perm = y.copy()
        for indices in strata.values():
            values = list(perm[indices])
            rng.shuffle(values)
            perm[indices] = values
        null = multiclass_metrics(perm, prob, classes, priors)
        null_balanced.append(null["balanced_accuracy"])
        null_logloss.append(null["log_loss_bits"])
    pairwise = []
    for i, a in enumerate(classes):
        for j, b in enumerate(classes[i + 1:], i + 1):
            mask = np.logical_or(y == i, y == j)
            score = np.log(np.clip(prob[mask, i], 1e-300, 1)) - np.log(np.clip(prob[mask, j], 1e-300, 1))
            pairwise.append({
                "unit_a": a, "unit_b": b,
                "held_events": int(mask.sum()),
                "auc_a_over_b": auc_binary((y[mask] == i).astype(int), score),
            })
    confusion_rows = []
    for i, actual in enumerate(classes):
        for j, predicted in enumerate(classes):
            confusion_rows.append({
                "actual": actual, "predicted": predicted,
                "count": int(metrics["confusion"][i, j]),
                "row_fraction": metrics["confusion"][i, j] / metrics["confusion"][i].sum(),
            })
    result = {
        "model": "categorical_multinomial_naive_bayes",
        "features": list(FEATURES), "alpha": 0.5,
        "ablations": ablations,
        "train_events": len(train), "held_events": len(held),
        "classes": classes, "train_priors": dict(zip(classes, priors.tolist())),
        "vocabulary_sizes": vocab_sizes,
        "held_accuracy": metrics["accuracy"],
        "held_balanced_accuracy": metrics["balanced_accuracy"],
        "held_log_loss_bits": metrics["log_loss_bits"],
        "held_train_prior_log_loss_bits": metrics["train_prior_log_loss_bits"],
        "held_gain_over_train_prior_bits_per_event": metrics["gain_over_train_prior_bits_per_event"],
        "conditional_permutations": 200,
        "permutation_strata": "section x hand x chunk_pos",
        "null_balanced_accuracy_mean": statistics.fmean(null_balanced),
        "null_balanced_accuracy_sd": statistics.stdev(null_balanced),
        "balanced_accuracy_empirical_p_ge": (1 + sum(x >= metrics["balanced_accuracy"] for x in null_balanced)) / 201,
        "null_log_loss_mean_bits": statistics.fmean(null_logloss),
        "null_log_loss_sd_bits": statistics.stdev(null_logloss),
        "log_loss_empirical_p_le": (1 + sum(x <= metrics["log_loss_bits"] for x in null_logloss)) / 201,
        "pairwise_auc": pairwise,
    }
    return result, confusion_rows


def metadata_rows(occurrences):
    out = []
    for split in ("train", "held", "pooled"):
        base = occurrences if split == "pooled" else [r for r in occurrences if r["split"] == split]
        for dimension in ("section", "currier", "hand"):
            exposure = Counter(r[dimension] for r in base)
            for unit in TARGETS:
                counts = Counter(r[dimension] for r in base if r["unit"] == unit)
                for value in sorted(exposure):
                    out.append({
                        "split": split, "dimension": dimension, "value": value, "unit": unit,
                        "count": counts[value], "all_unit_exposure": exposure[value],
                        "rate_per_1000_units": 1000 * counts[value] / exposure[value],
                        "within_unit_fraction": counts[value] / sum(counts.values()),
                    })
    return out


def folio_rows(occurrences):
    out = []
    for split in ("train", "held", "pooled"):
        base = occurrences if split == "pooled" else [r for r in occurrences if r["split"] == split]
        exposure = Counter(r["physical_folio"] for r in base)
        for unit in TARGETS:
            counts = Counter(r["physical_folio"] for r in base if r["unit"] == unit)
            for folio in sorted(exposure):
                out.append({
                    "split": split, "physical_folio": folio, "unit": unit,
                    "count": counts[folio], "all_unit_exposure": exposure[folio],
                    "rate_per_1000_units": 1000 * counts[folio] / exposure[folio],
                    "within_unit_fraction": counts[folio] / sum(counts.values()),
                })
    return out


def top_neighbors(occurrences):
    rows = []
    for split in ("train", "held", "pooled"):
        base = occurrences if split == "pooled" else [r for r in occurrences if r["split"] == split]
        for unit in TARGETS:
            values = [r for r in base if r["unit"] == unit]
            for side in ("left", "right"):
                counter = Counter(r[side] for r in values)
                for rank, (neighbor, count) in enumerate(counter.most_common(15), 1):
                    rows.append({
                        "split": split, "unit": unit, "side": side, "rank": rank,
                        "neighbor": neighbor, "count": count, "fraction": count / len(values),
                    })
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    observed = {name: sha(SOURCE / name) for name in EXPECTED}
    if observed != EXPECTED:
        raise RuntimeError(f"input drift: {observed}")
    guarded = read_tsv(SOURCE / "guarded_rows.tsv")
    if any(row["page"].lower().startswith("f84") for row in guarded):
        raise RuntimeError("forbidden page present")
    sequences = json.loads((SOURCE / "unit_sequences.json").read_text())
    metadata = paragraph_metadata(guarded)
    occurrences = build_occurrences(sequences, metadata)
    frequency = Counter(row["unit"] for row in occurrences)
    frozen_frequency = Counter(sequences["frequency"]["train"]) + Counter(sequences["frequency"]["held"])
    if frequency != frozen_frequency:
        raise RuntimeError("occurrence reconstruction mismatch")
    add_frame_flags(occurrences, set(TARGETS))
    matches, counts = select_matched_controls(occurrences)
    controls = tuple(value for _target, value in matches)
    summaries = []
    for split in ("train", "held", "pooled"):
        summaries.extend(unit_summary(occurrences, sequences["inventory"], split))
    mapping_rows = read_tsv(SOURCE / "complete_mappings.tsv")
    trace = category_trace(mapping_rows)
    architecture = architecture_rows(mapping_rows, summaries)
    architecture_by_unit = {r["unit"]: r for r in architecture}
    architecture_correlations = {}
    for feature in (
        "occurrences", "standalone_rate", "chunk_initial_rate", "chunk_final_rate",
        "line_initial_rate", "line_final_rate", "effective_neighbor_types",
        "folio_effective_fraction", "section_effective_fraction", "repeated_exact_frame_rate",
    ):
        x = [math.log(r[feature]) if feature == "occurrences" else r[feature] for r in architecture]
        y = [r["real_whole_word_fraction_36"] for r in architecture]
        architecture_correlations[feature] = {
            "pearson": correlation(x, y), "spearman": spearman(x, y)
        }

    group_rows = group_comparisons(occurrences, set(TARGETS), set(controls))
    individual_rows = individual_control_comparisons(occurrences, matches)
    pairs = pairwise_rows(occurrences)
    classifier, confusion = classifier_analysis(occurrences)
    metadata_out = metadata_rows(occurrences)
    folios = folio_rows(occurrences)
    neighbors = top_neighbors(occurrences)
    target_occurrences = [r for r in occurrences if r["unit"] in TARGETS]
    page_selection = [
        {"page": page, "physical_folio": folio, "split": split}
        for page, folio, split in sorted({
            (r["page"], r["physical_folio"], r["split"]) for r in guarded
        })
    ]

    target_unit_summary = [r for r in summaries if r["unit"] in TARGETS]
    target_meta_contingencies = {}
    for split in ("train", "held", "pooled"):
        base = target_occurrences if split == "pooled" else [r for r in target_occurrences if r["split"] == split]
        for dimension in ("section", "currier", "hand", "chunk_pos"):
            statistic, cramer, _matrix, rowvals, colvals = chi_square(base, "unit", dimension)
            target_meta_contingencies[f"{split}:{dimension}"] = {
                "chi_square": statistic, "cramers_v": cramer,
                "unit_levels": rowvals, "dimension_levels": colvals,
            }

    result = {
        "schema": "gdt606-whole-word-distributional-role-attack-v1",
        "decision_ceiling": "distributional default roles only; no word meaning or plaintext",
        "f84_f84r": "FORBIDDEN_AND_ABSENT",
        "targets": list(TARGETS),
        "matched_frequency_controls": [
            {"target": a, "target_occurrences": counts[a], "control": b, "control_occurrences": counts[b]}
            for a, b in matches
        ],
        "input_hashes": observed,
        "guarded_rows": len(guarded),
        "guarded_query": {
            "allow_list_source": "gdt327_joint_tuple_interlinear.tsv",
            "allow_list_source_sha256": "7eba46774be44992064cc114f67329723ac7bf589321b0d763fb7f7f748cc1e9",
            "selector": "page",
            "allow_values_count": len(page_selection),
            "allow_values_artifact": "guarded_page_selection.tsv",
            "forbid_prefix": "f84",
            "columns": "page,locus,line_number,section,language,hand,eva_clean,ivtff_raw",
            "physical_folios": len({r["physical_folio"] for r in guarded}),
            "train_folios": len({r["physical_folio"] for r in guarded if r["split"] == "train"}),
            "held_folios": len({r["physical_folio"] for r in guarded if r["split"] == "held"}),
        },
        "hard_chunks": len(sequences["sequences"]["train"]) + len(sequences["sequences"]["held"]),
        "all_unit_occurrences": len(occurrences),
        "target_occurrences": len(target_occurrences),
        "target_occurrences_by_split": dict(Counter(r["split"] for r in target_occurrences)),
        "paragraphs": len({r["paragraph_id"] for r in occurrences}),
        "category_trace": trace,
        "architecture_correlations": architecture_correlations,
        "target_metadata_contingencies": target_meta_contingencies,
        "classifier": classifier,
        "pairwise_summary": {
            split: {
                field: {
                    "min": min(r[field] for r in pairs if r["split"] == split),
                    "median": statistics.median(r[field] for r in pairs if r["split"] == split),
                    "max": max(r[field] for r in pairs if r["split"] == split),
                }
                for field in ("left_js_bits", "right_js_bits", "position_js_bits", "section_js_bits", "folio_js_bits", "masked_frame_sorensen")
            } for split in ("train", "held", "pooled")
        },
        "source_binding_note": "An initial pre-analysis input guard caught the final GDT606 rerun; the operative pins now match the completed binding inventory.",
    }

    occurrence_fields = [
        "split", "page", "physical_folio", "locus", "line_number", "section", "currier", "hand",
        "paragraph_id", "paragraph_line_index", "paragraph_line_count", "paragraph_line_pos",
        "paragraph_marker_start", "paragraph_marker_end",
        "chunk_index", "chunk_ordinal", "line_chunk_count", "line_chunk_pos", "chunk_length",
        "unit_index", "chunk_pos", "chunk_fraction", "line_unit_index", "line_unit_count",
        "line_edge", "line_quartile", "paragraph_initial_event", "paragraph_final_event",
        "unit", "left", "right", "masked_frame", "local_frame", "self_neighbor",
        "class_neighbor", "repeated_frame", "shared_class_frame",
        "same_unit_line_repeat", "same_unit_paragraph_repeat",
    ]
    write_tsv(OUT / "target_occurrences.tsv", target_occurrences, occurrence_fields)
    write_tsv(OUT / "unit_structural_summary.tsv", summaries)
    write_tsv(OUT / "target_structural_summary.tsv", target_unit_summary)
    write_tsv(OUT / "category_trace.tsv", trace)
    write_tsv(OUT / "architecture_unit_audit.tsv", architecture)
    write_tsv(OUT / "group_vs_frequency_controls.tsv", group_rows)
    write_tsv(OUT / "unit_vs_matched_control.tsv", individual_rows)
    write_tsv(OUT / "pairwise_substitution.tsv", pairs)
    write_tsv(OUT / "classifier_confusion.tsv", confusion)
    write_tsv(OUT / "metadata_rates.tsv", metadata_out)
    write_tsv(OUT / "folio_rates.tsv", folios)
    write_tsv(OUT / "top_neighbors.tsv", neighbors)
    write_tsv(OUT / "guarded_page_selection.tsv", page_selection)
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    generated = [
        "target_occurrences.tsv", "unit_structural_summary.tsv", "target_structural_summary.tsv",
        "category_trace.tsv", "architecture_unit_audit.tsv", "group_vs_frequency_controls.tsv",
        "unit_vs_matched_control.tsv",
        "pairwise_substitution.tsv", "classifier_confusion.tsv", "metadata_rates.tsv",
        "folio_rates.tsv", "top_neighbors.tsv", "RESULT.json",
        "guarded_page_selection.tsv",
    ]
    manifest = {
        "schema": "gdt606-role-attack-artifact-manifest-v1",
        "analysis_source_sha256": sha(Path(__file__)),
        "inputs": observed,
        "outputs": {name: sha(OUT / name) for name in generated},
    }
    (OUT / "ARTIFACT_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "result": result,
        "controls": controls,
        "output_manifest_sha256": sha(OUT / "ARTIFACT_MANIFEST.json"),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
