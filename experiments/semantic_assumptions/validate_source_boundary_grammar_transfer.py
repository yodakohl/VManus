#!/usr/bin/env python3
"""Nonimporting validator for the held source-boundary transfer result."""

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
R = BASE / "results"
LOCI = R / "source_sta_family_consensus_loci.tsv"
BOUNDARIES = R / "source_sta_family_consensus_boundaries.tsv"
CONSENSUS = R / "source_sta_family_consensus.json"
CAPACITY = R / "source_boundary_grammar_capacity.json"
CAPACITY_VALIDATION = R / "source_boundary_grammar_capacity_validation.json"
SPEC = BASE / "SOURCE_BOUNDARY_GRAMMAR_TRANSFER_SPEC.md"
PRODUCER = BASE / "run_source_boundary_grammar_transfer.py"
PRODUCTION = R / "source_boundary_grammar_transfer.json"
PRODUCTION_REPORT = R / "source_boundary_grammar_transfer_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = R / "source_boundary_grammar_transfer_validation.json"
OUT_REPORT = R / "source_boundary_grammar_transfer_validation_report.md"

EXPECTED_HASHES = {
    LOCI: "84354a9e5d291ab00f45c9bfe161f62d8cbd8c39db7511ff263cd9fcfe9d9e77",
    BOUNDARIES: "b32aa0a197f9a09eb19087ca80fcc0346601576d49429c346a5df23826ef3974",
    CONSENSUS: "193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7",
    CAPACITY: "7216a0e5d777d709d303421b2a8a62f38d34eda4b28cf55ee668a0284d2b8e48",
    CAPACITY_VALIDATION: "9288b2bde84538a292bd048a51768da2af96cd7b3a0dca5bca618e128cf7fcde",
    SPEC: "54619e474ff2dcce8b040a94196e6f6175c246b3388e3191645669b985b29a67",
    PRODUCER: "0211a2dadb440de36b35807f834a535afb1f36ca3ac819323f88aa8d780965c4",
    PRODUCTION: "15beab64f39736191d2b689eac5e36c692ada71912a0059a20f1715e5aa9d7ea",
    PRODUCTION_REPORT: "96c638e724103c2479ccff683830bd0d5aaf41e28d397501a67fc585cdf8e74e",
}
READINGS = ("ZL3b", "IT2a", "RF1b")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def held_folio(page: str) -> str:
    match = re.fullmatch(r"(f[0-9]+)[rv][0-9]*", page)
    assert match is not None
    return match.group(1)


def make_panel() -> tuple[list[dict[str, object]], list[str], int]:
    checks = 0
    strict = {}
    for row in table(LOCI):
        if row["strict_zero_alternative"] == "1":
            assert row["locus"] not in strict
            strict[row["locus"]] = row
            checks += 1
    assert len(strict) == 3572
    checks += 1
    boundaries = {}
    for row in table(BOUNDARIES):
        if row["strict_zero_alternative"] != "1":
            continue
        locus_id = row["locus"]
        position = int(row["position_after_symbol"])
        key = (locus_id, position)
        assert key not in boundaries and locus_id in strict
        locus = strict[locus_id]
        sequence = locus["family_sequence"]
        assert 0 < position < len(sequence)
        for field in ("page", "section", "currier", "hand", "code", "kind", "grammar_scope"):
            assert row[field] == locus[field]
            checks += 1
        assert row["left_family"] == sequence[position - 1]
        assert row["right_family"] == sequence[position]
        supporters = tuple(value for value in row["supporting_readings"].split(",") if value)
        support = int(row["support_count"])
        assert support in {1, 2, 3}
        assert len(supporters) == support
        assert set(supporters) <= set(READINGS)
        boundaries[key] = (support, supporters)
        checks += 7
    panel = []
    recovered = set()
    for locus_id in sorted(strict):
        locus = strict[locus_id]
        sequence = locus["family_sequence"]
        for position, (left, right) in enumerate(zip(sequence, sequence[1:]), 1):
            key = (locus_id, position)
            support, supporters = boundaries.get(key, (0, ()))
            if key in boundaries:
                recovered.add(key)
            panel.append({
                "locus": locus_id,
                "folio": held_folio(locus["page"]),
                "page": locus["page"],
                "section": locus["section"],
                "currier": locus["currier"],
                "kind": locus["kind"],
                "grammar_scope": locus["grammar_scope"],
                "position": position,
                "pair": left + right,
                "support": support,
                "supporters": supporters,
            })
            checks += 1
    assert recovered == set(boundaries)
    assert len(panel) == 91879
    assert Counter(row["support"] for row in panel) == Counter({0: 71356, 3: 19041, 1: 814, 2: 668})
    alphabet = sorted({character for locus in strict.values() for character in locus["family_sequence"]})
    assert len(alphabet) == 21
    checks += 4
    return panel, alphabet, checks


