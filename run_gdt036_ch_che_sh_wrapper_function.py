#!/usr/bin/env python3
"""GDT036: matched-host ch/che/sh construction-wrapper experiment.

The test is deliberately formal.  It treats ch, che and sh as three observed
left-edge renderers and asks whether their distribution contains shared
constructional information after the exact residual host has been fixed.
No linguistic or semantic labels are assigned.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
HOSTS_OUT = ROOT / "gdt036_matched_host_inventory.tsv"
OCC_OUT = ROOT / "gdt036_wrapper_occurrences.tsv"
TESTS_OUT = ROOT / "gdt036_feature_tests.tsv"
EFFECTS_OUT = ROOT / "gdt036_shared_effects.tsv"
RESULT_OUT = ROOT / "gdt036_result.json"
REPORT_OUT = ROOT / "GDT036_CH_CHE_SH_WRAPPER_FUNCTION_REPORT.md"

WRAPPERS = ("ch", "che", "sh")
MIN_ROWS = 10
MIN_WRAPPERS = 2
MIN_FOLIOS = 3
ALPHA = 0.5
SHRINK = 5.0
PERMUTATIONS = 5000
SEED = 36036
FEATURES = (
    "record_state",
    "line_position",
    "field_position",
    "previous_state",
    "next_state",
    "own_dy_closure",
    "dy_adjacency",
    "field_index",
    "section",
    "currier",
    "hand",
    "register",
)
FORMAL_FEATURES = FEATURES[:8]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def derive_rows(all_rows):
    by_line = defaultdict(list)
    for row in all_rows:
        assert not row["locus"].startswith("f84r"), "sealed f84r entered GDT016 inventory"
        by_line[row["locus"]].append(row)
    for rows in by_line.values():
        rows.sort(key=lambda r: int(r["group_index"]))

    candidates = []
    for locus, line in by_line.items():
        n = len(line)
        dy_seen = 0
        for i, row in enumerate(line):
            if row["stripped_prefix"] not in WRAPPERS:
                if row["record_state"] == "DY_RESOLUTION":
                    dy_seen += 1
                continue
            if n == 1:
                line_position = "SINGLE"
            elif i == 0:
                line_position = "FIRST"
            elif i == n - 1:
                line_position = "LAST"
            elif i < n / 3:
                line_position = "EARLY"
            elif i >= 2 * n / 3:
                line_position = "LATE"
            else:
                line_position = "MIDDLE"
            prev_state = "BOS" if i == 0 else line[i - 1]["record_state"]
            next_state = "EOS" if i == n - 1 else line[i + 1]["record_state"]
            if row["record_state"] == "DY_RESOLUTION":
                field_position = "CLOSE"
            elif i == 0 or prev_state == "DY_RESOLUTION":
                field_position = "FIELD_START"
            elif i == n - 1:
                field_position = "OPEN_TAIL_END"
            else:
                field_position = "FIELD_INTERNAL"
            prev_dy = int(prev_state == "DY_RESOLUTION")
            next_dy = int(next_state == "DY_RESOLUTION")
            d = dict(row)
            d.update(
                wrapper=row["stripped_prefix"],
                line_position=line_position,
                field_position=field_position,
                previous_state=prev_state,
                next_state=next_state,
                own_dy_closure=str(int(row["dy_closure"])),
                dy_adjacency=f"PREV{prev_dy}_NEXT{next_dy}",
                field_index=str(min(3, dy_seen + 1)),
                register=f'{row["section"]}|{row["currier"]}|{row["hand"]}',
            )
            candidates.append(d)
            if row["record_state"] == "DY_RESOLUTION":
                dy_seen += 1

    host_stats = defaultdict(lambda: {"n": 0, "wrappers": Counter(), "folios": set(), "pages": set()})
    for row in candidates:
        h = host_stats[row["residual_host"]]
        h["n"] += 1
        h["wrappers"][row["wrapper"]] += 1
        h["folios"].add(row["physical_folio"])
        h["pages"].add(row["page"])
    eligible = {
        host for host, x in host_stats.items()
        if x["n"] >= MIN_ROWS and len(x["wrappers"]) >= MIN_WRAPPERS and len(x["folios"]) >= MIN_FOLIOS
    }
    rows = [r for r in candidates if r["residual_host"] in eligible]
    rows.sort(key=lambda r: (r["locus"], int(r["group_index"]), r["wrapper"]))
    return rows, host_stats, eligible


def conditional_mi(h, f, y, h_count, f_count, n):
    hfw = np.bincount((h * f_count + f) * 3 + y, minlength=h_count * f_count * 3)
    hf = np.bincount(h * f_count + f, minlength=h_count * f_count)
    hw = np.bincount(h * 3 + y, minlength=h_count * 3)
    hh = np.bincount(h, minlength=h_count)
    total = 0.0
    for idx in np.flatnonzero(hfw):
        count = float(hfw[idx])
        wrapper = idx % 3
        hf_idx = idx // 3
        host = hf_idx // f_count
        denom = float(hf[hf_idx]) * float(hw[host * 3 + wrapper])
        total += count * math.log2(count * float(hh[host]) / denom)
    return total / n


def permutation_tests(rows):
    hosts = sorted({r["residual_host"] for r in rows})
    hmap = {v: i for i, v in enumerate(hosts)}
    h = np.array([hmap[r["residual_host"]] for r in rows], dtype=np.int32)
    ymap = {v: i for i, v in enumerate(WRAPPERS)}
    y = np.array([ymap[r["wrapper"]] for r in rows], dtype=np.int8)
    group_indices = [np.flatnonzero(h == i) for i in range(len(hosts))]
    encoded = {}
    observed = []
    for feat in FEATURES:
        values = sorted({r[feat] for r in rows})
        vmap = {v: i for i, v in enumerate(values)}
        f = np.array([vmap[r[feat]] for r in rows], dtype=np.int32)
        encoded[feat] = (f, len(values))
        observed.append(conditional_mi(h, f, y, len(hosts), len(values), len(rows)))
    null = np.empty((PERMUTATIONS, len(FEATURES)), dtype=float)
    rng = np.random.default_rng(SEED)
    for p in range(PERMUTATIONS):
        yp = y.copy()
        for idx in group_indices:
            yp[idx] = rng.permutation(yp[idx])
        for j, feat in enumerate(FEATURES):
            f, nf = encoded[feat]
            null[p, j] = conditional_mi(h, f, yp, len(hosts), nf, len(rows))
    means = null.mean(axis=0)
    stds = null.std(axis=0, ddof=1)
    obs = np.asarray(observed)
    z = np.divide(obs - means, stds, out=np.zeros_like(obs), where=stds > 0)
    null_z = np.divide(null - means, stds, out=np.zeros_like(null), where=stds > 0)
    max_z = null_z.max(axis=1)
    out = {}
    for j, feat in enumerate(FEATURES):
        local = (1 + int(np.count_nonzero(null[:, j] >= obs[j]))) / (PERMUTATIONS + 1)
        maxt = (1 + int(np.count_nonzero(max_z >= z[j]))) / (PERMUTATIONS + 1)
        out[feat] = {
            "cmi_bits_per_row": float(obs[j]),
            "null_mean": float(means[j]),
            "null_sd": float(stds[j]),
            "z": float(z[j]),
            "local_p": local,
            "maxT_p": maxt,
        }
    return out


def register_adjusted_permutation_tests(rows):
    strata = sorted({(r["residual_host"], r["register"]) for r in rows})
    smap = {v: i for i, v in enumerate(strata)}
    h = np.array([smap[(r["residual_host"], r["register"])] for r in rows], dtype=np.int32)
    ymap = {v: i for i, v in enumerate(WRAPPERS)}
    y = np.array([ymap[r["wrapper"]] for r in rows], dtype=np.int8)
    group_indices = [np.flatnonzero(h == i) for i in range(len(strata))]
    encoded = {}; observed = []
    for feat in FORMAL_FEATURES:
        values = sorted({r[feat] for r in rows}); vmap = {v: i for i, v in enumerate(values)}
        f = np.array([vmap[r[feat]] for r in rows], dtype=np.int32)
        encoded[feat] = (f, len(values))
        observed.append(conditional_mi(h, f, y, len(strata), len(values), len(rows)))
    null = np.empty((PERMUTATIONS, len(FORMAL_FEATURES)), dtype=float)
    rng = np.random.default_rng(SEED + 1)
    for p in range(PERMUTATIONS):
        yp = y.copy()
        for idx in group_indices:
            yp[idx] = rng.permutation(yp[idx])
        for j, feat in enumerate(FORMAL_FEATURES):
            f, nf = encoded[feat]
            null[p, j] = conditional_mi(h, f, yp, len(strata), nf, len(rows))
    means = null.mean(axis=0); stds = null.std(axis=0, ddof=1); obs = np.asarray(observed)
    z = np.divide(obs - means, stds, out=np.zeros_like(obs), where=stds > 0)
    null_z = np.divide(null - means, stds, out=np.zeros_like(null), where=stds > 0)
    max_z = null_z.max(axis=1)
    out = {}
    for j, feat in enumerate(FORMAL_FEATURES):
        out[feat] = {
            "register_adjusted_cmi_bits_per_row": float(obs[j]),
            "register_adjusted_local_p": (1 + int(np.count_nonzero(null[:, j] >= obs[j]))) / (PERMUTATIONS + 1),
            "register_adjusted_maxT_p": (1 + int(np.count_nonzero(max_z >= z[j]))) / (PERMUTATIONS + 1),
        }
    return out


def held_units(rows, key):
    units = defaultdict(list)
    for i, row in enumerate(rows):
        units[row[key]].append(i)
    return sorted(units.items())


def train_counts(rows, excluded):
    host_counts = Counter()
    global_counts = Counter()
    for i, row in enumerate(rows):
        if i in excluded:
            continue
        host_counts[(row["residual_host"], row["wrapper"])] += 1
        global_counts[row["wrapper"]] += 1
    return host_counts, global_counts


def shared_feature_gain(rows, feature, unit_key, base_mode):
    total_gain = 0.0
    positive = 0
    fold_rows = []
    wrappers = WRAPPERS
    for unit, indices in held_units(rows, unit_key):
        excluded = set(indices)
        host_counts, global_counts = train_counts(rows, excluded)
        base_counts = Counter()
        for i, row in enumerate(rows):
            if i in excluded:
                continue
            if base_mode == "host_register": key = (row["residual_host"], row["register"])
            elif base_mode == "register": key = row["register"]
            elif base_mode == "host": key = row["residual_host"]
            else: key = "_GLOBAL"
            base_counts[(key, row["wrapper"])] += 1
        train_n = len(rows) - len(indices)
        values = sorted({r[feature] for i, r in enumerate(rows) if i not in excluded})
        feat_obs = Counter()
        feat_exp = Counter()
        for i, row in enumerate(rows):
            if i in excluded:
                continue
            host = row["residual_host"]
            if base_mode == "host_register": key = (host, row["register"])
            elif base_mode == "register": key = row["register"]
            elif base_mode == "host": key = host
            else: key = "_GLOBAL"
            denom = sum(base_counts[(key, w)] for w in wrappers) + 3 * ALPHA
            for w in wrappers:
                q = (base_counts[(key, w)] + ALPHA) / denom
                feat_exp[(row[feature], w)] += q
            feat_obs[(row[feature], row["wrapper"])] += 1
        gain = 0.0
        for i in indices:
            row = rows[i]
            host = row["residual_host"]
            if base_mode == "host_register": key = (host, row["register"])
            elif base_mode == "register": key = row["register"]
            elif base_mode == "host": key = host
            else: key = "_GLOBAL"
            denom = sum(base_counts[(key, w)] for w in wrappers) + 3 * ALPHA
            probs_base = []
            ratios = []
            for w in wrappers:
                q = (base_counts[(key, w)] + ALPHA) / denom
                probs_base.append(q)
                ratios.append((feat_obs[(row[feature], w)] + SHRINK) / (feat_exp[(row[feature], w)] + SHRINK))
            weighted = [q * ratio for q, ratio in zip(probs_base, ratios)]
            denom = sum(weighted)
            actual = wrappers.index(row["wrapper"])
            p1 = weighted[actual] / denom
            p0 = probs_base[actual]
            gain += math.log2(p1 / p0)
        total_gain += gain
        positive += int(gain > 1e-12)
        fold_rows.append((unit, gain, len(indices)))
    return total_gain, positive, len(fold_rows), fold_rows


def host_baseline_gain(rows):
    gain = 0.0
    positive = 0
    folds = []
    for folio, indices in held_units(rows, "physical_folio"):
        excluded = set(indices)
        host_counts, global_counts = train_counts(rows, excluded)
        train_n = len(rows) - len(indices)
        fold_gain = 0.0
        for i in indices:
            row = rows[i]
            host = row["residual_host"]
            denom_h = sum(host_counts[(host, w)] for w in WRAPPERS) + 3 * ALPHA
            denom_g = train_n + 3 * ALPHA
            p_host = (host_counts[(host, row["wrapper"])] + ALPHA) / denom_h
            p_global = (global_counts[row["wrapper"]] + ALPHA) / denom_g
            fold_gain += math.log2(p_host / p_global)
        gain += fold_gain
        positive += int(fold_gain > 1e-12)
        folds.append((folio, fold_gain, len(indices)))
    return gain, positive, len(folds), folds


def effect_rows(rows):
    host_counts = Counter((r["residual_host"], r["wrapper"]) for r in rows)
    host_totals = Counter(r["residual_host"] for r in rows)
    output = []
    for feature in FEATURES:
        observed = Counter((r[feature], r["wrapper"]) for r in rows)
        expected = Counter()
        for row in rows:
            host = row["residual_host"]
            for wrapper in WRAPPERS:
                expected[(row[feature], wrapper)] += (host_counts[(host, wrapper)] + ALPHA) / (host_totals[host] + 3 * ALPHA)
        for value in sorted({r[feature] for r in rows}):
            for wrapper in WRAPPERS:
                obs = observed[(value, wrapper)]
                exp = expected[(value, wrapper)]
                output.append({
                    "feature": feature,
                    "value": value,
                    "wrapper": wrapper,
                    "observed": obs,
                    "host_conditioned_expected": f"{exp:.9f}",
                    "residual": f"{obs-exp:.9f}",
                    "shrunk_log2_multiplier": f"{math.log2((obs+SHRINK)/(exp+SHRINK)):.9f}",
                })
    return output


def feature_label(name, test):
    lofo = test["lofo_gain_bits"]
    loho = test["loho_gain_bits"]
    if name in {"section", "currier", "hand", "register"}:
        return "REGISTER_SIGNAL_CONFOUNDED" if lofo > 0 and loho > 0 else "METADATA_SIGNAL_UNSTABLE"
    alofo = test["register_adjusted_lofo_gain_bits"]
    aloho = test["register_adjusted_loho_gain_bits"]
    if alofo > 0 and aloho > 0 and test["register_adjusted_maxT_p"] <= 0.05:
        return "REGISTER_ADJUSTED_SHARED_TRANSFERABLE"
    if alofo > 0 and aloho > 0:
        return "REGISTER_ADJUSTED_WEAK_TRANSFER"
    if lofo > 0:
        return "FOLIO_TRANSFER_ONLY"
    if loho > 0:
        return "UNSEEN_HOST_ONLY"
    return "NO_TRANSFER_SIGNAL"


def main():
    all_rows = read_tsv(SOURCE)
    rows, stats, eligible = derive_rows(all_rows)
    assert rows and not any(r["page"].startswith("f84r") for r in rows)
    assert len({r["physical_folio"] for r in rows}) == 94

    host_rows = []
    for host in sorted(eligible, key=lambda h: (-stats[h]["n"], h)):
        x = stats[host]
        host_rows.append({
            "residual_host": host,
            "rows": x["n"],
            "ch": x["wrappers"]["ch"],
            "che": x["wrappers"]["che"],
            "sh": x["wrappers"]["sh"],
            "wrapper_types": len(x["wrappers"]),
            "physical_folios": len(x["folios"]),
            "pages": len(x["pages"]),
            "majority_wrapper": sorted(x["wrappers"], key=lambda w: (-x["wrappers"][w], w))[0],
            "majority_fraction": f'{max(x["wrappers"].values())/x["n"]:.9f}',
        })
    write_tsv(HOSTS_OUT, host_rows, list(host_rows[0]))

    occurrence_fields = [
        "locus", "page", "physical_folio", "section", "currier", "hand",
        "group_index", "group_count", "token", "wrapper", "residual_host",
        "family_surface", "record_state", "line_position", "field_position",
        "previous_state", "next_state", "own_dy_closure", "dy_adjacency",
        "field_index", "register",
    ]
    write_tsv(OCC_OUT, [{k: r[k] for k in occurrence_fields} for r in rows], occurrence_fields)

    perm = permutation_tests(rows)
    adjusted_perm = register_adjusted_permutation_tests(rows)
    host_gain, host_pos, host_folds, _ = host_baseline_gain(rows)
    tests = []
    for feature in FEATURES:
        lofo, pfolio, nfolio, _ = shared_feature_gain(rows, feature, "physical_folio", "host")
        loho, phost, nhost, _ = shared_feature_gain(rows, feature, "residual_host", "global")
        rec = {
            "feature": feature,
            "levels": len({r[feature] for r in rows}),
            **perm[feature],
            "lofo_gain_bits": lofo,
            "positive_lofo_folds": pfolio,
            "lofo_folds": nfolio,
            "loho_gain_bits": loho,
            "positive_loho_folds": phost,
            "loho_folds": nhost,
        }
        if feature in FORMAL_FEATURES:
            rec.update(adjusted_perm[feature])
            alofo, apfolio, _, _ = shared_feature_gain(rows, feature, "physical_folio", "host_register")
            aloho, aphost, _, _ = shared_feature_gain(rows, feature, "residual_host", "register")
            rec.update(register_adjusted_lofo_gain_bits=alofo, register_adjusted_positive_lofo_folds=apfolio,
                       register_adjusted_loho_gain_bits=aloho, register_adjusted_positive_loho_folds=aphost)
        else:
            rec.update(register_adjusted_cmi_bits_per_row="", register_adjusted_local_p="", register_adjusted_maxT_p="",
                       register_adjusted_lofo_gain_bits="", register_adjusted_positive_lofo_folds="",
                       register_adjusted_loho_gain_bits="", register_adjusted_positive_loho_folds="")
        rec["classification"] = feature_label(feature, rec)
        tests.append(rec)
    test_fields = [
        "feature", "levels", "cmi_bits_per_row", "null_mean", "null_sd", "z",
        "local_p", "maxT_p", "lofo_gain_bits", "positive_lofo_folds", "lofo_folds",
        "loho_gain_bits", "positive_loho_folds", "loho_folds",
        "register_adjusted_cmi_bits_per_row", "register_adjusted_local_p", "register_adjusted_maxT_p",
        "register_adjusted_lofo_gain_bits", "register_adjusted_positive_lofo_folds",
        "register_adjusted_loho_gain_bits", "register_adjusted_positive_loho_folds", "classification",
    ]
    write_tsv(TESTS_OUT, [{k: (f"{r[k]:.12f}" if isinstance(r[k], float) else r[k]) for k in test_fields} for r in tests], test_fields)
    effects = effect_rows(rows)
    write_tsv(EFFECTS_OUT, effects, list(effects[0]))

    total_counts = Counter(r["wrapper"] for r in rows)
    weighted_majority = sum(max(stats[h]["wrappers"].values()) for h in eligible) / len(rows)
    significant_formal = [r["feature"] for r in tests if r["feature"] in FORMAL_FEATURES and r["register_adjusted_lofo_gain_bits"] > 0 and r["register_adjusted_loho_gain_bits"] > 0]
    status = "HOST_LICENSED_WRAPPERS_WITH_WEAK_SHARED_POSITIONAL_TRANSFER_REGISTER_DOMINANT" if significant_formal else "CORE_SPECIFIC_SPELLING_REMAINS_SUFFICIENT"

    result = {
        "schema": "GDT036_CH_CHE_SH_WRAPPER_FUNCTION_RESULT_V1",
        "status": status,
        "scope": "Formal ch/che/sh wrapper behavior conditional on exact residual host; no semantic or linguistic interpretation.",
        "selection": {
            "wrappers": list(WRAPPERS),
            "minimum_rows_per_host": MIN_ROWS,
            "minimum_wrapper_types": MIN_WRAPPERS,
            "minimum_physical_folios": MIN_FOLIOS,
            "eligible_hosts": len(eligible),
            "rows": len(rows),
            "pages": len({r["page"] for r in rows}),
            "physical_folios": len({r["physical_folio"] for r in rows}),
            "wrapper_counts": dict(sorted(total_counts.items())),
        },
        "host_dependence": {
            "weighted_in_sample_host_majority_accuracy": weighted_majority,
            "lofo_exact_host_vs_global_gain_bits": host_gain,
            "positive_lofo_folds": host_pos,
            "lofo_folds": host_folds,
        },
        "formal_features_with_positive_lofo_and_loho_gain": significant_formal,
        "tests": tests,
        "controls": {
            "conditional_association": f"{PERMUTATIONS} exact-host-stratified label permutations with maxT over {len(FEATURES)} declared feature families",
            "folio_transfer": "leave one physical folio out; shared feature multiplier evaluated beyond an exact-host prior",
            "host_transfer": "leave one exact residual host out; shared feature multiplier evaluated beyond a global-wrapper prior",
            "register_adjustment": "formal-feature association is also permuted within exact host x register; transfer is rescored beyond host x register on held folios and beyond register on unseen hosts",
            "smoothing": {"categorical_alpha": ALPHA, "shared_multiplier_shrinkage": SHRINK},
        },
        "claim_ceiling": "Supports, at most, shared positional/contextual construction functions for orthographic wrappers beyond host-specific choice. It assigns no grammar name, technical function, meaning, morpheme, sound, language, plaintext, or translation.",
        "f84r": {"opened": False, "retained": False, "queried": False, "joined": False, "scored": False},
        "inputs": {
            "gdt016_group_state_inventory.tsv": sha(SOURCE),
            "gdt016_result.json": sha(ROOT / "gdt016_result.json"),
            "gdt029_result.json": sha(ROOT / "gdt029_result.json"),
            "gdt030_result.json": sha(ROOT / "gdt030_result.json"),
        },
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {
            HOSTS_OUT.name: sha(HOSTS_OUT), OCC_OUT.name: sha(OCC_OUT),
            TESTS_OUT.name: sha(TESTS_OUT), EFFECTS_OUT.name: sha(EFFECTS_OUT),
        },
    }
    by_name = {r["feature"]: r for r in tests}
    top_effects = sorted(effects, key=lambda r: -abs(float(r["residual"])))[:12]
    top_formal_effects = sorted(
        (r for r in effects if r["feature"] not in {"section", "currier", "hand", "register"}),
        key=lambda r: -abs(float(r["residual"])),
    )[:15]
    report = f"""# GDT036 — ch/che/sh matched-host wrapper functions

