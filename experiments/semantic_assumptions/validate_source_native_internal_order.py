#!/usr/bin/env python3
"""Clean-room validator for frozen edge-score internal-order transfer."""

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


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
EDGE = RESULTS / "source_native_edge_grammar.json"
EDGE_VALIDATION = RESULTS / "source_native_edge_grammar_validation.json"
SPEC = BASE / "SOURCE_NATIVE_INTERNAL_ORDER_SPEC.md"
PRODUCER = BASE / "run_source_native_internal_order.py"
PRODUCTION = RESULTS / "source_native_internal_order.json"
PRODUCTION_REPORT = RESULTS / "source_native_internal_order_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_internal_order_validation.json"
OUT_REPORT = RESULTS / "source_native_internal_order_validation_report.md"

HASHES = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    EDGE: "2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88",
    EDGE_VALIDATION: "0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712",
    SPEC: "649fb2ccc894db93cb94cc144a35fb44ed16c2392ac47b6cce652efc2a7d1a4a",
    PRODUCER: "3df5c6811bc744d721b5fe3bed258a23eb00710c812a313f2c12ec0991f1f8ba",
    PRODUCTION: "5d0fe0117cf5036af037ae3c7432199e261571dc697649d1f0ec1bca843ed66e",
    PRODUCTION_REPORT: "aec09077535f3f0d01b3036f680ae223e7606365b758b5799aa5c45ae6956a1e",
}
SCORE_HASH = "c27eaee78ec21c8f392157603c585cb44edaee8ad87d72363b9296cf05894b9f"
FEATURE_SPACE = {"P1": 21, "P2": 462, "S1": 21, "S2": 462, "LEN": 8}
REFERENCE = 2.7612409548291317


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fold(page: str) -> str:
    match = re.fullmatch(r"(f[0-9]+)[rv][0-9]*", page)
    assert match is not None
    return match.group(1)


def vector(surface: str) -> dict[str, str]:
    assert surface
    return {
        "P1": surface[0], "P2": surface[:2],
        "S1": surface[-1], "S2": surface[-2:],
        "LEN": str(len(surface)) if len(surface) < 8 else "8+",
    }


def source_groups() -> tuple[dict[str, list[dict[str, str]]], list[str], int]:
    checks = 0
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    grouped = defaultdict(list)
    alphabet = set()
    for row in source:
        if row["strict_zero_alternative"] == "1":
            grouped[row["locus"]].append(row)
            alphabet.update(row["family_surface"])
            assert int(row["symbol_count"]) == len(row["family_surface"])
            checks += 1
    for locus in sorted(grouped):
        rows = sorted(grouped[locus], key=lambda row: int(row["consensus_group_index"]))
        grouped[locus] = rows
        n = int(rows[0]["consensus_group_count"])
        assert len(rows) == n
        assert [int(row["consensus_group_index"]) for row in rows] == list(range(1, n + 1))
        for row in rows:
            for field in ("page", "section", "currier", "hand", "code", "kind", "grammar_scope"):
                assert row[field] == rows[0][field]
                checks += 1
        checks += 2
    assert len(alphabet) == 21
    checks += 1
    return dict(grouped), sorted(alphabet), checks


def endpoint_model(grouped, alphabet) -> tuple[dict[tuple[str, str], tuple[float, float]], str, Counter, Counter]:
    endpoint_rows = []
    total_surface = Counter()
    fold_surface = Counter()
    for rows in grouped.values():
        if len(rows) < 2:
            continue
        held = fold(rows[0]["page"])
        for role, row in (("FIRST", rows[0]), ("LAST", rows[-1])):
            surface = row["family_surface"]
            endpoint_rows.append((held, role, surface))
            total_surface[surface] += 1
            fold_surface[(held, surface)] += 1
    cell = Counter()
    held_cell = Counter()
    total = Counter()
    held_total = Counter()
    for held, role, surface in endpoint_rows:
        for namespace, value in vector(surface).items():
            cell[(role, namespace, value)] += 1
            held_cell[(held, role, namespace, value)] += 1
            total[(role, namespace)] += 1
            held_total[(held, role, namespace)] += 1
    folds = sorted({held for held, _, _ in endpoint_rows})
    endpoint_surfaces = sorted({surface for _, _, surface in endpoint_rows})
    all_surfaces = sorted({row["family_surface"] for rows in grouped.values() for row in rows})
    scores = {}
    for held in folds:
        for surface in all_surfaces:
            components = {}
            for namespace, value in vector(surface).items():
                logs = {}
                for role in ("FIRST", "LAST"):
                    count = cell[(role, namespace, value)] - held_cell[(held, role, namespace, value)]
                    n = total[(role, namespace)] - held_total[(held, role, namespace)]
                    logs[role] = math.log((count + 0.5) / (n + 0.5 * FEATURE_SPACE[namespace]))
                components[namespace] = logs["FIRST"] - logs["LAST"]
            scores[(held, surface)] = (sum(components.values()), components["LEN"])
    payload = bytearray()
    for held in folds:
        for surface in endpoint_surfaces:
            comp, length = scores[(held, surface)]
            payload += held.encode("ascii") + b"\0" + surface.encode("ascii") + b"\0" + struct.pack("<dd", comp, length)
    return scores, hashlib.sha256(payload).hexdigest(), total_surface, fold_surface


