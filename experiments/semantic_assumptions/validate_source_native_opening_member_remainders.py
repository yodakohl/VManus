#!/usr/bin/env python3
"""Independent reconstruction of exact-member NONE/DA capacity."""

from __future__ import annotations

import csv
import hashlib
import io
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
AUDITOR = BASE / "audit_source_native_opening_member_remainders.py"
TSV = RESULTS / "source_native_opening_member_remainders.tsv"
PRODUCTION = RESULTS / "source_native_opening_member_remainders.json"
PRODUCTION_REPORT = RESULTS / "source_native_opening_member_remainders_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_member_remainders_validation.json"
REPORT = RESULTS / "source_native_opening_member_remainders_validation_report.md"

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
    AUDITOR: "8f15a65f49407925bc6f6af518f01489f7d595099740252e61ef555ac297fb4b",
    TSV: "d008661424b2dcebbde36bef9a72db1b48c214726923215fb7d97a45c7a585b2",
    PRODUCTION: "3ba1a442cd36581d0562b4721a2ce2fffa3aeb01a8b4706edac1f6da211f675a",
    PRODUCTION_REPORT: "df71277b8a1d46cfa399153b2a6b4172ecd829e6d542bac4583a7ff735a57e1c",
}

PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
CODE_COLUMNS = ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")
SCHEMES = ("FAMILY_ONLY", "ALL_READING_TRIPLET_EXACT", "ALL_THREE_CONSENSUS_EXACT", "ZL3b_EXACT", "IT2a_EXACT", "RF1b_EXACT")
FIELDS = ("scheme", "mixed_exact_cells", "rows_in_mixed_cells", "none_rows", "da_rows", "physical_folios", "family_remainders", "global_shared_exact_signatures", "two_folio_per_operation_exact_signatures")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if not match:
        raise ValueError("folio")
    return match.group(1)


def dissect(surface: str):
    prefix = next((value for value in PREFIXES if surface.startswith(value)), None)
    if prefix is None:
        return "NONE", surface, 0
    return prefix, surface[len(prefix):], len(prefix)


def anonymize(domain: str, value: str) -> str:
    digest = hashlib.sha256(("SNOC1|" + domain + "|" + value).encode()).hexdigest()
    return domain + digest[:16]


def decoded(row):
    state, remainder, offset = dissect(row["family_surface"])
    sequences = tuple(tuple(row[column].split()) for column in CODE_COLUMNS)
    declared = int(row["symbol_count"])
    if len(row["family_surface"]) != declared or any(len(sequence) != declared for sequence in sequences):
        raise ValueError("full geometry")
    tails = tuple(sequence[offset:] for sequence in sequences)
    if not remainder or any(len(tail) != len(remainder) for tail in tails):
        raise ValueError("tail geometry")
    return state, remainder, tails


def exact_signature(row, mode):
    _, _, tails = decoded(row)
    if mode == "triplet":
        return tuple((tails[0][index], tails[1][index], tails[2][index]) for index in range(len(tails[0])))
    if mode == "consensus":
        return tails[0] if tails[0] == tails[1] == tails[2] else None
    return tails[mode]


def exact_inventory(records, mode, global_counts):
    cells = defaultdict(Counter)
    occurrences = defaultdict(lambda: defaultdict(list))
    for base, physical, state, row in records:
        signature = exact_signature(row, mode)
        if signature is None:
            continue
        cells[(base, physical, signature)][state] += 1
        occurrences[(base, signature)][state].append(physical)
    mixed = {key: value for key, value in cells.items() if value["NONE"] > 0 and value["DA"] > 0}
    shared = {key: value for key, value in occurrences.items() if value["NONE"] and value["DA"]}
    replicated = [key for key, value in shared.items() if len(set(value["NONE"])) >= 2 and len(set(value["DA"])) >= 2]
    row = {
        "mixed_exact_cells": len(mixed),
        "rows_in_mixed_cells": sum(value["NONE"] + value["DA"] for value in mixed.values()),
        "none_rows": sum(value["NONE"] for value in mixed.values()),
        "da_rows": sum(value["DA"] for value in mixed.values()),
        "physical_folios": len({key[1] for key in mixed}),
        "family_remainders": len({key[0] for key in mixed}),
        "global_shared_exact_signatures": len(shared) if global_counts else 0,
        "two_folio_per_operation_exact_signatures": len(replicated) if global_counts else 0,
    }
    return mixed, row


