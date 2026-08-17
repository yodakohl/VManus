#!/usr/bin/env python3
"""Independent non-importing validator for GDT269."""
import csv
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

R = Path(__file__).resolve().parent
SRC = "gdt227_q13_abstract_interlinear.tsv"
METHOD = "GDT269_Q13_WRAPPER_HOST_CONDITIONAL_METHOD.md"
RUNNER = "run_gdt269_q13_wrapper_host_conditional.py"
RESULT = "gdt269_result.json"
VARIANTS = [
    ("PAGE_HOST_PAGE", ("page", "page_host")),
    ("PAGE_HOST_PAGE_ROLE", ("page", "page_host", "field_role")),
    ("PAGE_HOST_PAGE_RELATIVE_QUARTILE", ("page", "page_host", "relative_quartile")),
    ("PAGE_HOST_PAGE_WITHIN_FIELD_POSITION", ("page", "page_host", "within_field_position")),
    ("PAGE_HOST_PAGE_FIELD_END", ("page", "page_host", "field_end")),
    ("PAGE_HOST_PAGE_ROLE_WITHIN_FIELD_POSITION", ("page", "page_host", "field_role", "within_field_position")),
    ("PAGE_HOST_PAGE_RELATIVE_QUARTILE_WITHIN_FIELD_POSITION", ("page", "page_host", "relative_quartile", "within_field_position")),
]