def fit(panel: list[dict[str, object]], alphabet: list[str]) -> tuple[dict[tuple[str, str], float], str]:
    totals = Counter()
    cells = Counter()
    held_totals = Counter()
    held_cells = Counter()
    for row in panel:
        label = row["support"]
        if label not in {0, 3}:
            continue
        folio = row["folio"]
        pair = row["pair"]
        totals[label] += 1
        cells[(label, pair)] += 1
        held_totals[(folio, label)] += 1
        held_cells[(folio, label, pair)] += 1
    score = {}
    raw = bytearray()
    k = len(alphabet) * len(alphabet)
    all_pairs = [left + right for left in alphabet for right in alphabet]
    for folio in sorted({row["folio"] for row in panel}):
        for pair in all_pairs:
            numerator3 = cells[(3, pair)] - held_cells[(folio, 3, pair)] + 0.5
            denominator3 = totals[3] - held_totals[(folio, 3)] + 0.5 * k
            numerator0 = cells[(0, pair)] - held_cells[(folio, 0, pair)] + 0.5
            denominator0 = totals[0] - held_totals[(folio, 0)] + 0.5 * k
            value = math.log(numerator3 / denominator3) - math.log(numerator0 / denominator0)
            assert math.isfinite(value)
            score[(folio, pair)] = value
            raw += folio.encode("ascii") + b"\0" + pair.encode("ascii") + b"\0" + struct.pack("<d", value)
    return score, hashlib.sha256(raw).hexdigest()


def exact_auc(high: list[float], low: list[float]) -> float:
    high_count = Counter(high)
    low_count = Counter(low)
    lower_low = 0
    wins = 0.0
    for value in sorted(set(high_count) | set(low_count)):
        wins += high_count[value] * (lower_low + low_count[value] / 2)
        lower_low += low_count[value]
    return wins / (len(high) * len(low))


def binomial_tail(positive: int, negative: int) -> float:
    n = positive + negative
    return sum(math.comb(n, k) for k in range(positive, n + 1)) / 2**n


def summarize(rows: list[dict[str, object]], score: dict[tuple[str, str], float]) -> dict:
    values: dict[str, dict[int, list[float]]] = defaultdict(lambda: {1: [], 2: []})
    for row in rows:
        label = row["support"]
        if label in {1, 2}:
            values[row["folio"]][label].append(score[(row["folio"], row["pair"])])
    details = []
    for folio in sorted(values):
        lower = values[folio][1]
        higher = values[folio][2]
        if lower and higher:
            details.append({
                "folio": folio,
                "support_1_n": len(lower),
                "support_2_n": len(higher),
                "contrast": mean(higher) - mean(lower),
            })
    contrasts = [row["contrast"] for row in details]
    positive = sum(value > 0 for value in contrasts)
    negative = sum(value < 0 for value in contrasts)
    tied = sum(value == 0 for value in contrasts)
    leave_one = [mean(contrasts[:i] + contrasts[i + 1:]) for i in range(len(contrasts))]
    return {
        "folios": len(details),
        "positions_support_1": sum(row["support_1_n"] for row in details),
        "positions_support_2": sum(row["support_2_n"] for row in details),
        "equal_folio_contrast": mean(contrasts),
        "positive_folios": positive,
        "negative_folios": negative,
        "tied_folios": tied,
        "nonzero_folios": positive + negative,
        "one_sided_sign_p": binomial_tail(positive, negative),
        "min_leave_one_folio_out_contrast": min(leave_one),
        "max_absolute_contribution_fraction": max(map(abs, contrasts)) / sum(map(abs, contrasts)),
        "folio_details": details,
    }


