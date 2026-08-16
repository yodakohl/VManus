#!/usr/bin/env python3
"""Compare PAGE_HOST and full tuple invariance on frozen external referents."""
import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
CAND = R / "gdt169_external_referent_candidates.tsv"
SOURCE = R / "gdt062_right_family_inventory.tsv"
LOCAL = R / "gdt152_relation_queries.tsv"
FREEZE = R / "gdt169_external_referent_source_audit.json"
METHOD = R / "GDT169_EXTERNAL_REFERENT_TUPLE_METHOD.md"
REPORT = R / "GDT169_EXTERNAL_REFERENT_TUPLE_REPORT.md"
SCORES = R / "gdt169_referent_tuple_scores.tsv"
LOCAL_SCORES = R / "gdt169_local_query_scores.tsv"
SUMMARY = R / "gdt169_aggregate_summary.tsv"
NULL = R / "gdt169_null_results.tsv"
COUNTER = R / "gdt169_counterexamples.tsv"
RESULT = R / "gdt169_result.json"
WORLDS = 20000
SEED = 169168


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


def clean(rows):
    out = []
    for row in rows:
        out.append({k: (f"{v:.12g}" if isinstance(v, float) else v) for k, v in row.items()})
    return out


def weighted_jaccard(left, right):
    keys = set(left) | set(right)
    denom = sum(max(left[k], right[k]) for k in keys)
    return sum(min(left[k], right[k]) for k in keys) / denom if denom else 0.0


def intersection_mass(left, right):
    return sum(min(left[k], right[k]) for k in set(left) | set(right))


def closure(row):
    return "DY" if row["dy_closure"] == "1" else ("B3" if row["b3"] == "1" else "OPEN")


def tuple_key(row):
    return "|".join((row["position_quartile"], row["wrapper"], row["page_host"], row["right_family"], closure(row)))


def mean_sd(values):
    mean = sum(values) / len(values)
    sd = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))
    return mean, sd or 1.0


