#!/usr/bin/env python3
"""Independent, nonimporting reconstruction of the DIC001 synthetic preflight."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
RES = ROOT / "results"
PANEL = RES / "dic001_drawing_interruption_capacity.tsv"
SPEC = ROOT / "DIC001_SYNTHETIC_TARGET_PREFLIGHT_SPEC.md"
PRODUCER = ROOT / "run_dic001_synthetic_target_preflight.py"
RESULT = RES / "dic001_synthetic_target_preflight.json"
REPORT = RES / "dic001_synthetic_target_preflight_report.md"
OUT = RES / "dic001_synthetic_target_preflight_validation.json"
OUT_REPORT = RES / "dic001_synthetic_target_preflight_validation_report.md"
HASHES = {
    PANEL: "e4e1a507211230f362ac4fd34bc0c382442300600132b7deb4e971cab69cfa2c",
    SPEC: "bdb36d2fd234ef372695cbf7004d7b257c280ba087a0a54d61c9e6ef03652822",
    PRODUCER: "6731c1069d0e8261c8b7a25c81c631d92da96ba4b9b24eb76dc20d2df271fc0d",
    RESULT: "919a8b69791d362155a18e8d8ca1cd79f7be21e4da07e349fcc3ad849234c1c0",
    REPORT: "0a938398c1c25e24cda2b976e27b28d96311b0504f286c2722145c7956147433",
}
WORLDS = 8192


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fake_length(boundary, side):
    return 1 + int.from_bytes(hashlib.sha256(f"{side}|{boundary}".encode()).digest()[:2], "little") % 8


def nuisance_basis(rows):
    n = len(rows)
    columns = [np.ones(n)]
    pages = sorted({r["page"] for r in rows})
    for page in pages[1:]:
        columns.append(np.array([r["page"] == page for r in rows], dtype=float))
    r = np.array([float(x["normalized_boundary_position"]) for x in rows])
    columns += [r, r ** 2, r ** 3]
    bins = np.minimum((10 * r).astype(np.int64), 9)
    columns += [(bins == value).astype(float) for value in range(1, 10)]
    counts = np.minimum(np.array([int(x["group_count"]) for x in rows]), 20)
    columns += [(counts == value).astype(float) for value in sorted(set(counts))[1:]]
    left = np.array([fake_length(x["boundary_id"], "L") for x in rows])
    right = np.array([fake_length(x["boundary_id"], "R") for x in rows])
    columns += [((left == a) & (right == b)).astype(float)
                for a in range(1, 9) for b in range(1, 9) if (a, b) != (1, 1)]
    return np.column_stack(columns), left.astype(float), right.astype(float)


def topology(rows):
    page_rows = defaultdict(list)
    for i, row in enumerate(rows):
        page_rows[row["page"]].append(i)
    folios = sorted({row["physical_folio"] for row in rows})
    page_count = Counter(rows[idx[0]]["physical_folio"] for idx in page_rows.values())
    true_weight = np.zeros(len(rows))
    meta = []
    for page, idx_list in page_rows.items():
        idx = np.array(idx_list)
        targets = np.array([i for i in idx if rows[i]["boundary_class"] == "DRAWING_INTERRUPTION"])
        controls = np.array([i for i in idx if rows[i]["boundary_class"] == "DEFINITE_SPACE"])
        first = rows[idx[0]]
        scale = 1 / (len(folios) * page_count[first["physical_folio"]])
        true_weight[targets] = scale / len(targets)
        true_weight[controls] = -scale / len(controls)
        meta.append({"page": page, "indices": idx, "k": len(targets), "scale": scale,
                     "folio": first["physical_folio"], "currier": first["currier"], "section": first["section"]})
    return true_weight, meta, folios


def shuffled_weights(meta, n_rows):
    output = np.zeros((WORLDS, n_rows))

    def one_page(item):
        key = int.from_bytes(hashlib.sha256(f"76001002|{item['page']}".encode()).digest()[:8], "little")
        random = np.random.default_rng(key).random((WORLDS, len(item["indices"])))
        chosen = np.argpartition(random, item["k"] - 1, axis=1)[:, :item["k"]]
        local = np.full(random.shape, -item["scale"] / (len(item["indices"]) - item["k"]))
        np.put_along_axis(local, chosen, item["scale"] / item["k"], axis=1)
        return item["indices"], local

    with ThreadPoolExecutor(max_workers=16) as executor:
        for indices, local in executor.map(one_page, meta):
            output[:, indices] = local
    return output


def diagnostics(vector, rows, true_weight, meta, folios):
    page_values = {}
    for item in meta:
        idx = item["indices"]
        chosen = np.array([rows[i]["boundary_class"] == "DRAWING_INTERRUPTION" for i in idx])
        page_values[item["page"]] = float(vector[idx][chosen].mean() - vector[idx][~chosen].mean())
    folio_values = {folio: float(np.mean([page_values[x["page"]] for x in meta if x["folio"] == folio])) for folio in folios}

    def subset(predicate):
        grouped = defaultdict(list)
        for item in meta:
            if predicate(item):
                grouped[item["folio"]].append(page_values[item["page"]])
        return float(np.mean([np.mean(values) for values in grouped.values()]))

    denominator = sum(abs(x) for x in folio_values.values())
    return {
        "effect": float(true_weight @ vector),
        "positive_folios": sum(x > 0 for x in folio_values.values()),
        "currier_A": subset(lambda x: x["currier"] == "A"),
        "currier_B": subset(lambda x: x["currier"] == "B"),
        "section_H": subset(lambda x: x["section"] == "H"),
        "section_non_H": subset(lambda x: x["section"] != "H"),
        "minimum_deletion_effect": min(float(np.mean([x for folio, x in folio_values.items() if folio != deletion])) for deletion in folios),
        "maximum_absolute_folio_concentration": max(abs(x) for x in folio_values.values()) / denominator if denominator else 1.0,
    }


def decision(raw, residual, raw_null, residual_null):
    p_raw = (1 + int(np.sum(raw_null >= raw["effect"]))) / 8193
    p_residual = (1 + int(np.sum(residual_null >= residual["effect"]))) / 8193
    gates = {
        "raw_effect_at_least_010": raw["effect"] >= 0.10,
        "residual_effect_at_least_010": residual["effect"] >= 0.10,
        "raw_p_at_most_001": p_raw <= 0.01,
        "residual_p_at_most_001": p_residual <= 0.01,
        "positive_residual_folios_at_least_39": residual["positive_folios"] >= 39,
        "currier_A_B_residual_at_least_010": min(residual["currier_A"], residual["currier_B"]) >= 0.10,
        "H_and_non_H_residual_at_least_010": min(residual["section_H"], residual["section_non_H"]) >= 0.10,
        "all_residual_deletions_positive": residual["minimum_deletion_effect"] > 0,
        "residual_folio_concentration_at_most_015": residual["maximum_absolute_folio_concentration"] <= 0.15,
    }
    return {"raw": raw, "residual": residual, "p_raw": p_raw, "p_residual": p_residual,
            "gates": gates, "passes": all(gates.values())}


def reconstruct():
    with PANEL.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 4571
    classes = Counter(r["boundary_class"] for r in rows)
    assert classes == {"DEFINITE_SPACE": 4143, "DRAWING_INTERRUPTION": 428}
    basis, left, right = nuisance_basis(rows)
    true_weight, meta, folios = topology(rows)
    null_weights = shuffled_weights(meta, len(rows))
    rng = np.random.default_rng(76001003)
    target = np.array([r["boundary_class"] == "DRAWING_INTERRUPTION" for r in rows], dtype=float)
    position = np.array([float(r["normalized_boundary_position"]) for r in rows])
    page_random = {page: rng.normal() for page in sorted({r["page"] for r in rows})}
    page_only = np.array([page_random[r["page"]] for r in rows])
    matrix, ids = [], []
    for world in range(64):
        matrix.append(rng.normal(size=len(rows))); ids.append(("NULL", "0.00", world))
    for amplitude in (0.50, 0.75):
        for world in range(8):
            matrix.append(rng.normal(scale=.50, size=len(rows)) + amplitude * target)
            ids.append(("DISTRIBUTED", f"{amplitude:.2f}", world))
    for world, folio in enumerate(folios[:8]):
        selected = np.array([r["physical_folio"] == folio for r in rows])
        matrix.append(rng.normal(scale=.25, size=len(rows)) + 3 * target * selected)
        ids.append(("ONE_FOLIO", "3.00", world))
    for world in range(8):
        herbal = np.array([r["section"] == "H" for r in rows])
        matrix.append(rng.normal(scale=.25, size=len(rows)) + target * herbal)
        ids.append(("ONE_SECTION", "1.00", world))
    for world in range(8):
        matrix.append(rng.normal(scale=.25, size=len(rows)) + 3 * page_only)
        ids.append(("PAGE_ONLY", "3.00", world))
    for world in range(8):
        matrix.append(rng.normal(scale=.25, size=len(rows)) + 3 * position)
        ids.append(("POSITION_ONLY", "3.00", world))
    for world in range(8):
        matrix.append(rng.normal(scale=.25, size=len(rows)) + .5 * left + .5 * right)
        ids.append(("LENGTH_ONLY", "1.00", world))
    for world in range(8):
        matrix.append(rng.normal(scale=.50, size=len(rows)) - .75 * target)
        ids.append(("REVERSED", "0.75", world))
    raw = np.column_stack(matrix)
    residual = raw - basis @ np.linalg.lstsq(basis, raw, rcond=None)[0]
    permuted_raw, permuted_residual = null_weights @ raw, null_weights @ residual
    records = []
    for j, (family, amplitude, world) in enumerate(ids):
        records.append({"family": family, "amplitude": amplitude, "world": world,
                        **decision(diagnostics(raw[:, j], rows, true_weight, meta, folios),
                                   diagnostics(residual[:, j], rows, true_weight, meta, folios),
                                   permuted_raw[:, j], permuted_residual[:, j])})
    grouped = defaultdict(list)
    for record in records:
        grouped[(record["family"], record["amplitude"])].append(record["passes"])
    pass_counts = {family + "@" + amplitude: sum(values) for (family, amplitude), values in sorted(grouped.items())}
    acceptance = {
        "null_zero_of_64": pass_counts["NULL@0.00"] == 0,
        "distributed_050_at_least_6_of_8": pass_counts["DISTRIBUTED@0.50"] >= 6,
        "distributed_075_8_of_8": pass_counts["DISTRIBUTED@0.75"] == 8,
        "one_folio_0_of_8": pass_counts["ONE_FOLIO@3.00"] == 0,
        "one_section_0_of_8": pass_counts["ONE_SECTION@1.00"] == 0,
        "page_only_0_of_8": pass_counts["PAGE_ONLY@3.00"] == 0,
        "position_only_0_of_8": pass_counts["POSITION_ONLY@3.00"] == 0,
        "length_only_0_of_8": pass_counts["LENGTH_ONLY@1.00"] == 0,
        "reversed_0_of_8": pass_counts["REVERSED@0.75"] == 0,
    }
    passed = all(acceptance.values())
    reconstructed = {
        "experiment": "DIC001_SYNTHETIC_TARGET_PREFLIGHT",
        "status": "PASS_TARGET_FREE_SYNTHETIC_CALIBRATION" if passed else "STOP_SYNTHETIC_CALIBRATION",
        "inputs": {path.name: sha(path) for path in (PANEL, SPEC, PRODUCER)},
        "counts": {"rows": len(rows), "targets": classes["DRAWING_INTERRUPTION"], "controls": classes["DEFINITE_SPACE"],
                   "pages": len(meta), "folios": len(folios), "synthetic_records": len(records), "permutation_worlds": WORLDS},
        "design": {"columns": basis.shape[1], "rank": int(np.linalg.matrix_rank(basis)),
                   "synthetic_length_source": "SHA256_BOUNDARY_ID_COORDINATE_ONLY"},
        "pass_counts": pass_counts, "acceptance": acceptance, "records": records,
        "target_structural_identity_accessed": False, "drawing_target_score_computed": False,
        "decision": "AUTHORIZE_INDEPENDENT_RECONSTRUCTION_ONLY" if passed else "STOP",
        "claim_ceiling": "Synthetic decision calibration on the masked DIC001 topology only; no drawing result, ownership, word, sound, POS, meaning, plaintext, language, cipher, or translation.",
    }
    expected_report = (
        "# DIC001 synthetic target preflight\n\n"
        f"Status: **{reconstructed['status']}**.\n\n"
        f"The target-blind suite evaluated **{len(records)}** synthetic records against **{WORLDS:,}** fixed-count within-page assignments on the masked **{len(rows):,}**-row topology. Pass counts were: "
        + ", ".join(f"{key}={value}" for key, value in sorted(pass_counts.items()))
        + ".\n\nNo drawing-boundary structural identity or score was accessed.\n"
    )
    return reconstructed, expected_report


def deep_compare(a, b, name="root"):
    count, errors, maximum = 1, [], 0.0
    if type(a) is not type(b):
        return count, [f"{name}: type mismatch"], maximum
    if isinstance(a, dict):
        if set(a) != set(b): errors.append(f"{name}: keys mismatch")
        for key in sorted(set(a) & set(b)):
            c, e, m = deep_compare(a[key], b[key], f"{name}.{key}")
            count += c; errors += e; maximum = max(maximum, m)
    elif isinstance(a, list):
        if len(a) != len(b): errors.append(f"{name}: length mismatch")
        for i, (x, y) in enumerate(zip(a, b)):
            c, e, m = deep_compare(x, y, f"{name}[{i}]")
            count += c; errors += e; maximum = max(maximum, m)
    elif isinstance(a, float):
        maximum = abs(a - b)
        if maximum > 2e-14: errors.append(f"{name}: delta {maximum:.3g}")
    elif a != b:
        errors.append(f"{name}: value mismatch")
    return count, errors, maximum


def main():
    drift = [path.name for path, expected in HASHES.items() if sha(path) != expected]
    if drift: raise SystemExit("frozen input drift: " + ",".join(drift))
    reconstructed, report = reconstruct()
    stored = json.loads(RESULT.read_text())
    checks, errors, maximum = deep_compare(reconstructed, stored)
    checks += 1
    if REPORT.read_text() != report: errors.append("report mismatch")
    checks += len(HASHES)
    validation = {
        "experiment": "DIC001_SYNTHETIC_TARGET_PREFLIGHT_VALIDATION",
        "status": "PASS" if not errors else "FAIL",
        "assertions": checks,
        "discrepancies": errors,
        "maximum_numeric_abs_difference": maximum,
        "reconstructed_records": len(reconstructed["records"]),
        "reconstructed_pass_counts": reconstructed["pass_counts"],
        "bound_sha256": {path.name: expected for path, expected in HASHES.items()},
        "target_structural_identity_accessed": False,
        "drawing_target_score_computed": False,
        "decision": "AUTHORIZE_TARGET_FREEZE" if not errors else "STOP",
        "claim_ceiling": reconstructed["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    OUT_REPORT.write_text(
        "# DIC001 synthetic preflight validation\n\n"
        f"Status: **{validation['status']}** with **{checks:,}** checks and **{len(errors)}** discrepancies.\n\n"
        f"The independent implementation reconstructed all **{len(reconstructed['records'])}** synthetic records and **{WORLDS:,}** assignments with maximum numeric difference **{maximum:.3g}**.\n\n"
        "No drawing-boundary structural identity or score was accessed.\n"
    )
    print(json.dumps(validation, indent=2, sort_keys=True))
    if errors: raise SystemExit(1)


if __name__ == "__main__":
    main()
