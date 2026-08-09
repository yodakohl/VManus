#!/usr/bin/env python3
"""Independent reconstruction of the STA member-resolution capacity audit."""

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
PRODUCER = BASE / "audit_source_member_resolution_capacity.py"
RESULT = RESULTS / "source_member_resolution_capacity.json"
PRODUCTION_REPORT = RESULTS / "source_member_resolution_capacity_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_member_resolution_capacity_validation.json"
REPORT = RESULTS / "source_member_resolution_capacity_validation_report.md"

FROZEN = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SCAFFOLD_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    EDGE: "2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88",
    EDGE_VALIDATION: "0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712",
    CLOSED: "4076d73acb6bde55e67cd1192cc85cfb4545444a6b57da784af15d2fdda0298b",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def held_folio(page: str) -> str:
    match = re.match(r"^(f\d+)[rv]", page)
    if match is None:
        raise ValueError(page)
    return match.group(1)


def member_views(row: dict[str, str]) -> dict[str, tuple[str, ...]]:
    values = tuple(row["zl_sta_codes"].split())
    return {"P1": values[0:1], "P2": values[0:2], "S1": values[-1:], "S2": values[-2:]}


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite validation artifacts")
    checks = 0

    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    for path, expected in FROZEN.items():
        require(digest(path) == expected, f"hash mismatch {path.name}")
    require(PRODUCER.exists() and SPEC.exists(), "missing producer/spec")
    require(RESULT.exists() and PRODUCTION_REPORT.exists(), "missing production artifacts")
    require("MINIMAL_PAIRS_ALLOGRAPHY_AND_SYNONYMS\tCLOSED\t" in CLOSED.read_text(encoding="utf-8"), "closed route missing")
    require(json.loads(SCAFFOLD_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION", "bad scaffold")
    require(json.loads(EDGE.read_text())["decision"] == "CONFIRMED_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR", "bad edge result")
    require(json.loads(EDGE_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_SOURCE_NATIVE_EDGE_RECONSTRUCTION", "bad edge validation")

    with GROUPS.open(encoding="utf-8", newline="") as handle:
        raw = list(csv.DictReader(handle, delimiter="\t"))
    strict_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    group_ids = set()
    for row in raw:
        require(row["consensus_group_id"] not in group_ids, "duplicate group id")
        group_ids.add(row["consensus_group_id"])
        if row["strict_zero_alternative"] == "1":
            strict_by_locus[row["locus"]].append(row)

    panel = []
    for locus in sorted(strict_by_locus):
        sequence = sorted(strict_by_locus[locus], key=lambda row: int(row["consensus_group_index"]))
        require(len(sequence) == int(sequence[0]["consensus_group_count"]), "group count")
        require([int(row["consensus_group_index"]) for row in sequence] == list(range(1, len(sequence) + 1)), "group order")
        if len(sequence) < 2:
            continue
        endpoints = []
        for role, row in zip(("FIRST", "LAST"), (sequence[0], sequence[-1])):
            codes = tuple(row["zl_sta_codes"].split())
            require(bool(codes), "empty code sequence")
            require("".join(code[0] for code in codes) == row["family_surface"], "code family")
            exact = row["zl_sta_codes"] == row["it_sta_codes"] == row["rf_sta_codes"]
            endpoints.append((role, row["family_surface"], row["zl_sta_codes"], exact, member_views(row) if exact else {}))
        panel.append((locus, held_folio(sequence[0]["page"]), endpoints))

    family_occurrences: dict[str, list[str]] = defaultdict(list)
    member_occurrences: dict[tuple[str, str], list[str]] = defaultdict(list)
    feature_occurrences: dict[tuple[str, str, tuple[str, ...]], list[str]] = defaultdict(list)
    feature_roles: dict[tuple[str, tuple[str, ...]], set[str]] = defaultdict(set)
    feature_folios: dict[tuple[str, tuple[str, ...]], set[str]] = defaultdict(set)
    shell_members: dict[str, set[str]] = defaultdict(set)
    shell_folios: dict[str, set[str]] = defaultdict(set)
    shell_occurrences = Counter()
    exact_endpoint_occurrences = 0
    for _, folio, endpoints in panel:
        for role, family, members, exact, views in endpoints:
            family_occurrences[family].append(folio)
            if not exact:
                continue
            exact_endpoint_occurrences += 1
            member_occurrences[(family, members)].append(folio)
            shell_members[family].add(members)
            shell_folios[family].add(folio)
            shell_occurrences[family] += 1
            for namespace, value in views.items():
                feature_occurrences[(role, namespace, value)].append(folio)
                feature_roles[(namespace, value)].add(role)
                feature_folios[(namespace, value)].add(folio)

    both_exact = []
    family_seen = []
    productive = []
    any_role = []
    prospective = []
    for item in panel:
        _, folio, endpoints = item
        if not all(endpoint[3] for endpoint in endpoints):
            continue
        both_exact.append(item)
        if not all(any(other != folio for other in family_occurrences[endpoint[1]]) for endpoint in endpoints):
            continue
        family_seen.append(item)
        if not any(not any(other != folio for other in member_occurrences[(endpoint[1], endpoint[2])]) for endpoint in endpoints):
            continue
        productive.append(item)
        fine_cells = [
            (namespace, value)
            for endpoint in endpoints
            for namespace, value in endpoint[4].items()
        ]
        if all(
            any(
                other != folio
                for role in ("FIRST", "LAST")
                for other in feature_occurrences[(role, namespace, value)]
            )
            for namespace, value in fine_cells
        ):
            any_role.append(item)
        if all(
            any(other != folio for other in feature_occurrences[(role, namespace, value)])
            for namespace, value in fine_cells
            for role in ("FIRST", "LAST")
        ):
            prospective.append(item)

    multi_three = {
        family for family in shell_members
        if len(shell_members[family]) >= 2 and len(shell_folios[family]) >= 3
    }
    counts = {
        "strict_multi_group_loci": len(panel),
        "endpoint_occurrences": 2 * len(panel),
        "exact_member_endpoint_occurrences": exact_endpoint_occurrences,
        "both_endpoints_exact_member_loci": len(both_exact),
        "both_endpoints_exact_member_folios": len({row[1] for row in both_exact}),
        "both_family_surfaces_seen_loci": len(family_seen),
        "both_family_surfaces_seen_folios": len({row[1] for row in family_seen}),
        "productive_unseen_member_surface_loci": len(productive),
        "productive_unseen_member_surface_folios": len({row[1] for row in productive}),
        "all_fine_features_seen_any_role_loci": len(any_role),
        "all_fine_features_seen_any_role_folios": len({row[1] for row in any_role}),
        "prospective_both_role_supported_loci": len(prospective),
        "prospective_both_role_supported_folios": len({row[1] for row in prospective}),
        "distinct_exact_family_shells": len(shell_members),
        "multi_member_shells": sum(len(values) >= 2 for values in shell_members.values()),
        "multi_member_shells_at_least_three_folios": len(multi_three),
        "endpoint_occurrences_in_multi_member_three_folio_shells": sum(shell_occurrences[x] for x in multi_three),
    }
    feature_capacity = {}
    all_feature_values: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for namespace, value in feature_roles:
        all_feature_values[namespace].add(value)
    for namespace in ("P1", "P2", "S1", "S2"):
        values = all_feature_values[namespace]
        feature_capacity[namespace] = {
            "distinct_values": len(values),
            "values_seen_in_both_roles": sum(feature_roles[(namespace, value)] == {"FIRST", "LAST"} for value in values),
            "both_role_values_on_at_least_three_folios": sum(
                feature_roles[(namespace, value)] == {"FIRST", "LAST"}
                and len(feature_folios[(namespace, value)]) >= 3
                for value in values
            ),
            "exact_endpoint_occurrences": exact_endpoint_occurrences,
        }
    target_ids = [row[0] for row in prospective]
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
    expected = {
        "experiment": "SOURCE_MEMBER_RESOLUTION_CAPACITY",
        "status": "PASS_SCORE_BLIND_MEMBER_RESOLUTION_CAPACITY" if all(gates.values()) else "STOP_MEMBER_RESOLUTION_CAPACITY",
        "decision": "GO_PREREGISTER_INCREMENTAL_MEMBER_TEST" if all(gates.values()) else "STOP_BEFORE_MEMBER_SCORE",
        "inputs": {path.name: digest(path) for path in (*FROZEN, SPEC, PRODUCER)},
        "novelty_boundary": {
            "old_route": "selected exact-glyph/minimal-pair substitution export",
            "present_route": "manuscript-wide exact-STA-member increment conditional on fixed STA-family shells",
            "reopens_allography_route": False,
        },
        "counts": counts,
        "feature_capacity": feature_capacity,
        "prospective_target_ids_sha256": hashlib.sha256("\n".join(target_ids).encode()).hexdigest(),
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
    actual = json.loads(RESULT.read_text(encoding="utf-8"))
    require(actual == expected, "production JSON mismatch")
    expected_bytes = json.dumps(expected, indent=2, sort_keys=True) + "\n"
    require(RESULT.read_text(encoding="utf-8") == expected_bytes, "noncanonical production JSON")
    report_text = f"""# Source-native STA member-resolution capacity

Status: **{expected['status']}**

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

Decision: **{expected['decision']}**. No target score or coefficient was computed.
The pass authorizes only a separately frozen incremental test. It assigns no
glyph identity, allography, sound, alphabet, word, meaning, plaintext,
language, cipher, or translation.
"""
    require(PRODUCTION_REPORT.read_text(encoding="utf-8") == report_text, "production report mismatch")
    require(all(gates.values()), "capacity gates did not all pass")
    require(counts == {
        "strict_multi_group_loci": 2873,
        "endpoint_occurrences": 5746,
        "exact_member_endpoint_occurrences": 4896,
        "both_endpoints_exact_member_loci": 2099,
        "both_endpoints_exact_member_folios": 101,
        "both_family_surfaces_seen_loci": 1418,
        "both_family_surfaces_seen_folios": 100,
        "productive_unseen_member_surface_loci": 426,
        "productive_unseen_member_surface_folios": 94,
        "all_fine_features_seen_any_role_loci": 393,
        "all_fine_features_seen_any_role_folios": 92,
        "prospective_both_role_supported_loci": 285,
        "prospective_both_role_supported_folios": 81,
        "distinct_exact_family_shells": 1402,
        "multi_member_shells": 354,
        "multi_member_shells_at_least_three_folios": 242,
        "endpoint_occurrences_in_multi_member_three_folio_shells": 3360,
    }, "frozen count vector mismatch")
    require(feature_capacity == {
        "P1": {"distinct_values": 24, "values_seen_in_both_roles": 16, "both_role_values_on_at_least_three_folios": 16, "exact_endpoint_occurrences": 4896},
        "P2": {"distinct_values": 202, "values_seen_in_both_roles": 91, "both_role_values_on_at_least_three_folios": 82, "exact_endpoint_occurrences": 4896},
        "S1": {"distinct_values": 28, "values_seen_in_both_roles": 18, "both_role_values_on_at_least_three_folios": 17, "exact_endpoint_occurrences": 4896},
        "S2": {"distinct_values": 155, "values_seen_in_both_roles": 64, "both_role_values_on_at_least_three_folios": 60, "exact_endpoint_occurrences": 4896},
    }, "frozen feature capacity mismatch")

    validation = {
        "experiment": "SOURCE_MEMBER_RESOLUTION_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_SCORE_BLIND_CAPACITY_RECONSTRUCTION",
        "checks": checks,
        "producer_sha256": digest(PRODUCER),
        "result_sha256": digest(RESULT),
        "production_report_sha256": digest(PRODUCTION_REPORT),
        "validator_sha256": digest(VALIDATOR),
        "reconstructed_counts": counts,
        "target_score_reconstructed": False,
        "production_module_imported": False,
        "claim_ceiling": expected["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validation_report = f"""# Source-native STA member-resolution capacity validation

Status: **{validation['status']}**

An independent, nonimporting implementation passed **{checks:,}** checks and
reconstructed the exact 2,873-locus panel, all capacity subsets, frozen count
vector, prospective-target digest, production JSON, and report text.

The validated decision is **{expected['decision']}** with 285 supported loci
on 81 physical folios. No target score or coefficient was reconstructed. This
validates capacity only, not glyph identity, allography, sound, alphabet,
meaning, plaintext, language, cipher, or translation.
"""
    REPORT.write_text(validation_report, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks, "decision": expected["decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
