#!/usr/bin/env python3
"""Score-blind capacity audit for STA member resolution beyond family shells."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
SCAFFOLD_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
EDGE = RESULTS / "source_native_edge_grammar.json"
EDGE_VALIDATION = RESULTS / "source_native_edge_grammar_validation.json"
CLOSED = BASE / "CLOSED_ROUTE_FAMILIES.tsv"
SPEC = BASE / "SOURCE_MEMBER_RESOLUTION_CAPACITY_SPEC.md"
SCRIPT = Path(__file__).resolve()
OUT = RESULTS / "source_member_resolution_capacity.json"
REPORT = RESULTS / "source_member_resolution_capacity_report.md"

FROZEN = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SCAFFOLD_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    EDGE: "2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88",
    EDGE_VALIDATION: "0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712",
    CLOSED: "4076d73acb6bde55e67cd1192cc85cfb4545444a6b57da784af15d2fdda0298b",
}
NAMESPACES = ("P1", "P2", "S1", "S2")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError(f"invalid page {page}")
    return match.group(1)


def fine_features(row: dict[str, str]) -> dict[str, tuple[str, ...]]:
    codes = tuple(row["zl_sta_codes"].split())
    if not codes or "".join(code[0] for code in codes) != row["family_surface"]:
        raise ValueError(f"member/family mismatch {row['consensus_group_id']}")
    return {
        "P1": codes[:1],
        "P2": codes[:2],
        "S1": codes[-1:],
        "S2": codes[-2:],
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite capacity artifacts")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    scaffold = json.loads(SCAFFOLD_VALIDATION.read_text(encoding="utf-8"))
    edge = json.loads(EDGE.read_text(encoding="utf-8"))
    edge_validation = json.loads(EDGE_VALIDATION.read_text(encoding="utf-8"))
    if scaffold["status"] != "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION":
        raise SystemExit("scaffold validation is not PASS")
    if edge["decision"] != "CONFIRMED_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR":
        raise SystemExit("family-only edge grammar is not confirmed")
    if edge_validation["status"] != "PASS_INDEPENDENT_SOURCE_NATIVE_EDGE_RECONSTRUCTION":
        raise SystemExit("edge validation is not PASS")
    closed_text = CLOSED.read_text(encoding="utf-8")
    if "MINIMAL_PAIRS_ALLOGRAPHY_AND_SYNONYMS\tCLOSED\t" not in closed_text:
        raise SystemExit("closed-route registry drift")

    with GROUPS.open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        if row["strict_zero_alternative"] == "1":
            grouped[row["locus"]].append(row)

    loci = []
    for locus in sorted(grouped):
        rows = sorted(grouped[locus], key=lambda row: int(row["consensus_group_index"]))
        if len(rows) != int(rows[0]["consensus_group_count"]):
            raise ValueError(f"group-count drift {locus}")
        if len(rows) < 2:
            continue
        endpoints = []
        for role, row in (("FIRST", rows[0]), ("LAST", rows[-1])):
            exact = row["zl_sta_codes"] == row["it_sta_codes"] == row["rf_sta_codes"]
            endpoints.append({
                "role": role,
                "family": row["family_surface"],
                "members": row["zl_sta_codes"],
                "exact": exact,
                "features": fine_features(row) if exact else None,
            })
        loci.append({
            "locus": locus,
            "folio": physical_folio(rows[0]["page"]),
            "endpoints": endpoints,
        })

    family_count = Counter()
    family_held = Counter()
    member_count = Counter()
    member_held = Counter()
    feature_role_count = Counter()
    feature_role_held = Counter()
    shell_members: dict[str, set[str]] = defaultdict(set)
    shell_folios: dict[str, set[str]] = defaultdict(set)
    shell_occurrences = Counter()
    exact_endpoints = 0
    feature_values: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    feature_both_roles: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    feature_roles: dict[tuple[str, tuple[str, ...]], set[str]] = defaultdict(set)
    feature_folios: dict[tuple[str, tuple[str, ...]], set[str]] = defaultdict(set)

    for locus in loci:
        folio = locus["folio"]
        for endpoint in locus["endpoints"]:
            family = endpoint["family"]
            family_count[family] += 1
            family_held[(folio, family)] += 1
            if not endpoint["exact"]:
                continue
            exact_endpoints += 1
            members = endpoint["members"]
            member_count[(family, members)] += 1
            member_held[(folio, family, members)] += 1
            shell_members[family].add(members)
            shell_folios[family].add(folio)
            shell_occurrences[family] += 1
            for namespace, value in endpoint["features"].items():
                role = endpoint["role"]
                feature_role_count[(role, namespace, value)] += 1
                feature_role_held[(folio, role, namespace, value)] += 1
                feature_values[namespace].add(value)
                feature_roles[(namespace, value)].add(role)
                feature_folios[(namespace, value)].add(folio)

    both_exact = []
    family_supported = []
    productive = []
    all_feature_any_role = []
    prospective = []
    for locus in loci:
        folio = locus["folio"]
        endpoints = locus["endpoints"]
        if not all(endpoint["exact"] for endpoint in endpoints):
            continue
        both_exact.append(locus)
        if not all(
            family_count[endpoint["family"]] > family_held[(folio, endpoint["family"])]
            for endpoint in endpoints
        ):
            continue
        family_supported.append(locus)
        if not any(
            member_count[(endpoint["family"], endpoint["members"])]
            == member_held[(folio, endpoint["family"], endpoint["members"])]
            for endpoint in endpoints
        ):
            continue
        productive.append(locus)
        if all(
            sum(feature_role_count[(role, namespace, value)] for role in ("FIRST", "LAST"))
            > sum(feature_role_held[(folio, role, namespace, value)] for role in ("FIRST", "LAST"))
            for endpoint in endpoints
            for namespace, value in endpoint["features"].items()
        ):
            all_feature_any_role.append(locus)
        if all(
            feature_role_count[(role, namespace, value)]
            > feature_role_held[(folio, role, namespace, value)]
            for endpoint in endpoints
            for namespace, value in endpoint["features"].items()
            for role in ("FIRST", "LAST")
        ):
            prospective.append(locus)

    for key, roles in feature_roles.items():
        if roles == {"FIRST", "LAST"}:
            feature_both_roles[key[0]].add(key[1])
    shell_multi_three = {
        family for family in shell_members
        if len(shell_members[family]) >= 2 and len(shell_folios[family]) >= 3
    }
    target_ids = [locus["locus"] for locus in prospective]
    if len(target_ids) != len(set(target_ids)):
        raise ValueError("duplicate prospective target")

    counts = {
        "strict_multi_group_loci": len(loci),
        "endpoint_occurrences": 2 * len(loci),
        "exact_member_endpoint_occurrences": exact_endpoints,
        "both_endpoints_exact_member_loci": len(both_exact),
        "both_endpoints_exact_member_folios": len({locus["folio"] for locus in both_exact}),
        "both_family_surfaces_seen_loci": len(family_supported),
        "both_family_surfaces_seen_folios": len({locus["folio"] for locus in family_supported}),
        "productive_unseen_member_surface_loci": len(productive),
        "productive_unseen_member_surface_folios": len({locus["folio"] for locus in productive}),
        "all_fine_features_seen_any_role_loci": len(all_feature_any_role),
        "all_fine_features_seen_any_role_folios": len({locus["folio"] for locus in all_feature_any_role}),
        "prospective_both_role_supported_loci": len(prospective),
        "prospective_both_role_supported_folios": len({locus["folio"] for locus in prospective}),
        "distinct_exact_family_shells": len(shell_members),
        "multi_member_shells": sum(len(values) >= 2 for values in shell_members.values()),
        "multi_member_shells_at_least_three_folios": len(shell_multi_three),
        "endpoint_occurrences_in_multi_member_three_folio_shells": sum(shell_occurrences[x] for x in shell_multi_three),
    }
    feature_capacity = {}
    for namespace in NAMESPACES:
        values = feature_values[namespace]
        feature_capacity[namespace] = {
            "distinct_values": len(values),
            "values_seen_in_both_roles": len(feature_both_roles[namespace]),
            "both_role_values_on_at_least_three_folios": sum(
                value in feature_both_roles[namespace]
                and len(feature_folios[(namespace, value)]) >= 3
                for value in values
            ),
            "exact_endpoint_occurrences": exact_endpoints,
        }
    gates = {
        "exact_2873_multi_group_loci": counts["strict_multi_group_loci"] == 2873,
        "exact_5746_endpoints": counts["endpoint_occurrences"] == 5746,
        "at_least_2000_both_exact_loci": counts["both_endpoints_exact_member_loci"] >= 2000,
        "at_least_300_productive_loci": counts["productive_unseen_member_surface_loci"] >= 300,
        "at_least_80_productive_folios": counts["productive_unseen_member_surface_folios"] >= 80,
        "at_least_250_both_role_supported_loci": counts["prospective_both_role_supported_loci"] >= 250,
        "at_least_75_both_role_supported_folios": counts["prospective_both_role_supported_folios"] >= 75,
        "at_least_200_multi_member_three_folio_shells": counts["multi_member_shells_at_least_three_folios"] >= 200,
        "unique_prospective_target_ids": len(target_ids) == len(set(target_ids)),
        "target_score_not_computed": True,
        "legacy_formal_fields_not_used": True,
        "english_glosses_zero": True,
    }
    passed = all(gates.values())
    result = {
        "experiment": "SOURCE_MEMBER_RESOLUTION_CAPACITY",
        "status": "PASS_SCORE_BLIND_MEMBER_RESOLUTION_CAPACITY" if passed else "STOP_MEMBER_RESOLUTION_CAPACITY",
        "decision": "GO_PREREGISTER_INCREMENTAL_MEMBER_TEST" if passed else "STOP_BEFORE_MEMBER_SCORE",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, SCRIPT)},
        "novelty_boundary": {
            "old_route": "selected exact-glyph/minimal-pair substitution export",
            "present_route": "manuscript-wide exact-STA-member increment conditional on fixed STA-family shells",
            "reopens_allography_route": False,
        },
        "counts": counts,
        "feature_capacity": feature_capacity,
        "prospective_target_ids_sha256": hashlib.sha256("\n".join(target_ids).encode("utf-8")).hexdigest(),
        "gates": gates,
        "target_score_computed": False,
        "fitted_coefficients_computed": False,
        "english_glosses": 0,
        "claim_ceiling": (
            "Score-blind capacity for a future held-folio test of exact STA member-code resolution "
            "conditional on fixed STA-family shells. This is not evidence that member codes are physical "
            "glyphs, allographs, sounds, morphemes, words, an alphabet, a cipher alphabet, meanings, "
            "plaintext, a language, or a translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Source-native STA member-resolution capacity

Status: **{result['status']}**

This route is not the old f57v/minimal-pair substitution test. It asks whether
fine STA member-code resolution adds structure after the coarse STA family is
held fixed across the whole manuscript.

The strict endpoint panel contains **{counts['both_endpoints_exact_member_loci']:,}** loci with exact
three-reading member codes at both ends. **{counts['productive_unseen_member_surface_loci']:,}** loci on
**{counts['productive_unseen_member_surface_folios']}** physical folios keep both complete family shells
seen outside the fold while making at least one complete member surface unseen.
After requiring every fine P1/P2/S1/S2 value on both endpoints to have outside-
folio examples in both roles, **{counts['prospective_both_role_supported_loci']:,}** loci on
**{counts['prospective_both_role_supported_folios']}** folios remain. There are
**{counts['multi_member_shells_at_least_three_folios']:,}** family shells with multiple exact member
realizations across at least three folios.

Decision: **{result['decision']}**. No target score or coefficient was computed.
The pass authorizes only a separately frozen incremental test. It assigns no
glyph identity, allography, sound, alphabet, word, meaning, plaintext,
language, cipher, or translation.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "decision": result["decision"], "counts": counts}, sort_keys=True))


if __name__ == "__main__":
    main()
