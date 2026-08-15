#!/usr/bin/env python3
"""GDT135: held-folio section-B adjacent field-architecture transfer."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import multiprocessing as mp
import os
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import run_gdt131_q20_cross_line_field_onset as q
import run_gdt133_raw_surface_transfer_decomposition as d
import run_gdt134_general_adjacent_continuation_transfer as g

ROOT = Path(__file__).resolve().parent
PREDICTION = ROOT / "gdt135_prediction.json"
METHOD = ROOT / "GDT135_SECTION_B_FIELD_ARCHITECTURE_TRANSFER_METHOD.md"
REPORT = ROOT / "GDT135_SECTION_B_FIELD_ARCHITECTURE_TRANSFER_REPORT.md"
INVENTORY = ROOT / "gdt135_section_b_field_architecture_inventory.tsv"
PREDICTIONS = ROOT / "gdt135_section_b_field_architecture_predictions.tsv"
SCORES = ROOT / "gdt135_section_b_field_architecture_scores.tsv"
FOLDS = ROOT / "gdt135_section_b_field_architecture_folds.tsv"
BLOCKS = ROOT / "gdt135_section_b_field_architecture_blocks.tsv"
NULL = ROOT / "gdt135_section_b_field_architecture_null.tsv"
COUNTER = ROOT / "gdt135_section_b_field_architecture_counterexamples.tsv"
RESULT = ROOT / "gdt135_result.json"
MODES = ("COMPILER12", "HOST_CHAR3", "RAW_CHAR3")
WORLDS = 4096
LAM = 1000.0
TARGET_INDEX = tuple(range(15)) + tuple(range(19, 22))
BLOCK_INDEX = {
    "FIRST_WRAPPER8": tuple(range(0, 8)),
    "FIRST_FRAME3": tuple(range(8, 11)),
    "FIRST_RENDERER4": tuple(range(11, 15)),
    "FIELD_CLOSURE3": tuple(range(15, 18)),
}
NULL_CONTEXT = None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def seed(*value):
    return int(hashlib.sha256("|".join(map(str, value)).encode()).hexdigest()[:16], 16)


def write(path, rows):
    fields = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fit(x, y):
    design = np.c_[np.ones(len(x)), x]
    penalty = np.eye(design.shape[1])
    penalty[0, 0] = 0
    return np.linalg.solve(design.T @ design + LAM * penalty, design.T @ y)


def predict(x, coefficient):
    return np.c_[np.ones(len(x)), x] @ coefficient


def standardize_train(train, test):
    mean = train.mean(0)
    scale = train.std(0)
    scale[scale < 1e-8] = 1.0
    return (train - mean) / scale, (test - mean) / scale, mean, scale


def bits(y, reference, model):
    return float((np.square(y - reference).sum() - np.square(y - model).sum()) / (2 * math.log(2)))


def nearest(prediction, classes, top=3):
    ranked = sorted((float(np.square(prediction - vector).sum()), name) for name, vector in classes.items())
    return ranked[0][1], [name for _, name in ranked[:top]]


def architecture(field):
    full, _, first, end = q.architecture(d.cells(field))
    vector = full[list(TARGET_INDEX)]
    return vector, f"{first};END={end}"


def nuisance(rows):
    page_max = defaultdict(int)
    for row in rows:
        page_max[row["page"]] = max(page_max[row["page"]], row["source_line_number"])
    out = []
    for row in rows:
        out.append(
            [
                len(row["groups"]),
                row["member_count"],
                len(row["last"]),
                sum(len(cell["page_host"]) for cell in row["last"]),
                sum(len(cell["token"]) for cell in row["last"]),
                len(row["target"]),
                row["source_line_number"] / max(1, page_max[row["page"]]),
                row["source_line_number"] % 2,
                int(row["page"].endswith("v")),
            ]
        )
    return np.asarray(out, float)


def load_panel():
    target = [row for row in g.external() if row["first_start"] == 0 and row["section"] == "B"]
    with (ROOT / "gdt134_general_continuation_inventory.tsv").open(encoding="utf-8", newline="") as handle:
        frozen = {
            (row["locus"], row["next_locus"])
            for row in csv.DictReader(handle, delimiter="\t")
            if row["primary_continuation_pair"] == "1" and row["section"] == "B"
        }
    assert {(row["locus"], row["next_locus"]) for row in target} == frozen
    assert len(target) == 69 and len({row["physical_folio"] for row in target}) == 9
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in target)
    return target


def prepare(rows):
    target = []
    keys = []
    for row in rows:
        vector, key = architecture(row["target"])
        target.append(vector)
        keys.append(key)
    representations = {mode: [] for mode in MODES}
    for row in rows:
        primitive = d.primitive(row["last"])
        for mode in MODES:
            representations[mode].append(primitive[mode])
    return nuisance(rows), np.vstack(target), keys, {mode: np.vstack(values) for mode, values in representations.items()}


def fold_cache(rows, x, y):
    cache = []
    for held in sorted({row["physical_folio"] for row in rows}):
        train = np.array([i for i, row in enumerate(rows) if row["physical_folio"] != held])
        test = np.array([i for i, row in enumerate(rows) if row["physical_folio"] == held])
        xtrain, xtest, _, _ = standardize_train(x[train], x[test])
        ytrain, ytest, ymean, yscale = standardize_train(y[train], y[test])
        coefficient = fit(xtrain, ytrain)
        reference = predict(xtest, coefficient)
        cache.append(
            {
                "held": held,
                "train": train,
                "test": test,
                "xtrain": xtrain,
                "xtest": xtest,
                "ytrain": ytrain,
                "ytest": ytest,
                "ymean": ymean,
                "yscale": yscale,
                "reference": reference,
            }
        )
    return cache


def evaluate(mode, assignment, details=False):
    context = NULL_CONTEXT
    representation = context["representations"][mode][assignment]
    total = 0.0
    folds = []
    predictions = []
    blocks = Counter()
    parity = Counter()
    for fold in context["folds"]:
        train = fold["train"]
        test = fold["test"]
        atrain, atest, _, _ = standardize_train(representation[train], representation[test])
        coefficient = fit(np.c_[fold["xtrain"], atrain], fold["ytrain"])
        model = predict(np.c_[fold["xtest"], atest], coefficient)
        gain = bits(fold["ytest"], fold["reference"], model)
        total += gain
        if not details:
            continue
        folds.append(
            {
                "model": mode,
                "held_folio": fold["held"],
                "pairs": len(test),
                "gain_bits": gain,
                "positive": int(gain > 0),
            }
        )
        for block, indices in BLOCK_INDEX.items():
            blocks[block] += bits(
                fold["ytest"][:, list(indices)],
                fold["reference"][:, list(indices)],
                model[:, list(indices)],
            )
        classes = defaultdict(list)
        for index in train:
            classes[context["keys"][index]].append(context["y"][index])
        class_vectors = {key: np.mean(values, axis=0) for key, values in classes.items()}
        reference_raw = fold["reference"] * fold["yscale"] + fold["ymean"]
        model_raw = model * fold["yscale"] + fold["ymean"]
        for position, index in enumerate(test):
            reference_guess, reference_top = nearest(reference_raw[position], class_vectors)
            model_guess, model_top = nearest(model_raw[position], class_vectors)
            actual = context["keys"][index]
            predictions.append(
                {
                    "model": mode,
                    "held_folio": fold["held"],
                    "locus": context["rows"][index]["locus"],
                    "next_locus": context["rows"][index]["next_locus"],
                    "actual_architecture": actual,
                    "reference_prediction": reference_guess,
                    "model_prediction": model_guess,
                    "reference_top1": int(reference_guess == actual),
                    "model_top1": int(model_guess == actual),
                    "reference_top3": int(actual in reference_top),
                    "model_top3": int(actual in model_top),
                    "actual_seen_in_training": int(actual in class_vectors),
                }
            )
            row_gain = bits(
                fold["ytest"][position : position + 1],
                fold["reference"][position : position + 1],
                model[position : position + 1],
            )
            parity[context["rows"][index]["source_line_number"] % 2] += row_gain
    return total, folds, predictions, blocks, parity


def null_worker(assignment):
    assignment = np.asarray(assignment, int)
    return tuple(evaluate(mode, assignment, False)[0] for mode in MODES)


def strata_for(rows, exact):
    out = defaultdict(list)
    for index, row in enumerate(rows):
        key = [row["page"], len(row["groups"]), len(row["target"])]
        if exact:
            key.extend(
                [
                    len(row["last"]),
                    sum(len(cell["page_host"]) for cell in row["last"]),
                    sum(len(cell["token"]) for cell in row["last"]),
                ]
            )
        out[tuple(key)].append(index)
    return out


def capacity(strata, keys):
    swappable = sum(len(indices) for indices in strata.values() if len(indices) > 1)
    mobile = sum(
        len(indices)
        for indices in strata.values()
        if len(indices) > 1 and len({keys[index] for index in indices}) > 1
    )
    return swappable, mobile


def assignments(strata, label, count):
    rng = random.Random(seed("GDT135", label))
    out = []
    for _ in range(count):
        assignment = list(range(sum(len(indices) for indices in strata.values())))
        for indices in strata.values():
            if len(indices) > 1:
                shuffled = indices[:]
                rng.shuffle(shuffled)
                for source, replacement in zip(indices, shuffled):
                    assignment[source] = replacement
        out.append(assignment)
    return out


def main():
    global NULL_CONTEXT
    prediction = json.loads(PREDICTION.read_text())
    assert prediction["status"] == "FROZEN_POSTSELECTED_BEFORE_TARGET_ARCHITECTURE_EXTRACTION"
    rows = load_panel()
    x, y, keys, representations = prepare(rows)
    folds_cache = fold_cache(rows, x, y)
    NULL_CONTEXT = {
        "rows": rows,
        "y": y,
        "keys": keys,
        "representations": representations,
        "folds": folds_cache,
    }
    identity = np.arange(len(rows))
    scores = []
    folds = []
    predictions = []
    blocks = []
    score_map = {}
    parity_map = {}
    for mode in MODES:
        gain, mode_folds, mode_predictions, mode_blocks, parity = evaluate(mode, identity, True)
        score = {
            "model": mode,
            "pairs": len(rows),
            "physical_folios": 9,
            "gain_bits": gain,
            "positive_folios": sum(row["positive"] for row in mode_folds),
            "reference_top1": sum(row["reference_top1"] for row in mode_predictions),
            "model_top1": sum(row["model_top1"] for row in mode_predictions),
            "reference_top3": sum(row["reference_top3"] for row in mode_predictions),
            "model_top3": sum(row["model_top3"] for row in mode_predictions),
            "architecture_seen": sum(row["actual_seen_in_training"] for row in mode_predictions),
            "even_source_line_gain_bits": parity[0],
            "odd_source_line_gain_bits": parity[1],
        }
        scores.append(score)
        score_map[mode] = score
        parity_map[mode] = parity
        folds.extend(mode_folds)
        predictions.extend(mode_predictions)
        blocks.extend(
            {
                "model": mode,
                "target_block": block,
                "gain_bits": mode_blocks[block],
                "status": "DESCRIPTIVE_FIXED_PARTITION_NOT_SEPARATE_TEST",
            }
            for block in BLOCK_INDEX
        )

    exact = strata_for(rows, True)
    coarse = strata_for(rows, False)
    exact_capacity, exact_mobile = capacity(exact, keys)
    coarse_capacity, coarse_mobile = capacity(coarse, keys)
    null_rows = []
    workers = min(32, os.cpu_count() or 1)
    with mp.Pool(workers) as pool:
        for null_id, strata in (("EXACT_OPPORTUNITY", exact), ("COARSE_PAGE_COUNT", coarse)):
            worlds = pool.map(null_worker, assignments(strata, null_id, WORLDS), chunksize=8)
            values = {mode: [world[position] for world in worlds] for position, mode in enumerate(MODES)}
            maxima = [max(world) for world in worlds]
            for mode in MODES:
                observed = score_map[mode]["gain_bits"]
                null_rows.append(
                    {
                        "null_id": null_id,
                        "model": mode,
                        "worlds": WORLDS,
                        "swappable_pairs": exact_capacity if null_id == "EXACT_OPPORTUNITY" else coarse_capacity,
                        "architecture_mobile_pairs": exact_mobile if null_id == "EXACT_OPPORTUNITY" else coarse_mobile,
                        "true_gain_bits": observed,
                        "null_mean_bits": float(np.mean(values[mode])),
                        "local_p": (1 + sum(value >= observed - 1e-12 for value in values[mode])) / (WORLDS + 1),
                        "max_three_p": (1 + sum(value >= observed - 1e-12 for value in maxima)) / (WORLDS + 1),
                    }
                )

    null_map = {(row["null_id"], row["model"]): row for row in null_rows}
    compiler = score_map["COMPILER12"]
    gates = {
        "compiler_gain_positive": compiler["gain_bits"] > 0,
        "compiler_beats_host": compiler["gain_bits"] > score_map["HOST_CHAR3"]["gain_bits"],
        "compiler_beats_raw": compiler["gain_bits"] > score_map["RAW_CHAR3"]["gain_bits"],
        "compiler_positive_at_least_6_of_9_folios": compiler["positive_folios"] >= 6,
        "compiler_positive_both_source_line_parities": compiler["even_source_line_gain_bits"] > 0
        and compiler["odd_source_line_gain_bits"] > 0,
        "exact_capacity_at_least_30": exact_capacity >= 30,
        "exact_max_three_p_le_005": exact_capacity >= 30
        and null_map["EXACT_OPPORTUNITY", "COMPILER12"]["max_three_p"] <= 0.05,
    }
    status = (
        "SECTION_B_ADJACENT_FIELD_ARCHITECTURE_TRANSFER_SUPPORTED"
        if all(gates.values())
        else "INSUFFICIENT_EXACT_NULL_CAPACITY"
        if exact_capacity < 30
        else "SECTION_B_COMPILER_LEAD_DOES_NOT_TRANSFER_TO_NEW_ARCHITECTURE_ENDPOINT"
    )

    inventory = []
    for index, row in enumerate(rows):
        inventory.append(
            {
                "locus": row["locus"],
                "next_locus": row["next_locus"],
                "page": row["page"],
                "physical_folio": row["physical_folio"],
                "source_line_number": row["source_line_number"],
                "source_group_count": len(row["groups"]),
                "source_member_count": row["member_count"],
                "last_field_group_count": len(row["last"]),
                "last_field_host_length": sum(len(cell["page_host"]) for cell in row["last"]),
                "last_field_raw_length": sum(len(cell["token"]) for cell in row["last"]),
                "target_first_field_group_count": len(row["target"]),
                "target_architecture": keys[index],
                "selection": "FROZEN_GDT134_SECTION_B_PRIMARY_PAIR",
            }
        )
    counterexamples = [
        {"counterexample": "POSTSELECTION", "detail": "Section B was selected after its GDT134 COMPILER12 count-bin lead was exposed."},
        {"counterexample": "EXACT_NULL_CAPACITY", "detail": str(exact_capacity)},
        {"counterexample": "EXACT_ARCHITECTURE_MOBILE", "detail": str(exact_mobile)},
        {"counterexample": "COARSE_NULL_CAPACITY", "detail": str(coarse_capacity)},
        {"counterexample": "ARCHITECTURE_TYPE_COUNT", "detail": str(len(set(keys)))},
        {"counterexample": "ADJACENT_PAIR_OVERLAP", "detail": "Even/odd source-line gains are required because neighboring pairs overlap within runs."},
        {"counterexample": "F84", "detail": "GDT134 guarded loader rejects all f84* rows before HPR2 parsing; no f84 target is retained or scored."},
    ]

    format_rows = lambda rows: [
        {key: (f"{value:.12f}" if isinstance(value, float) else value) for key, value in row.items()} for row in rows
    ]
    write(INVENTORY, inventory)
    write(PREDICTIONS, predictions)
    write(SCORES, format_rows(scores))
    write(FOLDS, format_rows(folds))
    write(BLOCKS, format_rows(blocks))
    write(NULL, format_rows(null_rows))
    write(COUNTER, counterexamples)

    lines = [
        "# GDT135 — section-B adjacent field-architecture transfer",
        "",
        f"Status: **{status}**",
        "",
        (
            f"The frozen postselected panel has {len(rows)} section-B continuation pairs on nine folios. "
            f"The new target has {len(set(keys))} distinct entry/closure architectures. Exact strata retain "
            f"{exact_capacity} swappable records ({exact_mobile} architecture-mobile); coarse strata retain "
            f"{coarse_capacity} ({coarse_mobile} mobile)."
        ),
        "",
        "| model | gain bits | positive folios | even / odd gain | top-1 vs ref | top-3 vs ref | exact max-3 p | coarse max-3 p |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for mode in MODES:
        row = score_map[mode]
        lines.append(
            f"| `{mode}` | {row['gain_bits']:+.3f} | {row['positive_folios']}/9 | "
            f"{row['even_source_line_gain_bits']:+.3f} / {row['odd_source_line_gain_bits']:+.3f} | "
            f"{row['model_top1']}/{len(rows)} vs {row['reference_top1']}/{len(rows)} | "
            f"{row['model_top3']}/{len(rows)} vs {row['reference_top3']}/{len(rows)} | "
            f"{null_map['EXACT_OPPORTUNITY', mode]['max_three_p']:.4f} | "
            f"{null_map['COARSE_PAGE_COUNT', mode]['max_three_p']:.4f} |"
        )
    lines += [
        "",
        f"Frozen gates: `{json.dumps(gates, sort_keys=True)}`.",
        "",
        "This is a postselected hypothesis-generation test of a new endpoint, not confirmation of GDT134.",
        "",
        (
            "No record meaning, heading, recipe, semantic role, word, morpheme, POS, sound, language, "
            "plaintext, meaning, or translation is inferred. No f84 row was retained, parsed, joined, or scored."
        ),
    ]
    REPORT.write_text("\n".join(lines) + "\n")

    result = {
        "schema": "GDT135_SECTION_B_FIELD_ARCHITECTURE_TRANSFER_RESULT_V1",
        "status": status,
        "chronology": prediction["chronology"],
        "pairs": len(rows),
        "pages": len({row["page"] for row in rows}),
        "physical_folios": len({row["physical_folio"] for row in rows}),
        "architecture_types": len(set(keys)),
        "scores": scores,
        "target_blocks": blocks,
        "null_capacity": {
            "exact_swappable": exact_capacity,
            "exact_architecture_mobile": exact_mobile,
            "coarse_swappable": coarse_capacity,
            "coarse_architecture_mobile": coarse_mobile,
        },
        "gates": gates,
        "interpretation": "Postselected section-B test of final-field compiler dependence on new next-field entry/closure architecture.",
        "claim_ceiling": "Section-B formal adjacent-field transition only; no semantics, language, plaintext, meaning, or translation.",
        "f84": {
            "retained_parsed_joined_or_scored": False,
            "new_f84r_access": False,
            "prior_limited_f84r_audit_exposure_inherited": True,
        },
        "inputs": {
            name: sha(ROOT / name)
            for name in (
                "gdt135_prediction.json",
                "gdt134_result.json",
                "gdt134_general_continuation_inventory.tsv",
                "gdt016_group_state_inventory.tsv",
                "gdt046_line_frames.tsv",
            )
        },
        "implementation": {
            Path(__file__).name: sha(Path(__file__)),
            "run_gdt131_q20_cross_line_field_onset.py": sha(ROOT / "run_gdt131_q20_cross_line_field_onset.py"),
            "run_gdt133_raw_surface_transfer_decomposition.py": sha(ROOT / "run_gdt133_raw_surface_transfer_decomposition.py"),
            "run_gdt134_general_adjacent_continuation_transfer.py": sha(ROOT / "run_gdt134_general_adjacent_continuation_transfer.py"),
        },
        "outputs": {
            path.name: sha(path)
            for path in (INVENTORY, PREDICTIONS, SCORES, FOLDS, BLOCKS, NULL, COUNTER)
        },
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "status": status,
                "scores": scores,
                "capacity": result["null_capacity"],
                "gates": gates,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
