#!/usr/bin/env python3
"""GDT126: compare within-record and cross-star adjacent line similarity."""
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
METHOD = ROOT / "GDT126_Q20_RECORD_BOUNDARY_RESET_METHOD.md"
REPORT = ROOT / "GDT126_Q20_RECORD_BOUNDARY_RESET_REPORT.md"
INVENTORY = ROOT / "gdt126_q20_record_boundary_inventory.tsv"
SCORES = ROOT / "gdt126_q20_record_boundary_scores.tsv"
FOLDS = ROOT / "gdt126_q20_record_boundary_folds.tsv"
NULL = ROOT / "gdt126_q20_record_boundary_null.tsv"
COUNTER = ROOT / "gdt126_q20_record_boundary_counterexamples.tsv"
RESULT = ROOT / "gdt126_result.json"
MODES = ("COMPILER12", "EDGE29", "RAW_CHAR3_HASH32", "HOST_CHAR3_HASH32")
WORLDS = 4096


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def write(path, rows):
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cosine(a, b):
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(a @ b / denominator) if denominator else 0.0


def vector(groups, mode):
    if mode == "COMPILER12":
        return g.compiler_vec(groups)
    if mode == "EDGE29":
        return g.edge_vec(groups)
    if mode == "RAW_CHAR3_HASH32":
        return g.hash_vec(groups, False)
    return g.hash_vec(groups, True)


def build_pairs():
    rows = []
    for edition in g.EDITIONS:
        records = [row for row in g.load_records() if row["edition"] == edition]
        by_page = defaultdict(list)
        for row in records:
            by_page[row["page"]].append(row)
            loci = [row["open_locus"]] + row["body_line_loci"].split("|")
            groups = row["open"] + row["body"]
            lines = [(locus, [item for item in groups if item["locus"] == locus]) for locus in loci]
            for position in range(len(lines) - 1):
                left, right = lines[position], lines[position + 1]
                rows.append({
                    "edition": edition, "page": row["page"], "physical_folio": row["physical_folio"],
                    "star_ordinal_left": row["star_ordinal"], "star_ordinal_right": row["star_ordinal"],
                    "left_locus": left[0], "right_locus": right[0], "boundary_class": "WITHIN_RECORD",
                    "left_groups": len(left[1]), "right_groups": len(right[1]), "left": left[1], "right": right[1],
                })
        for page, page_records in by_page.items():
            ordered = sorted(page_records, key=lambda row: row["star_ordinal"])
            for left_record, right_record in zip(ordered, ordered[1:]):
                if right_record["star_ordinal"] != left_record["star_ordinal"] + 1:
                    continue
                left_locus = left_record["body_line_loci"].split("|")[-1]
                left_groups = [item for item in left_record["body"] if item["locus"] == left_locus]
                right_locus = right_record["open_locus"]
                right_groups = right_record["open"]
                rows.append({
                    "edition": edition, "page": page, "physical_folio": left_record["physical_folio"],
                    "star_ordinal_left": left_record["star_ordinal"], "star_ordinal_right": right_record["star_ordinal"],
                    "left_locus": left_locus, "right_locus": right_locus, "boundary_class": "CROSS_RECORD",
                    "left_groups": len(left_groups), "right_groups": len(right_groups), "left": left_groups, "right": right_groups,
                })
    assert not any(row["page"].startswith("f84r") for row in rows)
    return rows


def residualize(rows, values):
    pages = sorted({row["page"] for row in rows})
    page_index = {page: index for index, page in enumerate(pages[1:])}
    x = np.zeros((len(rows), 5 + len(pages) - 1))
    for i, row in enumerate(rows):
        left, right = row["left_groups"], row["right_groups"]
        x[i, 0] = 1.0
        x[i, 1] = math.log1p(left)
        x[i, 2] = math.log1p(right)
        x[i, 3] = abs(left - right)
        x[i, 4] = row["star_ordinal_left"] / max(1, max(r["star_ordinal_left"] for r in rows if r["page"] == row["page"]))
        if row["page"] in page_index:
            x[i, 5 + page_index[row["page"]]] = 1.0
    beta = np.linalg.lstsq(x, np.asarray(values), rcond=None)[0]
    return np.asarray(values) - x @ beta


