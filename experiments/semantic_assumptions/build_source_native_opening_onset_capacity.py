#!/usr/bin/env python3
"""Build a target-label-masked first-member onset panel."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
PANEL = RESULTS / "source_native_opening_context_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
MEMBER_AUDIT = RESULTS / "source_native_opening_member_remainders.json"
MEMBER_VALIDATION = RESULTS / "source_native_opening_member_remainders_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_ONSET_CAPACITY_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT_PANEL = RESULTS / "source_native_opening_onset_masked.tsv"
OUT_JSON = RESULTS / "source_native_opening_onset_capacity.json"
OUT_REPORT = RESULTS / "source_native_opening_onset_capacity_report.md"

FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    PANEL: "6a043ba095d118594c9a8bd4bd4bf0ac96778963be0637400e353c517c5e616a",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    MEMBER_AUDIT: "3ba1a442cd36581d0562b4721a2ce2fffa3aeb01a8b4706edac1f6da211f675a",
    MEMBER_VALIDATION: "b8653ec6a42ed8bafb07e06894d2896f3d55fb68d9e9b03cb12acf5477db65f6",
    SPEC: "740ebd660724a3ae2e864e93c20d4ff5a083d577e0bf2eadc711c7edb61767a8",
}

PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
FIELDS = ("unit_id", "base_id", "physical_folio", "currier", "onset_id", "onset_consensus")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def operation(surface: str) -> tuple[str, str, int]:
    for prefix in PREFIXES:
        if surface.startswith(prefix):
            return prefix, surface[len(prefix):], len(prefix)
    return "NONE", surface, 0


def main() -> None:
    if any(path.exists() for path in (OUT_PANEL, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(MEMBER_AUDIT.read_text())["status"] != "PASS_MEMBER_RESOLVED_NONE_DA_CAPACITY" or json.loads(MEMBER_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_MEMBER_RESOLVED_NONE_DA_RECONSTRUCTION":
        raise ValueError("member safeguard")
    with PANEL.open(encoding="utf-8", newline="") as handle:
        panel_rows = list(csv.DictReader(handle, delimiter="\t"))
    with QUOTAS.open(encoding="utf-8", newline="") as handle:
        quota_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(panel_rows) != 5826 or len({row["unit_id"] for row in panel_rows}) != 5826:
        raise ValueError("panel identity")
    quotas = {(row["base_id"], row["physical_folio"]): (int(row["none_count"]), int(row["da_count"]), int(row["total_count"])) for row in quota_rows}
    if len(quotas) != 1763:
        raise ValueError("quota identity")
    grouped = defaultdict(list)
    for row in panel_rows:
        grouped[(row["base_id"], row["physical_folio"])].append(row)
    if set(grouped) != set(quotas) or any(len(grouped[key]) != quotas[key][2] for key in quotas):
        raise ValueError("quota geometry")
    mixed_keys = tuple(sorted(key for key, value in quotas.items() if value[0] and value[1]))
    selected = [row for key in mixed_keys for row in grouped[key]]
    if len(mixed_keys) != 197 or len(selected) != 1207:
        raise ValueError("mixed geometry")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    hidden = {}
    onset_values = {}
    for row in source_rows:
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        state, remainder, strip = operation(row["family_surface"])
        if not remainder or state not in {"NONE", "DA"}:
            continue
        sequences = tuple(tuple(row[field].split()) for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes"))
        if any(len(sequence) != int(row["symbol_count"]) for sequence in sequences):
            raise ValueError("member geometry")
        tails = tuple(sequence[strip:] for sequence in sequences)
        if any(len(tail) != len(remainder) for tail in tails):
            raise ValueError("remainder geometry")
        onset = tuple(tail[0] for tail in tails)
        unit_id = opaque("U", row["consensus_group_id"])
        if unit_id in hidden:
            raise ValueError("unit collision")
        hidden[unit_id] = (opaque("B", remainder), onset)
    output_rows = []
    for row in selected:
        if row["unit_id"] not in hidden or hidden[row["unit_id"]][0] != row["base_id"]:
            raise ValueError("source join")
        onset = hidden[row["unit_id"]][1]
        onset_id = opaque("O", "|".join(onset))
        if onset_id in onset_values and onset_values[onset_id] != onset:
            raise ValueError("onset collision")
        onset_values[onset_id] = onset
        output_rows.append({
            "unit_id": row["unit_id"],
            "base_id": row["base_id"],
            "physical_folio": row["physical_folio"],
            "currier": row["currier"],
            "onset_id": onset_id,
            "onset_consensus": int(len(set(onset)) == 1),
        })
    base_onsets = defaultdict(set)
    cell_onsets = defaultdict(set)
    pair_folios = defaultdict(set)
    for row in output_rows:
        base_onsets[row["base_id"]].add(row["onset_id"])
        cell_onsets[(row["base_id"], row["physical_folio"])].add(row["onset_id"])
        pair_folios[(row["base_id"], row["onset_id"])].add(row["physical_folio"])
    varying_cells = {key for key, values in cell_onsets.items() if len(values) >= 2}
    reused_pairs = {key for key, values in pair_folios.items() if len(values) >= 2}
    reused_rows = [row for row in output_rows if (row["base_id"], row["onset_id"]) in reused_pairs]
    capacity = {
        "rows": len(output_rows),
        "quota_cells": len(mixed_keys),
        "physical_folios": len({row["physical_folio"] for row in output_rows}),
        "family_remainders": len(base_onsets),
        "distinct_onset_triples": len(onset_values),
        "consensus_onset_rows": sum(int(row["onset_consensus"]) for row in output_rows),
        "onset_varying_family_remainders": sum(len(values) >= 2 for values in base_onsets.values()),
        "onset_varying_quota_cells": len(varying_cells),
        "rows_in_onset_varying_cells": sum((row["base_id"], row["physical_folio"]) in varying_cells for row in output_rows),
        "folios_with_onset_varying_cells": len({key[1] for key in varying_cells}),
        "loo_reused_rows": len(reused_rows),
        "loo_reused_folios": len({row["physical_folio"] for row in reused_rows}),
        "loo_reused_family_remainders": len({row["base_id"] for row in reused_rows}),
        "loo_reused_base_onset_pairs": len(reused_pairs),
    }
    gates = {
        "exact_1207_rows_197_cells_59_folios_44_bases": capacity["rows"] == 1207 and capacity["quota_cells"] == 197 and capacity["physical_folios"] == 59 and capacity["family_remainders"] == 44,
        "at_least_20_onset_triples": capacity["distinct_onset_triples"] >= 20,
        "at_least_25_onset_varying_bases": capacity["onset_varying_family_remainders"] >= 25,
        "at_least_75_onset_varying_cells": capacity["onset_varying_quota_cells"] >= 75,
        "at_least_500_rows_in_onset_varying_cells": capacity["rows_in_onset_varying_cells"] >= 500,
        "at_least_35_folios_with_onset_varying_cells": capacity["folios_with_onset_varying_cells"] >= 35,
        "at_least_1000_loo_reused_rows": capacity["loo_reused_rows"] >= 1000,
        "at_least_50_loo_reused_folios": capacity["loo_reused_folios"] >= 50,
        "at_least_25_loo_reused_bases": capacity["loo_reused_family_remainders"] >= 25,
        "at_least_40_loo_reused_base_onset_pairs": capacity["loo_reused_base_onset_pairs"] >= 40,
        "row_operation_labels_absent": set(output_rows[0]) == set(FIELDS),
    }
    status = "PASS_TARGET_MASKED_OPENING_ONSET_CAPACITY" if all(gates.values()) else "STOP_OPENING_ONSET_CAPACITY"
    with OUT_PANEL.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_ONSET_CAPACITY",
        "status": status,
        "decision": "FREEZE_TARGET_FREE_ONSET_COMPATIBILITY_CALIBRATION" if all(gates.values()) else "DO_NOT_CALIBRATE_ONSET_COMPATIBILITY",
        "inputs": {path.name: sha(path) for path in (*FROZEN, BUILDER)},
        "capacity": capacity,
        "gates": gates,
        "panel_sha256": sha(OUT_PANEL),
        "row_operation_labels_stored": 0,
        "prefix_member_codes_stored": 0,
        "full_remainder_signatures_stored": 0,
        "context_scores_computed": 0,
        "english_glosses": 0,
        "claim_ceiling": "Target-label-masked exact first-member compatibility capacity only; no detachment, allography, morphology, sound, wordhood, syntax, language, cipher operation, meaning, plaintext, or translation follows.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    OUT_REPORT.write_text(f"""# Exact-member onset compatibility capacity

Status: **{status}**

The label-masked panel retains **{capacity['rows']:,}** rows in
**{capacity['quota_cells']}** family-remainder/folio quota cells on
**{capacity['physical_folios']}** folios. It contains
**{capacity['distinct_onset_triples']}** opaque first-member triples;
**{capacity['onset_varying_family_remainders']}** family remainders and
**{capacity['onset_varying_quota_cells']}** cells vary internally. Exact
family/onset combinations recur outside the held folio for
**{capacity['loo_reused_rows']:,}** rows on **{capacity['loo_reused_folios']}**
folios across **{capacity['loo_reused_base_onset_pairs']}** reusable pairs.

All operation labels, prefix codes, full signatures, and context scores remain
absent. This authorizes target-free calibration only and supplies no
morphology, meaning, or translation.
""")
    print(json.dumps({"status": status, "capacity": capacity, "gates": gates}, sort_keys=True))


if __name__ == "__main__":
    main()
