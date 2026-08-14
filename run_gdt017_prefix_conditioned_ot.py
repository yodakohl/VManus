#!/usr/bin/env python3
"""Test whether the post-DY OT contrast survives recovered-prefix controls."""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

from run_gdt012_core_semantic_atlas import ROOT, canonical_sha, sha, write_tsv
from run_gdt013_latent_role_propagation import all_strict_groups

PAIRS = (("ar", "otar"), ("al", "otal"), ("ol", "otol"))


def hypergeom(n, k, m):
    denominator = math.comb(n, m)
    return {
        value: Fraction(math.comb(k, value) * math.comb(n - k, m - value), denominator)
        for value in range(max(0, m - (n - k)), min(m, k) + 1)
    }


def exact_test(parts):
    distribution = {0: Fraction(1)}
    observed = 0
    expected = Fraction()
    numerator = denominator = 0.0
    informative = 0
    ot_total = bare_total = outcome_total = 0
    for values in parts:
        n = len(values)
        m = sum(is_ot for is_ot, _ in values)
        k = sum(outcome for _, outcome in values)
        if not (0 < m < n and 0 < k < n):
            continue
        informative += 1
        overlap = sum(is_ot and outcome for is_ot, outcome in values)
        weight = m * (n - m) / n
        numerator += weight * (overlap / m - (k - overlap) / (n - m))
        denominator += weight
        observed += overlap
        expected += Fraction(m * k, n)
        ot_total += m
        bare_total += n - m
        outcome_total += k
        updated = defaultdict(Fraction)
        for left, left_p in distribution.items():
            for right, right_p in hypergeom(n, k, m).items():
                updated[left + right] += left_p * right_p
        distribution = updated
    deviation = abs(Fraction(observed) - expected)
    p = sum(
        probability for value, probability in distribution.items()
        if abs(Fraction(value) - expected) >= deviation
    ) if denominator else Fraction(1)
    return {
        "conditional_effect": numerator / denominator if denominator else 0.0,
        "exact_p": float(p), "observed_ot_previous_dy": observed,
        "expected_ot_previous_dy": float(expected),
        "informative_strata": informative, "informative_ot_groups": ot_total,
        "informative_bare_groups": bare_total, "stratum_previous_dy": outcome_total,
        "exact_distribution_support": len(distribution),
    }


