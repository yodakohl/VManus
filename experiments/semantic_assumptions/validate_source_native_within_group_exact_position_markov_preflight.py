#!/usr/bin/env python3
"""Clean-room reconstruction of the exact-position Markov preflight."""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import hashlib
import json
import math
import multiprocessing as mp
from collections import defaultdict
from pathlib import Path

import numpy as np
import validate_source_native_within_group_stage_preflight_v2 as clean

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL_PATH = RESULTS / "source_native_within_group_stage_masked.tsv"
CAPACITY_VALIDATION = RESULTS / "source_native_within_group_stage_capacity_validation.json"
CLEAN_VALIDATOR = BASE / "validate_source_native_within_group_stage_preflight_v2.py"
CORE = BASE / "source_native_within_group_exact_position_markov_core.py"
SPEC = BASE / "SOURCE_NATIVE_WITHIN_GROUP_EXACT_POSITION_MARKOV_SPEC.md"
RUNNER = BASE / "run_source_native_within_group_exact_position_markov_preflight.py"
PRODUCTION = RESULTS / "source_native_within_group_exact_position_markov_preflight.json"
PRODUCTION_REPORT = RESULTS / "source_native_within_group_exact_position_markov_preflight_report.md"
TARGET_OUT = RESULTS / "source_native_within_group_exact_position_markov_target.json"
TARGET_REPORT = RESULTS / "source_native_within_group_exact_position_markov_target_report.md"
OUT = RESULTS / "source_native_within_group_exact_position_markov_preflight_validation.json"
REPORT = RESULTS / "source_native_within_group_exact_position_markov_preflight_validation_report.md"
FROZEN = {
    PANEL_PATH: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    CAPACITY_VALIDATION: "2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",
    CLEAN_VALIDATOR: "9d33a815fc10b75aa02a57568207691cdb33daf1165c5060c463cb811f8ed30a",
    CORE: "269d0167fb13930386eaba2398a47578c54a897bcb74f0b9b1da8c57f4d1a892",
    SPEC: "8b2747a55cd88cafe0f2fcc4201634b123c9bd95bcaac6bd8495e36e75aea5d1",
    RUNNER: "bd51a51b7286a70559cabe48cd1d9319a5823106acd12b0e7c65ec019a8760dd",
    PRODUCTION: "3e12ded71c65d158f5e3c20301c5701536ec29f0b4bc53bd39caa994366194a9",
    PRODUCTION_REPORT: "8ee6741226d8aa4e091b3b90e8ba3bf8d40a738df8aab09fb4437a58e438f2ff",
}
TASKS = (
    [("POSITION_ONLY", world) for world in range(64)]
    + [("MARKOV", 100 + world) for world in range(8)]
    + [("CURRIER_ONE", 200 + world) for world in range(8)]
    + [("ONE_FOLIO", 300 + world) for world in range(8)]
    + [("FOLIO_RANDOM", 400 + world) for world in range(8)]
)
PANEL = None
ALPHA = 0.5


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit(panel, sequences, markov):
    contexts = 24 if markov else 1
    counts = {
        (currier, length, position): np.full((contexts, 24), ALPHA, dtype=np.float64)
        for currier in "AB"
        for length in range(2, 12)
        for position in range(1, length)
    }
    for row, sequence, length in zip(panel.rows, sequences, panel.lengths):
        if row["split"] != "TRAIN" or length < 2:
            continue
        for position in range(1, len(sequence)):
            context = sequence[position - 1] if markov else 0
            counts[(row["currier"], int(length), position)][context, sequence[position]] += 1.0
    return {key: value / value.sum(axis=1, keepdims=True) for key, value in counts.items()}


def probability(sequence, length, currier, model, markov):
    return sum(
        math.log(model[(currier, length, position)][sequence[position - 1] if markov else 0, sequence[position]])
        for position in range(1, len(sequence))
    )


def sign_p(positive, total):
    return sum(math.comb(total, k) for k in range(positive, total + 1)) / (2**total)


def summarize(values):
    effects = []
    for folio in sorted(values, key=lambda value: int(value[1:])):
        effects.append(sum(x for x, _ in values[folio]) / sum(n for _, n in values[folio]))
    array = np.asarray(effects, dtype=np.float64)
    deletion = (array.sum() - array) / (len(array) - 1)
    denominator = float(np.abs(array).sum())
    return {
        "effect_equal_folio": float(array.mean()),
        "positive_folios": int((array > 0).sum()),
        "folios": len(array),
        "sign_p": sign_p(int((array > 0).sum()), len(array)),
        "minimum_leave_one_folio_out": float(deletion.min()),
        "max_abs_contribution_fraction": float(np.abs(array).max() / denominator) if denominator else 1.0,
    }


