#!/usr/bin/env python3
"""Independent audit of the locked GDT952 run and enum correction.

The validator intentionally imports neither run.py nor count.py.  The frozen
run's separator mistake is retained and reported as an invalid test; the
post-exposure corrected directory is audited separately.
"""
from collections import defaultdict
from itertools import permutations
from pathlib import Path
import hashlib, json, random, re

EXP = Path(__file__).resolve().parents[1]
ART = EXP / "artifacts"
NAMES = ["Septentrio","Aquilo","Vulturnus","Subsolanus","Eurus","Euroauster",
         "Auster","Euronothus","Affricus","Zephirus","Chorus","Circius"]
NAME_EDGES = [("Vulturnus","Subsolanus"),("Eurus","Subsolanus"),
              ("Euroauster","Auster"),("Euroauster","Eurus"),
              ("Euronothus","Auster"),("Affricus","Zephirus"),
              ("Chorus","Zephirus"),("Circius","Septentrio")]
EDGES = [(NAMES.index(a),NAMES.index(b)) for a,b in NAME_EDGES]

def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def components(n, edges):
    adj=[[] for _ in range(n)]
    for a,b in edges: adj[a].append(b); adj[b].append(a)
    seen=set(); out=[]
    for start in range(n):
        if start in seen: continue
        todo=[start]; seen.add(start); got=[]
        while todo:
            v=todo.pop(); got.append(v)
            for w in adj[v]:
                if w not in seen: seen.add(w); todo.append(w)
        out.append(sorted(got))
    return sorted(out,key=lambda c:(-len(c),c))

