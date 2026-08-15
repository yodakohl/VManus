#!/usr/bin/env python3
"""Independent reconstruction of GDT152 HPR2 parsing and exact assignments."""
import csv
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
QUERIES = R / "gdt152_relation_queries.tsv"
HOSTS = R / "gdt062_right_family_inventory.tsv"
GROUPS = R / "gdt016_group_state_inventory.tsv"
MATRIX = R / "gdt152_score_matrix.tsv"
ASSIGN = R / "gdt152_assignment_results.tsv"
RESULT = R / "gdt152_result.json"
OUT = R / "gdt152_validation.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
REPS = ("PAGE_HOST_IDENTITY", "PAGE_HOST_CHAR3", "RAW_CHAR3", "SOURCE_FAMILY_CHAR3", "COMPILER_SIGNATURE")
PREFIXES = ("che", "ch", "sh", "t", "s", "d", "q")
RIGHT = ("aiin", "air", "ain", "ar", "al")


def read(path):
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip(token):
    prefix = "NONE"; host = token
    for candidate in PREFIXES:
        if host.startswith(candidate) and len(host) > len(candidate):
            prefix = candidate; host = host[len(candidate):]; break
    dy = int(host.endswith("dy") and len(host) > 2)
    if dy: host = host[:-2]
    return prefix, host, dy


def parse(token, licensed):
    prefix, host, dy = strip(token)
    b3 = int(host.endswith("m") and len(host) > 1)
    if b3: host = host[:-1]
    right = "NONE"
    for suffix in RIGHT:
        if host.endswith(suffix) and len(host) > len(suffix):
            host = host[:-len(suffix)]; right = suffix; break
    inner = int(prefix in {"ch", "che", "sh"} and host.startswith("d") and len(host) > 1)
    if inner: host = host[1:]
    frame = "NONE"
    if host.startswith("ot") and host[2:] in licensed:
        host = host[2:]; frame = "OT"
    elif host.startswith("o") and host[1:] in licensed:
        host = host[1:]; frame = "O"
    return host or "EMPTY", prefix, inner, frame, right, dy, b3


def preframe_host(host, prefix):
    if host.endswith("m") and len(host) > 1:
        host = host[:-1]
    for suffix in RIGHT:
        if host.endswith(suffix) and len(host) > len(suffix):
            host = host[:-len(suffix)]; break
    if prefix in {"ch", "che", "sh"} and host.startswith("d") and len(host) > 1:
        host = host[1:]
    return host


def add3(counter, value):
    value = "^" + value + "$"
    for i in range(max(1, len(value) - 2)):
        counter[value[i:i + 3]] += 1.0


def sim(left, right):
    keys = set(left) | set(right)
    denom = sum(max(left[key], right[key]) for key in keys)
    return sum(min(left[key], right[key]) for key in keys) / denom if denom else 0.0


def qvec(row, rep):
    out = Counter()
    if rep == "PAGE_HOST_IDENTITY": out[row["page_host"]] = 1
    elif rep == "PAGE_HOST_CHAR3": add3(out, row["page_host"])
    elif rep == "RAW_CHAR3": add3(out, row["token"])
    elif rep == "SOURCE_FAMILY_CHAR3": add3(out, row["family_surface"])
    else: out["|".join((row["wrapper"], row["inner_d"], row["local_frame"], row["right_family"], row["dy_closure"], row["b3"]))] = 1
    return out


def close(a, b, tol=5e-12):
    return abs(float(a) - float(b)) <= tol


