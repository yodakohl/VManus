#!/usr/bin/env python3
"""Apply the frozen source-native edge score to mirrored internal groups."""

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
EDGE_RESULT = RESULTS / "source_native_edge_grammar.json"
EDGE_VALIDATION = RESULTS / "source_native_edge_grammar_validation.json"
SPEC = BASE / "SOURCE_NATIVE_INTERNAL_ORDER_SPEC.md"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "source_native_internal_order.json"
REPORT = RESULTS / "source_native_internal_order_report.md"

FROZEN = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    EDGE_RESULT: "2a4a246bf1d8de1f2bed76e4e790d44832e9c5ba85cc8d3ad6f2e832b035ea88",
    EDGE_VALIDATION: "0a87ffb2c23fdc6882887e5a854112d678cb6c1de1946407068462ce91fca712",
}
EXPECTED_SCORE_HASH = "c27eaee78ec21c8f392157603c585cb44edaee8ad87d72363b9296cf05894b9f"
FEATURE_SIZES = {"P1": 21, "P2": 462, "S1": 21, "S2": 462, "LEN": 8}
EDGE_REFERENCE = 2.7612409548291317


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def held_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError(f"bad page: {page}")
    return match.group(1)


def feature_vector(surface: str) -> dict[str, str]:
    if not surface:
        raise ValueError("empty surface")
    return {
        "P1": surface[0], "P2": surface[:2],
        "S1": surface[-1], "S2": surface[-2:],
        "LEN": str(len(surface)) if len(surface) <= 7 else "8+",
    }


def load_groups() -> tuple[dict[str, list[dict[str, str]]], list[str]]:
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    alphabet = set()
    for row in rows:
        if row["strict_zero_alternative"] != "1":
            continue
        grouped[row["locus"]].append(row)
        alphabet.update(row["family_surface"])
    for locus, values in grouped.items():
        values.sort(key=lambda row: int(row["consensus_group_index"]))
        declared = int(values[0]["consensus_group_count"])
        if len(values) != declared or [int(row["consensus_group_index"]) for row in values] != list(range(1, declared + 1)):
            raise ValueError(f"group order drift: {locus}")
        for row in values:
            if any(row[field] != values[0][field] for field in ("page", "section", "currier", "hand", "code", "kind", "grammar_scope")):
                raise ValueError(f"metadata drift: {locus}")
    if len(alphabet) != 21:
        raise ValueError("alphabet drift")
    return grouped, sorted(alphabet)


def fit_endpoint_scores(grouped: dict[str, list[dict[str, str]]], alphabet: list[str]) -> tuple[dict[tuple[str, str], tuple[float, float]], str, Counter, Counter]:
    endpoints = []
    endpoint_total = Counter()
    endpoint_held = Counter()
    for values in grouped.values():
        if len(values) < 2:
            continue
        folio = held_folio(values[0]["page"])
        endpoints.append((folio, "FIRST", values[0]["family_surface"]))
        endpoints.append((folio, "LAST", values[-1]["family_surface"]))
        for surface in (values[0]["family_surface"], values[-1]["family_surface"]):
            endpoint_total[surface] += 1
            endpoint_held[(folio, surface)] += 1
    global_cell = Counter()
    held_cell = Counter()
    global_n = Counter()
    held_n = Counter()
    for folio, role, surface in endpoints:
        for namespace, value in feature_vector(surface).items():
            global_cell[(role, namespace, value)] += 1
            held_cell[(folio, role, namespace, value)] += 1
            global_n[(role, namespace)] += 1
            held_n[(folio, role, namespace)] += 1
    folios = sorted({folio for folio, _, _ in endpoints})
    endpoint_surfaces = sorted({surface for _, _, surface in endpoints})
    surfaces = sorted({row["family_surface"] for values in grouped.values() for row in values})
    scores = {}
    for folio in folios:
        for surface in surfaces:
            pieces = {}
            for namespace, value in feature_vector(surface).items():
                role_logs = {}
                for role in ("FIRST", "LAST"):
                    count = global_cell[(role, namespace, value)] - held_cell[(folio, role, namespace, value)]
                    total = global_n[(role, namespace)] - held_n[(folio, role, namespace)]
                    role_logs[role] = math.log((count + 0.5) / (total + 0.5 * FEATURE_SIZES[namespace]))
                pieces[namespace] = role_logs["FIRST"] - role_logs["LAST"]
            comp = sum(pieces.values())
            length = pieces["LEN"]
            if not math.isfinite(comp) or not math.isfinite(length):
                raise ValueError("nonfinite score")
            scores[(folio, surface)] = (comp, length)
    payload = bytearray()
    for folio in folios:
        for surface in endpoint_surfaces:
            comp, length = scores[(folio, surface)]
            payload.extend(folio.encode("ascii") + b"\0" + surface.encode("ascii") + b"\0")
            payload.extend(struct.pack("<dd", comp, length))
    return scores, hashlib.sha256(payload).hexdigest(), endpoint_total, endpoint_held


