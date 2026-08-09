#!/usr/bin/env python3
"""Run the frozen source-native productive locus-edge grammar test."""

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
CONSENSUS = RESULTS / "source_sta_family_consensus.json"
CONSENSUS_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
SPEC = BASE / "SOURCE_NATIVE_EDGE_GRAMMAR_SPEC.md"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "source_native_edge_grammar.json"
REPORT = RESULTS / "source_native_edge_grammar_report.md"

FROZEN = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    CONSENSUS: "193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7",
    CONSENSUS_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
}
ALPHA = 0.5
FEATURE_SIZES = {"P1": 21, "P2": 462, "S1": 21, "S2": 462, "LEN": 8}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError(f"invalid page: {page}")
    return match.group(1)


def features(surface: str) -> dict[str, str]:
    if not surface:
        raise ValueError("empty family surface")
    return {
        "P1": surface[0],
        "P2": surface[:2],
        "S1": surface[-1],
        "S2": surface[-2:],
        "LEN": str(len(surface)) if len(surface) <= 7 else "8+",
    }


def load_loci() -> tuple[list[dict[str, object]], list[str]]:
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    strict = [row for row in rows if row["strict_zero_alternative"] == "1"]
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in strict:
        by_locus[row["locus"]].append(row)
    loci = []
    alphabet = set()
    for locus_id in sorted(by_locus):
        group_rows = sorted(by_locus[locus_id], key=lambda row: int(row["consensus_group_index"]))
        expected_count = int(group_rows[0]["consensus_group_count"])
        if len(group_rows) != expected_count or [int(row["consensus_group_index"]) for row in group_rows] != list(range(1, expected_count + 1)):
            raise ValueError(f"group sequence drift: {locus_id}")
        for row in group_rows:
            for field in ("page", "section", "currier", "hand", "code", "kind", "grammar_scope"):
                if row[field] != group_rows[0][field]:
                    raise ValueError(f"metadata drift: {locus_id}: {field}")
            alphabet.update(row["family_surface"])
        if expected_count < 2:
            continue
        first = group_rows[0]
        last = group_rows[-1]
        loci.append({
            "locus": locus_id,
            "folio": physical_folio(first["page"]),
            "page": first["page"],
            "section": first["section"],
            "currier": first["currier"],
            "hand": first["hand"],
            "kind": first["kind"],
            "grammar_scope": first["grammar_scope"],
            "first_surface": first["family_surface"],
            "last_surface": last["family_surface"],
            "first_members_exact": first["zl_sta_codes"] == first["it_sta_codes"] == first["rf_sta_codes"],
            "last_members_exact": last["zl_sta_codes"] == last["it_sta_codes"] == last["rf_sta_codes"],
        })
    if len(loci) != 2873 or len(alphabet) != 21:
        raise ValueError("edge panel count drift")
    return loci, sorted(alphabet)


def feature_score_tables(loci: list[dict[str, object]], alphabet: list[str]) -> tuple[dict[tuple[str, str], tuple[float, float]], str]:
    folios = sorted({str(row["folio"]) for row in loci})
    surfaces = sorted({str(row[key]) for row in loci for key in ("first_surface", "last_surface")})
    global_counts = Counter()
    held_counts = Counter()
    global_totals = Counter()
    held_totals = Counter()
    for row in loci:
        folio = str(row["folio"])
        for role, key in (("FIRST", "first_surface"), ("LAST", "last_surface")):
            vector = features(str(row[key]))
            for namespace, value in vector.items():
                global_counts[(role, namespace, value)] += 1
                held_counts[(folio, role, namespace, value)] += 1
                global_totals[(role, namespace)] += 1
                held_totals[(folio, role, namespace)] += 1
    table = {}
    payload = bytearray()
    for folio in folios:
        for surface in surfaces:
            vector = features(surface)
            components = {}
            for namespace, value in vector.items():
                logs = {}
                for role in ("FIRST", "LAST"):
                    count = global_counts[(role, namespace, value)] - held_counts[(folio, role, namespace, value)]
                    total = global_totals[(role, namespace)] - held_totals[(folio, role, namespace)]
                    logs[role] = math.log((count + ALPHA) / (total + ALPHA * FEATURE_SIZES[namespace]))
                components[namespace] = logs["FIRST"] - logs["LAST"]
            compositional = sum(components.values())
            length_only = components["LEN"]
            if not math.isfinite(compositional) or not math.isfinite(length_only):
                raise ValueError("nonfinite edge score")
            table[(folio, surface)] = (compositional, length_only)
            payload.extend(folio.encode("ascii") + b"\0" + surface.encode("ascii") + b"\0")
            payload.extend(struct.pack("<dd", compositional, length_only))
    return table, hashlib.sha256(payload).hexdigest()


