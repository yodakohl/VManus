#!/usr/bin/env python3
"""Post-hoc worth screen for f57v N1/D1 same-quality identity."""

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
PRIOR = BASE / "results/f57_quality_label_neighbors_report.md"
OUT = BASE / "results/f57_cross_register_quality_identity_worth.json"
REPORT = BASE / "results/f57_cross_register_quality_identity_worth_report.md"
EDITIONS = ("zl3b_clean", "it2a_clean", "rf1b_clean")
POSITIONS = ("HOT_NE", "MOIST_SE", "COLD_SW", "DRY_NW")
N1 = ("f57v.6", "f57v.7", "f57v.8", "f57v.9")
D1 = ("f57v.11", "f57v.12", "f57v.13", "f57v.10")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def distance(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for row_index, left_item in enumerate(left, 1):
        current = [row_index]
        for column_index, right_item in enumerate(right, 1):
            current.append(min(
                current[-1] + 1,
                previous[column_index] + 1,
                previous[column_index - 1] + (left_item != right_item),
            ))
        previous = current
    return previous[-1]


def transform(value: str, view: str) -> str:
    value = "".join(value.split())
    if view in {"REMOVE_TERMINAL_Y", "REMOVE_KNOWN_STATE_BITS"} and value.endswith("y"):
        value = value[:-1]
    if view == "REMOVE_KNOWN_STATE_BITS":
        if value.startswith("ot") or value.startswith("ok"):
            value = value[2:]
    return value


def similarity(left: str, right: str, view: str) -> Fraction:
    left = transform(left, view)
    right = transform(right, view)
    denominator = max(len(left), len(right), 1)
    return Fraction(denominator - distance(left, right), denominator)


def score(
    surfaces: dict[str, dict[str, str]],
    n1: tuple[str, ...],
    d1: tuple[str, ...],
    assignment: tuple[int, ...],
    view: str,
) -> tuple[Fraction, Fraction, tuple[Fraction, ...]]:
    by_edition = tuple(
        sum(
            (similarity(surfaces[n1[index]][edition], surfaces[d1[target]][edition], view)
             for index, target in enumerate(assignment)),
            Fraction(),
        )
        for edition in EDITIONS
    )
    return min(by_edition), sum(by_edition, Fraction()) / len(by_edition), by_edition


def number(value: Fraction) -> float:
    return round(float(value), 12)


def evaluate(
    surfaces: dict[str, dict[str, str]],
    view: str,
    omitted_index: int | None = None,
) -> dict[str, object]:
    retained = tuple(index for index in range(4) if index != omitted_index)
    n1 = tuple(N1[index] for index in retained)
    d1 = tuple(D1[index] for index in retained)
    identity = tuple(range(len(retained)))
    rows = []
    for assignment in itertools.permutations(range(len(retained))):
        minimum, mean, by_edition = score(surfaces, n1, d1, assignment, view)
        rows.append((minimum, mean, assignment, by_edition))
    observed = next(row for row in rows if row[2] == identity)
    better = sum((row[0], row[1]) > (observed[0], observed[1]) for row in rows)
    tied = sum((row[0], row[1]) == (observed[0], observed[1]) for row in rows)
    best = max(rows, key=lambda row: (row[0], row[1], tuple(-x for x in row[2])))
    return {
        "assignments": len(rows),
        "omitted_position": None if omitted_index is None else POSITIONS[omitted_index],
        "observed_minimum": number(observed[0]),
        "observed_mean": number(observed[1]),
        "observed_by_edition": {edition: number(value) for edition, value in zip(EDITIONS, observed[3], strict=True)},
        "strictly_better": better,
        "tied_with_observed": tied,
        "tie_inclusive_competition_rank": better + tied,
        "best_assignment_positions": [POSITIONS[retained[index]] for index in best[2]],
        "identity_is_unique_best": better == 0 and tied == 1,
    }


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    wanted = set(N1 + D1)
    surfaces: dict[str, dict[str, str]] = {}
    with LINES.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in wanted:
                surfaces[row["locus"]] = {edition: row[edition] for edition in EDITIONS}
    if set(surfaces) != wanted:
        raise SystemExit("incomplete f57v cross-register surface panel")

    raw = evaluate(surfaces, "RAW")
    deletions = [evaluate(surfaces, "RAW", index) for index in range(4)]
    terminal = evaluate(surfaces, "REMOVE_TERMINAL_Y")
    bits = evaluate(surfaces, "REMOVE_KNOWN_STATE_BITS")
    result = {
        "experiment": "F57_CROSS_REGISTER_QUALITY_IDENTITY_WORTH",
        "schema": "F57CRI_WORTH_V1",
        "status": "POSTHOC_LOCAL_MATCH_EXPLAINED_BY_KNOWN_STATE_BITS",
        "decision": "DO_NOT_PROMOTE_CROSS_REGISTER_LABEL_IDENTITY",
        "provenance": {
            "quality_phase_and_all_surfaces_exposed_before_test": True,
            "metric_inherited_from_published_f57_label_neighbour_inventory": (
                "sum of compact whole-surface normalized Levenshtein similarity; "
                "rank by weakest corresponding reading then three-reading mean"
            ),
            "alternate_readings_are_sensitivity_views_not_replications": True,
            "single_physical_folio": True,
        },
        "mapping": [
            {"position": position, "n1_locus": n1, "d1_locus": d1}
            for position, n1, d1 in zip(POSITIONS, N1, D1, strict=True)
        ],
        "raw": raw,
        "leave_one_pair_out": deletions,
        "ablations": {
            "remove_one_terminal_y_from_each_surface": terminal,
            "also_remove_one_leading_ot_or_ok_from_each_surface": bits,
        },
        "inputs": {
            str(LINES.relative_to(ROOT)): sha(LINES),
            str(PRIOR.relative_to(ROOT)): sha(PRIOR),
        },
        "claim_ceiling": (
            "The physical N1-to-D1 coordinate assignment is uniquely best under the already published raw surface "
            "metric and every one-pair deletion, but it falls to ninth after terminal-y removal and third after "
            "removing the known ot/ok/y state bits. This is post-hoc single-folio local consistency dominated by "
            "previously known coordinate features, not independent lexical identity and not a quality word, sound, "
            "language, cipher, plaintext, meaning, or translation."
        ),
    }
    if not raw["identity_is_unique_best"] or not all(row["identity_is_unique_best"] for row in deletions):
        raise SystemExit("unexpected raw assignment reconstruction")
    if terminal["tie_inclusive_competition_rank"] != 9 or bits["tie_inclusive_competition_rank"] != 3:
        raise SystemExit("unexpected ablation ranks")
    OUT.write_bytes(canonical(result))
    REPORT.write_text(
        "# f57v cross-register quality-identity worth screen\n\n"
        "Status: **POSTHOC_LOCAL_MATCH_EXPLAINED_BY_KNOWN_STATE_BITS**.\n\n"
        "The physical Hot–Moist–Cold–Dry N1→D1 assignment is uniquely best among all 24 assignments under the "
        "already published corresponding-reading normalized edit-similarity metric. It remains uniquely best in "
        "all four leave-one-pair-out views.\n\n"
        "That apparent support is not independent. Removing one terminal `y` where present drops the physical "
        "assignment to tie-inclusive rank **9/24**. Removing the already documented leading `ot`/`ok` and terminal "
        "`y` state bits leaves it at rank **3/24**. The raw optimum therefore largely re-detects the known local "
        "coordinate code instead of showing that both registers spell the same four values.\n\n"
        "This was post-hoc on one exposed folio. Do not promote it to a quality lexicon or translation.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
