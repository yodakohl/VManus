#!/usr/bin/env python3
"""Production-free reconstruction of the one-time NONE/DA context target."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "32"
os.environ["OMP_NUM_THREADS"] = "32"
os.environ["MKL_NUM_THREADS"] = "32"

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

import validate_source_native_opening_context_preflight as independent


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
SOURCE_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
PANEL = RESULTS / "source_native_opening_context_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
PREFLIGHT = RESULTS / "source_native_opening_context_preflight.json"
PREFLIGHT_VALIDATION = RESULTS / "source_native_opening_context_preflight_validation.json"
CLEAN_VALIDATOR = BASE / "validate_source_native_opening_context_preflight.py"
CORE = BASE / "source_native_opening_context_core.py"
SPEC = BASE / "SOURCE_NATIVE_OPENING_CONTEXT_TARGET_SPEC.md"
RUNNER = BASE / "run_source_native_opening_context_target.py"
TARGET = RESULTS / "source_native_opening_context_target.json"
TARGET_REPORT = RESULTS / "source_native_opening_context_target_report.md"
OUT = RESULTS / "source_native_opening_context_target_validation.json"
REPORT = RESULTS / "source_native_opening_context_target_validation_report.md"
FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    PANEL: "6a043ba095d118594c9a8bd4bd4bf0ac96778963be0637400e353c517c5e616a",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    PREFLIGHT: "c78534f1bf10c6e901c7dea896119eaa9e82b3a4c8229f61ea2903f7cb6c3f68",
    PREFLIGHT_VALIDATION: "5c657778058cadf497cc12d7478499629aeec2de200d1db02815e60dc09f4b51",
    CLEAN_VALIDATOR: "045da3bde6fa9cccd6cadb50e9ba0eafb69eb4a0b652d94e2425637257430c95",
    CORE: "fe6d473758c744ee50f800fba3246d773a26daf7226447db685639561090a5cd",
    SPEC: "2f706243b576e1ad7bb7e737eeaac06f7324fb5d5ceaa35e11f33368ce6e6ab1",
    RUNNER: "b78efb158a08f9f8a25d42a16105b61c03b03460555a998e3ffbe65fd44dd669",
    TARGET: "dd66d499a8b4253eb02d8d895aeaa2f13de9fd02617d428cbb5b20c91631c6a3",
    TARGET_REPORT: "5897f79637545a192a4293b6cc835361b8a64284211df3352cb2ac3c47d7630e",
}
PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def operation(surface: str) -> tuple[str, str]:
    matches = [prefix for prefix in PREFIXES if surface.startswith(prefix)]
    if not matches:
        return "NONE", surface
    prefix = max(matches, key=len)
    return prefix, surface[len(prefix):]


def expected_report(position, neighbor) -> str:
    return f"""# `NONE` versus `DA` structural-context target

Status: **NONCONFIRM_DA_STRUCTURAL_CONTEXT**

The one-time join scores **1,207** rows in **197** exact remainder-folio quota
strata on **59** informative folios. `POSITION` has statistic
**{position['observed']:.6f}**, p=**{position['upper_p']:.6f}**, z=**{position['z']:.3f}**,
and passes=**false**. Position-residualized `NEIGHBOR` has
statistic **{neighbor['observed']:.6f}**, p=**{neighbor['upper_p']:.6f}**,
z=**{neighbor['z']:.3f}**, and passes=**false**.

