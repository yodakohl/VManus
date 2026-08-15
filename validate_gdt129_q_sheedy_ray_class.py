#!/usr/bin/env python3
"""Independently validate GDT129 inventory, exact diagnostics, and hashes."""
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt129_result.json"
INVENTORY = ROOT / "gdt129_q_sheedy_inventory.tsv"
TESTS = ROOT / "gdt129_q_sheedy_tests.tsv"
COUNTER = ROOT / "gdt129_q_sheedy_counterexamples.tsv"
OUT = ROOT / "gdt129_validation.json"
FIELDS = ROOT / "gdt127_q20_field_inventory.tsv"
STAR = ROOT / "experiments/semantic_assumptions/star_morphology_entry/source_panel.tsv"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
GDT128 = ROOT / "gdt128_result.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hypergeom_tail(population, successes, draws, observed):
    denominator = math.comb(population, draws)
    return sum(math.comb(successes, k) * math.comb(population - successes, draws - k)
               for k in range(observed, min(draws, successes) + 1)
               if 0 <= draws - k <= population - successes) / denominator


def close(a, b):
    return abs(float(a) - float(b)) <= 5e-13


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    rows = read(INVENTORY)
    tests = {row["test"]: row for row in read(TESTS)}
    counters = read(COUNTER)
    discovery = [row for row in rows if row["panel"] == "ARCHIVED_DISCOVERY"]
    prospective = [row for row in rows if row["panel"] == "PROSPECTIVE_GDT128"]
    q_discovery = [row for row in discovery if row["exact_adjacent_q_sheedy"] == "1"]
    q_all = [row for row in rows if row["exact_adjacent_q_sheedy"] == "1"]
    two = [row for row in discovery if row["has_exact_two_group_sheedy"] == "1"]
    q_two = [row for row in two if row["exact_adjacent_q_sheedy"] == "1"]
    # Reconstruct the primary census and alternate-reading predicate without
    # importing or calling the producer.
    rebuilt = defaultdict(lambda: {"forms": [], "q_forms": [], "q_loci": [], "two_group": False})
    for row in read(FIELDS):
        if row["edition"] != "ZL3b":
            continue
        tokens = row["group_tokens"].split("|")
        if "sheedy" not in tokens:
            continue
        key = (row["page"], row["star_ordinal"])
        rebuilt[key]["forms"].append(row["group_tokens"])
        rebuilt[key]["two_group"] |= len(tokens) == 2 and tokens[-1] == "sheedy"
        if any(tokens[i].startswith("q") and tokens[i + 1] == "sheedy" for i in range(len(tokens) - 1)):
            rebuilt[key]["q_forms"].append(row["group_tokens"])
            rebuilt[key]["q_loci"].append(row["locus"])
    star = {(row["page"], row["star_ordinal"]): row for row in read(STAR)}
    source = defaultdict(list)
    for row in read(SOURCE):
        source[(row["edition"], row["locus"])].append((int(row["source_group_index"]), row["ivtff_group_raw"]))
    for key in source:
        source[key].sort()
    def exact(info, edition):
        for locus in info["q_loci"]:
            tokens = [token for _, token in source[(edition, locus)]]
            if any(tokens[i].startswith("q") and tokens[i + 1] == "sheedy" for i in range(len(tokens) - 1)):
                return 1
        return 0
    inventory_discovery = {(row["page"], row["star_ordinal"]): row for row in discovery}
    transfer = json.loads(GDT128.read_text(encoding="utf-8"))
    checks = {}
    checks["schema"] = result["schema"] == "GDT129_Q_SHEEDY_RAY_CLASS_RESULT_V1"
    checks["status"] = result["status"] == "Q_SHEEDY_EIGHT_RAY_LEAD_PROVISIONAL_TAIL_STATE_FAILED"
    checks["row_census"] = len(rows) == 16 and len(discovery) == 15 and len(prospective) == 1
    checks["independent_primary_keyset"] = set(inventory_discovery) == set(rebuilt) and all(key in star for key in rebuilt)
    checks["independent_form_rebuild"] = all(inventory_discovery[key]["sheedy_fields"].split(";") == info["forms"] and inventory_discovery[key]["q_sheedy_fields"].split(";") == info["q_forms"] if info["q_forms"] else inventory_discovery[key]["q_sheedy_fields"] == "" for key, info in rebuilt.items())
    checks["independent_visual_join"] = all(inventory_discovery[key]["rays"] == star[key]["rays"] and inventory_discovery[key]["tail"] == star[key]["tail"] for key in rebuilt)
    checks["q_discovery"] = len(q_discovery) == 3 and all(row["rays"] == "8" and row["tail"] == "1" for row in q_discovery)
    checks["q_discovery_exact"] = {(row["page"], row["star_ordinal"], row["q_sheedy_fields"]) for row in q_discovery} == {("f104v", "5", "qotol|sheedy"), ("f104v", "6", "qotol|sheedy"), ("f115r", "12", "qokl|sheedy")}
    checks["prospective"] = prospective[0]["page"] == "f103r" and prospective[0]["star_ordinal"] == "15" and prospective[0]["rays"] == "8" and prospective[0]["tail"] == "0" and prospective[0]["q_sheedy_fields"] == "qokal|sheedy"
    checks["independent_prospective_join"] = transfer["review"]["ray_consensus"] == int(prospective[0]["rays"]) and transfer["review"]["tail_consensus"] == int(prospective[0]["tail"])
    checks["reading_rebuild"] = all(
        int(inventory_discovery[key][f"{edition_key}_exact_q_sheedy"]) == exact(info, edition)
        for key, info in rebuilt.items() for edition_key, edition in (("zl", "ZL3b"), ("it", "IT2a"), ("rf", "RF1b"))
    )
    checks["all_reading_sensitivity"] = sum(row["all_readings_exact_q_sheedy"] == "1" for row in rows) == 2 and all(row["rays"] == "8" for row in rows if row["all_readings_exact_q_sheedy"] == "1") and prospective[0]["all_readings_exact_q_sheedy"] == "0"
    checks["combined"] = len(q_all) == 4 and all(row["rays"] == "8" for row in q_all) and len({row["physical_folio"] for row in q_all}) == 3
    checks["tail_failure"] = [row["tail"] for row in q_all].count("1") == 3 and [row["tail"] for row in q_all].count("0") == 1
    checks["discovery_background"] = sum(row["rays"] == "8" for row in discovery) == 7
    checks["two_group_background"] = len(two) == 7 and sum(row["rays"] == "8" for row in two) == 5 and len(q_two) == 3
    checks["p_discovery"] = close(tests["DISCOVERY_CONDITIONAL_ON_EXACT_SHEEDY"]["one_sided_exact_p"], hypergeom_tail(15, 7, 3, 3))
    checks["p_two_group"] = close(tests["DISCOVERY_EXACT_TWO_GROUP_SHEEDY_ONLY"]["one_sided_exact_p"], hypergeom_tail(7, 5, 3, 3))
    checks["p_combined"] = close(tests["COMBINED_WITH_ONE_FROZEN_PROSPECTIVE_TARGET"]["one_sided_exact_p"], hypergeom_tail(16, 8, 4, 4)) and tests["COMBINED_WITH_ONE_FROZEN_PROSPECTIVE_TARGET"]["inference"] == "DESCRIPTIVE_NOT_CONFIRMATORY"
    checks["within_page_capacity"] = tests["WITHIN_PAGE_CONTRAST_CAPACITY"]["inference"] == "NO_IDENTIFIABLE_WITHIN_PAGE_CONTRAST_0_INFORMATIVE_PAGES"
    checks["counterexamples"] = any("FROZEN_1_TAIL_PREDICTION_FAILED" in row["counterexample"] for row in counters) and sum("PRIMARY_Q_SHEEDY_NOT_EXACT_IN_ALL_READINGS" in row["counterexample"] for row in counters) == 2
    checks["chronology"] = "post-reveal" in result["chronology"] and "GDT128 was prospectively frozen" in result["chronology"]
    checks["f84_absent"] = not any(row["page"].startswith("f84r") for row in rows) and all(value is False for value in result["f84r"].values())
    checks["input_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["inputs"].items())
    checks["implementation_hash"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["implementation"].items())
    checks["output_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["outputs"].items())
    checks["document_hashes"] = all((ROOT / name).exists() and sha(ROOT / name) == digest for name, digest in result["documents"].items())
    content = dict(result)
    recorded = content.pop("result_content_sha256")
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    checks["content_hash"] = hashlib.sha256(canonical).hexdigest() == recorded
    checks["claim_ceiling"] = all(term in result["claim_ceiling"] for term in ("no number", "star meaning", "plaintext", "translation"))
    status = "PASS_INDEPENDENT_PRIMARY_CENSUS_READING_SENSITIVITY_NULL_AND_HASHES" if all(checks.values()) else "FAIL"
    validation = {"schema": "GDT129_Q_SHEEDY_RAY_CLASS_VALIDATION_V1", "status": status,
                  "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
                  "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__))}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
