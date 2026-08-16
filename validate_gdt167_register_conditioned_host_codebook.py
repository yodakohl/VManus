#!/usr/bin/env python3
"""Independent, nonimporting reconstruction of GDT167."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt062_right_family_inventory.tsv"
DESIGN = R / "gdt167_design.json"
METHOD = R / "GDT167_REGISTER_CONDITIONED_HOST_CODEBOOK_METHOD.md"
REPORT = R / "GDT167_REGISTER_CONDITIONED_HOST_CODEBOOK_REPORT.md"
CAPACITY = R / "gdt167_stratum_capacity.tsv"
FOLDS = R / "gdt167_codebook_fold_scores.tsv"
SCORES = R / "gdt167_codebook_scores.tsv"
CODE_NULL = R / "gdt167_codebook_null.tsv"
PANELS = R / "gdt167_host_panels.tsv"
GEOMETRY = R / "gdt167_geometry_stability.tsv"
GEOMETRY_NULL = R / "gdt167_geometry_null.tsv"
MAPPINGS = R / "gdt167_alignment_mappings.tsv"
ALIGNMENT = R / "gdt167_alignment_scores.tsv"
ALIGNMENT_NULL = R / "gdt167_alignment_null.tsv"
COUNTER = R / "gdt167_counterexamples.tsv"
VARIANTS = R / "gdt167_variant_log.tsv"
RESULT = R / "gdt167_result.json"
VALIDATION = R / "gdt167_validation.json"

STRATA = {
    "HERBAL_A": ("H", "A"),
    "HERBAL_B": ("H", "B"),
    "STARS_RECIPE_B": ("S", "B"),
    "PHARMA_A": ("P", "A"),
    "BIOLOGICAL_B": ("B", "B"),
}
MODES = ("WINDOW_PM2", "WHOLE_LINE")
FEATURES = ("section", "currier", "hand", "frequency_bin", "position_quartile", "line_count_bin")
BLOCKS = ((0, 3), (3, 5), (5, 8), (8, 10))
ALPHA, BETA, WORLDS = 32.0, 16.0, 1024
PANEL_N, CONTEXT_N = 10, 128


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def opaque(text):
    return "H" + hashlib.sha256(text.encode()).hexdigest()[:16]


def seed(text):
    return int(hashlib.sha256(text.encode()).hexdigest()[:16], 16)


def csha(value):
    body = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(body.encode()).hexdigest()


def fbin(n):
    return "F1" if n == 1 else "F2_4" if n <= 4 else "F5_15" if n <= 15 else "F16_63" if n <= 63 else "F64P"


def lbin(n):
    return str(n) if n <= 4 else "5_7" if n <= 7 else "8P"


def lkey(locus):
    page, line = locus.split(".")
    return page, int(line)


def close(a, b, tol=4e-9):
    a, b = float(a), float(b)
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


class Checks:
    def __init__(self):
        self.rows = []

    def add(self, name, passed, detail=""):
        row = {"name": name, "passed": bool(passed), "detail": str(detail)}
        self.rows.append(row)
        if not passed:
            raise AssertionError(f"{name}: {detail}")


def stratum(section, currier):
    for name, pair in STRATA.items():
        if pair == (section, currier):
            return name
    return None


def rebuild_source(checks):
    rows, total, rejected = [], 0, 0
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle, delimiter="\t"):
            total += 1
            page, locus = raw["page"], raw["locus"]
            if page.startswith("f84") or locus.startswith("f84"):
                rejected += 1
                continue
            name = stratum(raw["section"], raw["currier"])
            if name is None or int(raw["group_count"]) <= 1:
                continue
            rows.append({
                "host": raw["page_host"], "locus": locus,
                "folio": raw["physical_folio"], "section": raw["section"],
                "currier": raw["currier"], "hand": raw["hand"],
                "index": int(raw["group_index"]), "group_count": int(raw["group_count"]),
                "position_quartile": raw["position_quartile"], "stratum": name,
            })
    checks.add("source_total_and_f84_rejection", (total, rejected) == (15592, 228), (total, rejected))
    checks.add("source_firewall", all(not x["locus"].startswith("f84") for x in rows))
    by = defaultdict(list)
    for row in rows:
        by[row["stratum"]].append(row)
    expected = {"HERBAL_A": 3909, "HERBAL_B": 1323, "STARS_RECIPE_B": 4854, "PHARMA_A": 650, "BIOLOGICAL_B": 3153}
    checks.add("powered_stratum_counts", {s: len(by[s]) for s in STRATA} == expected)
    contexts = {s: {m: [] for m in MODES} for s in STRATA}
    for name in STRATA:
        freq = Counter(x["host"] for x in by[name])
        lines = defaultdict(list)
        for row in by[name]:
            row["frequency_bin"] = fbin(freq[row["host"]])
            row["line_count_bin"] = lbin(row["group_count"])
            row["half"] = int(hashlib.sha256(f"{name}|{row['folio']}".encode()).hexdigest()[:8], 16) % 2
            row["occurrence_id"] = f"{name}:{row['locus']}:{row['index']}"
            row["nuisance_key"] = tuple(row[f] for f in FEATURES)
            lines[row["locus"]].append(row)
        for locus in sorted(lines, key=lkey):
            line = sorted(lines[locus], key=lambda x: x["index"])
            bag = Counter(x["host"] for x in line)
            for i, row in enumerate(line):
                window = Counter(line[j]["host"] for j in range(max(0, i - 2), min(len(line), i + 3)) if j != i)
                whole = bag.copy()
                whole[row["host"]] -= 1
                if whole[row["host"]] == 0:
                    del whole[row["host"]]
                contexts[name]["WINDOW_PM2"].append({**row, "context": window})
                contexts[name]["WHOLE_LINE"].append({**row, "context": whole})
    cap = {x["stratum"]: x for x in tsv(CAPACITY)}
    for name in STRATA:
        checks.add(f"capacity:{name}", int(cap[name]["groups"]) == len(by[name]))
    return rows, by, contexts


def fit(events, vocabulary):
    target, host_target, host_n = Counter(), Counter(), Counter()
    feature_target = [Counter() for _ in FEATURES]
    feature_n = [Counter() for _ in FEATURES]
    for row in events:
        mass = sum(row["context"].values())
        for target_id, count in row["context"].items():
            weight = count / mass
            target[target_id] += weight
            host_target[row["host"], target_id] += weight
            for j, feature in enumerate(FEATURES):
                feature_target[j][row[feature], target_id] += weight
        host_n[row["host"]] += 1
        for j, feature in enumerate(FEATURES):
            feature_n[j][row[feature]] += 1
    return {"target": target, "n": float(len(events)), "v": len(vocabulary), "ft": feature_target,
            "fn": feature_n, "ht": host_target, "hn": host_n}


def probability(model, row, target_id):
    q = (model["target"][target_id] + .5) / (model["n"] + .5 * model["v"])
    parts = []
    for j, feature in enumerate(FEATURES):
        parts.append((model["ft"][j][row[feature], target_id] + ALPHA * q) /
                     (model["fn"][j][row[feature]] + ALPHA))
    nuisance = sum(parts) / len(parts)
    host = (model["ht"][row["host"], target_id] + BETA * nuisance) / (model["hn"][row["host"]] + BETA)
    return q, nuisance, host


def score(model, row):
    mass, out = sum(row["context"].values()), Counter()
    for target_id, count in row["context"].items():
        weight = count / mass
        q, nuisance, host = probability(model, row, target_id)
        out["unigram_bits"] -= weight * math.log2(q)
        out["nuisance_bits"] -= weight * math.log2(nuisance)
        out["host_bits"] -= weight * math.log2(host)
    out["gain_bits"] = out["nuisance_bits"] - out["host_bits"]
    return out


def refit_codebooks(contexts, checks):
    exported = {(r["stratum"], r["context_mode"], r["axis"], r["held"]): r for r in tsv(FOLDS)}
    artifacts, aggregates = {}, {}
    for name in STRATA:
        vocab = tuple(sorted({x["host"] for x in contexts[name]["WHOLE_LINE"]}, key=opaque))
        for mode in MODES:
            events = contexts[name][mode]
            for axis, field in (("HELD_FOLIO", "folio"),) + (("HELD_HAND", "hand"),) * (name == "HERBAL_B"):
                for held in sorted({x[field] for x in events}):
                    training = [x for x in events if x[field] != held]
                    test = [x for x in events if x[field] == held]
                    model, total, seen = fit(training, vocab), Counter(), 0
                    for row in test:
                        total.update(score(model, row))
                        seen += int(model["hn"][row["host"]] > 0)
                    got = exported[name, mode, axis, held]
                    checks.add(f"fold_counts:{name}:{mode}:{axis}:{held}",
                               (int(got["focal_occurrences"]), int(got["training_occurrences"]), int(got["source_seen"])) ==
                               (len(test), len(training), seen))
                    checks.add(f"fold_bits:{name}:{mode}:{axis}:{held}", all(close(got[k], total[k]) for k in
                               ("unigram_bits", "nuisance_bits", "host_bits", "gain_bits")))
                    key = name, mode, axis
                    aggregates.setdefault(key, Counter()).update(total)
                    aggregates[key]["n"] += len(test)
                    aggregates[key]["positive"] += int(total["gain_bits"] > 0)
                    if axis == "HELD_FOLIO":
                        artifacts[name, mode, held] = model, test
    return artifacts, aggregates


def code_null(name, mode, events, artifacts):
    prepared, swappable, variable = {}, 0, 0
    for held in sorted({x["folio"] for x in events}):
        model, test = artifacts[name, mode, held]
        groups = defaultdict(list)
        for row in test:
            groups[row["nuisance_key"]].append(row)
        packed = {}
        for key, group in groups.items():
            sources = sorted({x["host"] for x in group}, key=opaque)
            targets = {y for x in group for y in x["context"]}
            logs, example = {}, group[0]
            for source in sources:
                fake = dict(example)
                fake["host"] = source
                for target_id in targets:
                    _, nuisance, host = probability(model, fake, target_id)
                    logs[source, target_id] = math.log2(host / nuisance)
            lookup = {}
            for row in group:
                mass = sum(row["context"].values())
                for source in sources:
                    lookup[row["occurrence_id"], source] = sum(
                        count / mass * logs[source, target_id] for target_id, count in row["context"].items())
            packed[key] = group, lookup
        prepared[held] = packed
        swappable += sum(len(g) for g in groups.values() if len(g) >= 2)
        variable += sum(len(g) for g in groups.values() if len({x["host"] for x in g}) >= 2)
    rng, values = random.Random(seed(f"GDT167_CODE_NULL_{name}_{mode}")), []
    for _ in range(WORLDS):
        gain = 0.0
        for held in sorted(prepared):
            for key in sorted(prepared[held], key=str):
                group, lookup = prepared[held][key]
                sources = [x["host"] for x in group]
                rng.shuffle(sources)
                gain += sum(lookup[x["occurrence_id"], source] for x, source in zip(group, sources))
        values.append(gain / len(events))
    return values, swappable, variable


def verify_codebook_nulls(contexts, artifacts, aggregates, checks):
    null_table = tsv(CODE_NULL)
    summary = {(x["stratum"], x["context_mode"], x["axis"]): x for x in tsv(SCORES)}
    nulls, caps = {}, {}
    for name in STRATA:
        for mode in MODES:
            values, swappable, variable = code_null(name, mode, contexts[name][mode], artifacts)
            nulls[name, mode], caps[name, mode] = values, (swappable, variable)
            field = f"{name}__{mode}_gain_per_focal"
            checks.add(f"code_null:{name}:{mode}", all(close(row[field], values[i]) for i, row in enumerate(null_table)))
    means = {key: sum(values) / WORLDS for key, values in nulls.items()}
    max_values = [max(nulls[key][world] - means[key] for key in nulls) for world in range(WORLDS)]
    checks.add("code_null_max10", all(close(row["max10_null_centered"], max_values[i]) for i, row in enumerate(null_table)))
    for key, total in aggregates.items():
        got = summary[key]
        checks.add("aggregate:" + ":".join(key), close(got["gain_bits"], total["gain_bits"]) and
                   int(got["positive_folds"]) == total["positive"] and int(got["focal_occurrences"]) == total["n"])
        if key[2] == "HELD_FOLIO":
            nm = means[key[:2]]
            observed = total["gain_bits"] / total["n"]
            local_p = (1 + sum(x >= observed - 1e-12 for x in nulls[key[:2]])) / (WORLDS + 1)
            max_p = (1 + sum(x >= observed - nm - 1e-12 for x in max_values)) / (WORLDS + 1)
            checks.add("aggregate_null:" + ":".join(key), close(got["null_mean_gain_per_focal"], nm) and
                       close(got["alignment_excess_per_focal"], observed - nm) and close(got["local_p"], local_p) and
                       close(got["max10_p"], max_p) and (int(got["null_swappable"]), int(got["null_variable"])) == caps[key[:2]])
    return summary


def select_panels(by, contexts, checks):
    exported = defaultdict(list)
    for row in tsv(PANELS):
        exported[row["stratum"]].append(row)
    out = {}
    for name in STRATA:
        freq = Counter(x["host"] for x in by[name])
        halves = {half: Counter(x["host"] for x in by[name] if x["half"] == half) for half in (0, 1)}
        eligible = [host for host, _ in sorted(freq.items(), key=lambda item: (-item[1], opaque(item[0])))
                    if halves[0][host] >= 4 and halves[1][host] >= 4]
        panel = tuple(eligible[:PANEL_N])
        context_mass = Counter()
        for row in contexts[name]["WHOLE_LINE"]:
            mass = sum(row["context"].values())
            for target_id, count in row["context"].items():
                context_mass[target_id] += count / mass
        context_panel = tuple(x for x, _ in sorted(context_mass.items(), key=lambda item: (-item[1], opaque(item[0])))[:CONTEXT_N])
        got = sorted(exported[name], key=lambda x: int(x["rank"]))
        checks.add(f"panel:{name}", [x["host"] for x in got] == list(panel) and
                   all(x["host_id"] == opaque(x["host"]) for x in got))
        out[name] = panel, context_panel
    return out


def ppmi(events, panel, context_panel):
    counts, mass, global_counts = defaultdict(Counter), Counter(), Counter()
    for row in events:
        if row["host"] not in panel:
            continue
        total = sum(row["context"].values())
        for target_id, count in row["context"].items():
            dim = target_id if target_id in context_panel else "__OTHER__"
            weight = count / total
            counts[row["host"]][dim] += weight
            global_counts[dim] += weight
        mass[row["host"]] += 1
    dims, global_total, vectors = tuple(sorted(set(context_panel) | {"__OTHER__"}, key=opaque)), sum(global_counts.values()), []
    for host in panel:
        vector = np.zeros(len(dims))
        if mass[host] and global_total:
            for j, dim in enumerate(dims):
                if counts[host][dim] and global_counts[dim]:
                    vector[j] = max(0, math.log2((counts[host][dim] / mass[host]) / (global_counts[dim] / global_total)))
        norm = float(np.linalg.norm(vector))
        vectors.append(vector / norm if norm else vector)
    return np.stack(vectors)


def similarity(events, panel, context_panel):
    matrix = ppmi(events, panel, context_panel)
    return matrix @ matrix.T


def upper(matrix, mapping=None):
    if mapping is not None:
        matrix = matrix[np.ix_(mapping, mapping)]
    return np.array([matrix[i, j] for i in range(PANEL_N) for j in range(i + 1, PANEL_N)], dtype=float)


def correlation(a, b):
    if np.std(a) < 1e-15 or np.std(b) < 1e-15:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def random_mapping(rng):
    mapping = list(range(PANEL_N))
    for lo, hi in BLOCKS:
        block = mapping[lo:hi]
        rng.shuffle(block)
        mapping[lo:hi] = block
    return mapping


def verify_geometry(contexts, panels, checks):
    exported = {(x["test"], x["stratum"]): x for x in tsv(GEOMETRY)}
    null_table = tsv(GEOMETRY_NULL)
    observed, nulls = {}, {}
    for name in STRATA:
        panel, cpanel = panels[name]
        events = contexts[name]["WHOLE_LINE"]
        left = similarity([x for x in events if x["half"] == 0], panel, cpanel)
        right = similarity([x for x in events if x["half"] == 1], panel, cpanel)
        observed[name] = correlation(upper(left), upper(right))
        rng = random.Random(seed("GDT167_GEOMETRY_" + name))
        nulls[name] = [correlation(upper(left), upper(right, random_mapping(rng))) for _ in range(WORLDS)]
        checks.add(f"geometry_null:{name}", all(close(row[f"{name}_correlation"], nulls[name][i]) for i, row in enumerate(null_table)))
    means = {name: sum(values) / WORLDS for name, values in nulls.items()}
    max_values = [max(nulls[name][world] - means[name] for name in STRATA) for world in range(WORLDS)]
    checks.add("geometry_max5", all(close(row["max5_null_centered"], max_values[i]) for i, row in enumerate(null_table)))
    for name in STRATA:
        got = exported["FOLIO_HALF_STABILITY", name]
        local_p = (1 + sum(x >= observed[name] - 1e-12 for x in nulls[name])) / (WORLDS + 1)
        max_p = (1 + sum(x >= observed[name] - means[name] - 1e-12 for x in max_values)) / (WORLDS + 1)
        checks.add(f"geometry_summary:{name}", close(got["correlation"], observed[name]) and close(got["null_mean"], means[name]) and
                   close(got["local_p"], local_p) and close(got["max5_p"], max_p))
    name = "HERBAL_B"
    panel, cpanel = panels[name]
    events = contexts[name]["WHOLE_LINE"]
    left = similarity([x for x in events if x["hand"] == "2"], panel, cpanel)
    right = similarity([x for x in events if x["hand"] in ("3", "5")], panel, cpanel)
    observed_hand = correlation(upper(left), upper(right))
    rng = random.Random(seed("GDT167_GEOMETRY_HERBAL_B_HAND"))
    hand_null = [correlation(upper(left), upper(right, random_mapping(rng))) for _ in range(WORLDS)]
    got = exported["HAND2_VS_HAND3_5", name]
    checks.add("herbal_b_hand_geometry", close(got["correlation"], observed_hand) and close(got["null_mean"], sum(hand_null) / WORLDS))
    return exported


def signatures(events, panel):
    occurrences, contexts, positions, line_sizes = Counter(), defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for row in events:
        if row["host"] not in panel:
            continue
        occurrences[row["host"]] += 1
        positions[row["host"]][row["position_quartile"]] += 1
        line_sizes[row["host"]][row["line_count_bin"]] += 1
        mass = sum(row["context"].values())
        for target_id, count in row["context"].items():
            contexts[row["host"]][target_id] += count / mass
    rows = []
    for host in panel:
        n = occurrences[host]
        values = sorted(contexts[host].values(), reverse=True)
        total = sum(values)
        probabilities = [x / total for x in values] if total else []
        entropy = -sum(x * math.log(x) for x in probabilities if x > 0) / (math.log(len(probabilities)) if len(probabilities) > 1 else 1)
        concentration = lambda k: sum(values[:k]) / total if total else 0
        vector = [math.log1p(n) / math.log1p(max(1, len(events))), entropy, concentration(1), concentration(3),
                  concentration(5), contexts[host][host] / total if total else 0]
        vector += [positions[host][f"Q{i}"] / n if n else 0 for i in range(4)]
        vector += [line_sizes[host][label] / n if n else 0 for label in ("2", "3", "4", "5_7", "8P")]
        rows.append(vector)
    matrix = np.array(rows, dtype=float)
    mean, sd = matrix.mean(axis=0), matrix.std(axis=0)
    sd[sd < 1e-12] = 1.0
    return (matrix - mean) / sd


def hungarian(cost):
    n = len(cost)
    u, v, p, way = [0.0] * (n + 1), [0.0] * (n + 1), [0] * (n + 1), [0] * (n + 1)
    for i in range(1, n + 1):
        p[0], j0, minimum, used = i, 0, [float("inf")] * (n + 1), [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], float("inf"), 0
            for j in range(1, n + 1):
                if not used[j]:
                    current = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if current < minimum[j] - 1e-15:
                        minimum[j], way[j] = current, j0
                    if minimum[j] < delta - 1e-15:
                        delta, j1 = minimum[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minimum[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    answer = [0] * n
    for j in range(1, n + 1):
        answer[p[j] - 1] = j - 1
    return answer


def alignment(source, target):
    mapping = [0] * PANEL_N
    for lo, hi in BLOCKS:
        costs = ((source[lo:hi, None, :] - target[None, lo:hi, :]) ** 2).sum(axis=2).tolist()
        assignment = hungarian(costs)
        for i, j in enumerate(assignment):
            mapping[lo + i] = lo + j
    return mapping


def verify_alignment(contexts, panels, checks):
    fold_export = {(x["stratum_a"], x["stratum_b"], int(x["train_half"])): x for x in tsv(ALIGNMENT) if x["row_type"] == "FOLD"}
    summaries = {(x["stratum_a"], x["stratum_b"]): x for x in tsv(ALIGNMENT) if x["row_type"] in ("PAIR_SUMMARY", "GLOBAL_SUMMARY")}
    mapping_export = defaultdict(list)
    for row in tsv(MAPPINGS):
        mapping_export[row["stratum_a"], row["stratum_b"], int(row["train_half"])].append(row)
    pairs, observed, nulls = list(itertools.combinations(STRATA, 2)), {}, {}
    for pair in pairs:
        fold_observed, fold_null = [], []
        for training_half in (0, 1):
            test_half = 1 - training_half
            pa, ca = panels[pair[0]]
            pb, cb = panels[pair[1]]
            ea, eb = contexts[pair[0]]["WHOLE_LINE"], contexts[pair[1]]["WHOLE_LINE"]
            sa = signatures([x for x in ea if x["half"] == training_half], pa)
            sb = signatures([x for x in eb if x["half"] == training_half], pb)
            mapping = alignment(sa, sb)
            got_map = sorted(mapping_export[pair[0], pair[1], training_half], key=lambda x: int(x["rank_a"]))
            checks.add(f"alignment_mapping:{pair[0]}:{pair[1]}:{training_half}", [int(x["rank_b"]) for x in got_map] == mapping)
            ga = similarity([x for x in ea if x["half"] == test_half], pa, ca)
            gb = similarity([x for x in eb if x["half"] == test_half], pb, cb)
            value = correlation(upper(ga), upper(gb, mapping))
            fold_observed.append(value)
            checks.add(f"alignment_fold:{pair[0]}:{pair[1]}:{training_half}", close(fold_export[pair + (training_half,)]["correlation"], value))
            rng = random.Random(seed("GDT167_ALIGN_" + "|".join(map(str, pair + (training_half,)))))
            fold_null.append([correlation(upper(ga), upper(gb, random_mapping(rng))) for _ in range(WORLDS)])
        observed[pair] = sum(fold_observed) / 2
        nulls[pair] = [(fold_null[0][i] + fold_null[1][i]) / 2 for i in range(WORLDS)]
    null_table = tsv(ALIGNMENT_NULL)
    for pair in pairs:
        field = f"{pair[0]}__{pair[1]}_mean_correlation"
        checks.add(f"alignment_null:{pair[0]}:{pair[1]}", all(close(row[field], nulls[pair][i]) for i, row in enumerate(null_table)))
    means = {pair: sum(values) / WORLDS for pair, values in nulls.items()}
    max_values = [max(nulls[pair][i] - means[pair] for pair in pairs) for i in range(WORLDS)]
    checks.add("alignment_max10", all(close(row["max10_null_centered"], max_values[i]) for i, row in enumerate(null_table)))
    for pair in pairs:
        got = summaries[pair]
        local_p = (1 + sum(x >= observed[pair] - 1e-12 for x in nulls[pair])) / (WORLDS + 1)
        max_p = (1 + sum(x >= observed[pair] - means[pair] - 1e-12 for x in max_values)) / (WORLDS + 1)
        checks.add(f"alignment_summary:{pair[0]}:{pair[1]}", close(got["mean_correlation"], observed[pair]) and
                   close(got["null_mean"], means[pair]) and close(got["local_p"], local_p) and close(got["max10_p"], max_p))
    global_observed = sum(observed.values()) / len(pairs)
    global_null = [sum(nulls[pair][i] for pair in pairs) / len(pairs) for i in range(WORLDS)]
    global_p = (1 + sum(x >= global_observed - 1e-12 for x in global_null)) / (WORLDS + 1)
    got = summaries["ALL_FIVE", "ALL_TEN_PAIRS"]
    checks.add("alignment_global", close(got["mean_correlation"], global_observed) and
               close(got["null_mean"], sum(global_null) / WORLDS) and close(got["local_p"], global_p) and
               all(close(row["global_mean_correlation"], global_null[i]) for i, row in enumerate(null_table)))
    return observed, global_observed, global_p


def main():
    checks = Checks()
    result = json.loads(RESULT.read_text())
    digest = result.pop("result_content_sha256")
    checks.add("result_content_hash", csha(result) == digest)
    result["result_content_sha256"] = digest
    checks.add("schema", result["schema"] == "GDT167_REGISTER_CONDITIONED_HOST_CODEBOOK_RESULT_V1")
    checks.add("design_frozen", json.loads(DESIGN.read_text())["status"] == "FROZEN_BEFORE_SCORING")
    for kind in ("inputs", "implementation", "outputs", "documents"):
        for name, expected in result[kind].items():
            checks.add(f"hash:{kind}:{name}", sha(R / name) == expected)
    rows, by, contexts = rebuild_source(checks)
    artifacts, aggregates = refit_codebooks(contexts, checks)
    code_summary = verify_codebook_nulls(contexts, artifacts, aggregates, checks)
    panels = select_panels(by, contexts, checks)
    geometry = verify_geometry(contexts, panels, checks)
    pair_observed, global_observed, global_p = verify_alignment(contexts, panels, checks)
    geometry_pass = {name for name in STRATA if float(geometry["FOLIO_HALF_STABILITY", name]["correlation"]) > 0 and
                     float(geometry["FOLIO_HALF_STABILITY", name]["max5_p"]) <= .05}
    codebook_pass = []
    for name in STRATA:
        candidates = [code_summary[name, mode, "HELD_FOLIO"] for mode in MODES]
        if name in geometry_pass and any(float(x["gain_bits"]) > 0 and int(x["positive_folds"]) / int(x["folds"]) >= .6 and
                                         float(x["max10_p"]) <= .05 for x in candidates):
            codebook_pass.append(name)
    pair_rows = [x for x in tsv(ALIGNMENT) if x["row_type"] == "PAIR_SUMMARY"]
    positive = [x for x in pair_rows if float(x["mean_correlation"]) > 0]
    corrected = [x for x in positive if float(x["max10_p"]) <= .05]
    covered = {name for row in corrected for name in (row["stratum_a"], row["stratum_b"])}
    common = global_p <= .05 and len(positive) >= 8 and len(corrected) >= 3 and covered == set(STRATA)
    if len(codebook_pass) >= 3 and common:
        status = "REGISTER_CODEBOOKS_WITH_COMMON_REBOUND_ALIGNMENT"
    elif len(codebook_pass) >= 3:
        status = "REGISTER_SPECIFIC_CODEBOOKS_WITHOUT_COMMON_ALIGNMENT"
    elif len(geometry_pass) >= 3 or common:
        status = "REGISTER_GEOMETRY_STABLE_BUT_CODEBOOK_PREDICTION_NEGATIVE"
    else:
        status = "NO_STABLE_REGISTER_CODEBOOK_OR_ALIGNMENT"
    checks.add("decision", result["status"] == status == "NO_STABLE_REGISTER_CODEBOOK_OR_ALIGNMENT")
    checks.add("decision_codebooks", result["codebook_supported_strata"] == codebook_pass == [])
    checks.add("decision_geometry", result["geometry_stable_strata"] == sorted(geometry_pass) == [])
    checks.add("decision_alignment", close(result["alignment"]["global_mean_correlation"], global_observed) and
               close(result["alignment"]["global_p"], global_p) and result["alignment"]["common_rebound_gate"] == common is False)
    checks.add("f84_result_flags", all(value is False for value in result["f84r"].values()))
    validation = {
        "schema": "GDT167_REGISTER_CONDITIONED_HOST_CODEBOOK_VALIDATION_V1",
        "status": f"PASS_{len(checks.rows)}_CHECK_INDEPENDENT_FULL_RECONSTRUCTION",
        "checks": len(checks.rows),
        "check_manifest_sha256": csha(checks.rows),
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "reconstructed": {
            "powered_groups": len(rows), "registers": len(STRATA), "codebook_null_worlds": 10 * WORLDS,
            "geometry_null_worlds": 5 * WORLDS, "alignment_null_worlds": 10 * WORLDS,
            "global_alignment_correlation": global_observed, "global_alignment_p": global_p,
        },
        "decision": status,
        "claim_ceiling": result["claim_ceiling"],
        "f84r": {"opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
    }
    validation["validation_content_sha256"] = csha(validation)
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"], "decision": status,
                      "alignment": global_observed, "p": global_p}, sort_keys=True))


if __name__ == "__main__":
    main()