def exact_count(n, edges, matrix):
    """Independent component embedding/exact-cover count and marginals."""
    comps=sorted(components(n,edges),key=lambda c:(-len(c),c))
    if all(matrix[i][j] for i in range(n) for j in range(n) if i!=j):
        f=1
        for k in range(2,n+1): f*=k
        return f, [[f//n]*n for _ in range(n)], comps, None, None
    inc=[set() for _ in range(n)]
    for a,b in edges: inc[a].add(b); inc[b].add(a)
    all_emb=[]; mask_counts=[]; emb_counts=[]
    for comp in comps:
        order=sorted(comp,key=lambda v:(-len(inc[v]),v)); rows=[]
        def visit(k, mapping, used):
            if k==len(order): rows.append(tuple(mapping[i] for i in comp)); return
            v=order[k]
            for pos in range(n):
                if used&(1<<pos): continue
                good=True
                for a,b in edges:
                    if a==v and b in mapping and not matrix[pos][mapping[b]]: good=False
                    if b==v and a in mapping and not matrix[mapping[a]][pos]: good=False
                if good:
                    mapping[v]=pos; visit(k+1,mapping,used|(1<<pos)); del mapping[v]
        visit(0,{},0)
        all_emb.append((comp,rows)); emb_counts.append(len(rows))
        mask_counts.append(len({sum(1<<p for p in r) for r in rows}))
    dp={0:(1,[[0]*n for _ in range(n)])}
    for comp,rows in all_emb:
        bymask=defaultdict(list)
        for row in rows: bymask[sum(1<<p for p in row)].append(row)
        nxt={}
        for used,(count,marg) in dp.items():
            for mask,choices in bymask.items():
                if used&mask: continue
                nm=[[x*len(choices) for x in r] for r in marg]
                for row in choices:
                    for i,pos in zip(comp,row): nm[i][pos]+=count
                key=used|mask
                if key not in nxt: nxt[key]=(0,[[0]*n for _ in range(n)])
                nxt[key]=(nxt[key][0]+count*len(choices),nxt[key][1])
                for i in range(n):
                    for j in range(n): nxt[key][1][i][j]+=nm[i][j]
        dp=nxt
    full=(1<<n)-1
    if full not in dp: return 0,[[0]*n for _ in range(n)],comps,mask_counts,emb_counts
    return dp[full][0],dp[full][1],comps,mask_counts,emb_counts

def brute_count(n,edges,matrix):
    return sum(all(matrix[p[a]][p[b]] for a,b in edges)
               for p in permutations(range(n)))

def fixture_checks():
    # Every directed n=3 adjacency graph, plus deterministic n=4..7 checks.
    e=[(0,1),(1,2)]
    for bits in range(64):
        m=[[True]*3 for _ in range(3)]; k=0
        for i in range(3):
            for j in range(3):
                if i!=j: m[i][j]=bool(bits&(1<<k)); k+=1
        if exact_count(3,e,m)[0]!=brute_count(3,e,m): return False
    rng=random.Random(952)
    for n in range(4,8):
        for _ in range(4):
            m=[[i==j or rng.random()<.55 for j in range(n)] for i in range(n)]
            if exact_count(n,e,m)[0]!=brute_count(n,e,m): return False
    return True

def records(data,spec,separator):
    raw=defaultdict(list)
    for r in data["raw"]: raw[(r["edition"],r["locus"])].append(r)
    legacy={(r["edition"],r["locus"]):r for r in data["legacy"]}; out={}
    for key,rows0 in raw.items():
        rows=sorted(rows0,key=lambda r:int(r["source_group_index"]))
        groups=[r["ivtff_group_raw"] for r in rows]
        clean=[bool(re.fullmatch(r"[a-z]+",g)) for g in groups]
        seams=all(a["right_separator"]==b["left_separator"]==separator for a,b in zip(rows,rows[1:]))
        indexes=[int(r["source_group_index"]) for r in rows]
        count_ok=all(int(r["source_group_count"])==len(rows) for r in rows) and indexes==list(range(1,len(rows)+1))
        lr=legacy.get(key); roots=lr["root_sequence"].split() if lr else []
        aligned=bool(lr) and lr["surface"].split()==groups and len(roots)==len(groups)
        for model in spec["models"]:
            vals=groups if model=="LITERAL" else (roots if aligned else groups)
            valid=[c and count_ok and seams and (model=="LITERAL" or aligned) for c in clean]
            out[(key[0],key[1],model)]={"values":vals,"valid":valid,"raw_groups":groups,
                "uncertain_seams":not seams or (model!="LITERAL" and not aligned),
                "root_aligned":aligned,"count_ok":count_ok}
    return out

def compare(title,body):
    if not all(title["valid"]): return "UNKNOWN",[]
    n=len(title["values"]); hits=[]; possible=False
    for j in range(len(body["values"])-n+1):
        vals=body["values"][j:j+n]; known=body["valid"][j:j+n]
        if vals==title["values"] and all(known): hits.append(j+1)
        if all(not k or a==b for a,b,k in zip(title["values"],vals,known)): possible=True
    if hits: return "PRESENT",hits
    if possible or body["uncertain_seams"] or not body["count_ok"]: return "UNKNOWN",[]
    return "ABSENT",[]

def reproduce(data,spec,separator):
    rec=records(data,spec,separator); statuses={}; defs={}
    for edition in spec["editions"]:
        for model in spec["models"]:
            titles=[rec[(edition,s["title"],model)] for s in spec["sectors"]]
            bodies=[]
            for s in spec["sectors"]:
                parts=[rec[(edition,l,model)] for l in s["body"]]
                bodies.append({"values":sum((p["values"] for p in parts),[]),
                               "valid":sum((p["valid"] for p in parts),[]),
                               "uncertain_seams":any(p["uncertain_seams"] for p in parts),
                               "count_ok":all(p["count_ok"] for p in parts)})
            statuses[(edition,model)]=[[compare(t,b)[0] for t in titles] for b in bodies]
            defs[(edition,model)]=sum(all(t["valid"]) for t in titles)
    return statuses,defs

def contract(data,spec):
    by=defaultdict(list)
    for r in data["raw"]: by[(r["edition"],r["locus"])].append(r)
    zero=[]; bad=[]; sep=defaultdict(int)
    for key,rows in by.items():
        ix=sorted(int(r["source_group_index"]) for r in rows)
        if ix==list(range(len(rows))): zero.append("%s|%s"%key)
        if ix!=list(range(1,len(rows)+1)): bad.append("%s|%s"%key)
        for r in rows: sep[r["right_separator"]]+=1
    return {"raw_rows":len(data["raw"]),"raw_loci":len(by),"legacy_rows":len(data["legacy"]),
            "raw_zero_based_loci":zero,"raw_non_one_based_loci":bad,
            "raw_separator_values":dict(sorted(sep.items())),"selected_loci":len(spec["loci"]),
            "source_page_values":sorted({r["page"] for r in data["raw"]}),
            "forbidden_page_rows":sum(str(r.get("page","")).startswith(("f84","f84r")) for r in data["raw"]+data["legacy"])}

def graph_audit(gjson,status):
    expected=[]
    for edition in SPEC["editions"]:
        for model in SPEC["models"]:
            matrix=status[(edition,model)]
            for bound in ("lower","upper"):
                adj=[[s=="PRESENT" if bound=="lower" else s!="ABSENT" for s in row] for row in matrix]
                expected.append((edition,model,bound,adj,exact_count(12,EDGES,adj)))
    rows=[]
    for got,want in zip(gjson["graphs"],expected):
        edition,model,bound,adj,(count,marg,comps,masks,emb)=want
        ok=(got.get("edition"),got.get("model"),got.get("bound"))==(edition,model,bound)
        ok=ok and got.get("adjacency")==adj and got.get("count")==count and got.get("marginals")==marg and got.get("components")==comps
        if "component_mask_counts" in got: ok=ok and got["component_mask_counts"]==masks and got["component_embedding_counts"]==emb
        rows.append({"edition":edition,"model":model,"bound":bound,"ok":ok,"independent_count":count,"reported_count":got.get("count")})
    return len(gjson["graphs"])==len(expected) and all(r["ok"] for r in rows),rows

def summary_audit(result,status,defs):
    rows=[]; pairs=[(e,m) for e in SPEC["editions"] for m in SPEC["models"]]
    for got,(edition,model) in zip(result["results"],pairs):
        mat=status[(edition,model)]; lower=[[s=="PRESENT" for s in r] for r in mat]; upper=[[s!="ABSENT" for s in r] for r in mat]
        want={"lower_count":exact_count(12,EDGES,lower)[0],"upper_count":exact_count(12,EDGES,upper)[0],
              "present_offdiagonal":sum(s=="PRESENT" for i,r in enumerate(mat) for j,s in enumerate(r) if i!=j),
              "unknown_offdiagonal":sum(s=="UNKNOWN" for i,r in enumerate(mat) for j,s in enumerate(r) if i!=j),"definite_titles":defs[(edition,model)]}
        rows.append({"edition":edition,"model":model,"ok":all(got.get(k)==v for k,v in want.items()),"expected":want,"reported":{k:got.get(k) for k in want}})
    return rows

def main():
    global SPEC
    lock=load(EXP/"PREREG_LOCK.json"); repo=EXP.parents[2]; lock_checks={}
    for group,base in (("files",EXP),("source_files",repo)):
        for rel,expected in lock[group].items():
            actual=sha(base/rel); lock_checks[group+":"+rel]={"expected":expected,"actual":actual,"ok":actual==expected}
    SPEC=load(EXP/"src/SPEC.json"); source=load(EXP/"src/SOURCE.json"); data=load(ART/"INPUT.json")
    original_status,original_defs=reproduce(data,SPEC,"."); corrected_status,corrected_defs=reproduce(data,SPEC,"DEFINITE_SPACE")
    og=load(ART/"GRAPHS.json"); cg=load(ART/"corrected/GRAPHS.json"); orr=load(ART/"RESULT.json"); crr=load(ART/"corrected/RESULT.json")
    go,grows=graph_audit(og,original_status); gc,cgrows=graph_audit(cg,corrected_status)
    osum=summary_audit(orr,original_status,original_defs); csum=summary_audit(crr,corrected_status,corrected_defs)
    lock_ok=all(x["ok"] for x in lock_checks.values()); fixtures=fixture_checks()
    original_reproduced=go and all(x["ok"] for x in osum); corrected_reproduced=gc and all(x["ok"] for x in csum)
    report={"experiment":"GDT952","validator":"independent_reconstruction_no_runner_or_count_import",
      "lock":{"all_hashes_match":lock_ok,"checks":lock_checks},
      "source_graph":{"names_and_edges_match_SOURCE":source["names"]==NAMES and [tuple(x) for x in source["mandatory_edges"]]==NAME_EDGES,
                       "edges_match_graphs":og.get("source_edges")==[[a,b] for a,b in EDGES] and cg.get("source_edges")==[[a,b] for a,b in EDGES],
                       "components":components(12,EDGES),"component_sizes":[len(x) for x in components(12,EDGES)],"expected_component_sizes":[6,3,2,1]},
      "solver_fixtures":{"all_64_n3_and_random_n4_to_n7":fixtures},"input_contract":contract(data,SPEC),
      "original_locked_run":{"graph_reproduction":go,"summary_reproduction":original_reproduced,"graph_checks":grows,"summary_checks":osum,
        "interpretation":"INVALID_TEST: frozen SPEC/run compares '.' but INPUT uses DEFINITE_SPACE; unresolved bounds are not a manuscript finding."},
      "corrected_post_exposure_diagnostic":{"graph_reproduction":gc,"summary_reproduction":corrected_reproduced,"graph_checks":cgrows,"summary_checks":csum,
        "interpretation":"Post-exposure schema correction; compatibility counts are uncertainty bounds only, with no significance or meaning claim."},
      "claim_ceiling":{"independent_physical_leaves":0,"additional_confirmation_capacity":0,"meaning_confirmed":0,"significance_test":False,
                       "observed_offdiagonal_matches":{"original":0,"corrected":0}},
      "overall":{"lock_ok":lock_ok,"solver_fixtures_ok":fixtures,"original_reproduced":original_reproduced,"corrected_reproduced":corrected_reproduced,
                  "original_interpretation_valid":False,"validator_status":"PASS" if lock_ok and fixtures and corrected_reproduced else "FAIL"}}
    (ART/"VALIDATION.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["overall"]["validator_status"],"input_contract":report["input_contract"],"corrected":crr["results"]},indent=2))
    return 0 if report["overall"]["validator_status"]=="PASS" else 1

if __name__=="__main__": raise SystemExit(main())
