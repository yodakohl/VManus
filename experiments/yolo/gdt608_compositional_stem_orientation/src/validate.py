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


SRC = Path(__file__).resolve().parent
HERE = SRC.parent
ROOT = find_repo_root(HERE)
G605 = ROOT / "experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts"
G606 = ROOT / "experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts"
OUT = HERE / "artifacts"
ALPHA = 0.5
SEED = 60560620260828
BINARY = ("standalone", "chunk_initial", "chunk_final", "line_initial", "line_final", "paragraph_initial", "paragraph_final")
PRIMARY_BINARY = ("chunk_initial", "chunk_final", "line_initial", "line_final", "paragraph_initial", "paragraph_final")
PRIMARY = ("left", "right") + PRIMARY_BINARY
INITIAL = {"chunk_initial", "line_initial", "paragraph_initial"}
FINAL = {"chunk_final", "line_final", "paragraph_final"}
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


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_tsv(path):
    with Path(path).open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b, tol=1e-10):
    return abs(float(a) - float(b)) <= tol


checks = []
failures = []


def check(name, condition, detail):
    record = {"name": name, "status": "PASS" if condition else "FAIL", "detail": detail}
    checks.append(record)
    if not condition:
        failures.append(record)


def entropy(counter):
    total = sum(counter.values())
    return -sum((value / total) * math.log(value / total) for value in counter.values() if value) if total else 0.0


def js(a, b):
    keys = sorted(set(a) | set(b))
    sa, sb = sum(a.values()), sum(b.values())
    value = 0.0
    for key in keys:
        pa, pb = a.get(key, 0) / sa, b.get(key, 0) / sb
        mean = (pa + pb) / 2
        if pa:
            value += 0.5 * pa * math.log2(pa / mean)
        if pb:
            value += 0.5 * pb * math.log2(pb / mean)
    return value


def ranks(values):
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    output = [0.0] * len(values)
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and ordered[j][1] == ordered[i][1]:
            j += 1
        value = (i + 1 + j) / 2
        for cursor in range(i, j):
            output[ordered[cursor][0]] = value
        i = j
    return output


def corr(x, y):
    x, y = np.asarray(x), np.asarray(y)
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x, y):
    return corr(ranks(x), ranks(y))


def blank():
    return {
        "n": 0,
        "binary": {field: 0 for field in BINARY},
        "left": Counter(), "right": Counter(), "folios": Counter(),
    }


def add(cell, event):
    cell["n"] += 1
    for field in BINARY:
        cell["binary"][field] += event[field]
    cell["left"][event["left"]] += 1
    cell["right"][event["right"]] += 1
    cell["folios"][event["folio"]] += 1


def bp(cell, field):
    return (cell["binary"][field] + ALPHA) / (cell["n"] + 2 * ALPHA)


def cp(cell, field, vocab):
    denom = cell["n"] + ALPHA * len(vocab)
    return {value: (cell[field].get(value, 0) + ALPHA) / denom for value in vocab}


def prediction(model, merged, left, right, stats, global_cell, vocab):
    if model == "SWAPPED":
        left, right = right, left
        model = "DIRECT"
    binary, cats = {}, {}
    if model == "GLOBAL":
        binary = {field: bp(global_cell, field) for field in BINARY}
        cats = {field: cp(global_cell, field, vocab) for field in ("left", "right")}
    elif model == "ATOMIC":
        binary = {field: bp(stats["train"][merged], field) for field in BINARY}
        cats = {field: cp(stats["train"][merged], field, vocab) for field in ("left", "right")}
    else:
        for field in BINARY:
            lp, rp = bp(stats["train"][left], field), bp(stats["train"][right], field)
            binary[field] = lp if field in INITIAL else rp if field in FINAL else math.sqrt(lp * rp)
        cats["left"] = cp(stats["train"][left], "left", vocab)
        cats["right"] = cp(stats["train"][right], "right", vocab)
    return binary, cats


def feature_scores(pred, held, vocab):
    binary, cats = pred
    output = {}
    for field in BINARY:
        yes = held["binary"][field]
        probability = min(1 - 1e-15, max(1e-15, binary[field]))
        output[field] = -(yes * math.log2(probability) + (held["n"] - yes) * math.log2(1 - probability)) / held["n"]
    for field in ("left", "right"):
        output[field] = -sum(count * math.log2(cats[field][value]) for value, count in held[field].items()) / held["n"]
    output["primary"] = statistics.fmean(output[field] for field in PRIMARY)
    return output