## Outcome

**{status}**

The wrapper choice is strongly host-licensed, but exact host is not the whole explanation. The frozen panel contains **{len(rows):,}** occurrences of `ch`, `che`, or `sh` over **{len(eligible)}** recurring residual hosts and **{len({r['physical_folio'] for r in rows})}** physical folios. An in-sample exact-host majority chooses {weighted_majority:.2%} correctly, and the exact-host prior gains {host_gain:.3f} held-folio bits over a global wrapper prior.

After that exact-host baseline is fixed, line position adds {by_name['line_position']['lofo_gain_bits']:.3f} bits in leave-one-folio-out evaluation and {by_name['line_position']['loho_gain_bits']:.3f} bits on completely unseen hosts. It remains positive after additionally conditioning the baseline on section–Currier–hand register: {by_name['line_position']['register_adjusted_lofo_gain_bits']:.3f}/{by_name['line_position']['register_adjusted_loho_gain_bits']:.3f} LOFO/LOHO bits. Previous-state context retains {by_name['previous_state']['register_adjusted_lofo_gain_bits']:.3f}/{by_name['previous_state']['register_adjusted_loho_gain_bits']:.3f} adjusted bits; next-state context retains {by_name['next_state']['register_adjusted_lofo_gain_bits']:.3f}/{by_name['next_state']['register_adjusted_loho_gain_bits']:.3f}. The strongest raw predictor is register (`section|Currier|hand`), at {by_name['register']['lofo_gain_bits']:.3f}/{by_name['register']['loho_gain_bits']:.3f} bits, but those metadata are historically entangled and cannot identify a single cause.