def internal_pairs(grouped, scores, surface_total, surface_fold) -> list[dict[str, object]]:
    result = []
    for locus in sorted(grouped):
        rows = grouped[locus]
        n = len(rows)
        if n < 4:
            continue
        held = fold(rows[0]["page"])
        for left_index in range(1, n - 1):
            right_index = n - 1 - left_index
            if left_index >= right_index:
                break
            left, right = rows[left_index], rows[right_index]
            left_score = scores[(held, left["family_surface"])]
            right_score = scores[(held, right["family_surface"])]
            comp = left_score[0] - right_score[0]
            length = left_score[1] - right_score[1]
            result.append({
                "pair_id": f"{locus}|M{left_index + 1:02d}-{right_index + 1:02d}",
                "locus": locus,
                "folio": held,
                "page": left["page"],
                "section": left["section"],
                "currier": left["currier"],
                "kind": left["kind"],
                "grammar_scope": left["grammar_scope"],
                "group_count": n,
                "mirror_depth": left_index,
                "earlier_group_index": left_index + 1,
                "later_group_index": right_index + 1,
                "earlier_surface": left["family_surface"],
                "later_surface": right["family_surface"],
                "earlier_unseen_in_endpoint_training": surface_total[left["family_surface"]] == surface_fold[(held, left["family_surface"])],
                "later_unseen_in_endpoint_training": surface_total[right["family_surface"]] == surface_fold[(held, right["family_surface"])],
                "members_exact": (
                    len({left["zl_sta_codes"], left["it_sta_codes"], left["rf_sta_codes"]}) == 1
                    and len({right["zl_sta_codes"], right["it_sta_codes"], right["rf_sta_codes"]}) == 1
                ),
                "compositional_contrast": comp,
                "length_only_contrast": length,
                "reversed_compositional_contrast": -comp,
            })
    assert len(result) == 7728
    return result


def tail(positive: int, negative: int) -> float:
    n = positive + negative
    return sum(math.comb(n, k) for k in range(positive, n + 1)) / 2**n


def summary(pairs: list[dict[str, object]]) -> dict:
    locus_rows = defaultdict(list)
    for row in pairs:
        locus_rows[row["locus"]].append(row)
    locus_details = []
    for locus in sorted(locus_rows):
        rows = locus_rows[locus]
        locus_details.append({
            "locus": locus,
            "folio": rows[0]["folio"],
            "pairs": len(rows),
            "compositional_contrast": mean(row["compositional_contrast"] for row in rows),
            "length_only_contrast": mean(row["length_only_contrast"] for row in rows),
        })
    folio_rows = defaultdict(list)
    for row in locus_details:
        folio_rows[row["folio"]].append(row)
    folio_details = []
    for held in sorted(folio_rows):
        rows = folio_rows[held]
        folio_details.append({
            "folio": held,
            "loci": len(rows),
            "pairs": sum(row["pairs"] for row in rows),
            "compositional_contrast": mean(row["compositional_contrast"] for row in rows),
            "length_only_contrast": mean(row["length_only_contrast"] for row in rows),
        })
    fv = [row["compositional_contrast"] for row in folio_details]
    lv = [row["length_only_contrast"] for row in folio_details]
    pv = [row["compositional_contrast"] for row in pairs]
    posf = sum(value > 0 for value in fv)
    negf = sum(value < 0 for value in fv)
    posp = sum(value > 0 for value in pv)
    negp = sum(value < 0 for value in pv)
    loo = [mean(fv[:i] + fv[i + 1:]) for i in range(len(fv))]
    return {
        "pairs": len(pairs), "loci": len(locus_details), "folios": len(folio_details),
        "equal_folio_compositional_contrast": mean(fv),
        "equal_folio_length_only_contrast": mean(lv),
        "increment_over_length_only": mean(fv) - mean(lv),
        "effect_fraction_of_endpoint_reference": mean(fv) / REFERENCE,
        "positive_folios": posf, "negative_folios": negf,
        "tied_folios": len(fv) - posf - negf, "nonzero_folios": posf + negf,
        "one_sided_folio_sign_p": tail(posf, negf),
        "positive_pairs": posp, "negative_pairs": negp,
        "tied_pairs": len(pv) - posp - negp,
        "nonzero_pair_accuracy": posp / (posp + negp),
        "minimum_leave_one_folio_out_contrast": min(loo),
        "max_absolute_folio_contribution_fraction": max(map(abs, fv)) / sum(map(abs, fv)),
        "folio_details": folio_details, "locus_details": locus_details,
    }


