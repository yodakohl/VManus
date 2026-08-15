#!/usr/bin/env python3
"""Independent source rebuild and real-score validator for GDT135."""

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
FRAMES = ROOT / "gdt046_line_frames.tsv"
INVENTORY = ROOT / "gdt135_section_b_field_architecture_inventory.tsv"
PREDICTIONS = ROOT / "gdt135_section_b_field_architecture_predictions.tsv"
SCORES = ROOT / "gdt135_section_b_field_architecture_scores.tsv"
FOLDS = ROOT / "gdt135_section_b_field_architecture_folds.tsv"
BLOCKS = ROOT / "gdt135_section_b_field_architecture_blocks.tsv"
NULL = ROOT / "gdt135_section_b_field_architecture_null.tsv"
RESULT = ROOT / "gdt135_result.json"
OUT = ROOT / "gdt135_validation.json"
PREFIXES = ("che", "ch", "sh", "t", "s", "d", "q")
WRAPS = ("q", "d", "s", "ch", "che", "sh", "t")
RIGHT = ("aiin", "air", "ain", "ar", "al")
Q20 = {"f104", "f105", "f106", "f107", "f112", "f113", "f114", "f115"}
MODES = ("COMPILER12", "HOST_CHAR3", "RAW_CHAR3")
BLOCKS_INDEX = {
    "FIRST_WRAPPER8": tuple(range(0, 8)),
    "FIRST_FRAME3": tuple(range(8, 11)),
    "FIRST_RENDERER4": tuple(range(11, 15)),
    "FIELD_CLOSURE3": tuple(range(15, 18)),
}
LAM = 1000.0


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded_rows(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        header = handle.readline().rstrip("\r\n").split("\t")
        locus_i = header.index("locus")
        page_i = header.index("page")
        for line in handle:
            cells = line.rstrip("\r\n").split("\t")
            if cells[locus_i].startswith("f84") or cells[page_i].startswith("f84"):
                continue
            yield dict(zip(header, cells))


def numeric(locus):
    match = re.match(r"^(.*)\.(\d+)$", locus)
    return (match.group(1), int(match.group(2))) if match else None


def strip(token):
    prefix = "NONE"
    residual = token
    for candidate in PREFIXES:
        if residual.startswith(candidate) and len(residual) > len(candidate):
            prefix = candidate
            residual = residual[len(candidate) :]
            break
    dy = int(residual.endswith("dy") and len(residual) > 2)
    if dy:
        residual = residual[:-2]
    return prefix, residual, dy


def preparse(prefix, residual):
    b3 = int(residual.endswith("m") and len(residual) > 1)
    host = residual[:-1] if b3 else residual
    right = "NONE"
    for suffix in RIGHT:
        if host.endswith(suffix) and len(host) > len(suffix):
            host = host[: -len(suffix)]
            right = suffix
            break
    inner = int(prefix in {"ch", "che", "sh"} and host.startswith("d") and len(host) > 1)
    if inner:
        host = host[1:]
    return host, b3, right, inner


def parse_source(source):
    prepared = []
    counts = Counter()
    for row in source:
        prefix, residual, dy = strip(row["token"])
        assert dy == int(row["dy_closure"])
        host, b3, right, inner = preparse(prefix, residual)
        prepared.append((row, prefix, host, b3, right, inner, dy))
        counts[host] += 1
    licensed = {host for host in counts if counts[host] and counts["o" + host] and counts["ot" + host]} | {"ar", "al", "ol"}
    parsed = {}
    for row, prefix, host, b3, right, inner, dy in prepared:
        frame = "NONE"
        if host.startswith("ot") and host[2:] in licensed:
            host = host[2:]
            frame = "OT"
        elif host.startswith("o") and host[1:] in licensed:
            host = host[1:]
            frame = "O"
        parsed[(row["locus"], int(row["group_index"]))] = {
            "token": row["token"],
            "page_host": host or "EMPTY",
            "wrapper": prefix,
            "frame": frame,
            "right": right,
            "inner": inner,
            "dy": dy,
            "b3": b3,
        }
    return parsed


def fields(groups):
    out = []
    current = []
    for group in groups:
        current.append(group)
        if group["dy"]:
            out.append(current)
            current = []
    if current:
        out.append(current)
    return out


def panel():
    source = list(guarded_rows(SOURCE))
    parsed = parse_source(source)
    by = defaultdict(list)
    for row in source:
        if row["section"] == "B" and row["physical_folio"] not in Q20:
            by[row["locus"]].append(row)
    complete = {}
    for locus, rows in by.items():
        rows.sort(key=lambda row: int(row["group_index"]))
        count = int(rows[0]["group_count"])
        if len(rows) == count and [int(row["group_index"]) for row in rows] == list(range(1, count + 1)):
            complete[locus] = rows
    frames = {row["locus"]: row for row in guarded_rows(FRAMES)}
    out = []
    for locus, rows in complete.items():
        if locus not in frames or frames[locus]["paragraph_start"] != "0":
            continue
        position = numeric(locus)
        if not position:
            continue
        next_locus = f"{position[0]}.{position[1] + 1}"
        if next_locus not in complete or next_locus not in frames or frames[next_locus]["paragraph_start"] != "0":
            continue
        source_groups = [parsed[(locus, int(row["group_index"]))] for row in rows]
        target_groups = [parsed[(next_locus, int(row["group_index"]))] for row in complete[next_locus]]
        out.append(
            {
                "locus": locus,
                "next_locus": next_locus,
                "page": rows[0]["page"],
                "physical_folio": rows[0]["physical_folio"],
                "line": position[1],
                "member_count": sum(len(row["family_surface"]) for row in rows),
                "groups": source_groups,
                "last": fields(source_groups)[-1],
                "target": fields(target_groups)[0],
            }
        )
    return sorted(out, key=lambda row: (row["physical_folio"], row["page"], row["line"]))


def architecture(field):
    first = field[0]
    wraps = ("NONE",) + WRAPS
    frames = ("NONE", "O", "OT")
    end = "DY" if field[-1]["dy"] else "B3" if field[-1]["b3"] else "OPEN"
    vector = [int(first["wrapper"] == value) for value in wraps]
    vector += [int(first["frame"] == value) for value in frames]
    vector += [int(first["right"] != "NONE"), first["inner"], first["dy"], first["b3"]]
    vector += [int(end == value) for value in ("DY", "B3", "OPEN")]
    key = (
        f"W={first['wrapper']};F={first['frame']};R={int(first['right'] != 'NONE')};"
        f"D={first['inner']};DY={first['dy']};B3={first['b3']};END={end}"
    )
    return np.asarray(vector, float), key


def hash32(text):
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16) % 32


