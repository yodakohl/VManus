#!/usr/bin/env python3
"""Independent validation of the prospective GDT219 target reveal."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent; CHECKS: list[str] = []


def check(value: bool, name: str) -> None:
    if not value: raise AssertionError(name)
    CHECKS.append(name)


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    result_path = ROOT / "gdt219_result.json"; result = json.loads(result_path.read_text(encoding="utf-8")); freeze = json.loads((ROOT / "gdt219_prediction_freeze.json").read_text(encoding="utf-8"))
    target = read("gdt219_f76_paragraph_keys.tsv"); nulls = read("gdt219_null_results.tsv"); counter = read("gdt219_counterexamples.tsv")
    roles = {row["locus"]: row for row in read("experiments/semantic_assumptions/results/existing_human_locus_roles.tsv") if row["page"] == "f76r"}
    groups = defaultdict(list)
    for row in read("gdt016_group_state_inventory.tsv"):
        if row["page"] == "f76r" and roles.get(row["locus"], {}).get("kind") == "P" and roles[row["locus"]]["paragraph_start"] == "1": groups[row["locus"]].append(row)
    check(result["experiment"] == "GDT219_SINGLE_SIGN_KEY_TEST", "experiment")
    check(len(groups) == len(target) == 2, "two_targets")
    expected = []
    label_set = set(freeze["label_key_set"])
    for locus in sorted(groups, key=lambda value: int(value.split(".")[1])):
        row = min(groups[locus], key=lambda value: int(value["group_index"])); key = row["family_surface"][:1]
        expected.append((locus, row["group_index"], row["family_surface"], key, str(int(key in label_set))))
    observed = [(row["paragraph_start_locus"], row["first_group_index"], row["first_group_family_surface"], row["single_family_key"], row["in_frozen_label_key_set"]) for row in target]
    check(observed == expected, "target_source_exact")
    training = read("gdt219_null_training_distribution.tsv"); expanded = []
    for row in training: expanded.extend([row["family_key"]] * int(row["discovery_paragraph_opening_occurrences"]))
    check(len(expanded) == 42, "training_42")
    distribution = Counter(int(expanded[i] in label_set) + int(expanded[j] in label_set) for i, j in itertools.combinations(range(42), 2))
    check(sum(distribution.values()) == 861, "worlds_861")
    hits = sum(int(row["in_frozen_label_key_set"]) for row in target); distinct = len({row["single_family_key"] for row in target}); exact_p = sum(count for value, count in distribution.items() if value >= hits) / 861
    check(result["target"] == {"page": "f76r", "paragraph_keys": [row["single_family_key"] for row in target], "hits": hits, "distinct_target_keys": distinct}, "target_result")
    check(abs(result["null"]["exact_inclusive_p"] - exact_p) < 1e-15, "exact_p")
    check(result["null"]["distribution"] == {str(key): distribution[key] for key in range(3)}, "null_distribution")
    check({int(row["hit_count"]): int(row["worlds"]) for row in nulls} == dict(distribution), "null_tsv")
    gates = result["decision_gates"]; expected_pass = hits == 2 and distinct >= 2 and exact_p <= .05
    check(gates == {"two_of_two_hits": hits == 2, "two_distinct_target_keys": distinct >= 2, "exact_p_at_most_05": exact_p <= .05, "all_pass": expected_pass}, "gates")
    check(result["status"] == ("SINGLE_SIGN_KEY_SET_PROVISIONAL_LEAD" if expected_pass else "SINGLE_SIGN_KEY_SET_NOT_SUPPORTED"), "status")
    check(len(counter) == 4, "four_counterexamples")
    check(result["access_chronology"] == {"label_side_frozen_before_target": True, "paragraph_side_first_opened_by_this_scorer": True, "prior_raw_label_display_disclosed": True}, "chronology")
    check(result["f84r"] == {"accessed": False, "input": False, "output": False}, "f84r")
    check(not any(row["page"].startswith("f84") or row["paragraph_start_locus"].startswith("f84") for row in target), "output_no_f84")
    for group in ("inputs_sha256", "selected_source_inputs_sha256", "outputs_sha256", "documents_sha256"):
        for name, digest in result[group].items():
            path = ROOT / name
            if not path.exists(): path = ROOT / "experiments/semantic_assumptions/results" / name
            check(sha(path) == digest, f"hash:{group}:{name}")
    check(sha(ROOT / "run_gdt219_single_sign_key_test.py") == result["implementation_sha256"], "implementation_hash")
    check(sha(Path(__file__)) == result["validator_sha256"], "validator_hash")
    payload = dict(result); observed_hash = payload.pop("content_sha256")
    check(hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == observed_hash, "content_hash")
    validation = {"experiment": result["experiment"], "status": "PASS", "checks_passed": len(CHECKS), "checks": CHECKS, "result_sha256": sha(result_path), "validator_sha256": sha(Path(__file__))}
    (ROOT / "gdt219_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {len(CHECKS)}/{len(CHECKS)}")


if __name__ == "__main__": main()