def reconstruct() -> tuple[dict, str, int]:
    for path, expected in HASHES.items():
        assert sha(path) == expected
    checks = len(HASHES)
    edge = json.loads(EDGE.read_text(encoding="utf-8"))
    edge_validation = json.loads(EDGE_VALIDATION.read_text(encoding="utf-8"))
    assert edge["decision"] == "CONFIRMED_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR"
    assert all(edge["target_gates"].values())
    assert edge_validation["status"] == "PASS_INDEPENDENT_SOURCE_NATIVE_EDGE_RECONSTRUCTION"
    checks += 3
    grouped, alphabet, source_checks = source_groups()
    checks += source_checks
    scores, score_hash, surface_total, surface_fold = endpoint_model(grouped, alphabet)
    assert score_hash == SCORE_HASH == edge["model"]["score_table_sha256"]
    checks += len(scores) + 1
    pairs = internal_pairs(grouped, scores, surface_total, surface_fold)
    assert all(row["reversed_compositional_contrast"] == -row["compositional_contrast"] for row in pairs)
    checks += len(pairs) * 2
    primary = summary(pairs)
    depths = {str(depth): summary([row for row in pairs if row["mirror_depth"] == depth]) for depth in (1, 2, 3)}
    robustness = {
        "confirmed_prose": summary([row for row in pairs if row["grammar_scope"] == "CONFIRMED_PROSE"]),
        "all_three_member_exact": summary([row for row in pairs if row["members_exact"]]),
        "at_least_one_endpoint_unseen": summary([row for row in pairs if row["earlier_unseen_in_endpoint_training"] or row["later_unseen_in_endpoint_training"]]),
        "both_endpoints_unseen": summary([row for row in pairs if row["earlier_unseen_in_endpoint_training"] and row["later_unseen_in_endpoint_training"]]),
        "currier_A": summary([row for row in pairs if row["currier"] == "A"]),
        "currier_B": summary([row for row in pairs if row["currier"] == "B"]),
        "group_count_4_to_7": summary([row for row in pairs if row["group_count"] <= 7]),
        "group_count_8_plus": summary([row for row in pairs if row["group_count"] >= 8]),
    }
    gates = {
        "exact_7728_pairs_2579_loci_102_folios": (primary["pairs"], primary["loci"], primary["folios"]) == (7728, 2579, 102),
        "primary_direction_positive": primary["equal_folio_compositional_contrast"] > 0,
        "effect_at_least_0_05_endpoint_reference": primary["effect_fraction_of_endpoint_reference"] >= 0.05,
        "pair_accuracy_at_least_0_55": primary["nonzero_pair_accuracy"] >= 0.55,
        "at_least_90_nonzero_folios": primary["nonzero_folios"] >= 90,
        "folio_sign_p_at_most_0_01": primary["one_sided_folio_sign_p"] <= 0.01,
        "leave_one_folio_out_positive": primary["minimum_leave_one_folio_out_contrast"] > 0,
        "max_contribution_at_most_0_10": primary["max_absolute_folio_contribution_fraction"] <= 0.10,
        "increment_over_length_positive": primary["increment_over_length_only"] > 0,
        "pair_reversal_exact": True,
        "first_three_mirror_depths_positive": all(row["equal_folio_compositional_contrast"] > 0 for row in depths.values()),
        "confirmed_prose_positive_at_least_90_folios": robustness["confirmed_prose"]["folios"] >= 90 and robustness["confirmed_prose"]["equal_folio_compositional_contrast"] > 0,
        "member_exact_positive_at_least_90_folios": robustness["all_three_member_exact"]["folios"] >= 90 and robustness["all_three_member_exact"]["equal_folio_compositional_contrast"] > 0,
        "one_unseen_positive_at_least_90_folios": robustness["at_least_one_endpoint_unseen"]["folios"] >= 90 and robustness["at_least_one_endpoint_unseen"]["equal_folio_compositional_contrast"] > 0,
        "both_unseen_positive_at_least_50_folios": robustness["both_endpoints_unseen"]["folios"] >= 50 and robustness["both_endpoints_unseen"]["equal_folio_compositional_contrast"] > 0,
        "currier_A_positive_at_least_45_folios": robustness["currier_A"]["folios"] >= 45 and robustness["currier_A"]["equal_folio_compositional_contrast"] > 0,
        "currier_B_positive_at_least_35_folios": robustness["currier_B"]["folios"] >= 35 and robustness["currier_B"]["equal_folio_compositional_contrast"] > 0,
        "short_and_long_loci_positive": all(robustness[key]["equal_folio_compositional_contrast"] > 0 for key in ("group_count_4_to_7", "group_count_8_plus")),
        "all_values_finite": all(
            math.isfinite(value)
            for item in (primary, *depths.values(), *robustness.values())
            for value in (
                item["equal_folio_compositional_contrast"], item["equal_folio_length_only_contrast"],
                item["one_sided_folio_sign_p"], item["minimum_leave_one_folio_out_contrast"],
                item["max_absolute_folio_contribution_fraction"],
            )
        ),
    }
    assert [key for key, value in gates.items() if not value] == [
        "effect_at_least_0_05_endpoint_reference", "pair_accuracy_at_least_0_55", "folio_sign_p_at_most_0_01"
    ]
    claim = (
        "At most, the frozen endpoint-family score extends directionally through mirrored internal "
        "synchronized groups as a relative construction-order coordinate. No temporal order, syntax "
        "type, SVO, word, START/STOP meaning, sound, linguistic morpheme, part of speech, lexeme, "
        "plaintext, language, cipher, or translation."
    )
    expected = {
        "experiment": "SOURCE_NATIVE_INTERNAL_ORDER",
        "status": "NONCONFIRM_SOURCE_NATIVE_INTERNAL_ORDER_COORDINATE",
        "decision": "NONCONFIRM_SOURCE_NATIVE_INTERNAL_ORDER_COORDINATE",
        "inputs": {path.name: sha(path) for path in (GROUPS, EDGE, EDGE_VALIDATION, SPEC, PRODUCER)},
        "frozen_model": {
            "score_table_sha256": score_hash,
            "endpoint_reference_contrast": REFERENCE,
            "features": ["P1", "P2", "S1", "S2", "LEN"],
            "retuned": False,
            "internal_positions_used_in_training": False,
        },
        "primary": primary, "mirror_depths": depths, "robustness": robustness,
        "gates": gates, "english_glosses": 0, "claim_ceiling": claim,
    }
    report = f"""# Frozen edge-score transfer to internal locus order

Status: **{expected['status']}**

The untouched frozen endpoint score was applied to **{primary['pairs']:,}**
mirrored internal pairs in **{primary['loci']:,}** loci and **{primary['folios']}**
physical folios. The equal-folio earlier-minus-later contrast is
**{primary['equal_folio_compositional_contrast']:.6f}**, or
**{primary['effect_fraction_of_endpoint_reference']:.2%}** of the endpoint
reference. Nonzero pair accuracy is **{primary['nonzero_pair_accuracy']:.3%}**;
**{primary['positive_folios']}/{primary['nonzero_folios']}** folios are positive
with exact sign p **{primary['one_sided_folio_sign_p']:.8g}**.

Decision: **{expected['decision']}**. This is a relative source-native
construction-order coordinate, not temporal order, SVO, a word, START/STOP
meaning, sound, part of speech, lexeme, plaintext, language, cipher, or
translation.
"""
    return expected, report, checks


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite internal-order validation")
    expected, report, checks = reconstruct()
    assert json.loads(PRODUCTION.read_text(encoding="utf-8")) == expected
    assert PRODUCTION_REPORT.read_text(encoding="utf-8") == report
    checks += 2
    validation = {
        "experiment": "SOURCE_NATIVE_INTERNAL_ORDER_VALIDATION",
        "status": "PASS_INDEPENDENT_INTERNAL_ORDER_NONCONFIRM_RECONSTRUCTION",
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
        "failed_gates": sorted(key for key, value in expected["gates"].items() if not value),
        "score_table_sha256": expected["frozen_model"]["score_table_sha256"],
        "model_retuned": False,
        "internal_positions_used_in_training": False,
        "english_glosses": 0,
        "claim_ceiling": expected["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    text = f"""# Frozen edge-score internal-order validation

Status: **PASS_INDEPENDENT_INTERNAL_ORDER_NONCONFIRM_RECONSTRUCTION**

A nonimporting implementation passed **{checks:,}** checks and reconstructs the
strict group sequences, untouched frozen endpoint score, 7,728 mirrored pairs,
hierarchical locus/folio summaries, depth and robustness panels, failed gates,
complete production object, and exact report text.

The registered decision remains
**NONCONFIRM_SOURCE_NATIVE_INTERNAL_ORDER_COORDINATE**. The confirmed endpoint
grammar does not establish a material smooth internal coordinate. No temporal
order, SVO, word, START/STOP meaning, sound, part of speech, lexeme, plaintext,
language, cipher, or translation follows.
"""
    OUT_REPORT.write_text(text, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks, "decision": validation["reconstructed_decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
