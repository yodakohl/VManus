#!/usr/bin/env python3
"""Build the target-label-masked cross-base onset capacity panel."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
SOURCE_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
PANEL = RESULTS / "source_native_opening_onset_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
ONSET_VALIDATION = RESULTS / "source_native_opening_onset_capacity_validation.json"
TARGET_VALIDATION = RESULTS / "source_native_opening_onset_target_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_CROSSBASE_CAPACITY_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT_PANEL = RESULTS / "source_native_opening_crossbase_masked.tsv"
OUT = RESULTS / "source_native_opening_crossbase_capacity.json"
REPORT = RESULTS / "source_native_opening_crossbase_capacity_report.md"

FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    PANEL: "628d2f657db080b975f2e201d6d684f3dab7ede75b19be6cc4e4c4b3f580e4a2",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    ONSET_VALIDATION: "bdb86a58e5ee0ef9850554d7b65685c9cf0a35f1af06cefd30f676e17ec6abed",
    TARGET_VALIDATION: "4de622cdb7e0d79466931ce6dfb49ec1d9ba062393575ffe91d9a8d1a2e4c812",
    SPEC: "5009251fe5d7c3e41cd5dec52ab355dd8309173c96a16ef95c8cbc753b3035b6",
}

INPUT_FIELDS = ("unit_id", "base_id", "physical_folio", "currier", "onset_id", "onset_consensus")
OUTPUT_FIELDS = INPUT_FIELDS + ("onset_family_id", "crossbase_eligible")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def main() -> None:
    if any(path.exists() for path in (OUT_PANEL, OUT, REPORT)):
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(ONSET_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_1207_ROW_OPENING_ONSET_CAPACITY_RECONSTRUCTION":
        raise ValueError("onset capacity validation")
    if json.loads(TARGET_VALIDATION.read_text())["status"] != "PASS_PRODUCTION_FREE_OPENING_ONSET_TARGET_RECONSTRUCTION":
        raise ValueError("confirmed predecessor validation")

    with PANEL.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1207 or tuple(rows[0]) != INPUT_FIELDS or len({row["unit_id"] for row in rows}) != 1207:
        raise ValueError("masked panel")
    if any(set(row) != set(INPUT_FIELDS) for row in rows):
        raise ValueError("masked fields")

    with QUOTAS.open(encoding="utf-8", newline="") as handle:
        quota_rows = list(csv.DictReader(handle, delimiter="\t"))
    mixed = {(row["base_id"], row["physical_folio"]) for row in quota_rows if int(row["none_count"]) and int(row["da_count"])}
    cells: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        cells[(row["base_id"], row["physical_folio"])].append(index)
    if len(quota_rows) != 1763 or len(mixed) != 197 or set(cells) != mixed:
        raise ValueError("quota geometry")

    # Recover only the member-family mapping.  Scanning all STA positions avoids
    # reading or deriving an opening-operation label.
    onset_families: dict[str, str] = {}
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(source_rows) != 26184:
        raise ValueError("source rows")
    for row in source_rows:
        sequences = [row[field].split() for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
        if len({len(sequence) for sequence in sequences}) != 1:
            raise ValueError("member geometry")
        for members in zip(*sequences):
            families = {member[0] for member in members if member}
            if len(families) != 1:
                continue
            onset_id = opaque("O", "|".join(members))
            family = next(iter(families))
            if onset_id in onset_families and onset_families[onset_id] != family:
                raise ValueError("family collision")
            onset_families[onset_id] = family
    if any(row["onset_id"] not in onset_families for row in rows):
        raise ValueError("unmapped onset")

    base_folios: dict[str, set[str]] = defaultdict(set)
    onset_base_folios: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for row in rows:
        base_folios[row["base_id"]].add(row["physical_folio"])
        onset_base_folios[row["onset_id"]].add((row["base_id"], row["physical_folio"]))
    preliminary: set[int] = set()
    for index, row in enumerate(rows):
        base, folio, onset = row["base_id"], row["physical_folio"], row["onset_id"]
        other_base_support = {candidate_base for candidate_base, candidate_folio in onset_base_folios[onset] if candidate_base != base and candidate_folio != folio}
        if base_folios[base] - {folio} and len(other_base_support) >= 2:
            preliminary.add(index)
    eligible: set[int] = set()
    for indices in cells.values():
        candidates = [index for index in indices if index in preliminary]
        if len({rows[index]["onset_id"] for index in candidates}) >= 2:
            eligible.update(candidates)

    output_rows = []
    for index, row in enumerate(rows):
        output_rows.append({
            **row,
            "onset_family_id": opaque("F", onset_families[row["onset_id"]]),
            "crossbase_eligible": str(int(index in eligible)),
        })
    eligible_rows = [row for index, row in enumerate(output_rows) if index in eligible]
    eligible_cells = {(row["base_id"], row["physical_folio"]) for row in eligible_rows}
    eligible_bases = {row["base_id"] for row in eligible_rows}
    eligible_folios = {row["physical_folio"] for row in eligible_rows}
    eligible_onsets = {row["onset_id"] for row in eligible_rows}
    eligible_families = {row["onset_family_id"] for row in eligible_rows}
    base_counts = Counter(row["base_id"] for row in eligible_rows)
    family_bases: dict[str, set[str]] = defaultdict(set)
    family_onsets: dict[str, set[str]] = defaultdict(set)
    for row in eligible_rows:
        family_bases[row["onset_family_id"]].add(row["base_id"])
        family_onsets[row["onset_family_id"]].add(row["onset_id"])
    capacity = {
        "panel_rows": len(rows),
        "quota_cells": len(cells),
        "preliminary_rows": len(preliminary),
        "eligible_rows": len(eligible_rows),
        "eligible_cells": len(eligible_cells),
        "eligible_bases": len(eligible_bases),
        "eligible_folios": len(eligible_folios),
        "eligible_onsets": len(eligible_onsets),
        "eligible_onset_families": len(eligible_families),
        "maximum_base_row_fraction": max(base_counts.values()) / len(eligible_rows),
        "minimum_bases_per_family": min(map(len, family_bases.values())),
        "minimum_onsets_per_family": min(map(len, family_onsets.values())),
    }
    gates = {
        "exact_1207_rows_197_cells": capacity["panel_rows"] == 1207 and capacity["quota_cells"] == 197,
        "at_least_600_eligible_rows": capacity["eligible_rows"] >= 600,
        "at_least_90_eligible_cells": capacity["eligible_cells"] >= 90,
        "at_least_20_eligible_bases": capacity["eligible_bases"] >= 20,
        "at_least_35_eligible_folios": capacity["eligible_folios"] >= 35,
        "at_least_12_eligible_onsets": capacity["eligible_onsets"] >= 12,
        "at_least_5_eligible_families": capacity["eligible_onset_families"] >= 5,
        "maximum_base_fraction_at_most_015": capacity["maximum_base_row_fraction"] <= 0.15,
        "every_family_has_two_bases_and_onsets": capacity["minimum_bases_per_family"] >= 2 and capacity["minimum_onsets_per_family"] >= 2,
        "target_operation_labels_absent": tuple(output_rows[0]) == OUTPUT_FIELDS,
    }
    status = "PASS_TARGET_MASKED_CROSSBASE_ONSET_CAPACITY" if all(gates.values()) else "STOP_CROSSBASE_ONSET_CAPACITY"
    decision = "FREEZE_TARGET_FREE_CROSSBASE_MEMBER_CALIBRATION" if all(gates.values()) else "DO_NOT_CALIBRATE_CROSSBASE_MEMBER_TRANSFER"
    with OUT_PANEL.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_CROSSBASE_CAPACITY",
        "status": status,
        "decision": decision,
        "inputs": {path.name: sha(path) for path in (*FROZEN, BUILDER)},
        "capacity": capacity,
        "gates": gates,
        "panel_sha256": sha(OUT_PANEL),
        "row_operation_labels_stored": 0,
        "prefix_codes_stored": 0,
        "full_remainders_stored": 0,
        "target_scores_computed": 0,
        "english_glosses": 0,
        "claim_ceiling": "Target-label-masked capacity for simultaneous cross-base and cross-folio exact-member transfer only; no detachment, allomorphy, harmony, orthography, morphology, pronunciation, wordhood, POS, syntax, language, cipher operation, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Cross-base opening-member capacity

Status: **{status}**

The 1,207-row masked panel retains **{capacity['eligible_rows']}** scoreable rows
in **{capacity['eligible_cells']}** base/folio cells after simultaneous
held-base and held-folio support requirements. They span
**{capacity['eligible_bases']}** bases, **{capacity['eligible_folios']}** folios,
**{capacity['eligible_onsets']}** exact onset states, and
**{capacity['eligible_onset_families']}** member families. The largest base
contributes **{capacity['maximum_base_row_fraction']:.3%}** of eligible rows.

Decision: **{decision}**. This is target-label-masked capacity only. It
supplies no allomorphy, harmony, morphology, meaning, plaintext, or
translation.
""")
    print(json.dumps({"status": status, "decision": decision, "capacity": capacity, "gates": gates}, sort_keys=True))


if __name__ == "__main__":
    main()
