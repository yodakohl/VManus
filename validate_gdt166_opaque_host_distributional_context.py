#!/usr/bin/env python3
"""Nonimporting independent validator for GDT166."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt062_right_family_inventory.tsv"
FRAMES = R / "gdt046_line_frames.tsv"
DESIGN = R / "gdt166_design.json"
METHOD = R / "GDT166_OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_METHOD.md"
REPORT = R / "GDT166_OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_REPORT.md"
INVENTORY = R / "gdt166_context_inventory.tsv"
SCORES = R / "gdt166_context_scores.tsv"
FOLDS = R / "gdt166_context_fold_scores.tsv"
NEIGHBORS = R / "gdt166_neighbor_relations.tsv"
NEIGHBOR_STABILITY = R / "gdt166_neighbor_stability.tsv"
NULLS = R / "gdt166_context_null.tsv"
NEIGHBOR_NULL = R / "gdt166_neighbor_null.tsv"
COUNTER = R / "gdt166_counterexamples.tsv"
VARIANTS = R / "gdt166_variant_log.tsv"
RESULT = R / "gdt166_result.json"
VALIDATION = R / "gdt166_validation.json"

MODES = ("WINDOW_PM2", "WHOLE_LINE", "PARAGRAPH_BAG")
AXES = (("HELD_FOLIO", "folio"), ("HELD_SECTION", "section"), ("HELD_HAND", "hand"))
FEATURES = ("section", "currier", "hand", "frequency_bin", "position_quartile", "line_count_bin")
ALPHA, BETA, WORLDS = 32.0, 16.0, 1024
FOCAL_N, CONTEXT_N, TRAIN_MASS, HELD_MASS = 64, 256, 16.0, 4.0


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def opaque(x): return "H" + hashlib.sha256(x.encode()).hexdigest()[:16]
def seed(x): return int(hashlib.sha256(x.encode()).hexdigest()[:16], 16)
def csha(x): return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def fbin(n): return "F1" if n == 1 else "F2_4" if n <= 4 else "F5_15" if n <= 15 else "F16_63" if n <= 63 else "F64P"
def lbin(n): return str(n) if n <= 4 else "5_7" if n <= 7 else "8P"
def lkey(x): page, line = x.split("."); return page, int(line)
def close(a, b, t=3e-8): return abs(float(a)-float(b)) <= t * max(1.0, abs(float(a)), abs(float(b)))


def tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as h: return list(csv.DictReader(h, delimiter="\t"))


class C:
    def __init__(self): self.rows = []
    def add(self, name, passed, detail=""):
        self.rows.append((name, bool(passed), str(detail)))
        if not passed: raise AssertionError(f"{name}: {detail}")


def rebuild(c):
    rows=[]; total=reject=0
    with SOURCE.open(encoding="utf-8", newline="") as h:
        for raw in csv.DictReader(h, delimiter="\t"):
            total += 1
            page,locus=raw["page"],raw["locus"]
            if page.startswith("f84") or locus.startswith("f84"): reject += 1; continue
            rows.append({"host":raw["page_host"],"locus":locus,"page":page,"folio":raw["physical_folio"],
                         "section":raw["section"],"currier":raw["currier"],"hand":raw["hand"],
                         "index":int(raw["group_index"]),"group_count":int(raw["group_count"]),
                         "position_quartile":raw["position_quartile"]})
    c.add("source_counts",(total,reject,len(rows))==(15592,228,15364),(total,reject,len(rows)))
    freq=Counter(x["host"] for x in rows)
    for x in rows:
        x["frequency_bin"]=fbin(freq[x["host"]]); x["line_count_bin"]=lbin(x["group_count"])
        x["occurrence_id"]=f"{x['locus']}:{x['index']}"; x["nuisance_key"]=tuple(x[f] for f in FEATURES)
    lines=defaultdict(list)
    for x in rows: lines[x["locus"]].append(x)
    for line in lines.values(): line.sort(key=lambda x:x["index"])
    contexts={m:[] for m in MODES}
    for locus in sorted(lines,key=lkey):
        line=lines[locus]; whole=Counter(x["host"] for x in line)
        for i,x in enumerate(line):
            w=Counter(line[j]["host"] for j in range(max(0,i-2),min(len(line),i+3)) if j!=i)
            bag=whole.copy(); bag[x["host"]]-=1
            if not bag[x["host"]]: del bag[x["host"]]
            if w: contexts["WINDOW_PM2"].append({**x,"context":w})
            if bag: contexts["WHOLE_LINE"].append({**x,"context":bag})
    frames={}; ft=fr=0
    with FRAMES.open(encoding="utf-8", newline="") as h:
        for raw in csv.DictReader(h,delimiter="\t"):
            ft+=1
            if raw["page"].startswith("f84") or raw["locus"].startswith("f84"): fr+=1; continue
            frames[raw["locus"]]=(raw["page"],int(raw["paragraph_start"]))
    c.add("frame_counts",(ft,fr,len(frames))==(1164,21,1143),(ft,fr,len(frames)))
    current={}; pn=Counter(); po={}
    for locus in sorted(frames,key=lkey):
        page,start=frames[locus]
        if page not in current or start: pn[page]+=1; current[page]=f"{page}:P{pn[page]}"
        po[locus]=current[page]
    paras=defaultdict(list)
    for locus,p in po.items(): paras[p].extend(lines.get(locus,[]))
    for p in sorted(paras):
        items=paras[p]; bag=Counter(x["host"] for x in items)
        for x in items:
            b=bag.copy(); b[x["host"]]-=1
            if not b[x["host"]]: del b[x["host"]]
            if b: contexts["PARAGRAPH_BAG"].append({**x,"context":b,"paragraph_id":p})
    c.add("context_counts",tuple(len(contexts[m]) for m in MODES)==(15203,15203,8447))
    c.add("layout_counts",(len(lines),len(paras),len({x['folio'] for x in rows}))==(2431,288,93))
    c.add("no_f84",all(not x["locus"].startswith("f84") for x in rows))
    return rows,contexts,freq


def train(events,vocab):
    target=Counter(); ft=[Counter() for _ in FEATURES]; fn=[Counter() for _ in FEATURES]; ht=Counter(); hn=Counter()
    for e in events:
        z=sum(e["context"].values())
        for y,n in e["context"].items():
            w=n/z; target[y]+=w; ht[e["host"],y]+=w
            for j,f in enumerate(FEATURES): ft[j][e[f],y]+=w
        hn[e["host"]]+=1.0
        for j,f in enumerate(FEATURES): fn[j][e[f]]+=1.0
    return {"target":target,"n":float(len(events)),"v":len(vocab),"ft":ft,"fn":fn,"ht":ht,"hn":hn}


def probs(m,e,y):
    q=(m["target"][y]+.5)/(m["n"]+.5*m["v"]); pieces=[]
    for j,f in enumerate(FEATURES): pieces.append((m["ft"][j][e[f],y]+ALPHA*q)/(m["fn"][j][e[f]]+ALPHA))
    n=sum(pieces)/len(pieces); h=(m["ht"][e["host"],y]+BETA*n)/(m["hn"][e["host"]]+BETA)
    return q,n,h


def score(m,e):
    z=sum(e["context"].values()); o=Counter()
    for y,n0 in e["context"].items():
        w=n0/z; q,n,h=probs(m,e,y); o["unigram_bits"]-=w*math.log2(q); o["nuisance_bits"]-=w*math.log2(n); o["host_bits"]-=w*math.log2(h)
        if e["host"]=="ok" and y=="y": o["ok_y_weight"]+=w; o["ok_y_gain_bits"]+=w*math.log2(h/n)
    o["gain_bits"]=o["nuisance_bits"]-o["host_bits"]
    return o


def refit(contexts,vocab,c):
    exported={(x["context_mode"],x["axis"],x["held"]):x for x in tsv(FOLDS)}; artifacts={}; aggregates={}
    for mode in MODES:
        for axis,key in AXES:
            for held in sorted({str(e[key]) for e in contexts[mode]}):
                tr=[e for e in contexts[mode] if str(e[key])!=held]; te=[e for e in contexts[mode] if str(e[key])==held]; m=train(tr,vocab); total=Counter(); seen=0
                for e in te: total.update(score(m,e)); seen+=int(m["hn"][e["host"]]>0)
                out=exported[mode,axis,held]
                c.add(f"fold_count:{mode}:{axis}:{held}",(int(out["focal_occurrences"]),int(out["training_occurrences"]),int(out["source_seen_occurrences"]))==(len(te),len(tr),seen))
                for field in ("unigram_bits","nuisance_bits","host_bits","gain_bits","ok_y_weight","ok_y_gain_bits"):
                    c.add(f"fold:{field}:{mode}:{axis}:{held}",close(out[field],total[field]))
                c.add(f"fold_no_oky:{mode}:{axis}:{held}",close(out["gain_without_ok_y_bits"],total["gain_bits"]-total["ok_y_gain_bits"]))
                aggregates[mode,axis]=aggregates.get((mode,axis),Counter()); aggregates[mode,axis].update(total); aggregates[mode,axis]["n"]+=len(te); aggregates[mode,axis]["positive"]+=int(total["gain_bits"]>0)
                if axis=="HELD_FOLIO": artifacts[mode,held]=(m,te)
    summary={(x["context_mode"],x["axis"]):x for x in tsv(SCORES)}
    for key,a in aggregates.items():
        out=summary[key]
        c.add("summary_gain:"+":".join(key),close(out["gain_bits"],a["gain_bits"]))
        c.add("summary_n:"+":".join(key),int(out["focal_occurrences"])==a["n"] and int(out["positive_folds"])==a["positive"])
    return artifacts,summary


def context_null(mode,events,artifacts):
    prepared={}; swap=variable=0
    for held in sorted({h for m,h in artifacts if m==mode}):
        model,test=artifacts[mode,held]; groups=defaultdict(list)
        for e in test: groups[e["nuisance_key"]].append(e)
        packed={}
        for key,g in groups.items():
            sources=sorted({e["host"] for e in g},key=opaque); targets={y for e in g for y in e["context"]}; ex=g[0]; logs={}
            for s in sources:
                p=dict(ex);p["host"]=s
                for y in targets:
                    _,n,h=probs(model,p,y);logs[s,y]=math.log2(h/n)
            lookup={}
            for e in g:
                z=sum(e["context"].values())
                for s in sources: lookup[e["occurrence_id"],s]=sum(n/z*logs[s,y] for y,n in e["context"].items())
            packed[key]=(g,lookup)
        prepared[held]=packed;swap+=sum(len(g) for g in groups.values() if len(g)>=2);variable+=sum(len(g) for g in groups.values() if len({e['host'] for e in g})>=2)
    rng=random.Random(seed("GDT166_CONTEXT_NULL_"+mode)); values=[]
    for _ in range(WORLDS):
        gain=0.0
        for held in sorted(prepared):
            for key in sorted(prepared[held],key=str):
                g,lookup=prepared[held][key]; sources=[e["host"] for e in g];rng.shuffle(sources)
                gain+=sum(lookup[e["occurrence_id"],s] for e,s in zip(g,sources))
        values.append(gain/len(events))
    return values,swap,variable


def profiles(events,focal,cpanel):
    counts=defaultdict(Counter);mass=Counter();glob=Counter()
    for e in events:
        if e["host"] not in focal:continue
        z=sum(e["context"].values())
        for y,n in e["context"].items():
            q=y if y in cpanel else "__OTHER__";w=n/z;counts[e["host"]][q]+=w;glob[q]+=w
        mass[e["host"]]+=1.0
    dims=tuple(sorted(set(cpanel)|{"__OTHER__"},key=opaque));gt=sum(glob.values());vec={}
    for h in focal:
        v=np.zeros(len(dims))
        if mass[h] and gt:
            for j,y in enumerate(dims):
                if counts[h][y] and glob[y]:v[j]=max(0,math.log2((counts[h][y]/mass[h])/(glob[y]/gt)))
        z=float(np.linalg.norm(v));vec[h]=v/z if z else v
    return vec,mass


def neighbors(events,focal,cpanel,freq):
    rv,rm=profiles(events,focal,cpanel); refs=[]
    for h in focal:
        cand=[x for x in focal if x!=h and rm[x]>=TRAIN_MASS]
        if rm[h]<TRAIN_MASS or not cand:continue
        n=sorted(cand,key=lambda x:(-float(rv[h]@rv[x]),opaque(x)))[0]
        refs.append((h,n,float(rv[h]@rv[n]),rm[h],rm[n]))
    pred=[]
    for axis,key in AXES:
        for held in sorted({str(e[key]) for e in events}):
            tr=[e for e in events if str(e[key])!=held];te=[e for e in events if str(e[key])==held];tv,tm=profiles(tr,focal,cpanel);hv,hm=profiles(te,focal,cpanel)
            tc=[h for h in focal if tm[h]>=TRAIN_MASS];hc=[h for h in focal if hm[h]>=HELD_MASS]
            for h in focal:
                if tm[h]<TRAIN_MASS or hm[h]<HELD_MASS:continue
                cand=[x for x in tc if x!=h]
                if not cand:continue
                n=sorted(cand,key=lambda x:(-float(tv[h]@tv[x]),opaque(x)))[0]
                if n not in hc:continue
                ranked=sorted((x for x in hc if x!=h),key=lambda x:(-float(hv[h]@hv[x]),opaque(x)))
                if n not in ranked:continue
                rank=ranked.index(n)+1;pred.append({"axis":axis,"held":held,"source":h,"predicted":n,"rank":rank,"candidates":len(ranked),"rr":1/rank,"top1":int(rank==1),"top5":int(rank<=5),"train_cos":float(tv[h]@tv[n]),"held_cos":float(hv[h]@hv[n]),"train_mass":tm[h],"held_mass":hm[h],"fbin":fbin(freq[h]),"rank_map":{x:i+1 for i,x in enumerate(ranked)}})
    return refs,pred


def nnull(pred):
    groups=defaultdict(list)
    for x in pred:groups[x["axis"],x["held"],x["fbin"]].append(x)
    rng=random.Random(seed("GDT166_NEIGHBOR_NULL"));worlds=[]
    for w in range(WORLDS):
        sums=Counter();nums=Counter()
        for key in sorted(groups,key=str):
            g=groups[key];ns=[x["predicted"] for x in g];rng.shuffle(ns)
            for x,n in zip(g,ns):
                rank=x["rank_map"].get(n);sums[x["axis"]]+=1/rank if rank else 0;nums[x["axis"]]+=1
        worlds.append({a:sums[a]/nums[a] if nums[a] else 0 for a,_ in AXES})
    return worlds,groups


def main():
    c=C();result=json.loads(RESULT.read_text());content=result.pop("result_content_sha256");c.add("result_content",csha(result)==content);result["result_content_sha256"]=content
    c.add("schema",result["schema"]=="GDT166_OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_RESULT_V1")
    c.add("status",result["status"]=="OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_NOT_TRANSFERABLE")
    c.add("design",json.loads(DESIGN.read_text())["status"]=="FROZEN_BEFORE_SCORING")
    for kind in ("inputs","implementation","outputs","documents"):
        for name,digest in result[kind].items():c.add(f"hash:{kind}:{name}",sha(R/name)==digest)
    rows,ctx,freq=rebuild(c);vocab=tuple(sorted({x["host"] for x in rows},key=opaque))
    inv=tsv(INVENTORY);c.add("inventory_n",len(inv)==38853)
    expected=[]
    for mode in MODES:
        for e in ctx[mode]:expected.append((mode,e["occurrence_id"],opaque(e["host"]),csha(sorted((opaque(k),v) for k,v in e["context"].items())),sum(e["context"].values()),len(e["context"])))
    for i,(out,exp) in enumerate(zip(inv,expected)):
        c.add(f"inventory:{i}",(out["context_mode"],out["occurrence_id"],out["focal_host_id"],out["context_sha256"],int(out["context_raw_count"]),int(out["context_unique_identities"]))==exp)
    artifacts,summary=refit(ctx,vocab,c);nulls={};caps={}
    exported_null=tsv(NULLS)
    for mode in MODES:nulls[mode],*caps[mode]=context_null(mode,ctx[mode],artifacts)
    means={m:sum(nulls[m])/WORLDS for m in MODES};maxs=[max(nulls[m][w]-means[m] for m in MODES) for w in range(WORLDS)]
    for w,out in enumerate(exported_null):
        for m in MODES:c.add(f"context_null:{w}:{m}",close(out[m+"_gain_per_focal"],nulls[m][w]))
        c.add(f"context_null_max:{w}",close(out["max3_null_centered_excess_per_focal"],maxs[w]))
    for m in MODES:
        out=summary[m,"HELD_FOLIO"];obs=float(out["gain_per_focal"]);p=(1+sum(x>=obs-1e-12 for x in nulls[m]))/(WORLDS+1);pm=(1+sum(x>=obs-means[m]-1e-12 for x in maxs))/(WORLDS+1)
        c.add("context_p:"+m,close(out["local_p"],p) and close(out["max3_p"],pm) and close(out["null_mean_gain_per_focal"],means[m]))
        c.add("context_capacity:"+m,result["null_capacity"][m]=={"swappable":caps[m][0],"variable":caps[m][1]})
    focal=tuple(h for h,_ in sorted(freq.items(),key=lambda x:(-x[1],opaque(x[0])))[:FOCAL_N]);cmass=Counter()
    for e in ctx["WHOLE_LINE"]:
        z=sum(e["context"].values())
        for y,n in e["context"].items():cmass[y]+=n/z
    cpanel=tuple(h for h,_ in sorted(cmass.items(),key=lambda x:(-x[1],opaque(x[0])))[:CONTEXT_N]);refs,pred=neighbors(ctx["WHOLE_LINE"],focal,cpanel,freq)
    er=tsv(NEIGHBORS);c.add("reference_neighbor_n",len(er)==len(refs)==64)
    for i,(out,x) in enumerate(zip(er,refs)):c.add(f"reference_neighbor:{i}",out["source_host"]==x[0] and out["neighbor_host"]==x[1] and close(out["cosine"],x[2]))
    ep=[x for x in tsv(NEIGHBOR_STABILITY) if x.get("source_host_id")];c.add("neighbor_prediction_n",len(ep)==len(pred)==799)
    for i,(out,x) in enumerate(zip(ep,pred)):
        c.add(f"neighbor_prediction:{i}",(out["axis"],out["held"],out["source_host"],out["predicted_neighbor"],int(out["held_rank"]),int(out["candidate_count"]))==(x["axis"],x["held"],x["source"],x["predicted"],x["rank"],x["candidates"]))
        c.add(f"neighbor_score:{i}",close(out["training_cosine"],x["train_cos"]) and close(out["held_cosine"],x["held_cos"]) and close(out["reciprocal_rank"],x["rr"]))
    worlds,groups=nnull(pred);en=tsv(NEIGHBOR_NULL);meansn={a:sum(x[a] for x in worlds)/WORLDS for a,_ in AXES};maxn=[max(x[a]-meansn[a] for a,_ in AXES) for x in worlds]
    for w,out in enumerate(en):
        for a,label in (("HELD_FOLIO","held_folio_mrr"),("HELD_SECTION","held_section_mrr"),("HELD_HAND","held_hand_mrr")):c.add(f"neighbor_null:{w}:{a}",close(out[label],worlds[w][a]))
        c.add(f"neighbor_null_max:{w}",close(out["max3_null_centered_excess"],maxn[w]))
    es={x["axis"]:x for x in tsv(NEIGHBOR_STABILITY) if x.get("predictions")}
    for a,_ in AXES:
        pp=[x for x in pred if x["axis"]==a];obs=sum(x["rr"] for x in pp)/len(pp);local=(1+sum(x[a]>=obs-1e-12 for x in worlds))/(WORLDS+1);pm=(1+sum(x>=obs-meansn[a]-1e-12 for x in maxn))/(WORLDS+1);out=es[a]
        c.add("neighbor_summary:"+a,int(out["predictions"])==len(pp) and close(out["mean_reciprocal_rank"],obs) and close(out["null_mean"],meansn[a]) and close(out["local_p"],local) and close(out["max3_p"],pm))
    c.add("decision",result["decision_inputs"]=={"any_held_folio_positive":False,"neighbor_stable_all_splits":False,"passing_context_modes":[]})
    c.add("f84",all(v is False for v in result["f84r"].values()))
    payload={"schema":"GDT166_OPAQUE_HOST_DISTRIBUTIONAL_CONTEXT_VALIDATION_V1","status":"PASS_INDEPENDENT_CONTEXT_MODELS_AND_BOTH_FULL_NULLS","checks_passed":len(c.rows),"checks_failed":0,"check_manifest_sha256":csha(c.rows),"scope":"Nonimporting source/context rebuild, all held exact-host weighted models, all 3x1024 context-null values, PPMI neighbor predictions, all 1024 neighbor-null values, hashes and decision.","result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"f84r":{"opened":False,"queried":False,"retained":False,"joined":False,"scored":False}}
    payload["validation_content_sha256"]=csha(payload);VALIDATION.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":payload["status"],"checks":payload["checks_passed"],"result_sha256":payload["result_sha256"]},sort_keys=True))


if __name__=="__main__":main()
