#!/usr/bin/env python3
"""Independent reconstruction of the f77r residual-form assignment result.

This module intentionally imports no production experiment code.
"""

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
RESULT = Path("experiments/semantic_assumptions/results/f77r_residual_form_assignment.json")
DESIGN = Path(
    "experiments/semantic_assumptions/f77r_quality_transition_bridge/"
    "RESIDUAL_FORM_ASSIGNMENT_DESIGN.md"
)
AUDIT = Path(
    "experiments/semantic_assumptions/f77r_quality_transition_bridge/"
    "audit_f77r_residual_form_assignment.py"
)
INTERLINEAR = Path("experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv")
F57_PRIOR = Path("experiments/semantic_assumptions/results/f57_quality_label_neighbors.json")
F77_PRIOR = Path("experiments/semantic_assumptions/results/f77r_quality_transition_bridge.json")
EDITIONS = ("ZL3b", "IT2a", "RF1b")
STATES = ("HOT", "MOIST", "COLD", "DRY")
LOCI = tuple(f"f77r.{number}" for number in range(2, 8))
DELETIONS = ("f77r.2", "f77r.7", "f77r.4", "f77r.5")
BITS_TO_STATE = {"10": "HOT", "01": "MOIST", "00": "COLD", "11": "DRY"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize(surface: str) -> str:
    value = surface.replace(" ", "")
    if value[:2] == "ot":
        value = value[2:]
    if value[-1:] == "y":
        value = value[:-1]
    return value


def state_from_surface(surface: str) -> str:
    value = surface.replace(" ", "")
    bits = f"{int(value[:2] == 'ot')}{int(value[-1:] == 'y')}"
    return BITS_TO_STATE[bits]


def edit_distance(a: str, b: str) -> int:
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        next_row = [i]
        for j, y in enumerate(b, 1):
            next_row.append(min(next_row[j - 1] + 1, row[j] + 1, row[j - 1] + (x != y)))
        row = next_row
    return row[-1]


def sim(a: str, b: str) -> Fraction:
    size = max(len(a), len(b))
    return Fraction(1) if size == 0 else Fraction(size - edit_distance(a, b), size)


def avg(values: list[Fraction]) -> Fraction:
    assert values
    return sum(values, Fraction()) / len(values)


def encoded(value: Fraction) -> dict[str, object]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": f"{float(value):.12f}",
    }


def code(mapping: dict[str, str]) -> str:
    return "|".join(f"{state}<-{mapping[state]}" for state in STATES)


def all_scores(
    exemplars: dict[str, dict[str, str]], rows: list[dict[str, str]]
) -> tuple[dict[str, dict[str, Fraction]], dict[str, Fraction]]:
    per_reading = {edition: {} for edition in EDITIONS}
    joint = {}
    for perm in itertools.permutations(STATES):
        mapping = dict(zip(STATES, perm, strict=True))
        label = code(mapping)
        edition_values = []
        for edition in EDITIONS:
            state_values = []
            for target_state in STATES:
                source = normalize(exemplars[mapping[target_state]][edition])
                targets = [
                    normalize(row["surface"])
                    for row in rows
                    if row["edition"] == edition and row["state"] == target_state
                ]
                state_values.append(avg([sim(source, target) for target in targets]))
            value = avg(state_values)
            per_reading[edition][label] = value
            edition_values.append(value)
        joint[label] = avg(edition_values)
    return per_reading, joint


