#!/usr/bin/env python3
"""Gzip and world-hypothesis interface corrections for GDT395 scoring."""

from __future__ import annotations

import csv
import gzip
import math
from pathlib import Path

import score_identifiability as v1


def open_tsv_v3(path: Path) -> tuple[object, csv.DictReader]:
    try:
        if path.suffix == ".gz":
            handle = gzip.open(path, "rt", encoding="utf-8", newline="")
        else:
            handle = path.open("r", encoding="utf-8", newline="")
    except OSError:
        raise v1.Refusal(f"cannot open TSV {v1.portable_path(path)}") from None
    reader = csv.DictReader(handle, delimiter="\t")
    if reader.fieldnames is None:
        handle.close()
        raise v1.Refusal(f"TSV has no header: {v1.portable_path(path)}")
    return handle, reader


def parse_world_boolean_v3(value: object) -> bool | None:
    token = v1.clean(value).upper()
    if token in {"TRUE", "HIGH"}:
        return True
    if token in {"FALSE", "LOW"}:
        return False
    if token in {"UNRESOLVED", "MEDIUM"}:
        return None
    try:
        number = float(token)
    except ValueError:
        raise v1.Refusal("noncanonical world-hypothesis value") from None
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        raise v1.Refusal("world-hypothesis probability outside [0,1]")
    return number >= 0.5


def architecture_scores_v3(rows: list[dict[str, str]],
                           decoders: tuple[str, ...]) -> list[dict[str, object]]:
    indexed = {(row["world_id"], row["decoder_id"]): row for row in rows}
    endpoints = (
        ("ARCHITECTURE_CLUSTER", "UNSCORED_NO_FROZEN_FAMILY_MAP"),
        ("LANGUAGE_LIKE", "UNSCORED_PROXY_NO_FROZEN_MAPPING"),
        ("NOTATION_LIKE", "UNSCORED_PROXY_NO_FROZEN_MAPPING"),
        ("CODEBOOK_LIKE", "UNSCORED_PROXY_NO_FROZEN_MAPPING"),
    )
    output: list[dict[str, object]] = []
    for decoder in decoders:
        for endpoint, basis in endpoints:
            output.append({
                "decoder_id": decoder, "endpoint": endpoint,
                "truth_basis": basis, "n": 0,
                "nmi": None, "ari": None, "pair_f1": None,
                "balanced_accuracy": None, "mcc": None, "fdr": None,
            })
        tp = fp = tn = fn = 0
        for world in v1.WORLDS:
            prediction = parse_world_boolean_v3(
                indexed[(world, decoder)]["semantics_light_like"]
            )
            truth = world == "W10"
            if prediction is None:
                if truth:
                    fn += 1
                else:
                    fp += 1
            elif prediction and truth:
                tp += 1
            elif prediction:
                fp += 1
            elif truth:
                fn += 1
            else:
                tn += 1
        scores = v1.binary_scores(tp, tn, fp, fn)
        output.append({
            "decoder_id": decoder, "endpoint": "SEMANTICS_LIGHT_LIKE",
            "truth_basis": "W10_ONLY_DIRECT_FROZEN_TRUTH_ADVERSARIAL_ABSTENTION_COMPLETION",
            "n": scores["n"], "nmi": None, "ari": None, "pair_f1": None,
            "balanced_accuracy": scores["balanced_accuracy"],
            "mcc": scores["mcc"], "fdr": scores["fdr"],
        })
    return output


def main() -> int:
    v1.open_tsv = open_tsv_v3
    v1.parse_bool = parse_world_boolean_v3
    v1.architecture_scores = architecture_scores_v3
    return v1.main()


if __name__ == "__main__":
    raise SystemExit(main())

