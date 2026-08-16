#!/usr/bin/env python3
"""Blind GDT113/GDT160/GDT162--167 calibration on two synthetic controls."""
from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from run_gdt003_nested_heldout import discover_operations
from run_gdt160_compatibility_pairing_null import (
    graph_arrays, graph_side, randomized_worlds, score_graph, semantic_stats,
)

ROOT = Path(__file__).resolve().parent
BLIND = ROOT / "gdt168_blind_synthetic_corpora.json.gz"
FREEZE = ROOT / "gdt168_source_encoder_freeze.json"
DESIGN = ROOT / "gdt168_blind_design.json"
SUMMARY = ROOT / "gdt168_blind_diagnostic_summary.tsv"
ALGEBRA = ROOT / "gdt168_blind_surface_algebra.tsv"
CONTEXT = ROOT / "gdt168_blind_context_scores.tsv"
SUBSTITUTION = ROOT / "gdt168_blind_substitution_scores.tsv"
ALIGNMENT = ROOT / "gdt168_blind_alignment_scores.tsv"
RESULT = ROOT / "gdt168_blind_result.json"

VIEWS = ("CONTROL_X", "CONTROL_Y")
RENDERERS = tuple(f"R{r}_S{s}" for r in range(1, 6) for s in range(1, 3))
MODES = ("COMPILER", "NEXT_HOST", "WINDOW_PM2", "WHOLE_LINE")
ALPHA, BETA, WORLDS = 16.0, 8.0, 1024
BLOCKS = ((0, 3), (3, 5), (5, 8), (8, 10))


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def opaque(text): return "H" + hashlib.sha256(text.encode()).hexdigest()[:16]
def seed(text): return int(hashlib.sha256(text.encode()).hexdigest()[:16], 16)


def write(path, rows):
    fields = []
    for row in rows:
        for field in row:
            if field not in fields: fields.append(field)
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows([{field: row.get(field, "NA") for field in fields} for row in rows])


