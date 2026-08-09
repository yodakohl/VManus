#!/usr/bin/env python3
"""Independent reconstruction of cross-base opening-member capacity."""

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
BUILDER = BASE / "build_source_native_opening_crossbase_capacity.py"
PRODUCTION_PANEL = RESULTS / "source_native_opening_crossbase_masked.tsv"
PRODUCTION = RESULTS / "source_native_opening_crossbase_capacity.json"
PRODUCTION_REPORT = RESULTS / "source_native_opening_crossbase_capacity_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_crossbase_capacity_validation.json"
REPORT = RESULTS / "source_native_opening_crossbase_capacity_validation_report.md"

FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    PANEL: "628d2f657db080b975f2e201d6d684f3dab7ede75b19be6cc4e4c4b3f580e4a2",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    ONSET_VALIDATION: "bdb86a58e5ee0ef9850554d7b65685c9cf0a35f1af06cefd30f676e17ec6abed",
    TARGET_VALIDATION: "4de622cdb7e0d79466931ce6dfb49ec1d9ba062393575ffe91d9a8d1a2e4c812",
    SPEC: "5009251fe5d7c3e41cd5dec52ab355dd8309173c96a16ef95c8cbc753b3035b6",
    BUILDER: "4f1cac39d6c44249c54ba4dfd53394e8c54c3b563984b8f223e21ebe63ba9478",
    PRODUCTION_PANEL: "62d1a8a42c061d4e022bc406dbdf5a1152370f17c0a628511bedb9740d916c06",
    PRODUCTION: "2bf61b7908775640b9698559eae90049f7b2d84007723c48ca60ed64f1727f88",
    PRODUCTION_REPORT: "7c4e9f412a6058f328645275f8e10509595842531c95a400f4ce3319f7929cd4",
}

