#!/usr/bin/env python3
"""Run the frozen GDT177 source-native tests of the GDT176 role-like schema."""
from __future__ import annotations
import csv, hashlib, json, math, random
from collections import Counter, defaultdict
from pathlib import Path

EDITIONS = ("ZL3b", "IT2a", "RF1b")
SUPPORTED = ("INSTRUCTION_CLAUSE_LIKE", "SHORT_ARGUMENT_LIKE", "RECORD_CLOSER_LIKE")

def read(path):
    with Path(path).open(encoding="utf-8", newline="") as h: return list(csv.DictReader(h,delimiter="\t"))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def bucket(n): return str(n) if n <= 3 else "4+"
def depth_bucket(n): return str(n) if n <= 2 else "3+"
def mean(x): return sum(x)/len(x) if x else 0.0
def write(path, rows):
    with Path(path).open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,list(rows[0]),delimiter="\t",lineterminator="\n"); w.writeheader(); w.writerows(rows)

def build_rows(edition, fields, projections):
    pf={r["field_id"]:r for r in projections if r["edition"]==edition}
    ff=[r for r in fields if r["edition"]==edition]
    assert all(not r["page"].startswith("f84") and not r["locus"].startswith("f84") for r in ff)
    by_record=defaultdict(list)
    for r in ff: by_record[(r["page"],r["star_ordinal"])].append(r)
    final_ids=set()
    for rr in by_record.values():
        rr.sort(key=lambda r:(int(r["line_depth"]),int(r["field_index"])))
        final_ids.add(rr[-1]["field_id"])
    host_folios=defaultdict(set)
    for r in ff:
        host=r["page_hosts"].split("|")[0]
        host_folios[host].add(r["physical_folio"])
    out=[]
    for r in ff:
        p=pf[r["field_id"]]
        skeleton=json.loads(r["compiler_skeleton"])
        components=sum((cell[0]!="NONE")+(cell[1]!="NONE")+(cell[2]!="NONE")+int(cell[3])+int(cell[4])+int(cell[5]) for cell in skeleton)
        host=r["page_hosts"].split("|")[0]
        abstract=p["supported_abstract_role_like"]
        supported_probs=[float(p["p_operation"]),float(p["p_ingredient"])+float(p["p_tool"]),float(p["p_closer"])]
        total=sum(supported_probs); supported_probs=[x/total for x in supported_probs]
        out.append({
            "edition":edition,"field_id":r["field_id"],"page":r["page"],"physical_folio":r["physical_folio"],
            "star_ordinal":r["star_ordinal"],"record_scope":r["record_scope"],"line_depth":int(r["line_depth"]),
            "field_index":int(r["field_index"]),"field_group_count":int(r["field_group_count"]),
            "group_bucket":bucket(int(r["field_group_count"])),"depth_bucket":depth_bucket(int(r["line_depth"])),
            "is_record_final":int(r["field_id"] in final_ids),"abstract_role":abstract,
            "first_page_host":host,"host_other_folio_count":len(host_folios[host]-{r["physical_folio"]}),
            "host_recurrent_other_2plus":int(len(host_folios[host]-{r["physical_folio"]})>=2),
            "ends_dy":int(r["ends_dy"]),"ends_b3":int(r["ends_b3"]),
            "compiler_components":components,"compiler_density":components/max(1,int(r["field_group_count"])),
            "p_instruction":supported_probs[0],"p_short_argument":supported_probs[1],"p_closer":supported_probs[2],
        })
    return out

def risk(rows, label, outcome, a, b):
    aa=[r[outcome] for r in rows if r[label]==a]; bb=[r[outcome] for r in rows if r[label]==b]
    return mean(aa)-mean(bb),len(aa),len(bb),mean(aa),mean(bb)

def permute_labels(rows, label, strata, rng):
    vals=[r[label] for r in rows]
    groups=defaultdict(list)
    for i,r in enumerate(rows): groups[tuple(r[s] for s in strata)].append(i)
    for inds in groups.values():
        shuffled=[vals[i] for i in inds]; rng.shuffle(shuffled)
        for i,v in zip(inds,shuffled): vals[i]=v
    return vals

