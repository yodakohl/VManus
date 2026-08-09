#!/usr/bin/env python3
"""Execute the one-shot exact-member onset compatibility target."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

import source_native_opening_onset_core as core


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
SOURCE_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
PANEL = RESULTS / "source_native_opening_onset_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_opening_onset_capacity_validation.json"
MEMBER_AUDIT = RESULTS / "source_native_opening_member_remainders.json"
MEMBER_VALIDATION = RESULTS / "source_native_opening_member_remainders_validation.json"
PREFLIGHT = RESULTS / "source_native_opening_onset_preflight.json"
PREFLIGHT_VALIDATION = RESULTS / "source_native_opening_onset_preflight_validation.json"
CORE = BASE / "source_native_opening_onset_core.py"
SPEC = BASE / "SOURCE_NATIVE_OPENING_ONSET_TARGET_SPEC.md"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_onset_target.json"
REPORT = RESULTS / "source_native_opening_onset_target_report.md"

FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    PANEL: "628d2f657db080b975f2e201d6d684f3dab7ede75b19be6cc4e4c4b3f580e4a2",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    CAPACITY_VALIDATION: "bdb86a58e5ee0ef9850554d7b65685c9cf0a35f1af06cefd30f676e17ec6abed",
    MEMBER_AUDIT: "3ba1a442cd36581d0562b4721a2ce2fffa3aeb01a8b4706edac1f6da211f675a",
    MEMBER_VALIDATION: "b8653ec6a42ed8bafb07e06894d2896f3d55fb68d9e9b03cb12acf5477db65f6",
    PREFLIGHT: "412cd477eb96a9679cc7d9273f3eeb3fbf547c790138fb95099cc10650c963a5",
    PREFLIGHT_VALIDATION: "e3dbc741a324a3824590cafb4a31e5efcc2c344c7c181c7b61eb8816bc459225",
    CORE: "33c1870c0e8f80516a02573a279f78b2eba4b12a2b2225bfe864525d18bc2adf",
    SPEC: "e4b2fb7d04098587aa815e343d9fb5ab5ba3526547426bca232b2b77d2e64e81",
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


def digest(array) -> str:
    return hashlib.sha256(np.ascontiguousarray(array, dtype="<f8").tobytes()).hexdigest()


def install_pair(result_bytes: bytes, report_bytes: bytes) -> None:
    if OUT.exists() or REPORT.exists():
        raise FileExistsError("target exists")
    with tempfile.TemporaryDirectory(prefix="opening_onset_target_", dir=RESULTS) as directory:
        staged_result = Path(directory) / "result.json"
        staged_report = Path(directory) / "report.md"
        staged_result.write_bytes(result_bytes)
        staged_report.write_bytes(report_bytes)
        if OUT.exists() or REPORT.exists():
            raise FileExistsError("target appeared")
        os.link(staged_result, OUT)
        try:
            os.link(staged_report, REPORT)
        except Exception:
            OUT.unlink(missing_ok=True)
            raise


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing second target")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(CAPACITY_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_1207_ROW_OPENING_ONSET_CAPACITY_RECONSTRUCTION":
        raise ValueError("capacity validation")
    if json.loads(MEMBER_AUDIT.read_text())["status"] != "PASS_MEMBER_RESOLVED_NONE_DA_CAPACITY" or json.loads(MEMBER_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_MEMBER_RESOLVED_NONE_DA_RECONSTRUCTION":
        raise ValueError("member safeguard")
    preflight = json.loads(PREFLIGHT.read_text())
    preflight_validation = json.loads(PREFLIGHT_VALIDATION.read_text())
    if preflight["status"] != "PASS_TARGET_FREE_OPENING_ONSET_PREFLIGHT" or not all(preflight["gates"].values()) or preflight_validation["status"] != "PASS_PRODUCTION_FREE_96_WORLD_ONSET_CALIBRATION_RECONSTRUCTION" or not preflight_validation["target_outputs_absent"]:
        raise ValueError("preflight authorization")
    panel = core.load_panel(PANEL, QUOTAS)
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(source_rows) != 26184 or len({row["consensus_group_id"] for row in source_rows}) != 26184:
        raise ValueError("source identity")
    hidden = {}
    for row in source_rows:
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        state, base = operation(row["family_surface"])
        if not base or state not in {"NONE", "DA"}:
            continue
        unit_id = opaque("U", row["consensus_group_id"])
        if unit_id in hidden:
            raise ValueError("hidden identity")
        hidden[unit_id] = (state, opaque("B", base))
    actual = np.empty(len(panel.rows), dtype=np.float64)
    for index, row in enumerate(panel.rows):
        if row["unit_id"] not in hidden or hidden[row["unit_id"]][1] != row["base_id"]:
            raise ValueError("target join")
        actual[index] = 1.0 if hidden[row["unit_id"]][0] == "DA" else 0.0
    if Counter(actual) != Counter({0.0: 892, 1.0: 315}):
        raise ValueError("label totals")
    for indices, expected in zip(panel.stratum_indices, panel.da_counts):
        if int(actual[indices].sum()) != int(expected):
            raise ValueError("label quota")
    null = core.quota_labels(panel, 8192, "PREFLIGHT_NULL")
    summary = core.summarize(panel, actual[None, :], null)[0]
    target_pass = core.passes(summary, 0.01)
    if target_pass:
        status = "CONFIRM_EXACT_ONSET_CONDITIONS_D1_A1_SELECTION"
        decision = "RETAIN_TRANSFERABLE_MEMBER_ONSET_COMPATIBILITY"
    else:
        status = "NONCONFIRM_EXACT_ONSET_CONDITIONS_D1_A1_SELECTION"
        decision = "RETAIN_DOMINANT_D1_A1_FORM_WITH_SELECTION_UNEXPLAINED"
    gates = {
        "exact_26184_source_rows": len(source_rows) == 26184,
        "exact_1207_target_join": len(actual) == 1207,
        "exact_892_NONE_315_DA": Counter(actual) == Counter({0.0: 892, 1.0: 315}),
        "every_quota_exact": all(int(actual[indices].sum()) == int(expected) for indices, expected in zip(panel.stratum_indices, panel.da_counts)),
        "exact_1141_eligible_rows_59_folios": int(panel.eligible.sum()) == 1141 and len(panel.folios) == 59,
        "ONSET_COMPATIBILITY_PASS": target_pass,
    }
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_ONSET_TARGET",
        "status": status,
        "decision": decision,
        "inputs": {path.name: sha(path) for path in (*FROZEN, RUNNER)},
        "source_rows_accessed": len(source_rows),
        "target_rows_joined": len(actual),
        "target_label_totals": {"DA": int(actual.sum()), "NONE": int(len(actual) - actual.sum())},
        "eligible_rows_scored": int(panel.eligible.sum()),
        "physical_folios": len(panel.folios),
        "target_label_sha256": digest(actual),
        "null_label_orbit_sha256": digest(null),
        "summary": {**summary, "PASS": target_pass},
        "gates": gates,
        "row_operation_labels_stored": 0,
        "event_loci_or_pages_stored": 0,
        "remainder_identities_stored": 0,
        "english_glosses": 0,
        "claim_ceiling": "Exact first-member compatibility with dominant D1-A1 selection only; no detachment, morphology, pronunciation, wordhood, POS, syntax, language, cipher operation, meaning, plaintext, or translation follows.",
    }
    report = f"""# Exact-member onset compatibility target

Status: **{status}**

The one-shot target joins **1,207** rows, scores **1,141** held-folio-reusable
rows on **59** folios, and preserves all **197** exact label quotas. The
base-plus-onset model gains **{summary['observed']:.6f}** nat/eligible row over
the base-only model (null mean **{summary['null_mean']:.6f}**, z=**{summary['z']:.3f}**,
p=**{summary['upper_p']:.6f}**). Folio support is
**{summary['positive_folios']}/59**; Currier A/B means are
**{summary['currier_A_mean']:.6f} / {summary['currier_B_mean']:.6f}**.

Decision: **{decision}**. No row label, locus, page, or remainder identity is
stored. This supplies no morphology, pronunciation, word meaning, plaintext,
or translation.
"""
    install_pair((json.dumps(result, indent=2, sort_keys=True) + "\n").encode(), report.encode())
    print(json.dumps({"status": status, "decision": decision, "summary": result["summary"], "gates": gates}, sort_keys=True))


if __name__ == "__main__":
    main()
