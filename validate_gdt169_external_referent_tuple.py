#!/usr/bin/env python3
"""Independent reconstruction of the GDT169 referent/tuple atlas."""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
RESULT = R / "gdt169_result.json"
VALIDATION = R / "gdt169_validation.json"


def read(path):
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def wj(left, right):
    keys = set(left) | set(right)
    denom = sum(max(left[k], right[k]) for k in keys)
    return sum(min(left[k], right[k]) for k in keys) / denom if denom else 0.0


def closure(row):
    return "DY" if row["dy_closure"] == "1" else ("B3" if row["b3"] == "1" else "OPEN")


def tkey(row):
    return "|".join((row["position_quartile"], row["wrapper"], row["page_host"], row["right_family"], closure(row)))


def close(a, b):
    return abs(float(a) - float(b)) <= 2e-10


def main():
    result = json.loads(RESULT.read_text())
    checks = []
    def ck(name, value):
        checks.append((name, bool(value)))

    content = dict(result); observed_content = content.pop("result_content_sha256")
    ck("result_content_hash", csha(content) == observed_content)
    ck("status_literal", result["status"] == "NO_REPLICATED_EXTERNAL_REFERENT_INVARIANCE")

    for name, digest in result["inputs"].items(): ck("input_hash_" + name, sha(R / name) == digest)
    for name, digest in result["outputs"].items(): ck("output_hash_" + name, sha(R / name) == digest)
    for name, digest in result["documents"].items(): ck("document_hash_" + name, sha(R / name) == digest)
    for name, digest in result["implementation"].items(): ck("implementation_hash_" + name, sha(R / name) == digest)

    candidates = read(R / "gdt169_external_referent_candidates.tsv")
    scores = read(R / "gdt169_referent_tuple_scores.tsv")
    local_scores = read(R / "gdt169_local_query_scores.tsv")
    freeze = json.loads((R / "gdt169_external_referent_source_audit.json").read_text())
    correction = json.loads((R / "gdt169_source_access_correction.json").read_text())
    ck("corrected_freeze_status", freeze["status"] == "CORRECTED_FROZEN_40_SOURCE_BOUND_RELATION_PAIRS_BEFORE_FORMAL_SCORING")
    ck("correction_hash_bound", freeze["source_access_correction"]["sha256"] == sha(R / freeze["source_access_correction"]["artifact"]))
    ck("correction_discloses_transient_human_row", correction["f84_exposure"]["description"].startswith("The superseded builder materialized"))
    ck("correction_zero_scientific_use", not correction["f84_exposure"]["formal_or_transcription_payload_accessed"] and not correction["f84_exposure"]["image_accessed"] and not correction["f84_exposure"]["retained_in_candidate_or_score"] and not correction["f84_exposure"]["used_for_selection_or_scoring"])
    ck("result_binds_access_correction", result["source_access_correction"] == freeze["source_access_correction"])
    ck("forty_candidates", len(candidates) == 40 == len(scores))
    ck("candidate_ids_exact", {x["candidate_id"] for x in candidates} == {x["candidate_id"] for x in scores})
    ck("zero_text_selected", all(x["selected_from_voynich_text"] == "0" for x in candidates))
    ck("ten_corroborated", sum(x["cross_source_corroborated"] == "1" for x in candidates) == 10)
    ck("five_local_queries", sum(x["local_query_locus"] != "NONE" for x in candidates) == 5 == len(local_scores))
    ck("zero_f84_candidate", not any(x["source_page"].startswith("f84") or x["target_page"].startswith("f84") for x in candidates))

    by_page = defaultdict(list); f84r = 0; f84other = 0
    with (R / "gdt062_right_family_inventory.tsv").open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page = row["page"]
            if page.startswith("f84r"): f84r += 1; continue
            if page.startswith("f84"): f84other += 1; continue
            by_page[page].append(row)
    ck("source_zero_f84r", f84r == 0)
    ck("other_f84_rejected", f84other == 228)
    ck("non_f84_pages", len(by_page) == 193)

    feat = {}; meta = {}
    for page, rows in by_page.items():
        hs = Counter(); ts = Counter()
        mm = {(x["section"], x["currier"], x["hand"], x["physical_folio"]) for x in rows}
        ck("metadata_single_" + page, len(mm) == 1)
        meta[page] = next(iter(mm))
        for x in rows: hs[x["page_host"]] += 1; ts[tkey(x)] += 1
        feat[page] = (hs, ts)

    by_score = {x["candidate_id"]: x for x in scores}
    rebuilt = 0
    for c in candidates:
        x = by_score[c["candidate_id"]]; a = c["source_page"]; b = c["target_page"]
        if a not in feat or b not in feat:
            ck("missing_status_" + c["candidate_id"], x["formal_status"] == "INSUFFICIENT_FORMAL_CAPACITY")
            continue
        rebuilt += 1
        section, currier, hand, _ = meta[b]
        pool = sorted(p for p, m in meta.items() if m[:3] == (section, currier, hand) and meta[p][3] != meta[a][3])
        ck("pool_n_" + c["candidate_id"], int(x["candidate_pool_pages"]) == len(pool) and b in pool)
        for idx, label in ((0, "host"), (1, "tuple")):
            vals = [wj(feat[a][idx], feat[p][idx]) for p in pool]; obs = wj(feat[a][idx], feat[b][idx])
            mu = sum(vals) / len(vals); sd = math.sqrt(sum((v-mu)**2 for v in vals)/len(vals)) or 1
            ck(label + "_sim_" + c["candidate_id"], close(obs, x[label + "_similarity"]))
            ck(label + "_rank_" + c["candidate_id"], int(x[label + "_rank"]) == 1 + sum(v > obs + 1e-12 for v in vals))
            ck(label + "_z_" + c["candidate_id"], close((obs-mu)/sd, x[label + "_z"]))
    ck("thirty_eight_scored", rebuilt == 38 == result["scorable_page_pairs"])

    local_queries = {x["label_locus"]: x for x in read(R / "gdt152_relation_queries.tsv") if x["edition"] == "ZL3b" and not x["label_locus"].startswith("f84")}
    local_host_hits = 0
    for x in local_scores:
        q = local_queries[x["label_locus"]]; page = x["paired_herbal_page"]
        count = feat[page][0][q["page_host"]]; local_host_hits += count > 0
        ck("local_host_count_" + x["candidate_id"], int(x["paired_page_host_occurrences"]) == count)
        ck("local_logical_tuple_" + x["candidate_id"], count > 0 or (x["full_tuple_invariant"] == "0" and x["full_tuple_evaluation_basis"] == "LOGICAL_SUBSET_OF_ABSENT_HOST"))
    ck("zero_local_host_hits", local_host_hits == 0 == result["local_query_exact_hits"]["page_host"])
    ck("zero_local_tuple_hits", sum(int(x["full_tuple_invariant"]) for x in local_scores) == 0 == result["local_query_exact_hits"]["full_tuple"])

    summary = {x["subset"]: x for x in read(R / "gdt169_aggregate_summary.tsv")}
    all_scored = [x for x in scores if x["formal_status"] == "SCORED"]
    hm = sum(float(x["host_z"]) for x in all_scored) / len(all_scored)
    tm = sum(float(x["tuple_z"]) for x in all_scored) / len(all_scored)
    ck("aggregate_host_mean", close(hm, summary["ALL_SCORABLE"]["host_mean_z"]))
    ck("aggregate_tuple_mean", close(tm, summary["ALL_SCORABLE"]["tuple_mean_z"]))
    ck("aggregate_result_host", close(hm, result["aggregate"]["ALL_SCORABLE"]["host_mean_z"]))
    ck("aggregate_result_tuple", close(tm, result["aggregate"]["ALL_SCORABLE"]["tuple_mean_z"]))
    ck("no_host_neighbor_outputs", not any("neighbor" in x.lower() for x in result["outputs"]))
    ck("f84_result_zero", result["f84"]["source_f84r_rows"] == 0 and result["f84"]["retained_joined_scored_rows"] == 0 and not result["f84"]["image_access"])

    failed = [name for name, ok in checks if not ok]
    validation = {
        "schema": "GDT169_EXTERNAL_REFERENT_TUPLE_VALIDATION_V1",
        "status": f"PASS_{len(checks)}_CHECK_INDEPENDENT_SOURCE_METRIC_AND_BINDING_RECONSTRUCTION" if not failed else "FAIL",
        "checks": len(checks), "failed": failed,
        "scope": "Independently reconstructs the candidate bindings, f84 exclusion, every page-pair host/tuple similarity/rank/z, local host absence, aggregate means, and artifact hashes; it does not claim independent human visual judgment.",
        "result_sha256": sha(RESULT), "result_content_sha256": observed_content,
    }
    validation["validation_content_sha256"] = csha(validation)
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf8")
    if failed: raise SystemExit(json.dumps(validation, sort_keys=True))
    print(json.dumps({"status": validation["status"], "decision": result["status"]}, sort_keys=True))


if __name__ == "__main__":
    main()
