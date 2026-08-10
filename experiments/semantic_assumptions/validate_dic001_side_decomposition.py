#!/usr/bin/env python3
"""Independent reconstruction of the descriptive DIC001 side decomposition."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent; RES = HERE / "results"
CLEAN = HERE / "validate_dic001_drawing_interruption_target.py"
SPEC = HERE / "DIC001_SIDE_DECOMPOSITION_SPEC.md"; PRODUCER = HERE / "analyze_dic001_side_decomposition.py"
RESULT = RES / "dic001_side_decomposition.json"; REPORT = RES / "dic001_side_decomposition_report.md"
OUT = RES / "dic001_side_decomposition_validation.json"; OUT_REPORT = RES / "dic001_side_decomposition_validation_report.md"
FROZEN = {CLEAN: "4a24b39a626dcec076b1edb0556ffeb8343c065f9a511e0a43d09960d7f7047a",
          SPEC: "bb88ef30548317f6bbdc157ed8a08f6f5f51eb18ec957b39316df78275e1df58",
          PRODUCER: "c6ed5de8efad2a4bd122599f5db127dc5e43f20885dde432efd338aefebf1e63",
          RESULT: "a8323b6a57118fbd63cd327cd75f3a322aac4488671b6505b5fe3c49d7a77a31",
          REPORT: "326af30f607b17666f80942a82656bffe839388c7a1a780ac9a150c43f466262"}
NAMES = ("LEFT_TERMINAL", "RIGHT_INITIAL", "CROSS_PAIR")


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def components(left, right):
    a, b = left["family_surface"], right["family_surface"]
    a2 = a[-2:] if len(a) > 1 else "#" + a; b2 = b[:2] if len(b) > 1 else b + "#"
    return ((a[-1], a2), (b[0], b2), (a[-1] + "|" + b[0], a2 + "|" + b2))


def train_blocks(events):
    counts = [[[Counter() for _ in range(2)] for _ in range(3)] for _ in range(2)]
    totals = [[[0] * 2 for _ in range(3)] for _ in range(2)]; vocabulary = [[set() for _ in range(2)] for _ in range(3)]
    for event in events:
        for block, values in enumerate(components(event[3], event[4])):
            for slot, value in enumerate(values):
                counts[event[2]][block][slot][value] += 1; totals[event[2]][block][slot] += 1; vocabulary[block][slot].add(value)
    def score(left, right):
        out = np.zeros(3)
        for block, values in enumerate(components(left, right)):
            for slot, value in enumerate(values):
                k = len(vocabulary[block][slot]) + 1
                out[block] += math.log((counts[1][block][slot][value] + 1) / (totals[1][block][slot] + k))
                out[block] -= math.log((counts[0][block][slot][value] + 1) / (totals[0][block][slot] + k))
        return out
    return score


def exact_basis(panel, neighbors):
    n = len(panel); columns = [np.ones(n)]; pages = sorted({row["page"] for row in panel})
    columns += [np.array([row["page"] == page for row in panel], dtype=float) for page in pages[1:]]
    r = np.array([float(row["normalized_boundary_position"]) for row in panel]); columns += [r, r ** 2, r ** 3]
    bins = np.minimum((10 * r).astype(np.int64), 9); columns += [(bins == x).astype(float) for x in range(1, 10)]
    count = np.minimum(np.array([int(row["group_count"]) for row in panel]), 20); columns += [(count == x).astype(float) for x in sorted(set(count))[1:]]
    left = np.array([min(8, len(a["family_surface"])) for a, _ in neighbors]); right = np.array([min(8, len(b["family_surface"])) for _, b in neighbors])
    cells = sorted(set(zip(left.tolist(), right.tolist()))); columns += [((left == a) & (right == b)).astype(float) for a, b in cells[1:]]
    return np.column_stack(columns)


def shuffled_six(metadata, vectors):
    worlds = 65536
    def one(meta):
        page, indices, k, scale, _, _, _ = meta
        seed = int.from_bytes(hashlib.sha256(f"76001004|{page}".encode()).digest()[:8], "little")
        priority = np.random.default_rng(seed).random((worlds, len(indices)))
        selected_index = np.argpartition(priority, k - 1, axis=1)[:, :k]
        selected = np.take(vectors[indices], selected_index, axis=0).sum(axis=1)
        total = vectors[indices].sum(axis=0)
        return scale * (selected / k - (total - selected) / (len(indices) - k))
    result = np.zeros((worlds, vectors.shape[1]))
    with ThreadPoolExecutor(max_workers=16) as executor:
        for contribution in executor.map(one, metadata): result += contribution
    return result


def compare(a, b, path="root"):
    checks, errors, maximum = 1, [], 0.0
    if type(a) is not type(b): return checks, [path + ":type"], maximum
    if isinstance(a, dict):
        if set(a) != set(b): errors.append(path + ":keys")
        for key in sorted(set(a) & set(b)):
            c, e, m = compare(a[key], b[key], path + "." + key); checks += c; errors += e; maximum = max(maximum, m)
    elif isinstance(a, float):
        maximum = abs(a - b)
        if maximum > 2e-14: errors.append(f"{path}:delta={maximum:.3g}")
    elif a != b: errors.append(path + ":value")
    return checks, errors, maximum


def main():
    for path, expected in FROZEN.items():
        if sha(path) != expected: raise SystemExit("input drift: " + path.name)
    spec = importlib.util.spec_from_file_location("clean_target_validator", CLEAN); clean = importlib.util.module_from_spec(spec); spec.loader.exec_module(clean)
    target = json.loads(clean.TARGET.read_text())
    with clean.SOURCE.open(newline="") as handle: source = list(csv.DictReader(handle, delimiter="\t"))
    with clean.PANEL.open(newline="") as handle: panel = list(csv.DictReader(handle, delimiter="\t"))
    pages = {row["page"] for row in panel if row["boundary_class"] == "DRAWING_INTERRUPTION"}
    source_index = {(row["locus"], int(row["group_index"])): row for row in source}
    neighbors = [(source_index[(row["locus"], int(row["left_group_index"]))], source_index[(row["locus"], int(row["right_group_index"]))]) for row in panel]
    reference = clean.make_reference(source, pages); folios = sorted({row["physical_folio"] for row in panel})
    raw = np.empty((len(panel), 3)); anchor = np.empty(len(panel))
    for held in folios:
        training = [event for event in reference if event[1] != held]; block_model = train_blocks(training); full_model = clean.classifier(training)
        block_spaces = np.vstack([block_model(event[3], event[4]) for event in training if event[2] == 0])
        full_spaces = np.array([full_model(event[3], event[4]) for event in training if event[2] == 0])
        means = block_spaces.mean(axis=0); mean = full_spaces.mean(); sd = full_spaces.std(ddof=0)
        indices = [i for i, row in enumerate(panel) if row["physical_folio"] == held]
        raw[indices] = np.vstack([(block_model(*neighbors[i]) - means) / sd for i in indices])
        anchor[indices] = [(full_model(*neighbors[i]) - mean) / sd for i in indices]
    raw_gap = float(np.max(np.abs(raw.sum(axis=1) - anchor))); raw[:, 2] += anchor - raw.sum(axis=1)
    basis = exact_basis(panel, neighbors); residual = raw - basis @ np.linalg.lstsq(basis, raw, rcond=None)[0]
    anchor_residual = anchor - basis @ np.linalg.lstsq(basis, anchor, rcond=None)[0]
    residual_gap = float(np.max(np.abs(residual.sum(axis=1) - anchor_residual))); residual[:, 2] += anchor_residual - residual.sum(axis=1)
    weight, metadata, folios = clean.panel_topology(panel)
    null = shuffled_six(metadata, np.column_stack((raw, residual)))
    blocks = {}
    for j, name in enumerate(NAMES):
        a = clean.describe(raw[:, j], panel, weight, metadata, folios); b = clean.describe(residual[:, j], panel, weight, metadata, folios)
        blocks[name] = {"raw": a, "residual": b, "p_raw": (1 + int(np.sum(null[:, j] >= a["effect"]))) / 65537,
                        "p_residual": (1 + int(np.sum(null[:, j + 3] >= b["effect"]))) / 65537}
    expected = {
        "experiment": "DIC001_SIDE_DECOMPOSITION", "status": "PASS_POST_CONFIRMATION_DESCRIPTIVE_DECOMPOSITION",
        "inputs": {path.name: sha(path) for path in (clean.SOURCE, clean.PANEL, clean.TARGET, SPEC, PRODUCER)}, "counts": {"panel_rows": len(panel), "targets": 428, "controls": 4143, "folios": len(folios), "permutation_worlds": 65536},
        "blocks": blocks, "additivity": {"raw_max_abs": raw_gap, "residual_max_abs": residual_gap,
            "post_reconciliation_raw_max_abs": float(np.max(np.abs(raw.sum(axis=1) - anchor))),
            "post_reconciliation_residual_max_abs": float(np.max(np.abs(residual.sum(axis=1) - anchor_residual))),
            "frozen_raw_sha256": target["transform"]["raw_score_sha256"], "frozen_residual_sha256": target["transform"]["residual_score_sha256"]},
        "new_confirmation_claim": False, "decision": "DESCRIBE_SIDE_LOCALIZATION_ONLY",
        "claim_ceiling": "Post-confirmation localization of the confirmed DIC001 structural score only; no picture ownership, word, POS, meaning, plaintext, language, cipher, or translation.",
    }
    checks, errors, maximum = compare(expected, json.loads(RESULT.read_text()))
    expected_report = "# DIC001 side decomposition\n\nStatus: **PASS_POST_CONFIRMATION_DESCRIPTIVE_DECOMPOSITION**.\n\n" + "\n".join(f"- {name}: raw **{blocks[name]['raw']['effect']:.6f}** (p **{blocks[name]['p_raw']:.6f}**); residual **{blocks[name]['residual']['effect']:.6f}** (p **{blocks[name]['p_residual']:.6f}**)." for name in NAMES) + "\n\nThis is a post-confirmation localization of the already-confirmed structural score, not a new independent result or a semantic reading.\n"
    checks += 1
    if REPORT.read_text() != expected_report: errors.append("report")
    validation = {"experiment": "DIC001_SIDE_DECOMPOSITION_VALIDATION", "status": "PASS" if not errors else "FAIL", "assertions": checks,
                  "discrepancies": errors, "maximum_numeric_abs_difference": maximum, "reconstructed_blocks": {n: {"raw": blocks[n]["raw"]["effect"], "residual": blocks[n]["residual"]["effect"]} for n in NAMES},
                  "claim_ceiling": expected["claim_ceiling"]}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    OUT_REPORT.write_text("# DIC001 side decomposition validation\n\n" f"Status: **{validation['status']}** with **{checks:,}** checks, **{len(errors)}** discrepancies, and maximum numeric difference **{maximum:.3g}**.\n")
    print(json.dumps(validation, indent=2, sort_keys=True))
    if errors: raise SystemExit(1)


if __name__ == "__main__": main()
