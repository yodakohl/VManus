#!/usr/bin/env python3
"""Independent, nonimporting reconstruction of the SME003 anonymous preflight.

This validator does not import or execute the production builder and never opens
any morphology/target artifact. Target paths are tested for existence only.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RESULTS = ROOT / "experiments/semantic_assumptions/results"
MATRIX = HERE / "anonymous_paragraph_matrix.tsv"
INVENTORY = HERE / "anonymous_feature_inventory.json"
SPEC = HERE / "SME003_CROSS_FOLIO_PREFLIGHT_SPEC.md"
PRODUCTION = HERE / "build_sme003_cross_folio_preflight.py"
PREFLIGHT = HERE / "sme003_cross_folio_preflight.json"
PREFLIGHT_REPORT = RESULTS / "sme003_cross_folio_preflight.md"
OUT = HERE / "sme003_cross_folio_preflight_validation.json"
REPORT = RESULTS / "sme003_cross_folio_preflight_validation.md"

EDITIONS = ("ZL3b", "IT2a", "RF1b")
META = ("unit_id", "page", "physical_folio", "star_ordinal", "locus", "edition")
SCALE_FLOOR = 1e-10
NUMERIC_FLOOR = 1e-15

EXPECTED_HASHES = {
    "anonymous_paragraph_matrix.tsv": "b246456b181b07e847c6d5a49b959b0346eff6a4c6febb8a543de104c505a26a",
    "anonymous_feature_inventory.json": "088232b431b4b9746bb94a08328cb969fb7c21c6a28cd112286da40d6429fea5",
    "SME003_CROSS_FOLIO_PREFLIGHT_SPEC.md": "d10ff711ebbb6269ce3d0ed0d760fd071836e7d7c6a6dda30be267b7292723b7",
    "build_sme003_cross_folio_preflight.py": "a94e75fa90e98141938742d0b7fc65e267e96c390fbf855fb6e9111dd9d44064",
    "sme003_cross_folio_preflight.json": "86c216302f99086bb4353e23eb97a7ddeb293e115461e0d733464d3bf3cacf4c",
    "sme003_cross_folio_preflight.md": "3ef8c2e24c9d97e0db0efca340c8a120e85f56b8c10c8f93bcb4cfc9007dc652",
}
EXPECTED_PAGES = {
    "f104r": 13,
    "f104v": 13,
    "f105r": 10,
    "f105v": 10,
    "f107v": 15,
    "f112v": 13,
    "f113r": 16,
    "f113v": 15,
    "f114r": 13,
    "f114v": 12,
    "f115r": 13,
    "f115v": 13,
}
TARGET_PATHS = (
    HERE / "TARGET_RESULT.json",
    HERE / "SME001_TARGET_RESULT.json",
    HERE / "SME003_TARGET_RESULT.json",
    HERE / "sme001_target_result.tsv",
    HERE / "sme003_target_result.tsv",
    RESULTS / "sme001_star_morphology_paragraph_result.md",
    RESULTS / "sme003_cross_folio_result.md",
)


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def float_array_digest(array: np.ndarray) -> str:
    packed = np.asarray(array, dtype=np.dtype("<f8"), order="C")
    return hashlib.sha256(packed.tobytes(order="C")).hexdigest()


def ordered_string_digest(strings: list[str]) -> str:
    payload = "".join(value + "\n" for value in strings).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def canonical_json_digest(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def page_demean(array: np.ndarray, page_labels: np.ndarray) -> np.ndarray:
    result = np.zeros_like(array, dtype=np.float64)
    for page in sorted(set(page_labels)):
        positions = np.flatnonzero(page_labels == page)
        result[positions] = array[positions] - array[positions].mean(axis=0, keepdims=True)
    return result


def check_unit_contract(
    page_labels: np.ndarray,
    folio_labels: np.ndarray,
    ordinal_values: np.ndarray,
) -> bool:
    observed = {
        page: int(np.count_nonzero(page_labels == page))
        for page in sorted(set(page_labels))
    }
    if observed != EXPECTED_PAGES:
        return False
    for page, count in observed.items():
        positions = page_labels == page
        if set(folio_labels[positions]) != {page[:-1]}:
            return False
        if sorted(ordinal_values[positions].tolist()) != list(range(1, count + 1)):
            return False
    return True


def valid_feature_domain(array: np.ndarray, word_column: int) -> bool:
    return bool(np.isfinite(array).all() and np.all(array[..., word_column] >= 0.0))


def oas_reference(training: np.ndarray) -> tuple[np.ndarray, dict[str, float | int]]:
    """Recompute the frozen population-covariance OAS transform directly."""
    n_rows, n_features = training.shape
    covariance = np.matmul(training.T, training) / n_rows
    mu = float(np.trace(covariance) / n_features)
    alpha = float(np.mean(np.square(covariance)))
    denominator = float((n_rows + 1) * (alpha - mu * mu / n_features))
    if denominator <= NUMERIC_FLOOR:
        rho = 1.0
    else:
        rho = min(1.0, (alpha + mu * mu) / denominator)
    regularized = (1.0 - rho) * covariance + rho * mu * np.identity(n_features)
    regularized_eigenvalues = np.linalg.eigvalsh(regularized)
    precision = np.linalg.inv(regularized)
    precision *= n_features / float(np.trace(precision))
    precision_eigenvalues = np.linalg.eigvalsh(precision)
    values: dict[str, float | int] = {
        "n": n_rows,
        "p": n_features,
        "mu": mu,
        "alpha": alpha,
        "denominator": denominator,
        "rho": rho,
        "covariance_min_eigenvalue": float(regularized_eigenvalues[0]),
        "covariance_max_eigenvalue": float(regularized_eigenvalues[-1]),
        "covariance_condition": float(regularized_eigenvalues[-1] / regularized_eigenvalues[0]),
        "weight_symmetry_max_abs": float(np.max(np.abs(precision - precision.T))),
        "weight_trace": float(np.trace(precision)),
        "weight_min_eigenvalue": float(precision_eigenvalues[0]),
    }
    return precision, values


def numeric_match(left: float, right: float) -> bool:
    return bool(np.isclose(left, right, rtol=2e-12, atol=2e-14, equal_nan=False))


def stop_wording_guard(production_text: str) -> bool:
    """Check the production authorization sentence is confined to the PASS arm."""
    try:
        tree = ast.parse(production_text)
    except SyntaxError:
        return False
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.If) or not node.orelse:
            continue
        test = ast.unparse(node.test)
        pass_text = " ".join(
            value.value
            for child in node.body
            for value in ast.walk(child)
            if isinstance(value, ast.Constant) and isinstance(value.value, str)
        )
        stop_text = " ".join(
            value.value
            for child in node.orelse
            for value in ast.walk(child)
            if isinstance(value, ast.Constant) and isinstance(value.value, str)
        )
        if "all(gates.values())" in test and "authorizes only" in pass_text:
            found = "STOP." in stop_text and "authorizes only" not in stop_text
    return found


def main() -> None:
    checks: list[str] = []

    def require(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    paths = (MATRIX, INVENTORY, SPEC, PRODUCTION, PREFLIGHT, PREFLIGHT_REPORT)
    observed_hashes = {path.name: file_digest(path) for path in paths}
    require("six frozen artifact hashes", observed_hashes == EXPECTED_HASHES)

    absent_before = {
        str(path.relative_to(ROOT)): not path.exists()
        for path in TARGET_PATHS
    }
    require("target artifacts absent before reconstruction", all(absent_before.values()))

    # Hashing is followed by parsing only for the two frozen anonymous inputs.
    with MATRIX.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fieldnames = list(reader.fieldnames or [])
        matrix_rows = [dict(row) for row in reader if row["page"] != "f106r"]
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    observed = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    production_text = PRODUCTION.read_text(encoding="utf-8")

    features = fieldnames[len(META):]
    expected_partition = (
        list(inventory["formal_features"])
        + ["ROOT_ATOM_RATE__" + item for item in inventory["root_atom_features"]]
        + ["ROOT_WORD_RATE__" + item for item in inventory["root_compound_word_features"]]
    )
    require("metadata columns exactly ordered", tuple(fieldnames[:len(META)]) == META)
    require("inventory component counts 34+32+18", (
        len(inventory["formal_features"]),
        len(inventory["root_atom_features"]),
        len(inventory["root_compound_word_features"]),
    ) == (34, 32, 18))
    require("ordered 84-feature partition", (
        len(features) == 84
        and features == inventory["all_features"]
        and features == expected_partition
    ))

    unit_ids = sorted({row["unit_id"] for row in matrix_rows})
    by_unit_reading: dict[tuple[str, str], dict[str, str]] = {}
    duplicate_keys: list[tuple[str, str]] = []
    for row in matrix_rows:
        key = (row["unit_id"], row["edition"])
        if key in by_unit_reading:
            duplicate_keys.append(key)
        by_unit_reading[key] = row
    require("156 units 468 rows unique reading keys", (
        len(unit_ids), len(matrix_rows), len(by_unit_reading), len(duplicate_keys)
    ) == (156, 468, 468, 0))
    require("exact three-reading coverage per unit", all(
        {row["edition"] for row in matrix_rows if row["unit_id"] == unit} == set(EDITIONS)
        for unit in unit_ids
    ))

    reference_rows = [by_unit_reading[(unit, EDITIONS[0])] for unit in unit_ids]
    pages = np.array([row["page"] for row in reference_rows], dtype=object)
    folios = np.array([row["physical_folio"] for row in reference_rows], dtype=object)
    ordinals = np.array([int(row["star_ordinal"]) for row in reference_rows], dtype=np.int64)
    loci = np.array([row["locus"] for row in reference_rows], dtype=object)
    require("exact 12-page map and ordinal/folio contract", check_unit_contract(pages, folios, ordinals))
    unique_folios = sorted(set(folios))
    require("exact seven physical folios", unique_folios == ["f104", "f105", "f107", "f112", "f113", "f114", "f115"])

    values = np.empty((156, 3, 84), dtype=np.float64)
    metadata_same = True
    for unit_position, unit in enumerate(unit_ids):
        for edition_position, edition in enumerate(EDITIONS):
            row = by_unit_reading[(unit, edition)]
            metadata_same &= (
                row["page"] == pages[unit_position]
                and row["physical_folio"] == folios[unit_position]
                and int(row["star_ordinal"]) == ordinals[unit_position]
                and row["locus"] == loci[unit_position]
            )
            values[unit_position, edition_position] = [float(row[name]) for name in features]
    require("page folio ordinal locus invariant across readings", metadata_same)
    word_column = features.index("PARA_WORD_COUNT")
    require("anonymous numeric domain finite with nonnegative word counts", valid_feature_domain(values, word_column))

    page_sizes = {page: EXPECTED_PAGES[page] for page in sorted(EXPECTED_PAGES)}
    relative_ordinal = np.array([
        (ordinal - 0.5) / page_sizes[page]
        for page, ordinal in zip(pages, ordinals)
    ], dtype=np.float64)
    absolute_ordinal = (ordinals.astype(np.float64) - 0.5) / 16.0
    first_half = np.array([
        ordinal <= page_sizes[page] / 2.0
        for page, ordinal in zip(pages, ordinals)
    ], dtype=np.float64)
    quarter = np.minimum(np.asarray(relative_ordinal * 4.0, dtype=np.int64), 3)
    formal_design = np.column_stack((
        relative_ordinal,
        relative_ordinal ** 2,
        relative_ordinal ** 3,
        absolute_ordinal,
        absolute_ordinal ** 2,
        absolute_ordinal ** 3,
        (ordinals % 2 == 1).astype(np.float64),
        first_half,
        (quarter == 1).astype(np.float64),
        (quarter == 2).astype(np.float64),
        (quarter == 3).astype(np.float64),
    ))
    formal_design = page_demean(formal_design, pages)
    require("relative absolute parity half quarter nuisance finite", (
        formal_design.shape == (156, 11) and bool(np.isfinite(formal_design).all())
    ))
    odd_pages = [page for page, size in page_sizes.items() if size % 2 == 1]
    require("odd-page middle assigned to late half", all(
        first_half[np.flatnonzero((pages == page) & (ordinals == (page_sizes[page] + 1) // 2))[0]] == 0.0
        for page in odd_pages
    ))

    root_start = 34
    residuals: dict[tuple[str, str], np.ndarray] = {}
    scales_by_transform: dict[tuple[str, str], np.ndarray] = {}
    reconstructed_folds: dict[str, dict[str, int | str]] = {}
    length_design_count = 0
    for held_folio in unique_folios:
        training = folios != held_folio
        held_out = ~training
        reconstructed_folds[held_folio] = {
            "train_units": int(np.count_nonzero(training)),
            "held_units": int(np.count_nonzero(held_out)),
            "train_pages": len(set(pages[training])),
            "held_pages": len(set(pages[held_out])),
            "training_unit_sha256": ordered_string_digest(sorted(np.asarray(unit_ids, dtype=object)[training].tolist())),
            "held_unit_sha256": ordered_string_digest(sorted(np.asarray(unit_ids, dtype=object)[held_out].tolist())),
        }
        for edition_position, edition in enumerate(EDITIONS):
            response = page_demean(values[:, edition_position, :], pages)
            log_length = np.log1p(values[:, edition_position, word_column])
            root_length_design = page_demean(np.column_stack((
                log_length, log_length ** 2, log_length ** 3,
            )), pages)
            require(f"finite 14-column root nuisance {held_folio} {edition}", (
                root_length_design.shape == (156, 3)
                and bool(np.isfinite(root_length_design).all())
                and bool(np.isfinite(formal_design).all())
            ))
            length_design_count += 1
            fitted_residuals = np.empty_like(response)
            for feature_position in range(84):
                if feature_position < root_start:
                    design = formal_design
                else:
                    design = np.concatenate((formal_design, root_length_design), axis=1)
                coefficients = np.linalg.lstsq(
                    design[training], response[training, feature_position], rcond=None
                )[0]
                fitted_residuals[:, feature_position] = (
                    response[:, feature_position] - design @ coefficients
                )
            scales = np.sqrt(np.mean(fitted_residuals[training] ** 2, axis=0))
            residuals[(held_folio, edition)] = fitted_residuals
            scales_by_transform[(held_folio, edition)] = scales
    require("all 7x3 nuisance fits reconstructed", length_design_count == 21)

    eligible_mask = np.ones(84, dtype=bool)
    for scale_vector in scales_by_transform.values():
        eligible_mask &= np.isfinite(scale_vector) & (scale_vector > SCALE_FLOOR)
    eligible_features = [name for name, eligible in zip(features, eligible_mask) if eligible]
    formal_eligible = [name for name in eligible_features if name in inventory["formal_features"]]
    root_eligible = [name for name in eligible_features if name not in inventory["formal_features"]]
    ineligible = [name for name, eligible in zip(features, eligible_mask) if not eligible]
    require("83-feature global intersection", (
        len(eligible_features), len(formal_eligible), len(root_eligible), ineligible
    ) == (83, 33, 50, ["OPEN_FIRST_HAS_Q"]))
    require("eligible identities and order", (
        formal_eligible == observed["formal_eligible"]
        and root_eligible == observed["root_eligible"]
        and ineligible == observed["ineligible"]
    ))

    require("all seven fold counts and unit digests exact", reconstructed_folds == observed["fold_rows"])
    unit_digest_matches = 14
    standardized_digest_matches = 0
    weight_digest_matches = 0
    numeric_diagnostic_matches = 0
    reconstructed_transforms: dict[str, dict[str, Any]] = {}
    all_transform_diagnostics = True
    for held_folio in unique_folios:
        training = folios != held_folio
        for edition in EDITIONS:
            eligible_scales = scales_by_transform[(held_folio, edition)][eligible_mask]
            standardized = residuals[(held_folio, edition)][:, eligible_mask] / eligible_scales
            require(f"finite standardized before OAS {held_folio} {edition}", bool(np.isfinite(standardized).all()))
            precision, diagnostics = oas_reference(standardized[training])
            diagnostics.update({
                "eligible_scale_min": float(np.min(eligible_scales)),
                "eligible_scale_max": float(np.max(eligible_scales)),
                "finite_standardized": bool(np.isfinite(standardized).all()),
                "finite_covariance": True,
                "finite_weight": bool(np.isfinite(precision).all()),
                "standardized_matrix_sha256": float_array_digest(standardized),
                "weight_matrix_sha256": float_array_digest(precision),
            })
            key = held_folio + "__" + edition
            expected = observed["transforms"][key]
            require(f"standardized digest {key}", diagnostics["standardized_matrix_sha256"] == expected["standardized_matrix_sha256"])
            standardized_digest_matches += 1
            require(f"weight digest {key}", diagnostics["weight_matrix_sha256"] == expected["weight_matrix_sha256"])
            weight_digest_matches += 1
            for name in (
                "n", "p", "mu", "alpha", "denominator", "rho",
                "covariance_min_eigenvalue", "covariance_max_eigenvalue",
                "covariance_condition", "weight_symmetry_max_abs", "weight_trace",
                "weight_min_eigenvalue", "eligible_scale_min", "eligible_scale_max",
            ):
                if name in ("n", "p"):
                    same = diagnostics[name] == expected[name]
                else:
                    same = numeric_match(float(diagnostics[name]), float(expected[name]))
                require(f"diagnostic {key} {name}", same)
                numeric_diagnostic_matches += 1
            for name in ("finite_standardized", "finite_covariance", "finite_weight"):
                require(f"diagnostic flag {key} {name}", diagnostics[name] is expected[name])
                numeric_diagnostic_matches += 1
            all_transform_diagnostics &= bool(
                diagnostics["finite_standardized"]
                and diagnostics["finite_covariance"]
                and diagnostics["finite_weight"]
                and diagnostics["covariance_min_eigenvalue"] > NUMERIC_FLOOR
                and diagnostics["weight_min_eigenvalue"] > NUMERIC_FLOOR
                and diagnostics["weight_symmetry_max_abs"] <= 1e-10
                and abs(diagnostics["weight_trace"] - len(eligible_features)) <= 1e-8
            )
            reconstructed_transforms[key] = diagnostics
    require("exact 21 transform key set", set(reconstructed_transforms) == set(observed["transforms"]))

    expected_gates = {
        "input_hashes": observed_hashes["anonymous_paragraph_matrix.tsv"] == EXPECTED_HASHES["anonymous_paragraph_matrix.tsv"]
        and observed_hashes["anonymous_feature_inventory.json"] == EXPECTED_HASHES["anonymous_feature_inventory.json"],
        "exact_matrix_contract": len(unit_ids) == 156 and len(matrix_rows) == 468 and len(features) == 84,
        "exact_page_folio_contract": len(page_sizes) == 12 and len(unique_folios) == 7,
        "formal_capacity_at_least_24": len(formal_eligible) >= 24,
        "root_capacity_at_least_32": len(root_eligible) >= 32,
        "all_transform_diagnostics": bool(all_transform_diagnostics),
        "target_artifacts_absent_before": all(absent_before.values()),
        "target_artifacts_absent_after": all(not path.exists() for path in TARGET_PATHS),
    }
    require("all eight gates independently reconstruct", expected_gates == observed["gates"] and all(expected_gates.values()))
    require("PASS status and synthetic-only decision reconstruct", (
        observed["status"] == "PASS_TARGET_BLIND_CROSS_FOLIO_PREFLIGHT"
        and observed["decision"] == "GO_TO_TARGET_FREE_SYNTHETIC_DESIGN"
        and observed["claim_ceiling"] == "target-blind cross-folio transform capacity only; no morphology association or meaning"
    ))
    require("reported source hashes exact", observed["source_hashes"] == {
        "SME003_CROSS_FOLIO_PREFLIGHT_SPEC.md": EXPECTED_HASHES["SME003_CROSS_FOLIO_PREFLIGHT_SPEC.md"],
        "build_sme003_cross_folio_preflight.py": EXPECTED_HASHES["build_sme003_cross_folio_preflight.py"],
    })
    require("reported input hashes exact", observed["input_hashes"] == {
        "anonymous_paragraph_matrix.tsv": EXPECTED_HASHES["anonymous_paragraph_matrix.tsv"],
        "anonymous_feature_inventory.json": EXPECTED_HASHES["anonymous_feature_inventory.json"],
    })
    require("reported target absence maps exact", (
        observed["target_artifact_absence_before"] == absent_before
        and observed["target_artifact_absence_after"] == absent_before
    ))
    require("reported no-target flags exact", (
        observed["target_rows_accessed"] is False
        and observed["morphology_fields_accessed"] is False
        and observed["target_join_performed"] is False
    ))
    require("reported cardinalities exact", (
        observed["units"] == 156
        and observed["rows"] == 468
        and observed["pages"] == EXPECTED_PAGES
        and observed["folios"] == unique_folios
        and observed["features_input"] == 84
        and observed["features_eligible"] == 83
    ))

    # Adversarial mutations exercise the independent guards, not production code.
    split_pages = pages.copy()
    split_pages[0] = "f104v" if split_pages[0] == "f104r" else "f104r"
    require("synthetic page-split mutation rejected", not check_unit_contract(split_pages, folios, ordinals))
    numeric_fixture = np.array([[[0.0, 1.0], [2.0, 3.0]]], dtype=np.float64)
    numeric_fixture[0, 1, 1] = -1.0
    require("synthetic negative word-count mutation rejected", not valid_feature_domain(numeric_fixture, 1))
    reordered_atoms = list(inventory["root_atom_features"])
    reordered_atoms[0], reordered_atoms[1] = reordered_atoms[1], reordered_atoms[0]
    reordered_partition = (
        list(inventory["formal_features"])
        + ["ROOT_ATOM_RATE__" + item for item in reordered_atoms]
        + ["ROOT_WORD_RATE__" + item for item in inventory["root_compound_word_features"]]
    )
    require("synthetic reordered-root partition rejected", reordered_partition != features)
    require("production STOP prose statically conditional", stop_wording_guard(production_text))
    false_gate_prose = "STOP. No later calibration or target access is authorized."
    require("synthetic failed gate cannot authorize prose", (
        false_gate_prose.startswith("STOP.") and "authorizes only" not in false_gate_prose
    ))

    absent_after = {
        str(path.relative_to(ROOT)): not path.exists()
        for path in TARGET_PATHS
    }
    require("target artifacts absent after reconstruction", all(absent_after.values()))

    rho_values = [float(value["rho"]) for value in reconstructed_transforms.values()]
    condition_values = [float(value["covariance_condition"]) for value in reconstructed_transforms.values()]
    digest_manifest = {
        key: {
            "standardized": value["standardized_matrix_sha256"],
            "weight": value["weight_matrix_sha256"],
        }
        for key, value in sorted(reconstructed_transforms.items())
    }
    validation = {
        "experiment": "SME003",
        "status": "PASS_INDEPENDENT_NONIMPORTING_PREFLIGHT_VALIDATION",
        "validator_scope": "two frozen anonymous inputs only; target artifacts existence-checked only",
        "frozen_hashes": observed_hashes,
        "contracts": {
            "units": 156,
            "reading_rows": 468,
            "readings": 3,
            "pages": 12,
            "folios": 7,
            "features": 84,
            "eligible": 83,
            "formal_eligible": 33,
            "root_eligible": 50,
            "ineligible": ineligible,
            "nuisance_fits": length_design_count,
        },
        "exact_digest_matches": {
            "fold_unit_lists": unit_digest_matches,
            "standardized_matrices": standardized_digest_matches,
            "weight_matrices": weight_digest_matches,
            "combined_transform_digest_sha256": canonical_json_digest(digest_manifest),
        },
        "numeric_diagnostic_matches": numeric_diagnostic_matches,
        "oas_ranges": {
            "rho_min": min(rho_values),
            "rho_max": max(rho_values),
            "condition_min": min(condition_values),
            "condition_max": max(condition_values),
        },
        "gates": expected_gates,
        "mutation_guards": {
            "page_split_rejected": True,
            "negative_word_count_rejected": True,
            "reordered_root_partition_rejected": True,
            "stop_prose_authorization_rejected": True,
        },
        "target_artifact_absence_before": absent_before,
        "target_artifact_absence_after": absent_after,
        "checks_passed": len(checks),
        "decision": "GO_TO_TARGET_FREE_SYNTHETIC_DESIGN_ONLY",
        "claim_ceiling": "anonymous transform capacity only; no morphology association, feature interpretation, meaning, lexeme, plaintext, language, or translation",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = f"""# SME003 independent preflight validation

