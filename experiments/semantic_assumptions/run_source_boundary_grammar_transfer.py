#!/usr/bin/env python3
"""Run the preregistered held source-boundary family-pair transfer test."""

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


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
LOCI = RESULTS / "source_sta_family_consensus_loci.tsv"
BOUNDARIES = RESULTS / "source_sta_family_consensus_boundaries.tsv"
CONSENSUS = RESULTS / "source_sta_family_consensus.json"
CAPACITY = RESULTS / "source_boundary_grammar_capacity.json"
CAPACITY_VALIDATION = RESULTS / "source_boundary_grammar_capacity_validation.json"
SPEC = HERE / "SOURCE_BOUNDARY_GRAMMAR_TRANSFER_SPEC.md"
RUNNER = Path(__file__).resolve()
OUT = RESULTS / "source_boundary_grammar_transfer.json"
REPORT = RESULTS / "source_boundary_grammar_transfer_report.md"

FROZEN = {
    LOCI: "84354a9e5d291ab00f45c9bfe161f62d8cbd8c39db7511ff263cd9fcfe9d9e77",
    BOUNDARIES: "b32aa0a197f9a09eb19087ca80fcc0346601576d49429c346a5df23826ef3974",
    CONSENSUS: "193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7",
    CAPACITY: "7216a0e5d777d709d303421b2a8a62f38d34eda4b28cf55ee668a0284d2b8e48",
    CAPACITY_VALIDATION: "9288b2bde84538a292bd048a51768da2af96cd7b3a0dca5bca618e128cf7fcde",
}
READINGS = ("ZL3b", "IT2a", "RF1b")
ALPHA = 0.5


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def physical_folio(page: str) -> str:
    found = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if found is None:
        raise ValueError(f"bad page: {page}")
    return found.group(1)


def reconstruct_gaps() -> tuple[list[dict[str, object]], list[str]]:
    strict = {
        row["locus"]: row
        for row in tsv(LOCI)
        if row["strict_zero_alternative"] == "1"
    }
    if len(strict) != 3572:
        raise ValueError("strict-locus count drift")
    boundary_map = {}
    for row in tsv(BOUNDARIES):
        if row["strict_zero_alternative"] != "1":
            continue
        key = (row["locus"], int(row["position_after_symbol"]))
        if key in boundary_map or row["locus"] not in strict:
            raise ValueError(f"bad boundary key: {key}")
        locus = strict[row["locus"]]
        sequence = locus["family_sequence"]
        position = key[1]
        if not 0 < position < len(sequence):
            raise ValueError(f"noninternal boundary: {key}")
        for field in ("page", "section", "currier", "hand", "code", "kind", "grammar_scope"):
            if row[field] != locus[field]:
                raise ValueError(f"metadata drift: {key}: {field}")
        if (row["left_family"], row["right_family"]) != (sequence[position - 1], sequence[position]):
            raise ValueError(f"family drift: {key}")
        support = int(row["support_count"])
        supporters = tuple(part for part in row["supporting_readings"].split(",") if part)
        if support not in (1, 2, 3) or len(supporters) != support or any(part not in READINGS for part in supporters):
            raise ValueError(f"support drift: {key}")
        boundary_map[key] = (support, supporters)
    gaps = []
    used = set()
    for locus_id in sorted(strict):
        locus = strict[locus_id]
        sequence = locus["family_sequence"]
        for position in range(1, len(sequence)):
            key = (locus_id, position)
            support, supporters = boundary_map.get(key, (0, ()))
            if key in boundary_map:
                used.add(key)
            gaps.append({
                "locus": locus_id,
                "folio": physical_folio(locus["page"]),
                "page": locus["page"],
                "section": locus["section"],
                "currier": locus["currier"],
                "kind": locus["kind"],
                "grammar_scope": locus["grammar_scope"],
                "position": position,
                "pair": sequence[position - 1:position + 1],
                "support": support,
                "supporters": supporters,
            })
    if used != set(boundary_map) or len(gaps) != 91879:
        raise ValueError("gap reconstruction drift")
    alphabet = sorted({character for row in strict.values() for character in row["family_sequence"]})
    if len(alphabet) != 21:
        raise ValueError("family alphabet drift")
    return gaps, alphabet