def rank(scores: dict[str, Fraction]) -> dict[str, object]:
    identity = code({state: state for state in STATES})
    observed = scores[identity]
    maximum = max(scores.values())
    higher = sum(value > observed for value in scores.values())
    tied = sum(value == observed for value in scores.values())
    return {
        "assignment_space": 24,
        "observed_mapping": identity,
        "observed_score": encoded(observed),
        "strictly_greater": higher,
        "exactly_equal_including_observed": tied,
        "inclusive_rank": higher + 1,
        "unique_optimum": higher == 0 and tied == 1,
        "maximum_score": encoded(maximum),
        "maximum_mappings": sorted(key for key, value in scores.items() if value == maximum),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = read_json(ROOT / RESULT)
    f57_prior = read_json(ROOT / F57_PRIOR)
    f77_prior = read_json(ROOT / F77_PRIOR)
    interlinear = read_tsv(ROOT / INTERLINEAR)
    checks: list[str] = []

    expected_bindings = {
        str(path): sha256(ROOT / path)
        for path in (DESIGN, INTERLINEAR, F57_PRIOR, F77_PRIOR)
    }
    assert result["inputs"] == expected_bindings
    assert result["implementation_sha256"] == sha256(ROOT / AUDIT)
    checks.append("all input and implementation hashes")

    by_key = {(row["edition"], row["locus"]): row for row in interlinear}
    assert len(by_key) == len(interlinear)
    checks.append("unique interlinear edition-locus keys")

    exemplar_loci = {}
    exemplars: dict[str, dict[str, str]] = defaultdict(dict)
    for state in STATES:
        entry = f57_prior["targets"][f"{state}_POSITION"]
        locus = entry["target_locus"]
        exemplar_loci[state] = locus
        for edition in EDITIONS:
            surface = by_key[(edition, locus)]["surface"]
            assert surface == entry["target_surfaces"][edition]
            assert state_from_surface(surface) == state
            exemplars[state][edition] = surface
    assert result["exemplar_loci"] == exemplar_loci
    assert result["exemplar_surfaces"] == exemplars
    checks.extend(["four prior exemplar identities", "exemplar transcription bindings", "exemplar bit states"])

    prior_rows = {
        (row["edition"], row["locus"]): row
        for row in f77_prior["target_rows"]
        if row["edition"] in EDITIONS and row["locus"] in LOCI
    }
    assert set(prior_rows) == {(edition, locus) for edition in EDITIONS for locus in LOCI}
    rows = []
    expected_target_rows = []
    for edition in EDITIONS:
        for locus in LOCI:
            prior = prior_rows[(edition, locus)]
            surface = by_key[(edition, locus)]["surface"]
            state = prior["f57_page_role_state"]
            assert surface == prior["surface"]
            assert state_from_surface(surface) == state
            row = {"edition": edition, "locus": locus, "state": state, "surface": surface}
            rows.append(row)
            source_surface = exemplars[state][edition]
            expected_target_rows.append(
                {
                    **row,
                    "source_locus": exemplar_loci[state],
                    "source_surface": source_surface,
                    "source_residual": normalize(source_surface),
                    "target_residual": normalize(surface),
                    "similarity": encoded(sim(normalize(source_surface), normalize(surface))),
                }
            )
    assert result["target_rows"] == expected_target_rows
    checks.extend(["exact 18-row f77 scope", "f77 prior/transcription bindings", "f77 bit states", "all residual row similarities"])

    per_reading, joint = all_scores(exemplars, rows)
    expected_rankings = {edition: rank(per_reading[edition]) for edition in EDITIONS}
    expected_rankings["JOINT"] = rank(joint)
    assert result["full_rankings"] == expected_rankings
    checks.extend(["all 72 reading-specific scores", "all 24 joint scores", "tie-aware full rankings"])

    expected_score_table = [
        {"mapping": label, "score": encoded(value)} for label, value in sorted(joint.items())
    ]
    assert result["joint_assignment_scores"] == expected_score_table
    checks.append("complete joint score table")

    expected_deletions = []
    for locus in DELETIONS:
        reduced = [row for row in rows if row["locus"] != locus]
        assert {row["state"] for row in reduced if row["edition"] == "ZL3b"} == set(STATES)
        _, reduced_joint = all_scores(exemplars, reduced)
        expected_deletions.append({"deleted_locus": locus, **rank(reduced_joint)})
    assert result["deletion_results"] == expected_deletions
    checks.extend(["four valid duplicated-state deletions", "all 96 deletion scores", "tie-aware deletion rankings"])

    assert expected_rankings["JOINT"]["strictly_greater"] == 3
    assert expected_rankings["JOINT"]["exactly_equal_including_observed"] == 1
    assert expected_rankings["JOINT"]["maximum_mappings"] == [
        "HOT<-MOIST|MOIST<-HOT|COLD<-COLD|DRY<-DRY"
    ]
    assert expected_deletions[0]["deleted_locus"] == "f77r.2"
    assert expected_deletions[0]["inclusive_rank"] == 18
    checks.extend(["observed joint rank 4 of 24", "HOT-MOIST swap unique joint optimum", "f77r.2 deletion rank collapse"])

    assert result["decision"] == {
        "status": "FINAL_POSTHOC_NONCONFIRMATION_OF_RESIDUAL_FORM_IDENTITY",
        "full_joint_identity_unique_optimum": False,
        "all_four_deletions_identity_unique_optimum": False,
        "retain": "the prior f57-to-f77r two-bit structural transition bridge only",
        "reject": "independent residual lexical quality identity under the fixed complete-surface normalization and state-balanced edit score",
        "forbid": "no alternative winning assignment, quality gloss, element gloss, affix meaning, label meaning, plaintext, language, or translation",
    }
    assert not any("p_value" in key for key in result for _ in (0,))
    checks.extend(["decision reconstruction", "post-hoc no-p-value ceiling"])

    validation = {
        "status": "PASS_INDEPENDENT_RESIDUAL_ASSIGNMENT_RECONSTRUCTION",
        "imports_production_code": False,
        "result_sha256": sha256(ROOT / RESULT),
        "audit_implementation_sha256": sha256(ROOT / AUDIT),
        "check_count": len(checks),
        "checks": checks,
        "reconstructed_assignment_evaluations": 24 * (3 + 1) + 4 * 24 * (3 + 1),
        "decision": result["decision"]["status"],
    }
    serialized = json.dumps(validation, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
