#!/usr/bin/env python3
"""Independent compact reconstruction of the f75v tail-echo worth screen."""

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
ANN = BASE / "results/existing_human_exact_locus_annotations.tsv"
LINES = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
RESULT = BASE / "results/f67_tail_echo_f75v_transfer_worth.json"
REPORT = BASE / "results/f67_tail_echo_f75v_transfer_worth_report.md"
OUT = BASE / "results/f67_tail_echo_f75v_transfer_worth_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def overlap(a: str, b: str) -> int:
    n = 0
    while n < 4 and n < len(a) and n < len(b) and a[-1 - n] == b[-1 - n]:
        n += 1
    return n


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    pair_re = re.compile(r"Label L([1-9]|10), line ([12])\.")
    pairs: dict[int, dict[int, str]] = {}
    with ANN.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            match = pair_re.search(row["local_comment"])
            if row["page"] == "f75v" and row["unit"] == "N1" and match:
                pair, line = map(int, match.groups())
                pairs.setdefault(pair, {})[line] = row["locus"]
    wanted = {value for pair in pairs.values() for value in pair.values()}
    rows = {}
    with LINES.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in wanted:
                rows[row["locus"]] = row
    rebuilt = {}
    for edition in ("zl3b_clean", "it2a_clean", "rf1b_clean"):
        left = ["".join(rows[pairs[i][1]][edition].split()) for i in range(1, 11)]
        right = ["".join(rows[pairs[i][2]][edition].split()) for i in range(1, 11)]
        matrix = [[overlap(a, b) for b in right] for a in left]
        observed = sum(matrix[i][i] for i in range(10))
        scores = [sum(matrix[i][p[i]] for i in range(10)) for p in itertools.permutations(range(10))]
        rebuilt[edition] = {
            "observed_score": observed,
            "maximum_score": max(scores),
            "assignments": math.factorial(10),
            "strictly_greater": sum(score > observed for score in scores),
            "tied": sum(score == observed for score in scores),
            "tie_inclusive_upper_tail": sum(score >= observed for score in scores) / math.factorial(10),
            "physical_pair_scores": [matrix[i][i] for i in range(10)],
            "matrix": matrix,
        }
    checks = {
        "canonical_result": RESULT.read_bytes() == canonical(result),
        "ten_human_pairs": sorted(pairs) == list(range(1, 11)) and all(sorted(x) == [1, 2] for x in pairs.values()),
        "complete_three_reading_surface_rows": len(rows) == 20,
        "exact_input_hashes": result["inputs"] == {str(ANN.relative_to(ROOT)): sha(ANN), str(LINES.relative_to(ROOT)): sha(LINES)},
        "full_exhaustive_reconstruction": result["editions"] == rebuilt,
        "exact_observed_scores": all(view["observed_score"] == 4 for view in rebuilt.values()),
        "poor_assignment_tails": rebuilt["zl3b_clean"]["tie_inclusive_upper_tail"] > .7 and rebuilt["it2a_clean"]["tie_inclusive_upper_tail"] > .7 and rebuilt["rf1b_clean"]["tie_inclusive_upper_tail"] > .7,
        "postexposure_stop": result["provenance"]["target_surfaces_were_exposed_before_this_screen"] is True and result["status"] == "POSTHOC_WORTH_STOP_NO_TWO_LINE_TRANSFER",
        "report_and_ceiling": REPORT.exists() and all(word in result["claim_ceiling"] for word in ("word", "meaning", "translation")),
    }
    if not all(checks.values()):
        raise SystemExit({key: value for key, value in checks.items() if not value})
    OUT.write_bytes(canonical({
        "experiment": "F67_TAIL_ECHO_F75V_TRANSFER_WORTH_VALIDATION",
        "status": "PASS_9_CHECK_INDEPENDENT_EXHAUSTIVE_WORTH_STOP_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": list(checks),
        "source_result_sha256": sha(RESULT),
        "source_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms the exposed worth-screen arithmetic only and supplies no field, word, meaning, or translation.",
    }))


if __name__ == "__main__":
    main()