def build_scores(gaps: list[dict[str, object]], alphabet: list[str]) -> tuple[dict[tuple[str, str], float], str]:
    pairs = [left + right for left in alphabet for right in alphabet]
    folios = sorted({str(row["folio"]) for row in gaps})
    global_counts = Counter()
    folio_counts = Counter()
    global_totals = Counter()
    folio_totals = Counter()
    for row in gaps:
        support = int(row["support"])
        if support not in (0, 3):
            continue
        folio = str(row["folio"])
        pair = str(row["pair"])
        global_counts[(support, pair)] += 1
        folio_counts[(folio, support, pair)] += 1
        global_totals[support] += 1
        folio_totals[(folio, support)] += 1
    k = len(alphabet) ** 2
    scores = {}
    payload = bytearray()
    for folio in folios:
        for pair in pairs:
            terms = {}
            for support in (0, 3):
                count = global_counts[(support, pair)] - folio_counts[(folio, support, pair)]
                total = global_totals[support] - folio_totals[(folio, support)]
                terms[support] = math.log((count + ALPHA) / (total + ALPHA * k))
            value = terms[3] - terms[0]
            if not math.isfinite(value):
                raise ValueError("nonfinite score")
            scores[(folio, pair)] = value
            payload.extend(folio.encode("ascii") + b"\0" + pair.encode("ascii") + b"\0")
            payload.extend(struct.pack("<d", value))
    return scores, hashlib.sha256(payload).hexdigest()


def auc(positives: list[float], negatives: list[float]) -> float:
    positive_counts = Counter(positives)
    negative_counts = Counter(negatives)
    below = 0
    favorable = 0.0
    for value in sorted(set(positive_counts) | set(negative_counts)):
        favorable += positive_counts[value] * (below + 0.5 * negative_counts[value])
        below += negative_counts[value]
    return favorable / (len(positives) * len(negatives))


def sign_tail(positive: int, negative: int) -> float:
    n = positive + negative
    return sum(math.comb(n, value) for value in range(positive, n + 1)) / (2 ** n)


