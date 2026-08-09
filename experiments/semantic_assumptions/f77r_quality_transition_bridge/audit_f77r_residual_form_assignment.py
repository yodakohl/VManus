#!/usr/bin/env python3
"""Enumerate residual f57-to-f77r state-form assignments exactly."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/f77r_quality_transition_bridge")
DESIGN = BASE / "RESIDUAL_FORM_ASSIGNMENT_DESIGN.md"
INTERLINEAR = Path("experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv")
F57_PRIOR = Path("experiments/semantic_assumptions/results/f57_quality_label_neighbors.json")
F77_PRIOR = Path("experiments/semantic_assumptions/results/f77r_quality_transition_bridge.json")
EDITIONS = ("ZL3b", "IT2a", "RF1b")
STATES = ("HOT", "MOIST", "COLD", "DRY")
OBSERVED = {state: state for state in STATES}
DELETIONS = ("f77r.2", "f77r.7", "f77r.4", "f77r.5")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def residual(surface: str) -> str:
    value = "".join(surface.split())
    if value.startswith("ot"):
        value = value[2:]
    if value.endswith("y"):
        value = value[:-1]
    return value


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, 1):
        current = [i]
        for j, right_char in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (left_char != right_char),
                )
            )
        previous = current
    return previous[-1]


def similarity(left: str, right: str) -> Fraction:
    denominator = max(len(left), len(right))
    if denominator == 0:
        return Fraction(1, 1)
    return Fraction(denominator - levenshtein(left, right), denominator)


def mean(values: list[Fraction]) -> Fraction:
    if not values:
        raise ValueError("empty exact mean")
    return sum(values, Fraction()) / len(values)


def frac(value: Fraction) -> dict[str, object]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": f"{float(value):.12f}",
    }


def mapping_code(mapping: dict[str, str]) -> str:
    return "|".join(f"{state}<-{mapping[state]}" for state in STATES)


def score(
    mapping: dict[str, str],
    edition: str,
    exemplars: dict[str, dict[str, str]],
    targets: list[dict[str, str]],
) -> Fraction:
    state_scores = []
    for target_state in STATES:
        source_state = mapping[target_state]
        source = residual(exemplars[source_state][edition])
        rows = [
            row
            for row in targets
            if row["edition"] == edition and row["state"] == target_state
        ]
        state_scores.append(
            mean([similarity(source, residual(row["surface"])) for row in rows])
        )
    return mean(state_scores)


def enumerate_scores(
    exemplars: dict[str, dict[str, str]],
    targets: list[dict[str, str]],
) -> tuple[dict[str, dict[str, Fraction]], dict[str, Fraction]]:
    by_edition: dict[str, dict[str, Fraction]] = {edition: {} for edition in EDITIONS}
    joint: dict[str, Fraction] = {}
    for permutation in itertools.permutations(STATES):
        mapping = dict(zip(STATES, permutation, strict=True))
        code = mapping_code(mapping)
        reading_scores = []
        for edition in EDITIONS:
            value = score(mapping, edition, exemplars, targets)
            by_edition[edition][code] = value
            reading_scores.append(value)
        joint[code] = mean(reading_scores)
    return by_edition, joint


def ranking(scores: dict[str, Fraction]) -> dict[str, object]:
    observed_code = mapping_code(OBSERVED)
    observed = scores[observed_code]
    greater = sum(value > observed for value in scores.values())
    equal = sum(value == observed for value in scores.values())
    maximum = max(scores.values())
    winners = sorted(code for code, value in scores.items() if value == maximum)
    return {
        "assignment_space": len(scores),
        "observed_mapping": observed_code,
        "observed_score": frac(observed),
        "strictly_greater": greater,
        "exactly_equal_including_observed": equal,
        "inclusive_rank": greater + 1,
        "unique_optimum": greater == 0 and equal == 1,
        "maximum_score": frac(maximum),
        "maximum_mappings": winners,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    input_paths = [ROOT / DESIGN, ROOT / INTERLINEAR, ROOT / F57_PRIOR, ROOT / F77_PRIOR]
    interlinear = read_tsv(ROOT / INTERLINEAR)
    with (ROOT / F57_PRIOR).open(encoding="utf-8") as handle:
        f57_prior = json.load(handle)
    with (ROOT / F77_PRIOR).open(encoding="utf-8") as handle:
        f77_prior = json.load(handle)

    by_key = {(row["edition"], row["locus"]): row for row in interlinear}
    if len(by_key) != len(interlinear):
        raise ValueError("duplicate edition/locus in interlinear")

    exemplars: dict[str, dict[str, str]] = defaultdict(dict)
    exemplar_loci: dict[str, str] = {}
    for state in STATES:
        prior = f57_prior["targets"][f"{state}_POSITION"]
        locus = prior["target_locus"]
        exemplar_loci[state] = locus
        for edition in EDITIONS:
            surface = by_key[(edition, locus)]["surface"]
            if surface != prior["target_surfaces"][edition]:
                raise ValueError(f"f57 prior/interlinear drift at {edition} {locus}")
            exemplars[state][edition] = surface

    targets = []
    seen = set()
    for row in f77_prior["target_rows"]:
        edition = row["edition"]
        locus = row["locus"]
        if edition not in EDITIONS or locus not in {f"f77r.{number}" for number in range(2, 8)}:
            continue
        key = (edition, locus)
        if key in seen:
            raise ValueError(f"duplicate f77 prior target {key}")
        seen.add(key)
        if by_key[key]["surface"] != row["surface"]:
            raise ValueError(f"f77 prior/interlinear drift at {edition} {locus}")
        targets.append(
            {
                "edition": edition,
                "locus": locus,
                "state": row["f57_page_role_state"],
                "surface": row["surface"],
            }
        )
    expected_keys = {(edition, f"f77r.{number}") for edition in EDITIONS for number in range(2, 8)}
    if seen != expected_keys or len(targets) != 18:
        raise ValueError("f77 prior target scope is not exact 3 x 6")

    by_edition_scores, joint_scores = enumerate_scores(exemplars, targets)
    full_ranking = {
        edition: ranking(by_edition_scores[edition]) for edition in EDITIONS
    }
    full_ranking["JOINT"] = ranking(joint_scores)

    deletion_results = []
    for locus in DELETIONS:
        reduced = [row for row in targets if row["locus"] != locus]
        _, deletion_joint = enumerate_scores(exemplars, reduced)
        deletion_results.append({"deleted_locus": locus, **ranking(deletion_joint)})

    observed_rows = []
    for target in sorted(targets, key=lambda row: (EDITIONS.index(row["edition"]), row["locus"])):
        source_surface = exemplars[target["state"]][target["edition"]]
        source_residual = residual(source_surface)
        target_residual = residual(target["surface"])
        observed_rows.append(
            {
                **target,
                "source_locus": exemplar_loci[target["state"]],
                "source_surface": source_surface,
                "source_residual": source_residual,
                "target_residual": target_residual,
                "similarity": frac(similarity(source_residual, target_residual)),
            }
        )

    full_unique = full_ranking["JOINT"]["unique_optimum"]
    deletion_unique = all(row["unique_optimum"] for row in deletion_results)
    decision = {
        "status": "FINAL_POSTHOC_NONCONFIRMATION_OF_RESIDUAL_FORM_IDENTITY",
        "full_joint_identity_unique_optimum": full_unique,
        "all_four_deletions_identity_unique_optimum": deletion_unique,
        "retain": "the prior f57-to-f77r two-bit structural transition bridge only",
        "reject": "independent residual lexical quality identity under the fixed complete-surface normalization and state-balanced edit score",
        "forbid": "no alternative winning assignment, quality gloss, element gloss, affix meaning, label meaning, plaintext, language, or translation",
    }
    if full_unique and deletion_unique:
        decision["status"] = "POSTHOC_RESIDUAL_FORM_SUPPORT_NOT_CONFIRMATION"

    result = {
        "status": "POSTHOC_EXACT_24_ASSIGNMENT_DIAGNOSTIC",
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in input_paths},
        "implementation_sha256": sha256(Path(__file__)),
        "normalization": "concatenate spaces; remove one leading ot; remove one terminal y",
        "score": "mean normalized Levenshtein similarity within target state, mean over four states, equal mean over three alternate readings",
        "alternate_reading_rule": "ZL3b IT2a RF1b are alternate readings of one manuscript and are averaged, not treated as independent samples",
        "states_are": "inherited f57 source-homology position names, not Voynich translations",
        "exemplar_loci": exemplar_loci,
        "exemplar_surfaces": exemplars,
        "target_rows": observed_rows,
        "full_rankings": full_ranking,
        "joint_assignment_scores": [
            {"mapping": code, "score": frac(value)}
            for code, value in sorted(joint_scores.items())
        ],
        "deletion_results": deletion_results,
        "decision": decision,
    }

    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
