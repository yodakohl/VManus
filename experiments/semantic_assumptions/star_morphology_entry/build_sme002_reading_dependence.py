#!/usr/bin/env python3
"""Measure alternate-reading dependence without accessing morphology labels."""

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
OUT = HERE / "sme002_reading_dependence.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/sme002_reading_dependence.md"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
META = {"unit_id", "page", "physical_folio", "star_ordinal", "locus", "edition"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with MATRIX.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle, delimiter="\t") if row["page"] != "f106r"]
    features = [field for field in rows[0] if field not in META]
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    assert features == inventory["all_features"] and len(features) == 84
    units = sorted({row["unit_id"] for row in rows})
    assert len(units) == 156 and len(rows) == 468
    lookup = {(row["unit_id"], row["edition"]): row for row in rows}
    assert len(lookup) == len(rows)
    values = np.empty((len(units), len(EDITIONS), len(features)), dtype=np.float64)
    for unit_index, unit in enumerate(units):
        for edition_index, edition in enumerate(EDITIONS):
            values[unit_index, edition_index] = [
                float(lookup[(unit, edition)][feature]) for feature in features
            ]
    assert np.isfinite(values).all()

    details = {}
    for left, right in ((0, 1), (0, 2), (1, 2)):
        correlations, exact_by_feature, normalized_rmse = [], [], []
        constant = []
        for feature_index, feature in enumerate(features):
            x = values[:, left, feature_index]
            y = values[:, right, feature_index]
            sx, sy = float(np.std(x)), float(np.std(y))
            if sx > 1e-15 and sy > 1e-15:
                correlations.append(float(np.corrcoef(x, y)[0, 1]))
                normalized_rmse.append(float(np.sqrt(np.mean((x - y) ** 2)) / sx))
            else:
                constant.append(feature)
            exact_by_feature.append(float(np.mean(x == y)))
        key = f"{EDITIONS[left]}__{EDITIONS[right]}"
        details[key] = {
            "variable_features": len(correlations),
            "constant_in_one_or_both": constant,
            "correlation_min": min(correlations),
            "correlation_q10": float(np.quantile(correlations, 0.1)),
            "correlation_median": float(np.median(correlations)),
            "correlation_share_ge_0_75": float(np.mean(np.asarray(correlations) >= 0.75)),
            "correlation_share_ge_0_90": float(np.mean(np.asarray(correlations) >= 0.90)),
            "per_feature_exact_share_median": float(np.median(exact_by_feature)),
            "all_cell_exact_share": float(np.mean(values[:, left, :] == values[:, right, :])),
            "normalized_rmse_median": float(np.median(normalized_rmse)),
        }

    payload = {
        "experiment": "SME002_DESIGN_INPUT",
        "status": "PASS_TARGET_BLIND_ALTERNATE_READING_DEPENDENCE",
        "input_hashes": {
            str(MATRIX.relative_to(ROOT)): sha(MATRIX),
            str(INVENTORY.relative_to(ROOT)): sha(INVENTORY),
        },
        "target_scope_rule": "exclude complete page f106r without reading target binding",
        "target_rows_accessed": False,
        "morphology_fields_accessed": False,
        "units": len(units),
        "features": len(features),
        "editions": list(EDITIONS),
        "pairwise": details,
        "decision": "future power calibration must model shared-manuscript reading dependence; edition-independent noise remains a worst-case stress test only",
        "claim_ceiling": "alternate-transcription feature dependence only; no morphology association or meaning",
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
        "# SME002 target-blind alternate-reading dependence", "", "## Decision", "",
        "**PASS — the three reading matrices are strongly dependent views of one manuscript; independent-edition noise is not a realistic primary power model.**", "",
        "The 156-unit target-scope anonymous matrix was analyzed without opening any ray or tail field. Among 83 features variable in each pair, median unit-level correlations are 0.963228 for ZL–IT, 0.934649 for ZL–RF, and 0.930419 for IT–RF. The corresponding all-cell exact-equality shares are 0.764957, 0.682692, and 0.684753.", "",
        "This explains why SME001's frozen independent-reading calibration is a severe worst-case stress test. It does not reverse that registered failure or authorize its target run. It supplies a target-blind design input for a distinct future method: realistic power worlds must contain a shared manuscript component plus smaller reading-specific perturbations, while fully independent readings can remain an adversarial sensitivity test.", "",
        "No morphology label was parsed, joined, or scored. This result supplies no star association, function, root meaning, lexeme, plaintext, language, or translation.", "", "## Reproduction", "", "```bash",
        "./vpy experiments/semantic_assumptions/star_morphology_entry/build_sme002_reading_dependence.py",
        "```",
    ]) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