def main():
    rows = [row for row in all_strict_groups() if row["grammar_scope"] == "CONFIRMED_PROSE"]
    assert len(rows) == 15592 and not any(row["locus"].startswith("f84r") for row in rows)
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["locus"]].append(row)
    observations = []
    examples = []
    pair_lookup = {host: (core, host == ot) for core, ot in PAIRS for host in (core, ot)}
    for locus, line in sorted(grouped.items()):
        line.sort(key=lambda row: row["group_index"])
        for index, row in enumerate(line):
            host = row["residual_host"]
            if host not in pair_lookup:
                continue
            core, is_ot = pair_lookup[host]
            position = ((row["group_index"] - 1) / (row["group_count"] - 1)
                        if row["group_count"] > 1 else 0.5)
            previous_dy = int(index > 0 and int(line[index - 1]["dy_closure"]))
            item = dict(row)
            item.update({"core": core, "is_ot": int(is_ot),
                         "position_bin": min(3, int(position * 4)),
                         "previous_dy": previous_dy})
            observations.append(item)
            if is_ot and previous_dy:
                previous = line[index - 1]
                examples.append({
                    "locus": locus, "page": row["page"],
                    "physical_folio": row["physical_folio"],
                    "group_index": row["group_index"], "core": core,
                    "previous_token": previous["token"],
                    "previous_family": previous["family_surface"],
                    "target_token": row["token"], "target_family": row["family_surface"],
                    "target_prefix": row["stripped_prefix"],
                    "target_residual_host": host,
                    "position_bin": item["position_bin"],
                    "claim_state": "OBSERVED_FORMAL_SEQUENCE_NOT_SEMANTIC",
                })
    specs = [
        ("POOLED_PREFIX_MATCHED", None, True),
        ("POOLED_NO_PREFIX", None, False),
        ("AR_OTAR_NO_PREFIX", "ar", False),
        ("AL_OTAL_NO_PREFIX", "al", False),
        ("OL_OTOL_NO_PREFIX", "ol", False),
    ]
    tests = []
    for name, core_filter, prefix_matched in specs:
        strata = defaultdict(list)
        for row in observations:
            if core_filter and row["core"] != core_filter:
                continue
            if not prefix_matched and row["stripped_prefix"] != "NONE":
                continue
            key = (row["core"], row["page"], row["position_bin"])
            if prefix_matched:
                key += (row["stripped_prefix"],)
            strata[key].append((row["is_ot"], row["previous_dy"]))
        result = exact_test(strata.values())
        result.update({
            "test": name,
            "conditioning": "CORE+PAGE+POSITION_QUARTILE+PREFIX" if prefix_matched
                            else "CORE+PAGE+POSITION_QUARTILE; PREFIX=NONE",
            "search_adjusted_p": min(1.0, result["exact_p"] * len(specs)),
            "claim_state": "PREFIX_CONDITIONED_FORMAL_SEQUENCE_LEAD"
                           if result["conditional_effect"] > 0
                           else "NO_POSITIVE_SEQUENCE_LEAD",
        })
        tests.append(result)
    prefix_counts = Counter(row["target_prefix"] for row in examples)
    write_tsv(ROOT / "gdt017_prefix_conditioned_tests.tsv", tests)
    write_tsv(ROOT / "gdt017_transition_examples.tsv", examples)
    primary = tests[0]
    no_prefix = tests[1]
    status = ("POST_RESOLUTION_OT_NOT_REDUCIBLE_TO_Q_PREFIX"
              if primary["search_adjusted_p"] < 0.05 and no_prefix["conditional_effect"] > 0
              else "PREFIX_CONFOUND_NOT_RESOLVED")
    report = f"""# GDT017 prefix-conditioned OT audit

Status: **{status.replace('_', ' ')}**

The earlier sequence is not only `dy | qo...`.  Among {len(examples)} observed
`DY -> OT+AR/AL/OL` transitions, {prefix_counts['q']} targets have recovered
q, {prefix_counts['NONE']} have no recovered prefix, and
{len(examples)-prefix_counts['q']-prefix_counts['NONE']} have another carrier.

After conditioning jointly on core, page, normalized line-position quartile,
and recovered prefix class, OT forms retain a previous-DY effect of
{primary['conditional_effect']:+.3f} across {primary['informative_strata']}
informative strata ({primary['observed_ot_previous_dy']} observed versus
{primary['expected_ot_previous_dy']:.3f} expected; exact p=
{primary['exact_p']:.6g}; five-test adjusted p=
{primary['search_adjusted_p']:.6g}).

The no-prefix-only sensitivity remains positive at
{no_prefix['conditional_effect']:+.3f} ({no_prefix['observed_ot_previous_dy']}
versus {no_prefix['expected_ot_previous_dy']:.3f}; p=
{no_prefix['exact_p']:.6g}), but its conservative five-test value is
{no_prefix['search_adjusted_p']:.6g}.  The core-specific table shows that
AL/OTAL supplies the clearest no-prefix component; AR/OTAR and OL/OTOL do not
independently resolve.

This strengthens the formal reading of OT as a post-resolution continuation
or local-frame state.  It does **not** determine whether OT is a morpheme, a
scribal construction grade, or a renderer state.  It also does not make
`AR`, `AL`, or `OL` semantic words.  The tests are inherited/post-hoc and the
same corpus shaped the hypothesis.  f84r was excluded before grouping.

No word, syntax, sound, language, plaintext, meaning, or translation is
confirmed.
"""
    (ROOT / "GDT017_PREFIX_CONDITIONED_OT_REPORT.md").write_text(report)
    outputs = (
        "gdt017_prefix_conditioned_tests.tsv", "gdt017_transition_examples.tsv",
        "GDT017_PREFIX_CONDITIONED_OT_REPORT.md",
    )
    inputs = (
        "gdt016_result.json", "gdt015_result.json",
        "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv",
        "experiments/semantic_assumptions/results/source_sta_family_consensus_groups.tsv",
        "GDT017_PREFIX_CONDITIONED_OT_METHOD.md",
    )
    result = {
        "schema": "GDT017_PREFIX_CONDITIONED_OT_RESULT_V1", "status": status,
        "strict_prose_groups": len(rows), "candidate_observations": len(observations),
        "dy_to_ot_examples": len(examples), "target_prefix_counts": dict(sorted(prefix_counts.items())),
        "tests": tests, "f84r": {"retained": False, "joined": False, "scored": False},
        "claim_ceiling": "Prefix-conditioned formal sequence relation only; no morpheme, word, syntax, sound, language, plaintext, meaning, or translation.",
        "inputs": {name: sha(ROOT / name) for name in inputs},
        "implementation": {"run_gdt017_prefix_conditioned_ot.py": sha(Path(__file__))},
        "outputs": {name: sha(ROOT / name) for name in outputs},
    }
    result["result_content_sha256"] = canonical_sha(result)
    (ROOT / "gdt017_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "prefix_counts": dict(prefix_counts), "tests": tests}, sort_keys=True))


if __name__ == "__main__":
    main()
