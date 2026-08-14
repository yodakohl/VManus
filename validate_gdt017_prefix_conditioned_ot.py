#!/usr/bin/env python3
"""Independent exact conditional validator for GDT017."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

from run_gdt013_latent_role_propagation import all_strict_groups

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt017_result.json"
VALIDATION = ROOT / "gdt017_validation.json"
PAIRS = (("ar", "otar"), ("al", "otal"), ("ol", "otol"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    ).encode()).hexdigest()


def read_tsv(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def distribution(n, k, m):
    denominator = math.comb(n, m)
    return {
        x: Fraction(math.comb(k, x) * math.comb(n-k, m-x), denominator)
        for x in range(max(0, m-(n-k)), min(m, k)+1)
    }


def exact(parts):
    dist = {0: Fraction(1)}
    observed = 0
    expected = Fraction()
    numerator = denominator = 0.0
    informative = ot_total = bare_total = outcome_total = 0
    for values in parts:
        n = len(values)
        m = sum(a for a, _ in values)
        k = sum(b for _, b in values)
        if not (0 < m < n and 0 < k < n):
            continue
        informative += 1
        overlap = sum(a and b for a, b in values)
        weight = m * (n-m) / n
        numerator += weight * (overlap/m - (k-overlap)/(n-m))
        denominator += weight
        observed += overlap
        expected += Fraction(m*k, n)
        ot_total += m
        bare_total += n-m
        outcome_total += k
        new = defaultdict(Fraction)
        for left, lp in dist.items():
            for right, rp in distribution(n, k, m).items():
                new[left+right] += lp*rp
        dist = new
    delta = abs(Fraction(observed)-expected)
    p = sum(probability for value, probability in dist.items()
            if abs(Fraction(value)-expected) >= delta) if denominator else Fraction(1)
    return numerator/denominator if denominator else 0.0, float(p), observed, float(expected), informative, ot_total, bare_total, outcome_total, len(dist)


def close(a, b):
    return abs(float(a)-float(b)) < 6e-12


def main():
    checks = []
    result = json.loads(RESULT.read_text())
    copy = dict(result)
    digest = copy.pop("result_content_sha256")
    checks += [("schema", result["schema"] == "GDT017_PREFIX_CONDITIONED_OT_RESULT_V1"),
               ("content", digest == canonical_sha(copy))]
    for part in ("inputs", "implementation", "outputs"):
        for name, expected in result[part].items():
            checks.append((part+":"+name, sha(ROOT/name) == expected))
    rows = [row for row in all_strict_groups() if row["grammar_scope"] == "CONFIRMED_PROSE"]
    by_line = defaultdict(list)
    for row in rows:
        by_line[row["locus"]].append(row)
    lookup = {host: (core, host == ot) for core, ot in PAIRS for host in (core, ot)}
    observations = []
    examples = []
    for locus, line in sorted(by_line.items()):
        line.sort(key=lambda row: row["group_index"])
        for index, row in enumerate(line):
            if row["residual_host"] not in lookup:
                continue
            core, is_ot = lookup[row["residual_host"]]
            position = ((row["group_index"]-1)/(row["group_count"]-1)
                        if row["group_count"] > 1 else .5)
            previous_dy = int(index > 0 and int(line[index-1]["dy_closure"]))
            observations.append({"core": core, "is_ot": is_ot, "page": row["page"],
                                 "bin": min(3, int(position*4)),
                                 "prefix": row["stripped_prefix"], "previous_dy": previous_dy})
            if is_ot and previous_dy:
                examples.append((locus, row["group_index"], row["stripped_prefix"],
                                 line[index-1]["token"], row["token"]))
    specs = (("POOLED_PREFIX_MATCHED", None, True), ("POOLED_NO_PREFIX", None, False),
             ("AR_OTAR_NO_PREFIX", "ar", False), ("AL_OTAL_NO_PREFIX", "al", False),
             ("OL_OTOL_NO_PREFIX", "ol", False))
    stored = {row["test"]: row for row in read_tsv("gdt017_prefix_conditioned_tests.tsv")}
    for name, core_filter, prefix_matched in specs:
        strata = defaultdict(list)
        for row in observations:
            if core_filter and row["core"] != core_filter:
                continue
            if not prefix_matched and row["prefix"] != "NONE":
                continue
            key = (row["core"], row["page"], row["bin"])
            if prefix_matched:
                key += (row["prefix"],)
            strata[key].append((row["is_ot"], row["previous_dy"]))
        values = exact(strata.values())
        row = stored[name]
        checks.append(("test:"+name,
            close(row["conditional_effect"], values[0]) and close(row["exact_p"], values[1])
            and int(row["observed_ot_previous_dy"]) == values[2]
            and close(row["expected_ot_previous_dy"], values[3])
            and int(row["informative_strata"]) == values[4]
            and int(row["informative_ot_groups"]) == values[5]
            and int(row["informative_bare_groups"]) == values[6]
            and int(row["stratum_previous_dy"]) == values[7]
            and int(row["exact_distribution_support"]) == values[8]))
    exported = read_tsv("gdt017_transition_examples.tsv")
    exported_keys = [(row["locus"], int(row["group_index"]), row["target_prefix"],
                      row["previous_token"], row["target_token"]) for row in exported]
    checks += [
        ("corpus", len(rows) == result["strict_prose_groups"] == 15592),
        ("candidate_count", len(observations) == result["candidate_observations"]),
        ("examples_exact", exported_keys == examples and len(examples) == result["dy_to_ot_examples"] == 62),
        ("prefix_counts", dict(sorted(Counter(value[2] for value in examples).items())) == result["target_prefix_counts"]),
        ("f84", not any(row["locus"].startswith("f84r") for row in rows)
         and result["f84r"] == {"retained": False, "joined": False, "scored": False}),
        ("ledger", (ROOT/"GDT002_YOLO_LEDGER.tsv").read_text().count("GDT017_CKPT001") == 1),
    ]
    report = (ROOT/"GDT017_PREFIX_CONDITIONED_OT_REPORT.md").read_text().lower()
    checks += [("claim", all(term in report for term in
                              ("not only", "no word", "no-prefix", "f84r was excluded")))]
    failures = [name for name, ok in checks if not ok]
    validation = {
        "schema": "GDT017_PREFIX_CONDITIONED_OT_VALIDATION_V1",
        "status": "PASS" if not failures else "FAIL", "checks": len(checks),
        "failures": failures, "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independent reconstruction of all exact-host observations, 62 previous-DY examples, prefix counts, five exact conditional distributions, hashes, f84 exclusion, ledger, and claims. Reuses the separately validated strict-group loader.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True)+"\n")
    print(json.dumps(validation, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
