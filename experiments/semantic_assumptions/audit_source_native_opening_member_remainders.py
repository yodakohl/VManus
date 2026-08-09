#!/usr/bin/env python3
"""Resolve NONE/DA natural alternations at exact STA-member level."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
SOURCE_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
CAPACITY = RESULTS / "source_native_opening_operation_capacity.json"
CAPACITY_VALIDATION = RESULTS / "source_native_opening_operation_capacity_validation.json"
PANEL = RESULTS / "source_native_opening_context_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
PANEL_VALIDATION = RESULTS / "source_native_opening_context_capacity_validation.json"
TARGET = RESULTS / "source_native_opening_context_target.json"
TARGET_VALIDATION = RESULTS / "source_native_opening_context_target_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_MEMBER_REMAINDER_AUDIT_SPEC.md"
AUDITOR = Path(__file__).resolve()
OUT_TSV = RESULTS / "source_native_opening_member_remainders.tsv"
OUT_JSON = RESULTS / "source_native_opening_member_remainders.json"
OUT_REPORT = RESULTS / "source_native_opening_member_remainders_report.md"

FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    CAPACITY: "0c1fcac00d1b5934d43acf5e265d79ef876ee08401cfe78695936fccbf903dc7",
    CAPACITY_VALIDATION: "5bf3d6f9d8b5503f2f169ab268cf99edef0858e4d5d409a753c38574fa1755eb",
    PANEL: "6a043ba095d118594c9a8bd4bd4bf0ac96778963be0637400e353c517c5e616a",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    PANEL_VALIDATION: "32dda1eedfa4ea2135583ddaa1593970b279aaab91d3f1fd3c1c75b629dafe53",
    TARGET: "dd66d499a8b4253eb02d8d895aeaa2f13de9fd02617d428cbb5b20c91631c6a3",
    TARGET_VALIDATION: "7f8dcd031c50d7a6dfa43c7caa763790dc4873d947fabd137e6799112e9d9cac",
    SPEC: "777f40c9357ec3d4ccb8547ae27c4ec8e483610e0a2a5b39650fd8736fdd06dd",
}

PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
EDITIONS = ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")
SCHEMES = ("FAMILY_ONLY", "ALL_READING_TRIPLET_EXACT", "ALL_THREE_CONSENSUS_EXACT", "ZL3b_EXACT", "IT2a_EXACT", "RF1b_EXACT")
FIELDS = (
    "scheme", "mixed_exact_cells", "rows_in_mixed_cells", "none_rows", "da_rows",
    "physical_folios", "family_remainders", "global_shared_exact_signatures",
    "two_folio_per_operation_exact_signatures",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError("page")
    return match.group(1)


def operation(surface: str) -> tuple[str, str, int]:
    for prefix in PREFIXES:
        if surface.startswith(prefix):
            return prefix, surface[len(prefix):], len(prefix)
    return "NONE", surface, 0


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def member_sequences(row: dict[str, str], strip: int, remainder: str) -> tuple[tuple[str, ...], ...]:
    complete = tuple(tuple(row[field].split()) for field in EDITIONS)
    if any(len(sequence) != int(row["symbol_count"]) for sequence in complete):
        raise ValueError("member geometry")
    stripped = tuple(sequence[strip:] for sequence in complete)
    if any(len(sequence) != len(remainder) for sequence in stripped):
        raise ValueError("remainder geometry")
    return stripped


def triplet_signature(row: dict[str, str]) -> tuple[tuple[str, str, str], ...]:
    _, remainder, strip = operation(row["family_surface"])
    return tuple(zip(*member_sequences(row, strip, remainder)))


def consensus_signature(row: dict[str, str]):
    _, remainder, strip = operation(row["family_surface"])
    sequences = member_sequences(row, strip, remainder)
    return sequences[0] if sequences[0] == sequences[1] == sequences[2] else None


def edition_signature(row: dict[str, str], edition_index: int) -> tuple[str, ...]:
    _, remainder, strip = operation(row["family_surface"])
    return member_sequences(row, strip, remainder)[edition_index]


def mixed_inventory(records, signature_function, include_global: bool):
    exact_cells = defaultdict(lambda: Counter())
    exact_folios = defaultdict(lambda: defaultdict(list))
    for base, folio, state, row in records:
        signature = signature_function(row)
        if signature is None:
            continue
        exact_cells[(base, folio, signature)][state] += 1
        exact_folios[(base, signature)][state].append(folio)
    mixed = {key: counts for key, counts in exact_cells.items() if counts["NONE"] and counts["DA"]}
    shared = {key: values for key, values in exact_folios.items() if values["NONE"] and values["DA"]}
    replicated = {
        key for key, values in shared.items()
        if len(set(values["NONE"])) >= 2 and len(set(values["DA"])) >= 2
    }
    return {
        "mixed": mixed,
        "row": {
            "mixed_exact_cells": len(mixed),
            "rows_in_mixed_cells": sum(sum(counts.values()) for counts in mixed.values()),
            "none_rows": sum(counts["NONE"] for counts in mixed.values()),
            "da_rows": sum(counts["DA"] for counts in mixed.values()),
            "physical_folios": len({key[1] for key in mixed}),
            "family_remainders": len({key[0] for key in mixed}),
            "global_shared_exact_signatures": len(shared) if include_global else 0,
            "two_folio_per_operation_exact_signatures": len(replicated) if include_global else 0,
        },
    }


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(SOURCE_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION":
        raise ValueError("source validation")
    if json.loads(CAPACITY.read_text())["selected_operation_pair"] != "NONE__DA" or json.loads(CAPACITY_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_10_PAIR_OPENING_CAPACITY_RECONSTRUCTION":
        raise ValueError("operation capacity")
    if json.loads(PANEL_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_5826_ROW_MASKED_CONTEXT_RECONSTRUCTION":
        raise ValueError("panel validation")
    target = json.loads(TARGET.read_text())
    if target["status"] != "NONCONFIRM_DA_STRUCTURAL_CONTEXT" or json.loads(TARGET_VALIDATION.read_text())["status"] != "PASS_PRODUCTION_FREE_DA_CONTEXT_NONCONFIRMATION_RECONSTRUCTION":
        raise ValueError("target state")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(source_rows) != 26184 or len({row["consensus_group_id"] for row in source_rows}) != 26184:
        raise ValueError("source identity")
    prose = [row for row in source_rows if row["strict_zero_alternative"] == "1" and row["grammar_scope"] == "CONFIRMED_PROSE"]
    by_base = defaultdict(lambda: defaultdict(list))
    for row in prose:
        state, base, _ = operation(row["family_surface"])
        if base and state in {"NONE", "DA"}:
            by_base[base][state].append(row)
    retained = {
        base for base, states in by_base.items()
        if len({physical_folio(row["page"]) for row in states["NONE"]}) >= 2
        and len({physical_folio(row["page"]) for row in states["DA"]}) >= 2
    }
    if len(retained) != 53:
        raise ValueError("retained bases")
    cells = defaultdict(lambda: defaultdict(list))
    for base in retained:
        for state in ("NONE", "DA"):
            for row in by_base[base][state]:
                cells[(base, physical_folio(row["page"]))][state].append(row)
    mixed_family = {key: values for key, values in cells.items() if values["NONE"] and values["DA"]}
    records = [
        (base, folio, state, row)
        for (base, folio), values in mixed_family.items()
        for state in ("NONE", "DA")
        for row in values[state]
    ]
    family_counts = Counter(state for _, _, state, _ in records)
    if len(mixed_family) != 197 or len(records) != 1207 or family_counts != Counter({"NONE": 892, "DA": 315}):
        raise ValueError("target universe")
    with PANEL.open(encoding="utf-8", newline="") as handle:
        masked_rows = list(csv.DictReader(handle, delimiter="\t"))
    with QUOTAS.open(encoding="utf-8", newline="") as handle:
        quota_rows = list(csv.DictReader(handle, delimiter="\t"))
    masked_ids = {row["unit_id"] for row in masked_rows}
    expected_ids = {opaque("U", row["consensus_group_id"]) for row in prose if operation(row["family_surface"])[1] in retained and operation(row["family_surface"])[0] in {"NONE", "DA"}}
    if len(masked_rows) != 5826 or masked_ids != expected_ids:
        raise ValueError("masked binding")
    mixed_quota = [row for row in quota_rows if int(row["none_count"]) and int(row["da_count"])]
    if len(mixed_quota) != 197 or sum(int(row["total_count"]) for row in mixed_quota) != 1207:
        raise ValueError("quota binding")

    output_rows = [{
        "scheme": "FAMILY_ONLY",
        "mixed_exact_cells": len(mixed_family),
        "rows_in_mixed_cells": len(records),
        "none_rows": family_counts["NONE"],
        "da_rows": family_counts["DA"],
        "physical_folios": len({folio for _, folio, _, _ in records}),
        "family_remainders": len({base for base, _, _, _ in records}),
        "global_shared_exact_signatures": 0,
        "two_folio_per_operation_exact_signatures": 0,
    }]
    inventories = {}
    inventory_functions = (
        ("ALL_READING_TRIPLET_EXACT", triplet_signature, True),
        ("ALL_THREE_CONSENSUS_EXACT", consensus_signature, True),
        ("ZL3b_EXACT", lambda row: edition_signature(row, 0), False),
        ("IT2a_EXACT", lambda row: edition_signature(row, 1), False),
        ("RF1b_EXACT", lambda row: edition_signature(row, 2), False),
    )
    for scheme, function, include_global in inventory_functions:
        inventory = mixed_inventory(records, function, include_global)
        inventories[scheme] = inventory
        output_rows.append({"scheme": scheme, **inventory["row"]})
    if tuple(row["scheme"] for row in output_rows) != SCHEMES:
        raise ValueError("scheme order")
    triplet_mixed = inventories["ALL_READING_TRIPLET_EXACT"]["mixed"]
    matched_da_rows = [
        row for base, folio, state, row in records
        if state == "DA" and (base, folio, triplet_signature(row)) in triplet_mixed
    ]
    prefix_counts = Counter()
    for row in matched_da_rows:
        complete = tuple(tuple(row[field].split()) for field in EDITIONS)
        if any(len(sequence) < 2 for sequence in complete):
            raise ValueError("DA prefix geometry")
        signature = tuple(zip(*(sequence[:2] for sequence in complete)))
        prefix_counts[signature] += 1
    prefix_rows = [
        {
            "position_1_readings": "/".join(signature[0]),
            "position_2_readings": "/".join(signature[1]),
            "rows": count,
        }
        for signature, count in sorted(prefix_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    consensus_remainder_rows = sum(consensus_signature(row) is not None for _, _, _, row in records)
    gates = {
        "exact_53_retained_family_remainders": len(retained) == 53,
        "exact_197_family_mixed_cells": len(mixed_family) == 197,
        "exact_1207_rows_892_NONE_315_DA": len(records) == 1207 and family_counts == Counter({"NONE": 892, "DA": 315}),
        "triplet_at_least_100_mixed_cells": inventories["ALL_READING_TRIPLET_EXACT"]["row"]["mixed_exact_cells"] >= 100,
        "triplet_at_least_500_rows": inventories["ALL_READING_TRIPLET_EXACT"]["row"]["rows_in_mixed_cells"] >= 500,
        "triplet_at_least_40_folios": inventories["ALL_READING_TRIPLET_EXACT"]["row"]["physical_folios"] >= 40,
        "triplet_at_least_30_family_remainders": inventories["ALL_READING_TRIPLET_EXACT"]["row"]["family_remainders"] >= 30,
        "triplet_at_least_150_rows_each_operation": min(inventories["ALL_READING_TRIPLET_EXACT"]["row"]["none_rows"], inventories["ALL_READING_TRIPLET_EXACT"]["row"]["da_rows"]) >= 150,
        "dominant_exact_D1_A1_prefix_at_least_95_percent": prefix_counts[(("D1", "D1", "D1"), ("A1", "A1", "A1"))] / len(matched_da_rows) >= 0.95,
        "prior_context_target_remains_nonconfirmation": target["status"] == "NONCONFIRM_DA_STRUCTURAL_CONTEXT",
        "external_context_rescored": False,
    }
    passed = all(value for key, value in gates.items() if key != "external_context_rescored") and gates["external_context_rescored"] is False
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    triplet = inventories["ALL_READING_TRIPLET_EXACT"]["row"]
    consensus = inventories["ALL_THREE_CONSENSUS_EXACT"]["row"]
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_MEMBER_REMAINDER_AUDIT",
        "status": "PASS_MEMBER_RESOLVED_NONE_DA_CAPACITY" if passed else "STOP_INSUFFICIENT_MEMBER_RESOLVED_NONE_DA_CAPACITY",
        "decision": "RETAIN_DOMINANT_D1_A1_PREFIX_FORM_WITHOUT_CONTEXT_RERUN" if passed else "RETAIN_FAMILY_LEVEL_OPENING_CHAIN_ONLY",
        "inputs": {path.name: sha(path) for path in (*FROZEN, AUDITOR)},
        "source_rows": len(source_rows),
        "prose_groups": len(prose),
        "retained_family_remainders": len(retained),
        "family_mixed_cells": len(mixed_family),
        "family_target_rows": len(records),
        "all_three_consensus_complete_remainder_rows": consensus_remainder_rows,
        "inventories": {row["scheme"]: {key: value for key, value in row.items() if key != "scheme"} for row in output_rows},
        "matched_triplet_DA_rows": len(matched_da_rows),
        "prefix_member_signatures": prefix_rows,
        "dominant_prefix": {"position_1_readings": "D1/D1/D1", "position_2_readings": "A1/A1/A1", "rows": prefix_counts[(("D1", "D1", "D1"), ("A1", "A1", "A1"))], "fraction": prefix_counts[(("D1", "D1", "D1"), ("A1", "A1", "A1"))] / len(matched_da_rows)},
        "gates": gates,
        "tsv_sha256": sha(OUT_TSV),
        "external_context_scores_computed": 0,
        "remainder_identities_stored": 0,
        "loci_or_pages_stored": 0,
        "english_glosses": 0,
        "claim_ceiling": "Exact-member capacity and dominant formal D1-A1 prefix census only; no external-context rescue, detachment, allography, morphology, sound, wordhood, syntax, language, cipher operation, meaning, plaintext, or translation follows.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    OUT_REPORT.write_text(f"""# Exact-member `NONE`/`DA` remainder safeguard

