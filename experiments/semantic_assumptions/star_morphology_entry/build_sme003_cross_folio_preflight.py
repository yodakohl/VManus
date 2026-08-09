#!/usr/bin/env python3
"""Target-blind capacity build for SME003 cross-folio concordance."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MATRIX = HERE / "anonymous_paragraph_matrix.tsv"
INVENTORY = HERE / "anonymous_feature_inventory.json"
SPEC = HERE / "SME003_CROSS_FOLIO_PREFLIGHT_SPEC.md"
SELF = HERE / "build_sme003_cross_folio_preflight.py"
OUT = HERE / "sme003_cross_folio_preflight.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/sme003_cross_folio_preflight.md"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
EXPECTED_HASHES = {
    "anonymous_paragraph_matrix.tsv": "b246456b181b07e847c6d5a49b959b0346eff6a4c6febb8a543de104c505a26a",
    "anonymous_feature_inventory.json": "088232b431b4b9746bb94a08328cb969fb7c21c6a28cd112286da40d6429fea5",
}
META = {"unit_id", "page", "physical_folio", "star_ordinal", "locus", "edition"}
SCALE_TOL = 1e-10
NUM_TOL = 1e-15
TARGET_ARTIFACTS = (
    HERE / "TARGET_RESULT.json",
    HERE / "SME001_TARGET_RESULT.json",
    HERE / "SME003_TARGET_RESULT.json",
    HERE / "sme001_target_result.tsv",
    HERE / "sme003_target_result.tsv",
    ROOT / "experiments/semantic_assumptions/results/sme001_star_morphology_paragraph_result.md",
    ROOT / "experiments/semantic_assumptions/results/sme003_cross_folio_result.md",
)


def sha256(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def array_sha256(values: np.ndarray) -> str:
    canonical = np.asarray(values, dtype="<f8", order="C")
    return hashlib.sha256(canonical.tobytes()).hexdigest()


def centered_by_page(values: np.ndarray, pages: np.ndarray) -> np.ndarray:
    answer = np.empty_like(values, dtype=np.float64)
    for page in sorted(set(pages.tolist())):
        mask = pages == page
        answer[mask] = values[mask] - np.mean(values[mask], axis=0, keepdims=True)
    return answer


def analytic_shrinkage(train: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, dict]:
    n, p = train.shape
    covariance = (train.T @ train) / n
    mu = float(np.trace(covariance) / p)
    alpha = float(np.mean(covariance * covariance))
    denominator = float((n + 1) * (alpha - mu * mu / p))
    rho = 1.0 if denominator <= NUM_TOL else min(1.0, (alpha + mu * mu) / denominator)
    shrunk = (1.0 - rho) * covariance + rho * mu * np.eye(p)
    eigenvalues = np.linalg.eigvalsh(shrunk)
    weight = np.linalg.inv(shrunk)
    weight *= p / float(np.trace(weight))
    diagnostics = {
        "n": n,
        "p": p,
        "mu": mu,
        "alpha": alpha,
        "denominator": denominator,
        "rho": rho,
        "covariance_min_eigenvalue": float(eigenvalues[0]),
        "covariance_max_eigenvalue": float(eigenvalues[-1]),
        "covariance_condition": float(eigenvalues[-1] / eigenvalues[0]),
        "weight_symmetry_max_abs": float(np.max(np.abs(weight - weight.T))),
        "weight_trace": float(np.trace(weight)),
        "weight_min_eigenvalue": float(np.linalg.eigvalsh(weight)[0]),
    }
    return shrunk, weight, rho, diagnostics


def main() -> None:
    actual_hashes = {path.name: sha256(path) for path in (MATRIX, INVENTORY)}
    if actual_hashes != EXPECTED_HASHES:
        raise RuntimeError(f"input hash mismatch: {actual_hashes}")
    absent_before = {str(path.relative_to(ROOT)): not path.exists() for path in TARGET_ARTIFACTS}
    if not all(absent_before.values()):
        raise RuntimeError("target artifact exists before target-blind preflight")

    with MATRIX.open(encoding="utf-8", newline="") as handle:
        raw_rows = [row for row in csv.DictReader(handle, delimiter="\t") if row["page"] != "f106r"]
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    features = [field for field in raw_rows[0] if field not in META]
    if features != inventory["all_features"] or len(features) != 84:
        raise RuntimeError("feature inventory/order mismatch")

    units = sorted({row["unit_id"] for row in raw_rows})
    lookup = {(row["unit_id"], row["edition"]): row for row in raw_rows}
    if len(units) != 156 or len(raw_rows) != 468 or len(lookup) != 468:
        raise RuntimeError("matrix cardinality mismatch")
    first_rows = [lookup[(unit, EDITIONS[0])] for unit in units]
    pages = np.asarray([row["page"] for row in first_rows], dtype=object)
    folios = np.asarray([row["physical_folio"] for row in first_rows], dtype=object)
    ordinals = np.asarray([int(row["star_ordinal"]) for row in first_rows], dtype=np.int64)
    page_sizes = {page: int(np.sum(pages == page)) for page in sorted(set(pages.tolist()))}
    for page, size in page_sizes.items():
        page_ordinals = sorted(ordinals[pages == page].tolist())
        if page_ordinals != list(range(1, size + 1)):
            raise RuntimeError(f"noncontiguous ordinal sequence on {page}")
    relative = np.asarray([
        (ordinal - 0.5) / page_sizes[page] for page, ordinal in zip(pages, ordinals)
    ], dtype=np.float64)
    absolute = (ordinals.astype(np.float64) - 0.5) / 16.0
    early = np.asarray([
        ordinal <= page_sizes[page] / 2.0 for page, ordinal in zip(pages, ordinals)
    ], dtype=np.float64)
    quarter = np.minimum((relative * 4).astype(np.int64), 3)
    nuisance_formal = np.stack([
        relative,
        relative ** 2,
        relative ** 3,
        absolute,
        absolute ** 2,
        absolute ** 3,
        (ordinals % 2 == 1).astype(np.float64),
        early,
        (quarter == 1).astype(np.float64),
        (quarter == 2).astype(np.float64),
        (quarter == 3).astype(np.float64),
    ], axis=1)
    nuisance_formal = centered_by_page(nuisance_formal, pages)

    values = np.empty((len(units), len(EDITIONS), len(features)), dtype=np.float64)
    for unit_index, unit in enumerate(units):
        for edition_index, edition in enumerate(EDITIONS):
            row = lookup[(unit, edition)]
            first = first_rows[unit_index]
            if (
                row["page"] != pages[unit_index]
                or row["physical_folio"] != folios[unit_index]
                or row["star_ordinal"] != first["star_ordinal"]
                or row["locus"] != first["locus"]
            ):
                raise RuntimeError("alternate-reading metadata drift")
            values[unit_index, edition_index] = [float(row[feature]) for feature in features]
    if not np.isfinite(values).all():
        raise RuntimeError("nonfinite anonymous matrix")

    root_start = len(inventory["formal_features"])
    if root_start != 34 or len(features) - root_start != 50:
        raise RuntimeError("formal/root feature partition mismatch")
    word_index = features.index("PARA_WORD_COUNT")
    unique_folios = sorted(set(folios.tolist()))
    if len(unique_folios) != 7 or len(page_sizes) != 12:
        raise RuntimeError("page/folio capacity mismatch")

    fold_residuals: dict[tuple[str, str], np.ndarray] = {}
    scale_table: dict[tuple[str, str], np.ndarray] = {}
    fold_rows = {}
    for held in unique_folios:
        train_mask = folios != held
        held_mask = ~train_mask
        fold_rows[held] = {
            "train_units": int(np.sum(train_mask)),
            "held_units": int(np.sum(held_mask)),
            "train_pages": len(set(pages[train_mask].tolist())),
            "held_pages": len(set(pages[held_mask].tolist())),
        }
        for edition_index, edition in enumerate(EDITIONS):
            centered_values = centered_by_page(values[:, edition_index, :], pages)
            log_length = np.log1p(values[:, edition_index, word_index])
            length_design = np.stack([log_length, log_length ** 2, log_length ** 3], axis=1)
            length_design = centered_by_page(length_design, pages)
            residual = np.empty_like(centered_values)
            for feature_index in range(len(features)):
                design = nuisance_formal
                if feature_index >= root_start:
                    design = np.concatenate([nuisance_formal, length_design], axis=1)
                beta, *_ = np.linalg.lstsq(design[train_mask], centered_values[train_mask, feature_index], rcond=None)
                residual[:, feature_index] = centered_values[:, feature_index] - design @ beta
            scales = np.sqrt(np.mean(residual[train_mask] ** 2, axis=0))
            fold_residuals[(held, edition)] = residual
            scale_table[(held, edition)] = scales

    eligible_mask = np.ones(len(features), dtype=bool)
    for scales in scale_table.values():
        eligible_mask &= np.isfinite(scales) & (scales > SCALE_TOL)
    eligible = [feature for feature, keep in zip(features, eligible_mask) if keep]
    formal_eligible = [feature for feature in eligible if feature in inventory["formal_features"]]
    root_eligible = [feature for feature in eligible if feature not in inventory["formal_features"]]

    transforms = {}
    all_diagnostics_ok = True
    for held in unique_folios:
        train_mask = folios != held
        for edition in EDITIONS:
            scales = scale_table[(held, edition)][eligible_mask]
            standardized = fold_residuals[(held, edition)][:, eligible_mask] / scales
            shrunk, weight, rho, diagnostics = analytic_shrinkage(standardized[train_mask])
            diagnostics.update({
                "eligible_scale_min": float(np.min(scales)),
                "eligible_scale_max": float(np.max(scales)),
                "finite_standardized": bool(np.isfinite(standardized).all()),
                "finite_covariance": bool(np.isfinite(shrunk).all()),
                "finite_weight": bool(np.isfinite(weight).all()),
                "standardized_matrix_sha256": array_sha256(standardized),
                "weight_matrix_sha256": array_sha256(weight),
            })
            key = f"{held}__{edition}"
            transforms[key] = diagnostics
            all_diagnostics_ok &= (
                diagnostics["finite_standardized"]
                and diagnostics["finite_covariance"]
                and diagnostics["finite_weight"]
                and diagnostics["covariance_min_eigenvalue"] > NUM_TOL
                and diagnostics["weight_min_eigenvalue"] > NUM_TOL
                and diagnostics["weight_symmetry_max_abs"] <= 1e-10
                and abs(diagnostics["weight_trace"] - len(eligible)) <= 1e-8
            )

    absent_after = {str(path.relative_to(ROOT)): not path.exists() for path in TARGET_ARTIFACTS}
    gates = {
        "input_hashes": actual_hashes == EXPECTED_HASHES,
        "exact_matrix_contract": len(units) == 156 and len(raw_rows) == 468 and len(features) == 84,
        "exact_page_folio_contract": len(page_sizes) == 12 and len(unique_folios) == 7,
        "formal_capacity_at_least_24": len(formal_eligible) >= 24,
        "root_capacity_at_least_32": len(root_eligible) >= 32,
        "all_transform_diagnostics": bool(all_diagnostics_ok),
        "target_artifacts_absent_before": all(absent_before.values()),
        "target_artifacts_absent_after": all(absent_after.values()),
    }
    status = "PASS_TARGET_BLIND_CROSS_FOLIO_PREFLIGHT" if all(gates.values()) else "STOP_TARGET_BLIND_CROSS_FOLIO_PREFLIGHT"
    payload = {
        "experiment": "SME003",
        "status": status,
        "input_hashes": actual_hashes,
        "source_hashes": {
            "SME003_CROSS_FOLIO_PREFLIGHT_SPEC.md": sha256(SPEC),
            "build_sme003_cross_folio_preflight.py": sha256(SELF),
        },
        "target_rows_accessed": False,
        "morphology_fields_accessed": False,
        "target_join_performed": False,
        "units": len(units),
        "rows": len(raw_rows),
        "pages": page_sizes,
        "folios": unique_folios,
        "features_input": len(features),
        "features_eligible": len(eligible),
        "formal_eligible": formal_eligible,
        "root_eligible": root_eligible,
        "ineligible": [feature for feature, keep in zip(features, eligible_mask) if not keep],
        "fold_rows": fold_rows,
        "transforms": transforms,
        "gates": gates,
        "target_artifact_absence_before": absent_before,
        "target_artifact_absence_after": absent_after,
        "decision": "GO_TO_TARGET_FREE_SYNTHETIC_DESIGN" if all(gates.values()) else "STOP_BEFORE_SYNTHETIC_DESIGN",
        "claim_ceiling": "target-blind cross-folio transform capacity only; no morphology association or meaning",
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rho_values = [value["rho"] for value in transforms.values()]
    conditions = [value["covariance_condition"] for value in transforms.values()]
    REPORT.write_text("\n".join([
        "# SME003 target-blind cross-folio preflight", "",
        f"**{status}**", "",
        f"The frozen anonymous matrix retains {len(eligible)}/84 features: {len(formal_eligible)} formal and {len(root_eligible)} root-rate features. The seven physical folios, 12 pages, 156 units, 468 alternate-reading rows, and every input hash match the freeze.", "",
        f"Across the 21 held-folio/reading transforms, analytic shrinkage ranges from {min(rho_values):.6f} to {max(rho_values):.6f}; shrunk covariance condition numbers range from {min(conditions):.6f} to {max(conditions):.6f}. Every standardized matrix, covariance, and inverse is finite and positive definite.", "",
        "No ray, tail, core, color, or other morphology row was opened or joined, and every target artifact remained absent. This authorizes only a separately frozen synthetic calibration of cross-folio concordance. It supplies no association, meaning, lexeme, plaintext, language, or translation.", "",
        "## Reproduction", "", "```bash",
        "./vpy experiments/semantic_assumptions/star_morphology_entry/build_sme003_cross_folio_preflight.py",
        "```",
    ]) + "\n", encoding="utf-8")
    if not all(gates.values()):
        raise SystemExit(status)


if __name__ == "__main__":
    main()
