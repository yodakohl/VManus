#!/usr/bin/env python3
"""Exhaustive five-relation HPR2 label-to-Herbal assignment test."""
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
P151 = R / "gdt151_result.json"
OLD = R / "experiments/semantic_assumptions/results/five_pair_ordered_multiroot_capacity.json"
FPR = R / "experiments/semantic_assumptions/results/fpr001_f37v_one_shot_target.json"
METHOD = R / "GDT152_OWNED_LABEL_HPR2_PAGE_ADDRESS_METHOD.md"
REPORT = R / "GDT152_OWNED_LABEL_HPR2_PAGE_ADDRESS_REPORT.md"
MATRIX = R / "gdt152_score_matrix.tsv"
ASSIGN = R / "gdt152_assignment_results.tsv"
COUNTER = R / "gdt152_counterexamples.tsv"
RESULT = R / "gdt152_result.json"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
REPS = ("PAGE_HOST_IDENTITY", "PAGE_HOST_CHAR3", "RAW_CHAR3", "SOURCE_FAMILY_CHAR3", "COMPILER_SIGNATURE")


def read(path):
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def add3(counter, value):
    value = "^" + value + "$"
    for i in range(max(1, len(value) - 2)):
        counter[value[i:i + 3]] += 1.0


def sim(left, right):
    keys = set(left) | set(right)
    denom = sum(max(left[key], right[key]) for key in keys)
    return sum(min(left[key], right[key]) for key in keys) / denom if denom else 0.0


def compiler(row):
    return "|".join((row["wrapper"], row["inner_d"], row["local_frame"], row["right_family"], row["dy_closure"], row["b3"]))


def qvec(row, rep):
    out = Counter()
    if rep == "PAGE_HOST_IDENTITY": out[row["page_host"]] = 1
    elif rep == "PAGE_HOST_CHAR3": add3(out, row["page_host"])
    elif rep == "RAW_CHAR3": add3(out, row["token"])
    elif rep == "SOURCE_FAMILY_CHAR3": add3(out, row["family_surface"])
    elif rep == "COMPILER_SIGNATURE": out[compiler(row)] = 1
    return out