def target_summary(rows: list[dict[str, object]], scores: dict[tuple[str, str], float]) -> dict:
    by_folio: dict[str, dict[int, list[float]]] = defaultdict(lambda: {1: [], 2: []})
    for row in rows:
        support = int(row["support"])
        if support in (1, 2):
            by_folio[str(row["folio"])][support].append(scores[(str(row["folio"]), str(row["pair"]))])
    details = []
    for folio in sorted(by_folio):
        one = by_folio[folio][1]
        two = by_folio[folio][2]
        if one and two:
            details.append({
                "folio": folio,
                "support_1_n": len(one),
                "support_2_n": len(two),
                "contrast": mean(two) - mean(one),
            })
    contrasts = [row["contrast"] for row in details]
    positive = sum(value > 0 for value in contrasts)
    negative = sum(value < 0 for value in contrasts)
    ties = sum(value == 0 for value in contrasts)
    overall = mean(contrasts)
    loo = [mean(contrasts[:index] + contrasts[index + 1:]) for index in range(len(contrasts))]
    concentration = max(map(abs, contrasts)) / sum(map(abs, contrasts))
    return {
        "folios": len(details),
        "positions_support_1": sum(row["support_1_n"] for row in details),
        "positions_support_2": sum(row["support_2_n"] for row in details),
        "equal_folio_contrast": overall,
        "positive_folios": positive,
        "negative_folios": negative,
        "tied_folios": ties,
        "nonzero_folios": positive + negative,
        "one_sided_sign_p": sign_tail(positive, negative),
        "min_leave_one_folio_out_contrast": min(loo),
        "max_absolute_contribution_fraction": concentration,
        "folio_details": details,
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite transfer result")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    capacity_validation = json.loads(CAPACITY_VALIDATION.read_text(encoding="utf-8"))
    if capacity["decision"] != "GO_FREEZE_SOURCE_BOUNDARY_GRAMMAR_TEST" or not all(capacity["gates"].values()):
        raise SystemExit("capacity decision is not GO")
    if capacity_validation["status"] != "PASS_INDEPENDENT_RECONSTRUCTION":
        raise SystemExit("capacity validation is not PASS")

    gaps, alphabet = reconstruct_gaps()
    scores, score_digest = build_scores(gaps, alphabet)
    mutated = [dict(row, support=({1: 2, 2: 1}.get(int(row["support"]), int(row["support"])))) for row in gaps]
    _, mutated_digest = build_scores(mutated, alphabet)

    folios = sorted({str(row["folio"]) for row in gaps})
    calibration_details = []
    for folio in folios:
        positives = [scores[(folio, str(row["pair"]))] for row in gaps if row["folio"] == folio and row["support"] == 3]
        negatives = [scores[(folio, str(row["pair"]))] for row in gaps if row["folio"] == folio and row["support"] == 0]
        if not positives or not negatives:
            raise ValueError(f"missing calibration class in {folio}")
        calibration_details.append({
            "folio": folio,
            "support_0_n": len(negatives),
            "support_3_n": len(positives),
            "contrast": mean(positives) - mean(negatives),
            "auc": auc(positives, negatives),
        })
    train_contrasts = [row["contrast"] for row in calibration_details]
    train_aucs = [row["auc"] for row in calibration_details]
    calibration = {
        "folios": len(calibration_details),
        "mean_equal_folio_contrast": mean(train_contrasts),
        "positive_folios": sum(value > 0 for value in train_contrasts),
        "mean_equal_folio_auc": mean(train_aucs),
        "minimum_folio_auc": min(train_aucs),
        "score_table_sha256": score_digest,
        "target_label_swap_score_table_sha256": mutated_digest,
        "folio_details": calibration_details,
    }
    preflight_gates = {
        "capacity_go_and_validated": True,
        "exact_102_calibration_folios": calibration["folios"] == 102,
        "all_calibration_folios_have_both_classes": True,
        "mean_auc_at_least_0_90": calibration["mean_equal_folio_auc"] >= 0.90,
        "minimum_auc_at_least_0_80": calibration["minimum_folio_auc"] >= 0.80,
        "all_102_training_contrasts_positive": calibration["positive_folios"] == 102,
        "mean_training_contrast_at_least_4": calibration["mean_equal_folio_contrast"] >= 4.0,
        "target_label_swap_leaves_scores_identical": score_digest == mutated_digest,
        "all_calibration_values_finite": all(
            math.isfinite(value)
            for row in calibration_details
            for value in (row["contrast"], row["auc"])
        ),
    }

    common = {
        "experiment": "SOURCE_BOUNDARY_GRAMMAR_TRANSFER",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, RUNNER)},
        "model": {
            "family_alphabet": alphabet,
            "family_count": len(alphabet),
            "ordered_pair_space": len(alphabet) ** 2,
            "jeffreys_alpha": ALPHA,
            "held_unit": "physical_folio",
            "training_support_classes": [0, 3],
            "target_support_classes": [1, 2],
            "score_table_sha256": score_digest,
        },
        "calibration": calibration,
        "preflight_gates": preflight_gates,
        "claim_ceiling": (
            "At most, an ordered adjacent STA-family context learned from unanimous source-boundary "
            "evidence transfers to stronger versus weaker alternate-reading boundary support across "
            "held physical folios. No authorial boundary, word, corrected transcription, grammar role, "
            "sound, morpheme, lexeme, plaintext, language, cipher, or translation."
        ),
        "english_glosses": 0,
    }
    if not all(preflight_gates.values()):
        result = {
            **common,
            "status": "STOP_TARGET_UNOPENED_PREFLIGHT_FAILURE",
            "decision": "STOP_SOURCE_BOUNDARY_GRAMMAR_BEFORE_TARGET",
            "target_scores_joined_to_labels": False,
            "target": None,
            "target_gates": None,
        }
    else:
        primary = target_summary(gaps, scores)
        primary["effect_fraction_of_training_contrast"] = (
            primary["equal_folio_contrast"] / calibration["mean_equal_folio_contrast"]
        )
        prose = target_summary([row for row in gaps if row["grammar_scope"] == "CONFIRMED_PROSE"], scores)
        anchors = {}
        for reading in READINGS:
            anchor_rows = [
                row for row in gaps
                if (row["support"] == 1 and row["supporters"] == (reading,))
                or (row["support"] == 2 and reading in row["supporters"])
            ]
            anchors[reading] = target_summary(anchor_rows, scores)
        robustness = {"confirmed_prose": prose, "anchored_readings": anchors}
        target_gates = {
            "primary_direction_positive": primary["equal_folio_contrast"] > 0,
            "effect_at_least_0_05_training_contrast": primary["effect_fraction_of_training_contrast"] >= 0.05,
            "folio_sign_p_at_most_0_01": primary["one_sided_sign_p"] <= 0.01,
            "at_least_80_nonzero_folios": primary["nonzero_folios"] >= 80,
            "leave_one_folio_out_positive": primary["min_leave_one_folio_out_contrast"] > 0,
            "max_contribution_at_most_0_10": primary["max_absolute_contribution_fraction"] <= 0.10,
            "confirmed_prose_positive_at_least_50_folios": prose["folios"] >= 50 and prose["equal_folio_contrast"] > 0,
            "all_reading_anchors_positive_at_least_50_folios": all(
                row["folios"] >= 50 and row["equal_folio_contrast"] > 0
                for row in anchors.values()
            ),
            "all_target_values_finite": all(
                math.isfinite(value)
                for summary in (primary, prose, *anchors.values())
                for value in (
                    summary["equal_folio_contrast"],
                    summary["one_sided_sign_p"],
                    summary["min_leave_one_folio_out_contrast"],
                    summary["max_absolute_contribution_fraction"],
                )
            ),
        }
        passed = all(target_gates.values())
        result = {
            **common,
            "status": "PASS_HELD_SOURCE_BOUNDARY_TRANSFER" if passed else "NONCONFIRM_HELD_SOURCE_BOUNDARY_TRANSFER",
            "decision": (
                "CONFIRMED_SOURCE_BOUNDARY_FAMILY_GRAMMAR_TRANSFER"
                if passed else "NONCONFIRM_SOURCE_BOUNDARY_FAMILY_GRAMMAR_TRANSFER"
            ),
            "target_scores_joined_to_labels": True,
            "target": {"primary": primary, "robustness": robustness},
            "target_gates": target_gates,
        }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    target = result["target"]
    if target is None:
        target_text = "The preflight failed, so target scores were not joined to target labels."
    else:
        primary = target["primary"]
        target_text = f"""The primary equal-folio support-2 minus support-1 contrast is
**{primary['equal_folio_contrast']:.6f}**, or
**{primary['effect_fraction_of_training_contrast']:.3%}** of the unanimous
boundary contrast. **{primary['positive_folios']}/{primary['nonzero_folios']}**
nonzero folios are positive; the exact one-sided sign p-value is
**{primary['one_sided_sign_p']:.8f}**."""
    report = f"""# Held source-boundary family grammar transfer

Status: **{result['status']}**

The frozen family-pair score passed all target-blind preflight gates. Its held
unanimous-boundary versus unanimous-nonboundary mean folio AUC is
**{calibration['mean_equal_folio_auc']:.6f}** (minimum
**{calibration['minimum_folio_auc']:.6f}**), with all
**{calibration['positive_folios']}/{calibration['folios']}** folio contrasts
positive.

{target_text}

Decision: **{result['decision']}**. At most, this concerns transferable source-
boundary confidence in adjacent STA-family context. It does not select an
authorial boundary, prove a word, correct a transcription, or identify a
grammar role, sound, morpheme, lexeme, plaintext, language, cipher, or
translation.
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