def main():
    result = json.loads(RESULT.read_text(encoding="utf8"))
    queries = read(QUERIES); stored_matrix = read(MATRIX); stored_assign = read(ASSIGN)
    group_rows = read(GROUPS)
    counts = Counter(preframe_host(row["residual_host"], row["stripped_prefix"]) for row in group_rows)
    licensed = {host for host in counts if counts[host] and counts["o" + host] and counts["ot" + host]} | {"ar", "al", "ol"}
    parse_ok = True
    for row in queries:
        parsed = parse(row["token"], licensed)
        expected = (row["page_host"], row["wrapper"], int(row["inner_d"]), row["local_frame"], row["right_family"], int(row["dy_closure"]), int(row["b3"]))
        parse_ok &= parsed == expected
    rids = sorted({row["relation_id"] for row in queries})
    targets = [next(row["target_page"] for row in queries if row["relation_id"] == rid) for rid in rids]
    features = {page: {rep: Counter() for rep in REPS} for page in targets}
    host_rows_retained = 0
    with HOSTS.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] not in features: continue
            host_rows_retained += 1; page = row["page"]
            features[page]["PAGE_HOST_IDENTITY"][row["page_host"]] += 1
            add3(features[page]["PAGE_HOST_CHAR3"], row["page_host"])
            add3(features[page]["RAW_CHAR3"], row["token"])
            features[page]["COMPILER_SIGNATURE"]["|".join((row["wrapper"], row["inner_d"], row["local_frame"], row["right_family"], row["dy_closure"], row["b3"]))] += 1
    for row in group_rows:
        if row["page"] in features: add3(features[row["page"]]["SOURCE_FAMILY_CHAR3"], row["family_surface"])
    permutations = list(itertools.permutations(range(5)))
    rebuilt_matrix = {}; summaries = []; worlds = np.zeros((120, 15)); col = 0
    for edition in EDITIONS:
        byrid = {row["relation_id"]: row for row in queries if row["edition"] == edition}
        for rep in REPS:
            matrix = np.array([[sim(qvec(byrid[rid], rep), features[page][rep]) for page in targets] for rid in rids])
            for i, rid in enumerate(rids):
                for j, page in enumerate(targets): rebuilt_matrix[(edition, rep, rid, page)] = (matrix[i, j], 1 + int(np.sum(matrix[i] > matrix[i, j] + 1e-12)))
            scores = np.array([sum(matrix[i, perm[i]] for i in range(5)) for perm in permutations]); worlds[:, col] = scores
            true = float(scores[0]); summaries.append((edition, rep, true, 1 + int(np.sum(scores > true + 1e-12)), float(np.mean(scores >= true - 1e-12)), [1 + int(np.sum(matrix[i] > matrix[i, i] + 1e-12)) for i in range(5)])); col += 1
    mu = worlds.mean(0); sd = worlds.std(0); sd[sd == 0] = 1; maxz = ((worlds - mu) / sd).max(1)
    stored_matrix_map = {(row["edition"], row["representation"], row["relation_id"], row["candidate_target_page"]): (float(row["similarity"]), int(row["row_rank"])) for row in stored_matrix}
    stored_assign_map = {(row["edition"], row["representation"]): row for row in stored_assign}
    checks = {}
    checks["schema"] = result["schema"] == "GDT152_OWNED_LABEL_HPR2_PAGE_ADDRESS_RESULT_V1"
    checks["status"] = result["status"] == "OWNED_LABEL_HPR2_PAGE_ADDRESS_NOT_SUPPORTED"
    checks["query_capacity"] = len(queries) == 15 and len(rids) == len(set(targets)) == 5 and {row["edition"] for row in queries} == set(EDITIONS)
    checks["query_parser"] = parse_ok and len(licensed) == 50
    checks["target_rows"] = host_rows_retained > 0 and all(features[page]["RAW_CHAR3"] for page in targets)
    checks["matrix"] = len(stored_matrix) == 375 and stored_matrix_map.keys() == rebuilt_matrix.keys() and all(close(stored_matrix_map[key][0], rebuilt_matrix[key][0]) and stored_matrix_map[key][1] == rebuilt_matrix[key][1] for key in rebuilt_matrix)
    for j, (edition, rep, score, rank, tail, rowranks) in enumerate(summaries):
        row = stored_assign_map[(edition, rep)]
        checks[f"{edition}_{rep}"] = close(row["true_assignment_score"], score) and int(row["true_assignment_rank"]) == rank and close(row["inclusive_assignment_tail"], tail) and row["true_row_ranks"] == ",".join(map(str, rowranks)) and close(row["max_15_score_p"], np.mean(maxz >= (score - mu[j]) / sd[j] - 1e-12))
    checks["zero_exact_capacity"] = all(float(row["true_assignment_score"]) == 0 and float(row["inclusive_assignment_tail"]) == 1 for row in stored_assign if row["representation"] == "PAGE_HOST_IDENTITY")
    checks["host3_failure"] = [int(row["true_assignment_rank"]) for row in stored_assign if row["representation"] == "PAGE_HOST_CHAR3"] == [28, 28, 30]
    checks["raw_instability"] = [int(row["true_assignment_rank"]) for row in stored_assign if row["representation"] == "RAW_CHAR3"] == [8, 8, 31]
    checks["f84_absent"] = not any(row["label_locus"].startswith("f84") or row["target_page"].startswith("f84") for row in queries) and all(value is False for value in result["f84r"].values())
    checks["input_hashes"] = all((R / name).exists() and sha(R / name) == digest for name, digest in result["inputs"].items())
    checks["implementation_hash"] = all((R / name).exists() and sha(R / name) == digest for name, digest in result["implementation"].items())
    checks["output_hashes"] = all((R / name).exists() and sha(R / name) == digest for name, digest in result["outputs"].items())
    checks["document_hashes"] = all((R / name).exists() and sha(R / name) == digest for name, digest in result["documents"].items())
    content = dict(result); recorded = content.pop("result_content_sha256")
    checks["content_hash"] = hashlib.sha256(json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest() == recorded
    checks["claim_ceiling"] = all(word in result["claim_ceiling"] for word in ("no plant", "semantic role", "plaintext", "translation"))
    status = "PASS_INDEPENDENT_HPR2_PARSE_MATRIX_AND_120_ASSIGNMENT_RECONSTRUCTION" if all(checks.values()) else "FAIL"
    validation = {"schema": "GDT152_OWNED_LABEL_HPR2_PAGE_ADDRESS_VALIDATION_V1", "status": status,
                  "checks_total": len(checks), "checks_passed": sum(checks.values()), "checks": checks,
                  "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__))}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, "passed": sum(checks.values()), "total": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