def ridge_fit(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mean, scale = x.mean(0), x.std(0)
    scale[scale == 0] = 1
    design = np.column_stack((np.ones(len(x)), (x - mean) / scale))
    penalty = np.eye(design.shape[1])
    penalty[0, 0] = 0
    beta = np.linalg.solve(design.T @ design + penalty, design.T @ y)
    return beta, mean, scale


def logit(value):
    value = min(1 - 1e-12, max(1e-12, value))
    return math.log(value / (1 - value))


def sigmoid(value):
    return 1 / (1 + math.exp(-value))


def main():
    initial_hashes = {str(path.relative_to(ROOT)): sha(path) for path in EXPECTED}
    expected_hashes = {str(path.relative_to(ROOT)): value for path, value in EXPECTED.items()}
    for name, expected in expected_hashes.items():
        check(f"input hash {name}", initial_hashes[name] == expected, initial_hashes[name])

    merges = [{**r, "rank": int(r["rank"])} for r in read_tsv(G605 / "gdt605_bpe_merges.tsv")]
    check("64 registered merges", len(merges) == 64, len(merges))
    check("64 unique outputs", len({r["merged"] for r in merges}) == 64, len({r["merged"] for r in merges}))
    expected_pairs = {"ol": ("o", "l"), "or": ("o", "r"), "ok": ("o", "k"), "ot": ("o", "t"), "dy": ("d", "y"), "aN": ("a", "N")}
    rule = {r["merged"]: (r["left"], r["right"]) for r in merges}
    for unit, pair in expected_pairs.items():
        check(f"nominated merge {unit}", rule.get(unit) == pair, rule.get(unit))

    guarded = read_tsv(G606 / "guarded_rows.tsv")
    check("guarded rows", len(guarded) == 4165, len(guarded))
    check("sealed selectors absent", not any(r["page"].lower().startswith("f84") or r["physical_folio"].lower().startswith("f84") for r in guarded), "absent")
    meta = {}
    active, page_count, paragraphs = {}, Counter(), defaultdict(list)
    for row in guarded:
        page, raw = row["page"], row["ivtff_raw"]
        if "<%>" in raw[:32] or page not in active:
            page_count[page] += 1
            active[page] = f"{page}:p{page_count[page]}"
        pid = active[page]
        paragraphs[pid].append(row["locus"])
        meta[row["locus"]] = {"pid": pid, "hand": row["hand"], "currier": row["language"]}
        if "<$>" in raw:
            active.pop(page, None)
    for pid, loci in paragraphs.items():
        for index, locus in enumerate(loci):
            meta[locus]["index"] = index
            meta[locus]["count"] = len(loci)

    sequences = json.loads((G606 / "unit_sequences.json").read_text())
    inventory = sequences["inventory"]
    check("98-unit inventory", len(inventory) == 98, len(inventory))
    check("train chunks", len(sequences["sequences"]["train"]) == 20336, len(sequences["sequences"]["train"]))
    check("held chunks", len(sequences["sequences"]["held"]) == 9838, len(sequences["sequences"]["held"]))
    events = []
    for split in ("train", "held"):
        by_locus = defaultdict(list)
        for record in sequences["sequences"][split]:
            by_locus[record["locus"]].append(record)
        for locus, chunks in by_locus.items():
            chunks.sort(key=lambda r: int(r["chunk_index"]))
            line_total = sum(len(r["units"]) for r in chunks)
            offset = 0
            for chunk in chunks:
                units = chunk["units"]
                for index, unit in enumerate(units):
                    line_index = offset + index
                    events.append({
                        "split": split, "folio": chunk["physical_folio"], "unit": unit,
                        "left": units[index - 1] if index else "<BOS>",
                        "right": units[index + 1] if index + 1 < len(units) else "<EOS>",
                        "standalone": int(len(units) == 1),
                        "chunk_initial": int(index == 0), "chunk_final": int(index == len(units) - 1),
                        "line_initial": int(line_index == 0), "line_final": int(line_index == line_total - 1),
                        "paragraph_initial": int(meta[locus]["index"] == 0 and line_index == 0),
                        "paragraph_final": int(meta[locus]["index"] == meta[locus]["count"] - 1 and line_index == line_total - 1),
                    })
                offset += len(units)
    check("train events", sum(e["split"] == "train" for e in events) == 43335, sum(e["split"] == "train" for e in events))
    check("held events", sum(e["split"] == "held" for e in events) == 21679, sum(e["split"] == "held" for e in events))
    check("event selector safety inherited", not any(e["folio"].lower().startswith("f84") for e in events), "safe")

    stats = {split: {unit: blank() for unit in inventory} for split in ("train", "held")}
    global_cell = blank()
    for event in events:
        add(stats[event["split"]][event["unit"]], event)
        if event["split"] == "train":
            add(global_cell, event)
    outputs = {r["merged"] for r in merges}
    check("merge output train events", sum(stats["train"][u]["n"] for u in outputs) == 28756, sum(stats["train"][u]["n"] for u in outputs))
    check("merge output held events", sum(stats["held"][u]["n"] for u in outputs) == 14390, sum(stats["held"][u]["n"] for u in outputs))

    vocab = sorted(set(inventory) | {"<BOS>", "<EOS>"})
    all_scores, all_predictions = {}, {}
    for merge in merges:
        unit = merge["merged"]
        all_scores[unit] = {}
        for model in ("GLOBAL", "ATOMIC", "DIRECT", "SWAPPED"):
            pred = prediction(model, unit, merge["left"], merge["right"], stats, global_cell, vocab)
            all_predictions[unit, model] = pred
            all_scores[unit][model] = feature_scores(pred, stats["held"][unit], vocab)
    total = sum(stats["held"][u]["n"] for u in outputs)
    aggregate = {
        model: sum(stats["held"][u]["n"] * all_scores[u][model]["primary"] for u in outputs) / total
        for model in ("GLOBAL", "ATOMIC", "DIRECT", "SWAPPED")
    }
    expected_aggregate = {"GLOBAL": 1.2370399133839813, "ATOMIC": 0.8658858990317139, "DIRECT": 1.0592254284188403, "SWAPPED": 2.0199409052227635}
    for model, expected in expected_aggregate.items():
        check(f"independent aggregate score {model}", close(aggregate[model], expected, 1e-12), aggregate[model])
    check("DIRECT beats GLOBAL types", sum(all_scores[u]["DIRECT"]["primary"] < all_scores[u]["GLOBAL"]["primary"] for u in outputs) == 58, sum(all_scores[u]["DIRECT"]["primary"] < all_scores[u]["GLOBAL"]["primary"] for u in outputs))
    check("DIRECT beats SWAPPED types", sum(all_scores[u]["DIRECT"]["primary"] < all_scores[u]["SWAPPED"]["primary"] for u in outputs) == 63, sum(all_scores[u]["DIRECT"]["primary"] < all_scores[u]["SWAPPED"]["primary"] for u in outputs))
    check("DIRECT beats ATOMIC types", sum(all_scores[u]["DIRECT"]["primary"] < all_scores[u]["ATOMIC"]["primary"] for u in outputs) == 13, sum(all_scores[u]["DIRECT"]["primary"] < all_scores[u]["ATOMIC"]["primary"] for u in outputs))

    expected_rates = {
        ("ol", "chunk_initial"): .4044943820224719, ("ol", "chunk_final"): .5463483146067416,
        ("or", "chunk_initial"): .2504672897196262, ("or", "chunk_final"): .6504672897196262,
        ("ok", "chunk_initial"): .8208, ("ok", "chunk_final"): .0096,
        ("ot", "chunk_initial"): .9201741654571843, ("ot", "chunk_final"): .008708272859216255,
        ("dy", "chunk_initial"): .18137254901960784, ("dy", "chunk_final"): .9362745098039216,
        ("aN", "chunk_initial"): .18705035971223022, ("aN", "chunk_final"): .9766187050359713,
    }
    for (unit, metric), expected in expected_rates.items():
        observed = stats["held"][unit]["binary"][metric] / stats["held"][unit]["n"]
        check(f"nominated held rate {unit}:{metric}", close(observed, expected, 1e-12), observed)

    # Frequency/mobility matched mobile null.
    train_folios = len({e["folio"] for e in events if e["split"] == "train"})
    descriptor = np.asarray([
        (math.log(stats["train"][m["merged"]]["n"]), math.exp(entropy(stats["train"][m["merged"]]["folios"])) / train_folios)
        for m in merges
    ])
    z = (descriptor - descriptor.mean(0)) / descriptor.std(0)
    nearest = {}
    for i, merge in enumerate(merges):
        nearest[merge["merged"]] = [j for _distance, j in sorted((float(np.linalg.norm(z[i] - z[j])), j) for j in range(64) if j != i)[:8]]
    donor_feature = defaultdict(dict)
    for target in merges:
        target_unit = target["merged"]
        for donor in merges:
            pred = prediction("DIRECT", target_unit, donor["left"], donor["right"], stats, global_cell, vocab)
            donor_feature[target_unit][donor["merged"]] = feature_scores(pred, stats["held"][target_unit], vocab)
    rng = random.Random(SEED)
    null = []
    draws = []
    for _ in range(1000):
        current, draw = 0.0, []
        for merge in merges:
            donor_index = rng.choice(nearest[merge["merged"]])
            donor = merges[donor_index]["merged"]
            draw.append(donor)
            current += stats["held"][merge["merged"]]["n"] * donor_feature[merge["merged"]][donor]["primary"]
        null.append(current / total)
        draws.append(draw)
    check("mobile null mean", close(statistics.fmean(null), 1.7061001502997892, 1e-12), statistics.fmean(null))
    check("mobile null sd", close(statistics.stdev(null), 0.08424720415160517, 1e-12), statistics.stdev(null))
    check("mobile null p", (1 + sum(value <= aggregate["DIRECT"] for value in null)) / 1001 == 1/1001, (1 + sum(value <= aggregate["DIRECT"] for value in null)) / 1001)

    # Held physical-folio direction signs.
    folio_cells = defaultdict(lambda: defaultdict(blank))
    for event in events:
        if event["split"] == "held" and event["unit"] in outputs:
            add(folio_cells[event["folio"]][event["unit"]], event)
    folio_rows = []
    for folio, cells in folio_cells.items():
        n = sum(cell["n"] for cell in cells.values())
        values = {}
        for model in ("GLOBAL", "ATOMIC", "DIRECT", "SWAPPED"):
            values[model] = sum(cell["n"] * feature_scores(all_predictions[unit, model], cell, vocab)["primary"] for unit, cell in cells.items()) / n
        folio_rows.append((folio, values))
    check("held folio count", len(folio_rows) == 23, len(folio_rows))
    check("DIRECT beats GLOBAL on every folio", all(v["DIRECT"] < v["GLOBAL"] for _f, v in folio_rows), "23/23")
    check("DIRECT beats SWAPPED on every folio", all(v["DIRECT"] < v["SWAPPED"] for _f, v in folio_rows), "23/23")
    check("ATOMIC beats DIRECT on every folio", all(v["ATOMIC"] < v["DIRECT"] for _f, v in folio_rows), "23/23")

    # Family-side reconstruction and frozen stable set.
    groups = {"left": defaultdict(list), "right": defaultdict(list)}
    for merge in merges:
        groups["left"][merge["left"]].append(merge)
        groups["right"][merge["right"]].append(merge)
    stable = set()
    child_index = {m["merged"]: i for i, m in enumerate(merges)}
    family_observed = {}
    for side in ("left", "right"):
        fields = ("left", "chunk_initial", "line_initial", "paragraph_initial") if side == "left" else ("right", "chunk_final", "line_final", "paragraph_final")
        for stem, children in groups[side].items():
            if len(children) < 3:
                continue
            n = sum(stats["held"][m["merged"]]["n"] for m in children)
            direct = sum(stats["held"][m["merged"]]["n"] * statistics.fmean(all_scores[m["merged"]]["DIRECT"][f] for f in fields) for m in children) / n
            swapped = sum(stats["held"][m["merged"]]["n"] * statistics.fmean(all_scores[m["merged"]]["SWAPPED"][f] for f in fields) for m in children) / n
            positive = sum(statistics.fmean(all_scores[m["merged"]]["SWAPPED"][f] - all_scores[m["merged"]]["DIRECT"][f] for f in fields) > 0 for m in children)
            family_null = []
            for replicate in range(1000):
                value = 0.0
                for child in children:
                    unit = child["merged"]
                    donor = draws[replicate][child_index[unit]]
                    value += stats["held"][unit]["n"] * statistics.fmean(donor_feature[unit][donor][f] for f in fields)
                family_null.append(value / n)
            p = (1 + sum(value <= direct for value in family_null)) / 1001
            family_observed[side, stem] = {"direct": direct, "swapped": swapped, "positive": positive, "children": len(children), "p": p}
            if swapped > direct and positive / len(children) >= .75 and p <= .05:
                stable.add((side, stem))
    expected_stable = {("left", x) for x in ("C", "Ce", "S", "a", "d", "e", "ok", "q")} | {("right", x) for x in ("aN", "al", "dy", "k", "r", "y")}
    check("14 stable stem-side families", stable == expected_stable, sorted(f"{a}:{b}" for a, b in stable))
    check("left o family rejected", ("left", "o") not in stable and family_observed["left", "o"]["positive"] == 5 and close(family_observed["left", "o"]["p"], .08591408591408592, 1e-15), family_observed["left", "o"])
    check("right y family stable", ("right", "y") in stable and family_observed["right", "y"]["positive"] == 12, family_observed["right", "y"])
    check("right dy family stable", ("right", "dy") in stable and family_observed["right", "dy"]["positive"] == 6, family_observed["right", "dy"])

    # Independent W/frequency diagnostic over merge outputs.
    mappings = read_tsv(G606 / "complete_mappings.tsv")
    real = defaultdict(list)
    destroyed = defaultdict(list)
    for row in mappings:
        (real if row["model_kind"] == "real" else destroyed)[row["unit"]].append(row["category"])
    w_real = [sum(x == "W" for x in real[m["merged"]]) / len(real[m["merged"]]) for m in merges]
    w_destroyed = [sum(x == "W" for x in destroyed[m["merged"]]) / len(destroyed[m["merged"]]) for m in merges]
    frequency = [math.log(stats["train"][m["merged"]]["n"]) for m in merges]
    comp_gain = []
    for m in merges:
        local = statistics.fmean(donor_feature[m["merged"]][merges[j]["merged"]]["primary"] for j in nearest[m["merged"]])
        comp_gain.append(local - all_scores[m["merged"]]["DIRECT"]["primary"])
    check("frequency versus real W Spearman", close(spearman(frequency, w_real), .6523128994525839, 1e-12), spearman(frequency, w_real))
    check("composition versus real W Spearman", close(spearman(comp_gain, w_real), .07777942024538148, 1e-12), spearman(comp_gain, w_real))
    check("composition versus destroyed W Spearman", close(spearman(comp_gain, w_destroyed), .23047118608380476, 1e-12), spearman(comp_gain, w_destroyed))

    # Independent LOMO reconstruction for all seven rates.
    lomo_losses = {name: [] for name in ("atomic", "direct", "lomo")}
    lomo_weights = []
    lomo_errors = {name: [] for name in ("atomic", "direct", "lomo")}
    for field in BINARY:
        x, y = [], []
        for merge in merges:
            x.append([
                logit(bp(stats["train"][merge["left"]], field)),
                logit(bp(stats["train"][merge["right"]], field)),
                math.log(stats["train"][merge["left"]]["n"]),
                math.log(stats["train"][merge["right"]]["n"]),
                math.log(stats["train"][merge["merged"]]["n"]),
            ])
            y.append(logit(bp(stats["train"][merge["merged"]], field)))
        for i, merge in enumerate(merges):
            indices = [j for j in range(64) if j != i]
            beta, mean, scale = ridge_fit([x[j] for j in indices], [y[j] for j in indices])
            vector = np.concatenate(([1.0], (np.asarray(x[i]) - mean) / scale))
            lp = sigmoid(float(vector @ beta))
            atomic = bp(stats["train"][merge["merged"]], field)
            left, right = bp(stats["train"][merge["left"]], field), bp(stats["train"][merge["right"]], field)
            direct = left if field in INITIAL else right if field in FINAL else math.sqrt(left * right)
            held = stats["held"][merge["merged"]]
            rate = held["binary"][field] / held["n"]
            for name, probability in (("atomic", atomic), ("direct", direct), ("lomo", lp)):
                loss = -(held["binary"][field] * math.log2(probability) + (held["n"] - held["binary"][field]) * math.log2(1 - probability)) / held["n"]
                if field in PRIMARY_BINARY:
                    lomo_losses[name].append((loss, held["n"]))
                lomo_errors[name].append(abs(rate - probability))
    lomo_summary = {name: sum(loss * n for loss, n in lomo_losses[name]) / sum(n for _loss, n in lomo_losses[name]) for name in lomo_losses}
    for name, expected in {"atomic": .25534164723694525, "direct": .32910678304455454, "lomo": .31594249293475973}.items():
        check(f"independent LOMO edge score {name}", close(lomo_summary[name], expected, 1e-12), lomo_summary[name])
    for name, expected in {"atomic": .022348329514525, "direct": .10101196898469708, "lomo": .07671986487085822}.items():
        observed = statistics.fmean(lomo_errors[name])
        check(f"independent seven-rate MAE {name}", close(observed, expected, 1e-12), observed)

    result = json.loads((OUT / "RESULT.json").read_text())
    check("result decision", result["decision"] == "PARTIAL_COMPOSITIONAL_BACKOFF", result["decision"])
    check("result claim ceiling", "no morphology" in result["claim_ceiling"], result["claim_ceiling"])
    check("result sealed data", result["sealed_data"] == {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"}, result["sealed_data"])

    stable_rows = read_tsv(OUT / "stable_stem_role_summary.tsv")
    check("manual stable role rows", len(stable_rows) == 14, len(stable_rows))
    check("manual stable role set", {(r["side"], r["stem"]) for r in stable_rows} == expected_stable, sorted((r["side"], r["stem"]) for r in stable_rows))
    nominated = read_tsv(OUT / "nominated_pair_verdicts.tsv")
    check("six nominated verdicts", len(nominated) == 6 and {r["merge"].split("=")[-1] for r in nominated} == set(expected_pairs), [r["merge"] for r in nominated])
    counter = read_tsv(OUT / "compositional_counterexamples.tsv")
    check("counterexample table covers standalone and o", {"standalone", "left_o_family", "W_category"} <= {r["scope"] for r in counter}, [r["scope"] for r in counter])

    manifest = json.loads((OUT / "ARTIFACT_MANIFEST.json").read_text())
    check("analysis source hash", manifest["analysis_source_sha256"] == sha(SRC / "analyze.py"), manifest["analysis_source_sha256"])
    for name, expected in manifest["outputs"].items():
        check(f"analysis artifact hash {name}", sha(OUT / name) == expected, sha(OUT / name))
    report = (HERE / "REPORT.md").read_text()
    for phrase in (
        "PARTIAL_COMPOSITIONAL_BACKOFF__ATOMIC_MERGE_IDENTITY_RETAINS_RESIDUAL_ROLE",
        "`o` ist **kein** stabiler linker Stamm",
        "Rechte Komponenten `y`, `dy` und `aN`",
        "linguistische Morphologie",
        "23/23 held Folios",
    ):
        check(f"report phrase {phrase}", phrase in report, phrase)

    final_hashes = {str(path.relative_to(ROOT)): sha(path) for path in EXPECTED}
    check("source hashes unchanged", final_hashes == initial_hashes == expected_hashes, final_hashes)
    artifact_supplemental = (
        "stable_stem_role_summary.tsv", "nominated_pair_verdicts.tsv",
        "compositional_counterexamples.tsv",
    )
    validation = {
        "schema": "gdt608-composition-validation-v1",
        "status": "FAIL" if failures else "PASS",
        "checks_passed": sum(row["status"] == "PASS" for row in checks),
        "checks_failed": len(failures),
        "checks": checks,
        "decision": "PARTIAL_COMPOSITIONAL_BACKOFF__ATOMIC_MERGE_IDENTITY_RETAINS_RESIDUAL_ROLE",
        "claim_ceiling": "formal collapsed-unit composition only; no linguistic morphology, word, sound, language, plaintext, or meaning",
        "sealed_data": {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"},
        "input_hashes": initial_hashes,
        "analysis_manifest_sha256": sha(OUT / "ARTIFACT_MANIFEST.json"),
        "supplemental_hashes": {
            "PREREGISTRATION.md": sha(HERE / "PREREGISTRATION.md"),
            "REPORT.md": sha(HERE / "REPORT.md"),
            **{name: sha(OUT / name) for name in artifact_supplemental},
            "src/analyze.py": sha(SRC / "analyze.py"),
            "src/validate.py": sha(SRC / "validate.py"),
        },
    }
    (OUT / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": validation["status"], "checks_passed": validation["checks_passed"],
        "checks_failed": validation["checks_failed"], "sha256": sha(OUT / "VALIDATION.json"),
    }, indent=2, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