def binomial_tail(positive: int, negative: int) -> float:
    n = positive + negative
    return sum(math.comb(n, k) for k in range(positive, n + 1)) / 2**n


def summarize(loci: list[dict[str, object]], score: dict[tuple[str, str], tuple[float, float]]) -> dict:
    locus_details = []
    by_folio: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in loci:
        folio = str(row["folio"])
        first = score[(folio, str(row["first_surface"]))]
        last = score[(folio, str(row["last_surface"]))]
        compositional = first[0] - last[0]
        length_only = first[1] - last[1]
        locus_details.append({
            "locus": row["locus"],
            "folio": folio,
            "compositional_contrast": compositional,
            "length_only_contrast": length_only,
        })
        by_folio[folio].append((compositional, length_only))
    folio_details = []
    for folio in sorted(by_folio):
        values = by_folio[folio]
        folio_details.append({
            "folio": folio,
            "loci": len(values),
            "compositional_contrast": mean(value[0] for value in values),
            "length_only_contrast": mean(value[1] for value in values),
        })
    folio_values = [row["compositional_contrast"] for row in folio_details]
    length_values = [row["length_only_contrast"] for row in folio_details]
    locus_values = [row["compositional_contrast"] for row in locus_details]
    positive_folios = sum(value > 0 for value in folio_values)
    negative_folios = sum(value < 0 for value in folio_values)
    positive_loci = sum(value > 0 for value in locus_values)
    negative_loci = sum(value < 0 for value in locus_values)
    leave_one = [mean(folio_values[:index] + folio_values[index + 1:]) for index in range(len(folio_values))]
    return {
        "loci": len(locus_details),
        "folios": len(folio_details),
        "equal_folio_compositional_contrast": mean(folio_values),
        "equal_folio_length_only_contrast": mean(length_values),
        "increment_over_length_only": mean(folio_values) - mean(length_values),
        "positive_folios": positive_folios,
        "negative_folios": negative_folios,
        "tied_folios": len(folio_values) - positive_folios - negative_folios,
        "nonzero_folios": positive_folios + negative_folios,
        "one_sided_folio_sign_p": binomial_tail(positive_folios, negative_folios),
        "positive_loci": positive_loci,
        "negative_loci": negative_loci,
        "tied_loci": len(locus_values) - positive_loci - negative_loci,
        "nonzero_locus_accuracy": positive_loci / (positive_loci + negative_loci),
        "minimum_leave_one_folio_out_contrast": min(leave_one),
        "max_absolute_folio_contribution_fraction": max(map(abs, folio_values)) / sum(map(abs, folio_values)),
        "folio_details": folio_details,
        "locus_details": locus_details,
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite edge-grammar result")
    for path, expected in FROZEN.items():
        if digest(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    validation = json.loads(CONSENSUS_VALIDATION.read_text(encoding="utf-8"))
    if validation["status"] != "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION":
        raise SystemExit("source scaffold validation is not PASS")
    loci, alphabet = load_loci()
    scores, score_hash = feature_score_tables(loci, alphabet)

    endpoint_occurrences = Counter()
    held_endpoint_occurrences = Counter()
    for row in loci:
        for key in ("first_surface", "last_surface"):
            surface = str(row[key])
            endpoint_occurrences[surface] += 1
            held_endpoint_occurrences[(str(row["folio"]), surface)] += 1
    for row in loci:
        folio = str(row["folio"])
        row["first_seen"] = endpoint_occurrences[str(row["first_surface"])] > held_endpoint_occurrences[(folio, str(row["first_surface"]))]
        row["last_seen"] = endpoint_occurrences[str(row["last_surface"])] > held_endpoint_occurrences[(folio, str(row["last_surface"]))]
    calibration_loci = [row for row in loci if row["first_seen"] and row["last_seen"]]
    target_loci = [row for row in loci if not row["first_seen"] or not row["last_seen"]]
    both_unseen = [row for row in target_loci if not row["first_seen"] and not row["last_seen"]]
    if (len(calibration_loci), len(target_loci), len(both_unseen)) != (1903, 970, 117):
        raise ValueError("seen/unseen split drift")

    calibration = summarize(calibration_loci, scores)
    preflight_gates = {
        "exact_1903_both_seen_loci": calibration["loci"] == 1903,
        "at_least_90_calibration_folios": calibration["folios"] >= 90,
        "calibration_direction_positive": calibration["equal_folio_compositional_contrast"] > 0,
        "calibration_locus_accuracy_at_least_0_65": calibration["nonzero_locus_accuracy"] >= 0.65,
        "calibration_folio_sign_p_at_most_0_01": calibration["one_sided_folio_sign_p"] <= 0.01,
        "calibration_increment_over_length_positive": calibration["increment_over_length_only"] > 0,
        "calibration_leave_one_folio_out_positive": calibration["minimum_leave_one_folio_out_contrast"] > 0,
        "calibration_max_contribution_at_most_0_10": calibration["max_absolute_folio_contribution_fraction"] <= 0.10,
        "score_table_finite_and_deterministic": bool(score_hash) and all(
            math.isfinite(value) for pair in scores.values() for value in pair
        ),
        "held_folio_excluded_from_fitting": True,
    }
    common = {
        "experiment": "SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR",
        "inputs": {path.name: digest(path) for path in (*FROZEN, SPEC, RUNNER)},
        "model": {
            "features": ["P1", "P2", "S1", "S2", "LEN"],
            "feature_vocabulary_sizes": FEATURE_SIZES,
            "alpha": ALPHA,
            "family_alphabet": alphabet,
            "held_unit": "physical_folio",
            "score_table_sha256": score_hash,
            "exact_full_family_surface_feature_used": False,
        },
        "capacity": {
            "multi_group_loci": len(loci),
            "both_seen_calibration_loci": len(calibration_loci),
            "at_least_one_unseen_target_loci": len(target_loci),
            "both_unseen_target_loci": len(both_unseen),
            "target_folios": len({row["folio"] for row in target_loci}),
        },
        "calibration": calibration,
        "preflight_gates": preflight_gates,
        "english_glosses": 0,
        "claim_ceiling": (
            "At most, reusable STA-family prefixes, suffixes, and length transfer first-versus-last "
            "construction-group position to unseen complete family forms across held physical folios. "
            "FIRST/LAST are structural positions, not meanings; no authorial word, sound, linguistic "
            "morpheme, part of speech, lexeme, plaintext, language, cipher, or translation."
        ),
    }
    if not all(preflight_gates.values()):
        result = {
            **common,
            "status": "STOP_UNSEEN_TARGET_UNOPENED_PREFLIGHT_FAILURE",
            "decision": "STOP_SOURCE_NATIVE_EDGE_GRAMMAR_BEFORE_TARGET",
            "target_joined": False,
            "target": None,
            "target_gates": None,
        }
    else:
        primary = summarize(target_loci, scores)
        subsets = {
            "both_endpoints_unseen": summarize(both_unseen, scores),
            "confirmed_prose": summarize([row for row in target_loci if row["grammar_scope"] == "CONFIRMED_PROSE"], scores),
            "all_three_member_exact_endpoints": summarize([
                row for row in target_loci if row["first_members_exact"] and row["last_members_exact"]
            ], scores),
            "currier_A": summarize([row for row in target_loci if row["currier"] == "A"], scores),
            "currier_B": summarize([row for row in target_loci if row["currier"] == "B"], scores),
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
                    summary["equal_folio_compositional_contrast"],
                    summary["equal_folio_length_only_contrast"],
                    summary["one_sided_folio_sign_p"],
                    summary["minimum_leave_one_folio_out_contrast"],
                    summary["max_absolute_folio_contribution_fraction"],
                )
            ),
        }
        passed = all(target_gates.values())
        result = {
            **common,
            "status": "PASS_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR" if passed else "NONCONFIRM_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR",
            "decision": "CONFIRMED_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR" if passed else "NONCONFIRM_SOURCE_NATIVE_PRODUCTIVE_EDGE_GRAMMAR",
            "target_joined": True,
            "target": {"primary": primary, "robustness": subsets},
            "target_gates": target_gates,
        }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["target"] is None:
        target_text = "The calibration failed and the unseen-form target remained unopened."
    else:
        primary = result["target"]["primary"]
        target_text = f"""On **{primary['loci']:,}** at-least-one-unseen endpoint pairs across
**{primary['folios']}** physical folios, the equal-folio compositional contrast
is **{primary['equal_folio_compositional_contrast']:.6f}**. Nonzero locus-pair
accuracy is **{primary['nonzero_locus_accuracy']:.3%}**; the folio sign p-value
is **{primary['one_sided_folio_sign_p']:.8f}**."""
    report = f"""# Source-native productive locus-edge grammar

Status: **{result['status']}**

The target-blind both-seen calibration uses **{calibration['loci']:,}** loci
and reaches **{calibration['nonzero_locus_accuracy']:.3%}** nonzero paired
accuracy with folio sign p **{calibration['one_sided_folio_sign_p']:.8f}**.

{target_text}

Decision: **{result['decision']}**. `FIRST` and `LAST` are source-native
structural positions, not START/STOP meanings. The result cannot establish an
authorial word, sound, linguistic morpheme, part of speech, lexeme, plaintext,
language, cipher, or translation.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "decision": result["decision"],
        "preflight_pass": all(preflight_gates.values()),
        "target_pass": None if result["target_gates"] is None else all(result["target_gates"].values()),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