def build_pairs(grouped, scores, endpoint_total, endpoint_held) -> list[dict[str, object]]:
    pairs = []
    for locus in sorted(grouped):
        values = grouped[locus]
        n = len(values)
        if n < 4:
            continue
        folio = held_folio(values[0]["page"])
        for earlier_index in range(1, n - 1):
            later_index = n - 1 - earlier_index
            if earlier_index >= later_index:
                break
            earlier = values[earlier_index]
            later = values[later_index]
            earlier_score = scores[(folio, earlier["family_surface"])]
            later_score = scores[(folio, later["family_surface"])]
            earlier_unseen = endpoint_total[earlier["family_surface"]] == endpoint_held[(folio, earlier["family_surface"])]
            later_unseen = endpoint_total[later["family_surface"]] == endpoint_held[(folio, later["family_surface"])]
            comp = earlier_score[0] - later_score[0]
            length = earlier_score[1] - later_score[1]
            pairs.append({
                "pair_id": f"{locus}|M{earlier_index + 1:02d}-{later_index + 1:02d}",
                "locus": locus,
                "folio": folio,
                "page": earlier["page"],
                "section": earlier["section"],
                "currier": earlier["currier"],
                "kind": earlier["kind"],
                "grammar_scope": earlier["grammar_scope"],
                "group_count": n,
                "mirror_depth": earlier_index,
                "earlier_group_index": earlier_index + 1,
                "later_group_index": later_index + 1,
                "earlier_surface": earlier["family_surface"],
                "later_surface": later["family_surface"],
                "earlier_unseen_in_endpoint_training": earlier_unseen,
                "later_unseen_in_endpoint_training": later_unseen,
                "members_exact": (
                    earlier["zl_sta_codes"] == earlier["it_sta_codes"] == earlier["rf_sta_codes"]
                    and later["zl_sta_codes"] == later["it_sta_codes"] == later["rf_sta_codes"]
                ),
                "compositional_contrast": comp,
                "length_only_contrast": length,
                "reversed_compositional_contrast": -comp,
            })
    if len(pairs) != 7728:
        raise ValueError(f"pair capacity drift: {len(pairs)}")
    return pairs


def sign_tail(positive: int, negative: int) -> float:
    n = positive + negative
    return sum(math.comb(n, value) for value in range(positive, n + 1)) / 2**n


