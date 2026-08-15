#!/usr/bin/env python3
"""Independent integrity/recomposition checks for the GDT155 blind run."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt155_blind_result.json"
OUT = ROOT / "gdt155_blind_validation.json"


def read(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"check": name, "pass": bool(condition), "detail": detail})
    assert condition, (name, detail)


result = json.loads(RESULT.read_text(encoding="utf-8"))
trans = read("gdt155_blind_transformations.tsv")
rect = read("gdt155_blind_rectangles.tsv")
parses = read("gdt155_blind_group_parses.tsv")
arch = read("gdt155_blind_record_architecture.tsv")
profiles = read("gdt155_blind_record_profiles.tsv")
neighbors = read("gdt155_blind_retrieval_neighbors.tsv")

check("schema", result["schema"] == "GDT155_BLIND_ANALYSIS_RESULT_V1", result["schema"])
check("status", result["status"] == "BLIND_FORMAL_ANALYSIS_COMPLETE_TRUTH_UNEXPOSED", result["status"])
check("record_count", len(profiles) == result["records"] == 3178, len(profiles))
check("nuremberg_records", sum(row["corpus"] == "NUREMBERG" for row in profiles) == 3176, sum(row["corpus"] == "NUREMBERG" for row in profiles))
check("ste1_records", sum(row["corpus"] == "STE1" for row in profiles) == 2, sum(row["corpus"] == "STE1" for row in profiles))
check("representations", len(result["representations"]) == 7 and len(set(result["representations"])) == 7, result["representations"])

by_fold_side: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
for row in trans: by_fold_side[row["fold"], row["side"]].append(row)
for fold in ("Band2", "Band3", "Band4", "Band5", "ALL_NUREMBERG"):
    for side in ("LEFT", "RIGHT"):
        values = by_fold_side[fold, side]
        check(f"{fold}_{side}_12", len(values) == 12, len(values))
        check(f"{fold}_{side}_rank", sorted(int(row["selected_rank"]) for row in values) == list(range(1, 13)), sorted(int(row["selected_rank"]) for row in values))
        check(f"{fold}_{side}_eligible", all(row["eligible"] == "1" and int(row["distinct_hosts"]) >= 8 and int(row["training_records"]) >= 5 for row in values), len(values))

check("rectangle_rows", len(rect) == 5 * 12 * 12, len(rect))
check("rectangle_sum", sum(int(row["complete_4_of_4_hosts"]) for row in rect if row["fold"] != "ALL_NUREMBERG") == result["complete_rectangle_host_instances_four_folds"], result["complete_rectangle_host_instances_four_folds"])

licensed = {(row["fold"], row["side"], row["operation"]) for row in trans}
recomposition_bad = 0
operation_bad = 0
for row in parses:
    fold = row["fold"] if row["fold"] != "STE1_TRANSFER" else "ALL_NUREMBERG"
    left = "".join(value for value in (row["outer_left"], row["local_left"]) if value != "NONE")
    right = "".join(value for value in (row["right_inner"], row["right_outer"]) if value != "NONE")
    reconstructed = "" if row["page_host"] == "EMPTY" else left + row["page_host"] + right
    if reconstructed != row["surface_without_marker"]:
        recomposition_bad += 1
    for side, fields in (("LEFT", ("outer_left", "local_left")), ("RIGHT", ("right_outer", "right_inner"))):
        for field in fields:
            if row[field] != "NONE" and (fold, side, row[field]) not in licensed:
                operation_bad += 1
check("parse_recomposition", recomposition_bad == 0, recomposition_bad)
check("parse_operations_licensed", operation_bad == 0, operation_bad)
check("parse_unique", len({(row["fold"], row["surface_group"]) for row in parses}) == len(parses), len(parses))
check("no_truth_columns", not any(any(word in key.lower() for word in ("expan", "regular", "meaning", "gloss", "addressee", "content")) for key in parses[0]), list(parses[0]))

expected_neighbors = 3176 * 7 * 10
check("neighbor_rows", len(neighbors) == expected_neighbors, len(neighbors))
check("neighbor_representation_set", {row["representation"] for row in neighbors} == set(result["representations"]), sorted({row["representation"] for row in neighbors}))
check("neighbor_distinct_records", all(row["query_record"] != row["candidate_record"] for row in neighbors), len(neighbors))
rank_counts = Counter((row["query_record"], row["representation"]) for row in neighbors)
rank_values: dict[tuple[str, str], list[int]] = defaultdict(list)
for row in neighbors:
    rank_values[row["query_record"], row["representation"]].append(int(row["blind_rank"]))
check("ten_neighbors_each", len(rank_counts) == 3176 * 7 and set(rank_counts.values()) == {10}, sorted(set(rank_counts.values())))
check("neighbor_ranks", all(sorted(values) == list(range(1, 11)) for values in rank_values.values()), len(rank_values))
check("architecture_books", {row["book_or_ms"] for row in arch} == {"Band2", "Band3", "Band4", "Band5", "Ste1"}, sorted({row["book_or_ms"] for row in arch}))

for name, expected in result["outputs"].items():
    check("hash_" + name, sha(ROOT / name) == expected, expected)
copy = dict(result); expected_content = copy.pop("result_content_sha256")
check("result_content_hash", csha(copy) == expected_content, expected_content)
check("truth_unused", result["truth_exported_or_used"] is False, result["truth_exported_or_used"])
check("no_voynich_inputs", result["f84"]["voynich_inputs"] == 0 and result["f84"]["accessed"] is False, result["f84"])

validation = {
    "schema": "GDT155_BLIND_ANALYSIS_VALIDATION_V1",
    "status": f"PASS_{len(checks)}_CHECK_BLIND_RECOMPOSITION_AND_INTEGRITY",
    "checks": checks,
    "result_sha256": sha(RESULT),
    "validator_sha256": sha(Path(__file__)),
    "scope": "Independent artifact integrity, parse recomposition, operation licensing, and neighbor-table arithmetic; does not rerun the operator search.",
}
OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(validation["status"])