def main():
    design=json.loads(Path("gdt177_design.json").read_text())
    fields=read("gdt127_q20_field_inventory.tsv"); projections=read("gdt176_q20_role_like_projection.tsv")
    all_rows={e:build_rows(e,fields,projections) for e in EDITIONS}
    primary=all_rows["ZL3b"]
    t1=[r for r in primary if r["is_record_final"] and r["abstract_role"] in SUPPORTED]
    t23=[r for r in primary if r["abstract_role"] in ("INSTRUCTION_CLAUSE_LIKE","SHORT_ARGUMENT_LIKE")]
    obs1=risk(t1,"abstract_role","ends_b3","RECORD_CLOSER_LIKE","INSTRUCTION_CLAUSE_LIKE")[0] # preliminary; other combines I+S below
    close=[r for r in t1 if r["abstract_role"]=="RECORD_CLOSER_LIKE"]
    nonclose=[r for r in t1 if r["abstract_role"]!="RECORD_CLOSER_LIKE"]
    obs1=mean([r["ends_b3"] for r in close])-mean([r["ends_b3"] for r in nonclose])
    obs1dy=mean([r["ends_dy"] for r in close])-mean([r["ends_dy"] for r in nonclose])
    obs2=risk(t23,"abstract_role","host_recurrent_other_2plus","SHORT_ARGUMENT_LIKE","INSTRUCTION_CLAUSE_LIKE")[0]
    obs3=risk(t23,"abstract_role","compiler_density","INSTRUCTION_CLAUSE_LIKE","SHORT_ARGUMENT_LIKE")[0]

    rng=random.Random(design["permutation_seed"]); worlds=design["permutation_worlds"]
    null1=[]; null2=[]; null3=[]
    for _ in range(worlds):
        labels1=permute_labels(t1,"abstract_role",("physical_folio","group_bucket"),rng)
        c=[r["ends_b3"] for r,l in zip(t1,labels1) if l=="RECORD_CLOSER_LIKE"]
        n=[r["ends_b3"] for r,l in zip(t1,labels1) if l!="RECORD_CLOSER_LIKE"]
        null1.append(mean(c)-mean(n))
        labels=permute_labels(t23,"abstract_role",("physical_folio","record_scope","depth_bucket","group_bucket"),rng)
        short=[r for r,l in zip(t23,labels) if l=="SHORT_ARGUMENT_LIKE"]
        instruction=[r for r,l in zip(t23,labels) if l=="INSTRUCTION_CLAUSE_LIKE"]
        null2.append(mean([r["host_recurrent_other_2plus"] for r in short])-mean([r["host_recurrent_other_2plus"] for r in instruction]))
        null3.append(mean([r["compiler_density"] for r in instruction])-mean([r["compiler_density"] for r in short]))
    observed=(obs1,obs2,obs3); nulls=(null1,null2,null3)
    means=[mean(x) for x in nulls]
    sds=[math.sqrt(mean([(v-m)**2 for v in x])) or 1 for x,m in zip(nulls,means)]
    obs_z=[(o-m)/s for o,m,s in zip(observed,means,sds)]
    max_world=[max((nulls[j][i]-means[j])/sds[j] for j in range(3)) for i in range(worlds)]
    local_p=[(1+sum(v>=o for v in n))/(worlds+1) for o,n in zip(observed,nulls)]
    max_p=[(1+sum(v>=z for v in max_world))/(worlds+1) for z in obs_z]

    test_rows=[]
    names=("T1_FINAL_FIELD_B3","T2_CROSS_FOLIO_HOST_RECURRENCE","T3_COMPILER_STATE_DENSITY")
    for name,o,m,s,z,lp,mp in zip(names,observed,means,sds,obs_z,local_p,max_p):
        test_rows.append({"test_id":name,"edition":"ZL3b","effect":f"{o:.9f}","null_mean":f"{m:.9f}","null_sd":f"{s:.9f}","z":f"{z:.6f}","local_p":f"{lp:.9f}","max3_p":f"{mp:.9f}"})
    # Alternate-reading effect sensitivity, without treating readings as samples.
    for edition in EDITIONS[1:]:
        rr=all_rows[edition]
        final=[r for r in rr if r["is_record_final"] and r["abstract_role"] in SUPPORTED]
        c=[r for r in final if r["abstract_role"]=="RECORD_CLOSER_LIKE"]; n=[r for r in final if r["abstract_role"]!="RECORD_CLOSER_LIKE"]
        pair=[r for r in rr if r["abstract_role"] in ("INSTRUCTION_CLAUSE_LIKE","SHORT_ARGUMENT_LIKE")]
        effects=(mean([r["ends_b3"] for r in c])-mean([r["ends_b3"] for r in n]),
                 risk(pair,"abstract_role","host_recurrent_other_2plus","SHORT_ARGUMENT_LIKE","INSTRUCTION_CLAUSE_LIKE")[0],
                 risk(pair,"abstract_role","compiler_density","INSTRUCTION_CLAUSE_LIKE","SHORT_ARGUMENT_LIKE")[0])
        for name,effect in zip(names,effects): test_rows.append({"test_id":name,"edition":edition,"effect":f"{effect:.9f}","null_mean":"NOT_RUN","null_sd":"NOT_RUN","z":"NOT_RUN","local_p":"NOT_RUN","max3_p":"NOT_RUN"})
    test_rows.append({"test_id":"T1_FINAL_FIELD_DY_SECONDARY","edition":"ZL3b","effect":f"{obs1dy:.9f}","null_mean":"NOT_RUN","null_sd":"NOT_RUN","z":"NOT_RUN","local_p":"NOT_RUN","max3_p":"NOT_RUN"})

    # T4 held-folio exact-host update over frozen external probabilities.
    t4rows=[]; total_base=total_update=0.0; total_n=total_eligible=0; top_base=top_update=0
    for held in sorted({r["physical_folio"] for r in primary}):
        train=[r for r in primary if r["physical_folio"]!=held and r["abstract_role"] in SUPPORTED]
        test=[r for r in primary if r["physical_folio"]==held and r["abstract_role"] in SUPPORTED]
        counts=defaultdict(Counter)
        for r in train: counts[r["first_page_host"]][r["abstract_role"]]+=1
        bb=uu=0.0; eligible=0; tb=tu=0
        for r in test:
            truth=SUPPORTED.index(r["abstract_role"]); base=[r["p_instruction"],r["p_short_argument"],r["p_closer"]]
            hostc=counts.get(r["first_page_host"])
            if hostc:
                eligible+=1; n=sum(hostc.values()); hp=[(hostc[c]+1)/(n+3) for c in SUPPORTED]
                updated=[(base[i]+design["host_update_pseudocount"]*hp[i])/(1+design["host_update_pseudocount"]) for i in range(3)]
            else: updated=base
            bb-=math.log2(max(base[truth],1e-12)); uu-=math.log2(max(updated[truth],1e-12))
            tb+=max(range(3),key=lambda i:base[i])==truth; tu+=max(range(3),key=lambda i:updated[i])==truth
        gain=bb-uu
        t4rows.append({"held_folio":held,"n":len(test),"host_update_eligible":eligible,"baseline_bits":f"{bb:.9f}","updated_bits":f"{uu:.9f}","gain_bits":f"{gain:.9f}","baseline_top1":tb,"updated_top1":tu})
        total_base+=bb; total_update+=uu; total_n+=len(test); total_eligible+=eligible; top_base+=tb; top_update+=tu

    row_export=[]
    for e in EDITIONS:
        for r in all_rows[e]:
            row_export.append({k:(f"{v:.9f}" if isinstance(v,float) else v) for k,v in r.items()})
    null_rows=[]
    for name,values in zip(names,nulls):
        for i,v in enumerate(values): null_rows.append({"test_id":name,"world":i,"effect":f"{v:.9f}"})
    write("gdt177_field_inventory.tsv",row_export); write("gdt177_tests.tsv",test_rows); write("gdt177_null.tsv",null_rows); write("gdt177_host_update_folds.tsv",t4rows)

    result={
        "experiment":"GDT177_Q20_ROLE_SCHEMA_VALIDATION","status":"POSITION_LENGTH_ANALOGY_ONLY_NO_INDEPENDENT_Q20_ROLE_SUPPORT",
        "primary_fields":len(primary),"primary_supported_fields":sum(r["abstract_role"] in SUPPORTED for r in primary),
        "t1":{"final_fields":len(t1),"closer_like":len(close),"other":len(nonclose),"b3_effect":obs1,"dy_effect":obs1dy,"local_p":local_p[0],"max3_p":max_p[0]},
        "t2":{"fields":len(t23),"effect":obs2,"local_p":local_p[1],"max3_p":max_p[1]},
        "t3":{"fields":len(t23),"effect":obs3,"local_p":local_p[2],"max3_p":max_p[2]},
        "t4":{"n":total_n,"eligible":total_eligible,"coverage":total_eligible/total_n,"baseline_bits":total_base,"updated_bits":total_update,"gain_bits":total_base-total_update,"positive_folios":sum(float(r["gain_bits"])>0 for r in t4rows),"folio_count":len(t4rows),"baseline_top1":top_base,"updated_top1":top_update},
        "alternate_readings_are_sensitivities":True,"f84r_accessed":False,
        "inputs":{p:sha(p) for p in ("gdt177_design.json","gdt176_result.json","gdt176_q20_role_like_projection.tsv","gdt127_q20_field_inventory.tsv")},
        "implementation":{"run_gdt177_q20_role_schema_validation.py":sha("run_gdt177_q20_role_schema_validation.py")},
        "outputs":{p:sha(p) for p in ("gdt177_field_inventory.tsv","gdt177_tests.tsv","gdt177_null.tsv","gdt177_host_update_folds.tsv")},
        "claim_ceiling":"partial abstract record-schema support only; no ingredient tool operation word language plaintext or translation",
    }
    payload=json.dumps(result,sort_keys=True,separators=(",",":")).encode(); result["content_hash"]=hashlib.sha256(payload).hexdigest()
    Path("gdt177_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in ("status","t1","t2","t3","t4")},indent=2,sort_keys=True))

if __name__=="__main__": main()