def read(name):
    with (R / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(name):
    return hashlib.sha256((R / name).read_bytes()).hexdigest()


def close(a, b, tolerance=5e-10):
    return abs(float(a) - float(b)) <= tolerance


def reconstruct_occurrences():
    source = read(SRC)
    assert source and all(not row["page"].startswith("f84") for row in source)
    records = defaultdict(list)
    loci = defaultdict(set)
    for row in source:
        key = (row["page"], row["record_id"])
        records[key].append(row)
        loci[key].add(row["locus"])
    candidates = defaultdict(list)
    for (page, record_id), values in loci.items():
        if len(values) >= 4:
            candidates[page].append(record_id)
    panel = {page: sorted(values) for page, values in candidates.items() if len(values) == 2}
    rows = []
    for page, ids in sorted(panel.items()):
        for ordinal, record_id in enumerate(ids):
            for field in records[(page, record_id)]:
                hosts = field["page_hosts"].split("|")
                cells = field["compiler_cells"].split("|")
                tokens = field["source_tokens"].split("|")
                assert len(hosts) == len(cells) == len(tokens)
                for index, (host, cell, token) in enumerate(zip(hosts, cells, tokens)):
                    wrapper = cell.split(":")[0]
                    if wrapper not in {"q", "NONE"}:
                        continue
                    within = "SINGLE" if len(hosts) == 1 else "FIRST" if index == 0 else "LAST" if index == len(hosts) - 1 else "MIDDLE"
                    rows.append({
                        "page": page, "physical_folio": field["physical_folio"], "record_id": record_id,
                        "ordinal_class": "EARLIER" if ordinal == 0 else "LATER", "ordinal_binary": str(ordinal),
                        "locus": field["locus"], "field_ordinal": field["field_ordinal"],
                        "field_role": field["abstract_role_like"],
                        "relative_quartile": str(min(3, int(float(field["relative_position"]) * 4))),
                        "within_field_position": within, "field_end": field["line_field_end"],
                        "page_host": host, "wrapper": wrapper, "source_token": token,
                        "claim_state": "OPAQUE_CONSTRUCTIONAL_OCCURRENCE_NO_GLOSS",
                    })
    return panel, rows


def calculate(name, keys, occurrences):
    grouped = defaultdict(Counter)
    for row in occurrences:
        grouped[tuple(row[key] for key in keys)][row["wrapper"], int(row["ordinal_binary"])] += 1
    mobile = []
    for key, counts in grouped.items():
        n = sum(counts.values())
        q = counts["q", 0] + counts["q", 1]
        early = counts["q", 0] + counts["NONE", 0]
        low, high = max(0, q - (n - early)), min(q, early)
        if high > low:
            mobile.append((key, counts, n, q, early, low, high))
    distribution = {0: 1.0}
    num = den = score = variance = 0.0
    observed = 0
    page_score = defaultdict(float)
    for key, counts, n, q, early, low, high in mobile:
        a, b, c, d = counts["q", 0], counts["q", 1], counts["NONE", 0], counts["NONE", 1]
        num += a * d / n
        den += b * c / n
        delta = a - q * early / n
        score += delta
        page_score[key[0]] += delta
        observed += a
        variance += q * (n - q) * early * (n - early) / (n * n * (n - 1))
        local = {value: comb(early, value) * comb(n - early, q - value) / comb(n, q) for value in range(low, high + 1)}
        new = defaultdict(float)
        for total, p0 in distribution.items():
            for value, p1 in local.items():
                new[total + value] += p0 * p1
        distribution = dict(new)
    mean = sum(value * probability for value, probability in distribution.items())
    upper = sum(probability for value, probability in distribution.items() if value >= observed)
    two = sum(probability for value, probability in distribution.items() if abs(value - mean) >= abs(observed - mean) - 1e-12)
    pages = sorted({row["page"] for row in occurrences})
    values = [page_score[page] for page in pages]
    stat = abs(sum(values)) / math.sqrt(sum(value * value for value in values))
    null = []
    for signs in itertools.product((-1, 1), repeat=len(values)):
        denominator = math.sqrt(sum(value * value for value in values))
        null.append(abs(sum(sign * value for sign, value in zip(signs, values))) / denominator if denominator else 0.0)
    sign_p = (1 + sum(value >= stat - 1e-15 for value in null)) / (len(null) + 1)
    return {
        "variant": name, "all_strata": len(grouped), "movable_strata": len(mobile),
        "mobile_occurrences": sum(item[2] for item in mobile),
        "mobile_hosts": len({item[0][1] for item in mobile}), "mobile_pages": len({item[0][0] for item in mobile}),
        "observed": observed, "expected": mean, "score": score, "z": score / math.sqrt(variance),
        "or": num / den, "upper": upper, "two": two,
        "positive": sum(value > 0 for value in values), "negative": sum(value < 0 for value in values),
        "ties": sum(value == 0 for value in values), "stat": stat, "sign_p": sign_p,
        "distribution": distribution,
    }


def main():
    checks = []

    def check(name, condition):
        assert condition, name
        checks.append(name)

    panel, occurrences = reconstruct_occurrences()
    exported_occurrences = read("gdt269_occurrences.tsv")
    check("nine_pages", len(panel) == 9)
    check("eighteen_records", sum(len(value) for value in panel.values()) == 18)
    check("occurrence_count", len(occurrences) == len(exported_occurrences) == 632)
    check("occurrences_exact", occurrences == exported_occurrences)
    check("q_none_only", {row["wrapper"] for row in occurrences} == {"q", "NONE"})
    check("no_f84_occurrences", all(not row["page"].startswith("f84") for row in occurrences))

    exported_tests = {row["variant"]: row for row in read("gdt269_tests.tsv")}
    check("variant_names", set(exported_tests) == {name for name, _ in VARIANTS})
    rebuilt = {}
    for name, keys in VARIANTS:
        value = calculate(name, keys, occurrences)
        rebuilt[name] = value
        row = exported_tests[name]
        check(name + "_counts", int(row["all_strata"]) == value["all_strata"] and int(row["movable_strata"]) == value["movable_strata"] and int(row["mobile_occurrences"]) == value["mobile_occurrences"] and int(row["mobile_hosts"]) == value["mobile_hosts"] and int(row["mobile_pages"]) == value["mobile_pages"])
        check(name + "_effect", close(row["expected_q_early"], value["expected"]) and close(row["conditional_score_u"], value["score"]) and close(row["conditional_z"], value["z"]) and close(row["mantel_haenszel_odds_ratio"], value["or"]))
        check(name + "_pvalues", close(row["exact_upper_p"], value["upper"]) and close(row["exact_two_sided_p"], value["two"]) and close(row["page_sign_flip_p"], value["sign_p"]))
        check(name + "_page_directions", int(row["positive_page_scores"]) == value["positive"] and int(row["negative_page_scores"]) == value["negative"] and int(row["tied_page_scores"]) == value["ties"])

    null_rows = defaultdict(dict)
    for row in read("gdt269_exact_null.tsv"):
        null_rows[row["variant"]][int(row["q_early_total"])] = float(row["probability"])
    for name, value in rebuilt.items():
        check(name + "_null_support", set(null_rows[name]) == set(value["distribution"]))
        check(name + "_null_mass", close(sum(null_rows[name].values()), 1.0, 2e-12))
        check(name + "_null_values", all(close(null_rows[name][key], probability, 2e-12) for key, probability in value["distribution"].items()))

    result = json.loads((R / RESULT).read_text(encoding="utf-8"))
    stored_hash = result.pop("content_hash")
    check("result_content_hash", stored_hash == hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
    check("source_hash", result["inputs"][SRC] == sha(SRC))
    check("method_hash", result["documents"][METHOD] == sha(METHOD))
    check("runner_hash", result["implementation"][RUNNER] == sha(RUNNER))
    check("all_input_hashes", all(sha(name) == digest for name, digest in result["inputs"].items()))
    check("all_output_hashes", all(sha(name) == digest for name, digest in result["outputs"].items()))
    check("primary_result", close(result["primary"]["mh_odds_ratio"], rebuilt["PAGE_HOST_PAGE"]["or"]) and close(result["primary"]["exact_two_sided_p"], rebuilt["PAGE_HOST_PAGE"]["two"]) and close(result["primary"]["page_sign_flip_p"], rebuilt["PAGE_HOST_PAGE"]["sign_p"]))
    check("position_result", close(result["position_sensitivity"]["mh_odds_ratio"], rebuilt["PAGE_HOST_PAGE_WITHIN_FIELD_POSITION"]["or"]) and close(result["position_sensitivity"]["exact_two_sided_p"], rebuilt["PAGE_HOST_PAGE_WITHIN_FIELD_POSITION"]["two"]))
    check("semantic_assignments_zero", result["semantic_assignments"] == 0)
    check("f84_flags_false", result["f84r"]["new_access"] is False and result["f84r"]["used"] is False and result["f84r"]["scored"] is False)
    check("status_exact", result["status"] == "Q13_Q_STAGE_SURVIVES_EXACT_HOST_PAGE_CONDITIONING_BUT_IS_POSITION_SENSITIVE")

    validation = {
        "experiment": "GDT269_Q13_WRAPPER_HOST_CONDITIONAL",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks": checks,
        "independent_reconstruction": True,
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__).name),
        "f84r_accessed": False,
    }
    (R / "gdt269_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "checks": len(checks), "primary_two_sided": rebuilt["PAGE_HOST_PAGE"]["two"], "position_two_sided": rebuilt["PAGE_HOST_PAGE_WITHIN_FIELD_POSITION"]["two"]}, sort_keys=True))


if __name__ == "__main__":
    main()