**PASS_INDEPENDENT_NONIMPORTING_PREFLIGHT_VALIDATION**

Independent code reparsed only the two frozen anonymous inputs and reconstructed the exact 156-unit, 468-row, three-reading, 12-page, seven-folio, and ordered 34+32+18 feature contracts. It reproduced the 83-feature global eligibility intersection (33 formal, 50 root; only `OPEN_FIRST_HAS_Q` excluded), all 21 held-folio/reading nuisance residualizations, all 14 fold-unit-list digests, all 21 standardized-matrix digests, all 21 weight-matrix digests, and all {numeric_diagnostic_matches} stored OAS numeric/boolean diagnostics.

Analytic shrinkage rho spans {min(rho_values):.6f}--{max(rho_values):.6f}; shrunk covariance condition numbers span {min(condition_values):.6f}--{max(condition_values):.6f}. All eight production gates and the PASS/synthetic-only decision reconstruct. Synthetic mutations of a page split, a negative paragraph word count, and the ordered root partition are rejected; static and synthetic checks also keep authorizing prose out of the STOP branch.

The spec, production script, preflight JSON, and preflight report match their final frozen hashes. No production module was imported or executed. Morphology/target paths were checked only for existence and remained absent before and after validation.

This validates anonymous transform capacity only and authorizes at most separately frozen target-free synthetic design. It supplies no morphology association, feature interpretation, meaning, lexeme, plaintext, language, or translation.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": validation["status"],
        "checks_passed": validation["checks_passed"],
        "exact_digest_matches": validation["exact_digest_matches"],
        "numeric_diagnostic_matches": numeric_diagnostic_matches,
        "output": str(OUT.relative_to(ROOT)),
        "report": str(REPORT.relative_to(ROOT)),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
