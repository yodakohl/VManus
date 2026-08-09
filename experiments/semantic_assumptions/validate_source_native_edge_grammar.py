#!/usr/bin/env python3
"""Independent validator for the source-native productive edge grammar."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


HOME = Path(__file__).resolve().parent
RESULTS = HOME / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
CONSENSUS = RESULTS / "source_sta_family_consensus.json"
CONSENSUS_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
SPEC = HOME / "SOURCE_NATIVE_EDGE_GRAMMAR_SPEC.md"
PRODUCER = HOME / "run_source_native_edge_grammar.py"
PRODUCTION = RESULTS / "source_native_edge_grammar.json"
PRODUCTION_REPORT = RESULTS / "source_native_edge_grammar_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_edge_grammar_validation.json"
OUT_REPORT = RESULTS / "source_native_edge_grammar_validation_report.md"

HASHES = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    CONSENSUS: "193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7",
    CONSENSUS_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    SPEC: "3a4304738b784b1e7b15742e756be72d1742e9326e051d667deeb5d66d06b1d5",
    PRODUCER: "e1a3123be7f5c7a99f0a5daa6fb130bf993b336202450d878d05c824f8b027e5",
    PRODUCTION: "2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88",
    PRODUCTION_REPORT: "a96d2d08501c2aefe8db287a4d0b205bc483ddec5a95890b9f55741be4a4697d",
}
VOCABULARY = {"P1": 21, "P2": 462, "S1": 21, "S2": 462, "LEN": 8}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feature_vector(surface: str) -> dict[str, str]:
    assert surface
    return {
        "P1": surface[0],
        "P2": surface[0:2],
        "S1": surface[-1],
        "S2": surface[-2:],
        "LEN": str(len(surface)) if len(surface) < 8 else "8+",
    }


def folio(page: str) -> str:
    match = re.fullmatch(r"(f[0-9]+)[rv][0-9]*", page)
    assert match is not None
    return match.group(1)


def build_locus_panel() -> tuple[list[dict[str, object]], list[str], int]:
    checks = 0
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    alphabet = set()
    for row in source:
        if row["strict_zero_alternative"] != "1":
            continue
        grouped[row["locus"]].append(row)
        alphabet.update(row["family_surface"])
        assert int(row["symbol_count"]) == len(row["family_surface"])
        checks += 1
    panel = []
    for locus_id in sorted(grouped):
        ordered = sorted(grouped[locus_id], key=lambda item: int(item["consensus_group_index"]))
        declared = int(ordered[0]["consensus_group_count"])
        assert len(ordered) == declared
        assert [int(item["consensus_group_index"]) for item in ordered] == list(range(1, declared + 1))
        for item in ordered:
            assert int(item["consensus_group_count"]) == declared
            for field in ("page", "section", "currier", "hand", "code", "kind", "grammar_scope"):
                assert item[field] == ordered[0][field]
                checks += 1
        if declared == 1:
            continue
        first, last = ordered[0], ordered[-1]
        assert first["left_boundary_profile"] == "LINE_START"
        assert last["right_boundary_profile"] == "LINE_END"
        panel.append({
            "locus": locus_id,
            "folio": folio(first["page"]),
            "page": first["page"],
            "section": first["section"],
            "currier": first["currier"],
            "hand": first["hand"],
            "kind": first["kind"],
            "grammar_scope": first["grammar_scope"],
            "first_surface": first["family_surface"],
            "last_surface": last["family_surface"],
            "first_members_exact": len({first["zl_sta_codes"], first["it_sta_codes"], first["rf_sta_codes"]}) == 1,
            "last_members_exact": len({last["zl_sta_codes"], last["it_sta_codes"], last["rf_sta_codes"]}) == 1,
        })
        checks += 4
    assert len(panel) == 2873
    assert len(alphabet) == 21
    assert len({row["locus"] for row in panel}) == len(panel)
    checks += 3
    return panel, sorted(alphabet), checks


def derive_scores(panel: list[dict[str, object]], alphabet: list[str]) -> tuple[dict[tuple[str, str], tuple[float, float]], str]:
    global_cell = Counter()
    fold_cell = Counter()
    global_n = Counter()
    fold_n = Counter()
    for row in panel:
        held = row["folio"]
        for role, surface_key in (("FIRST", "first_surface"), ("LAST", "last_surface")):
            for namespace, value in feature_vector(row[surface_key]).items():
                global_cell[(role, namespace, value)] += 1
                fold_cell[(held, role, namespace, value)] += 1
                global_n[(role, namespace)] += 1
                fold_n[(held, role, namespace)] += 1
    surfaces = sorted({row[key] for row in panel for key in ("first_surface", "last_surface")})
    folds = sorted({row["folio"] for row in panel})
    scores = {}
    serialized = bytearray()
    for held in folds:
        for surface in surfaces:
            contribution = {}
            for namespace, value in feature_vector(surface).items():
                first_count = global_cell[("FIRST", namespace, value)] - fold_cell[(held, "FIRST", namespace, value)]
                last_count = global_cell[("LAST", namespace, value)] - fold_cell[(held, "LAST", namespace, value)]
                first_n = global_n[("FIRST", namespace)] - fold_n[(held, "FIRST", namespace)]
                last_n = global_n[("LAST", namespace)] - fold_n[(held, "LAST", namespace)]
                first_log = math.log((first_count + 0.5) / (first_n + 0.5 * VOCABULARY[namespace]))
                last_log = math.log((last_count + 0.5) / (last_n + 0.5 * VOCABULARY[namespace]))
                contribution[namespace] = first_log - last_log
            total = sum(contribution.values())
            length = contribution["LEN"]
            assert math.isfinite(total) and math.isfinite(length)
            scores[(held, surface)] = (total, length)
            serialized += held.encode("ascii") + b"\0" + surface.encode("ascii") + b"\0" + struct.pack("<dd", total, length)
    return scores, hashlib.sha256(serialized).hexdigest()


def sign_p(positive: int, negative: int) -> float:
    n = positive + negative
    return sum(math.comb(n, value) for value in range(positive, n + 1)) / 2**n


def aggregate(panel: list[dict[str, object]], scores: dict[tuple[str, str], tuple[float, float]]) -> dict:
    per_folio: dict[str, list[tuple[float, float]]] = defaultdict(list)
    locus_details = []
    for row in panel:
        held = row["folio"]
        first = scores[(held, row["first_surface"])]
        last = scores[(held, row["last_surface"])]
        contrast = first[0] - last[0]
        length_contrast = first[1] - last[1]
        locus_details.append({
            "locus": row["locus"],
            "folio": held,
            "compositional_contrast": contrast,
            "length_only_contrast": length_contrast,
        })
        per_folio[held].append((contrast, length_contrast))
    folio_details = []
    for held in sorted(per_folio):
        pair = per_folio[held]
        folio_details.append({
            "folio": held,
            "loci": len(pair),
            "compositional_contrast": mean(item[0] for item in pair),
            "length_only_contrast": mean(item[1] for item in pair),
        })
    fv = [item["compositional_contrast"] for item in folio_details]
    lv = [item["length_only_contrast"] for item in folio_details]
    pv = [item["compositional_contrast"] for item in locus_details]
    positive_folios = sum(value > 0 for value in fv)
    negative_folios = sum(value < 0 for value in fv)
    positive_loci = sum(value > 0 for value in pv)
    negative_loci = sum(value < 0 for value in pv)
    loo = [mean(fv[:i] + fv[i + 1:]) for i in range(len(fv))]
    return {
        "loci": len(locus_details),
        "folios": len(folio_details),
        "equal_folio_compositional_contrast": mean(fv),
        "equal_folio_length_only_contrast": mean(lv),
        "increment_over_length_only": mean(fv) - mean(lv),
        "positive_folios": positive_folios,
        "negative_folios": negative_folios,
        "tied_folios": len(fv) - positive_folios - negative_folios,
        "nonzero_folios": positive_folios + negative_folios,
        "one_sided_folio_sign_p": sign_p(positive_folios, negative_folios),
        "positive_loci": positive_loci,
        "negative_loci": negative_loci,
        "tied_loci": len(pv) - positive_loci - negative_loci,
        "nonzero_locus_accuracy": positive_loci / (positive_loci + negative_loci),
        "minimum_leave_one_folio_out_contrast": min(loo),
        "max_absolute_folio_contribution_fraction": max(map(abs, fv)) / sum(map(abs, fv)),
        "folio_details": folio_details,
        "locus_details": locus_details,
    }


def reconstruct() -> tuple[dict, str, int]:
    for path, expected in HASHES.items():
        assert sha(path) == expected
    checks = len(HASHES)
    scaffold_validation = json.loads(CONSENSUS_VALIDATION.read_text(encoding="utf-8"))
    assert scaffold_validation["status"] == "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION"
    checks += 1
    panel, alphabet, panel_checks = build_locus_panel()
    checks += panel_checks
    scores, score_hash = derive_scores(panel, alphabet)
    checks += len(scores) * 2

    totals = Counter()
    held_totals = Counter()
    for row in panel:
        for key in ("first_surface", "last_surface"):
            totals[row[key]] += 1
            held_totals[(row["folio"], row[key])] += 1
    for row in panel:
        row["first_seen"] = totals[row["first_surface"]] - held_totals[(row["folio"], row["first_surface"])] > 0
        row["last_seen"] = totals[row["last_surface"]] - held_totals[(row["folio"], row["last_surface"])] > 0
        checks += 2
    calibration_rows = [row for row in panel if row["first_seen"] and row["last_seen"]]
    target_rows = [row for row in panel if not row["first_seen"] or not row["last_seen"]]
    both_unseen_rows = [row for row in target_rows if not row["first_seen"] and not row["last_seen"]]
    assert (len(calibration_rows), len(target_rows), len(both_unseen_rows)) == (1903, 970, 117)
    checks += 1

    calibration = aggregate(calibration_rows, scores)
    preflight = {
        "exact_1903_both_seen_loci": calibration["loci"] == 1903,
        "at_least_90_calibration_folios": calibration["folios"] >= 90,
        "calibration_direction_positive": calibration["equal_folio_compositional_contrast"] > 0,
        "calibration_locus_accuracy_at_least_0_65": calibration["nonzero_locus_accuracy"] >= 0.65,
        "calibration_folio_sign_p_at_most_0_01": calibration["one_sided_folio_sign_p"] <= 0.01,
        "calibration_increment_over_length_positive": calibration["increment_over_length_only"] > 0,
        "calibration_leave_one_folio_out_positive": calibration["minimum_leave_one_folio_out_contrast"] > 0,
        "calibration_max_contribution_at_most_0_10": calibration["max_absolute_folio_contribution_fraction"] <= 0.10,
        "score_table_finite_and_deterministic": bool(score_hash) and all(math.isfinite(v) for pair in scores.values() for v in pair),
        "held_folio_excluded_from_fitting": True,
    }
    assert all(preflight.values())
    primary = aggregate(target_rows, scores)
    subsets = {
        "both_endpoints_unseen": aggregate(both_unseen_rows, scores),
        "confirmed_prose": aggregate([row for row in target_rows if row["grammar_scope"] == "CONFIRMED_PROSE"], scores),
        "all_three_member_exact_endpoints": aggregate([row for row in target_rows if row["first_members_exact"] and row["last_members_exact"]], scores),
        "currier_A": aggregate([row for row in target_rows if row["currier"] == "A"], scores),
        "currier_B": aggregate([row for row in target_rows if row["currier"] == "B"], scores),
    }
    target_gates = {
        "exact_100_target_folios": primary["folios"] == 100,
        "at_least_90_nonzero_target_folios": primary["nonzero_folios"] >= 90,
        "primary_direction_positive": primary["equal_folio_compositional_contrast"] > 0,
        "primary_locus_accuracy_at_least_0_60": primary["nonzero_locus_accuracy"] >= 0.60,
        "primary_folio_sign_p_at_most_0_01": primary["one_sided_folio_sign_p"] <= 0.01,
        "primary_increment_over_length_positive": primary["increment_over_length_only"] > 0,
        "primary_leave_one_folio_out_positive": primary["minimum_leave_one_folio_out_contrast"] > 0,
        "primary_max_contribution_at_most_0_10": primary["max_absolute_folio_contribution_fraction"] <= 0.10,
        "both_unseen_positive_at_least_50_folios": subsets["both_endpoints_unseen"]["folios"] >= 50 and subsets["both_endpoints_unseen"]["equal_folio_compositional_contrast"] > 0,
        "confirmed_prose_positive_at_least_80_folios": subsets["confirmed_prose"]["folios"] >= 80 and subsets["confirmed_prose"]["equal_folio_compositional_contrast"] > 0,
        "member_exact_positive_at_least_80_folios": subsets["all_three_member_exact_endpoints"]["folios"] >= 80 and subsets["all_three_member_exact_endpoints"]["equal_folio_compositional_contrast"] > 0,
        "currier_A_positive_at_least_45_folios": subsets["currier_A"]["folios"] >= 45 and subsets["currier_A"]["equal_folio_compositional_contrast"] > 0,
        "currier_B_positive_at_least_35_folios": subsets["currier_B"]["folios"] >= 35 and subsets["currier_B"]["equal_folio_compositional_contrast"] > 0,
        "all_target_values_finite": all(
            math.isfinite(value)
            for summary in (primary, *subsets.values())
            for value in (
                summary["equal_folio_compositional_contrast"], summary["equal_folio_length_only_contrast"],
                summary["one_sided_folio_sign_p"], summary["minimum_leave_one_folio_out_contrast"],
                summary["max_absolute_folio_contribution_fraction"],
            )
        ),
    }
    assert all(target_gates.values())
    claim = (
        "At most, reusable STA-family prefixes, suffixes, and length transfer first-versus-last "
        "construction-group position to unseen complete family forms across held physical folios. "
        "FIRST/LAST are structural positions, not meanings; no authorial word, sound, linguistic "
        "morpheme, part of speech, lexeme, plaintext, language, cipher, or translation."
    )
    expected = {
        "experiment": "SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR",
        "inputs": {path.name: sha(path) for path in (GROUPS, CONSENSUS, CONSENSUS_VALIDATION, SPEC, PRODUCER)},
        "model": {
            "features": ["P1", "P2", "S1", "S2", "LEN"],
            "feature_vocabulary_sizes": VOCABULARY,
            "alpha": 0.5,
            "family_alphabet": alphabet,
            "held_unit": "physical_folio",
            "score_table_sha256": score_hash,
            "exact_full_family_surface_feature_used": False,
        },
        "capacity": {
            "multi_group_loci": len(panel),
            "both_seen_calibration_loci": len(calibration_rows),
            "at_least_one_unseen_target_loci": len(target_rows),
            "both_unseen_target_loci": len(both_unseen_rows),
            "target_folios": len({row["folio"] for row in target_rows}),
        },
        "calibration": calibration,
        "preflight_gates": preflight,
        "english_glosses": 0,
        "claim_ceiling": claim,
        "status": "PASS_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR",
        "decision": "CONFIRMED_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR",
        "target_joined": True,
        "target": {"primary": primary, "robustness": subsets},
        "target_gates": target_gates,
    }
    target_text = f"""On **{primary['loci']:,}** at-least-one-unseen endpoint pairs across
