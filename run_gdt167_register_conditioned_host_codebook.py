#!/usr/bin/env python3
"""GDT167: opaque register-conditioned host codebooks and glyph-blind alignment."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
SOURCE = R / "gdt062_right_family_inventory.tsv"
DESIGN = R / "gdt167_design.json"
METHOD = R / "GDT167_REGISTER_CONDITIONED_HOST_CODEBOOK_METHOD.md"
REPORT = R / "GDT167_REGISTER_CONDITIONED_HOST_CODEBOOK_REPORT.md"
CAPACITY = R / "gdt167_stratum_capacity.tsv"
FOLDS = R / "gdt167_codebook_fold_scores.tsv"
SCORES = R / "gdt167_codebook_scores.tsv"
CODE_NULL = R / "gdt167_codebook_null.tsv"
PANELS = R / "gdt167_host_panels.tsv"
GEOMETRY = R / "gdt167_geometry_stability.tsv"
GEOMETRY_NULL = R / "gdt167_geometry_null.tsv"
MAPPINGS = R / "gdt167_alignment_mappings.tsv"
ALIGNMENT = R / "gdt167_alignment_scores.tsv"
ALIGNMENT_NULL = R / "gdt167_alignment_null.tsv"
COUNTER = R / "gdt167_counterexamples.tsv"
VARIANTS = R / "gdt167_variant_log.tsv"
RESULT = R / "gdt167_result.json"

STRATA = {
    "HERBAL_A": ("H", "A"),
    "HERBAL_B": ("H", "B"),
    "STARS_RECIPE_B": ("S", "B"),
    "PHARMA_A": ("P", "A"),
    "BIOLOGICAL_B": ("B", "B"),
}
MODES = ("WINDOW_PM2", "WHOLE_LINE")
FEATURES = ("section", "currier", "hand", "frequency_bin", "position_quartile", "line_count_bin")
BLOCKS = ((0, 3), (3, 5), (5, 8), (8, 10))
ALPHA, BETA, WORLDS = 32.0, 16.0, 1024
PANEL_N, CONTEXT_N = 10, 128


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def opaque(x): return "H" + hashlib.sha256(x.encode()).hexdigest()[:16]
def seed(x): return int(hashlib.sha256(x.encode()).hexdigest()[:16], 16)
def csha(x): return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def fbin(n): return "F1" if n == 1 else "F2_4" if n <= 4 else "F5_15" if n <= 15 else "F16_63" if n <= 63 else "F64P"
def lbin(n): return str(n) if n <= 4 else "5_7" if n <= 7 else "8P"
def lkey(x): page, line = x.split("."); return page, int(line)


def write(path, rows):
    fields=[]
    for row in rows:
        for key in row:
            if key not in fields: fields.append(key)
    if "claim_state" in fields: fields.remove("claim_state"); fields.append("claim_state")
    with Path(path).open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)


def stratum_for(section, currier):
    for name, key in STRATA.items():
        if (section, currier) == key: return name
    return None


def load():
    rows=[]; total=rejected=0
    with SOURCE.open(encoding="utf-8",newline="") as h:
        for raw in csv.DictReader(h,delimiter="\t"):
            total+=1; page,locus=raw["page"],raw["locus"]
            if page.startswith("f84") or locus.startswith("f84"): rejected+=1;continue
            stratum=stratum_for(raw["section"],raw["currier"])
            if stratum is None or int(raw["group_count"]) <= 1: continue
            rows.append({"host":raw["page_host"],"locus":locus,"folio":raw["physical_folio"],
                         "section":raw["section"],"currier":raw["currier"],"hand":raw["hand"],
                         "index":int(raw["group_index"]),"group_count":int(raw["group_count"]),
                         "position_quartile":raw["position_quartile"],"stratum":stratum})
    assert (total,rejected)==(15592,228)
    by_stratum=defaultdict(list)
    for x in rows: by_stratum[x["stratum"]].append(x)
    expected={"HERBAL_A":3909,"HERBAL_B":1323,"STARS_RECIPE_B":4854,"PHARMA_A":650,"BIOLOGICAL_B":3153}
    assert {s:len(by_stratum[s]) for s in STRATA}==expected
    contexts={s:{m:[] for m in MODES} for s in STRATA}; capacity=[]
    for s in STRATA:
        rr=by_stratum[s];freq=Counter(x["host"] for x in rr); lines=defaultdict(list)
        for x in rr:
            x["frequency_bin"]=fbin(freq[x["host"]]);x["line_count_bin"]=lbin(x["group_count"])
            x["half"]=int(hashlib.sha256(f"{s}|{x['folio']}".encode()).hexdigest()[:8],16)%2
            x["occurrence_id"]=f"{s}:{x['locus']}:{x['index']}";x["nuisance_key"]=tuple(x[f] for f in FEATURES)
            lines[x["locus"]].append(x)
        window_links=line_links=0
        for locus in sorted(lines,key=lkey):
            line=sorted(lines[locus],key=lambda x:x["index"]);bag=Counter(x["host"] for x in line)
            for i,x in enumerate(line):
                w=Counter(line[j]["host"] for j in range(max(0,i-2),min(len(line),i+3)) if j!=i)
                b=bag.copy();b[x["host"]]-=1
                if not b[x["host"]]:del b[x["host"]]
                contexts[s]["WINDOW_PM2"].append({**x,"context":w});contexts[s]["WHOLE_LINE"].append({**x,"context":b})
                window_links+=sum(w.values());line_links+=sum(b.values())
        folios=sorted({x["folio"] for x in rr});hands=Counter(x["hand"] for x in rr)
        capacity.append({"stratum":s,"section":STRATA[s][0],"currier":STRATA[s][1],"groups":len(rr),
                         "physical_lines":len(lines),"physical_folios":len(folios),"exact_hosts":len(freq),
                         "half0_folios":len({x['folio'] for x in rr if x['half']==0}),
                         "half1_folios":len({x['folio'] for x in rr if x['half']==1}),
                         "hands":json.dumps(dict(sorted(hands.items())),sort_keys=True),
                         "window_raw_links":window_links,"line_raw_links":line_links,
                         "claim_state":"REGISTER_CAPACITY_NO_SEMANTIC_CLASS"})
    return rows,by_stratum,contexts,capacity,total,rejected


def train(events,vocab):
    target=Counter();ft=[Counter() for _ in FEATURES];fn=[Counter() for _ in FEATURES];ht=Counter();hn=Counter()
    for e in events:
        z=sum(e["context"].values())
        for y,n in e["context"].items():
            w=n/z;target[y]+=w;ht[e["host"],y]+=w
            for j,f in enumerate(FEATURES):ft[j][e[f],y]+=w
        hn[e["host"]]+=1
        for j,f in enumerate(FEATURES):fn[j][e[f]]+=1
    return {"target":target,"n":float(len(events)),"v":len(vocab),"ft":ft,"fn":fn,"ht":ht,"hn":hn}


def probs(m,e,y):
    q=(m["target"][y]+.5)/(m["n"]+.5*m["v"]);parts=[]
    for j,f in enumerate(FEATURES):parts.append((m["ft"][j][e[f],y]+ALPHA*q)/(m["fn"][j][e[f]]+ALPHA))
    nuisance=sum(parts)/len(parts);host=(m["ht"][e["host"],y]+BETA*nuisance)/(m["hn"][e["host"]]+BETA)
    return q,nuisance,host


def score(m,e):
    z=sum(e["context"].values());o=Counter()
    for y,n in e["context"].items():
        w=n/z;q,u,h=probs(m,e,y);o["unigram_bits"]-=w*math.log2(q);o["nuisance_bits"]-=w*math.log2(u);o["host_bits"]-=w*math.log2(h)
    o["gain_bits"]=o["nuisance_bits"]-o["host_bits"]
    return o


def codebook_scores(contexts):
    folds=[];artifacts={}
    for s in STRATA:
        vocab=tuple(sorted({e["host"] for e in contexts[s]["WHOLE_LINE"]},key=opaque))
        for mode in MODES:
            events=contexts[s][mode]
            for held in sorted({e["folio"] for e in events}):
                tr=[e for e in events if e["folio"]!=held];te=[e for e in events if e["folio"]==held];m=train(tr,vocab);o=Counter();seen=0
                for e in te:o.update(score(m,e));seen+=int(m["hn"][e["host"]]>0)
                folds.append({"stratum":s,"context_mode":mode,"axis":"HELD_FOLIO","held":held,
                              "focal_occurrences":len(te),"training_occurrences":len(tr),"source_seen":seen,
                              "source_seen_fraction":seen/len(te),"unigram_bits":o["unigram_bits"],
                              "nuisance_bits":o["nuisance_bits"],"host_bits":o["host_bits"],"gain_bits":o["gain_bits"],
                              "gain_per_focal":o["gain_bits"]/len(te),"claim_state":"REGISTER_OPAQUE_CODEBOOK_NO_LEXEME_OR_MEANING"})
                artifacts[s,mode,held]=(m,te)
            if s=="HERBAL_B":
                for held in sorted({e["hand"] for e in events}):
                    tr=[e for e in events if e["hand"]!=held];te=[e for e in events if e["hand"]==held];m=train(tr,vocab);o=Counter();seen=0
                    for e in te:o.update(score(m,e));seen+=int(m["hn"][e["host"]]>0)
                    folds.append({"stratum":s,"context_mode":mode,"axis":"HELD_HAND","held":held,
                                  "focal_occurrences":len(te),"training_occurrences":len(tr),"source_seen":seen,
                                  "source_seen_fraction":seen/len(te),"unigram_bits":o["unigram_bits"],
                                  "nuisance_bits":o["nuisance_bits"],"host_bits":o["host_bits"],"gain_bits":o["gain_bits"],
                                  "gain_per_focal":o["gain_bits"]/len(te),"claim_state":"REGISTER_OPAQUE_CODEBOOK_NO_LEXEME_OR_MEANING"})
    return folds,artifacts


def code_null(s,mode,events,artifacts):
    prepared={};swap=variable=0
    for held in sorted({e["folio"] for e in events}):
        m,te=artifacts[s,mode,held];groups=defaultdict(list)
        for e in te:groups[e["nuisance_key"]].append(e)
        packed={}
        for key,g in groups.items():
            sources=sorted({e["host"] for e in g},key=opaque);targets={y for e in g for y in e["context"]};ex=g[0];logs={}
            for src in sources:
                p=dict(ex);p["host"]=src
                for y in targets:
                    _,u,h=probs(m,p,y);logs[src,y]=math.log2(h/u)
            lookup={}
            for e in g:
                z=sum(e["context"].values())
                for src in sources:lookup[e["occurrence_id"],src]=sum(n/z*logs[src,y] for y,n in e["context"].items())
            packed[key]=(g,lookup)
        prepared[held]=packed;swap+=sum(len(g) for g in groups.values() if len(g)>=2);variable+=sum(len(g) for g in groups.values() if len({e['host'] for e in g})>=2)
    rng=random.Random(seed(f"GDT167_CODE_NULL_{s}_{mode}"));values=[]
    for _ in range(WORLDS):
        gain=0.0
        for held in sorted(prepared):
            for key in sorted(prepared[held],key=str):
                g,lookup=prepared[held][key];src=[e["host"] for e in g];rng.shuffle(src)
                gain+=sum(lookup[e["occurrence_id"],x] for e,x in zip(g,src))
        values.append(gain/len(events))
    return values,swap,variable


def aggregate_code(folds,nulls,caps):
    rows=[]
    for s in STRATA:
        for mode in MODES:
            for axis in ("HELD_FOLIO","HELD_HAND"):
                rr=[x for x in folds if x["stratum"]==s and x["context_mode"]==mode and x["axis"]==axis]
                if not rr:continue
                n=sum(x["focal_occurrences"] for x in rr);gain=sum(x["gain_bits"] for x in rr)
                rows.append({"stratum":s,"context_mode":mode,"axis":axis,"focal_occurrences":n,"folds":len(rr),
                             "gain_bits":gain,"gain_per_focal":gain/n,"positive_folds":sum(x["gain_bits"]>0 for x in rr),
                             "source_seen_fraction":sum(x["source_seen"] for x in rr)/n,
                             "claim_state":"REGISTER_OPAQUE_CODEBOOK_NO_LEXEME_OR_MEANING"})
    means={k:sum(v)/WORLDS for k,v in nulls.items()};maxs=[max(nulls[k][w]-means[k] for k in nulls) for w in range(WORLDS)]
    for row in rows:
        if row["axis"]!="HELD_FOLIO":continue
        key=row["stratum"],row["context_mode"];values=nulls[key];obs=row["gain_per_focal"]
        row["null_mean_gain_per_focal"]=means[key];row["alignment_excess_per_focal"]=obs-means[key]
        row["local_p"]=(1+sum(x>=obs-1e-12 for x in values))/(WORLDS+1)
        row["max10_p"]=(1+sum(x>=obs-means[key]-1e-12 for x in maxs))/(WORLDS+1)
        row["null_swappable"]=caps[key][0];row["null_variable"]=caps[key][1]
    return rows,maxs


def panels(by_stratum,contexts):
    out={};rows=[]
    for s in STRATA:
        rr=by_stratum[s];freq=Counter(x["host"] for x in rr);half={h:Counter(x["host"] for x in rr if x["half"]==h) for h in (0,1)}
        eligible=[host for host,n in sorted(freq.items(),key=lambda x:(-x[1],opaque(x[0]))) if half[0][host]>=4 and half[1][host]>=4]
        assert len(eligible)>=PANEL_N
        panel=tuple(eligible[:PANEL_N]);cm=Counter()
        for e in contexts[s]["WHOLE_LINE"]:
            z=sum(e["context"].values())
            for y,n in e["context"].items():cm[y]+=n/z
        cpanel=tuple(y for y,_ in sorted(cm.items(),key=lambda x:(-x[1],opaque(x[0])))[:CONTEXT_N]);out[s]=(panel,cpanel)
        for rank,host in enumerate(panel):
            rows.append({"stratum":s,"rank":rank,"host_id":opaque(host),"host":host,"total_occurrences":freq[host],
                         "half0_occurrences":half[0][host],"half1_occurrences":half[1][host],
                         "frequency_block":next(i for i,(a,b) in enumerate(BLOCKS) if a<=rank<b),
                         "claim_state":"OPAQUE_CAPACITY_SELECTED_HOST_NO_LEXEME_OR_MEANING"})
    return out,rows


def ppmi(events,panel,cpanel):
    counts=defaultdict(Counter);mass=Counter();glob=Counter()
    for e in events:
        if e["host"] not in panel:continue
        z=sum(e["context"].values())
        for y,n in e["context"].items():
            q=y if y in cpanel else "__OTHER__";w=n/z;counts[e["host"]][q]+=w;glob[q]+=w
        mass[e["host"]]+=1
    dims=tuple(sorted(set(cpanel)|{"__OTHER__"},key=opaque));gt=sum(glob.values());mat=[]
    for host in panel:
        v=np.zeros(len(dims))
        if mass[host] and gt:
            for j,y in enumerate(dims):
                if counts[host][y] and glob[y]:v[j]=max(0,math.log2((counts[host][y]/mass[host])/(glob[y]/gt)))
        z=float(np.linalg.norm(v));mat.append(v/z if z else v)
    return np.stack(mat),mass


def sim_matrix(events,panel,cpanel):
    p,_=ppmi(events,panel,cpanel);return p@p.T


def upper(matrix,mapping=None):
    if mapping is not None:matrix=matrix[np.ix_(mapping,mapping)]
    return np.array([matrix[i,j] for i in range(PANEL_N) for j in range(i+1,PANEL_N)],dtype=float)


def corr(a,b):
    a=np.asarray(a);b=np.asarray(b)
    if np.std(a)<1e-15 or np.std(b)<1e-15:return 0.0
    return float(np.corrcoef(a,b)[0,1])


def random_block_mapping(rng):
    mapping=list(range(PANEL_N))
    for a,b in BLOCKS:
        block=mapping[a:b];rng.shuffle(block);mapping[a:b]=block
    return mapping


def internal_geometry(contexts,panel_data):
    observed={};nulls={};rows=[]
    for s in STRATA:
        panel,cpanel=panel_data[s];events=contexts[s]["WHOLE_LINE"]
        a=sim_matrix([e for e in events if e["half"]==0],panel,cpanel);b=sim_matrix([e for e in events if e["half"]==1],panel,cpanel)
        obs=corr(upper(a),upper(b));rng=random.Random(seed("GDT167_GEOMETRY_"+s));values=[]
        for _ in range(WORLDS):values.append(corr(upper(a),upper(b,random_block_mapping(rng))))
        observed[s]=obs;nulls[s]=values
    means={s:sum(nulls[s])/WORLDS for s in STRATA};maxs=[max(nulls[s][w]-means[s] for s in STRATA) for w in range(WORLDS)]
    for s in STRATA:
        obs=observed[s];values=nulls[s]
        rows.append({"test":"FOLIO_HALF_STABILITY","stratum":s,"correlation":obs,"null_mean":means[s],
                     "excess":obs-means[s],"local_p":(1+sum(x>=obs-1e-12 for x in values))/(WORLDS+1),
                     "max5_p":(1+sum(x>=obs-means[s]-1e-12 for x in maxs))/(WORLDS+1),
                     "claim_state":"REGISTER_INTERNAL_GEOMETRY_NO_LEXEME_OR_MEANING"})
    s="HERBAL_B";panel,cpanel=panel_data[s];events=contexts[s]["WHOLE_LINE"]
    a=sim_matrix([e for e in events if e["hand"]=="2"],panel,cpanel);b=sim_matrix([e for e in events if e["hand"] in ("3","5")],panel,cpanel)
    obs=corr(upper(a),upper(b));rng=random.Random(seed("GDT167_GEOMETRY_HERBAL_B_HAND"));values=[corr(upper(a),upper(b,random_block_mapping(rng))) for _ in range(WORLDS)]
    rows.append({"test":"HAND2_VS_HAND3_5","stratum":s,"correlation":obs,"null_mean":sum(values)/WORLDS,"excess":obs-sum(values)/WORLDS,
                 "local_p":(1+sum(x>=obs-1e-12 for x in values))/(WORLDS+1),"max5_p":"NOT_IN_FIVE_STRATUM_FAMILY",
                 "claim_state":"REGISTER_CROSS_HAND_GEOMETRY_SENSITIVITY_NO_AUTHORSHIP"})
    null_rows=[]
    for w in range(WORLDS):
        row={"world":w,**{s+"_correlation":nulls[s][w] for s in STRATA},"max5_null_centered":maxs[w],
             "claim_state":"REGISTER_INTERNAL_GEOMETRY_BLOCK_PERMUTATION_NULL"};null_rows.append(row)
    return rows,null_rows,observed,nulls


def signatures(events,panel):
    occurrence=Counter();context=defaultdict(Counter);pos=defaultdict(Counter);line=defaultdict(Counter)
    for e in events:
        if e["host"] not in panel:continue
        occurrence[e["host"]]+=1;pos[e["host"]][e["position_quartile"]]+=1;line[e["host"]][e["line_count_bin"]]+=1
        z=sum(e["context"].values())
        for y,n in e["context"].items():context[e["host"]][y]+=n/z
    matrix=[]
    for h in panel:
        mass=occurrence[h];vals=sorted(context[h].values(),reverse=True);total=sum(vals);p=[x/total for x in vals] if total else []
        entropy=-sum(x*math.log(x) for x in p if x>0)/(math.log(len(p)) if len(p)>1 else 1)
        conc=lambda k:sum(vals[:k])/total if total else 0
        self_frac=context[h][h]/total if total else 0
        v=[math.log1p(mass)/math.log1p(max(1,len(events))),entropy,conc(1),conc(3),conc(5),self_frac]
        v += [pos[h][f"Q{i}"]/mass if mass else 0 for i in range(4)]
        v += [line[h][x]/mass if mass else 0 for x in ("2","3","4","5_7","8P")]
        matrix.append(v)
    x=np.array(matrix,dtype=float);mean=x.mean(axis=0);sd=x.std(axis=0);sd[sd<1e-12]=1.0
    return (x-mean)/sd


def hungarian(cost):
    n=len(cost);u=[0.0]*(n+1);v=[0.0]*(n+1);p=[0]*(n+1);way=[0]*(n+1)
    for i in range(1,n+1):
        p[0]=i;j0=0;minv=[float("inf")]*(n+1);used=[False]*(n+1)
        while True:
            used[j0]=True;i0=p[j0];delta=float("inf");j1=0
            for j in range(1,n+1):
                if not used[j]:
                    cur=cost[i0-1][j-1]-u[i0]-v[j]
                    if cur<minv[j]-1e-15:minv[j]=cur;way[j]=j0
                    if minv[j]<delta-1e-15:delta=minv[j];j1=j
            for j in range(n+1):
                if used[j]:u[p[j]]+=delta;v[j]-=delta
                else:minv[j]-=delta
            j0=j1
            if p[j0]==0:break
        while True:
            j1=way[j0];p[j0]=p[j1];j0=j1
            if j0==0:break
    ans=[0]*n
    for j in range(1,n+1):ans[p[j]-1]=j-1
    return ans


def block_alignment(a,b):
    mapping=[0]*PANEL_N
    for lo,hi in BLOCKS:
        cost=((a[lo:hi,None,:]-b[None,lo:hi,:])**2).sum(axis=2).tolist();assign=hungarian(cost)
        for i,j in enumerate(assign):mapping[lo+i]=lo+j
    return mapping


def cross_alignment(contexts,panel_data):
    pairs=list(itertools.combinations(STRATA,2));fold_rows=[];map_rows=[];cell_null={}
    for sa,sb in pairs:
        pa,ca=panel_data[sa];pb,cb=panel_data[sb]
        for train_half in (0,1):
            test_half=1-train_half;ea=contexts[sa]["WHOLE_LINE"];eb=contexts[sb]["WHOLE_LINE"]
            sig_a=signatures([e for e in ea if e["half"]==train_half],pa);sig_b=signatures([e for e in eb if e["half"]==train_half],pb)
            mapping=block_alignment(sig_a,sig_b);ga=sim_matrix([e for e in ea if e["half"]==test_half],pa,ca);gb=sim_matrix([e for e in eb if e["half"]==test_half],pb,cb)
            obs=corr(upper(ga),upper(gb,mapping));cell=(sa,sb,train_half);rng=random.Random(seed("GDT167_ALIGN_"+"|".join(map(str,cell))));values=[]
            for _ in range(WORLDS):values.append(corr(upper(ga),upper(gb,random_block_mapping(rng))))
            cell_null[cell]=values;fold_rows.append({"row_type":"FOLD","stratum_a":sa,"stratum_b":sb,"train_half":train_half,"test_half":test_half,
                                                    "correlation":obs,"claim_state":"GLYPH_BLIND_HELD_GEOMETRY_ALIGNMENT"})
            for i,j in enumerate(mapping):
                map_rows.append({"stratum_a":sa,"stratum_b":sb,"train_half":train_half,"test_half":test_half,"rank_a":i,"rank_b":j,
                                 "host_a_id":opaque(pa[i]),"host_b_id":opaque(pb[j]),"host_a":pa[i],"host_b":pb[j],
                                 "frequency_block":next(k for k,(lo,hi) in enumerate(BLOCKS) if lo<=i<hi),
                                 "claim_state":"GLYPH_BLIND_ASSIGNMENT_DISPLAY_ONLY_NO_LEXEME_OR_MEANING"})
    pair_observed={};pair_null={}
    for pair in pairs:
        pair_observed[pair]=sum(x["correlation"] for x in fold_rows if (x["stratum_a"],x["stratum_b"])==pair)/2
        pair_null[pair]=[(cell_null[pair+(0,)][w]+cell_null[pair+(1,)][w])/2 for w in range(WORLDS)]
    means={p:sum(v)/WORLDS for p,v in pair_null.items()};maxs=[max(pair_null[p][w]-means[p] for p in pairs) for w in range(WORLDS)]
    summary=[]
    for pair in pairs:
        obs=pair_observed[pair];v=pair_null[pair]
        summary.append({"row_type":"PAIR_SUMMARY","stratum_a":pair[0],"stratum_b":pair[1],"folds":2,"mean_correlation":obs,
                        "null_mean":means[pair],"excess":obs-means[pair],"local_p":(1+sum(x>=obs-1e-12 for x in v))/(WORLDS+1),
                        "max10_p":(1+sum(x>=obs-means[pair]-1e-12 for x in maxs))/(WORLDS+1),
                        "claim_state":"GLYPH_BLIND_HELD_GEOMETRY_ALIGNMENT"})
    global_observed=sum(pair_observed.values())/len(pairs);global_null=[sum(pair_null[p][w] for p in pairs)/len(pairs) for w in range(WORLDS)]
    global_p=(1+sum(x>=global_observed-1e-12 for x in global_null))/(WORLDS+1)
    summary.append({"row_type":"GLOBAL_SUMMARY","stratum_a":"ALL_FIVE","stratum_b":"ALL_TEN_PAIRS","folds":20,
                    "mean_correlation":global_observed,"null_mean":sum(global_null)/WORLDS,"excess":global_observed-sum(global_null)/WORLDS,
                    "local_p":global_p,"max10_p":"NOT_APPLICABLE_GLOBAL_ENDPOINT","claim_state":"GLYPH_BLIND_COMMON_ALIGNMENT_GLOBAL_TEST"})
    null_rows=[]
    for w in range(WORLDS):
        row={"world":w}
        for pair in pairs:row[pair[0]+"__"+pair[1]+"_mean_correlation"]=pair_null[pair][w]
        row["global_mean_correlation"]=global_null[w];row["max10_null_centered"]=maxs[w];row["claim_state"]="BLOCK_PRESERVING_RANDOM_ALIGNMENT_NULL";null_rows.append(row)
    return fold_rows+summary,map_rows,null_rows,summary,pair_observed,global_observed,global_p


def main():
    design=json.loads(DESIGN.read_text());assert design["status"]=="FROZEN_BEFORE_SCORING" and design["alignment"]["assignment_constraint"]=="SAME_FOUR_FREQUENCY_RANK_BLOCKS_AS_NULL"
    rows,by_stratum,contexts,capacity,total,rejected=load();folds,artifacts=codebook_scores(contexts);nulls={};null_caps={}
    for s in STRATA:
        for mode in MODES:nulls[s,mode],sw,var=code_null(s,mode,contexts[s][mode],artifacts);null_caps[s,mode]=(sw,var)
    code_scores,code_max=aggregate_code(folds,nulls,null_caps);code_null_rows=[]
    for w in range(WORLDS):
        row={"world":w}
        for s in STRATA:
            for mode in MODES:row[s+"__"+mode+"_gain_per_focal"]=nulls[s,mode][w]
        row["max10_null_centered"]=code_max[w];row["claim_state"]="REGISTER_FOCAL_ID_ALIGNMENT_NULL";code_null_rows.append(row)
    panel_data,panel_rows=panels(by_stratum,contexts);geometry_rows,geometry_null_rows,_,_=internal_geometry(contexts,panel_data)
    alignment_rows,mapping_rows,alignment_null_rows,alignment_summary,pair_observed,global_alignment,global_p=cross_alignment(contexts,panel_data)

    geometry_pass={r["stratum"] for r in geometry_rows if r["test"]=="FOLIO_HALF_STABILITY" and r["correlation"]>0 and float(r["max5_p"])<=.05}
    codebook_pass=[]
    for s in STRATA:
        candidates=[r for r in code_scores if r["stratum"]==s and r["axis"]=="HELD_FOLIO"]
        if any(r["gain_bits"]>0 and r["positive_folds"]/r["folds"]>=.6 and r["max10_p"]<=.05 for r in candidates) and s in geometry_pass:codebook_pass.append(s)
    pair_summaries=[r for r in alignment_summary if r["row_type"]=="PAIR_SUMMARY"]
    positive_pairs=[r for r in pair_summaries if r["mean_correlation"]>0];corrected=[r for r in pair_summaries if r["mean_correlation"]>0 and r["max10_p"]<=.05]
    covered={x for r in corrected for x in (r["stratum_a"],r["stratum_b"])}
    alignment_pass=global_p<=.05 and len(positive_pairs)>=8 and len(corrected)>=3 and covered==set(STRATA)
    if len(codebook_pass)>=3 and alignment_pass:status="REGISTER_CODEBOOKS_WITH_COMMON_REBOUND_ALIGNMENT"
    elif len(codebook_pass)>=3:status="REGISTER_SPECIFIC_CODEBOOKS_WITHOUT_COMMON_ALIGNMENT"
    elif len(geometry_pass)>=3 or alignment_pass:status="REGISTER_GEOMETRY_STABLE_BUT_CODEBOOK_PREDICTION_NEGATIVE"
    else:status="NO_STABLE_REGISTER_CODEBOOK_OR_ALIGNMENT"

    counter=[]
    for r in code_scores:
        if r["axis"]=="HELD_FOLIO" and r["gain_bits"]<=0:counter.append({"counterexample_type":"NEGATIVE_REGISTER_CODEBOOK","item":r["stratum"]+":"+r["context_mode"],"evidence":f"gain={r['gain_bits']:+.6f}; positive={r['positive_folds']}/{r['folds']}","impact":"Register conditioning does not produce positive exact-host held codelength."})
    for r in pair_summaries:
        if r["mean_correlation"]<=0:counter.append({"counterexample_type":"NONPOSITIVE_CROSS_REGISTER_ALIGNMENT","item":r["stratum_a"]+"<->"+r["stratum_b"],"evidence":f"mean correlation={r['mean_correlation']:+.6f}","impact":"Marginal structural mapping does not preserve held co-occurrence geometry."})
    variants=[{"variant_id":"V00","status":"PRIMARY","description":"Five separate WHOLE_LINE register codebooks."},{"variant_id":"V01","status":"SENSITIVITY","description":"Five separate WINDOW_PM2 register codebooks."},{"variant_id":"V02","status":"TRANSFER","description":"HERBAL_B held-hand scores."},{"variant_id":"V03","status":"GEOMETRY","description":"Five deterministic folio-half geometry correlations plus Herbal-B cross-hand."},{"variant_id":"V04","status":"ALIGNMENT","description":"Ten block-constrained marginal-signature Hungarian register pairs x two folds."},{"variant_id":"V05","status":"NULL","description":"1024 worlds for codebook, geometry, and alignment families."},{"variant_id":"V06","status":"FORBIDDEN","description":"No raw/same-group HPR2/glyph/string/identity-alignment/semantic/f84 feature."}]
    def fmt(rr):return [{k:(f"{v:.12f}" if isinstance(v,float) else v) for k,v in x.items()} for x in rr]
    write(CAPACITY,capacity);write(FOLDS,fmt(folds));write(SCORES,fmt(code_scores));write(CODE_NULL,fmt(code_null_rows));write(PANELS,panel_rows);write(GEOMETRY,fmt(geometry_rows));write(GEOMETRY_NULL,fmt(geometry_null_rows));write(MAPPINGS,mapping_rows);write(ALIGNMENT,fmt(alignment_rows));write(ALIGNMENT_NULL,fmt(alignment_null_rows));write(COUNTER,counter);write(VARIANTS,variants)

    report=f"""# GDT167 — register-conditioned opaque host codebooks

