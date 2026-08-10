#!/usr/bin/env python3
"""Target-identity-blind synthetic calibration for the DIC001 one-shot test."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
PANEL = RESULTS / "dic001_drawing_interruption_capacity.tsv"
SPEC = HERE / "DIC001_SYNTHETIC_TARGET_PREFLIGHT_SPEC.md"
SCRIPT = Path(__file__).resolve()
OUTPUT = RESULTS / "dic001_synthetic_target_preflight.json"
REPORT = RESULTS / "dic001_synthetic_target_preflight_report.md"
PANEL_SHA = "e4e1a507211230f362ac4fd34bc0c382442300600132b7deb4e971cab69cfa2c"
CALIBRATION_WORLDS = 8192


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pseudo_length(boundary_id: str, side: str) -> int:
    raw = hashlib.sha256((side + "|" + boundary_id).encode()).digest()
    return 1 + int.from_bytes(raw[:2], "little") % 8


def design_matrix(rows):
    n = len(rows)
    pages = sorted({row["page"] for row in rows})
    page_index = {page: i for i, page in enumerate(pages)}
    columns = [np.ones(n)]
    for page in pages[1:]:
        columns.append(np.fromiter((row["page"] == page for row in rows), dtype=float, count=n))
    position = np.array([float(row["normalized_boundary_position"]) for row in rows])
    columns.extend((position, position * position, position * position * position))
    decile = np.minimum((position * 10).astype(int), 9)
    for value in range(1, 10):
        columns.append((decile == value).astype(float))
    count = np.minimum(np.array([int(row["group_count"]) for row in rows]), 20)
    for value in sorted(set(count))[1:]:
        columns.append((count == value).astype(float))
    left = np.array([pseudo_length(row["boundary_id"], "L") for row in rows])
    right = np.array([pseudo_length(row["boundary_id"], "R") for row in rows])
    # One baseline plus 63 pair cells spans both marginal length effects without
    # the exact collinearity created by also including separate marginals.
    for a in range(1, 9):
        for b in range(1, 9):
            if a != 1 or b != 1:
                columns.append(((left == a) & (right == b)).astype(float))
    matrix = np.column_stack(columns)
    return matrix, left.astype(float), right.astype(float), page_index


def residualize(design, values):
    beta = np.linalg.lstsq(design, values, rcond=None)[0]
    return values - design @ beta


def weights_and_groups(rows):
    pages = defaultdict(list)
    for i, row in enumerate(rows):
        pages[row["page"]].append(i)
    page_counts = Counter(rows[indices[0]]["physical_folio"] for indices in pages.values())
    folios = sorted({row["physical_folio"] for row in rows})
    folio_index = {folio: i for i, folio in enumerate(folios)}
    weight = np.zeros(len(rows))
    page_meta = []
    for page, indices in pages.items():
        target = [i for i in indices if rows[i]["boundary_class"] == "DRAWING_INTERRUPTION"]
        control = [i for i in indices if rows[i]["boundary_class"] == "DEFINITE_SPACE"]
        folio = rows[indices[0]]["physical_folio"]
        scale = 1.0 / (len(folios) * page_counts[folio])
        weight[target] = scale / len(target)
        weight[control] = -scale / len(control)
        first = rows[indices[0]]
        page_meta.append((page, np.array(indices), len(target), scale, folio, first["currier"], first["section"]))
    return weight, page_meta, folios, page_counts, folio_index


def permutation_weights(rows, page_meta, worlds, seed):
    matrix = np.zeros((worlds, len(rows)), dtype=np.float64)
    def build(meta):
        page, indices, k, scale, _, _, _ = meta
        page_seed = int.from_bytes(hashlib.sha256(f"{seed}|{page}".encode()).digest()[:8], "little")
        rng = np.random.default_rng(page_seed)
        priorities = rng.random((worlds, len(indices)), dtype=np.float64)
        chosen = np.argpartition(priorities, k - 1, axis=1)[:, :k]
        local = np.full((worlds, len(indices)), -scale / (len(indices) - k), dtype=np.float64)
        np.put_along_axis(local, chosen, scale / k, axis=1)
        return indices, local
    with ThreadPoolExecutor(max_workers=16) as pool:
        built = pool.map(build, page_meta)
        for indices, local in built:
            matrix[:, indices] = local
    return matrix


def metrics(values, rows, weight, page_meta, folios):
    effect = float(weight @ values)
    page_contrast = {}
    page_lookup = {}
    for page, indices, _, _, folio, currier, section in page_meta:
        mask = np.array([rows[i]["boundary_class"] == "DRAWING_INTERRUPTION" for i in indices])
        page_contrast[page] = float(values[indices][mask].mean() - values[indices][~mask].mean())
        page_lookup[page] = (folio, currier, section)
    folio_values = {}
    for folio in folios:
        vals = [value for page, value in page_contrast.items() if page_lookup[page][0] == folio]
        folio_values[folio] = float(np.mean(vals))

    def subset(field, accepted):
        selected = []
        for page, value in page_contrast.items():
            folio, currier, section = page_lookup[page]
            candidate = currier if field == "currier" else section
            if accepted(candidate):
                selected.append((folio, value))
        grouped = defaultdict(list)
        for folio, value in selected:
            grouped[folio].append(value)
        return float(np.mean([np.mean(values) for values in grouped.values()])) if grouped else float("nan")

    absolute = sum(abs(value) for value in folio_values.values())
    return {
        "effect": effect,
        "positive_folios": sum(value > 0 for value in folio_values.values()),
        "currier_A": subset("currier", lambda value: value == "A"),
        "currier_B": subset("currier", lambda value: value == "B"),
        "section_H": subset("section", lambda value: value == "H"),
        "section_non_H": subset("section", lambda value: value != "H"),
        "minimum_deletion_effect": min(float(np.mean([v for f, v in folio_values.items() if f != deleted])) for deleted in folios),
        "maximum_absolute_folio_concentration": max(abs(value) for value in folio_values.values()) / absolute if absolute else 1.0,
    }


def gate(raw, residual, null_raw, null_residual):
    p_raw = (1 + int(np.sum(null_raw >= raw["effect"]))) / (1 + len(null_raw))
    p_residual = (1 + int(np.sum(null_residual >= residual["effect"]))) / (1 + len(null_residual))
    gates = {
        "raw_effect_at_least_010": raw["effect"] >= 0.10,
        "residual_effect_at_least_010": residual["effect"] >= 0.10,
        "raw_p_at_most_001": p_raw <= 0.01,
        "residual_p_at_most_001": p_residual <= 0.01,
        "positive_residual_folios_at_least_39": residual["positive_folios"] >= 39,
        "currier_A_B_residual_at_least_010": residual["currier_A"] >= 0.10 and residual["currier_B"] >= 0.10,
        "H_and_non_H_residual_at_least_010": residual["section_H"] >= 0.10 and residual["section_non_H"] >= 0.10,
        "all_residual_deletions_positive": residual["minimum_deletion_effect"] > 0,
        "residual_folio_concentration_at_most_015": residual["maximum_absolute_folio_concentration"] <= 0.15,
    }
    return {"raw": raw, "residual": residual, "p_raw": p_raw, "p_residual": p_residual, "gates": gates, "passes": all(gates.values())}


def main():
    if sha256(PANEL) != PANEL_SHA:
        raise SystemExit("DIC001 masked panel drift")
    with PANEL.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 4571
    assert Counter(row["boundary_class"] for row in rows) == {"DEFINITE_SPACE": 4143, "DRAWING_INTERRUPTION": 428}
    design, left, right, _ = design_matrix(rows)
    weight, page_meta, folios, _, _ = weights_and_groups(rows)
    assert len(page_meta) == 87 and len(folios) == 59
    permutation = permutation_weights(rows, page_meta, CALIBRATION_WORLDS, 76001002)
    rng = np.random.default_rng(76001003)

    columns = []
    identities = []
    target = np.array([row["boundary_class"] == "DRAWING_INTERRUPTION" for row in rows], dtype=float)
    position = np.array([float(row["normalized_boundary_position"]) for row in rows])
    pages = sorted({row["page"] for row in rows})
    page_noise_basis = {page: rng.normal() for page in pages}
    page_noise = np.array([page_noise_basis[row["page"]] for row in rows])
    selected_folios = folios[:8]
    for world in range(64):
        columns.append(rng.normal(size=len(rows)))
        identities.append(("NULL", "0.00", world))
    for amplitude in (0.50, 0.75):
        for world in range(8):
            columns.append(rng.normal(scale=0.50, size=len(rows)) + amplitude * target)
            identities.append(("DISTRIBUTED", f"{amplitude:.2f}", world))
    for world, folio in enumerate(selected_folios):
        mask = np.array([row["physical_folio"] == folio for row in rows])
        columns.append(rng.normal(scale=0.25, size=len(rows)) + 3.0 * target * mask)
        identities.append(("ONE_FOLIO", "3.00", world))
    for world in range(8):
        h = np.array([row["section"] == "H" for row in rows])
        columns.append(rng.normal(scale=0.25, size=len(rows)) + 1.0 * target * h)
        identities.append(("ONE_SECTION", "1.00", world))
    for world in range(8):
        columns.append(rng.normal(scale=0.25, size=len(rows)) + 3.0 * page_noise)
        identities.append(("PAGE_ONLY", "3.00", world))
    for world in range(8):
        columns.append(rng.normal(scale=0.25, size=len(rows)) + 3.0 * position)
        identities.append(("POSITION_ONLY", "3.00", world))
    for world in range(8):
        columns.append(rng.normal(scale=0.25, size=len(rows)) + 0.5 * left + 0.5 * right)
        identities.append(("LENGTH_ONLY", "1.00", world))
    for world in range(8):
        columns.append(rng.normal(scale=0.50, size=len(rows)) - 0.75 * target)
        identities.append(("REVERSED", "0.75", world))

    raw_matrix = np.column_stack(columns)
    residual_matrix = residualize(design, raw_matrix)
    null_raw = permutation @ raw_matrix
    null_residual = permutation @ residual_matrix
    records = []
    for j, (family, amplitude, world) in enumerate(identities):
        raw = metrics(raw_matrix[:, j], rows, weight, page_meta, folios)
        residual = metrics(residual_matrix[:, j], rows, weight, page_meta, folios)
        records.append({"family": family, "amplitude": amplitude, "world": world, **gate(raw, residual, null_raw[:, j], null_residual[:, j])})
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
    status = "PASS_TARGET_FREE_SYNTHETIC_CALIBRATION" if all(acceptance.values()) else "STOP_SYNTHETIC_CALIBRATION"
    result = {
        "experiment": "DIC001_SYNTHETIC_TARGET_PREFLIGHT",
        "status": status,
        "inputs": {path.name: sha256(path) for path in (PANEL, SPEC, SCRIPT)},
        "counts": {"rows": len(rows), "targets": int(target.sum()), "controls": int(len(rows) - target.sum()), "pages": len(page_meta), "folios": len(folios), "synthetic_records": len(records), "permutation_worlds": CALIBRATION_WORLDS},
        "design": {"columns": design.shape[1], "rank": int(np.linalg.matrix_rank(design)), "synthetic_length_source": "SHA256_BOUNDARY_ID_COORDINATE_ONLY"},
        "pass_counts": pass_counts,
        "acceptance": acceptance,
        "records": records,
        "target_structural_identity_accessed": False,
        "drawing_target_score_computed": False,
        "decision": "AUTHORIZE_INDEPENDENT_RECONSTRUCTION_ONLY" if all(acceptance.values()) else "STOP",
        "claim_ceiling": "Synthetic decision calibration on the masked DIC001 topology only; no drawing result, ownership, word, sound, POS, meaning, plaintext, language, cipher, or translation.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# DIC001 synthetic target preflight\n\n"
        f"Status: **{status}**.\n\n"
        f"The target-blind suite evaluated **{len(records)}** synthetic records against **{CALIBRATION_WORLDS:,}** fixed-count within-page assignments on the masked **{len(rows):,}**-row topology. Pass counts were: "
        + ", ".join(f"{key}={value}" for key, value in sorted(pass_counts.items()))
        + ".\n\nNo drawing-boundary structural identity or score was accessed.\n"
    )
    print(json.dumps({"status": status, "pass_counts": pass_counts, "acceptance": acceptance}, indent=2, sort_keys=True))
    if not all(acceptance.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