def hvec(strings):
    vector = np.zeros(32)
    for string in strings:
        padded = "^" + string + "$"
        for index in range(max(0, len(padded) - 2)):
            vector[hash32(padded[index : index + 3])] += 1
    return vector / max(1, vector.sum())


def compiler(groups):
    counts = Counter()
    for group in groups:
        if group["wrapper"] in WRAPS:
            counts["W_" + group["wrapper"]] += 1
        if group["frame"] in {"O", "OT"}:
            counts["F_" + group["frame"]] += 1
        counts["RIGHT"] += group["right"] != "NONE"
        counts["DY"] += group["dy"]
        counts["B3"] += group["b3"]
    keys = tuple("W_" + value for value in WRAPS) + ("F_O", "F_OT", "RIGHT", "DY", "B3")
    return np.asarray([counts[key] / len(groups) for key in keys], float)


def nuisance(rows):
    maximum = defaultdict(int)
    for row in rows:
        maximum[row["page"]] = max(maximum[row["page"]], row["line"])
    return np.asarray(
        [
            [
                len(row["groups"]),
                row["member_count"],
                len(row["last"]),
                sum(len(group["page_host"]) for group in row["last"]),
                sum(len(group["token"]) for group in row["last"]),
                len(row["target"]),
                row["line"] / max(1, maximum[row["page"]]),
                row["line"] % 2,
                int(row["page"].endswith("v")),
            ]
            for row in rows
        ],
        float,
    )


def representation(row, mode):
    if mode == "COMPILER12":
        return compiler(row["last"])
    if mode == "HOST_CHAR3":
        return hvec([group["page_host"] for group in row["last"]])
    return hvec([group["token"] for group in row["last"]])


def standardize(train, test):
    mean = train.mean(0)
    scale = train.std(0)
    scale[scale < 1e-8] = 1
    return (train - mean) / scale, (test - mean) / scale, mean, scale


