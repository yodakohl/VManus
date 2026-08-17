#!/usr/bin/env python3
"""Score the frozen full-atlas host/raw distributional representations."""
from __future__ import annotations
import csv,hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path

REPS=("HOST_EXACT","HOST_CHAR2","HOST_CHAR3","RAW_CHAR3","HOST_LENGTH")
def read(p):
    with Path(p).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows):
    with Path(p).open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ngrams(s,n):
    s="^"+s+"$";return [s[i:i+n] for i in range(max(0,len(s)-n+1))]
def wj(a,b):
    keys=set(a)|set(b);d=sum(max(a[k],b[k]) for k in keys);return sum(min(a[k],b[k]) for k in keys)/d if d else 0
def ms(x):
    m=sum(x)/len(x);s=math.sqrt(sum((v-m)**2 for v in x)/len(x));return m,s or 1

def main():
    d=json.loads(Path("gdt178_design.json").read_text());cand=read("gdt169_external_referent_candidates.tsv")
    by=defaultdict(list)
    for r in read("gdt062_right_family_inventory.tsv"):
        if r["page"].startswith("f84"):continue
        by[r["page"]].append(r)
    features={};meta={}
    for page,rr in by.items():
        mm={(x["section"],x["currier"],x["hand"],x["physical_folio"]) for x in rr};assert len(mm)==1;meta[page]=next(iter(mm))
        f={k:Counter() for k in REPS}
        for x in rr:
            host=x["page_host"];token=x["token"]
            f["HOST_EXACT"][host]+=1;f["HOST_LENGTH"][str(len(host))]+=1
            f["HOST_CHAR2"].update(ngrams(host,2));f["HOST_CHAR3"].update(ngrams(host,3));f["RAW_CHAR3"].update(ngrams(token,3))
        features[page]=f
    scores=[];pools={}
    for c in cand:
        s=c["source_page"];t=c["target_page"]
        if s not in features or t not in features:continue
        key=meta[t][:3];pool=sorted(p for p,m in meta.items() if m[:3]==key and m[3]!=meta[s][3]);assert t in pool
        vals={rep:[wj(features[s][rep],features[p][rep]) for p in pool] for rep in REPS};row={k:c[k] for k in ("candidate_id","evidence_priority_rank","evidence_panel","source_page","target_page","relation_class","component","assertion_strength","cross_source_corroborated","local_query_locus")};row["candidate_pool_pages"]=len(pool)
        for rep in REPS:
            obs=wj(features[s][rep],features[t][rep]);mu,sd=ms(vals[rep]);row[f"{rep.lower()}_similarity"]=f"{obs:.9f}";row[f"{rep.lower()}_rank"]=1+sum(v>obs+1e-12 for v in vals[rep]);row[f"{rep.lower()}_tail"]=f"{sum(v>=obs-1e-12 for v in vals[rep])/len(vals[rep]):.9f}";row[f"{rep.lower()}_z"]=f"{(obs-mu)/sd:.9f}"
        scores.append(row);pools[c["candidate_id"]]=(pool,vals)
    assert len(scores)==38
    subsets=[("ALL",lambda x:True),("CROSS_SOURCE",lambda x:x["cross_source_corroborated"]=="1"),("ASSERTED_SAME_STRONG",lambda x:x["assertion_strength"] in {"ASSERTED_SAME","STRONG"}),("INTERNAL_HERBAL",lambda x:x["evidence_panel"]=="INTERNAL_HERBAL"),("HERBAL_TO_PHARMA",lambda x:x["evidence_panel"]=="HERBAL_TO_PHARMA")]
    summary=[]
    for name,fn in subsets:
        rr=[x for x in scores if fn(x)];row={"subset":name,"pairs":len(rr)}
        for rep in REPS:
            z=[float(x[f"{rep.lower()}_z"]) for x in rr];row[f"{rep.lower()}_mean_z"]=f"{sum(z)/len(z):.9f}";row[f"{rep.lower()}_positive_pairs"]=sum(v>0 for v in z);row[f"{rep.lower()}_top_decile_pairs"]=sum(float(x[f"{rep.lower()}_tail"])<=.1 for x in rr)
        summary.append(row)
    observed={rep:float(summary[0][f"{rep.lower()}_mean_z"]) for rep in REPS}
    rng=random.Random(d["seed"]);world_vectors=[]
    for _ in range(d["worlds"]):
        sums=Counter()
        for row in scores:
            pool,vals=pools[row["candidate_id"]];j=rng.randrange(len(pool))
            for rep in REPS:
                mu,sd=ms(vals[rep]);sums[rep]+=(vals[rep][j]-mu)/sd
        world_vectors.append({rep:sums[rep]/len(scores) for rep in REPS})
    null=[]
    for rep in REPS:
        local=(1+sum(w[rep]>=observed[rep]-1e-12 for w in world_vectors))/(len(world_vectors)+1)
        maxp=(1+sum(max(w.values())>=observed[rep]-1e-12 for w in world_vectors))/(len(world_vectors)+1)
        null.append({"representation":rep,"observed_mean_z":f"{observed[rep]:.9f}","worlds":len(world_vectors),"local_p":f"{local:.9f}","max5_p":f"{maxp:.9f}","seed":d["seed"]})
    # Pair- and folio-deletion diagnostics.
    deletion=[]
    for rep in REPS:
        for x in scores:
            rr=[y for y in scores if y is not x];deletion.append({"representation":rep,"deletion_type":"PAIR","deleted_id":x["candidate_id"],"remaining_pairs":len(rr),"mean_z":f"{sum(float(y[f'{rep.lower()}_z']) for y in rr)/len(rr):.9f}"})
        folios=sorted({c["source_physical_folio"] for c in cand}|{c["target_physical_folio"] for c in cand})
        cmap={c["candidate_id"]:c for c in cand}
        for folio in folios:
            rr=[y for y in scores if cmap[y["candidate_id"]]["source_physical_folio"]!=folio and cmap[y["candidate_id"]]["target_physical_folio"]!=folio]
            if rr:deletion.append({"representation":rep,"deletion_type":"PHYSICAL_FOLIO","deleted_id":folio,"remaining_pairs":len(rr),"mean_z":f"{sum(float(y[f'{rep.lower()}_z']) for y in rr)/len(rr):.9f}"})
    # Five local host-char3 queries.
    q={x["label_locus"]:x for x in read("gdt152_relation_queries.tsv") if x["edition"]=="ZL3b"}
    local=[]
    for c in cand:
        locus=c["local_query_locus"]
        if locus=="NONE" or locus not in q or c["source_page"] not in features:continue
        query=Counter(ngrams(q[locus]["page_host"],3));s=c["source_page"];key=meta[s][:3];pool=sorted(p for p,m in meta.items() if m[:3]==key and m[3]!=c["target_physical_folio"]);vals=[wj(query,features[p]["HOST_CHAR3"]) for p in pool];obs=wj(query,features[s]["HOST_CHAR3"])
        local.append({"candidate_id":c["candidate_id"],"label_locus":locus,"paired_page":s,"query_page_host":q[locus]["page_host"],"candidate_pool_pages":len(pool),"similarity":f"{obs:.9f}","rank":1+sum(v>obs+1e-12 for v in vals),"tail":f"{sum(v>=obs-1e-12 for v in vals)/len(vals):.9f}"})
    write("gdt178_pair_scores.tsv",scores);write("gdt178_summary.tsv",summary);write("gdt178_null.tsv",null);write("gdt178_deletions.tsv",deletion);write("gdt178_local_queries.tsv",local)
    best=min(null,key=lambda x:float(x["max5_p"]));host3=next(x for x in null if x["representation"]=="HOST_CHAR3")
    status="FULL_ATLAS_HOST_CHAR3_PROFILE_SUPPORTED" if float(host3["max5_p"])<=.05 and observed["HOST_CHAR3"]>0 else "FULL_ATLAS_DISTRIBUTIONAL_HOST_PROFILE_NOT_SUPPORTED"
    result={"experiment":"GDT178_REFERENT_DISTRIBUTIONAL_HOST","status":status,"scored_pairs":len(scores),"best_representation_by_max5":best["representation"],"summary":{x["representation"]:{"mean_z":float(x["observed_mean_z"]),"local_p":float(x["local_p"]),"max5_p":float(x["max5_p"])} for x in null},"local_queries":len(local),"local_top_decile":sum(float(x["tail"])<=.1 for x in local),"f84r_accessed":False,"inputs":{p:sha(p) for p in ("gdt178_design.json","gdt169_external_referent_candidates.tsv","gdt062_right_family_inventory.tsv","gdt152_relation_queries.tsv")},"implementation":{"run_gdt178_referent_distributional_host.py":sha("run_gdt178_referent_distributional_host.py")},"outputs":{p:sha(p) for p in ("gdt178_pair_scores.tsv","gdt178_summary.tsv","gdt178_null.tsv","gdt178_deletions.tsv","gdt178_local_queries.tsv")},"claim_ceiling":"anonymous page-profile similarity only; no plant identity word meaning language plaintext or translation"}
    payload=json.dumps(result,sort_keys=True,separators=(",",":")).encode();result["content_hash"]=hashlib.sha256(payload).hexdigest();Path("gdt178_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