Status: **{result['status']}**

The original 197 coarse family-remainder/folio cells contain 1,207 rows. After
requiring the same complete ordered `(ZL3b, IT2a, RF1b)` member triple at every
remainder position, **{triplet['mixed_exact_cells']}** cells remain with
**{triplet['rows_in_mixed_cells']}** rows (**{triplet['none_rows']} `NONE` /
{triplet['da_rows']} `DA`) on **{triplet['physical_folios']}** folios and
**{triplet['family_remainders']}** family remainders. The stricter all-three-
consensus inventory retains **{consensus['mixed_exact_cells']}** cells and
**{consensus['rows_in_mixed_cells']}** rows on **{consensus['physical_folios']}**
folios.

Among the **{len(matched_da_rows)}** exact-triplet-matched `DA` rows,
**{result['dominant_prefix']['rows']}** ({result['dominant_prefix']['fraction']:.2%})
have member prefix `D1 A1` in all three readings. The two remaining rows are
alternate-reading member variants; IT2a reads `D1 A1` in all {len(matched_da_rows)}.
Thus the coarse alternation survives exact member resolution at substantial
capacity and exposes one dominant formal prefix construction.

The earlier external-context target remains a nonconfirmation and was not
rescored. `D1 A1` is a structural member-code sequence, not a sound, morpheme,
word, operator name, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "decision": result["decision"], "triplet": triplet, "dominant_prefix": result["dominant_prefix"]}, sort_keys=True))


if __name__ == "__main__":
    main()
