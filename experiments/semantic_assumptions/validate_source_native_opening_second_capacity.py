#!/usr/bin/env python3
"""Independent reconstruction of second-member incremental capacity."""

from __future__ import annotations

import csv
import hashlib
import io
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
BUILDER = BASE / "build_source_native_opening_second_capacity.py"
PRODUCTION_PANEL = RESULTS / "source_native_opening_second_masked.tsv"
PRODUCTION = RESULTS / "source_native_opening_second_capacity.json"
PRODUCTION_REPORT = RESULTS / "source_native_opening_second_capacity_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_second_capacity_validation.json"
REPORT = RESULTS / "source_native_opening_second_capacity_validation_report.md"

FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    PANEL: "628d2f657db080b975f2e201d6d684f3dab7ede75b19be6cc4e4c4b3f580e4a2",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    SURFACE_VALIDATION: "8017493d6b325e3455f552b82315fe67fc4357e22e5712fd8da046bbc824707a",
    SPEC: "f2a4945ef681c9143b238e0ce91901875474216fb79ded44015cc74b760b5747",
    BUILDER: "fea5a5700fb932cc02ea5801ce6d235aa1756a11bca82624d1168da56aba6a9c",
    PRODUCTION_PANEL: "46f0c8ad22880b870afc54d96852781b4bea9ebdc885dc1164c1da742a7bc581",
    PRODUCTION: "bf0ed5ce9c758b81797564a627e8fe8676e18fb902352d66f7163cd677f149d1",
    PRODUCTION_REPORT: "132bc699e97d666cc052053fd94757e92a9fd570395dee834d28a83ae1102ad4",
}

PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
INPUT_FIELDS = ("unit_id", "base_id", "physical_folio", "currier", "onset_id", "onset_consensus")
OUTPUT_FIELDS = INPUT_FIELDS + ("second_id", "second_consensus", "second_eligible")
CLAIM = "Target-label-masked capacity for a second-member increment beyond fixed coarse base and exact first onset only; no longer dependency, morphology, sound, word function, POS, syntax, language, cipher operation, meaning, plaintext, or translation follows."


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def split(surface: str):
    prefix = next((value for value in PREFIXES if surface.startswith(value)), "")
    return prefix or "NONE", surface[len(prefix):], len(prefix)