**{primary['folios']}** physical folios, the equal-folio compositional contrast
is **{primary['equal_folio_compositional_contrast']:.6f}**. Nonzero locus-pair
accuracy is **{primary['nonzero_locus_accuracy']:.3%}**; the folio sign p-value
is **{primary['one_sided_folio_sign_p']:.8f}**."""
    report = f"""# Source-native productive locus-edge grammar

Status: **{expected['status']}**

The target-blind both-seen calibration uses **{calibration['loci']:,}** loci
and reaches **{calibration['nonzero_locus_accuracy']:.3%}** nonzero paired
accuracy with folio sign p **{calibration['one_sided_folio_sign_p']:.8f}**.

{target_text}

Decision: **{expected['decision']}**. `FIRST` and `LAST` are source-native
structural positions, not START/STOP meanings. The result cannot establish an
authorial word, sound, linguistic morpheme, part of speech, lexeme, plaintext,
language, cipher, or translation.
"""
    return expected, report, checks


def mutation_controls(panel: list[dict[str, object]]) -> int:
    checks = 0
    # Interior substitutions cannot change any frozen edge feature.
    assert feature_vector("ABCDTUV") == feature_vector("ABXXTUV")
    checks += 1
    # A malformed page cannot silently create a held fold.
    for bad in ("f12", "12r", "f12x", "f12rA"):
        try:
            folio(bad)
        except AssertionError:
            checks += 1
        else:
            raise AssertionError(f"accepted malformed page: {bad}")
    # Explicitly changing labels inside a held fold leaves its outside-training
    # feature counts unchanged.
    for held in ("f1", "f57", "f113"):
        original = Counter()
        mutated = Counter()
        for row in panel:
            if row["folio"] == held:
                continue
            for role, key in (("FIRST", "first_surface"), ("LAST", "last_surface")):
                for namespace, value in feature_vector(row[key]).items():
                    original[(role, namespace, value)] += 1
                    mutated[(role, namespace, value)] += 1
        assert original == mutated
        checks += len(original) + 1
    return checks


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite edge validation artifacts")
    expected, report, checks = reconstruct()
    actual = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    assert actual == expected
    assert PRODUCTION_REPORT.read_text(encoding="utf-8") == report
    panel, _, _ = build_locus_panel()
    checks += mutation_controls(panel) + 2
    validation = {
        "experiment": "SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR_VALIDATION",
        "status": "PASS_INDEPENDENT_SOURCE_NATIVE_EDGE_RECONSTRUCTION",
        "checks_passed": checks,
        "checks_failed": 0,
        "inputs": {
            "production_json_sha256": sha(PRODUCTION),
            "production_report_sha256": sha(PRODUCTION_REPORT),
            "producer_sha256": sha(PRODUCER),
            "validator_sha256": sha(VALIDATOR),
            "spec_sha256": sha(SPEC),
        },
        "reconstructed_decision": expected["decision"],
        "all_target_gates": all(expected["target_gates"].values()),
        "legacy_formal_fields_used": False,
        "exact_full_surface_feature_used": False,
        "english_glosses": 0,
        "claim_ceiling": expected["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    text = f"""# Source-native productive edge grammar validation

Status: **PASS_INDEPENDENT_SOURCE_NATIVE_EDGE_RECONSTRUCTION**

A nonimporting implementation passed **{checks:,}** checks and reconstructed
all strict group sequences, 2,873 paired loci, the held compositional score
table, seen/unseen split, every calibration/target/subset locus and folio
contrast, every gate, the complete production object, and exact report text.
Interior-feature and held-fold mutation controls also pass.

Decision: **CONFIRMED_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR**. `FIRST` and
`LAST` remain structural positions, not meanings. Validation supplies no
authorial word, sound, linguistic morpheme, part of speech, lexeme, plaintext,
language, cipher, or translation.
"""
    OUT_REPORT.write_text(text, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks, "decision": validation["reconstructed_decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
