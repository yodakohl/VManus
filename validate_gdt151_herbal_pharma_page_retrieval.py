#!/usr/bin/env python3
"""Independent reconstruction of GDT151 inventory, ranks, null, and hashes."""
import csv
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt062_right_family_inventory.tsv"
HMETA = R / "gdt137_herbal_visual_feature_inventory.tsv"
HUMAN = R / "experiments/semantic_assumptions/results/existing_human_page_annotations.tsv"
INV = R / "gdt151_relation_inventory.tsv"
RANKS = R / "gdt151_target_ranks.tsv"
NULL = R / "gdt151_null_results.tsv"
RESULT = R / "gdt151_result.json"
OUT = R / "gdt151_validation.json"
REPS = ("PAGE_HOST_IDENTITY", "PAGE_HOST_CHAR3", "RAW_CHAR3", "COMPILER_SIGNATURE", "GROUP_COUNT_PROXIMITY", "TARGET_DEGREE_PRIOR")
WORLDS = 100000
SEED = 151148


def read(path):
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add3(counter, value):
    value = "^" + value + "$"
    for i in range(max(1, len(value) - 2)):
        counter[value[i:i + 3]] += 1.0


def sim(left, right):
    keys = set(left) | set(right)
    denom = sum(max(left[key], right[key]) for key in keys)
    return sum(min(left[key], right[key]) for key in keys) / denom if denom else 0.0


def close(a, b, tol=5e-12):
    return abs(float(a) - float(b)) <= tol