def reconstruct(source_rows, panel_rows, quota_rows):
    mixed = {(row["base_id"], row["physical_folio"]) for row in quota_rows if int(row["none_count"]) > 0 and int(row["da_count"]) > 0}
    if len(source_rows) != 26184 or len(panel_rows) != 1207 or len({row["unit_id"] for row in panel_rows}) != 1207 or any(tuple(row) != INPUT_FIELDS for row in panel_rows) or len(quota_rows) != 1763 or len(mixed) != 197:
        raise ValueError("geometry")
    hidden = {}
    for row in source_rows:
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        state, remainder, cut = split(row["family_surface"])
        if state not in {"NONE", "DA"} or not remainder:
            continue
        sequences = [row[field].split()[cut:] for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
        if any(len(sequence) != len(remainder) for sequence in sequences):
            raise ValueError("members")
        first = tuple(sequence[0] for sequence in sequences)
        second = tuple(sequence[1] for sequence in sequences) if len(remainder) >= 2 else None
        identity = opaque("U", row["consensus_group_id"])
        if identity in hidden:
            raise ValueError("duplicate")
        hidden[identity] = opaque("B", remainder), opaque("O", "|".join(first)), second
    output = []
    for row in panel_rows:
        if row["unit_id"] not in hidden:
            raise ValueError("join")
        base, onset, second = hidden[row["unit_id"]]
        if base != row["base_id"] or onset != row["onset_id"]:
            raise ValueError("binding")
        output.append({**row, "second_id": "NA" if second is None else opaque("S", "|".join(second)), "second_consensus": "NA" if second is None else str(int(len(set(second)) == 1)), "second_eligible": "0"})
    if {(row["base_id"], row["physical_folio"]) for row in output} != mixed:
        raise ValueError("cells")
    baseline_states, full_folios = defaultdict(set), defaultdict(set)
    for row in output:
        if row["second_id"] != "NA":
            baseline = row["base_id"], row["onset_id"]
            baseline_states[baseline].add(row["second_id"])
            full_folios[(*baseline, row["second_id"])].add(row["physical_folio"])
    preliminary = {index for index, row in enumerate(output) if row["second_id"] != "NA" and len(baseline_states[(row["base_id"], row["onset_id"])]) >= 2 and len(full_folios[(row["base_id"], row["onset_id"], row["second_id"])]) >= 2}
    folio_preliminary = Counter(output[index]["physical_folio"] for index in preliminary)
    eligible = {index for index in preliminary if folio_preliminary[output[index]["physical_folio"]] >= 3}
    for index in eligible:
        output[index]["second_eligible"] = "1"
    selected = [row for index, row in enumerate(output) if index in eligible]
    folios = Counter(row["physical_folio"] for row in selected)
    capacity = {
        "panel_rows": len(output), "quota_cells": len(mixed),
        "rows_with_second_member": sum(row["second_id"] != "NA" for row in output),
        "preliminary_rows": len(preliminary), "eligible_rows": len(selected),
        "eligible_folios": len(folios), "eligible_bases": len({row["base_id"] for row in selected}),
        "varying_baselines": len({(row["base_id"], row["onset_id"]) for row in selected}),
        "reusable_refinements": len({(row["base_id"], row["onset_id"], row["second_id"]) for row in selected}),
        "second_member_triplets": len({row["second_id"] for row in selected}),
        "consensus_second_rows": sum(row["second_consensus"] == "1" for row in selected),
        "currier_A_rows": sum(row["currier"] == "A" for row in selected),
        "currier_B_rows": sum(row["currier"] == "B" for row in selected),
        "maximum_folio_row_fraction": max(folios.values()) / len(selected),
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
        "maximum_folio_fraction_at_most_010": capacity["maximum_folio_row_fraction"] <= .10,
        "operation_labels_absent": tuple(output[0]) == OUTPUT_FIELDS,
    }
    return output, capacity, gates


def table_bytes(rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    return buffer.getvalue().encode()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures, checks = [], 0
    def check(value, name):
        nonlocal checks
        checks += 1
        if not value: failures.append(name)
    for path, expected in FROZEN.items(): check(sha(path) == expected, "hash:" + path.name)
    with SOURCE.open(encoding="utf-8", newline="") as handle: source = list(csv.DictReader(handle, delimiter="\t"))
    with PANEL.open(encoding="utf-8", newline="") as handle: panel = list(csv.DictReader(handle, delimiter="\t"))
    with QUOTAS.open(encoding="utf-8", newline="") as handle: quotas = list(csv.DictReader(handle, delimiter="\t"))
    rows, capacity, gates = reconstruct(source, panel, quotas)
    check(table_bytes(rows) == PRODUCTION_PANEL.read_bytes(), "panel bytes")
    production = json.loads(PRODUCTION.read_text())
    check(production["capacity"] == capacity, "capacity")
    check(production["gates"] == gates and all(gates.values()), "gates")
    check(production["panel_sha256"] == sha(PRODUCTION_PANEL), "binding")
    check(production["inputs"] == {path.name: sha(path) for path in list(FROZEN)[:6]}, "inputs")
    check(production["status"] == "PASS_TARGET_MASKED_SECOND_MEMBER_INCREMENT_CAPACITY" and production["decision"] == "FREEZE_TARGET_FREE_SECOND_MEMBER_CALIBRATION", "decision")
    check(production["claim_ceiling"] == CLAIM and production["row_operation_labels_stored"] == production["prefix_codes_stored"] == production["complete_member_sequences_stored"] == production["target_scores_computed"] == production["english_glosses"] == 0, "ceiling")
    expected_report = f"""# Second-member incremental opening capacity

Status: **{production['status']}**

After fixing coarse base and exact first onset, the target-label-masked panel
retains **{capacity['eligible_rows']}** second-member rows on
**{capacity['eligible_folios']}** folios and **{capacity['eligible_bases']}**
bases. They span **{capacity['varying_baselines']}** varying baselines,
**{capacity['reusable_refinements']}** reusable exact refinements, and
**{capacity['second_member_triplets']}** second-member triplets;
**{capacity['consensus_second_rows']}/{capacity['eligible_rows']}** rows agree
in all three readings.

Decision: **{production['decision']}**. This is masked capacity only and supplies no longer
dependency, morphology, meaning, plaintext, or translation.
"""
    check(PRODUCTION_REPORT.read_text() == expected_report, "report")
    mutations = {}
    for name, source_case, panel_case in (("missing_source", source[:-1], panel), ("missing_panel", source, panel[:-1]), ("duplicate_panel", source, panel + [panel[0]])):
        try: reconstruct(source_case, panel_case, quotas)
        except ValueError: mutations[name] = True
        else: mutations[name] = False
    wrong = [dict(row) for row in panel]; wrong[0]["onset_id"] = "O" + "0" * 16
    try: reconstruct(source, wrong, quotas)
    except ValueError: mutations["wrong_binding"] = True
    else: mutations["wrong_binding"] = False
    check(all(mutations.values()), "mutations")
    if failures: raise SystemExit("validation failed: " + failures[0])
    result = {"experiment":"SOURCE_NATIVE_OPENING_SECOND_CAPACITY_VALIDATION","status":"PASS_INDEPENDENT_SECOND_MEMBER_CAPACITY_RECONSTRUCTION","checks":checks,"failures":[],"capacity":capacity,"gates":gates,"mutations":mutations,"inputs":{path.name:sha(path) for path in FROZEN},"validator_sha256":sha(VALIDATOR),"row_operation_labels_stored":0,"target_scores_computed":0,"english_glosses":0,"claim_ceiling":CLAIM}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Second-member incremental capacity validation

Status: **{result['status']}**

Independent code reconstructs all 1,207 masked rows, 639 eligible rows, exact
panel bytes, capacity, gates, report, and four mutations in **{checks}** checks.
No operation row label or target score is read or stored.

This validates target-free calibration capacity only and supplies no longer
dependency, morphology, meaning, plaintext, or translation.
""")
    print(json.dumps({"status":result["status"],"checks":checks,"capacity":capacity}, sort_keys=True))


if __name__ == "__main__": main()