def evaluate(panel, sequences):
    if len(panel.rows) != 21899 or len({row["unit_id"] for row in panel.rows}) != 21899:
        raise ValueError("panel identity")
    if not all(len(array) == 21899 for array in (panel.lengths, panel.splits, panel.curriers, panel.folios)):
        raise ValueError("panel identity")
    if any(int(length) < 1 or int(length) > 11 for length in panel.lengths):
        raise ValueError("panel length")
    if len(sequences) != len(panel.rows) or any(len(sequence) != length for sequence, length in zip(sequences, panel.lengths)):
        raise ValueError("geometry")
    if any(not sequence or any(symbol < 0 or symbol >= 24 for symbol in sequence) for sequence in sequences):
        raise ValueError("symbol")
    baseline = fit(panel, sequences, False)
    full = fit(panel, sequences, True)
    calibration_gain = 0.0
    calibration_symbols = 0
    for row, sequence, length in zip(panel.rows, sequences, panel.lengths):
        if row["split"] == "CAL" and length >= 2:
            calibration_gain += probability(sequence, int(length), row["currier"], full, True) - probability(sequence, int(length), row["currier"], baseline, False)
            calibration_symbols += len(sequence) - 1
    by_folio = defaultdict(list)
    unseen_by_folio = defaultdict(list)
    by_currier = {"A": defaultdict(list), "B": defaultdict(list)}
    train = {
        (row["currier"], int(length), sequence)
        for row, length, sequence in zip(panel.rows, panel.lengths, sequences)
        if row["split"] == "TRAIN"
    }
    total = unseen_total = 0.0
    test_groups = test_symbols = unseen_groups = unseen_symbols = 0
    for row, sequence, length in zip(panel.rows, sequences, panel.lengths):
        if row["split"] != "TEST" or length < 2:
            continue
        gain = probability(sequence, int(length), row["currier"], full, True) - probability(sequence, int(length), row["currier"], baseline, False)
        symbols = len(sequence) - 1
        folio = row["physical_folio"]
        by_folio[folio].append((gain, symbols))
        by_currier[row["currier"]][folio].append((gain, symbols))
        total += gain
        test_groups += 1
        test_symbols += symbols
        if (row["currier"], int(length), sequence) not in train:
            unseen_by_folio[folio].append((gain, symbols))
            unseen_total += gain
            unseen_groups += 1
            unseen_symbols += symbols
    return {
        "cal_gain_per_symbol": calibration_gain / calibration_symbols,
        "test_groups": test_groups,
        "test_symbols": test_symbols,
        "gain_equal_symbol": total / test_symbols,
        "gain": summarize(by_folio),
        "unseen": {
            "groups": unseen_groups,
            "symbols": unseen_symbols,
            "gain_equal_symbol": unseen_total / unseen_symbols,
            **summarize(unseen_by_folio),
        },
        "currier": {currier: {"gain": summarize(by_currier[currier])} for currier in "AB"},
    }


def passes(result):
    return (
        result["cal_gain_per_symbol"] > 0
        and result["test_groups"] == 5521
        and result["test_symbols"] == 17435
        and result["gain"]["folios"] == 24
        and result["gain"]["effect_equal_folio"] >= 0.005
        and result["gain"]["positive_folios"] >= 18
        and result["gain"]["sign_p"] <= 0.01
        and result["gain"]["minimum_leave_one_folio_out"] > 0
        and result["gain"]["max_abs_contribution_fraction"] <= 0.15
        and result["unseen"]["groups"] >= 500
        and result["unseen"]["effect_equal_folio"] >= 0.003
        and result["unseen"]["minimum_leave_one_folio_out"] > 0
        and all(
            result["currier"][currier]["gain"]["effect_equal_folio"] >= 0.002
            and result["currier"][currier]["gain"]["minimum_leave_one_folio_out"] > 0
            and result["currier"][currier]["gain"]["positive_folios"] / result["currier"][currier]["gain"]["folios"] >= 0.65
            for currier in "AB"
        )
    )