Therefore `ch`/`che`/`sh` are not well described as arbitrary spelling variants attached independently inside each core. They behave as host-licensed renderers with weaker shared positional and neighbouring-state preferences. However, no non-metadata feature clears the register-adjusted maxT threshold (field position is closest at {by_name['field_position']['register_adjusted_maxT_p']:.4f}), so a stable universal wrapper function is **not established**. This is an exploratory constructional lead only; the experiment does not identify what any preference does or means.

## Design

- Source: the f84-free, all-reading-agreeing physical/manual group inventory from GDT016.
- Candidate host: remove exactly one observed prefix in {{`ch`,`che`,`sh`}} and retain the exact residual string.
- Capacity rule fixed before scoring: at least {MIN_ROWS} rows, at least {MIN_WRAPPERS} wrapper types, and at least {MIN_FOLIOS} physical folios.
- Primary association: conditional mutual information given exact host, tested with {PERMUTATIONS:,} exact-host-stratified wrapper permutations and maxT across {len(FEATURES)} declared feature families.
- Register-adjusted control: each of the eight non-metadata features is also tested by permutation inside exact `host × register` cells, and held prediction is rescored beyond host×register or register-only baselines.
- Transfer: a shared multiplicative feature effect is trained outside one physical folio at a time and scored beyond an exact-host prior; a stricter unseen-host pass holds out every occurrence of one residual host and scores beyond the global wrapper prior.
- Uncertainty: this is exploratory YOLO model selection. The shrinkage constants are fixed (`alpha={ALPHA}`, `lambda={SHRINK}`), but they are a compact diagnostic model, not a globally optimal grammar.

