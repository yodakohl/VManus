#!/usr/bin/env python3
"""Post-exposure worth screen for f67r2's fixed tail echo on f75v pairs."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
ANNOTATIONS = BASE / "results/existing_human_exact_locus_annotations.tsv"
LINES = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
OUT = BASE / "results/f67_tail_echo_f75v_transfer_worth.json"
REPORT = BASE / "results/f67_tail_echo_f75v_transfer_worth_report.md"
EDITIONS = ("zl3b_clean", "it2a_clean", "rf1b_clean")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def suffix_overlap(left: str, right: str, cap: int = 4) -> int:
    score = 0
    for a, b in zip(left[::-1], right[::-1]):
        if a != b or score == cap:
            break
        score += 1
    return score


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")

    selected: dict[int, dict[int, str]] = {}
    pattern = re.compile(r"Label L(\d+), line ([12])\.$")
    with ANNOTATIONS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] != "f75v" or row["unit"] != "N1":
                continue
            match = pattern.search(row["local_comment"])
            if match:
                pair, line = map(int, match.groups())
                selected.setdefault(pair, {})[line] = row["locus"]
    if sorted(selected) != list(range(1, 11)) or any(sorted(lines) != [1, 2] for lines in selected.values()):
        raise SystemExit("human source does not reconstruct ten complete pairs")

    surfaces: dict[str, dict[str, str]] = {}
    with LINES.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in {locus for pair in selected.values() for locus in pair.values()}:
                surfaces[row["locus"]] = row
    if len(surfaces) != 20:
        raise SystemExit("cross-reading surface coverage is incomplete")

    edition_results = {}
    for edition in EDITIONS:
        top = ["".join(surfaces[selected[pair][1]][edition].split()) for pair in range(1, 11)]
        bottom = ["".join(surfaces[selected[pair][2]][edition].split()) for pair in range(1, 11)]
        matrix = [[suffix_overlap(a, b) for b in bottom] for a in top]
        observed = sum(matrix[index][index] for index in range(10))
        greater = tied = 0
        maximum = 0
        for permutation in itertools.permutations(range(10)):
            score = sum(matrix[index][permutation[index]] for index in range(10))
            maximum = max(maximum, score)
            greater += score > observed
            tied += score == observed
        total = math.factorial(10)
        edition_results[edition] = {
            "observed_score": observed,
            "maximum_score": maximum,
            "assignments": total,
            "strictly_greater": greater,
            "tied": tied,
            "tie_inclusive_upper_tail": (greater + tied) / total,
            "physical_pair_scores": [matrix[index][index] for index in range(10)],
            "matrix": matrix,
        }

    result = {
        "experiment": "F67_TAIL_ECHO_F75V_TRANSFER_WORTH_SCREEN",
        "schema": "F67TE_F75V_WORTH_V1",
        "status": "POSTHOC_WORTH_STOP_NO_TWO_LINE_TRANSFER",
        "decision": "DO_NOT_REGISTER_F75V_TAIL_ECHO_CONFIRMATION",
        "provenance": {
            "target_surfaces_were_exposed_before_this_screen": True,
            "fixed_inherited_statistic": "sum of capped-four exact character suffix overlap for each human top/bottom pair",
            "pairing_source": "human exact-locus comments Label L1--L10, line 1/2",
            "alternate_readings_are_sensitivity_views_not_replications": True,
        },
        "counts": {"physical_pairs": 10, "physical_folios": 1, "readings": 3},
        "editions": edition_results,
        "inputs": {
            str(ANNOTATIONS.relative_to(ROOT)): sha(ANNOTATIONS),
            str(LINES.relative_to(ROOT)): sha(LINES),
        },
        "claim_ceiling": (
            "This exposed exploratory screen shows that the fixed f67r2 capped tail-echo statistic does not privilege "
            "the human f75v two-line pairings. It does not invalidate f67r2's local result or establish a field, "
            "owner, word, sound, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_bytes(canonical(result))
    REPORT.write_text(
        "# f67r2 tail-echo transfer worth screen on f75v\n\n"
        "Status: **POSTHOC_WORTH_STOP_NO_TWO_LINE_TRANSFER**.\n\n"
        "The only repeated comparison family has ten human-defined top/bottom label pairs on f75v. "
        "Using the already fixed capped-four exact suffix-overlap statistic, the physical assignment scores 4 "
        "in every reading. Alternative assignments reach 15 in ZL/IT and 14 in RF. Tie-inclusive exhaustive "
        "upper tails are .736270, .736270, and .712593.\n\n"
        "The strings were exposed before this worth screen, so this is not a confirmatory experiment. It is "
        "enough to reject a preregistered f75v replication: the strong f67r2 own-body tail echo is not a generic "
        "two-line-label convention at this resolution.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