def synthetic(panel, world, mode, strength=0.45):
    if mode not in {"POSITION_ONLY", "MARKOV", "CURRIER_ONE", "ONE_FOLIO", "FOLIO_RANDOM"}:
        raise ValueError("mode")
    folios = sorted(set(panel.folios), key=lambda value: int(value[1:]))
    active_folio = folios[world % len(folios)]
    mappings = {
        currier: tuple(sorted(range(24), key=lambda symbol: clean.stable_u64(f"SNWGM2|{world}|MAP|{currier}|{symbol}")))
        for currier in "AB"
    }
    output = []
    for row, length_value in zip(panel.rows, panel.lengths):
        length = int(length_value)
        bucket = clean.stable_u64(f"SNWGM2|BUCKET|{row['unit_id']}") % 128
        position_mappings = {
            position: sorted(range(24), key=lambda symbol: clean.stable_u64(f"SNWGM2|{world}|BASE|{row['currier']}|{length}|{position}|{symbol}"))
            for position in range(length)
        }
        transition = mappings[row["currier"]]
        if mode == "FOLIO_RANDOM":
            transition = tuple(sorted(range(24), key=lambda symbol: clean.stable_u64(f"SNWGM2|{world}|FMAP|{row['physical_folio']}|{row['currier']}|{symbol}")))
        sequence = []
        for position in range(length):
            uniform = (clean.stable_u64(f"SNWGM2|{world}|U|{row['split']}|{row['currier']}|{length}|{bucket}|{position}") + 0.5) / (1 << 64)
            base = position_mappings[position]
            if uniform < 0.36:
                symbol = base[0]
            elif uniform < 0.57:
                symbol = base[1]
            else:
                symbol = clean.stable_u64(f"SNWGM2|{world}|R|{row['split']}|{row['currier']}|{length}|{bucket}|{position}") % 24
            active = (
                mode in {"MARKOV", "CURRIER_ONE", "ONE_FOLIO", "FOLIO_RANDOM"}
                and (mode != "CURRIER_ONE" or row["currier"] == "B")
                and (mode != "ONE_FOLIO" or row["physical_folio"] == active_folio)
            )
            if active and position > 0 and uniform < strength:
                symbol = transition[sequence[-1]]
            sequence.append(int(symbol))
        output.append(tuple(sequence))
    return output


def compact(result):
    return {**result, "EXACT_POSITION_MARKOV_PASS": passes(result)}


def worker(payload):
    mode, world, reverse = payload
    sequences = synthetic(PANEL, world, mode)
    if reverse:
        sequences = [tuple(reversed(sequence)) for sequence in sequences]
    return mode, world, reverse, compact(evaluate(PANEL, sequences))


def numeric_max(left, right):
    if isinstance(left, dict):
        return math.inf if set(left) != set(right) else max((numeric_max(left[key], right[key]) for key in left), default=0.0)
    if isinstance(left, list):
        return math.inf if len(left) != len(right) else max((numeric_max(a, b) for a, b in zip(left, right)), default=0.0)
    if isinstance(left, (int, float)) and not isinstance(left, bool):
        return abs(float(left) - float(right))
    return 0.0 if left == right else math.inf


def finite(value):
    if isinstance(value, dict):
        return all(finite(item) for item in value.values())
    if isinstance(value, list):
        return all(finite(item) for item in value)
    return not isinstance(value, float) or math.isfinite(value)


def expected_report(status, decision, counts, passed):
    return f"""# Exact-position-controlled transition preflight

Status: **{status}**

Forward/reversed grids yield **{counts['forward']['POSITION_ONLY']['passes']}/64**
and **{counts['reversed']['POSITION_ONLY']['passes']}/64** position-only false
passes and **{counts['forward']['MARKOV']['passes']}/8** and
**{counts['reversed']['MARKOV']['passes']}/8** Markov-plant passes. Every
adversarial family yields zero passes in both orientations; all 96 decisions
are reversal-stable and remaining gates are **{'passing' if passed else 'not all passing'}**.

Zero manuscript sequences or scores were opened. Decision: **{decision}**.
No syntax, morphology, sound, word, language, meaning, plaintext, cipher, or
translation follows.
"""


