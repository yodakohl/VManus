#!/usr/bin/env python3
"""Execute the hash-frozen LRG001 manuscript target exactly once."""

from __future__ import annotations

import os

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[variable] = "1"

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from lrg001_core import assignment_coefficients, evaluate, feature_matrix, load_geometry, sha256_array


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
FREEZE = HERE / "LRG001_TARGET_FREEZE.json"
CAPACITY = RESULTS / "lrg001_label_register_capacity.tsv"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
OUT_JSON = RESULTS / "lrg001_label_register_target.json"
OUT_REPORT = RESULTS / "lrg001_label_register_target_report.md"
VALIDATION_JSON = RESULTS / "lrg001_label_register_target_validation.json"
VALIDATION_REPORT = RESULTS / "lrg001_label_register_target_validation_report.md"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def atomic_new(path: Path, text: str) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite {path.name}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    if path.exists():
        temporary.unlink()
        raise RuntimeError(f"concurrent output {path.name}")
    os.link(temporary, path)
    temporary.unlink()


def verify_freeze() -> dict[str, object]:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze["status"] != "FROZEN_LRG001_SINGLE_TARGET" or freeze["result_paths"] != [
        str(OUT_JSON.relative_to(ROOT)), str(OUT_REPORT.relative_to(ROOT)),
        str(VALIDATION_JSON.relative_to(ROOT)), str(VALIDATION_REPORT.relative_to(ROOT)),
    ]:
        raise RuntimeError("invalid LRG001 freeze")
    for relative, expected in freeze["frozen_files"].items():
        path = ROOT / relative
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError(f"freeze drift {relative}")
    if any(path.exists() for path in (OUT_JSON, OUT_REPORT, VALIDATION_JSON, VALIDATION_REPORT)):
        raise RuntimeError("target or validation output already exists")
    return freeze


def target_rows() -> tuple[list[str], np.ndarray]:
    capacity = [row for row in load_tsv(CAPACITY) if row["section"] in {"B", "P"}]
    eligible: dict[tuple[str, int], dict[str, list[dict[str, str]]]] = defaultdict(lambda: {"L": [], "P": []})
    for row in load_tsv(GROUPS):
        if row["strict_zero_alternative"] != "1":
            continue
        if row["kind"] == "L":
            kind = "L"
        elif row["kind"] == "P" and row["grammar_scope"] == "CONFIRMED_PROSE":
            kind = "P"
        else:
            continue
        eligible[row["page"], int(row["symbol_count"])][kind].append(row)
    sequences: list[str] = []
    labels: list[int] = []
    for cell in capacity:
        key = cell["page"], int(cell["symbol_count"])
        selected = eligible[key]
        for kind, target in (("L", 1), ("P", 0)):
            current = sorted(selected[kind], key=lambda row: row["consensus_group_id"])
            expected = int(cell["label_rows"] if kind == "L" else cell["prose_rows"])
            if len(current) != expected:
                raise RuntimeError(f"target cell count drift {key} {kind}")
            for row in current:
                sequence = row["family_surface"]
                if len(sequence) != int(row["symbol_count"]):
                    raise RuntimeError("target sequence length drift")
                sequences.append(sequence)
                labels.append(target)
    return sequences, np.asarray(labels, dtype=np.int8)


def main() -> None:
    freeze = verify_freeze()
    geometry = load_geometry(CAPACITY)
    sequences, labels = target_rows()
    if len(sequences) != len(geometry.row_ids) or int(labels.sum()) != 288:
        raise RuntimeError("target row geometry mismatch")
    matrix = feature_matrix(sequences, geometry.lengths)
    numbers = np.asarray([int(value[1:]) for value in geometry.folios])
    coefficient_even = assignment_coefficients(geometry, numbers % 2 == 0)
    coefficient_odd = assignment_coefficients(geometry, numbers % 2 == 1)
    evaluation = evaluate(matrix, labels, geometry, coefficient_even, coefficient_odd)
    passed = bool(evaluation["passes"])
    status = (
        "CONFIRMED_TRANSFERABLE_SOURCE_NATIVE_LABEL_PROFILE" if passed
        else "FINAL_NONCONFIRMATION_SOURCE_NATIVE_LABEL_PROFILE"
    )
    decision = "PROFILE_PROJECTION_AUTHORIZED_AFTER_VALIDATION" if passed else "CLOSE_EXACT_LRG001_REPRESENTATION"
    claim = (
        "A pass establishes only a transferable label-associated structural profile under exact page, length, physical-folio parity, and B/P section controls. "
        "Neither outcome supplies an identifier, name, noun, object ownership, part of speech, language, meaning, plaintext, or translation."
    )
    result = {
        "status": status,
        "decision": decision,
        "claim_ceiling": claim,
        "freeze_sha256": digest(FREEZE),
        "frozen_code_commit": freeze["code_commit"],
        "target_rows_accessed": True,
        "target_sequences_emitted": False,
        "individual_feature_weights_emitted": False,
        "counts": {
            "rows": len(sequences), "labels": int(labels.sum()),
            "prose": int(len(labels) - labels.sum()), "cells": len(set(geometry.cell_ids)),
            "physical_folios": len(set(geometry.folios)), "feature_columns": matrix.shape[1],
        },
        "target_matrix_sha256": sha256_array(matrix),
        "label_vector_sha256": sha256_array(labels),
        "assignment_digests": {
            "EVEN_HELD": sha256_array(coefficient_even[1]),
            "ODD_HELD": sha256_array(coefficient_odd[1]),
        },
        "evaluation": evaluation,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    report = "\n".join([
        "# LRG001 source-native label-register target", "",
        f"Status: **{status}**.", "",
        "The sealed target used 288 manual label groups and 2,479 exact-page/exact-length confirmed-prose controls in 101 cells on 13 physical folios.", "",
        "| direction | effect | p | positive folios | B effect | P effect | min deletion | concentration | pass |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        *[
            f"| {name} | {value['effect']:+.9f} | {value['p']:.9f} | {value['positive_folios']}/{value['folio_count']} | "
            f"{value['section_effects']['B']:+.9f} | {value['section_effects']['P']:+.9f} | "
            f"{value['minimum_deletion']:+.9f} | {value['maximum_absolute_folio_concentration']:.9f} | {value['passes']} |"
            for name, value in evaluation["directions"].items()
        ],
        "",
        f"Independent-profile cosine: **{evaluation['profile_cosine']:+.9f}**.", "",
        f"Decision: **{decision}**.", "",
        "No individual family weight, form, sequence, member code, EVA spelling, identifier, name, noun, object ownership, meaning, plaintext, or translation is emitted.", "",
    ])
    atomic_new(OUT_JSON, text)
    try:
        atomic_new(OUT_REPORT, report)
    except Exception:
        OUT_JSON.unlink(missing_ok=True)
        raise
    print(text, end="")


if __name__ == "__main__":
    main()
