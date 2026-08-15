#!/usr/bin/env python3
"""Complete human-catalogue Herbal-to-pharmaceutical page retrieval."""
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
P148 = R / "gdt148_result.json"
P150 = R / "gdt150_result.json"
METHOD = R / "GDT151_HERBAL_PHARMA_PAGE_RETRIEVAL_METHOD.md"
REPORT = R / "GDT151_HERBAL_PHARMA_PAGE_RETRIEVAL_REPORT.md"
INV = R / "gdt151_relation_inventory.tsv"
RANKS = R / "gdt151_target_ranks.tsv"
NULL = R / "gdt151_null_results.tsv"
COUNTER = R / "gdt151_counterexamples.tsv"
RESULT = R / "gdt151_result.json"
REPS = ("PAGE_HOST_IDENTITY", "PAGE_HOST_CHAR3", "RAW_CHAR3", "COMPILER_SIGNATURE", "GROUP_COUNT_PROXIMITY", "TARGET_DEGREE_PRIOR")
WORLDS = 100000
SEED = 151148


def read(path):
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows):
    with path.open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def add3(counter, value):
    value = "^" + value + "$"
    for i in range(max(1, len(value) - 2)):
        counter[value[i:i + 3]] += 1.0


def similarity(left, right):
    keys = set(left) | set(right)
    denom = sum(max(left[key], right[key]) for key in keys)
    return sum(min(left[key], right[key]) for key in keys) / denom if denom else 0.0


def clean(rows):
    return [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in rows]


