#!/usr/bin/env python3
"""Build the target-label-masked second-member incremental capacity panel."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
PANEL = RESULTS / "source_native_opening_onset_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
SURFACE_VALIDATION = RESULTS / "source_native_opening_onset_surface_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_SECOND_CAPACITY_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT_PANEL = RESULTS / "source_native_opening_second_masked.tsv"
OUT = RESULTS / "source_native_opening_second_capacity.json"
REPORT = RESULTS / "source_native_opening_second_capacity_report.md"

FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    PANEL: "628d2f657db080b975f2e201d6d684f3dab7ede75b19be6cc4e4c4b3f580e4a2",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    SURFACE_VALIDATION: "8017493d6b325e3455f552b82315fe67fc4357e22e5712fd8da046bbc824707a",
    SPEC: "f2a4945ef681c9143b238e0ce91901875474216fb79ded44015cc74b760b5747",
}

PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
INPUT_FIELDS = ("unit_id", "base_id", "physical_folio", "currier", "onset_id", "onset_consensus")
OUTPUT_FIELDS = INPUT_FIELDS + ("second_id", "second_consensus", "second_eligible")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def split(surface: str) -> tuple[str, str, int]:
    prefix = next((value for value in PREFIXES if surface.startswith(value)), "")
    return prefix or "NONE", surface[len(prefix):], len(prefix)


def main() -> None:
    if any(path.exists() for path in (OUT_PANEL, OUT, REPORT)):
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(SURFACE_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_STA_SURFACE_RECLASSIFICATION_RECONSTRUCTION":
        raise ValueError("surface interpretation validation")
    with PANEL.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with QUOTAS.open(encoding="utf-8", newline="") as handle:
        quota_rows = list(csv.DictReader(handle, delimiter="\t"))
    mixed = {(row["base_id"], row["physical_folio"]) for row in quota_rows if int(row["none_count"]) and int(row["da_count"])}
    if len(rows) != 1207 or len({row["unit_id"] for row in rows}) != 1207 or any(tuple(row) != INPUT_FIELDS for row in rows) or len(quota_rows) != 1763 or len(mixed) != 197:
        raise ValueError("masked geometry")
    if {(row["base_id"], row["physical_folio"]) for row in rows} != mixed:
        raise ValueError("quota cells")

    hidden = {}
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(source_rows) != 26184:
        raise ValueError("source geometry")
    for row in source_rows:
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        state, remainder, cut = split(row["family_surface"])
        if state not in {"NONE", "DA"} or not remainder:
            continue
        sequences = [row[field].split()[cut:] for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
        if any(len(sequence) != len(remainder) for sequence in sequences):
            raise ValueError("remainder geometry")
        onset = tuple(sequence[0] for sequence in sequences)
        second = tuple(sequence[1] for sequence in sequences) if len(remainder) >= 2 else None
        identity = opaque("U", row["consensus_group_id"])
        if identity in hidden:
            raise ValueError("hidden identity")
        hidden[identity] = opaque("B", remainder), opaque("O", "|".join(onset)), second

    enriched = []
    for row in rows:
        if row["unit_id"] not in hidden:
            raise ValueError("source join")
        base, onset, second = hidden[row["unit_id"]]
        if base != row["base_id"] or onset != row["onset_id"]:
            raise ValueError("binding drift")
        enriched.append({
            **row,
            "second_id": "NA" if second is None else opaque("S", "|".join(second)),
            "second_consensus": "NA" if second is None else str(int(len(set(second)) == 1)),
            "second_eligible": "0",
        })
    baseline_seconds: dict[tuple[str, str], set[str]] = defaultdict(set)
    full_folios: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in enriched:
        if row["second_id"] == "NA":
            continue
        baseline = row["base_id"], row["onset_id"]
        baseline_seconds[baseline].add(row["second_id"])
        full_folios[(*baseline, row["second_id"])].add(row["physical_folio"])
    preliminary = {
        index for index, row in enumerate(enriched)
        if row["second_id"] != "NA"
        and len(baseline_seconds[(row["base_id"], row["onset_id"])]) >= 2
        and len(full_folios[(row["base_id"], row["onset_id"], row["second_id"])]) >= 2
    }
    preliminary_folios = Counter(enriched[index]["physical_folio"] for index in preliminary)
    eligible = {index for index in preliminary if preliminary_folios[enriched[index]["physical_folio"]] >= 3}
    for index in eligible:
        enriched[index]["second_eligible"] = "1"
    selected = [row for index, row in enumerate(enriched) if index in eligible]
    folio_counts = Counter(row["physical_folio"] for row in selected)
    capacity = {
        "panel_rows": len(enriched),
        "quota_cells": len(mixed),
        "rows_with_second_member": sum(row["second_id"] != "NA" for row in enriched),
        "preliminary_rows": len(preliminary),
        "eligible_rows": len(selected),
        "eligible_folios": len(folio_counts),
        "eligible_bases": len({row["base_id"] for row in selected}),
        "varying_baselines": len({(row["base_id"], row["onset_id"]) for row in selected}),
        "reusable_refinements": len({(row["base_id"], row["onset_id"], row["second_id"]) for row in selected}),
        "second_member_triplets": len({row["second_id"] for row in selected}),
        "consensus_second_rows": sum(row["second_consensus"] == "1" for row in selected),
        "currier_A_rows": sum(row["currier"] == "A" for row in selected),
        "currier_B_rows": sum(row["currier"] == "B" for row in selected),
        "maximum_folio_row_fraction": max(folio_counts.values()) / len(selected),
    }
    gates = {
        "exact_1207_rows_197_cells": capacity["panel_rows"] == 1207 and capacity["quota_cells"] == 197,
        "at_least_600_eligible_rows": capacity["eligible_rows"] >= 600,
        "at_least_40_eligible_folios": capacity["eligible_folios"] >= 40,
        "at_least_15_eligible_bases": capacity["eligible_bases"] >= 15,
        "at_least_25_varying_baselines": capacity["varying_baselines"] >= 25,
        "at_least_35_reusable_refinements": capacity["reusable_refinements"] >= 35,
        "at_least_12_second_member_triplets": capacity["second_member_triplets"] >= 12,
        "at_least_600_consensus_second_rows": capacity["consensus_second_rows"] >= 600,
        "at_least_100_rows_each_currier": min(capacity["currier_A_rows"], capacity["currier_B_rows"]) >= 100,
        "maximum_folio_fraction_at_most_010": capacity["maximum_folio_row_fraction"] <= 0.10,
        "operation_labels_absent": tuple(enriched[0]) == OUTPUT_FIELDS,
    }
    status = "PASS_TARGET_MASKED_SECOND_MEMBER_INCREMENT_CAPACITY" if all(gates.values()) else "STOP_SECOND_MEMBER_INCREMENT_CAPACITY"
    decision = "FREEZE_TARGET_FREE_SECOND_MEMBER_CALIBRATION" if all(gates.values()) else "DO_NOT_CALIBRATE_SECOND_MEMBER_INCREMENT"
    with OUT_PANEL.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(enriched)
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_SECOND_CAPACITY",
        "status": status,
        "decision": decision,
        "inputs": {path.name: sha(path) for path in (*FROZEN, BUILDER)},
        "capacity": capacity,
        "gates": gates,
        "panel_sha256": sha(OUT_PANEL),
        "row_operation_labels_stored": 0,
        "prefix_codes_stored": 0,
        "complete_member_sequences_stored": 0,
        "target_scores_computed": 0,
        "english_glosses": 0,
        "claim_ceiling": "Target-label-masked capacity for a second-member increment beyond fixed coarse base and exact first onset only; no longer dependency, morphology, sound, word function, POS, syntax, language, cipher operation, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Second-member incremental opening capacity

Status: **{status}**

After fixing coarse base and exact first onset, the target-label-masked panel
retains **{capacity['eligible_rows']}** second-member rows on
**{capacity['eligible_folios']}** folios and **{capacity['eligible_bases']}**
bases. They span **{capacity['varying_baselines']}** varying baselines,
**{capacity['reusable_refinements']}** reusable exact refinements, and
**{capacity['second_member_triplets']}** second-member triplets;
**{capacity['consensus_second_rows']}/{capacity['eligible_rows']}** rows agree
in all three readings.

Decision: **{decision}**. This is masked capacity only and supplies no longer
dependency, morphology, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": status, "decision": decision, "capacity": capacity, "gates": gates}, sort_keys=True))


if __name__ == "__main__":
    main()