def main():
    result = json.loads(RESULT.read_text(encoding="utf8"))
    stored_inventory = read(INV)
    stored_ranks = read(RANKS)
    stored_null = {row["representation"]: row for row in read(NULL)}
    herbal = {row["page"] for row in read(HMETA) if not row["page"].startswith("f84")}
    by_page = defaultdict(list)
    rejected_f84 = 0
    with SOURCE.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"].startswith("f84"):
                rejected_f84 += 1
                continue
            by_page[row["page"]].append(row)
    pharma = sorted(page for page, rows in by_page.items() if rows[0]["section"] == "P")
    descriptions = {}
    with HUMAN.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"].startswith("f84") or row["page"] not in herbal:
                continue
            descriptions[row["page"]] = row["illustrations"]
    rebuilt_pairs = []
    for source in sorted(descriptions):
        refs = list(dict.fromkeys(ref.lower() for ref in re.findall(r"\bf\d+[rv](?:\d)?\b", descriptions[source], re.I)))
        for target in refs:
            if target in pharma or re.match(r"^f(?:88|89|99|100|101|102)", target):
                rebuilt_pairs.append((source, target, "SCORED_COMPLETE_PHARMA_PAGE_BAG" if target in pharma else "UNSCORED_NO_FORMAL_PAGE_BAG"))
    stored_pairs = [(row["source_page"], row["target_page"], row["scoring_status"]) for row in stored_inventory]
    relations = [(source, target) for source, target, state in rebuilt_pairs if state.startswith("SCORED")]
    n = len(relations); pcount = len(pharma)
    target_idx = {page: i for i, page in enumerate(pharma)}
    assignment0 = np.array([target_idx[target] for _, target in relations], dtype=int)
    blocks = defaultdict(list)
    for i, (source, _) in enumerate(relations):
        blocks[source].append(i)
    features = {page: {rep: Counter() for rep in REPS[:4]} for page in by_page}
    lengths = {page: len(rows) for page, rows in by_page.items()}
    for page, rows in by_page.items():
        for row in rows:
            features[page]["PAGE_HOST_IDENTITY"][row["page_host"]] += 1
            add3(features[page]["PAGE_HOST_CHAR3"], row["page_host"])
            add3(features[page]["RAW_CHAR3"], row["token"])
            features[page]["COMPILER_SIGNATURE"]["|".join((row["wrapper"], row["inner_d"], row["local_frame"], row["right_family"], row["dy_closure"], row["b3"]))] += 1
    rank_mats = {}
    score_mats = {}
    for rep in REPS[:-1]:
        scores = np.zeros((n, pcount))
        for i, (source, _) in enumerate(relations):
            for j, target in enumerate(pharma):
                scores[i, j] = -abs(lengths[source] - lengths[target]) if rep == "GROUP_COUNT_PROXIMITY" else sim(features[source][rep], features[target][rep])
        ranks = np.ones_like(scores, dtype=int)
        for i in range(n):
            for j in range(pcount):
                ranks[i, j] = 1 + int(np.sum(scores[i] > scores[i, j] + 1e-12))
        score_mats[rep] = scores; rank_mats[rep] = ranks

    def prior_ranks(assignment):
        output = np.ones((n, pcount), dtype=int)
        total = Counter(map(int, assignment))
        for indices in blocks.values():
            train = total.copy()
            for idx in indices:
                train[int(assignment[idx])] -= 1
            values = np.array([train[j] for j in range(pcount)])
            ranks = 1 + np.array([np.sum(values > values[j]) for j in range(pcount)], dtype=int)
            for idx in indices:
                output[idx] = ranks
        return output

    rank_mats["TARGET_DEGREE_PRIOR"] = prior_ranks(assignment0)
    observed = {}
    rebuilt_rank_map = {}
    for rep in REPS:
        true_ranks = rank_mats[rep][np.arange(n), assignment0]
        observed[rep] = (float(np.mean(1.0 / true_ranks)), float(np.mean(true_ranks)), int(np.sum(true_ranks <= 3)))
        for i, (source, target) in enumerate(relations):
            rebuilt_rank_map[(source, target, rep)] = int(true_ranks[i])
    stored_rank_map = {(row["source_page"], row["target_page"], row["representation"]): int(row["true_target_rank"]) for row in stored_ranks}

    rng = random.Random(SEED)
    null_mrr = np.zeros((WORLDS, len(REPS)))
    null_top = np.zeros((WORLDS, len(REPS)), dtype=int)
    original = list(map(int, assignment0))
    double = next(indices for indices in blocks.values() if len(indices) == 2)
    for world in range(WORLDS):
        while True:
            draw = original.copy(); rng.shuffle(draw)
            if draw[double[0]] != draw[double[1]]:
                break
        assignment = np.array(draw, dtype=int)
        for j, rep in enumerate(REPS):
            ranks = prior_ranks(assignment) if rep == "TARGET_DEGREE_PRIOR" else rank_mats[rep]
            selected = ranks[np.arange(n), assignment]
            null_mrr[world, j] = np.mean(1.0 / selected)
            null_top[world, j] = int(np.sum(selected <= 3))
    mu_m = null_mrr.mean(0); sd_m = null_mrr.std(0); sd_m[sd_m == 0] = 1
    mu_t = null_top.mean(0); sd_t = null_top.std(0); sd_t[sd_t == 0] = 1
    obs_m = np.array([observed[rep][0] for rep in REPS]); obs_t = np.array([observed[rep][2] for rep in REPS])
    max_m = ((null_mrr - mu_m) / sd_m).max(1); max_t = ((null_top - mu_t) / sd_t).max(1)
    checks = {}
    checks["schema"] = result["schema"] == "GDT151_HERBAL_PHARMA_PAGE_RETRIEVAL_RESULT_V1"
    checks["status"] = result["status"] == "HERBAL_PHARMA_PAGE_HOST_RETRIEVAL_NOT_SUPPORTED"
    checks["inventory_exact"] = rebuilt_pairs == stored_pairs and len(rebuilt_pairs) == 32
    checks["scored_capacity"] = n == 31 and len(blocks) == 30 and pcount == 15
    checks["unscored_exact"] = [x for x in rebuilt_pairs if x[2].startswith("UNSCORED")] == [("f37r", "f101v", "UNSCORED_NO_FORMAL_PAGE_BAG")]
    checks["rank_rows"] = len(stored_ranks) == n * len(REPS) and stored_rank_map == rebuilt_rank_map
    checks["target_degree_multiset"] = Counter(target for _, target in relations) == Counter({"f102r2": 5, "f101r": 4, "f89v2": 4, "f89r1": 3, "f99r": 3, "f100v": 2, "f102r1": 2, "f99v": 2, "f100r": 1, "f102v1": 1, "f102v2": 1, "f88r": 1, "f88v": 1, "f89r2": 1})
    for j, rep in enumerate(REPS):
        row = stored_null[rep]
        checks[f"{rep}_observed"] = close(row["true_mrr"], observed[rep][0]) and close(row["true_mean_rank"], observed[rep][1]) and int(row["true_top_three"]) == observed[rep][2]
        checks[f"{rep}_null"] = close(row["null_mrr_mean"], mu_m[j]) and close(row["null_mrr_sd"], sd_m[j]) and close(row["null_top_three_mean"], mu_t[j]) and close(row["null_top_three_sd"], sd_t[j])
        checks[f"{rep}_tails"] = close(row["local_mrr_p"], np.mean(null_mrr[:, j] >= obs_m[j] - 1e-12)) and close(row["max_six_mrr_p"], np.mean(max_m >= (obs_m[j] - mu_m[j]) / sd_m[j] - 1e-12)) and close(row["local_top_three_p"], np.mean(null_top[:, j] >= obs_t[j])) and close(row["max_six_top_three_p"], np.mean(max_t >= (obs_t[j] - mu_t[j]) / sd_t[j] - 1e-12))
    checks["page_host_below_controls"] = observed["PAGE_HOST_IDENTITY"][0] < observed["GROUP_COUNT_PROXIMITY"][0] < observed["TARGET_DEGREE_PRIOR"][0]
    checks["source_filter"] = rejected_f84 == result["source_filter"]["rejected_f84_prefixed_gdt062_rows"] == 228 and not any(page.startswith("f84") for page in by_page)
    checks["f84_sealed"] = all(value is False for value in result["f84r"].values())
    checks["input_hashes"] = all((R / name).exists() and sha(R / name) == digest for name, digest in result["inputs"].items())
    checks["implementation_hash"] = all((R / name).exists() and sha(R / name) == digest for name, digest in result["implementation"].items())
    checks["output_hashes"] = all((R / name).exists() and sha(R / name) == digest for name, digest in result["outputs"].items())
    checks["document_hashes"] = all((R / name).exists() and sha(R / name) == digest for name, digest in result["documents"].items())
    content = dict(result); recorded = content.pop("result_content_sha256")
    checks["content_hash"] = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest() == recorded
    checks["claim_ceiling"] = all(word in result["claim_ceiling"] for word in ("no plant", "semantic role", "plaintext", "translation"))
    status = "PASS_INDEPENDENT_COMPLETE_GRAPH_RANK_AND_100000_WORLD_RECONSTRUCTION" if all(checks.values()) else "FAIL"
    validation = {"schema": "GDT151_HERBAL_PHARMA_PAGE_RETRIEVAL_VALIDATION_V1", "status": status,
                  "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
                  "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__))}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