Decision: **{status}**.

## Within-register held-folio prediction

| stratum | context | gain bits | bits/focal | positive folios | null excess | local/max10 p | geometry corr/max5 p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
"""+"".join(f"| `{r['stratum']}` | `{r['context_mode']}` | {r['gain_bits']:+.3f} | {r['gain_per_focal']:+.5f} | {r['positive_folds']}/{r['folds']} | {r['alignment_excess_per_focal']:+.5f} | {r['local_p']:.4f}/{r['max10_p']:.4f} | {next(x for x in geometry_rows if x['stratum']==r['stratum'] and x['test']=='FOLIO_HALF_STABILITY')['correlation']:+.4f}/{float(next(x for x in geometry_rows if x['stratum']==r['stratum'] and x['test']=='FOLIO_HALF_STABILITY')['max5_p']):.4f} |\n" for r in code_scores if r["axis"]=="HELD_FOLIO")+f"""

Predictive codebook strata: `{json.dumps(codebook_pass)}`.  Geometry-stable
strata: `{json.dumps(sorted(geometry_pass))}`.  Herbal-B held-hand scores are
reported in the machine tables and are sensitivities, not independent samples.

## Glyph-blind cross-register alignment

| register pair | held geometry correlation | null excess | local/max10 p |
| --- | ---: | ---: | ---: |
"""+"".join(f"| `{r['stratum_a']} <-> {r['stratum_b']}` | {r['mean_correlation']:+.4f} | {r['excess']:+.4f} | {r['local_p']:.4f}/{r['max10_p']:.4f} |\n" for r in pair_summaries)+f"""