def reconstruct() -> tuple[dict, str, int]:
    for path, expected in EXPECTED_HASHES.items():
        assert file_hash(path) == expected
    checks = len(EXPECTED_HASHES)
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    capacity_validation = json.loads(CAPACITY_VALIDATION.read_text(encoding="utf-8"))
    assert capacity["decision"] == "GO_FREEZE_SOURCE_BOUNDARY_GRAMMAR_TEST"
    assert all(capacity["gates"].values())
    assert capacity_validation["status"] == "PASS_INDEPENDENT_RECONSTRUCTION"
    checks += 3
    panel, alphabet, panel_checks = make_panel()
    checks += panel_checks
    score, score_hash = fit(panel, alphabet)
    swapped = [dict(row, support={1: 2, 2: 1}.get(row["support"], row["support"])) for row in panel]
    _, swapped_hash = fit(swapped, alphabet)
    checks += len(score) * 2

    calibration_details = []
    for folio in sorted({row["folio"] for row in panel}):
        high = [score[(folio, row["pair"])] for row in panel if row["folio"] == folio and row["support"] == 3]
        low = [score[(folio, row["pair"])] for row in panel if row["folio"] == folio and row["support"] == 0]
        assert high and low
        calibration_details.append({
            "folio": folio,
            "support_0_n": len(low),
            "support_3_n": len(high),
            "contrast": mean(high) - mean(low),
            "auc": exact_auc(high, low),
        })
        checks += len(high) + len(low) + 1
    train_contrasts = [row["contrast"] for row in calibration_details]
    train_aucs = [row["auc"] for row in calibration_details]
    calibration = {
        "folios": len(calibration_details),
        "mean_equal_folio_contrast": mean(train_contrasts),
        "positive_folios": sum(value > 0 for value in train_contrasts),
        "mean_equal_folio_auc": mean(train_aucs),
        "minimum_folio_auc": min(train_aucs),
        "score_table_sha256": score_hash,
        "target_label_swap_score_table_sha256": swapped_hash,
        "folio_details": calibration_details,
    }
    preflight = {
        "capacity_go_and_validated": True,
        "exact_102_calibration_folios": calibration["folios"] == 102,
        "all_calibration_folios_have_both_classes": True,
        "mean_auc_at_least_0_90": calibration["mean_equal_folio_auc"] >= 0.90,
        "minimum_auc_at_least_0_80": calibration["minimum_folio_auc"] >= 0.80,
        "all_102_training_contrasts_positive": calibration["positive_folios"] == 102,
        "mean_training_contrast_at_least_4": calibration["mean_equal_folio_contrast"] >= 4.0,
        "target_label_swap_leaves_scores_identical": score_hash == swapped_hash,
        "all_calibration_values_finite": all(
            math.isfinite(value)
            for row in calibration_details
            for value in (row["contrast"], row["auc"])
        ),
    }
    assert all(preflight.values())
    primary = summarize(panel, score)
    primary["effect_fraction_of_training_contrast"] = primary["equal_folio_contrast"] / calibration["mean_equal_folio_contrast"]
    prose = summarize([row for row in panel if row["grammar_scope"] == "CONFIRMED_PROSE"], score)
    anchors = {}
    for reading in READINGS:
        subset = [
            row for row in panel
            if (row["support"] == 1 and row["supporters"] == (reading,))
            or (row["support"] == 2 and reading in row["supporters"])
        ]
        anchors[reading] = summarize(subset, score)
    target_gates = {
        "primary_direction_positive": primary["equal_folio_contrast"] > 0,
        "effect_at_least_0_05_training_contrast": primary["effect_fraction_of_training_contrast"] >= 0.05,
        "folio_sign_p_at_most_0_01": primary["one_sided_sign_p"] <= 0.01,
        "at_least_80_nonzero_folios": primary["nonzero_folios"] >= 80,
        "leave_one_folio_out_positive": primary["min_leave_one_folio_out_contrast"] > 0,
        "max_contribution_at_most_0_10": primary["max_absolute_contribution_fraction"] <= 0.10,
        "confirmed_prose_positive_at_least_50_folios": prose["folios"] >= 50 and prose["equal_folio_contrast"] > 0,
        "all_reading_anchors_positive_at_least_50_folios": all(
            row["folios"] >= 50 and row["equal_folio_contrast"] > 0 for row in anchors.values()
        ),
        "all_target_values_finite": all(
            math.isfinite(value)
            for summary in (primary, prose, *anchors.values())
            for value in (
                summary["equal_folio_contrast"], summary["one_sided_sign_p"],
                summary["min_leave_one_folio_out_contrast"], summary["max_absolute_contribution_fraction"],
            )
        ),
    }
    claim = (
        "At most, an ordered adjacent STA-family context learned from unanimous source-boundary "
        "evidence transfers to stronger versus weaker alternate-reading boundary support across "
        "held physical folios. No authorial boundary, word, corrected transcription, grammar role, "
        "sound, morpheme, lexeme, plaintext, language, cipher, or translation."
    )
    expected = {
        "experiment": "SOURCE_BOUNDARY_GRAMMAR_TRANSFER",
        "inputs": {path.name: file_hash(path) for path in (*EXPECTED_HASHES.keys(),) if path not in {PRODUCTION, PRODUCTION_REPORT}},
        "model": {
            "family_alphabet": alphabet,
            "family_count": len(alphabet),
            "ordered_pair_space": len(alphabet) ** 2,
            "jeffreys_alpha": 0.5,
            "held_unit": "physical_folio",
            "training_support_classes": [0, 3],
            "target_support_classes": [1, 2],
            "score_table_sha256": score_hash,
        },
        "calibration": calibration,
        "preflight_gates": preflight,
        "claim_ceiling": claim,
        "english_glosses": 0,
        "status": "NONCONFIRM_HELD_SOURCE_BOUNDARY_TRANSFER",
        "decision": "NONCONFIRM_SOURCE_BOUNDARY_FAMILY_GRAMMAR_TRANSFER",
        "target_scores_joined_to_labels": True,
        "target": {"primary": primary, "robustness": {"confirmed_prose": prose, "anchored_readings": anchors}},
        "target_gates": target_gates,
    }
    target_text = f"""The primary equal-folio support-2 minus support-1 contrast is
**{primary['equal_folio_contrast']:.6f}**, or
**{primary['effect_fraction_of_training_contrast']:.3%}** of the unanimous
boundary contrast. **{primary['positive_folios']}/{primary['nonzero_folios']}**
nonzero folios are positive; the exact one-sided sign p-value is
**{primary['one_sided_sign_p']:.8f}**."""
    report = f"""# Held source-boundary family grammar transfer

Status: **{expected['status']}**

The frozen family-pair score passed all target-blind preflight gates. Its held
unanimous-boundary versus unanimous-nonboundary mean folio AUC is
**{calibration['mean_equal_folio_auc']:.6f}** (minimum
**{calibration['minimum_folio_auc']:.6f}**), with all
**{calibration['positive_folios']}/{calibration['folios']}** folio contrasts
positive.

{target_text}

Decision: **{expected['decision']}**. At most, this concerns transferable source-
boundary confidence in adjacent STA-family context. It does not select an
authorial boundary, prove a word, correct a transcription, or identify a
grammar role, sound, morpheme, lexeme, plaintext, language, cipher, or
translation.
"""
    return expected, report, checks


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite validation outputs")
    expected, report, checks = reconstruct()
    actual = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    assert actual == expected
    assert PRODUCTION_REPORT.read_text(encoding="utf-8") == report
    assert expected["target_gates"]["all_reading_anchors_positive_at_least_50_folios"] is False
    assert expected["target"]["robustness"]["anchored_readings"]["IT2a"]["equal_folio_contrast"] < 0
    checks += 4
    validation = {
        "experiment": "SOURCE_BOUNDARY_GRAMMAR_TRANSFER_VALIDATION",
        "status": "PASS_INDEPENDENT_NONCONFIRM_RECONSTRUCTION",
        "checks_passed": checks,
        "checks_failed": 0,
        "inputs": {
            "production_json_sha256": file_hash(PRODUCTION),
            "production_report_sha256": file_hash(PRODUCTION_REPORT),
            "producer_sha256": file_hash(PRODUCER),
            "validator_sha256": file_hash(VALIDATOR),
            "spec_sha256": file_hash(SPEC),
        },
        "reconstructed_decision": expected["decision"],
        "failed_target_gates": sorted(key for key, value in expected["target_gates"].items() if not value),
        "target_scores_joined_to_labels": True,
        "english_glosses": 0,
        "claim_ceiling": expected["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    text = f"""# Held source-boundary family grammar transfer validation

Status: **PASS_INDEPENDENT_NONCONFIRM_RECONSTRUCTION**

A nonimporting implementation passed **{checks:,}** checks and reconstructed
the complete gap panel, 102-by-441 held score table, target-label-swap
invariance, every folio calibration/AUC, every primary and robustness contrast,
all gates, the production object, and the exact report text.

The registered decision remains
**NONCONFIRM_SOURCE_BOUNDARY_FAMILY_GRAMMAR_TRANSFER** because the IT2a anchor
is negative even though the aggregate contrast is positive. This validates the
nonconfirmation; it supplies no authorial boundary, word, corrected
transcription, grammar role, sound, morpheme, lexeme, plaintext, language,
cipher, or translation.
"""
    OUT_REPORT.write_text(text, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks, "decision": validation["reconstructed_decision"]}, sort_keys=True))


if __name__ == "__main__":
    main()