def contrast(rows, residuals, labels=None, keep_folios=None):
    labels = labels if labels is not None else [row["boundary_class"] for row in rows]
    pages = sorted({row["page"] for row in rows if keep_folios is None or row["physical_folio"] in keep_folios})
    effects = []
    for page in pages:
        within = [residuals[i] for i, row in enumerate(rows) if row["page"] == page and labels[i] == "WITHIN_RECORD"]
        cross = [residuals[i] for i, row in enumerate(rows) if row["page"] == page and labels[i] == "CROSS_RECORD"]
        if within and cross:
            effects.append(float(np.mean(within) - np.mean(cross)))
    return float(np.mean(effects)), effects


def permuted_labels(rows, rng):
    labels = [row["boundary_class"] for row in rows]
    strata = defaultdict(list)
    for i, row in enumerate(rows):
        total_bucket = min(5, (row["left_groups"] + row["right_groups"]) // 6)
        strata[(row["page"], total_bucket)].append(i)
    capacity = 0
    for indices in strata.values():
        vals = [labels[i] for i in indices]
        if len(set(vals)) > 1:
            capacity += len(indices)
            rng.shuffle(vals)
            for index, value in zip(indices, vals):
                labels[index] = value
    return labels, capacity


def main():
    all_pairs = build_pairs()
    inventory, scores, fold_rows, null_rows, counterexamples = [], [], [], [], []
    summaries = {}
    for edition in g.EDITIONS:
        rows = [row for row in all_pairs if row["edition"] == edition]
        assert Counter(row["boundary_class"] for row in rows) == {"WITHIN_RECORD": 408, "CROSS_RECORD": 156}
        for row in rows:
            inventory.append({key: value for key, value in row.items() if key not in {"left", "right"}})
        values_by_mode = {mode: [cosine(vector(row["left"], mode), vector(row["right"], mode)) for row in rows] for mode in MODES}
        residuals_by_mode = {mode: residualize(rows, values) for mode, values in values_by_mode.items()}
        observed = {}
        for mode in MODES:
            effect, page_effects = contrast(rows, residuals_by_mode[mode])
            observed[mode] = effect
            for page, page_effect in zip(sorted({row["page"] for row in rows}), page_effects):
                fold_rows.append({"edition": edition, "model": mode, "held_unit": page, "unit_type": "PAGE", "effect": page_effect, "positive_effect": int(page_effect > 0)})
            folios = sorted({row["physical_folio"] for row in rows})
            for held in folios:
                remaining = set(folios) - {held}
                leave_effect, _ = contrast(rows, residuals_by_mode[mode], keep_folios=remaining)
                fold_rows.append({"edition": edition, "model": mode, "held_unit": held, "unit_type": "LEAVE_FOLIO_OUT", "effect": leave_effect, "positive_effect": int(leave_effect > 0)})
                if leave_effect <= 0:
                    counterexamples.append({"edition": edition, "model": mode, "held_folio": held, "leave_folio_effect": leave_effect, "counterexample": "NONPOSITIVE_LEAVE_FOLIO_EFFECT"})
        rng = random.Random(g.seed("GDT126", edition))
        worlds = {mode: [] for mode in MODES}
        capacity = 0
        for _ in range(WORLDS):
            labels, capacity = permuted_labels(rows, rng)
            for mode in MODES:
                effect, _ = contrast(rows, residuals_by_mode[mode], labels=labels)
                worlds[mode].append(effect)
        max_world = [max(worlds[mode][i] for mode in MODES) for i in range(WORLDS)]
        summaries[edition] = {}
        for mode in MODES:
            effect = observed[mode]
            page_rows = [row for row in fold_rows if row["edition"] == edition and row["model"] == mode and row["unit_type"] == "PAGE"]
            leave_rows = [row for row in fold_rows if row["edition"] == edition and row["model"] == mode and row["unit_type"] == "LEAVE_FOLIO_OUT"]
            score = {
                "edition": edition, "model": mode, "adjacent_pairs": len(rows),
                "within_pairs": 408, "cross_pairs": 156, "pages": len(page_rows), "physical_folios": len(leave_rows),
                "permutation_capacity": capacity, "residual_similarity_effect": effect,
                "positive_pages": sum(row["effect"] > 0 for row in page_rows),
                "minimum_leave_folio_effect": min(row["effect"] for row in leave_rows),
                "null_median_effect": float(np.median(worlds[mode])),
                "local_p": (1 + sum(value >= effect - 1e-12 for value in worlds[mode])) / (WORLDS + 1),
                "max_four_p": (1 + sum(value >= effect - 1e-12 for value in max_world)) / (WORLDS + 1),
            }
            scores.append(score)
            summaries[edition][mode] = score
            null_rows.append({
                "edition": edition, "model": mode, "worlds": WORLDS, "true_effect": effect,
                "null_mean": float(np.mean(worlds[mode])), "null_sd": float(np.std(worlds[mode])),
                "null_q95": float(np.quantile(worlds[mode], .95)), "local_p": score["local_p"], "max_four_p": score["max_four_p"],
            })
    primary = summaries["ZL3b"]["COMPILER12"]
    gates = {
        "positive_effect": primary["residual_similarity_effect"] > 0,
        "positive_all_leave_folio": primary["minimum_leave_folio_effect"] > 0,
        "max_four_p_le_005": primary["max_four_p"] <= .05,
        "all_readings_positive": all(summaries[edition]["COMPILER12"]["residual_similarity_effect"] > 0 for edition in g.EDITIONS),
        "beats_string_controls": primary["residual_similarity_effect"] >= max(summaries["ZL3b"][mode]["residual_similarity_effect"] for mode in ("RAW_CHAR3_HASH32", "HOST_CHAR3_HASH32")),
    }
    if all(gates.values()):
        status = "Q20_STAR_BOUNDARY_HAS_COMPILER_RESET"
    elif primary["residual_similarity_effect"] > 0:
        status = "Q20_STAR_BOUNDARY_RESET_WEAK_NONCONFIRMING"
    else:
        status = "Q20_STAR_BOUNDARY_COMPILER_RESET_NOT_SUPPORTED"
    formatted = lambda rows: [{key: f"{value:.12f}" if isinstance(value, float) else value for key, value in row.items()} for row in rows]
    write(INVENTORY, inventory)
    write(SCORES, formatted(scores))
    write(FOLDS, formatted(fold_rows))
    write(NULL, formatted(null_rows))
    write(COUNTER, formatted(counterexamples or [{"counterexample": "NONE"}]))
    report = f'''# GDT126 — Q20 star-boundary record-reset test

Status: **{status}**

The panel contains 408 adjacent line transitions inside records and 156
transitions across successive star-defined records per reading. Positive values
mean greater line-profile similarity inside a record after page and line-length
residualization.

| representation | ZL effect | positive pages | min LOFO | max-4 p | IT effect | RF effect |
|---|---:|---:|---:|---:|---:|---:|
''' + ''.join(
        f"| `{mode}` | {summaries['ZL3b'][mode]['residual_similarity_effect']:+.4f} | "
        f"{summaries['ZL3b'][mode]['positive_pages']}/13 | {summaries['ZL3b'][mode]['minimum_leave_folio_effect']:+.4f} | "
        f"{summaries['ZL3b'][mode]['max_four_p']:.4f} | {summaries['IT2a'][mode]['residual_similarity_effect']:+.4f} | "
        f"{summaries['RF1b'][mode]['residual_similarity_effect']:+.4f} |\n"
        for mode in MODES
    ) + f'''
Registered gates: `{json.dumps(gates, sort_keys=True)}`.

This test concerns the scope of anonymous formal texture. It neither makes the
stars lexical labels nor identifies the content of a record. No bullet meaning,
heading, recipe, semantic role, word, morpheme, POS, sound, language, plaintext,
meaning, or translation is assigned. f84r remained fully sealed.
'''
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "schema": "GDT126_Q20_RECORD_BOUNDARY_RESET_RESULT_V1", "status": status,
        "within_pairs": 408, "cross_pairs": 156, "pages": 13, "physical_folios": 8,
        "worlds": WORLDS, "models": list(MODES), "primary": primary, "gates": gates, "scores": scores,
        "interpretation": "Adjacent-line formal similarity at human-inventoried Q20 star-record boundaries.",
        "claim_ceiling": "Formal record-boundary scope only; no bullet meaning, heading, recipe, semantic role, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("opened", "retained", "queried", "joined", "scored", "targeted", "predicted")},
        "inputs": {"gdt125_result.json": sha(ROOT / "gdt125_result.json"), "gdt117_result.json": sha(ROOT / "gdt117_result.json"), "q20ob001_source_panel.tsv": sha(ROOT / "q20ob001_source_panel.tsv")},
        "implementation": {Path(__file__).name: sha(Path(__file__)), "run_gdt114_q20_record_template_linkage.py": sha(ROOT / "run_gdt114_q20_record_template_linkage.py")},
        "outputs": {path.name: sha(path) for path in (INVENTORY, SCORES, FOLDS, NULL, COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "primary": primary, "gates": gates}, sort_keys=True))


if __name__ == "__main__":
    main()