def fit(x, y):
    design = np.c_[np.ones(len(x)), x]
    penalty = np.eye(design.shape[1])
    penalty[0, 0] = 0
    return np.linalg.solve(design.T @ design + LAM * penalty, design.T @ y)


def predict(x, coefficient):
    return np.c_[np.ones(len(x)), x] @ coefficient


def bits(y, reference, model):
    return float((np.square(y - reference).sum() - np.square(y - model).sum()) / (2 * math.log(2)))


def nearest(prediction, classes):
    ranked = sorted((float(np.square(prediction - vector).sum()), key) for key, vector in classes.items())
    return ranked[0][1], [key for _, key in ranked[:3]]


def close(left, right):
    return abs(float(left) - float(right)) < 2e-9


def main():
    result = json.loads(RESULT.read_text())
    checks = []

    def check(name, value):
        checks.append({"check": name, "pass": bool(value)})
        assert value, name

    check("schema", result["schema"] == "GDT135_SECTION_B_FIELD_ARCHITECTURE_TRANSFER_RESULT_V1")
    check("status", result["status"] == "INSUFFICIENT_EXACT_NULL_CAPACITY")
    prediction = json.loads((ROOT / "gdt135_prediction.json").read_text())
    check("freeze", prediction["status"] == "FROZEN_POSTSELECTED_BEFORE_TARGET_ARCHITECTURE_EXTRACTION")
    rows = panel()
    check("panel", len(rows) == 69 and len({row["page"] for row in rows}) == 17 and len({row["physical_folio"] for row in rows}) == 9)
    check("no_f84", not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in rows))
    vectors_and_keys = [architecture(row["target"]) for row in rows]
    y = np.vstack([item[0] for item in vectors_and_keys])
    keys = [item[1] for item in vectors_and_keys]
    check("types", len(set(keys)) == result["architecture_types"] == 29)

    inventory = read(INVENTORY)
    indexed = {(row["locus"], row["next_locus"]): row for row in inventory}
    check("inventory_keys", set(indexed) == {(row["locus"], row["next_locus"]) for row in rows})
    for row, key in zip(rows, keys):
        exported = indexed[row["locus"], row["next_locus"]]
        check("inventory_" + row["locus"], exported["target_architecture"] == key and int(exported["target_first_field_group_count"]) == len(row["target"]))

    x = nuisance(rows)
    representations = {mode: np.vstack([representation(row, mode) for row in rows]) for mode in MODES}
    fold_export = read(FOLDS)
    prediction_export = read(PREDICTIONS)
    block_export = read(BLOCKS)
    score_export = {row["model"]: row for row in read(SCORES)}
    reconstructed = {}
    for mode in MODES:
        total = 0.0
        positive = 0
        parity = Counter()
        blocks = Counter()
        hit = Counter()
        for held in sorted({row["physical_folio"] for row in rows}):
            train = np.array([i for i, row in enumerate(rows) if row["physical_folio"] != held])
            test = np.array([i for i, row in enumerate(rows) if row["physical_folio"] == held])
            xtrain, xtest, _, _ = standardize(x[train], x[test])
            ytrain, ytest, ymean, yscale = standardize(y[train], y[test])
            reference = predict(xtest, fit(xtrain, ytrain))
            atrain, atest, _, _ = standardize(representations[mode][train], representations[mode][test])
            model = predict(np.c_[xtest, atest], fit(np.c_[xtrain, atrain], ytrain))
            gain = bits(ytest, reference, model)
            total += gain
            positive += gain > 0
            exported_fold = next(row for row in fold_export if row["model"] == mode and row["held_folio"] == held)
            check("fold_" + mode + "_" + held, close(exported_fold["gain_bits"], gain))
            for block, indices in BLOCKS_INDEX.items():
                blocks[block] += bits(ytest[:, list(indices)], reference[:, list(indices)], model[:, list(indices)])
            classes = defaultdict(list)
            for index in train:
                classes[keys[index]].append(y[index])
            classes = {key: np.mean(values, axis=0) for key, values in classes.items()}
            reference_raw = reference * yscale + ymean
            model_raw = model * yscale + ymean
            for position, index in enumerate(test):
                ref_guess, ref_top = nearest(reference_raw[position], classes)
                model_guess, model_top = nearest(model_raw[position], classes)
                hit["seen"] += keys[index] in classes
                hit["ref1"] += ref_guess == keys[index]
                hit["model1"] += model_guess == keys[index]
                hit["ref3"] += keys[index] in ref_top
                hit["model3"] += keys[index] in model_top
                parity[rows[index]["line"] % 2] += bits(ytest[position : position + 1], reference[position : position + 1], model[position : position + 1])
                exported_prediction = next(row for row in prediction_export if row["model"] == mode and row["locus"] == rows[index]["locus"])
                check("prediction_" + mode + "_" + rows[index]["locus"], exported_prediction["actual_architecture"] == keys[index] and int(exported_prediction["model_top1"]) == int(model_guess == keys[index]))
        reconstructed[mode] = (total, positive, parity, blocks, hit)
        exported = score_export[mode]
        check("score_" + mode, close(exported["gain_bits"], total) and int(exported["positive_folios"]) == positive and close(exported["even_source_line_gain_bits"], parity[0]) and close(exported["odd_source_line_gain_bits"], parity[1]))
        check("hits_" + mode, int(exported["architecture_seen"]) == hit["seen"] and int(exported["reference_top1"]) == hit["ref1"] and int(exported["model_top1"]) == hit["model1"] and int(exported["reference_top3"]) == hit["ref3"] and int(exported["model_top3"]) == hit["model3"])
        for block in BLOCKS_INDEX:
            exported_block = next(row for row in block_export if row["model"] == mode and row["target_block"] == block)
            check("block_" + mode + "_" + block, close(exported_block["gain_bits"], blocks[block]))
        check("block_sum_" + mode, close(total, sum(blocks.values())))

    def strata(exact):
        groups = defaultdict(list)
        for index, row in enumerate(rows):
            key = [row["page"], len(row["groups"]), len(row["target"])]
            if exact:
                key += [len(row["last"]), sum(len(group["page_host"]) for group in row["last"]), sum(len(group["token"]) for group in row["last"])]
            groups[tuple(key)].append(index)
        return groups

    def capacity(groups):
        return (
            sum(len(indices) for indices in groups.values() if len(indices) > 1),
            sum(len(indices) for indices in groups.values() if len(indices) > 1 and len({keys[index] for index in indices}) > 1),
        )

    check("capacity", capacity(strata(True)) == (0, 0) and capacity(strata(False)) == (7, 7))
    null = read(NULL)
    check("null_rows", len(null) == 6 and all(int(row["swappable_pairs"]) == (0 if row["null_id"] == "EXACT_OPPORTUNITY" else 7) for row in null))
    compiler, host, raw = (score_export[mode] for mode in MODES)
    gates = {
        "compiler_gain_positive": float(compiler["gain_bits"]) > 0,
        "compiler_beats_host": float(compiler["gain_bits"]) > float(host["gain_bits"]),
        "compiler_beats_raw": float(compiler["gain_bits"]) > float(raw["gain_bits"]),
        "compiler_positive_at_least_6_of_9_folios": int(compiler["positive_folios"]) >= 6,
        "compiler_positive_both_source_line_parities": float(compiler["even_source_line_gain_bits"]) > 0 and float(compiler["odd_source_line_gain_bits"]) > 0,
        "exact_capacity_at_least_30": False,
        "exact_max_three_p_le_005": False,
    }
    check("gates", gates == result["gates"])
    check("input_hashes", all(sha(ROOT / path) == digest for path, digest in result["inputs"].items()))
    check("implementation_hashes", all(sha(ROOT / path) == digest for path, digest in result["implementation"].items()))
    check("output_hashes", all(sha(ROOT / path) == digest for path, digest in result["outputs"].items()))
    check("document_hashes", all(sha(ROOT / path) == digest for path, digest in result["documents"].items()))
    content = dict(result)
    digest = content.pop("result_content_sha256")
    check("content", csha(content) == digest)

    validation = {
        "schema": "GDT135_SECTION_B_FIELD_ARCHITECTURE_TRANSFER_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_SOURCE_REBUILD_AND_REAL_SCORE_REFIT",
        "checks": len(checks),
        "passed": sum(row["pass"] for row in checks),
        "scope": "Independent guarded source/HPR2 rebuild and all real LOFO scores, blocks, hits, capacities, gates, and hashes; 4096 retained permutation worlds are not independently replayed.",
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "check_rows": checks,
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"], "checks": validation["checks"]}, sort_keys=True))


if __name__ == "__main__":
    main()