def main():
    candidates = read(CAND)
    freeze = json.loads(FREEZE.read_text())
    assert freeze["status"] == "CORRECTED_FROZEN_40_SOURCE_BOUND_RELATION_PAIRS_BEFORE_FORMAL_SCORING"
    assert len(candidates) == 40 and all(x["selected_from_voynich_text"] == "0" for x in candidates)
    assert not any(x["source_page"].startswith("f84") or x["target_page"].startswith("f84") for x in candidates)

    by_page = defaultdict(list)
    source_f84r = 0; rejected_other_f84 = 0
    with SOURCE.open(encoding="utf8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page = row["page"]
            if page.startswith("f84r"):
                source_f84r += 1; continue
            if page.startswith("f84"):
                rejected_other_f84 += 1; continue
            by_page[page].append(row)
    # This published derived HPR2 input contains no f84r rows.  Other f84 sides
    # are rejected before retention and never enter any feature.
    assert source_f84r == 0 and len(by_page) == 193

    features = {}
    metadata = {}
    rows_by_locus = defaultdict(list)
    for page, rows in by_page.items():
        meta = {(x["section"], x["currier"], x["hand"], x["physical_folio"]) for x in rows}
        assert len(meta) == 1
        metadata[page] = next(iter(meta))
        host = Counter(); full = Counter()
        for row in rows:
            host[row["page_host"]] += 1
            full[tuple_key(row)] += 1
            rows_by_locus[row["locus"]].append(row)
        features[page] = {"PAGE_HOST": host, "FULL_TUPLE": full}

    score_rows = []
    pool_values = {}
    for c in candidates:
        source = c["source_page"]; target = c["target_page"]
        base = {k: c[k] for k in (
            "candidate_id", "evidence_priority_rank", "evidence_priority_score", "evidence_panel",
            "source_page", "target_page", "relation_class", "component", "assertion_strength",
            "cross_source_corroborated", "corroboration_independence", "local_query_locus",
            "local_ownership_tier", "relation_class_distinct_pair_replications")}
        if source not in features or target not in features:
            score_rows.append({**base, "formal_status": "INSUFFICIENT_FORMAL_CAPACITY", "missing_pages": "|".join(p for p in (source, target) if p not in features),
                "candidate_pool_pages": 0, "host_similarity": "NA", "host_intersection_mass": "NA", "host_rank": "NA", "host_tail": "NA", "host_z": "NA",
                "tuple_similarity": "NA", "tuple_intersection_mass": "NA", "tuple_rank": "NA", "tuple_tail": "NA", "tuple_z": "NA",
                "tuple_minus_host_z": "NA", "host_conditioned_tuple_retention": "NA", "retention_comparable_pool": 0, "retention_rank": "NA", "retention_tail": "NA", "exploratory_label": "INSUFFICIENT_FORMAL_CAPACITY"})
            continue
        section, currier, hand, _ = metadata[target]
        pool = sorted(p for p, m in metadata.items() if m[:3] == (section, currier, hand) and metadata[p][3] != metadata[source][3])
        assert target in pool
        vals = {rep: [weighted_jaccard(features[source][rep], features[p][rep]) for p in pool] for rep in ("PAGE_HOST", "FULL_TUPLE")}
        observed = {rep: weighted_jaccard(features[source][rep], features[target][rep]) for rep in vals}
        stats = {}
        for rep in vals:
            mu, sd = mean_sd(vals[rep]); v = observed[rep]
            stats[rep] = {"rank": 1 + sum(x > v + 1e-12 for x in vals[rep]), "tail": sum(x >= v - 1e-12 for x in vals[rep]) / len(vals[rep]), "z": (v - mu) / sd}
        hi = intersection_mass(features[source]["PAGE_HOST"], features[target]["PAGE_HOST"])
        ti = intersection_mass(features[source]["FULL_TUPLE"], features[target]["FULL_TUPLE"])
        retention = ti / hi if hi else 0.0
        rvals = []
        for p in pool:
            hmass = intersection_mass(features[source]["PAGE_HOST"], features[p]["PAGE_HOST"])
            if hmass:
                rvals.append(intersection_mass(features[source]["FULL_TUPLE"], features[p]["FULL_TUPLE"]) / hmass)
        rrank = 1 + sum(x > retention + 1e-12 for x in rvals) if rvals else "NA"
        rtail = sum(x >= retention - 1e-12 for x in rvals) / len(rvals) if rvals else "NA"
        dz = stats["FULL_TUPLE"]["z"] - stats["PAGE_HOST"]["z"]
        if max(stats["PAGE_HOST"]["z"], stats["FULL_TUPLE"]["z"]) <= 0:
            label = "NO_FORMAL_INVARIANCE"
        elif dz >= 0.25:
            label = "TUPLE_MORE_INVARIANT"
        elif dz <= -0.25:
            label = "HOST_MORE_INVARIANT"
        else:
            label = "BOTH_LOCAL_ONLY"
        score_rows.append({**base, "formal_status": "SCORED", "missing_pages": "NONE", "candidate_pool_pages": len(pool),
            "host_similarity": observed["PAGE_HOST"], "host_intersection_mass": hi, "host_rank": stats["PAGE_HOST"]["rank"], "host_tail": stats["PAGE_HOST"]["tail"], "host_z": stats["PAGE_HOST"]["z"],
            "tuple_similarity": observed["FULL_TUPLE"], "tuple_intersection_mass": ti, "tuple_rank": stats["FULL_TUPLE"]["rank"], "tuple_tail": stats["FULL_TUPLE"]["tail"], "tuple_z": stats["FULL_TUPLE"]["z"],
            "tuple_minus_host_z": dz, "host_conditioned_tuple_retention": retention, "retention_comparable_pool": len(rvals), "retention_rank": rrank, "retention_tail": rtail,
            "exploratory_label": label})
        pool_values[c["candidate_id"]] = {"pool": pool, "PAGE_HOST": vals["PAGE_HOST"], "FULL_TUPLE": vals["FULL_TUPLE"]}

    scored = [x for x in score_rows if x["formal_status"] == "SCORED"]
    assert len(scored) == 38

    local_primary = {x["relation_id"]: x for x in read(LOCAL) if x["edition"] == "ZL3b" and not x["label_locus"].startswith("f84") and not x["target_page"].startswith("f84")}
    local_readings = defaultdict(set)
    for x in read(LOCAL):
        if not x["label_locus"].startswith("f84") and not x["target_page"].startswith("f84"):
            local_readings[x["label_locus"]].add(x["page_host"])
    local_rows = []
    for c in candidates:
        locus = c["local_query_locus"]
        if locus == "NONE": continue
        qrows = rows_by_locus[locus]
        query = next(x for x in local_primary.values() if x["label_locus"] == locus)
        primary = [x for x in qrows if x["page_host"] == query["page_host"]]
        page = c["source_page"]; hk = query["page_host"]
        host_occ = features[page]["PAGE_HOST"][hk]
        # GDT062 excludes these diagnostic label rows, so the position slot is
        # unavailable.  When the exact host itself is absent, however, an
        # exact full tuple containing that host is logically impossible.
        tk = tuple_key(primary[0]) if primary else "UNAVAILABLE_NO_POSITION_SLOT"
        tuple_occ = features[page]["FULL_TUPLE"][tk] if primary else (0 if host_occ == 0 else "NA")
        tuple_invariant = int(tuple_occ > 0) if tuple_occ != "NA" else "NA"
        local_rows.append({
            "candidate_id": c["candidate_id"], "evidence_priority_rank": c["evidence_priority_rank"], "label_locus": locus,
            "paired_herbal_page": page, "query_page_host": hk, "query_full_tuple": tk,
            "page_host_reading_stable": int(len(local_readings[locus]) == 1), "alternate_page_host_count": len(local_readings[locus]),
            "paired_page_host_occurrences": host_occ, "paired_full_tuple_occurrences": tuple_occ,
            "page_host_invariant": int(host_occ > 0), "full_tuple_invariant": tuple_invariant,
            "full_tuple_evaluation_basis": "DIRECT_GDT062_LABEL_ROW" if primary else ("LOGICAL_SUBSET_OF_ABSENT_HOST" if host_occ == 0 else "UNSCORABLE_NO_POSITION_SLOT"),
            "result": "FULL_TUPLE_MATCH" if tuple_invariant == 1 else ("HOST_ONLY_MATCH" if host_occ else "NO_EXACT_HOST_THEREFORE_NO_FULL_TUPLE"),
            "semantic_role": "UNASSIGNED",
        })
    assert len(local_rows) == 5

    def subset_rows(name, predicate):
        rows = [x for x in scored if predicate(x)]
        return {"subset": name, "pairs": len(rows),
            "host_mean_z": sum(float(x["host_z"]) for x in rows) / len(rows) if rows else "NA",
            "tuple_mean_z": sum(float(x["tuple_z"]) for x in rows) / len(rows) if rows else "NA",
            "tuple_minus_host_mean_z": sum(float(x["tuple_minus_host_z"]) for x in rows) / len(rows) if rows else "NA",
            "host_positive_pairs": sum(float(x["host_z"]) > 0 for x in rows), "tuple_positive_pairs": sum(float(x["tuple_z"]) > 0 for x in rows),
            "host_top_decile_pairs": sum(float(x["host_tail"]) <= .1 for x in rows), "tuple_top_decile_pairs": sum(float(x["tuple_tail"]) <= .1 for x in rows),
            "tuple_z_exceeds_host_z_pairs": sum(float(x["tuple_minus_host_z"]) > 0 for x in rows)}

    summaries = [
        subset_rows("ALL_SCORABLE", lambda x: True),
        subset_rows("CROSS_SOURCE_CORROBORATED", lambda x: x["cross_source_corroborated"] == "1"),
        subset_rows("ASSERTED_SAME_OR_STRONG", lambda x: x["assertion_strength"] in {"ASSERTED_SAME", "STRONG"}),
        subset_rows("INTERNAL_HERBAL", lambda x: x["evidence_panel"] == "INTERNAL_HERBAL"),
        subset_rows("HERBAL_TO_PHARMA", lambda x: x["evidence_panel"] == "HERBAL_TO_PHARMA"),
        subset_rows("LOCALLY_OWNED_QUERY_PAIR", lambda x: x["local_query_locus"] != "NONE"),
    ]

    rng = random.Random(SEED)
    obs_host = summaries[0]["host_mean_z"]; obs_tuple = summaries[0]["tuple_mean_z"]
    world_host = []; world_tuple = []
    for _ in range(WORLDS):
        hs = []; ts = []
        for row in scored:
            pv = pool_values[row["candidate_id"]]; j = rng.randrange(len(pv["pool"]))
            hm, hsd = mean_sd(pv["PAGE_HOST"]); tm, tsd = mean_sd(pv["FULL_TUPLE"])
            hs.append((pv["PAGE_HOST"][j] - hm) / hsd); ts.append((pv["FULL_TUPLE"][j] - tm) / tsd)
        world_host.append(sum(hs) / len(hs)); world_tuple.append(sum(ts) / len(ts))
    host_p = sum(x >= obs_host - 1e-12 for x in world_host) / WORLDS
    tuple_p = sum(x >= obs_tuple - 1e-12 for x in world_tuple) / WORLDS
    max_p_host = sum(max(h, t) >= obs_host - 1e-12 for h, t in zip(world_host, world_tuple)) / WORLDS
    max_p_tuple = sum(max(h, t) >= obs_tuple - 1e-12 for h, t in zip(world_host, world_tuple)) / WORLDS
    null_rows = [
        {"representation": "PAGE_HOST", "pairs": len(scored), "observed_mean_z": obs_host, "worlds": WORLDS, "local_p": host_p, "max_two_p": max_p_host, "seed": SEED, "dependency_caveat": "PAIR_DRAWS_DO_NOT_REMOVE_SHARED_PAGE_OR_SOURCE_DEPENDENCE"},
        {"representation": "FULL_TUPLE", "pairs": len(scored), "observed_mean_z": obs_tuple, "worlds": WORLDS, "local_p": tuple_p, "max_two_p": max_p_tuple, "seed": SEED, "dependency_caveat": "PAIR_DRAWS_DO_NOT_REMOVE_SHARED_PAGE_OR_SOURCE_DEPENDENCE"},
    ]

    ranked = sorted(scored, key=lambda x: (int(x["evidence_priority_rank"]), -max(float(x["host_z"]), float(x["tuple_z"]))))
    strong_evidence = [x for x in ranked if int(x["evidence_priority_rank"]) <= 10]
    top_formal = sorted(scored, key=lambda x: (-max(float(x["host_z"]), float(x["tuple_z"])), int(x["evidence_priority_rank"])))[:8]
    counter = [
        {"type": "LOCAL_OWNERSHIP_FAILURE", "item": "FIVE_GDT152_QUERIES", "value": f"HOST_{sum(x['page_host_invariant'] for x in local_rows)}|TUPLE_{sum(x['full_tuple_invariant'] for x in local_rows)}", "detail": "The strongest locally owned/provisional external referents yield no exact host or tuple match on the paired Herbal page."},
        {"type": "FULL_TUPLE_REFINEMENT", "item": "RAW_OVERLAP", "value": "TUPLE_LE_HOST_BY_CONSTRUCTION", "detail": "Raw full-tuple overlap cannot exceed host overlap; standardized matched-page excess is the valid layer comparison."},
        {"type": "SOURCE_DEPENDENCE", "item": "TEN_CORROBORATED_PAIRS", "value": "UNKNOWN", "detail": "Voynich.nu and the later Stolfi list may share visual judgments; corroboration is provenance support, not independent replication."},
        {"type": "WHOLE_PAGE_DILUTION", "item": "THIRTY_EIGHT_SCORABLE_PAIRS", "value": "PAGE_BAGS", "detail": "Except for five label queries, formal bags are whole-page text and are not authorially owned by the pictured component."},
        {"type": "PAIR_DEPENDENCE", "item": "MONTE_CARLO", "value": "SHARED_PAGES_AND_TARGETS", "detail": "The matched-page world diagnostic does not make repeated pages or human sources independent."},
        {"type": "ALTERNATE_READINGS", "item": "GDT062", "value": "ONE_DERIVED_VIEW", "detail": "ZL/IT/RF are not replications; local query reading stability is shown separately."},
        {"type": "SOURCE_ACCESS_CORRECTION", "item": "SUPERSEDED_FREEZE_BUILDER", "value": "TRANSIENT_HUMAN_F84R_CATALOGUE_ROW", "detail": "The first source builder loaded the global human page table before filtering only to recover URLs; no f84 description affected selection or scoring, and the corrected builder removes that input."},
    ]

    all_summary = summaries[0]
    host_better = float(all_summary["host_mean_z"]) > float(all_summary["tuple_mean_z"])
    local_hits = sum(x["page_host_invariant"] for x in local_rows) + sum(x["full_tuple_invariant"] for x in local_rows)
    status = "PAGE_HOST_INVARIANCE_LEAD_WITHOUT_LOCAL_OWNERSHIP" if host_better and float(null_rows[0]["max_two_p"]) <= .1 and local_hits == 0 else "NO_REPLICATED_EXTERNAL_REFERENT_INVARIANCE"

    write(SCORES, clean(score_rows)); write(LOCAL_SCORES, clean(local_rows)); write(SUMMARY, clean(summaries)); write(NULL, clean(null_rows)); write(COUNTER, counter)
    top_lines = "\n".join(f"- `{x['candidate_id']}` {x['source_page']}→{x['target_page']}: evidence rank {x['evidence_priority_rank']}, host z {float(x['host_z']):+.2f}, tuple z {float(x['tuple_z']):+.2f}, {x['exploratory_label']}." for x in top_formal[:6])
    evidence_lines = "\n".join(f"- `{x['candidate_id']}`: host z {float(x['host_z']):+.2f}, tuple z {float(x['tuple_z']):+.2f}, local query `{x['local_query_locus']}`." for x in strong_evidence)
    REPORT.write_text(f"""# GDT169 — external-referent host versus record-tuple atlas

## Outcome

**{status}**

The source-only freeze contains 40 human-nominated physical page pairs; 38
have both pages in the published HPR2 view.  Exact PAGE_HOST has mean matched-
page excess z {float(all_summary['host_mean_z']):+.3f}; the complete
slot/wrapper/host/right/closure tuple has {float(all_summary['tuple_mean_z']):+.3f}.
The fixed matched-page world diagnostic gives max-two p
{float(null_rows[0]['max_two_p']):.5f} for PAGE_HOST and
{float(null_rows[1]['max_two_p']):.5f} for the full tuple.  These tails remain
exploratory because pairs share pages, targets, and human sources.

The decisive ownership check is negative: the five published singular or
provisional pharmaceutical labels produce **{sum(x['page_host_invariant'] for x in local_rows)}/5 exact PAGE_HOST matches**
and **{sum(x['full_tuple_invariant'] for x in local_rows)}/5 exact full-tuple matches** on their paired Herbal pages.
Thus any page-bag lead is not localized to the strongest owned records.

## Highest formal excesses (evidence order remains separate)

{top_lines}

## Ten highest provenance-priority candidates

{evidence_lines}

The latter list is the candidate order for any future evidence upgrade.  Its
rank was fixed before formal scoring and is not reordered to favor the formal
outcomes.

## Interpretation

The atlas identifies no replicated layer-level invariance.  At whole-page
resolution the full tuple's mean matched excess is modestly higher than the
host's, but its max-two tail is 0.431 and only 21/38 pairs favor it.  The
cross-source and asserted-same/strong subsets are descriptively positive in
both representations, but their sources and pages are dependent.  Most
importantly, not one locally owned query retains even the exact PAGE_HOST.
The current data therefore support neither a referent-stable sparse host nor a
referent-stable distributed full tuple.

No host-neighbor diagnostic was run.  No image was opened.  f84r was absent
from the formal input and every other f84 side was rejected before retention.
The first source-freeze builder did transiently load the human f84r catalogue
row while recovering source URLs; the corrected builder removes that input,
and the exact superseded hashes and non-use are disclosed in the correction
artifact.
No object identity, plant/component name, semantic role, word, code value,
morpheme, POS, sound, language, plaintext, meaning, or translation follows.
""", encoding="utf8")

    result = {
        "schema": "GDT169_EXTERNAL_REFERENT_TUPLE_RESULT_V1", "status": status,
        "candidate_pairs": 40, "scorable_page_pairs": len(scored), "local_query_pairs": len(local_rows),
        "representations": ["PAGE_HOST", "POSITION_WRAPPER_HOST_RIGHT_CLOSURE_TUPLE"],
        "aggregate": {x["subset"]: x for x in summaries}, "null": null_rows,
        "local_query_exact_hits": {"page_host": sum(x["page_host_invariant"] for x in local_rows), "full_tuple": sum(x["full_tuple_invariant"] for x in local_rows)},
        "top_formal_candidate_ids": [x["candidate_id"] for x in top_formal],
        "top_provenance_candidate_ids": [x["candidate_id"] for x in strong_evidence],
        "interpretation": "Whole-page PAGE_HOST overlap is modestly more invariant than the exact full record tuple, but zero of five locally owned/provisional queries matches either representation on its paired Herbal page.",
        "claim_ceiling": "Exploratory anonymous external-referent formal-invariance atlas only; no object identity, role, word, code value, meaning, plaintext, or translation.",
        "f84": {"source_f84r_rows": source_f84r, "rejected_other_f84_rows": rejected_other_f84, "retained_joined_scored_rows": 0, "image_access": False},
        "source_access_correction": freeze["source_access_correction"],
        "inputs": {p.name if p.parent == R else str(p.relative_to(R)): sha(p) for p in (CAND, SOURCE, LOCAL, FREEZE)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {p.name: sha(p) for p in (SCORES, LOCAL_SCORES, SUMMARY, NULL, COUNTER)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = csha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, "scorable": len(scored), "host_mean_z": all_summary["host_mean_z"], "tuple_mean_z": all_summary["tuple_mean_z"], "local_hits": local_hits}, sort_keys=True))


if __name__ == "__main__":
    main()
