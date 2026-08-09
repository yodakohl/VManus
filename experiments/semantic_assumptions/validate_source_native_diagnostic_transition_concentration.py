#!/usr/bin/env python3
"""Production-free reconstruction of the diagnostic concentration audit."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np

import validate_source_native_diagnostic_transition_preflight as independent
import validate_source_native_diagnostic_transition_target as target_validator


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL = RESULTS / "source_native_diagnostic_transition_masked.tsv"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
SPEC = BASE / "SOURCE_NATIVE_DIAGNOSTIC_CONCENTRATION_AUDIT_SPEC.md"
AUDITOR = BASE / "audit_source_native_diagnostic_transition_concentration.py"
TARGET = RESULTS / "source_native_diagnostic_transition_target.json"
TARGET_VALIDATION = RESULTS / "source_native_diagnostic_transition_target_validation.json"
TSV = RESULTS / "source_native_diagnostic_transition_concentration.tsv"
PRODUCTION = RESULTS / "source_native_diagnostic_transition_concentration.json"
PRODUCTION_REPORT = RESULTS / "source_native_diagnostic_transition_concentration_report.md"
OUT = RESULTS / "source_native_diagnostic_transition_concentration_validation.json"
REPORT = RESULTS / "source_native_diagnostic_transition_concentration_validation_report.md"

FROZEN = {
    PANEL: "7ed9f8186dcb31bd49a446e6b7751dc0bfc0f9d508feb816314fc71105daea02",
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SPEC: "03b545c5096abcb332b4b34126feedd8eb9a8c128653402aede5db05e85bdca7",
    AUDITOR: "ea7862488989dddca2b4a38470bac62c18c91a762c2601999f380ba47ef68db5",
    TARGET: "f01ca643dda1030b6fb7d43efa04c87a81e111e2c43a38c669f1380a67d34182",
    TARGET_VALIDATION: "4b6eb35f19c0a0152ac5947e070daa026ee5d4cb549f09d5b68aea56904ec294",
    TSV: "ad9a9d5d7daa1b365635f85a61aed879c0d778751d5eecaf912d9d2705735b32",
    PRODUCTION: "be64e18dc3c153d268eb28e43d33717ebc6284c9697f4d0651cc9b37b2a3e37b",
    PRODUCTION_REPORT: "649aaae928cf87f650ba0fa7bbe5672ed80fdb04b45960fa3ac1647b3e507e74",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rebuild_rows(panel, sequences):
    rows = []
    summaries = {}
    for ensemble in ("SECTION_KIND_LENGTH", "FOLIO_KIND_LENGTH"):
        favored, disfavored, favored_folio, disfavored_folio, _ = independent.compute(
            panel, sequences, ensemble, 8192
        )
        favored_residual = favored_folio[0] - favored_folio[1:].mean(axis=0)
        disfavored_residual = disfavored_folio[0] - disfavored_folio[1:].mean(axis=0)
        favored_denominator = float(np.abs(favored_residual).sum())
        disfavored_denominator = float(np.abs(disfavored_residual).sum())
        for index, folio in enumerate(panel.folios):
            favored_without = favored - favored_folio[:, index]
            disfavored_without = disfavored - disfavored_folio[:, index]
            mask = panel.folio_index == index
            rows.append(
                {
                    "ensemble": ensemble,
                    "physical_folio": folio,
                    "groups": int(mask.sum()),
                    "noninitial_positions": int(np.maximum(0, panel.lengths[mask] - 1).sum()),
                    "observed_favored": int(favored_folio[0, index]),
                    "null_mean_favored": float(favored_folio[1:, index].mean()),
                    "favored_residual": float(favored_residual[index]),
                    "favored_abs_contribution_fraction": float(abs(favored_residual[index]) / favored_denominator) if favored_denominator else 1.0,
                    "observed_disfavored": int(disfavored_folio[0, index]),
                    "null_mean_disfavored": float(disfavored_folio[1:, index].mean()),
                    "disfavored_residual": float(disfavored_residual[index]),
                    "disfavored_abs_contribution_fraction": float(abs(disfavored_residual[index]) / disfavored_denominator) if disfavored_denominator else 1.0,
                    "deletion_favored_upper_p": float(np.mean(favored_without >= favored_without[0])),
                    "deletion_disfavored_lower_p": float(np.mean(disfavored_without <= disfavored_without[0])),
                }
            )
        maximum = max(
            (row for row in rows if row["ensemble"] == ensemble),
            key=lambda row: (row["favored_abs_contribution_fraction"], row["physical_folio"]),
        )
        summaries[ensemble] = {
            "maximum_favored_folio": maximum["physical_folio"],
            "maximum_favored_abs_contribution_fraction": maximum["favored_abs_contribution_fraction"],
            "maximum_folio_favored_residual": maximum["favored_residual"],
            "maximum_folio_groups": maximum["groups"],
            "maximum_folio_noninitial_positions": maximum["noninitial_positions"],
            "maximum_deletion_favored_upper_p": maximum["deletion_favored_upper_p"],
            "maximum_deletion_disfavored_lower_p": maximum["deletion_disfavored_lower_p"],
            "all_deletion_favored_p_at_most_01": all(row["deletion_favored_upper_p"] <= 0.01 for row in rows if row["ensemble"] == ensemble),
            "all_deletion_disfavored_p_at_most_01": all(row["deletion_disfavored_lower_p"] <= 0.01 for row in rows if row["ensemble"] == ensemble),
        }
    return rows, summaries


def serialize_tsv(rows) -> str:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue()


def expected_report(summaries) -> str:
    section = summaries["SECTION_KIND_LENGTH"]
    held = summaries["FOLIO_KIND_LENGTH"]
    return f"""# Diagnostic transition concentration audit