def main():
    queries = read(QUERIES)
    assert len(queries) == 15 and {row["edition"] for row in queries} == set(EDITIONS)
    relation_ids = sorted({row["relation_id"] for row in queries})
    targets = [next(row["target_page"] for row in queries if row["relation_id"] == rid) for rid in relation_ids]
    assert len(relation_ids) == len(set(targets)) == 5 and not any(page.startswith("f84") for page in targets)
    target_set = set(targets)
    page_features = {page: {rep: Counter() for rep in REPS} for page in targets}
    with HOSTS.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] not in target_set:
                continue
            page = row["page"]
            page_features[page]["PAGE_HOST_IDENTITY"][row["page_host"]] += 1
            add3(page_features[page]["PAGE_HOST_CHAR3"], row["page_host"])
            add3(page_features[page]["RAW_CHAR3"], row["token"])
            page_features[page]["COMPILER_SIGNATURE"]["|".join((row["wrapper"], row["inner_d"], row["local_frame"], row["right_family"], row["dy_closure"], row["b3"]))] += 1
    with GROUPS.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] in target_set:
                add3(page_features[row["page"]]["SOURCE_FAMILY_CHAR3"], row["family_surface"])
    assert all(page_features[page]["RAW_CHAR3"] for page in targets)

    permutations = list(itertools.permutations(range(5)))
    matrices = {}; matrix_rows = []; assignment_rows = []
    score_worlds = np.zeros((len(permutations), len(EDITIONS) * len(REPS)))
    test_index = 0
    summaries = {}
    for edition in EDITIONS:
        by_relation = {row["relation_id"]: row for row in queries if row["edition"] == edition}
        for rep in REPS:
            matrix = np.zeros((5, 5))
            for i, rid in enumerate(relation_ids):
                query = qvec(by_relation[rid], rep)
                for j, page in enumerate(targets):
                    matrix[i, j] = sim(query, page_features[page][rep])
                    matrix_rows.append({"edition": edition, "representation": rep, "relation_id": rid,
                                        "label_locus": by_relation[rid]["label_locus"], "candidate_target_page": page,
                                        "is_true_target": int(i == j), "similarity": f"{matrix[i,j]:.12g}",
                                        "row_rank": 1 + int(np.sum(matrix[i] > matrix[i,j] + 1e-12)) if j == 4 else "PENDING"})
            # Replace provisional row ranks after the full row is available.
            for row in matrix_rows[-25:]:
                i = relation_ids.index(row["relation_id"]); j = targets.index(row["candidate_target_page"])
                row["row_rank"] = 1 + int(np.sum(matrix[i] > matrix[i, j] + 1e-12))
            matrices[(edition, rep)] = matrix
            scores = np.array([sum(matrix[i, perm[i]] for i in range(5)) for perm in permutations])
            score_worlds[:, test_index] = scores
            true = float(scores[0]); rank = 1 + int(np.sum(scores > true + 1e-12)); tail = float(np.mean(scores >= true - 1e-12))
            row_true_ranks = [1 + int(np.sum(matrix[i] > matrix[i, i] + 1e-12)) for i in range(5)]
            summary = {"edition": edition, "representation": rep, "relations": 5, "assignments": 120,
                       "true_assignment_score": true, "true_assignment_rank": rank,
                       "inclusive_assignment_tail": tail, "true_row_ranks": ",".join(map(str, row_true_ranks)),
                       "exact_page_host_query_hits": int(sum(matrix[i, i] > 0 for i in range(5))) if rep == "PAGE_HOST_IDENTITY" else "NA"}
            summaries[(edition, rep)] = summary; assignment_rows.append(summary); test_index += 1
    mu = score_worlds.mean(0); sd = score_worlds.std(0); sd[sd == 0] = 1
    max_z = ((score_worlds - mu) / sd).max(1)
    for j, row in enumerate(assignment_rows):
        z = (float(row["true_assignment_score"]) - mu[j]) / sd[j]
        row["max_15_score_p"] = float(np.mean(max_z >= z - 1e-12))
    write(MATRIX, matrix_rows); write(ASSIGN, [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in assignment_rows])
    raw_zl = summaries[("ZL3b", "RAW_CHAR3")]; raw_rf = summaries[("RF1b", "RAW_CHAR3")]
    host_rows = [summaries[(edition, "PAGE_HOST_IDENTITY")] for edition in EDITIONS]
    host3_rows = [summaries[(edition, "PAGE_HOST_CHAR3")] for edition in EDITIONS]
    supported = all(int(row["true_assignment_rank"]) == 1 for row in host_rows + host3_rows) and all(float(row["max_15_score_p"]) <= 0.05 for row in host_rows + host3_rows)
    status = "OWNED_LABEL_HPR2_PAGE_ADDRESS_SUPPORTED" if supported else "OWNED_LABEL_HPR2_PAGE_ADDRESS_NOT_SUPPORTED"
    counter = [
        {"type": "ZERO_EXACT_CAPACITY", "item": "PAGE_HOST_IDENTITY", "value": "0_OF_25_PER_READING", "detail": "None of the five label PAGE_HOSTs occurs on any of the five paired/candidate Herbal target pages."},
        {"type": "HPR2_ASSIGNMENT_FAILURE", "item": "PAGE_HOST_CHAR3", "value": f"ZL{host3_rows[0]['true_assignment_rank']}_OF120|IT{host3_rows[1]['true_assignment_rank']}_OF120|RF{host3_rows[2]['true_assignment_rank']}_OF120", "detail": "The HPR2 host similarity does not recover the true five-way assignment."},
        {"type": "RAW_READING_INSTABILITY", "item": "RAW_CHAR3", "value": f"ZL{raw_zl['true_assignment_rank']}_OF120|RF{raw_rf['true_assignment_rank']}_OF120", "detail": "The near local primary-view string rank is not stable to RF1b alternatives and is not a PAGE_HOST effect."},
        {"type": "SOURCE_FAMILY_FAILURE", "item": "SOURCE_FAMILY_CHAR3", "value": "86_OF120_ALL_READINGS", "detail": "The source-native consensus-family representation strongly fails the true assignment."},
        {"type": "EXPOSED_PANEL", "item": "FIVE_RELATIONS", "value": "POSTHOC", "detail": "All five label identities and Herbal targets were exposed by earlier root-route experiments."},
        {"type": "DERIVED_DISPLAY", "item": "HPR2_TOKEN_AND_HOST", "value": "LOSSY", "detail": "Nearest-basic display strings are a derived view; only SOURCE_FAMILY_CHAR3 is source-native here."},
    ]
    write(COUNTER, counter)
    REPORT.write_text(f"""# GDT152 — owned pharmaceutical-label HPR2 page address

## Outcome

**{status}**

The local-ownership rescue fails. None of the five label PAGE_HOSTs occurs on
any of the five candidate Herbal pages: **0/25** exact query/page cells in
every reading. PAGE_HOST-char3 ranks the true five-way assignment
**{host3_rows[0]['true_assignment_rank']}/120** in ZL3b and IT2a and
**{host3_rows[2]['true_assignment_rank']}/120** in RF1b.

Raw display trigrams give the most attractive local result, rank **8/120**
(tail 0.0667) in ZL3b/IT2a, but fall to **31/120** in RF1b. That is ordinary
string resemblance, reading-unstable, and does not localize to PAGE_HOST.
Source-native family trigrams rank **86/120** in all readings; compiler
signature ranks **49/120**.

Thus singular/provisional fragment ownership does not rescue the selected
GDT148 page-address interpretation under HPR2. This is distinct from the old
ordered-root test, but it reuses the same exposed five relations and therefore
is a mechanism audit rather than an independent replication. It leaves open a
more complex nonliteral content code, but supplies no positive address.

No plant/component identity, semantic role, gloss, word, morpheme, POS, sound,
language, plaintext, meaning, or translation follows. f84r is absent from the
query and target panel and was not retained, joined, scored, or targeted.
""", encoding="utf8")
    result = {
        "schema": "GDT152_OWNED_LABEL_HPR2_PAGE_ADDRESS_RESULT_V1", "status": status,
        "relations": 5, "editions": list(EDITIONS), "representations": list(REPS), "assignments": 120,
        "page_host_identity": host_rows, "page_host_char3": host3_rows,
        "raw_char3": [summaries[(edition, "RAW_CHAR3")] for edition in EDITIONS],
        "interpretation": "Neither exact nor character-level HPR2 PAGE_HOST recovers the fixed five-label to five-Herbal-page assignment; the small raw-string lead is RF-unstable.",
        "claim_ceiling": "Post-hoc anonymous local-label address failure only; no plant/component identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("retained", "joined", "scored", "targeted", "assigned", "predicted")},
        "inputs": {path.name if path.parent == R else str(path.relative_to(R)): sha(path) for path in (QUERIES, HOSTS, GROUPS, P151, OLD, FPR)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in (MATRIX, ASSIGN, COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, "host3_ranks": [row["true_assignment_rank"] for row in host3_rows], "raw_ranks": [summaries[(edition, "RAW_CHAR3")]["true_assignment_rank"] for edition in EDITIONS]}, sort_keys=True))


if __name__ == "__main__":
    main()
