#!/usr/bin/env python3
"""Independent exact reconstruction for GDT039."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
OCC = ROOT / "gdt039_terminal_m_occurrences.tsv"
TESTS = ROOT / "gdt039_family_tests.tsv"
SPEC = ROOT / "gdt039_specificity_tests.tsv"
RESULT = ROOT / "gdt039_result.json"
LEDGER = ROOT / "GDT002_YOLO_LEDGER.tsv"
VALIDATION = ROOT / "gdt039_validation.json"
DISCOVERY = {"f39", "f46", "f95", "f106", "f112"}
OUTCOMES = ("final_open_field", "physical_line_end", "open_physical_line_end")


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def target_section(row):
    if row["section"] == "H" and row["currier"] == "B":
        return "HB"
    if row["section"] == "S" and row["currier"] == "B":
        return "SB"
    return "OUT"


def reconstruct_lines(rows):
    grouped = defaultdict(list)
    for row in rows:
        assert not row["locus"].startswith("f84r")
        if target_section(row) in {"HB", "SB"} and row["physical_folio"] not in DISCOVERY:
            grouped[row["locus"]].append(row)
    lines = []
    for locus, line in grouped.items():
        line.sort(key=lambda row: int(row["group_index"]))
        count = int(line[0]["group_count"])
        if len(line) != count or {int(row["group_index"]) for row in line} != set(range(1, count + 1)):
            continue
        final_dy = max([-1] + [i for i, row in enumerate(line)
                              if row["record_state"] == "DY_RESOLUTION"])
        output = []
        for i, row in enumerate(line):
            output.append({**row, "target_section": target_section(row),
                "final_open_field": int(i > final_dy),
                "physical_line_end": int(i == count - 1),
                "open_physical_line_end": int(i == count - 1 and
                                               row["record_state"] != "DY_RESOLUTION")})
        lines.append(output)
    lines.sort(key=lambda line: line[0]["locus"])
    return lines


def hypergeom(n, successes, draws):
    denominator = math.comb(n, draws)
    lower, upper = max(0, draws - n + successes), min(successes, draws)
    return {hits: math.comb(successes, hits) * math.comb(n - successes, draws - hits) /
            denominator for hits in range(lower, upper + 1)}


def convolve(left, right):
    output = defaultdict(float)
    for a, p in left.items():
        for b, q in right.items():
            output[a + b] += p * q
    return dict(output)


def core_test(lines, predicate, outcome, base):
    pmf = {0: 1.0}
    observed = count = informative = 0
    for line in lines:
        pool = [row for row in line if base(row)]
        draws = sum(predicate(row) for row in pool)
        if not draws:
            continue
        successes = sum(int(row[outcome]) for row in pool)
        observed += sum(predicate(row) and int(row[outcome]) for row in pool)
        count += draws
        informative += int(0 < successes < len(pool))
        pmf = convolve(pmf, hypergeom(len(pool), successes, draws))
    expected = sum(value * probability for value, probability in pmf.items())
    return observed, count, expected, sum(probability for value, probability in pmf.items()
                                          if value >= observed), min(pmf), max(pmf), informative


def full_test(lines, predicate, outcome, base=lambda row: True):
    observed, count, expected, pvalue, low, high, informative = core_test(
        lines, predicate, outcome, base)
    folios = sorted({row["physical_folio"] for line in lines for row in line
                     if base(row) and predicate(row)})
    section = defaultdict(lambda: [0, 0])
    for line in lines:
        for row in line:
            if base(row) and predicate(row):
                section[row["target_section"]][0] += int(row[outcome])
                section[row["target_section"]][1] += 1
    deletion_rates, deletion_effects = [], []
    for held in folios:
        subset = [[row for row in line if row["physical_folio"] != held] for line in lines]
        subset = [line for line in subset if line]
        o, n, e, _, _, _, _ = core_test(subset, predicate, outcome, base)
        deletion_rates.append(o / n)
        deletion_effects.append((o - e) / n)
    return {"observed": observed, "family_n": count,
            "observed_rate": observed / count, "null_expected_hits": expected,
            "null_expected_rate": expected / count,
            "rate_effect": (observed - expected) / count, "local_p": pvalue,
            "null_support_min": low, "null_support_max": high,
            "informative_lines": informative, "target_folios": len(folios),
            "hb_hits": section["HB"][0], "hb_n": section["HB"][1],
            "sb_hits": section["SB"][0], "sb_n": section["SB"][1],
            "lofo_min_rate": min(deletion_rates),
            "lofo_min_effect": min(deletion_effects)}


def close(stored, expected, tolerance=5e-10):
    return abs(float(stored) - expected) <= tolerance


def compare_row(stored, expected, adjusted_name, adjusted_tests):
    exact = all(int(stored[key]) == expected[key] for key in (
        "observed", "family_n", "null_support_min", "null_support_max",
        "informative_lines", "target_folios", "hb_hits", "hb_n", "sb_hits", "sb_n"))
    for key in ("observed_rate", "null_expected_hits", "null_expected_rate",
                "rate_effect", "local_p", "lofo_min_rate", "lofo_min_effect"):
        exact &= close(stored[key], expected[key])
    exact &= close(stored[adjusted_name], min(1.0, expected["local_p"] * adjusted_tests))
    return exact


def main():
    checks = {}
    lines = reconstruct_lines(read(SOURCE))
    rows = [row for line in lines for row in line]
    checks["held_population_exact"] = (len(lines) == 284 and len(rows) == 2561 and
        len({row["physical_folio"] for row in rows}) == 22 and
        not ({row["physical_folio"] for row in rows} & DISCOVERY))
    predicates = {
        "TERMINAL_M": lambda row: row["residual_host"].endswith("m"),
        "TERMINAL_AM": lambda row: row["residual_host"].endswith("am"),
        "TERMINAL_DAM": lambda row: row["residual_host"].endswith("dam"),
        "EXACT_AM_HOST": lambda row: row["residual_host"] == "am",
        "D_WRAPPED_AM": lambda row: row["residual_host"] == "am" and row["stripped_prefix"] == "d",
        "CARRIER_WRAPPED_AM": lambda row: row["residual_host"] == "am" and
                                      row["stripped_prefix"] in {"ch", "che", "sh"},
    }
    actual_tests = {(row["family"], row["outcome"]): row for row in read(TESTS)}
    tests_exact = True
    expected_tests = {}
    for family, predicate in predicates.items():
        for outcome in OUTCOMES:
            expected = full_test(lines, predicate, outcome)
            expected_tests[family, outcome] = expected
            tests_exact &= compare_row(actual_tests[family, outcome], expected,
                                       "bonferroni_18_p", 18)
    checks["all_18_family_tests_exact"] = tests_exact

    nested = {
        "TERMINAL_AM_WITHIN_TERMINAL_M": (predicates["TERMINAL_AM"], predicates["TERMINAL_M"]),
        "TERMINAL_DAM_WITHIN_TERMINAL_AM": (predicates["TERMINAL_DAM"], predicates["TERMINAL_AM"]),
        "EXACT_AM_WITHIN_TERMINAL_AM": (predicates["EXACT_AM_HOST"], predicates["TERMINAL_AM"]),
    }
    actual_spec = {(row["contrast"], row["outcome"]): row for row in read(SPEC)}
    specificity_exact = True
    expected_spec = {}
    for contrast, (predicate, base) in nested.items():
        for outcome in OUTCOMES:
            expected = full_test(lines, predicate, outcome, base)
            expected_spec[contrast, outcome] = expected
            specificity_exact &= compare_row(actual_spec[contrast, outcome], expected,
                                             "bonferroni_9_p", 9)
    checks["all_9_specificity_tests_exact"] = specificity_exact

    expected_occ = []
    for row in rows:
        if predicates["TERMINAL_M"](row):
            expected_occ.append({key: str(row[key]) for key in (
                "locus", "page", "physical_folio", "target_section", "hand",
                "group_index", "group_count", "token", "stripped_prefix",
                "residual_host", "record_state", "final_open_field",
                "physical_line_end", "open_physical_line_end")})
    expected_occ.sort(key=lambda row: (row["physical_folio"], row["locus"],
                                       int(row["group_index"])))
    checks["terminal_m_occurrences_exact"] = read(OCC) == expected_occ and len(expected_occ) == 81

    terminal = expected_tests["TERMINAL_M", "physical_line_end"]
    am_nested = expected_spec["TERMINAL_AM_WITHIN_TERMINAL_M", "physical_line_end"]
    dam_nested = expected_spec["TERMINAL_DAM_WITHIN_TERMINAL_AM", "physical_line_end"]
    checks["decision_arithmetic"] = (terminal["observed"] == 59 and terminal["family_n"] == 81 and
        terminal["lofo_min_effect"] > 0 and am_nested["rate_effect"] <= 0 and
        dam_nested["rate_effect"] <= 0)

    result = json.loads(RESULT.read_text())
    body = dict(result)
    claimed = body.pop("result_content_sha256")
    checks["result_content_hash"] = canonical_sha(body) == claimed
    checks["result_status"] = result["status"] == (
        "DAM_FIELD_ROLE_ATTRIBUTED_TO_TERMINAL_M_POSITIONAL_SYSTEM")
    checks["input_output_document_hashes"] = all(
        sha(ROOT / name) == digest for family in ("inputs", "outputs", "documents")
        for name, digest in result[family].items())
    checks["implementation_hash"] = all(sha(ROOT / name) == digest
                                         for name, digest in result["implementation"].items())
    checks["f84_sealed"] = not any(result["f84r"].values()) and not any(
        row["locus"].startswith("f84r") for row in rows)
    report = (ROOT / "GDT039_TERMINAL_M_POSITIONAL_CONTROL_REPORT.md").read_text()
    checks["report_ceiling_and_counterexample"] = ("not DAM-specific" in report and
        "10/11" in report and "No concrete function" in report)
    ledger = [row for row in read(LEDGER) if row["checkpoint_id"] == "GDT039_CKPT001"]
    checks["ledger_exact"] = (len(ledger) == 1 and ledger[0]["status"] == result["status"] and
                               ledger[0]["result_artifact"] == RESULT.name)
    passed = all(checks.values())
    validation = {"schema": "GDT039_TERMINAL_M_POSITIONAL_CONTROL_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_EXACT_RECONSTRUCTION" if passed else "FAIL",
        "checks": checks, "checks_passed": sum(checks.values()),
        "checks_total": len(checks), "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independent population, exact hypergeometric convolution, nested specificity, occurrences, hashes, claims, and ledger."}
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": validation["status"],
                      "checks": f'{validation["checks_passed"]}/{validation["checks_total"]}'},
                     sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