def main():
    global PANEL
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
        check(sha(path) == expected, f"hash:{path.name}")
    PANEL = clean.load_panel()
    payloads = [(mode, world, reverse) for reverse in (False, True) for mode, world in TASKS]
    with mp.get_context("fork").Pool(32) as pool:
        rebuilt = pool.map(worker, payloads)
    reconstructed = {(mode, world, reverse): value for mode, world, reverse, value in rebuilt}
    production = json.loads(PRODUCTION.read_text())
    stored = {(row["mode"], row["world"], row["reverse"]): row for row in production["records"]}
    check(set(reconstructed) == set(stored), "record identities")
    maximum_delta = 0.0
    for key, value in reconstructed.items():
        delta = numeric_max({"mode": key[0], "world": key[1], "reverse": key[2], **value}, stored[key])
        maximum_delta = max(maximum_delta, delta)
        check(delta <= 1e-12, f"record:{key}")
    counts = {}
    for reverse in (False, True):
        name = "reversed" if reverse else "forward"
        counts[name] = {
            mode: {
                "worlds": sum(candidate == mode for candidate, _ in TASKS),
                "passes": sum(reconstructed[(mode, world, reverse)]["EXACT_POSITION_MARKOV_PASS"] for candidate, world in TASKS if candidate == mode),
            }
            for mode in ("POSITION_ONLY", "MARKOV", "CURRIER_ONE", "ONE_FOLIO", "FOLIO_RANDOM")
        }
    check(production["counts"] == counts, "counts")
    mismatches = [
        f"{mode}:{world}"
        for mode, world in TASKS
        if reconstructed[(mode, world, False)]["EXACT_POSITION_MARKOV_PASS"] != reconstructed[(mode, world, True)]["EXACT_POSITION_MARKOV_PASS"]
    ]
    check(production["reversal_decision_mismatches"] == mismatches, "reversal")
    reference_sequences = synthetic(PANEL, 100, "MARKOV")
    reference = compact(evaluate(PANEL, reference_sequences))
    permutation = np.asarray([(7 * value + 3) % 24 for value in range(24)], dtype=np.int64)
    relabeled = compact(evaluate(PANEL, [tuple(int(permutation[symbol]) for symbol in sequence) for sequence in reference_sequences]))
    label_delta = numeric_max(reference, relabeled)
    check(abs(production["label_relabel_max_abs"] - label_delta) <= 1e-12, "label")
    mutations = {}
    for name, altered in (
        ("missing_sequence", reference_sequences[:-1]),
        ("length_mismatch", [tuple()] + reference_sequences[1:]),
        ("invalid_symbol", [(-1,) + reference_sequences[0][1:]] + reference_sequences[1:]),
    ):
        try:
            evaluate(PANEL, altered)
        except ValueError:
            mutations[name] = True
        else:
            mutations[name] = False
    bad_rows = [dict(row) for row in PANEL.rows]
    bad_rows[0]["unit_id"] = bad_rows[1]["unit_id"]
    bad_panel = type(PANEL)(bad_rows, PANEL.lengths, PANEL.splits, PANEL.curriers, PANEL.folios)
    try:
        evaluate(bad_panel, reference_sequences)
    except ValueError:
        mutations["duplicate_unit_id"] = True
    else:
        mutations["duplicate_unit_id"] = False
    check(production["mutations"] == mutations, "mutations")

    def pattern(name):
        return (
            counts[name]["POSITION_ONLY"]["passes"] <= 1
            and counts[name]["MARKOV"]["passes"] >= 7
            and all(counts[name][mode]["passes"] == 0 for mode in ("CURRIER_ONE", "ONE_FOLIO", "FOLIO_RANDOM"))
        )

    gates = {
        "forward_expected_pattern": pattern("forward"),
        "reversed_expected_pattern": pattern("reversed"),
        "all_96_decisions_reversal_stable": not mismatches,
        "label_relabel_invariance": label_delta <= 1e-10,
        "finite_values": all(finite(value) for value in reconstructed.values()),
        "mutation_guards": all(mutations.values()),
        "exact_capacity": sum((PANEL.splits == "TEST") & (PANEL.lengths >= 2)) == 5521
        and int(sum(max(0, int(length) - 1) for length in PANEL.lengths[PANEL.splits == "TEST"])) == 17435
        and len(set(PANEL.folios)) == 94,
        "target_absent": not TARGET_OUT.exists() and not TARGET_REPORT.exists(),
    }
    check(production["gates"] == gates, "gates")
    check(all(gates.values()), "all gates")
    check(
        production["status"] == "PASS_TARGET_FREE_EXACT_POSITION_MARKOV_PREFLIGHT"
        and production["decision"] == "GO_INDEPENDENTLY_VALIDATE_EXACT_POSITION_MARKOV",
        "decision",
    )
    check(
        production["target_source_opened"] is False
        and production["target_sequences_accessed"] == 0
        and production["target_scores_computed"] == 0
        and production["target_outputs_absent"] is True,
        "isolation",
    )
    check(PRODUCTION_REPORT.read_text() == expected_report(production["status"], production["decision"], counts, True), "report")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_WITHIN_GROUP_EXACT_POSITION_MARKOV_PREFLIGHT_VALIDATION",
        "status": "PASS_INDEPENDENT_192_WORLD_EXACT_POSITION_MARKOV_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "reconstructed_worlds": 192,
        "counts": counts,
        "max_record_numeric_delta": maximum_delta,
        "target_source_opened": False,
        "target_sequences_accessed": 0,
        "target_scores_computed": 0,
        "target_outputs_absent": True,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "claim_ceiling": "Independent synthetic exact-position-transition reconstruction only; no syntax, morphology, sound, word, language, meaning, plaintext, cipher, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Exact-position Markov preflight validation

Status: **{result['status']}**

A production-free implementation reconstructs all **192** synthetic records,
counts, invariance, mutations, gates, decision, and report in **{checks} checks**
with maximum numeric discrepancy **{maximum_delta:.3g}**. The target remains absent.

This validates calibration only and supplies no syntax, morphology, sound,
word, language, meaning, plaintext, cipher, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks, "max_delta": maximum_delta}, sort_keys=True))


if __name__ == "__main__":
    main()
