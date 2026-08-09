#!/usr/bin/env python3
"""Production-free reconstruction of the exact-member onset target."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

import validate_source_native_opening_onset_preflight as independent


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
INDEPENDENT = BASE / "validate_source_native_opening_onset_preflight.py"
CORE = BASE / "source_native_opening_onset_core.py"
SPEC = BASE / "SOURCE_NATIVE_OPENING_ONSET_TARGET_SPEC.md"
RUNNER = BASE / "run_source_native_opening_onset_target.py"
PRODUCTION = RESULTS / "source_native_opening_onset_target.json"
PRODUCTION_REPORT = RESULTS / "source_native_opening_onset_target_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_onset_target_validation.json"
REPORT = RESULTS / "source_native_opening_onset_target_validation_report.md"

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
    INDEPENDENT: "fc7cfb93a4fa9a8842f283f2a04fd1c8010fea68a30825dc0938a85a6c0cb108",
    CORE: "33c1870c0e8f80516a02573a279f78b2eba4b12a2b2225bfe864525d18bc2adf",
    SPEC: "e4b2fb7d04098587aa815e343d9fb5ab5ba3526547426bca232b2b77d2e64e81",
    RUNNER: "5b167e893c2877c0f9038d48c6fb8223ff15aa3691e5a2eadb27ef21376b3f0a",
    PRODUCTION: "677408e4431f5ee6fad410e07e6e1f7cd64762c074383cf5fda62708d9c0982f",
    PRODUCTION_REPORT: "b482ed4ab996761e393f0dfc5930c09774ab39ca86ce046a3ee6480102eb7748",
}

PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
CLAIM = (
    "Exact first-member compatibility with dominant D1-A1 selection only; no "
    "detachment, morphology, pronunciation, wordhood, POS, syntax, language, "
    "cipher operation, meaning, plaintext, or translation follows."
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def operation(surface: str) -> tuple[str, str]:
    for prefix in PREFIXES:
        if surface.startswith(prefix):
            return prefix, surface[len(prefix):]
    return "NONE", surface


def digest(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array, dtype="<f8").tobytes()).hexdigest()


def numeric_delta(left, right) -> float:
    if isinstance(left, dict):
        if set(left) != set(right):
            return math.inf
        return max((numeric_delta(left[key], right[key]) for key in left), default=0.0)
    if isinstance(left, list):
        if len(left) != len(right):
            return math.inf
        return max((numeric_delta(a, b) for a, b in zip(left, right)), default=0.0)
    if isinstance(left, (int, float)) and not isinstance(left, bool):
        return abs(float(left) - float(right))
    return 0.0 if left == right else math.inf


def derive_hidden(source_rows: list[dict]) -> dict[str, tuple[str, str]]:
    hidden: dict[str, tuple[str, str]] = {}
    for row in source_rows:
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        state, base = operation(row["family_surface"])
        if not base or state not in {"NONE", "DA"}:
            continue
        unit_id = opaque("U", row["consensus_group_id"])
        if unit_id in hidden:
            raise ValueError("duplicate hidden identity")
        hidden[unit_id] = state, opaque("B", base)
    return hidden


def join_labels(panel, hidden: dict[str, tuple[str, str]]) -> np.ndarray:
    labels = np.empty(len(panel.rows), dtype=np.float64)
    for index, row in enumerate(panel.rows):
        if row["unit_id"] not in hidden:
            raise ValueError("missing target identity")
        state, base = hidden[row["unit_id"]]
        if base != row["base_id"]:
            raise ValueError("base mismatch")
        labels[index] = 1.0 if state == "DA" else 0.0
    for indices, expected in zip(panel.strata_rows, panel.quota):
        if int(labels[indices].sum()) != int(expected):
            raise ValueError("quota drift")
    return labels


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures: list[str] = []
    checks = 0

    def check(value: bool, name: str) -> None:
        nonlocal checks
        checks += 1
        if not value:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, "hash:" + path.name)

    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    check(len(source_rows) == 26184, "source rows")
    check(len({row["consensus_group_id"] for row in source_rows}) == 26184, "source identities")

    panel = independent.load_panel()
    hidden = derive_hidden(source_rows)
    actual = join_labels(panel, hidden)
    counts = Counter(actual)
    check(counts == Counter({0.0: 892, 1.0: 315}), "label totals")
    check(len(actual) == 1207 and int(panel.eligible.sum()) == 1141 and len(panel.folios) == 59, "capacity")
    check(all(int(actual[indices].sum()) == int(expected) for indices, expected in zip(panel.strata_rows, panel.quota)), "quotas")

    null = independent.labels_from_ranks(panel, 8192, "PREFLIGHT_NULL")
    rebuilt = independent.summaries(panel, actual[None, :], null)[0]
    rebuilt["PASS"] = independent.passing(rebuilt)
    stored = json.loads(PRODUCTION.read_text())
    maximum = numeric_delta(rebuilt, stored["summary"])
    check(maximum == 0.0, "summary")
    check(stored["target_label_sha256"] == digest(actual), "target digest")
    check(stored["null_label_orbit_sha256"] == digest(null), "null digest")

    gates = {
        "exact_26184_source_rows": len(source_rows) == 26184,
        "exact_1207_target_join": len(actual) == 1207,
        "exact_892_NONE_315_DA": counts == Counter({0.0: 892, 1.0: 315}),
        "every_quota_exact": all(int(actual[indices].sum()) == int(expected) for indices, expected in zip(panel.strata_rows, panel.quota)),
        "exact_1141_eligible_rows_59_folios": int(panel.eligible.sum()) == 1141 and len(panel.folios) == 59,
        "ONSET_COMPATIBILITY_PASS": rebuilt["PASS"],
    }
    check(gates == stored["gates"] and all(gates.values()), "gates")
    check(stored["status"] == "CONFIRM_EXACT_ONSET_CONDITIONS_D1_A1_SELECTION", "status")
    check(stored["decision"] == "RETAIN_TRANSFERABLE_MEMBER_ONSET_COMPATIBILITY", "decision")
    check(stored["claim_ceiling"] == CLAIM, "claim")
    expected_inputs = {path.name: sha(path) for path in FROZEN if path not in {INDEPENDENT, PRODUCTION, PRODUCTION_REPORT}}
    check(stored["inputs"] == expected_inputs, "input binding")
    check(stored["source_rows_accessed"] == 26184 and stored["target_rows_joined"] == 1207, "access counts")
    check(stored["target_label_totals"] == {"DA": 315, "NONE": 892}, "stored totals")
    check(stored["eligible_rows_scored"] == 1141 and stored["physical_folios"] == 59, "stored capacity")
    check(stored["row_operation_labels_stored"] == stored["event_loci_or_pages_stored"] == stored["remainder_identities_stored"] == stored["english_glosses"] == 0, "storage boundary")

    expected_report = f"""# Exact-member onset compatibility target