Status: **PASS_POST_RESULT_CONCENTRATION_DIAGNOSTIC**

The largest favored contributor is **{section['maximum_favored_folio']}** under
`SECTION_KIND_LENGTH` ({section['maximum_favored_abs_contribution_fraction']:.3%};
{section['maximum_folio_groups']} groups / {section['maximum_folio_noninitial_positions']}
positions) and **{held['maximum_favored_folio']}** under `FOLIO_KIND_LENGTH`
({held['maximum_favored_abs_contribution_fraction']:.3%};
{held['maximum_folio_groups']} groups / {held['maximum_folio_noninitial_positions']}
positions). Deleting those folios gives favored p
**{section['maximum_deletion_favored_upper_p']:.6f} / {held['maximum_deletion_favored_upper_p']:.6f}**
and disfavored p
**{section['maximum_deletion_disfavored_lower_p']:.6f} / {held['maximum_deletion_disfavored_lower_p']:.6f}**.

This audit changes no registered gate or decision. The result remains a frozen
nonconfirmation and supplies no wordhood, ownership, label meaning, picture
identity, sound, language, cipher, plaintext, or translation.
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
    panel = independent.load_panel()
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    sequences, _ = target_validator.join(panel, source_rows)
    rows, summaries = rebuild_rows(panel, sequences)
    check(len(rows) == 52, "rows")
    check(serialize_tsv(rows) == TSV.read_text(), "tsv-bytes")
    stored = json.loads(PRODUCTION.read_text())
    check(stored["ensembles"] == summaries, "summaries")
    check(stored["tsv_sha256"] == sha(TSV), "tsv-binding")
    check(stored["rows"] == 52 and stored["original_gate_changed"] is False, "decision-lock")
    check(stored["original_target_status"] == "NONCONFIRM_PROSE_GRAPH_TRANSFER_TO_DIAGNOSTIC_TEXT", "status-lock")
    check(stored["original_target_decision"] == "RETAIN_PROSE_LOCAL_TRANSITION_GRAMMAR_ONLY", "claim-lock")
    check(stored["event_level_sequences_stored"] == 0 and stored["event_level_pairs_stored"] == 0 and stored["member_codes_accessed"] == 0 and stored["english_glosses"] == 0, "ceiling")
    check(PRODUCTION_REPORT.read_text() == expected_report(summaries), "report-bytes")
    check(all(value["maximum_favored_folio"] == "f68" for value in summaries.values()), "f68")
    check(all(value["all_deletion_favored_p_at_most_01"] and value["all_deletion_disfavored_p_at_most_01"] for value in summaries.values()), "all-deletions")
    check(all(math.isclose(value["maximum_deletion_favored_upper_p"], 1 / 8192) and math.isclose(value["maximum_deletion_disfavored_lower_p"], 1 / 8192) for value in summaries.values()), "maximum-deletion-tail")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_CONCENTRATION_VALIDATION",
        "status": "PASS_PRODUCTION_FREE_52_ROW_CONCENTRATION_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "maximum_favored_folio_both_ensembles": "f68",
        "all_52_deletions_both_tails_p_at_most_01": True,
        "maximum_folio_deletion_p": 1 / 8192,
        "original_decision_unchanged": True,
        "event_level_sequences_stored": 0,
        "english_glosses": 0,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "claim_ceiling": "Production-free reconstruction of the post-result concentration diagnosis only; the frozen diagnostic-transfer nonconfirmation is unchanged and no meaning or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        f"""# Diagnostic concentration audit validation

Status: **{result['status']}**

A production-free implementation reconstructs the two complete 8,192-assignment
orbits, all **52** folio rows, their exact TSV bytes, both summaries, all deletion
tails, and the report in **{checks}** checks. Folio f68 is the largest favored
contributor in both ensembles, but every one-folio deletion retains both tails
at p<=.01; deleting f68 itself leaves both tails at p=1/8192.

The original concentration gate and nonconfirmation remain unchanged. This
supplies no wordhood, label meaning, sound, language, cipher, plaintext, or
translation.
"""
    )
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