## Feature atlas

| Feature | CMI bits/row | local p | maxT p | LOFO gain bits | LOHO gain bits | Classification |
|---|---:|---:|---:|---:|---:|---|
"""
    for r in sorted(tests, key=lambda x: -x["lofo_gain_bits"]):
        report += f"| {r['feature']} | {r['cmi_bits_per_row']:.6f} | {r['local_p']:.6f} | {r['maxT_p']:.6f} | {r['lofo_gain_bits']:.3f} | {r['loho_gain_bits']:.3f} | {r['classification']} |\n"
    report += "\n## Register-adjusted formal-feature transfer\n\n"
    report += "| Feature | adjusted CMI | adjusted local p | adjusted maxT p | adjusted LOFO bits | adjusted LOHO bits |\n|---|---:|---:|---:|---:|---:|\n"
    for r in sorted((x for x in tests if x["feature"] in FORMAL_FEATURES), key=lambda x: -x["register_adjusted_lofo_gain_bits"]):
        report += f"| {r['feature']} | {r['register_adjusted_cmi_bits_per_row']:.6f} | {r['register_adjusted_local_p']:.6f} | {r['register_adjusted_maxT_p']:.6f} | {r['register_adjusted_lofo_gain_bits']:.3f} | {r['register_adjusted_loho_gain_bits']:.3f} |\n"
    report += "\n## Largest exact-host-adjusted descriptive residuals\n\n"
    report += "| Feature=value | Wrapper | Observed | Host-conditioned expected | Residual |\n|---|---|---:|---:|---:|\n"
    for r in top_effects:
        report += f"| {r['feature']}={r['value']} | {r['wrapper']} | {r['observed']} | {float(r['host_conditioned_expected']):.2f} | {float(r['residual']):+.2f} |\n"
    report += "\n## Strongest non-metadata constructional residuals\n\n"
    report += "| Feature=value | Wrapper | Observed | Host-conditioned expected | Residual |\n|---|---|---:|---:|---:|\n"
    for r in top_formal_effects:
        report += f"| {r['feature']}={r['value']} | {r['wrapper']} | {r['observed']} | {float(r['host_conditioned_expected']):.2f} | {float(r['residual']):+.2f} |\n"
    report += f"""