def load():
    with gzip.open(BLIND, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    rows = payload["rows"]
    assert payload["schema"] == "GDT168_BLIND_SYNTHETIC_CORPORA_V1" and len(rows) == 240000
    forbidden = {"plaintext_form", "concept_index", "canonical_a_code", "canonical_host", "system"}
    assert not forbidden.intersection(rows[0])
    by = defaultdict(list)
    for row in rows: by[row["corpus_view"], row["renderer"]].append(row)
    assert set(x[0] for x in by) == set(VIEWS) and all(len(by[v, r]) == 12000 for v in VIEWS for r in RENDERERS)
    for values in by.values(): values.sort(key=lambda x: (x["source_unit_id"], x["record_id"], int(x["slot"])))
    return rows, by


def line_map(rows):
    lines = defaultdict(list)
    for row in rows: lines[row["line_id"]].append(row)
    for line in lines.values(): line.sort(key=lambda x: int(x["position_in_line"]))
    return lines


def record_metrics(rows):
    ends = [x for x in rows if int(x["slot"]) == int(x["record_length"]) - 1]
    nonends = [x for x in rows if x not in ends]
    line_ends = [x for x in rows if int(x["position_in_line"]) == 5 or int(x["slot"]) == int(x["record_length"]) - 1]
    b3_precision = sum(int(x["b3"]) for x in ends) / len(ends)
    b3_false = sum(int(x["b3"]) for x in nonends) / max(1, len(nonends))
    closure_recall = sum(int(x["dy_closure"]) or int(x["b3"]) for x in line_ends) / len(line_ends)
    host_freq, surface_freq = Counter(x["page_host"] for x in rows), Counter(x["surface"] for x in rows)
    return {"record_end_b3_precision": b3_precision, "nonend_b3_rate": b3_false,
            "line_end_closure_recall": closure_recall, "host_types": len(host_freq), "surface_types": len(surface_freq),
            "host_recurrent_mass": sum(n for n in host_freq.values() if n >= 2) / len(rows),
            "surface_recurrent_mass": sum(n for n in surface_freq.values() if n >= 2) / len(rows)}


def algebra_metrics(rows, view):
    forms = {x["surface"] for x in rows}; freq = Counter(x["surface"] for x in rows)
    units, folds = defaultdict(set), defaultdict(set)
    for row in rows:
        units[row["surface"]].add(row["source_unit_id"]); folds[row["surface"]].add(row["fold_id"])
    selected, edges = discover_operations(forms, freq, units)
    stats, _ = semantic_stats(forms, selected, edges)
    left = [x for x in selected if str(x["operation"][0]).startswith("PREFIX")]
    right = [x for x in selected if str(x["operation"][0]).startswith("SUFFIX")]
    denominator = len(selected) * (len(selected) - 1) // 2
    semantic = int(stats["eligible_LL"] + stats["eligible_LR"] + stats["eligible_RR"])
    if left and right:
        lg, rg = graph_side(left, edges), graph_side(right, edges)
        arrays = graph_arrays(lg, rg)
        observed, _, _, _ = score_graph(arrays, np.asarray([x[2] for x in rg["edges"]], dtype=np.int32), len(left), len(right))
        null = randomized_worlds(rg, arrays, len(left), freq, folds, units, False, WORLDS,
                                 seed("GDT168_ALGEBRA_" + view), False)
        null_mean = sum(null["counts"]) / WORLDS
        p = (1 + sum(x >= observed for x in null["counts"])) / (WORLDS + 1)
        switch = null["switchable_edges"] / max(1, len(rg["edges"]))
    else:
        observed = null_mean = switch = 0; p = 1.0
    return {"view": view, "renderer": "R1_S1", "forms": len(forms), "selected_operations": len(selected),
            "left_operations": len(left), "right_operations": len(right), "compatible_pairs": semantic,
            "compatible_pair_density": semantic / max(1, denominator), "graph_lr_pairs": observed,
            "null_mean_graph_lr_pairs": null_mean, "graph_lr_excess": observed - null_mean,
            "inclusive_p": p, "switchable_right_fraction": switch}


def endpoint_observations(rows, mode):
    lines = line_map(rows); out = []
    if mode == "COMPILER":
        for row in rows:
            target = "|".join((row["wrapper"], row["local_frame"], row["right_family"], row["closure_value"], str(row["dy_closure"]), str(row["b3"])))
            out.append((row, target, 1.0))
        return out
    for line in lines.values():
        bag = Counter(x["page_host"] for x in line)
        for i, row in enumerate(line):
            if mode == "NEXT_HOST":
                if i + 1 < len(line): out.append((row, line[i + 1]["page_host"], 1.0))
            elif mode == "WINDOW_PM2":
                values = [line[j]["page_host"] for j in range(max(0, i - 2), min(len(line), i + 3)) if j != i]
                for target, count in Counter(values).items(): out.append((row, target, count / len(values)))
            else:
                values = bag.copy(); values[row["page_host"]] -= 1
                if not values[row["page_host"]]: del values[row["page_host"]]
                total = sum(values.values())
                for target, count in values.items(): out.append((row, target, count / total))
    return out


def nuisance(row):
    return (row["renderer"], int(row["position_in_line"]), int(row["line_index"]), min(18, int(row["record_length"])))


def held_gain(rows, mode):
    observations = endpoint_observations(rows, mode); vocab = {target for _, target, _ in observations}
    global_t, global_n = Counter(), 0.0
    nt, nn, ht, hn = Counter(), Counter(), Counter(), Counter()
    ut, un, unt, unn, uht, uhn = defaultdict(Counter), Counter(), defaultdict(Counter), defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for row, target, weight in observations:
        unit, nk, host = row["source_unit_id"], nuisance(row), row["page_host"]
        global_t[target] += weight; global_n += weight; nt[nk, target] += weight; nn[nk] += weight; ht[host, target] += weight; hn[host] += weight
        ut[unit][target] += weight; un[unit] += weight; unt[unit][nk, target] += weight; unn[unit][nk] += weight; uht[unit][host, target] += weight; uhn[unit][host] += weight
    by_unit = Counter(); total_gain = 0.0
    for row, target, weight in observations:
        unit, nk, host = row["source_unit_id"], nuisance(row), row["page_host"]
        q = (global_t[target] - ut[unit][target] + .5) / (global_n - un[unit] + .5 * len(vocab))
        base = (nt[nk, target] - unt[unit][nk, target] + ALPHA * q) / (nn[nk] - unn[unit][nk] + ALPHA)
        hp = (ht[host, target] - uht[unit][host, target] + BETA * base) / (hn[host] - uhn[unit][host] + BETA)
        gain = weight * math.log2(hp / base); total_gain += gain; by_unit[unit] += gain
    units = len(by_unit)
    return {"events": len({x[0]["blind_id"] for x in observations}), "weighted_targets": sum(x[2] for x in observations),
            "gain_bits": total_gain, "gain_per_event": total_gain / max(1, len({x[0]["blind_id"] for x in observations})),
            "positive_units": sum(x > 0 for x in by_unit.values()), "units": units}


def short_host_metrics(rows):
    freq = Counter(x["page_host"] for x in rows); forms = sorted(freq, key=opaque)
    short_mass = sum(n for h, n in freq.items() if len(h) in (2, 3)) / len(rows)
    pattern = defaultdict(list)
    for host in forms:
        if len(host) not in (2, 3): continue
        for i in range(len(host)): pattern[len(host), i, host[:i] + "_" + host[i + 1:]].append(host)
    edges = set()
    for group in pattern.values():
        for a, b in itertools.combinations(sorted(set(group), key=opaque), 2): edges.add((a, b))
    return {"host_types": len(forms), "short_host_mass": short_mass, "hamming1_edges": len(edges),
            "hamming1_density": 2 * len(edges) / max(1, len(forms) * (len(forms) - 1)), "edges": edges}


def sparse_cos(a, b):
    dot = sum(v * b.get(k, 0.0) for k, v in a.items()); na = math.sqrt(sum(v * v for v in a.values())); nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def substitution_metrics(rows, edges, endpoint):
    profiles = defaultdict(Counter)
    if endpoint == "COMPILER":
        for row in rows:
            target = "|".join((row["wrapper"], row["local_frame"], row["right_family"], row["closure_value"], str(row["dy_closure"]), str(row["b3"])))
            profiles[row["page_host"]][target] += 1
    else:
        for row, target, weight in endpoint_observations(rows, "WINDOW_PM2"): profiles[row["page_host"]][target] += weight
    classes = defaultdict(list)
    for a, b in edges:
        diffs = [i for i in range(len(a)) if a[i] != b[i]]
        if len(diffs) != 1: continue
        i = diffs[0]
        if opaque(a) > opaque(b): a, b = b, a
        delta = Counter(profiles[b]); delta.subtract(profiles[a])
        scale = sum(abs(x) for x in delta.values())
        if scale: delta = Counter({k: v / scale for k, v in delta.items() if v})
        classes[len(a), i, a[i], b[i]].append(delta)
    vals=[]; retained=0
    for group in classes.values():
        if len(group) < 3: continue
        retained += 1
        vals.extend(sparse_cos(a, b) for a, b in itertools.combinations(group, 2))
    return {"endpoint": endpoint, "repeated_classes": retained, "delta_pairs": len(vals), "mean_delta_cosine": sum(vals) / len(vals) if vals else 0.0}


def hsig(rows, panel):
    occ, pos, line, ctx = Counter(), defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for row in rows:
        host = row["page_host"]
        if host not in panel: continue
        occ[host] += 1; pos[host][int(row["position_in_line"])] += 1; line[host][int(row["line_index"])] += 1
    for row, target, weight in endpoint_observations(rows, "WHOLE_LINE"):
        if row["page_host"] in panel: ctx[row["page_host"]][target] += weight
    out=[]
    for host in panel:
        n=occ[host]; vals=sorted(ctx[host].values(), reverse=True); total=sum(vals); probs=[x/total for x in vals] if total else []
        ent=-sum(x*math.log(x) for x in probs if x)/(math.log(len(probs)) if len(probs)>1 else 1)
        v=[math.log1p(n), ent, sum(vals[:1])/total if total else 0, sum(vals[:3])/total if total else 0, ctx[host][host]/total if total else 0]
        v += [pos[host][i]/n if n else 0 for i in range(6)]
        v += [line[host][i]/n if n else 0 for i in range(3)]
        out.append(v)
    a=np.array(out,float); sd=a.std(axis=0); sd[sd<1e-12]=1
    return (a-a.mean(axis=0))/sd


def hungarian(cost):
    n=len(cost);u=[0.]*(n+1);v=[0.]*(n+1);p=[0]*(n+1);way=[0]*(n+1)
    for i in range(1,n+1):
        p[0]=i;j0=0;mv=[float('inf')]*(n+1);used=[False]*(n+1)
        while True:
            used[j0]=True;i0=p[j0];delta=float('inf');j1=0
            for j in range(1,n+1):
                if not used[j]:
                    cur=cost[i0-1][j-1]-u[i0]-v[j]
                    if cur<mv[j]-1e-15:mv[j]=cur;way[j]=j0
                    if mv[j]<delta-1e-15:delta=mv[j];j1=j
            for j in range(n+1):
                if used[j]:u[p[j]]+=delta;v[j]-=delta
                else:mv[j]-=delta
            j0=j1
            if p[j0]==0:break
        while True:
            j1=way[j0];p[j0]=p[j1];j0=j1
            if j0==0:break
    ans=[0]*n
    for j in range(1,n+1):ans[p[j]-1]=j-1
    return ans


def block_map(a,b):
    out=[0]*10
    for lo,hi in BLOCKS:
        assign=hungarian(((a[lo:hi,None,:]-b[None,lo:hi,:])**2).sum(axis=2).tolist())
        for i,j in enumerate(assign):out[lo+i]=lo+j
    return out


def geometry(rows, panel):
    contexts=defaultdict(Counter)
    for row,target,weight in endpoint_observations(rows,"WHOLE_LINE"):
        if row["page_host"] in panel:contexts[row["page_host"]][target]+=weight
    dims=sorted({x for h in panel for x in contexts[h]},key=opaque); mat=[]
    for h in panel:
        v=np.array([contexts[h][d] for d in dims],float);z=np.linalg.norm(v);mat.append(v/z if z else v)
    a=np.stack(mat);return a@a.T


def upper(a,m=None):
    if m is not None:a=a[np.ix_(m,m)]
    return np.array([a[i,j] for i in range(10) for j in range(i+1,10)])


def corr(a,b): return float(np.corrcoef(a,b)[0,1]) if np.std(a)>1e-15 and np.std(b)>1e-15 else 0.


def random_map(rng):
    m=list(range(10))
    for lo,hi in BLOCKS:
        q=m[lo:hi];rng.shuffle(q);m[lo:hi]=q
    return m


def alignments(by, view):
    ref="R1_S1"; comparisons=("R1_S2","R2_S1","R3_S1","R4_S1","R5_S1"); out=[]
    for other in comparisons:
        fold_obs=[];fold_null=[]
        for train_half in (0,1):
            ra=by[view,ref];rb=by[view,other]
            half=lambda row: seed(row["source_unit_id"])%2
            fa=Counter(x["page_host"] for x in ra);fb=Counter(x["page_host"] for x in rb)
            pa=tuple(x for x,_ in sorted(fa.items(),key=lambda q:(-q[1],opaque(q[0])))[:10]);pb=tuple(x for x,_ in sorted(fb.items(),key=lambda q:(-q[1],opaque(q[0])))[:10])
            sa=hsig([x for x in ra if half(x)==train_half],pa);sb=hsig([x for x in rb if half(x)==train_half],pb);mapping=block_map(sa,sb)
            ga=geometry([x for x in ra if half(x)!=train_half],pa);gb=geometry([x for x in rb if half(x)!=train_half],pb)
            obs=corr(upper(ga),upper(gb,mapping));rng=random.Random(seed(f"GDT168_ALIGN|{view}|{other}|{train_half}"));null=[corr(upper(ga),upper(gb,random_map(rng))) for _ in range(WORLDS)]
            fold_obs.append(obs);fold_null.append(null)
        observed=sum(fold_obs)/2;null=[(fold_null[0][i]+fold_null[1][i])/2 for i in range(WORLDS)]
        out.append({"view":view,"reference_renderer":ref,"other_renderer":other,"alignment_type":"CROSS_SCRIBE" if other=="R1_S2" else "CROSS_REGISTER",
                    "mean_held_geometry_correlation":observed,"null_mean":sum(null)/WORLDS,"excess":observed-sum(null)/WORLDS,
                    "inclusive_p":(1+sum(x>=observed-1e-12 for x in null))/(WORLDS+1)})
    return out


def main():
    design=json.loads(DESIGN.read_text());assert design["status"]=="FROZEN_BEFORE_BLIND_SCORING"
    rows,by=load();summary=[];algebra=[];context=[];subs=[];align=[]
    for view in VIEWS:
        primary=by[view,"R1_S1"];rec=record_metrics(primary);short=short_host_metrics(primary)
        for metric,value in rec.items():summary.append({"view":view,"diagnostic":"GDT113_RECORD_ARCHITECTURE","metric":metric,"value":value})
        for metric in ("host_types","short_host_mass","hamming1_edges","hamming1_density"):summary.append({"view":view,"diagnostic":"GDT162_SHORT_HOST","metric":metric,"value":short[metric]})
        alg=algebra_metrics(primary,view);algebra.append(alg)
        for metric in ("selected_operations","compatible_pair_density","graph_lr_excess","inclusive_p","switchable_right_fraction"):summary.append({"view":view,"diagnostic":"GDT160_SURFACE_ALGEBRA","metric":metric,"value":alg[metric]})
        for renderer in RENDERERS:
            rr=by[view,renderer]
            for mode in MODES:
                g=held_gain(rr,mode);context.append({"view":view,"renderer":renderer,"mode":mode,**g})
        for endpoint in ("COMPILER","EXTERNAL_WINDOW"):
            s=substitution_metrics(primary,short["edges"],endpoint);s["view"]=view;subs.append(s)
            summary.append({"view":view,"diagnostic":"GDT163_164_SUBSTITUTION","metric":endpoint+"_DELTA_COSINE","value":s["mean_delta_cosine"]})
        aa=alignments(by,view);align.extend(aa)
        for mode in MODES:
            rr=[x for x in context if x["view"]==view and x["mode"]==mode];events=sum(x["events"] for x in rr);gain=sum(x["gain_bits"] for x in rr);pos=sum(x["positive_units"] for x in rr);units=sum(x["units"] for x in rr)
            summary.append({"view":view,"diagnostic":"GDT162_167_CONTEXT","metric":mode+"_GAIN_PER_EVENT","value":gain/events,"gain_bits":gain,"positive_units":pos,"units":units})
        ar=[x for x in aa if x["alignment_type"]=="CROSS_REGISTER"]
        summary.append({"view":view,"diagnostic":"GDT167_ALIGNMENT","metric":"CROSS_REGISTER_MEAN_CORRELATION","value":sum(x["mean_held_geometry_correlation"] for x in ar)/len(ar)})
    write(SUMMARY,summary);write(ALGEBRA,algebra);write(CONTEXT,context);write(SUBSTITUTION,subs);write(ALIGNMENT,align)
    result={"schema":"GDT168_BLIND_DIAGNOSTIC_RESULT_V1","status":"BLIND_DIAGNOSTICS_COMPLETE_TRUTH_NOT_READ","views":list(VIEWS),"rows":len(rows),
            "summary":{v:{x["diagnostic"]+":"+x["metric"]:x["value"] for x in summary if x["view"]==v} for v in VIEWS},
            "truth_files_read":[],"forbidden_fields_seen":[],"inputs":{BLIND.name:sha(BLIND),DESIGN.name:sha(DESIGN),FREEZE.name:sha(FREEZE)},
            "implementation":{Path(__file__).name:sha(Path(__file__)),"run_gdt003_nested_heldout.py":sha(ROOT/"run_gdt003_nested_heldout.py"),"run_gdt160_compatibility_pairing_null.py":sha(ROOT/"run_gdt160_compatibility_pairing_null.py")},
            "outputs":{p.name:sha(p) for p in (SUMMARY,ALGEBRA,CONTEXT,SUBSTITUTION,ALIGNMENT)},
            "f84r":{"opened":False,"queried":False,"retained":False,"joined":False,"scored":False},
            "claim_ceiling":"Blind synthetic diagnostic output only; no Voynich word, code value, language, meaning, plaintext, or translation."}
    result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"views":result["summary"]},sort_keys=True))


if __name__=="__main__":main()
