#!/usr/bin/env python3
"""One-time real NONE/DA context target."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from collections import Counter
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import numpy as np

import source_native_opening_context_core as core

try:
    import cupy as cp
except ImportError:
    cp = None


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
SOURCE_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
PANEL = RESULTS / "source_native_opening_context_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
PREFLIGHT = RESULTS / "source_native_opening_context_preflight.json"
PREFLIGHT_VALIDATION = RESULTS / "source_native_opening_context_preflight_validation.json"
CORE = BASE / "source_native_opening_context_core.py"
SPEC = BASE / "SOURCE_NATIVE_OPENING_CONTEXT_TARGET_SPEC.md"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_context_target.json"
REPORT = RESULTS / "source_native_opening_context_target_report.md"
FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    PANEL: "6a043ba095d118594c9a8bd4bd4bf0ac96778963be0637400e353c517c5e616a",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    PREFLIGHT: "c78534f1bf10c6e901c7dea896119eaa9e82b3a4c8229f61ea2903f7cb6c3f68",
    PREFLIGHT_VALIDATION: "5c657778058cadf497cc12d7478499629aeec2de200d1db02815e60dc09f4b51",
    CORE: "fe6d473758c744ee50f800fba3246d773a26daf7226447db685639561090a5cd",
    SPEC: "2f706243b576e1ad7bb7e737eeaac06f7324fb5d5ceaa35e11f33368ce6e6ab1",
}
PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def operation(surface: str) -> tuple[str, str]:
    for prefix in PREFIXES:
        if surface.startswith(prefix):
            return prefix, surface[len(prefix):]
    return "NONE", surface


def decision(position_pass: bool, neighbor_pass: bool) -> tuple[str, str]:
    if position_pass and neighbor_pass:
        return "CONFIRM_DA_POSITION_AND_EXTERNAL_CONTEXT", "RETAIN_POSITION_AND_EXTERNAL_CONTEXT_OPERATION"
    if position_pass:
        return "CONFIRM_DA_LOCUS_POSITION_CONTEXT", "RETAIN_LOCUS_POSITION_OPERATION_ONLY"
    if neighbor_pass:
        return "CONFIRM_DA_EXTERNAL_NEIGHBOR_CONTEXT", "RETAIN_EXTERNAL_NEIGHBOR_CONTEXT_OPERATION_ONLY"
    return "NONCONFIRM_DA_STRUCTURAL_CONTEXT", "RETAIN_OPENING_CHAIN_CAPACITY_ONLY"


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(PREFLIGHT_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_104_WORLD_CONTEXT_CALIBRATION_RECONSTRUCTION":
        raise SystemExit("preflight validation")
    with PANEL.open(encoding="utf-8", newline="") as handle:
        masked_rows = list(csv.DictReader(handle, delimiter="\t"))
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(source_rows) != 26184 or len(masked_rows) != 5826:
        raise SystemExit("source counts")
    hidden = {}
    for row in source_rows:
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        state, base = operation(row["family_surface"])
        if base and state in {"NONE", "DA"}:
            unit_id = opaque("U", row["consensus_group_id"])
            if unit_id in hidden:
                raise SystemExit("hidden identity")
            hidden[unit_id] = (state, opaque("B", base))
    masked_ids = {row["unit_id"] for row in masked_rows}
    if len(masked_ids) != 5826 or any(unit_id not in hidden for unit_id in masked_ids):
        raise SystemExit("masked join")
    for row in masked_rows:
        if hidden[row["unit_id"]][1] != row["base_id"]:
            raise SystemExit("base binding")
    panel = core.load_panel(PANEL, QUOTAS)
    actual = np.asarray([1.0 if hidden[row["unit_id"]][0] == "DA" else 0.0 for row in panel.rows])
    if len(actual) != 1207 or int(actual.sum()) != 315:
        raise SystemExit("target labels")
    for indices, expected in zip(panel.stratum_indices, panel.da_counts):
        if int(actual[indices].sum()) != int(expected):
            raise SystemExit("quota assignment")
    null = core.null_orbit(panel, 8192, "PREFLIGHT")
    backend = cp if cp is not None else np
    position = core.summarize_batch(panel, panel.position, actual[None, :], null, xp=backend)[0]
    neighbor = core.summarize_batch(panel, panel.neighbor, actual[None, :], null, xp=backend)[0]
    position_pass = core.passes(position, 0.01)
    neighbor_pass = core.passes(neighbor, 0.01)
    status, final_decision = decision(position_pass, neighbor_pass)
    gates = {
        "exact_26184_source_rows": len(source_rows) == 26184,
        "exact_5826_masked_join": len(masked_ids) == 5826,
        "exact_1207_scored_rows": len(actual) == 1207,
        "exact_197_quota_strata": len(panel.strata) == 197,
        "exact_59_informative_folios": len(panel.folios) == 59,
        "exact_892_NONE_315_DA_labels": Counter(actual) == Counter({0.0: 892, 1.0: 315}),
        "every_quota_exact": all(int(actual[indices].sum()) == int(expected) for indices, expected in zip(panel.stratum_indices, panel.da_counts)),
        "POSITION_PASS": position_pass,
        "NEIGHBOR_PASS": neighbor_pass,
    }
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_CONTEXT_TARGET",
        "status": status,
        "decision": final_decision,
        "inputs": {path.name: sha(path) for path in (*FROZEN, RUNNER)},
        "backend": "cupy" if cp is not None else "numpy",
        "backend_version": cp.__version__ if cp is not None else np.__version__,
        "source_rows_accessed": len(source_rows),
        "masked_rows_joined": len(masked_ids),
        "target_rows_scored": len(actual),
        "target_label_totals": {"DA": int(actual.sum()), "NONE": int(len(actual) - actual.sum())},
        "POSITION": {**position, "PASS": position_pass},
        "NEIGHBOR": {**neighbor, "PASS": neighbor_pass},
        "gates": gates,
        "row_operation_labels_stored": 0,
        "remainder_identities_stored": 0,
        "event_loci_stored": 0,
        "english_glosses": 0,
        "claim_ceiling": "Aggregate NONE-versus-DA structural context only; even a pass establishes no physical detachment, wordhood, prefix name, POS, syntax label, sound, language, cipher operation, English meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# `NONE` versus `DA` structural-context target

Status: **{status}**

The one-time join scores **1,207** rows in **197** exact remainder-folio quota
strata on **59** informative folios. `POSITION` has statistic
**{position['observed']:.6f}**, p=**{position['upper_p']:.6f}**, z=**{position['z']:.3f}**,
and passes=**{str(position_pass).lower()}**. Position-residualized `NEIGHBOR` has
statistic **{neighbor['observed']:.6f}**, p=**{neighbor['upper_p']:.6f}**,
z=**{neighbor['z']:.3f}**, and passes=**{str(neighbor_pass).lower()}**.

Decision: **{final_decision}**. No row label, remainder identity, locus, page,
or event context is stored. Even a pass establishes no physical detachment,
wordhood, prefix name, POS, syntax label, sound, language, cipher, English
meaning, plaintext, or translation.
""")
    print(json.dumps({"status": status, "decision": final_decision, "position": result["POSITION"], "neighbor": result["NEIGHBOR"]}, sort_keys=True))


if __name__ == "__main__":
    main()