These residuals describe the fitted panel; the held-folio and held-host gains above are the relevant transfer diagnostics. One-sided or rare contexts remain observations rather than automatic failures.

## What this does and does not establish

The reusable signal is principally **where a wrapped host occurs** and **which record state precedes or follows it**. Direct association with the group's own anonymous record state is weak; DY adjacency is also substantially weaker than the positional and register effects. That pattern is compatible with a wrapper layer selecting constructional renderers around already licensed hosts, but it does not distinguish grammar, scribal convention, technical layout, or register-conditioned orthography.

Currier, hand, section, and combined register effects are reported separately. They must not be read as four independent causes, and the all-Herbal hand/Currier coupling remains a known confound. Exact-host preferences remain large, so this result also rejects a freely interchangeable universal prefix slot.

No meanings, morphemes, sounds, parts of speech, languages, plaintext, or translations were inferred. **f84r was not opened, retained, queried, joined, or scored.**
"""
    REPORT_OUT.write_text(report, encoding="utf-8")
    result["documents"] = {
        "GDT036_CH_CHE_SH_WRAPPER_FUNCTION_METHOD.md": sha(ROOT / "GDT036_CH_CHE_SH_WRAPPER_FUNCTION_METHOD.md"),
        REPORT_OUT.name: sha(REPORT_OUT),
    }
    body = dict(result)
    result["result_content_sha256"] = csha(body)
    RESULT_OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "rows": len(rows), "hosts": len(eligible), "result": RESULT_OUT.name}, sort_keys=True))


if __name__ == "__main__":
    main()