Overall ten-pair mean correlation is {global_alignment:+.4f}, with global
p={global_p:.6f}.  The common re-bound compiler gate is
`{'PASS' if alignment_pass else 'FAIL'}`.

Mappings were fitted only from anonymous marginal frequency, entropy,
concentration, self-context, position and line-size signatures.  Host strings,
shared identities and glyph similarity were unavailable.  Held targets were
separate-folio-half host--host co-occurrence geometries.

## Interpretation

This result distinguishes predictive exact-host codebooks, internally stable
register geometry, and cross-register anonymous geometry alignment.  None is a
word or semantic identification.  Correlated whole-line contexts are weighted
descriptive evidence, not independent linguistic tokens.

All f84-prefix rows were rejected before retention.  No f84r material was
opened, queried, retained, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
    result={"schema":"GDT167_REGISTER_CONDITIONED_HOST_CODEBOOK_RESULT_V1","status":status,"capacity":{"source_total":total,"f84_rejected":rejected,"retained_powered_groups":len(rows)},"codebook_scores":{r['stratum']+':'+r['context_mode']+':'+r['axis']:r for r in code_scores},"codebook_supported_strata":codebook_pass,"geometry_stable_strata":sorted(geometry_pass),"alignment":{"global_mean_correlation":global_alignment,"global_p":global_p,"positive_pairs":len(positive_pairs),"max10_positive_pairs":len(corrected),"registers_covered_by_corrected_pairs":sorted(covered),"common_rebound_gate":alignment_pass},"decision_inputs":{"codebook_supported_count":len(codebook_pass),"geometry_stable_count":len(geometry_pass),"common_alignment":alignment_pass},"interpretation":"Opaque register-conditioned context codes and glyph-blind structural-space alignment only.","claim_ceiling":"No word, lexeme, code value, morpheme, POS, language, semantic role, meaning, plaintext, or translation.","f84r":{"opened":False,"queried":False,"retained":False,"joined":False,"scored":False},"inputs":{p.name:sha(p) for p in (SOURCE,DESIGN,R/"gdt166_result.json",R/"gdt166_context_scores.tsv",R/"gdt166_neighbor_relations.tsv")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{p.name:sha(p) for p in (CAPACITY,FOLDS,SCORES,CODE_NULL,PANELS,GEOMETRY,GEOMETRY_NULL,MAPPINGS,ALIGNMENT,ALIGNMENT_NULL,COUNTER,VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,"codebook_strata":codebook_pass,"geometry_strata":sorted(geometry_pass),"alignment_global":global_alignment,"alignment_p":global_p},sort_keys=True))


if __name__=="__main__":main()
