#!/usr/bin/env python3
"""Registered one-shot FPR001 f37v ordered-root target scorer."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
SPEC = BASE / "FPR001_F37V_ONE_SHOT_TARGET_SPEC.md"
CALIBRATION = BASE / "results/fpr001_ordered_root_target_blind_calibration.json"
CAL_VALIDATION = BASE / "results/fpr001_ordered_root_target_blind_calibration_validation.json"
SOURCE = BASE / "results/pre_grounding_interlinear.tsv"
VALIDATOR = BASE / "validate_fpr001_f37v_one_shot_target.py"
FREEZE = BASE / "FPR001_F37V_ONE_SHOT_TARGET_FREEZE.json"
OUT = BASE / "results/fpr001_f37v_one_shot_target.json"
REPORT = BASE / "results/fpr001_f37v_one_shot_target_report.md"
VAL_OUT = BASE / "results/fpr001_f37v_one_shot_target_validation.json"
VAL_REPORT = BASE / "results/fpr001_f37v_one_shot_target_validation_report.md"
QUERY = ("ot", "od", "e", "od", "or")
EDITIONS = ("ZL3b", "IT2a", "RF1b")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def strict_json(path: Path) -> tuple[dict[str, object], bytes]:
    raw = path.read_bytes()
    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        out = {}
        for key, value in items:
            if key in out:
                raise RuntimeError(("duplicate key", key))
            out[key] = value
        return out
    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    if type(value) is not dict or canonical(value) != raw:
        raise RuntimeError("noncanonical freeze")
    return value, raw


def lcs(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    prior = [0] * (len(right) + 1)
    for x in left:
        current = [0]
        for j, y in enumerate(right, 1):
            current.append(prior[j - 1] + 1 if x == y else max(prior[j], current[-1]))
        prior = current
    return prior[-1]


def witness(word: tuple[str, ...]) -> dict[str, object]:
    best: tuple[int, tuple[int, ...], tuple[int, ...]] | None = None
    for size in range(1, len(QUERY) + 1):
        for qi in itertools.combinations(range(len(QUERY)), size):
            wanted = tuple(QUERY[i] for i in qi)
            for ti in itertools.combinations(range(len(word)), size):
                if tuple(word[i] for i in ti) == wanted:
                    candidate = (size, qi, ti)
                    if best is None or size > best[0] or (size == best[0] and (qi, ti) < (best[1], best[2])):
                        best = candidate
                    break
    if best is None:
        return {"length": 0, "query_indices": [], "target_indices": [], "roots": []}
    return {"length": best[0], "query_indices": list(best[1]), "target_indices": list(best[2]),
            "roots": [QUERY[i] for i in best[1]]}


def load_freeze() -> dict[str, object]:
    freeze, _ = strict_json(FREEZE)
    expected_paths = (SPEC, CALIBRATION, CAL_VALIDATION, SOURCE, Path(__file__).resolve(), VALIDATOR)
    expected_inputs = {str(path.relative_to(ROOT)): sha(path) for path in expected_paths}
    expected_outputs = [str(path.relative_to(ROOT)) for path in (OUT, REPORT, VAL_OUT, VAL_REPORT)]
    if freeze != {
        "experiment": "FPR001_F37V_ONE_SHOT_TARGET",
        "schema": "FPR001_F37V_ONE_SHOT_TARGET_FREEZE_V1",
        "status": "FROZEN_UNSCORED",
        "decision": "AUTHORIZE_EXACTLY_ONE_F37V_TARGET_RUN",
        "registration_commit": freeze.get("registration_commit"),
        "inputs": expected_inputs,
        "outputs_absent": expected_outputs,
        "query": list(QUERY),
        "target_page": "f37v",
        "background_pages_per_reading": 94,
        "lcs_threshold": 3,
        "rank_denominator": 95,
        "rank_ceiling": 0.02,
        "claim_ceiling": "Anonymous manuscript-internal ordered-root recurrence only; no translation.",
    }:
        raise RuntimeError("freeze schema or binding")
    if type(freeze["registration_commit"]) is not str or len(freeze["registration_commit"]) != 40:
        raise RuntimeError("registration commit")
    if any(path.exists() for path in (OUT, REPORT, VAL_OUT, VAL_REPORT)):
        raise RuntimeError("registered output already exists")
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    validation = json.loads(CAL_VALIDATION.read_text(encoding="utf-8"))
    if calibration["decision"] != "GO_FREEZE_ONE_SHOT_F37V_TARGET" or not all(calibration["gates"].values()):
        raise RuntimeError("calibration gate")
    if validation["status"] != "PASS_8_CHECK_INDEPENDENT_120_WORLD_RECONSTRUCTION":
        raise RuntimeError("calibration validation gate")
    return freeze


def build() -> tuple[dict[str, object], str]:
    freeze = load_freeze()
    background = {e: defaultdict(int) for e in EDITIONS}
    target_words: dict[str, list[dict[str, object]]] = {e: [] for e in EDITIONS}
    target_rows = 0
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            is_target = row["page"] == "f37v"
            if is_target:
                target_rows += 1
            if (row["section"], row["currier"], row["hand"], row["grammar_scope"]) != (
                "H", "A", "1", "CONFIRMED_PROSE"
            ):
                continue
            edition = row["edition"]
            roots = row["root_sequence"].split()
            surfaces = row["surface"].split()
            if len(roots) != len(surfaces):
                raise RuntimeError(("surface/root word count", row["locus"]))
            for index, (root_word, surface_word) in enumerate(zip(roots, surfaces)):
                atoms = tuple(root_word.split("+"))
                score = lcs(QUERY, atoms)
                if is_target:
                    target_words[edition].append({"locus": row["locus"], "word_index": index,
                                                  "surface_word": surface_word, "root_word": root_word,
                                                  "score": score, "witness": witness(atoms)})
                else:
                    background[edition][row["page"]] = max(background[edition][row["page"]], score)
    pages = sorted(set.intersection(*(set(background[e]) for e in EDITIONS)))
    if len(pages) != 94 or any(set(background[e]) != set(pages) for e in EDITIONS) or target_rows != 69:
        raise RuntimeError("registered geometry")
    scores = {e: max((int(item["score"]) for item in target_words[e]), default=-1) for e in EDITIONS}
    ranks = {e: 1 + sum(score >= scores[e] for score in background[e].values()) for e in EDITIONS}
    pooled_target = sum(scores.values())
    pooled_rank = 1 + sum(sum(background[e][page] for e in EDITIONS) >= pooled_target for page in pages)
    best = {e: [item for item in target_words[e] if item["score"] == scores[e]] for e in EDITIONS}
    gates = {
        "score_at_least_3_all_readings": all(scores[e] >= 3 for e in EDITIONS),
        "inclusive_rank_1_of_95_all_readings": all(ranks[e] == 1 for e in EDITIONS),
        "pooled_inclusive_rank_1_of_95": pooled_rank == 1,
        "all_readings_positive_agreement": all(scores[e] >= 3 and ranks[e] == 1 for e in EDITIONS),
        "all_rank_fractions_at_most_0_02": all(ranks[e] / 95 <= 0.02 for e in EDITIONS) and pooled_rank / 95 <= 0.02,
    }
    passed = all(gates.values())
    decision = ("PASS_ANONYMOUS_SAME_PLANT_ORDERED_ROOT_RECURRENCE" if passed
                else "FINAL_NONCONFIRMATION_FIFTH_RELATION_ORDERED_ROOT")
    result: dict[str, object] = {
        "experiment": "FPR001_F37V_ONE_SHOT_TARGET",
        "schema": "FPR001_F37V_ONE_SHOT_TARGET_RESULT_V1",
        "status": "PASS_ONE_SHOT_TARGET" if passed else "FINAL_ONE_SHOT_NONCONFIRMATION",
        "decision": decision,
        "query": list(QUERY),
        "target_page": "f37v",
        "target_rows": target_rows,
        "background_pages_per_reading": 94,
        "target_page_scores": scores,
        "inclusive_ranks": {e: {"rank": ranks[e], "denominator": 95, "fraction": ranks[e] / 95} for e in EDITIONS},
        "pooled": {"score_sum": pooled_target, "rank": pooled_rank, "denominator": 95, "fraction": pooled_rank / 95},
        "best_target_words": best,
        "gates": gates,
        "freeze_sha256": sha(FREEZE),
        "registration_commit": freeze["registration_commit"],
        "inputs": freeze["inputs"],
        "claim_ceiling": (
            "A pass establishes only anonymous ordered-root recurrence in one externally fixed same-plant relation. "
            "It does not establish a plant name, word, morpheme, sound, language, cipher, plaintext, meaning, or translation."
        ),
    }
    score_text = ", ".join(f"{e}={scores[e]} (rank {ranks[e]}/95)" for e in EDITIONS)
    report = (
        "# FPR001 f37v one-shot ordered-root target\n\n"
        f"Decision: **{decision}**.\n\n"
        f"The frozen f37v page scores are {score_text}; pooled rank is {pooled_rank}/95. "
        f"All five preregistered gates {'pass' if passed else 'do not all pass'}. The result file records every "
        "maximum-scoring target word and deterministic LCS witness.\n\n"
        "This is an anonymous manuscript-internal formal recurrence test. It supplies no plant name, word, sound, "
        "language, cipher, plaintext, meaning, or translation.\n"
    )
    return result, report


def install_pair(result: bytes, report: str) -> None:
    tmp = Path(tempfile.mkdtemp(prefix="fpr001_target_"))
    staged = (tmp / "result.json", tmp / "report.md")
    linked: list[Path] = []
    try:
        staged[0].write_bytes(result); staged[1].write_text(report, encoding="utf-8")
        for source, destination in zip(staged, (OUT, REPORT)):
            os.link(source, destination); linked.append(destination)
    except Exception:
        for path in linked:
            if path.exists() and path.stat().st_ino in {p.stat().st_ino for p in staged}:
                path.unlink()
        raise
    finally:
        for path in staged:
            if path.exists(): path.unlink()
        tmp.rmdir()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-sha256", required=True)
    args = parser.parse_args()
    if sha(FREEZE) != args.freeze_sha256:
        raise RuntimeError("freeze sha")
    result, report = build()
    install_pair(canonical(result), report)


if __name__ == "__main__":
    main()