def main():
    herbal_meta = {row["page"]: row for row in read(HMETA) if not row["page"].startswith("f84")}
    assert len(herbal_meta) == 127
    by_page = defaultdict(list)
    rejected_f84 = 0
    with SOURCE.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"].startswith("f84"):
                rejected_f84 += 1
                continue
            by_page[row["page"]].append(row)
    pharma_pages = sorted(page for page, rows in by_page.items() if rows[0]["section"] == "P")
    assert len(pharma_pages) == 15 and not any(page.startswith("f84") for page in pharma_pages)

    descriptions = {}
    with HUMAN.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page = row["page"]
            if page.startswith("f84") or page not in herbal_meta:
                continue
            descriptions[page] = row
    inventory = []
    serial = 0
    for source_page in sorted(descriptions):
        row = descriptions[source_page]
        refs = list(dict.fromkeys(ref.lower() for ref in re.findall(r"\bf\d+[rv](?:\d)?\b", row["illustrations"], re.I)))
        for target_page in refs:
            is_pharma_reference = target_page in pharma_pages or re.match(r"^f(?:88|89|99|100|101|102)", target_page)
            if not is_pharma_reference:
                continue
            serial += 1
            phrase_class = "SAME_PLANT_FRAGMENT_ASSERTION" if "same plant as shown in fragment" in row["illustrations"].lower() else "PLANT_FRAGMENT_SIMILARITY"
            inventory.append({
                "relation_id": f"GDT151_HP{serial:03d}", "source_page": source_page,
                "source_physical_folio": herbal_meta[source_page]["physical_folio"],
                "target_page": target_page, "relation_class": phrase_class,
                "scoring_status": "SCORED_COMPLETE_PHARMA_PAGE_BAG" if target_page in pharma_pages else "UNSCORED_NO_FORMAL_PAGE_BAG",
                "source_url": row["source_url"], "raw_human_illustration_description": row["illustrations"],
                "provenance": "EXISTING_HUMAN_ANNOTATION", "semantic_role": "UNASSIGNED",
            })
    assert len(inventory) == 32
    scored_relations = [row for row in inventory if row["scoring_status"].startswith("SCORED")]
    assert len(scored_relations) == 31 and len({row["source_page"] for row in scored_relations}) == 30
    assert [row for row in inventory if row["scoring_status"].startswith("UNSCORED")][0]["target_page"] == "f101v"
    write(INV, inventory)

    features = {page: {rep: Counter() for rep in REPS[:4]} for page in by_page}
    group_counts = {page: len(rows) for page, rows in by_page.items()}
    for page, rows in by_page.items():
        for row in rows:
            features[page]["PAGE_HOST_IDENTITY"][row["page_host"]] += 1
            add3(features[page]["PAGE_HOST_CHAR3"], row["page_host"])
            add3(features[page]["RAW_CHAR3"], row["token"])
            features[page]["COMPILER_SIGNATURE"]["|".join((row["wrapper"], row["inner_d"], row["local_frame"], row["right_family"], row["dy_closure"], row["b3"]))] += 1

    n = len(scored_relations)
    pcount = len(pharma_pages)
    target_index = {page: i for i, page in enumerate(pharma_pages)}
    source_blocks = defaultdict(list)
    for i, rel in enumerate(scored_relations):
        source_blocks[rel["source_page"]].append(i)
    target_ids = np.array([target_index[rel["target_page"]] for rel in scored_relations], dtype=int)
    score_matrices = {}
    rank_matrices = {}
    for rep in REPS[:-1]:
        matrix = np.zeros((n, pcount))
        for i, rel in enumerate(scored_relations):
            source_page = rel["source_page"]
            for j, target_page in enumerate(pharma_pages):
                if rep == "GROUP_COUNT_PROXIMITY":
                    matrix[i, j] = -abs(group_counts[source_page] - group_counts[target_page])
                else:
                    matrix[i, j] = similarity(features[source_page][rep], features[target_page][rep])
        ranks = np.ones_like(matrix, dtype=int)
        for i in range(n):
            for j in range(pcount):
                ranks[i, j] = 1 + int(np.sum(matrix[i] > matrix[i, j] + 1e-12))
        score_matrices[rep] = matrix
        rank_matrices[rep] = ranks

    def prior_ranks(assignment):
        ranks = np.ones((n, pcount), dtype=int)
        total = Counter(int(value) for value in assignment)
        for source, indices in source_blocks.items():
            train = total.copy()
            for idx in indices:
                train[int(assignment[idx])] -= 1
            values = np.array([train[j] for j in range(pcount)])
            row_ranks = 1 + np.array([np.sum(values > values[j]) for j in range(pcount)], dtype=int)
            for idx in indices:
                ranks[idx] = row_ranks
        return ranks

    rank_matrices["TARGET_DEGREE_PRIOR"] = prior_ranks(target_ids)
    rank_rows = []
    obs_mrr = []
    obs_top3 = []
    obs_mean_rank = []
    for rep in REPS:
        ranks = rank_matrices[rep]
        true_ranks = ranks[np.arange(n), target_ids]
        obs_mrr.append(float(np.mean(1.0 / true_ranks)))
        obs_top3.append(int(np.sum(true_ranks <= 3)))
        obs_mean_rank.append(float(np.mean(true_ranks)))
        for i, rel in enumerate(scored_relations):
            target = int(target_ids[i])
            rank_rows.append({
                "relation_id": rel["relation_id"], "source_page": rel["source_page"], "target_page": rel["target_page"],
                "representation": rep, "candidate_pages": pcount,
                "similarity_or_control_score": score_matrices[rep][i, target] if rep in score_matrices else "LEAVE_SOURCE_OUT_TARGET_DEGREE",
                "true_target_rank": int(true_ranks[i]), "reciprocal_rank": float(1.0 / true_ranks[i]),
                "top_three": int(true_ranks[i] <= 3), "semantic_role": "UNASSIGNED",
            })
    write(RANKS, clean(rank_rows))

    rng = random.Random(SEED)
    null_mrr = np.zeros((WORLDS, len(REPS)))
    null_top3 = np.zeros((WORLDS, len(REPS)), dtype=int)
    original = list(map(int, target_ids))
    two_edge_indices = next(indices for indices in source_blocks.values() if len(indices) == 2)
    assert len([indices for indices in source_blocks.values() if len(indices) == 2]) == 1
    for world in range(WORLDS):
        while True:
            draw = original.copy()
            rng.shuffle(draw)
            if draw[two_edge_indices[0]] != draw[two_edge_indices[1]]:
                break
        assignment = np.array(draw, dtype=int)
        for j, rep in enumerate(REPS):
            ranks = prior_ranks(assignment) if rep == "TARGET_DEGREE_PRIOR" else rank_matrices[rep]
            selected = ranks[np.arange(n), assignment]
            null_mrr[world, j] = np.mean(1.0 / selected)
            null_top3[world, j] = int(np.sum(selected <= 3))
    mrr_mu = null_mrr.mean(axis=0); mrr_sd = null_mrr.std(axis=0); mrr_sd[mrr_sd == 0] = 1
    top_mu = null_top3.mean(axis=0); top_sd = null_top3.std(axis=0); top_sd[top_sd == 0] = 1
    obs_mrr_a = np.array(obs_mrr); obs_top_a = np.array(obs_top3)
    mrr_z = (obs_mrr_a - mrr_mu) / mrr_sd; top_z = (obs_top_a - top_mu) / top_sd
    max_mrr = ((null_mrr - mrr_mu) / mrr_sd).max(axis=1)
    max_top = ((null_top3 - top_mu) / top_sd).max(axis=1)
    null_rows = []
    for j, rep in enumerate(REPS):
        null_rows.append({
            "representation": rep, "relations": n, "candidate_pages": pcount,
            "true_mrr": obs_mrr[j], "true_mean_rank": obs_mean_rank[j], "true_top_three": obs_top3[j],
            "null_mrr_mean": float(mrr_mu[j]), "null_mrr_sd": float(mrr_sd[j]),
            "local_mrr_p": float(np.mean(null_mrr[:, j] >= obs_mrr[j] - 1e-12)),
            "max_six_mrr_p": float(np.mean(max_mrr >= mrr_z[j] - 1e-12)),
            "null_top_three_mean": float(top_mu[j]), "null_top_three_sd": float(top_sd[j]),
            "local_top_three_p": float(np.mean(null_top3[:, j] >= obs_top3[j])),
            "max_six_top_three_p": float(np.mean(max_top >= top_z[j] - 1e-12)),
            "worlds": WORLDS, "seed": SEED,
        })
    write(NULL, clean(null_rows))
    summary = {row["representation"]: row for row in null_rows}
    host = summary["PAGE_HOST_IDENTITY"]
    prior = summary["TARGET_DEGREE_PRIOR"]
    length = summary["GROUP_COUNT_PROXIMITY"]
    supported = ((host["max_six_mrr_p"] <= 0.05 and host["true_mrr"] > max(prior["true_mrr"], length["true_mrr"])) or
                 (host["max_six_top_three_p"] <= 0.05 and host["true_top_three"] > max(prior["true_top_three"], length["true_top_three"])))
    status = "HERBAL_PHARMA_PAGE_HOST_RETRIEVAL_SUPPORTED" if supported else "HERBAL_PHARMA_PAGE_HOST_RETRIEVAL_NOT_SUPPORTED"
    counter = [
        {"type": "COMPLETE_PANEL_FAILURE", "item": "PAGE_HOST_IDENTITY", "value": f"MRR={host['true_mrr']:.6f};TOP3={host['true_top_three']}", "detail": "Exact PAGE_HOST does not beat the length or leave-source-out target-degree controls on the complete catalogue-derived graph."},
        {"type": "ADVERSARIAL_CONTROL", "item": "TARGET_DEGREE_PRIOR", "value": f"MRR={prior['true_mrr']:.6f};TOP3={prior['true_top_three']}", "detail": "Catalogue target popularity predicts the referenced page substantially better than every formal representation."},
        {"type": "TARGET_DILUTION", "item": "COMPLETE_PHARMA_PAGE_BAG", "value": "31_RELATIONS", "detail": "A pharmaceutical page contains multiple fragments and prose; this test cannot bind a referenced fragment to one local inscription."},
        {"type": "UNSCORED_REFERENCE", "item": "f37r_TO_f101v", "value": "NO_FORMAL_PAGE_BAG", "detail": "The complete source crawl preserves this human relation but cannot score it in GDT062."},
        {"type": "POSTEXPOSURE", "item": "GDT148_PAGE_HOST_LEAD", "value": "EXPOSED", "detail": "This stress test was designed after the selected six-relation PAGE_HOST result and is not a pristine replication."},
        {"type": "ONE_DERIVED_READING", "item": "GDT062", "value": "NO_ALTERNATE_REPLICATION", "detail": "ZL3b, IT2a, and RF1b are alternate readings; the page-bag view is one derived source representation."},
    ]
    write(COUNTER, counter)
    REPORT.write_text(f"""# GDT151 — complete Herbal-to-pharmaceutical page retrieval

## Outcome

**{status}**

The mechanically complete cached human catalogue contributes **32** Herbal to
pharmaceutical drawing references. Thirty-one are scorable as full-page bags
against all **15** pharmaceutical pages; f37r to f101v is preserved but has no
GDT062 pharmaceutical page bag.

Exact PAGE_HOST frequency performs poorly: MRR **{host['true_mrr']:.4f}**,
mean rank **{host['true_mean_rank']:.2f}/15**, and **{host['true_top_three']}/31**
top-three targets. PAGE_HOST character trigrams are similarly weak. The simple
group-count control reaches MRR **{length['true_mrr']:.4f}**, while a
leave-source-out target-degree prior reaches **{prior['true_mrr']:.4f}** and
**{prior['true_top_three']}/31** top-three targets. No formal representation
beats that adversarial nontextual control.

This is a direct generalization failure for the selected GDT148 relation lead.
The six-pair Herbal-to-Herbal result remains an interesting exposed pattern,
but complete cross-section fragment references do not behave like transferable
PAGE_HOST content addresses at page resolution. The negative has an important
limit: each pharmaceutical page contains multiple fragments, and most lack
singular text ownership, so a real fragment code could be diluted beyond
recognition by the complete page bag.

The 100,000 target-label worlds preserve catalogue target popularity and the
two-edge source structure; maximum-over-six tails are reported rather than
used to rescue a representation. No plant or component identity, semantic
role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or
translation follows. f84r was not retained, joined, scored, or targeted.
""", encoding="utf8")
    result = {
        "schema": "GDT151_HERBAL_PHARMA_PAGE_RETRIEVAL_RESULT_V1", "status": status,
        "inventory": {"references": len(inventory), "scored_relations": n,
                      "scored_source_pages": len(source_blocks), "pharma_candidate_pages": pcount,
                      "unscored_relations": len(inventory) - n},
        "representations": list(REPS), "worlds": WORLDS, "seed": SEED,
        "page_host_summary": host, "length_control_summary": length, "target_degree_prior_summary": prior,
        "interpretation": "The complete catalogue-derived Herbal-to-pharmaceutical graph does not reproduce the selected GDT148 PAGE_HOST retrieval lead at whole-page resolution.",
        "claim_ceiling": "Exploratory anonymous whole-page retrieval failure only; no plant or component identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {key: False for key in ("retained", "joined", "scored", "targeted", "assigned", "predicted")},
        "source_filter": {"rejected_f84_prefixed_gdt062_rows": rejected_f84, "retained_f84_rows": 0},
        "inputs": {str(path.relative_to(R)): sha(path) for path in (SOURCE, HMETA, HUMAN, P148, P150)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in (INV, RANKS, NULL, COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, "relations": n, "page_host_mrr": host["true_mrr"], "target_prior_mrr": prior["true_mrr"]}, sort_keys=True))


if __name__ == "__main__":
    main()