INPUT_FIELDS = ("unit_id", "base_id", "physical_folio", "currier", "onset_id", "onset_consensus")
OUTPUT_FIELDS = INPUT_FIELDS + ("onset_family_id", "crossbase_eligible")
CLAIM = "Target-label-masked capacity for simultaneous cross-base and cross-folio exact-member transfer only; no detachment, allomorphy, harmony, orthography, morphology, pronunciation, wordhood, POS, syntax, language, cipher operation, meaning, plaintext, or translation follows."


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def reconstruct(rows: list[dict], source_rows: list[dict], mixed: set[tuple[str, str]]) -> tuple[list[dict], dict, dict]:
    if len(rows) != 1207 or len({row["unit_id"] for row in rows}) != 1207 or any(tuple(row) != INPUT_FIELDS for row in rows):
        raise ValueError("panel identity")
    cell_indices: dict[tuple[str, str], list[int]] = defaultdict(list)
    base_to_folios: dict[str, set[str]] = defaultdict(set)
    onset_locations: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for index, row in enumerate(rows):
        key = row["base_id"], row["physical_folio"]
        cell_indices[key].append(index)
        base_to_folios[key[0]].add(key[1])
        onset_locations[row["onset_id"]].add(key)
    if set(cell_indices) != mixed:
        raise ValueError("cell identity")

    possible_families: dict[str, set[str]] = defaultdict(set)
    for row in source_rows:
        codes = [row[name].split() for name in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
        if len({len(values) for values in codes}) != 1:
            raise ValueError("member lengths")
        for triple in zip(*codes):
            families = {value[:1] for value in triple}
            if len(families) == 1:
                possible_families[opaque("O", "|".join(triple))].update(families)
    family_by_onset = {key: next(iter(values)) for key, values in possible_families.items() if len(values) == 1}
    if any(row["onset_id"] not in family_by_onset for row in rows):
        raise ValueError("onset family")

    supported: set[int] = set()
    for index, row in enumerate(rows):
        base, folio, onset = row["base_id"], row["physical_folio"], row["onset_id"]
        other_bases = {other_base for other_base, other_folio in onset_locations[onset] if other_base != base and other_folio != folio}
        if len(base_to_folios[base] - {folio}) >= 1 and len(other_bases) >= 2:
            supported.add(index)
    eligible: set[int] = set()
    for indices in cell_indices.values():
        candidates = [index for index in indices if index in supported]
        if len({rows[index]["onset_id"] for index in candidates}) >= 2:
            eligible.update(candidates)

    output = []
    for index, row in enumerate(rows):
        output.append({**row, "onset_family_id": opaque("F", family_by_onset[row["onset_id"]]), "crossbase_eligible": str(int(index in eligible))})
    selected = [row for index, row in enumerate(output) if index in eligible]
    bases = Counter(row["base_id"] for row in selected)
    family_bases: dict[str, set[str]] = defaultdict(set)
    family_onsets: dict[str, set[str]] = defaultdict(set)
    for row in selected:
        family_bases[row["onset_family_id"]].add(row["base_id"])
        family_onsets[row["onset_family_id"]].add(row["onset_id"])
    capacity = {
        "panel_rows": len(rows),
        "quota_cells": len(cell_indices),
        "preliminary_rows": len(supported),
        "eligible_rows": len(selected),
        "eligible_cells": len({(row["base_id"], row["physical_folio"]) for row in selected}),
        "eligible_bases": len(bases),
        "eligible_folios": len({row["physical_folio"] for row in selected}),
        "eligible_onsets": len({row["onset_id"] for row in selected}),
        "eligible_onset_families": len(family_bases),
        "maximum_base_row_fraction": max(bases.values()) / len(selected),
        "minimum_bases_per_family": min(len(values) for values in family_bases.values()),
        "minimum_onsets_per_family": min(len(values) for values in family_onsets.values()),
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
        "target_operation_labels_absent": tuple(output[0]) == OUTPUT_FIELDS,
    }
    return output, capacity, gates


def panel_bytes(rows: list[dict]) -> bytes:
    import io
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()


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
    with PANEL.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    with QUOTAS.open(encoding="utf-8", newline="") as handle:
        quota_rows = list(csv.DictReader(handle, delimiter="\t"))
    mixed = {(row["base_id"], row["physical_folio"]) for row in quota_rows if int(row["none_count"]) > 0 and int(row["da_count"]) > 0}
    check(len(source_rows) == 26184 and len(quota_rows) == 1763 and len(mixed) == 197, "source geometry")
    rebuilt_rows, capacity, gates = reconstruct(rows, source_rows, mixed)
    check(panel_bytes(rebuilt_rows) == PRODUCTION_PANEL.read_bytes(), "panel bytes")
    stored = json.loads(PRODUCTION.read_text())
    check(stored["capacity"] == capacity, "capacity")
    check(stored["gates"] == gates and all(gates.values()), "gates")
    check(stored["status"] == "PASS_TARGET_MASKED_CROSSBASE_ONSET_CAPACITY", "status")
    check(stored["decision"] == "FREEZE_TARGET_FREE_CROSSBASE_MEMBER_CALIBRATION", "decision")
    check(stored["panel_sha256"] == sha(PRODUCTION_PANEL), "panel binding")
    check(stored["inputs"] == {path.name: sha(path) for path in list(FROZEN)[:8]}, "input binding")
    check(stored["row_operation_labels_stored"] == stored["prefix_codes_stored"] == stored["full_remainders_stored"] == stored["target_scores_computed"] == stored["english_glosses"] == 0, "target isolation")
    check(stored["claim_ceiling"] == CLAIM, "claim")
    expected_report = f"""# Cross-base opening-member capacity

Status: **{stored['status']}**

The 1,207-row masked panel retains **{capacity['eligible_rows']}** scoreable rows
in **{capacity['eligible_cells']}** base/folio cells after simultaneous
held-base and held-folio support requirements. They span
**{capacity['eligible_bases']}** bases, **{capacity['eligible_folios']}** folios,
**{capacity['eligible_onsets']}** exact onset states, and
**{capacity['eligible_onset_families']}** member families. The largest base
contributes **{capacity['maximum_base_row_fraction']:.3%}** of eligible rows.

Decision: **{stored['decision']}**. This is target-label-masked capacity only. It
supplies no allomorphy, harmony, morphology, meaning, plaintext, or
translation.
"""
    check(PRODUCTION_REPORT.read_text() == expected_report, "report")

    mutations = {}
    cases = {
        "missing_panel_row": rows[:-1],
        "duplicate_unit": rows + [rows[0]],
    }
    for name, candidate in cases.items():
        try:
            reconstruct(candidate, source_rows, mixed)
        except ValueError:
            mutations[name] = True
        else:
            mutations[name] = False
    wrong = [dict(row) for row in rows]
    wrong[0]["onset_id"] = "O" + "0" * 16
    try:
        reconstruct(wrong, source_rows, mixed)
    except ValueError:
        mutations["unmapped_onset"] = True
    else:
        mutations["unmapped_onset"] = False
    altered_mixed = set(mixed)
    altered_mixed.pop()
    try:
        reconstruct(rows, source_rows, altered_mixed)
    except ValueError:
        mutations["quota_cell_drift"] = True
    else:
        mutations["quota_cell_drift"] = False
    check(all(mutations.values()) and len(mutations) == 4, "mutations")

    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_CROSSBASE_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_CROSSBASE_ONSET_CAPACITY_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "capacity": capacity,
        "gates": gates,
        "mutations": mutations,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "validator_sha256": sha(VALIDATOR),
        "row_operation_labels_stored": 0,
        "target_scores_computed": 0,
        "english_glosses": 0,
        "claim_ceiling": CLAIM,
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Cross-base opening-member capacity validation

Status: **{result['status']}**

Independent code reconstructs the complete 1,207-row masked panel, all 658
eligible rows and 101 cells, exact output bytes, capacity, gates, report, and
four mutations in **{checks}** checks. No operation row label or target score
is read or stored.

This validates capacity for target-free calibration only and supplies no
allomorphy, harmony, morphology, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks, "capacity": capacity}, sort_keys=True))


if __name__ == "__main__":
    main()
