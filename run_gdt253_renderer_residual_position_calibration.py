#!/usr/bin/env python3
"""Max-search calibration of the exposed GDT252 renderer/residual slot lead."""
import csv, hashlib, json, random
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
ARR = "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv"
OBJ = "gdt235_label_object_inventory.tsv"
ALIGN = "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
R252 = "gdt252_result.json"
DOCS = ["GDT253_RENDERER_RESIDUAL_POSITION_CALIBRATION_METHOD.md", "GDT253_RENDERER_RESIDUAL_POSITION_CALIBRATION_REPORT.md"]
OUTS = ["gdt253_renderer_residual_inventory.tsv", "gdt253_candidate_summary.tsv", "gdt253_null_results.tsv", "gdt253_counterexamples.tsv"]
EDITIONS = ("ZL3b", "IT2a", "RF1b")
WORLDS = 65536

def sha(p): return hashlib.sha256((R / p).read_bytes()).hexdigest()
def read(p):
    with (R / p).open(encoding="utf-8") as f: return list(csv.DictReader(f, delimiter="\t"))
def write(p, rows):
    with (R / p).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)

def aligned_by_locus(rows):
    out = defaultdict(lambda: defaultdict(list))
    for r in rows:
        out[r["locus"]][r["edition"]].append(r)
    for by_ed in out.values():
        for ed in by_ed: by_ed[ed].sort(key=lambda x: int(x["source_group_index"]))
    return out

def renderer(groups, prefix):
    codes = []
    for g in groups: codes.extend(g["primary_sta_codes"].split())
    k = len(prefix)
    return " ".join(codes[:k]) if len(codes) >= k else ""

def max_stat(rows):
    seen = defaultdict(set)
    for r in rows: seen[(r["renderer_signature"], r["strict_residual"], r["slot_index"])].add(r["physical_folio"])
    return max((len(v) for v in seen.values()), default=0)

def permute(rows, mode, rng):
    z = [dict(r) for r in rows]
    groups = defaultdict(list)
    for i, r in enumerate(z): groups[r["array_id"]].append(i)
    for ix in groups.values():
        if mode == "INDEPENDENT_RENDERER_RESIDUAL_WITHIN_ARRAY":
            a = [z[i]["renderer_signature"] for i in ix]
            b = [z[i]["strict_residual"] for i in ix]
            rng.shuffle(a); rng.shuffle(b)
            for j, i in enumerate(ix): z[i]["renderer_signature"], z[i]["strict_residual"] = a[j], b[j]
        else:
            a = [(z[i]["renderer_signature"], z[i]["strict_residual"]) for i in ix]
            rng.shuffle(a)
            for j, i in enumerate(ix): z[i]["renderer_signature"], z[i]["strict_residual"] = a[j]
    return z

