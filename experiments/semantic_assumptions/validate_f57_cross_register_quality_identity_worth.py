#!/usr/bin/env python3
"""Independent compact reconstruction of the f57v cross-register worth screen."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
LINES = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
RESULT = BASE / "results/f57_cross_register_quality_identity_worth.json"
REPORT = BASE / "results/f57_cross_register_quality_identity_worth_report.md"
OUT = BASE / "results/f57_cross_register_quality_identity_worth_validation.json"
EDITIONS = ("zl3b_clean", "it2a_clean", "rf1b_clean")
POSITIONS = ("HOT_NE", "MOIST_SE", "COLD_SW", "DRY_NW")
N1 = ("f57v.6", "f57v.7", "f57v.8", "f57v.9")
D1 = ("f57v.11", "f57v.12", "f57v.13", "f57v.10")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def edit(left: str, right: str) -> int:
    row = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        nxt = [i]
        for j, b in enumerate(right, 1):
            nxt.append(min(nxt[-1] + 1, row[j] + 1, row[j - 1] + (a != b)))
        row = nxt
    return row[-1]


def clean(value: str, view: str) -> str:
    value = value.replace(" ", "")
    if view != "RAW" and value.endswith("y"):
        value = value[:-1]
    if view == "BITS" and value[:2] in {"ot", "ok"}:
        value = value[2:]
    return value


def sim(left: str, right: str, view: str) -> Fraction:
    left, right = clean(left, view), clean(right, view)
    size = max(len(left), len(right), 1)
    return Fraction(size - edit(left, right), size)


def ranking(surfaces: dict[str, dict[str, str]], view: str, omit: int | None) -> tuple[int, bool]:
    keep = [index for index in range(4) if index != omit]
    observed = tuple(range(len(keep)))
    rows = []
    for assignment in itertools.permutations(range(len(keep))):
        scores = []
        for edition in EDITIONS:
            scores.append(sum((sim(surfaces[N1[keep[i]]][edition], surfaces[D1[keep[target]]][edition], view)
                               for i, target in enumerate(assignment)), Fraction()))
        rows.append((min(scores), sum(scores, Fraction()) / 3, assignment))
    target = next(row for row in rows if row[2] == observed)
    better = sum(row[:2] > target[:2] for row in rows)
    tied = sum(row[:2] == target[:2] for row in rows)
    return better + tied, better == 0 and tied == 1


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    wanted = set(N1 + D1)
    surfaces = {}
    with LINES.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in wanted:
                surfaces[row["locus"]] = {edition: row[edition] for edition in EDITIONS}
    raw_rank, raw_unique = ranking(surfaces, "RAW", None)
    deletion = [ranking(surfaces, "RAW", index) for index in range(4)]
    terminal_rank, terminal_unique = ranking(surfaces, "Y", None)
    bits_rank, bits_unique = ranking(surfaces, "BITS", None)
    checks = {
        "canonical_result": RESULT.read_bytes() == canonical(stored),
        "complete_eight_locus_panel": set(surfaces) == wanted,
        "exact_coordinate_order": [(row["position"], row["n1_locus"], row["d1_locus"]) for row in stored["mapping"]]
            == list(zip(POSITIONS, N1, D1, strict=True)),
        "raw_identity_unique_best": (raw_rank, raw_unique) == (1, True),
        "all_four_deletions_unique_best": deletion == [(1, True)] * 4,
        "terminal_y_ablation_rank_nine": (terminal_rank, terminal_unique) == (9, False),
        "known_bits_ablation_rank_three": (bits_rank, bits_unique) == (3, False),
        "stored_rank_summary_matches": stored["raw"]["tie_inclusive_competition_rank"] == raw_rank
            and [row["tie_inclusive_competition_rank"] for row in stored["leave_one_pair_out"]] == [1] * 4
            and stored["ablations"]["remove_one_terminal_y_from_each_surface"]["tie_inclusive_competition_rank"] == terminal_rank
            and stored["ablations"]["also_remove_one_leading_ot_or_ok_from_each_surface"]["tie_inclusive_competition_rank"] == bits_rank,
        "posthoc_nonlexical_stop": stored["status"] == "POSTHOC_LOCAL_MATCH_EXPLAINED_BY_KNOWN_STATE_BITS"
            and stored["provenance"]["quality_phase_and_all_surfaces_exposed_before_test"] is True,
        "report_and_ceiling": REPORT.exists() and all(word in stored["claim_ceiling"] for word in ("word", "meaning", "translation")),
    }
    if not all(checks.values()):
        raise SystemExit({key: value for key, value in checks.items() if not value})
    OUT.write_bytes(canonical({
        "experiment": "F57_CROSS_REGISTER_QUALITY_IDENTITY_WORTH_VALIDATION",
        "status": "PASS_10_CHECK_INDEPENDENT_ORBIT_AND_ABLATION_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": list(checks),
        "source_result_sha256": sha(RESULT),
        "source_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only the post-hoc local assignment and ablation arithmetic; it supplies no quality word, meaning, or translation.",
    }))


if __name__ == "__main__":
    main()