Status: **{stored['status']}**

The one-shot target joins **1,207** rows, scores **1,141** held-folio-reusable
rows on **59** folios, and preserves all **197** exact label quotas. The
base-plus-onset model gains **{rebuilt['observed']:.6f}** nat/eligible row over
the base-only model (null mean **{rebuilt['null_mean']:.6f}**, z=**{rebuilt['z']:.3f}**,
p=**{rebuilt['upper_p']:.6f}**). Folio support is
**{rebuilt['positive_folios']}/59**; Currier A/B means are
**{rebuilt['currier_A_mean']:.6f} / {rebuilt['currier_B_mean']:.6f}**.

Decision: **{stored['decision']}**. No row label, locus, page, or remainder identity is
stored. This supplies no morphology, pronunciation, word meaning, plaintext,
or translation.
"""
    check(PRODUCTION_REPORT.read_text() == expected_report, "report")

    mutations: dict[str, bool] = {}
    for name, mutate in {
        "missing_source_identity": lambda rows: rows[:-1],
        "duplicate_source_identity": lambda rows: rows + [rows[0]],
    }.items():
        candidate = mutate(source_rows.copy())
        try:
            if len(candidate) != 26184 or len({row["consensus_group_id"] for row in candidate}) != 26184:
                raise ValueError("identity")
            join_labels(panel, derive_hidden(candidate))
        except ValueError:
            mutations[name] = True
        else:
            mutations[name] = False
    wrong = {key: value for key, value in hidden.items()}
    first = panel.rows[0]["unit_id"]
    wrong[first] = wrong[first][0], "B" + "0" * 16
    try:
        join_labels(panel, wrong)
    except ValueError:
        mutations["wrong_base_binding"] = True
    else:
        mutations["wrong_base_binding"] = False
    drift = {key: value for key, value in hidden.items()}
    for index in panel.strata_rows[0]:
        unit_id = panel.rows[int(index)]["unit_id"]
        state, base = drift[unit_id]
        drift[unit_id] = ("NONE" if state == "DA" else "DA"), base
        break
    try:
        join_labels(panel, drift)
    except ValueError:
        mutations["quota_drift"] = True
    else:
        mutations["quota_drift"] = False
    check(all(mutations.values()) and len(mutations) == 4, "mutations")

    if failures:
        raise SystemExit("validation failed: " + failures[0])

    result = {
        "experiment": "SOURCE_NATIVE_OPENING_ONSET_TARGET_VALIDATION",
        "status": "PASS_PRODUCTION_FREE_OPENING_ONSET_TARGET_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "maximum_numeric_delta": maximum,
        "source_rows_reconstructed": len(source_rows),
        "target_rows_joined": len(actual),
        "eligible_rows_scored": int(panel.eligible.sum()),
        "physical_folios": len(panel.folios),
        "target_label_totals": {"DA": int(actual.sum()), "NONE": int(len(actual) - actual.sum())},
        "summary": rebuilt,
        "mutations": mutations,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "validator_sha256": sha(VALIDATOR),
        "row_operation_labels_stored": 0,
        "event_loci_or_pages_stored": 0,
        "remainder_identities_stored": 0,
        "english_glosses": 0,
        "claim_ceiling": CLAIM,
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Exact-member onset target validation

Status: **{result['status']}**

A production-free implementation independently reconstructs the 26,184-row
source join, all 1,207 target labels and 197 quotas, the complete 8,192-label
null orbit, every score and gate, the exact report, and four mutations in
**{checks}** checks with zero numeric discrepancy.

The result retains a transferable formal compatibility between the exact first
remainder member and dominant `D1 A1` selection. It supplies no morphology,
pronunciation, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks, "maximum_numeric_delta": maximum}, sort_keys=True))


if __name__ == "__main__":
    main()