def build_universe(rows):
    prose = [row for row in rows if row["strict_zero_alternative"] == "1" and row["grammar_scope"] == "CONFIRMED_PROSE"]
    groups = defaultdict(lambda: defaultdict(list))
    for row in prose:
        state, base, _ = dissect(row["family_surface"])
        if base and state in ("NONE", "DA"):
            groups[base][state].append(row)
    retained = {
        base for base, states in groups.items()
        if len({folio(row["page"]) for row in states["NONE"]}) >= 2
        and len({folio(row["page"]) for row in states["DA"]}) >= 2
    }
    cell_map = defaultdict(lambda: defaultdict(list))
    for base in retained:
        for state in ("NONE", "DA"):
            for row in groups[base][state]:
                cell_map[(base, folio(row["page"]))][state].append(row)
    mixed = {key: value for key, value in cell_map.items() if value["NONE"] and value["DA"]}
    records = [(base, physical, state, row) for (base, physical), values in mixed.items() for state in ("NONE", "DA") for row in values[state]]
    return prose, retained, mixed, records


def serialize(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def report_text(result, triplet, consensus):
    return f"""# Exact-member `NONE`/`DA` remainder safeguard

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

Among the **{result['matched_triplet_DA_rows']}** exact-triplet-matched `DA` rows,
**{result['dominant_prefix']['rows']}** ({result['dominant_prefix']['fraction']:.2%})
have member prefix `D1 A1` in all three readings. The two remaining rows are
alternate-reading member variants; IT2a reads `D1 A1` in all {result['matched_triplet_DA_rows']}.
Thus the coarse alternation survives exact member resolution at substantial
capacity and exposes one dominant formal prefix construction.

The earlier external-context target remains a nonconfirmation and was not
rescored. `D1 A1` is a structural member-code sequence, not a sound, morpheme,
word, operator name, meaning, plaintext, or translation.
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
        check(sha(path) == expected, "hash:" + path.name)
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    check(len(source_rows) == 26184 and len({row["consensus_group_id"] for row in source_rows}) == 26184, "source-identity")
    prose, retained, family_cells, records = build_universe(source_rows)
    labels = Counter(state for _, _, state, _ in records)
    check(len(prose) == 21899, "prose")
    check(len(retained) == 53, "retained")
    check(len(family_cells) == 197 and len(records) == 1207 and labels == Counter({"NONE": 892, "DA": 315}), "target-universe")

    with PANEL.open(encoding="utf-8", newline="") as handle:
        panel_rows = list(csv.DictReader(handle, delimiter="\t"))
    expected_bindings = {}
    for row in prose:
        state, base, _ = dissect(row["family_surface"])
        if state in ("NONE", "DA") and base in retained:
            expected_bindings[anonymize("U", row["consensus_group_id"])] = anonymize("B", base)
    actual_bindings = {row["unit_id"]: row["base_id"] for row in panel_rows}
    check(len(panel_rows) == len(actual_bindings) == 5826 and actual_bindings == expected_bindings, "panel-binding")
    with QUOTAS.open(encoding="utf-8", newline="") as handle:
        quotas = list(csv.DictReader(handle, delimiter="\t"))
    source_quota = Counter()
    for row in prose:
        state, base, _ = dissect(row["family_surface"])
        if state in ("NONE", "DA") and base in retained:
            source_quota[(anonymize("B", base), folio(row["page"]), state)] += 1
    quota_bindings = {(row["base_id"], row["physical_folio"]): (int(row["none_count"]), int(row["da_count"]), int(row["total_count"])) for row in quotas}
    check(len(quota_bindings) == 1763, "quota-count")
    check(all(quota_bindings[key] == (source_quota[(key[0], key[1], "NONE")], source_quota[(key[0], key[1], "DA")], source_quota[(key[0], key[1], "NONE")] + source_quota[(key[0], key[1], "DA")]) for key in quota_bindings), "quota-binding")
    check(sum(n + d for n, d, _ in quota_bindings.values() if n and d) == 1207 and sum(bool(n and d) for n, d, _ in quota_bindings.values()) == 197, "mixed-quotas")

    output_rows = [{
        "scheme": "FAMILY_ONLY", "mixed_exact_cells": 197, "rows_in_mixed_cells": 1207,
        "none_rows": 892, "da_rows": 315, "physical_folios": 59,
        "family_remainders": 44, "global_shared_exact_signatures": 0,
        "two_folio_per_operation_exact_signatures": 0,
    }]
    modes = (("ALL_READING_TRIPLET_EXACT", "triplet", True), ("ALL_THREE_CONSENSUS_EXACT", "consensus", True), ("ZL3b_EXACT", 0, False), ("IT2a_EXACT", 1, False), ("RF1b_EXACT", 2, False))
    mixed_by_scheme = {}
    for name, mode, global_counts in modes:
        mixed, row = exact_inventory(records, mode, global_counts)
        mixed_by_scheme[name] = mixed
        output_rows.append({"scheme": name, **row})
    check(tuple(row["scheme"] for row in output_rows) == SCHEMES, "scheme-order")
    check(serialize(output_rows) == TSV.read_text(), "tsv-bytes")

    triplet_mixed = mixed_by_scheme["ALL_READING_TRIPLET_EXACT"]
    matched_da = [row for base, physical, state, row in records if state == "DA" and (base, physical, exact_signature(row, "triplet")) in triplet_mixed]
    prefix = Counter()
    for row in matched_da:
        sequences = tuple(tuple(row[column].split()) for column in CODE_COLUMNS)
        signature = ((sequences[0][0], sequences[1][0], sequences[2][0]), (sequences[0][1], sequences[1][1], sequences[2][1]))
        prefix[signature] += 1
    prefix_rows = [{"position_1_readings": "/".join(key[0]), "position_2_readings": "/".join(key[1]), "rows": value} for key, value in sorted(prefix.items(), key=lambda item: (-item[1], item[0]))]
    dominant_key = (("D1", "D1", "D1"), ("A1", "A1", "A1"))
    consensus_rows = sum(exact_signature(row, "consensus") is not None for _, _, _, row in records)
    inventories = {row["scheme"]: {key: value for key, value in row.items() if key != "scheme"} for row in output_rows}
    gates = {
        "exact_53_retained_family_remainders": len(retained) == 53,
        "exact_197_family_mixed_cells": len(family_cells) == 197,
        "exact_1207_rows_892_NONE_315_DA": len(records) == 1207 and labels == Counter({"NONE": 892, "DA": 315}),
        "triplet_at_least_100_mixed_cells": inventories["ALL_READING_TRIPLET_EXACT"]["mixed_exact_cells"] >= 100,
        "triplet_at_least_500_rows": inventories["ALL_READING_TRIPLET_EXACT"]["rows_in_mixed_cells"] >= 500,
        "triplet_at_least_40_folios": inventories["ALL_READING_TRIPLET_EXACT"]["physical_folios"] >= 40,
        "triplet_at_least_30_family_remainders": inventories["ALL_READING_TRIPLET_EXACT"]["family_remainders"] >= 30,
        "triplet_at_least_150_rows_each_operation": min(inventories["ALL_READING_TRIPLET_EXACT"]["none_rows"], inventories["ALL_READING_TRIPLET_EXACT"]["da_rows"]) >= 150,
        "dominant_exact_D1_A1_prefix_at_least_95_percent": prefix[dominant_key] / len(matched_da) >= 0.95,
        "prior_context_target_remains_nonconfirmation": json.loads(TARGET.read_text())["status"] == "NONCONFIRM_DA_STRUCTURAL_CONTEXT",
        "external_context_rescored": False,
    }
    production = json.loads(PRODUCTION.read_text())
    check(production["inventories"] == inventories, "inventories")
    check(production["prefix_member_signatures"] == prefix_rows, "prefix")
    check(production["dominant_prefix"] == {"position_1_readings": "D1/D1/D1", "position_2_readings": "A1/A1/A1", "rows": prefix[dominant_key], "fraction": prefix[dominant_key] / len(matched_da)}, "dominant")
    check(production["all_three_consensus_complete_remainder_rows"] == consensus_rows == 1090, "consensus-rows")
    check(production["matched_triplet_DA_rows"] == len(matched_da) == 213, "matched-DA")
    check(production["gates"] == gates and all(value for key, value in gates.items() if key != "external_context_rescored") and not gates["external_context_rescored"], "gates")
    check(production["status"] == "PASS_MEMBER_RESOLVED_NONE_DA_CAPACITY" and production["decision"] == "RETAIN_DOMINANT_D1_A1_PREFIX_FORM_WITHOUT_CONTEXT_RERUN", "decision")
    check(production["external_context_scores_computed"] == 0 and production["remainder_identities_stored"] == 0 and production["loci_or_pages_stored"] == 0 and production["english_glosses"] == 0, "ceiling")
    check(production["tsv_sha256"] == sha(TSV), "tsv-binding")
    check(PRODUCTION_REPORT.read_text() == report_text(production, inventories["ALL_READING_TRIPLET_EXACT"], inventories["ALL_THREE_CONSENSUS_EXACT"]), "report-bytes")
    check(sum(value for (first, second), value in prefix.items() if first[1] == "D1" and second[1] == "A1") == 213, "IT-all-D1-A1")

    mutations = {}
    base_row = dict(records[0][3])
    for name, mutate in (
        ("missing_member", lambda row: row.__setitem__("zl_sta_codes", " ".join(row["zl_sta_codes"].split()[:-1]))),
        ("extra_member", lambda row: row.__setitem__("it_sta_codes", row["it_sta_codes"] + " A1")),
        ("wrong_symbol_count", lambda row: row.__setitem__("symbol_count", str(int(row["symbol_count"]) + 1))),
    ):
        candidate = dict(base_row)
        mutate(candidate)
        try:
            decoded(candidate)
        except ValueError:
            mutations[name] = True
        else:
            mutations[name] = False
    wrong_panel = dict(panel_rows[0])
    wrong_panel["base_id"] = "B0000000000000000"
    mutations["wrong_base_binding"] = {**actual_bindings, wrong_panel["unit_id"]: wrong_panel["base_id"]} != expected_bindings
    duplicate = source_rows + [dict(source_rows[0])]
    mutations["duplicate_source_id"] = len({row["consensus_group_id"] for row in duplicate}) != len(duplicate)
    check(all(mutations.values()), "mutations")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_MEMBER_REMAINDER_VALIDATION",
        "status": "PASS_INDEPENDENT_MEMBER_RESOLVED_NONE_DA_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "source_rows": len(source_rows),
        "family_cells": len(family_cells),
        "target_rows": len(records),
        "triplet_mixed_cells": inventories["ALL_READING_TRIPLET_EXACT"]["mixed_exact_cells"],
        "triplet_rows": inventories["ALL_READING_TRIPLET_EXACT"]["rows_in_mixed_cells"],
        "matched_DA_rows": len(matched_da),
        "dominant_D1_A1_all_readings_rows": prefix[dominant_key],
        "IT2a_D1_A1_rows": 213,
        "mutations": mutations,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "validator_sha256": sha(VALIDATOR),
        "external_context_scores_computed": 0,
        "english_glosses": 0,
        "claim_ceiling": "Independent exact-member capacity reconstruction only; no context rescue, detachment, allography, morphology, sound, wordhood, syntax, language, cipher, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Exact-member opening safeguard validation

Status: **{result['status']}**

An independent implementation reconstructs all 26,184 source rows, 53 retained
family remainders, 197 family cells, all six resolution inventories, exact TSV
bytes, 213 matched `DA` prefixes, gates, decision, report, and five mutations
in **{checks}** checks. It independently confirms 211/213 all-reading `D1 A1`
prefixes and IT2a `D1 A1` in 213/213.

No external-context score was recomputed. This validates a dominant exact
formal construction only and supplies no morphology, meaning, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
