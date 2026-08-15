#!/usr/bin/env python3
"""GDT125: test OPEN information after BODY line 1 is already known."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import run_gdt114_q20_record_template_linkage as g

ROOT = Path(__file__).resolve().parent
METHOD = ROOT / "GDT125_Q20_OPEN_INCREMENTAL_RECORD_SELECTOR_METHOD.md"
REPORT = ROOT / "GDT125_Q20_OPEN_INCREMENTAL_RECORD_SELECTOR_REPORT.md"
INVENTORY = ROOT / "gdt125_q20_open_incremental_inventory.tsv"
SCORES = ROOT / "gdt125_q20_open_incremental_scores.tsv"
FOLDS = ROOT / "gdt125_q20_open_incremental_folds.tsv"
NULL = ROOT / "gdt125_q20_open_incremental_null.tsv"
COUNTER = ROOT / "gdt125_q20_open_incremental_counterexamples.tsv"
RESULT = ROOT / "gdt125_result.json"
LAM = 1000.0
WORLDS = 4096
MODES = (
    ("OPEN_COMPILER_AFTER_BODY1", "BODY1_COMPILER", "OPEN_COMPILER", "OPEN"),
    ("BODY1_COMPILER_AFTER_OPEN", "OPEN_COMPILER", "BODY1_COMPILER", "BODY1"),
    ("OPEN_RAW_AFTER_BODY1", "BODY1_COMPILER", "OPEN_RAW", "OPEN"),
    ("BODY1_RAW_AFTER_OPEN", "OPEN_COMPILER", "BODY1_RAW", "BODY1"),
    ("OPEN_EDGE_AFTER_BODY1", "BODY1_COMPILER", "OPEN_EDGE", "OPEN"),
    ("BODY1_EDGE_AFTER_OPEN", "OPEN_COMPILER", "BODY1_EDGE", "BODY1"),
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def write_tsv(path, rows):
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_records():
    records = []
    for row in g.load_records():
        loci = row["body_line_loci"].split("|")
        if len(loci) < 2:
            continue
        body1 = [group for group in row["body"] if group["locus"] == loci[0]]
        tail = [group for group in row["body"] if group["locus"] in set(loci[1:])]
        assert body1 and tail
        records.append({**row, "body1": body1, "tail": tail})
    assert len(records) == 135 * 3
    assert not any(row["page"].startswith("f84r") for row in records)
    return records


def local_target_mean(records, index):
    peers = [g.compiler_vec(row["tail"]) for j, row in enumerate(records) if j != index and row["page"] == records[index]["page"]]
    return np.mean(peers, axis=0) if peers else np.zeros(12)


def nuisance(records):
    page_counts = Counter(row["page"] for row in records)
    output = []
    for i, row in enumerate(records):
        ordinal = row["star_ordinal"] / max(1, page_counts[row["page"]])
        shape = np.array([
            row["record_line_count"], len(row["open"]), len(row["body1"]), len(row["tail"]),
            row["open_member_count"], row["body_member_count"],
            float(row["page"].endswith("v")), ordinal,
        ])
        output.append(np.r_[shape, local_target_mean(records, i)])
    return np.vstack(output)


def channel(row, name):
    groups = row["open"] if name.startswith("OPEN_") else row["body1"]
    if name.endswith("COMPILER"):
        return g.compiler_vec(groups)
    if name.endswith("RAW"):
        return g.hash_vec(groups, False)
    if name.endswith("EDGE"):
        return g.edge_vec(groups)
    raise ValueError(name)


def fit_mode(records, name, base_name, add_name, source_kind):
    xn = nuisance(records)
    xb = np.vstack([channel(row, base_name) for row in records])
    xa = np.vstack([channel(row, add_name) for row in records])
    y = np.vstack([g.compiler_vec(row["tail"]) for row in records])
    folds, cache = [], {}
    for held in sorted({row["physical_folio"] for row in records}):
        train = [i for i, row in enumerate(records) if row["physical_folio"] != held]
        test = [i for i, row in enumerate(records) if row["physical_folio"] == held]
        xntr, xnte, _, _ = g.standardize(xn[train], xn[test])
        xbtr, xbte, _, _ = g.standardize(xb[train], xb[test])
        xatr, xate, amu, asd = g.standardize(xa[train], xa[test])
        ytr, yte, _, _ = g.standardize(y[train], y[test])
        fixed_train = np.c_[xntr, xbtr]
        fixed_test = np.c_[xnte, xbte]
        b0 = g.ridge_fit(fixed_train, ytr, LAM)
        p0 = g.ridge_pred(fixed_test, b0)
        b1 = g.ridge_fit(np.c_[fixed_train, xatr], ytr, LAM)
        p1 = g.ridge_pred(np.c_[fixed_test, xate], b1)
        gain = g.pseudo_bits(yte, p0, p1)
        folds.append({
            "edition": records[0]["edition"], "model": name, "held_folio": held,
            "held_records": len(test), "pseudo_gain_bits": gain, "positive_gain": int(gain > 0),
        })
        cache[held] = {"test": test, "fixed": fixed_test, "y": yte, "p0": p0, "b1": b1, "amu": amu, "asd": asd}
    return folds, cache, xa, source_kind


def assignment(records, cache, source_kind, rng):
    assignments, capacity = {}, 0
    for held, cell in cache.items():
        test = cell["test"]
        strata = defaultdict(list)
        for position, index in enumerate(test):
            row = records[index]
            source_len = len(row["open"]) if source_kind == "OPEN" else len(row["body1"])
            strata[(row["page"], source_len)].append(position)
        perm = list(range(len(test)))
        for positions in strata.values():
            if len(positions) > 1:
                capacity += len(positions)
                shuffled = positions[:]
                rng.shuffle(shuffled)
                for source, target in zip(positions, shuffled):
                    perm[source] = target
        assignments[held] = perm
    return assignments, capacity


def main():
    all_records = build_records()
    inventory, fold_rows, score_rows, null_rows, counterexamples = [], [], [], [], []
    edition_summary = {}
    for edition in g.EDITIONS:
        records = [row for row in all_records if row["edition"] == edition]
        assert len(records) == 135
        for row in records:
            inventory.append({
                "unit_id": row["unit_id"], "edition": edition, "page": row["page"],
                "physical_folio": row["physical_folio"], "star_ordinal": row["star_ordinal"],
                "open_locus": row["open_locus"], "body1_locus": row["body_line_loci"].split("|")[0],
                "tail_loci": "|".join(row["body_line_loci"].split("|")[1:]),
                "open_groups": len(row["open"]), "body1_groups": len(row["body1"]),
                "tail_groups": len(row["tail"]),
                "open_compiler_sha256": csha(g.compiler_vec(row["open"]).tolist()),
                "body1_compiler_sha256": csha(g.compiler_vec(row["body1"]).tolist()),
                "tail_compiler_sha256": csha(g.compiler_vec(row["tail"]).tolist()),
            })
        models = []
        true = {}
        for spec in MODES:
            folds, cache, add, source_kind = fit_mode(records, *spec)
            models.append((spec, cache, add, source_kind))
            fold_rows.extend(folds)
            true[spec[0]] = sum(row["pseudo_gain_bits"] for row in folds)
            for row in sorted(folds, key=lambda value: value["pseudo_gain_bits"])[:2]:
                counterexamples.append({**row, "counterexample": "WORST_INCREMENTAL_HELD_FOLIO"})
        worlds = {spec[0]: [] for spec in MODES}
        capacities = {}
        rngs = {spec[0]: random.Random(g.seed("GDT125", edition, spec[0])) for spec in MODES}
        for world_index in range(WORLDS):
            for spec, cache, add, source_kind in models:
                name = spec[0]
                assign, capacity = assignment(records, cache, source_kind, rngs[name])
                capacities[name] = capacity
                total = 0.0
                for held, cell in cache.items():
                    raw = add[cell["test"]][assign[held]]
                    standardized = (raw - cell["amu"]) / cell["asd"]
                    pred = g.ridge_pred(np.c_[cell["fixed"], standardized], cell["b1"])
                    total += g.pseudo_bits(cell["y"], cell["p0"], pred)
                worlds[name].append(total)
        max_world = [max(worlds[name][i] for name, *_ in MODES) for i in range(WORLDS)]
        edition_summary[edition] = {}
        for name, base, added, source_kind in MODES:
            folds = [row for row in fold_rows if row["edition"] == edition and row["model"] == name]
            observed = true[name]
            local_p = (1 + sum(value >= observed - 1e-12 for value in worlds[name])) / (WORLDS + 1)
            max_p = (1 + sum(value >= observed - 1e-12 for value in max_world)) / (WORLDS + 1)
            score = {
                "edition": edition, "model": name, "baseline_channel": base, "added_channel": added,
                "records": len(records), "held_folios": 8, "swappable_records": capacities[name],
                "pseudo_gain_bits": observed, "selector_paid_gain_bits": observed - math.log2(len(MODES)),
                "positive_folios": sum(row["pseudo_gain_bits"] > 0 for row in folds),
                "null_median_bits": float(np.median(worlds[name])), "local_p": local_p, "max_six_p": max_p,
            }
            score_rows.append(score)
            edition_summary[edition][name] = score
            null_rows.append({
                "edition": edition, "model": name, "worlds": WORLDS, "true_gain_bits": observed,
                "null_mean_bits": float(np.mean(worlds[name])), "null_sd_bits": float(np.std(worlds[name])),
                "null_q95_bits": float(np.quantile(worlds[name], .95)),
                "inclusive_local_p": local_p, "inclusive_max_six_p": max_p,
            })
    primary = edition_summary["ZL3b"]["OPEN_COMPILER_AFTER_BODY1"]
    reverse = edition_summary["ZL3b"]["BODY1_COMPILER_AFTER_OPEN"]
    gates = {
        "selector_paid_positive": primary["selector_paid_gain_bits"] > 0,
        "six_of_eight_positive_folios": primary["positive_folios"] >= 6,
        "max_six_p_le_005": primary["max_six_p"] <= .05,
        "all_readings_positive": all(edition_summary[e]["OPEN_COMPILER_AFTER_BODY1"]["pseudo_gain_bits"] > 0 for e in g.EDITIONS),
    }
    if all(gates.values()):
        status = "Q20_OPEN_RETAINS_INCREMENTAL_RECORD_SELECTOR_SIGNAL"
    elif reverse["pseudo_gain_bits"] > primary["pseudo_gain_bits"]:
        status = "Q20_FIRST_BODY_EXPLAINS_RECORD_SETPOINT"
    else:
        status = "Q20_OPEN_INCREMENTAL_SIGNAL_WEAK_OR_UNSTABLE"
    formatted = lambda rows: [{key: f"{value:.12f}" if isinstance(value, float) else value for key, value in row.items()} for row in rows]
    write_tsv(INVENTORY, inventory)
    write_tsv(SCORES, formatted(score_rows))
    write_tsv(FOLDS, formatted(fold_rows))
    write_tsv(NULL, formatted(null_rows))
    write_tsv(COUNTER, formatted(counterexamples))
    report = f'''# GDT125 — Q20 OPEN incremental record-selector test

Status: **{status}**

The primary test asks whether OPEN compiler proportions predict BODY lines two
and later after BODY line one is already supplied. It gains
{primary['pseudo_gain_bits']:+.3f} pseudo-bits ({primary['positive_folios']}/8
positive folios), selector-paid {primary['selector_paid_gain_bits']:+.3f}, with
local/max-six p={primary['local_p']:.4f}/{primary['max_six_p']:.4f}. The reverse
increment—BODY line one after OPEN—is {reverse['pseudo_gain_bits']:+.3f} bits.

| model | ZL gain | positive folios | max-6 p | IT gain | RF gain |
|---|---:|---:|---:|---:|---:|
''' + ''.join(
        f"| `{name}` | {edition_summary['ZL3b'][name]['pseudo_gain_bits']:+.3f} | "
        f"{edition_summary['ZL3b'][name]['positive_folios']}/8 | {edition_summary['ZL3b'][name]['max_six_p']:.4f} | "
        f"{edition_summary['IT2a'][name]['pseudo_gain_bits']:+.3f} | {edition_summary['RF1b'][name]['pseudo_gain_bits']:+.3f} |\n"
        for name, *_ in MODES
    ) + f'''
Registered gates: `{json.dumps(gates, sort_keys=True)}`.

This separates a persistent first-line selector from adjacent-line texture. It
does not by itself identify a heading or the content selected. No recipe,
semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or
translation is assigned. f84r remained completely sealed and unpredicted.
'''
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "schema": "GDT125_Q20_OPEN_INCREMENTAL_RECORD_SELECTOR_RESULT_V1",
        "status": status, "records": 135, "physical_folios": 8, "worlds": WORLDS,
        "models": [spec[0] for spec in MODES], "primary": primary, "reverse": reverse,
        "gates": gates, "scores": score_rows,
        "interpretation": "Nested held-folio direction test of persistent OPEN information after BODY line one.",
        "claim_ceiling": "Formal record-selector analogy only; no heading, recipe, semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("opened", "retained", "queried", "joined", "scored", "targeted", "predicted")},
        "inputs": {"gdt115_result.json": sha(ROOT / "gdt115_result.json"), "gdt118_result.json": sha(ROOT / "gdt118_result.json"), "q20ob001_source_panel.tsv": sha(ROOT / "q20ob001_source_panel.tsv")},
        "implementation": {Path(__file__).name: sha(Path(__file__)), "run_gdt114_q20_record_template_linkage.py": sha(ROOT / "run_gdt114_q20_record_template_linkage.py")},
        "outputs": {path.name: sha(path) for path in (INVENTORY, SCORES, FOLDS, NULL, COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "primary": primary, "reverse": reverse}, sort_keys=True))


if __name__ == "__main__":
    main()