def main():
    arr = read(ARR); obj = {r["locus"]: r for r in read(OBJ)}; ali = aligned_by_locus(read(ALIGN))
    assert all(not r["locus"].startswith("f84") for r in arr)
    target = [a for a in arr if a["slot_count"] == "10" and a["locus"] in obj and obj[a["locus"]]["transferred_prefix"] != "NONE"]
    inventory = []
    by_ed = defaultdict(list)
    for a in target:
        o = obj[a["locus"]]
        for ed in EDITIONS:
            groups = ali.get(a["locus"], {}).get(ed, [])
            sig = renderer(groups, o["transferred_prefix"]) if groups else ""
            if not sig: continue
            r = {"edition": ed, "array_id": a["array_id"], "page": a["page"], "physical_folio": a["physical_folio"],
                 "locus": a["locus"], "slot_index": int(a["slot_index"]), "slot_count": 10,
                 "transferred_prefix": o["transferred_prefix"], "renderer_signature": sig,
                 "strict_residual": o["strict_residual"], "raw_family": o["raw_family"],
                 "gdt252_pair": int(a["locus"] in {"f70v1.5", "f72r1.5"})}
            inventory.append(r); by_ed[ed].append(r)
    inventory.sort(key=lambda r: (EDITIONS.index(r["edition"]), r["array_id"], r["slot_index"]))
    write(OUTS[0], inventory)

    summaries = []
    for ed in EDITIONS:
        rows = by_ed[ed]
        keyed = defaultdict(list)
        for r in rows: keyed[(r["renderer_signature"], r["strict_residual"])].append(r)
        for (sig, res), z in sorted(keyed.items()):
            fols = {r["physical_folio"] for r in z}
            if len(fols) < 2: continue
            slots = Counter(r["slot_index"] for r in z)
            summaries.append({"edition": ed, "renderer_signature": sig, "strict_residual": res,
                              "occurrences": len(z), "physical_folios": len(fols),
                              "modal_slot": min(k for k, v in slots.items() if v == max(slots.values())),
                              "modal_slot_folios": max(slots.values()),
                              "loci": ";".join(r["locus"] for r in z),
                              "classification": "CROSS_FOLIO_RECURRENT_PAIR"})
    if not summaries:
        summaries = [{"edition":"NONE","renderer_signature":"NONE","strict_residual":"NONE","occurrences":0,"physical_folios":0,"modal_slot":0,"modal_slot_folios":0,"loci":"","classification":"NO_CROSS_FOLIO_PAIR"}]
    write(OUTS[1], summaries)

    nulls = []
    for eidx, ed in enumerate(EDITIONS):
        rows = by_ed[ed]; observed = max_stat(rows)
        for midx, mode in enumerate(("INDEPENDENT_RENDERER_RESIDUAL_WITHIN_ARRAY", "WHOLE_PAIR_POSITION_WITHIN_ARRAY")):
            rng = random.Random(253000 + eidx * 100 + midx)
            hist = Counter()
            for _ in range(WORLDS): hist[max_stat(permute(rows, mode, rng))] += 1
            ge = sum(v for k, v in hist.items() if k >= observed)
            nulls.append({"edition": ed, "null_model": mode, "rows": len(rows), "arrays": len({r['array_id'] for r in rows}),
                          "observed_max_distinct_folios_same_pair_same_slot": observed, "worlds": WORLDS,
                          "worlds_ge_observed": ge, "inclusive_p": f"{(ge+1)/(WORLDS+1):.12f}",
                          "null_score_histogram": json.dumps(dict(sorted(hist.items())), separators=(",", ":"))})
    write(OUTS[2], nulls)

    cand = {r["edition"]: r for r in summaries if r["strict_residual"] == "AB" and r["modal_slot"] == 4 and "f70v1.5" in r["loci"] and "f72r1.5" in r["loci"]}
    assert set(cand) == {"ZL3b", "IT2a"}
    counters = [
        {"counterexample":"RF_MEMBER_PREFIX_INSTABILITY","value":"RF1b reads the f72r1 renderer prefix A1 Qa A3 B2 rather than f70v1 A1 Q1 A3 B2","consequence":"the exact source-member renderer pair exists in ZL3b and IT2a but not RF1b"},
        {"counterexample":"FAMILY_ONLY_SLOT3","value":"f70v2.25 has whole family AQABAB at slot 3/10","consequence":"AQABAB or residual AB alone is not a position-4 code"},
        {"counterexample":"PARTIAL_HOMOLOG_COVERAGE","value":"only 2/4 formally covered Kluge-09A labels carry the exposed construction","consequence":"the construction is not invariant at the named homolog"},
        {"counterexample":"POSTHOC_MAX_SEARCH","value":"renderer residual and slot were exposed before this calibration","consequence":"even a small diagnostic p cannot be treated as prospective confirmation"},
        {"counterexample":"EDITORIAL_SLOT_PHASE","value":"slot indices are human catalogue order without a proven authorial degree-1 start","consequence":"no number or zodiac-degree interpretation is licensed"},
    ]
    write(OUTS[3], counters)
    zl = next(r for r in nulls if r["edition"] == "ZL3b" and r["null_model"] == "INDEPENDENT_RENDERER_RESIDUAL_WITHIN_ARRAY")
    status = "GDT252_POSITION_LEAD_MAXT_BORDERLINE_AND_RF_READING_UNSTABLE_NO_POSITION_KEY"
    result = {"experiment":"GDT253_RENDERER_RESIDUAL_POSITION_CALIBRATION", "status":status,
              "ten_slot_arrays":8, "eligible_rows_by_edition":{ed:len(by_ed[ed]) for ed in EDITIONS},
              "cross_folio_recurrent_pairs_by_edition":dict(Counter(r["edition"] for r in summaries)),
              "gdt252_pair_exact_member_support_readings":["ZL3b","IT2a"], "gdt252_pair_failed_exact_member_readings":["RF1b"],
              "zl_primary_max_statistic":int(zl["observed_max_distinct_folios_same_pair_same_slot"]),
              "zl_independent_pairing_max_search_p":float(zl["inclusive_p"]),
              "interpretation":"The full renderer/residual slot-4 coincidence is the only cross-folio repeated pair in ZL3b/IT2a and is borderline under a max-search null, but it fails exact RF1b member stability and cannot yet serve as a positional key.",
              "active_semantic_assignments":0,
              "claim_ceiling":"Exploratory catalogue-position association only; no authorial number degree direction word language plaintext or translation.",
              "f84":{"input":False,"retained":False,"joined":False,"scored":False,"new_access":False},
              "inputs":{p:sha(p) for p in [ARR,OBJ,ALIGN,R252]}, "outputs":{}, "documents":{}, "implementation":{}}
    for p in OUTS: result["outputs"][p] = sha(p)
    for p in DOCS: result["documents"][p] = sha(p)
    result["implementation"][Path(__file__).name] = sha(Path(__file__).name)
    result["content_hash"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (R / "gdt253_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Fill the numerical report in a deterministic appendix.
    report = (R / DOCS[1]).read_text(encoding="utf-8").split("\n## Reproducible result", 1)[0].rstrip()
    report += "\n\n## Reproducible result\n\n"
    report += f"Status: **{status}**.\n\n"
    report += f"The ZL3b max-search statistic is **{int(zl['observed_max_distinct_folios_same_pair_same_slot'])} folios**, with independent renderer/residual p = **{float(zl['inclusive_p']):.6f}**. "
    wp = next(r for r in nulls if r['edition']=='ZL3b' and r['null_model']=='WHOLE_PAIR_POSITION_WITHIN_ARRAY')
    report += f"Conditional on intact pairs, the position-shuffle p is **{float(wp['inclusive_p']):.6f}**. "
    report += "The exact member-prefix pair reproduces in ZL3b and IT2a but not RF1b.\n\n"
    report += "The result is therefore a **weak borderline renderer-plus-residual positional lead**, not an executable key. The strongest next evidence would be a prospectively selected occurrence of the same full construction at the same homologous slot on a new independently inventoried folio.\n\n"
    report += "No number, degree, direction, word, language, plaintext, or translation is assigned. No f84 input was used.\n"
    (R / DOCS[1]).write_text(report, encoding="utf-8")
    # Rebind the report after its numerical appendix is written.
    result["documents"][DOCS[1]] = sha(DOCS[1])
    result["content_hash"] = hashlib.sha256(json.dumps({k:v for k,v in result.items() if k!='content_hash'}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (R / "gdt253_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status":status,"zl_p":zl["inclusive_p"],"readings":list(cand)},sort_keys=True))

if __name__ == "__main__": main()