def summarize(pairs: list[dict[str, object]]) -> dict:
    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in pairs:
        by_locus[str(row["locus"])].append(row)
    locus_details = []
    for locus in sorted(by_locus):
        rows = by_locus[locus]
        locus_details.append({
            "locus": locus,
            "folio": rows[0]["folio"],
            "pairs": len(rows),
            "compositional_contrast": mean(float(row["compositional_contrast"]) for row in rows),
            "length_only_contrast": mean(float(row["length_only_contrast"]) for row in rows),
        })
    by_folio: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in locus_details:
        by_folio[str(row["folio"])].append(row)
    folio_details = []
    for folio in sorted(by_folio):
        rows = by_folio[folio]
        folio_details.append({
            "folio": folio,
            "loci": len(rows),
            "pairs": sum(int(row["pairs"]) for row in rows),
            "compositional_contrast": mean(float(row["compositional_contrast"]) for row in rows),
            "length_only_contrast": mean(float(row["length_only_contrast"]) for row in rows),
        })
    fv = [row["compositional_contrast"] for row in folio_details]
    lv = [row["length_only_contrast"] for row in folio_details]
    pv = [float(row["compositional_contrast"]) for row in pairs]
    positive_folios = sum(value > 0 for value in fv)
    negative_folios = sum(value < 0 for value in fv)
    positive_pairs = sum(value > 0 for value in pv)
    negative_pairs = sum(value < 0 for value in pv)
    loo = [mean(fv[:i] + fv[i + 1:]) for i in range(len(fv))]
    return {
        "pairs": len(pairs),
        "loci": len(locus_details),
        "folios": len(folio_details),
        "equal_folio_compositional_contrast": mean(fv),
        "equal_folio_length_only_contrast": mean(lv),
        "increment_over_length_only": mean(fv) - mean(lv),
        "effect_fraction_of_endpoint_reference": mean(fv) / EDGE_REFERENCE,
        "positive_folios": positive_folios,
        "negative_folios": negative_folios,
        "tied_folios": len(fv) - positive_folios - negative_folios,
        "nonzero_folios": positive_folios + negative_folios,
        "one_sided_folio_sign_p": sign_tail(positive_folios, negative_folios),
        "positive_pairs": positive_pairs,
        "negative_pairs": negative_pairs,
        "tied_pairs": len(pv) - positive_pairs - negative_pairs,
        "nonzero_pair_accuracy": positive_pairs / (positive_pairs + negative_pairs),
        "minimum_leave_one_folio_out_contrast": min(loo),
        "max_absolute_folio_contribution_fraction": max(map(abs, fv)) / sum(map(abs, fv)),
        "folio_details": folio_details,
        "locus_details": locus_details,
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite internal-order result")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    edge = json.loads(EDGE_RESULT.read_text(encoding="utf-8"))
    validation = json.loads(EDGE_VALIDATION.read_text(encoding="utf-8"))
    if edge["decision"] != "CONFIRMED_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR" or not all(edge["target_gates"].values()):
        raise SystemExit("edge result is not confirmed")
    if validation["status"] != "PASS_INDEPENDENT_SOURCE_NATIVE_EDGE_RECONSTRUCTION":
        raise SystemExit("edge validation is not PASS")
    grouped, alphabet = load_groups()
    scores, score_hash, endpoint_total, endpoint_held = fit_endpoint_scores(grouped, alphabet)
    if score_hash != EXPECTED_SCORE_HASH or score_hash != edge["model"]["score_table_sha256"]:
        raise SystemExit("frozen score-table mismatch")
    pairs = build_pairs(grouped, scores, endpoint_total, endpoint_held)
    if any(float(row["reversed_compositional_contrast"]) != -float(row["compositional_contrast"]) for row in pairs):
        raise ValueError("reversal control failed")
    primary = summarize(pairs)
    depth = {str(value): summarize([row for row in pairs if row["mirror_depth"] == value]) for value in (1, 2, 3)}
    robustness = {
        "confirmed_prose": summarize([row for row in pairs if row["grammar_scope"] == "CONFIRMED_PROSE"]),
        "all_three_member_exact": summarize([row for row in pairs if row["members_exact"]]),
        "at_least_one_endpoint_unseen": summarize([row for row in pairs if row["earlier_unseen_in_endpoint_training"] or row["later_unseen_in_endpoint_training"]]),
        "both_endpoints_unseen": summarize([row for row in pairs if row["earlier_unseen_in_endpoint_training"] and row["later_unseen_in_endpoint_training"]]),
        "currier_A": summarize([row for row in pairs if row["currier"] == "A"]),
        "currier_B": summarize([row for row in pairs if row["currier"] == "B"]),
        "group_count_4_to_7": summarize([row for row in pairs if int(row["group_count"]) <= 7]),
        "group_count_8_plus": summarize([row for row in pairs if int(row["group_count"]) >= 8]),
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
        "first_three_mirror_depths_positive": all(row["equal_folio_compositional_contrast"] > 0 for row in depth.values()),
        "confirmed_prose_positive_at_least_90_folios": robustness["confirmed_prose"]["folios"] >= 90 and robustness["confirmed_prose"]["equal_folio_compositional_contrast"] > 0,
        "member_exact_positive_at_least_90_folios": robustness["all_three_member_exact"]["folios"] >= 90 and robustness["all_three_member_exact"]["equal_folio_compositional_contrast"] > 0,
        "one_unseen_positive_at_least_90_folios": robustness["at_least_one_endpoint_unseen"]["folios"] >= 90 and robustness["at_least_one_endpoint_unseen"]["equal_folio_compositional_contrast"] > 0,
        "both_unseen_positive_at_least_50_folios": robustness["both_endpoints_unseen"]["folios"] >= 50 and robustness["both_endpoints_unseen"]["equal_folio_compositional_contrast"] > 0,
        "currier_A_positive_at_least_45_folios": robustness["currier_A"]["folios"] >= 45 and robustness["currier_A"]["equal_folio_compositional_contrast"] > 0,
        "currier_B_positive_at_least_35_folios": robustness["currier_B"]["folios"] >= 35 and robustness["currier_B"]["equal_folio_compositional_contrast"] > 0,
        "short_and_long_loci_positive": all(robustness[key]["equal_folio_compositional_contrast"] > 0 for key in ("group_count_4_to_7", "group_count_8_plus")),
        "all_values_finite": all(
            math.isfinite(value)
            for summary in (primary, *depth.values(), *robustness.values())
            for value in (
                summary["equal_folio_compositional_contrast"], summary["equal_folio_length_only_contrast"],
                summary["one_sided_folio_sign_p"], summary["minimum_leave_one_folio_out_contrast"],
                summary["max_absolute_folio_contribution_fraction"],
            )
        ),
    }
    passed = all(gates.values())
    result = {
        "experiment": "SOURCE_NATIVE_INTERNAL_ORDER",
        "status": "PASS_SOURCE_NATIVE_INTERNAL_ORDER_COORDINATE" if passed else "NONCONFIRM_SOURCE_NATIVE_INTERNAL_ORDER_COORDINATE",
        "decision": "CONFIRMED_SOURCE_NATIVE_INTERNAL_ORDER_COORDINATE" if passed else "NONCONFIRM_SOURCE_NATIVE_INTERNAL_ORDER_COORDINATE",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, RUNNER)},
        "frozen_model": {
            "score_table_sha256": score_hash,
            "endpoint_reference_contrast": EDGE_REFERENCE,
            "features": ["P1", "P2", "S1", "S2", "LEN"],
            "retuned": False,
            "internal_positions_used_in_training": False,
        },
        "primary": primary,
        "mirror_depths": depth,
        "robustness": robustness,
        "gates": gates,
        "english_glosses": 0,
        "claim_ceiling": (
            "At most, the frozen endpoint-family score extends directionally through mirrored internal "
            "synchronized groups as a relative construction-order coordinate. No temporal order, syntax "
            "type, SVO, word, START/STOP meaning, sound, linguistic morpheme, part of speech, lexeme, "
            "plaintext, language, cipher, or translation."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Frozen edge-score transfer to internal locus order

Status: **{result['status']}**

The untouched frozen endpoint score was applied to **{primary['pairs']:,}**
mirrored internal pairs in **{primary['loci']:,}** loci and **{primary['folios']}**
physical folios. The equal-folio earlier-minus-later contrast is
**{primary['equal_folio_compositional_contrast']:.6f}**, or
**{primary['effect_fraction_of_endpoint_reference']:.2%}** of the endpoint
reference. Nonzero pair accuracy is **{primary['nonzero_pair_accuracy']:.3%}**;
**{primary['positive_folios']}/{primary['nonzero_folios']}** folios are positive
with exact sign p **{primary['one_sided_folio_sign_p']:.8g}**.

Decision: **{result['decision']}**. This is a relative source-native
construction-order coordinate, not temporal order, SVO, a word, START/STOP
meaning, sound, part of speech, lexeme, plaintext, language, cipher, or
translation.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "decision": result["decision"], "all_gates": passed}, sort_keys=True))


if __name__ == "__main__":
    main()