Decision: **RETAIN_OPENING_CHAIN_CAPACITY_ONLY**. No row label, remainder identity, locus, page,
or event context is stored. Even a pass establishes no physical detachment,
wordhood, prefix name, POS, syntax label, sound, language, cipher, English
meaning, plaintext, or translation.
"""


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures = []
    checks = 0

    def check(condition, name):
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, f"hash:{path.name}")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    with PANEL.open(encoding="utf-8", newline="") as handle:
        masked_rows = list(csv.DictReader(handle, delimiter="\t"))
    hidden = {}
    for row in source_rows:
        if row["strict_zero_alternative"] == "1" and row["grammar_scope"] == "CONFIRMED_PROSE":
            state, base = operation(row["family_surface"])
            if base and state in {"NONE", "DA"}:
                key = opaque("U", row["consensus_group_id"])
                if key in hidden:
                    raise ValueError("duplicate")
                hidden[key] = (state, opaque("B", base))
    check(len(source_rows) == 26184 and len(masked_rows) == 5826 and len({row["unit_id"] for row in masked_rows}) == 5826, "identity")
    check(all(row["unit_id"] in hidden and hidden[row["unit_id"]][1] == row["base_id"] for row in masked_rows), "join")
    data = independent.load()
    actual = np.asarray([1.0 if hidden[row["unit_id"]][0] == "DA" else 0.0 for row in data[0]])
    check(len(actual) == 1207 and Counter(actual) == Counter({0.0: 892, 1.0: 315}), "labels")
    check(all(int(actual[indices].sum()) == int(count) for indices, count in zip(data[2], data[3])), "quotas")
    null = independent.orbit(data[0], data[1], data[2], data[3], 8192, "PREFLIGHT")
    position = independent.summaries(data, data[10], actual[None], null)[0]
    neighbor = independent.summaries(data, data[11], actual[None], null)[0]
    position_pass = independent.passes(position)
    neighbor_pass = independent.passes(neighbor)
    stored = json.loads(TARGET.read_text())
    check(independent.numeric_max(stored["POSITION"], {**position, "PASS": position_pass}) <= 1e-12, "position")
    check(independent.numeric_max(stored["NEIGHBOR"], {**neighbor, "PASS": neighbor_pass}) <= 1e-12, "neighbor")
    check(not position_pass and not neighbor_pass, "nonconfirmation")
    expected_gates = {"exact_26184_source_rows": True, "exact_5826_masked_join": True, "exact_1207_scored_rows": True, "exact_197_quota_strata": True, "exact_59_informative_folios": True, "exact_892_NONE_315_DA_labels": True, "every_quota_exact": True, "POSITION_PASS": False, "NEIGHBOR_PASS": False}
    check(stored["gates"] == expected_gates, "gates")
    check(stored["status"] == "NONCONFIRM_DA_STRUCTURAL_CONTEXT" and stored["decision"] == "RETAIN_OPENING_CHAIN_CAPACITY_ONLY", "decision")
    check(stored["source_rows_accessed"] == 26184 and stored["masked_rows_joined"] == 5826 and stored["target_rows_scored"] == 1207 and stored["target_label_totals"] == {"DA": 315, "NONE": 892}, "access")
    check(stored["row_operation_labels_stored"] == 0 and stored["remainder_identities_stored"] == 0 and stored["event_loci_stored"] == 0 and stored["english_glosses"] == 0, "ceiling")
    check(TARGET_REPORT.read_text() == expected_report(position, neighbor), "report")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    maximum = max(independent.numeric_max(stored["POSITION"], {**position, "PASS": position_pass}), independent.numeric_max(stored["NEIGHBOR"], {**neighbor, "PASS": neighbor_pass}))
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_CONTEXT_TARGET_VALIDATION",
        "status": "PASS_PRODUCTION_FREE_DA_CONTEXT_NONCONFIRMATION_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "maximum_numeric_delta": maximum,
        "reconstructed_status": stored["status"],
        "reconstructed_decision": stored["decision"],
        "position_p": position["upper_p"],
        "neighbor_p": neighbor["upper_p"],
        "target_rows_reconstructed": 1207,
        "row_operation_labels_stored": 0,
        "english_glosses": 0,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "claim_ceiling": "Production-free reconstruction of the frozen DA context nonconfirmation only; no detachment, wordhood, prefix function, syntax, sound, language, cipher, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Opening-context target validation

Status: **{result['status']}**

A prior clean-room CPU implementation reconstructs the 26,184-row source join,
all 1,207 target assignments, exact quotas, both 8,192-assignment scores, gates,
decision, and report in **{checks}** checks. Maximum GPU-versus-CPU numeric
difference is **{maximum:.3g}**. Both systems remain nonconfirmations.

This supplies no detachment, wordhood, prefix function, syntax, sound,
language, cipher, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks, "maximum_numeric_delta": maximum}, sort_keys=True))


if __name__ == "__main__":
    main()
