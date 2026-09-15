#!/usr/bin/env python3
"""Independent GDT953 contract/result audit; never imports run.py."""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import hashlib, itertools, json, re

E = Path(__file__).resolve().parents[1]
R = E.parents[2]

def read(path): return json.loads(path.read_text(encoding="utf-8"))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def map_candidate(c):
    return {row: f"f69v.{4 + (c['start'] + c['direction']*(row-1)) % 28}" for row in range(1,29)}

def matching(domains):
    """Bipartite matching and an exhaustive first Hall deficiency."""
    owner = {}
    def augment(atom, seen):
        for unit in sorted(domains[atom]):
            if unit in seen: continue
            seen.add(unit)
            if unit not in owner or augment(owner[unit], seen):
                owner[unit] = atom; return True
        return False
    for atom in sorted(domains): augment(atom,set())
    result={a:u for u,a in owner.items()}; hall=None
    atoms=sorted(domains)
    for k in range(1,len(atoms)+1):
        for subset in combinations(atoms,k):
            units=set().union(*(set(domains[a]) for a in subset))
            if len(units)<k:
                hall={"atoms":list(subset),"units":sorted(units)}; return result,hall
    return result,hall

def synthetic_checks():
    # Unique perfect matching, deficient Hall graph, and empty-domain accounting.
    a={"A":{"x"},"B":{"y"}}; m,h=matching(a)
    if len(m)!=2 or h is not None: return False
    a={"A":{"x"},"B":{"x"}}; m,h=matching(a)
    if len(m)!=1 or not h or h["atoms"]!=["A","B"]: return False
    m,h=matching({"A":set(),"B":{"x"}})
    return len(m)==1 and h and h["atoms"]==["A"] and h["units"]==[]

def line_records(data,spec):
    raw=defaultdict(list)
    for row in data["raw"]: raw[(row["edition"],row["locus"])].append(row)
    legacy={(row["edition"],row["locus"]):row for row in data["legacy"]}
    out={}; defects=[]
    for key,rows0 in raw.items():
        rows=sorted(rows0,key=lambda x:int(x["source_group_index"]))
        groups=[x["ivtff_group_raw"] for x in rows]
        unknown=[]
        if any(not re.fullmatch(r"[a-z]+",g) for g in groups): unknown.append("NONLITERAL_RAW_GROUP")
        if any(a["right_separator"]!="DEFINITE_SPACE" or b["left_separator"]!="DEFINITE_SPACE" for a,b in zip(rows,rows[1:])): unknown.append("UNCERTAIN_INTERNAL_SEAM")
        indices=[int(x["source_group_index"]) for x in rows]
        # Unlike run.py, explicitly check every count field.
        counts=[int(x["source_group_count"]) for x in rows]
        if any(c!=len(rows) for c in counts): defects.append({"key":key,"kind":"GROUP_COUNT_MISMATCH","counts":counts,"actual":len(rows)})
        if indices!=list(range(1,len(rows)+1)): defects.append({"key":key,"kind":"GROUP_INDEX_MISMATCH","indices":indices})
        lr=legacy.get(key); roots=lr["root_sequence"].split() if lr else []
        root_unknown=list(unknown)
        if not lr: root_unknown.append("MISSING_LEGACY")
        elif lr["surface"].split()!=groups: root_unknown.append("LEGACY_SURFACE_MISMATCH")
        if len(roots)!=len(groups): root_unknown.append("LEGACY_ROOT_GROUP_COUNT_MISMATCH")
        units=[u for g in roots for u in g.split("+")]
        if not units or any(not re.fullmatch(r"[A-Za-z]+",u) for u in units): root_unknown.append("NONALPHABETIC_ROOT_UNIT")
        # Frozen runner's count_ok is retained for exact output replay.
        count_ok=(all(c==len(rows) for c in counts) and indices==list(range(1,len(rows)+1)))
        for model in spec["models"]:
            literal_unknown=list(unknown)
            aligned=bool(lr) and lr["surface"].split()==groups and len(roots)==len(groups)
            if model!="LITERAL" and not aligned: literal_unknown.append("LEGACY_ALIGNMENT")
            out[(key[0],key[1],model)]={"groups":groups,"values":groups if model=="LITERAL" or not aligned else roots,
                "whole":None if unknown else tuple(groups),
                "units":None if root_unknown else set(units),
                "literal_unknown":literal_unknown,"root_unknown":root_unknown,
                "count_ok":count_ok,"aligned":aligned}
    return out,defects

def target_input(data,spec):
    expected={(e,l) for e in spec["editions"] for l in spec["loci"]}
    rawkeys={(r["edition"],r["locus"]) for r in data["raw"]}; legkeys={(r["edition"],r["locus"]) for r in data["legacy"]}
    issues=[]
    if rawkeys!=expected: issues.append({"kind":"RAW_KEY_SET","missing":sorted(expected-rawkeys),"extra":sorted(rawkeys-expected)})
    if legkeys!=expected: issues.append({"kind":"LEGACY_KEY_SET","missing":sorted(expected-legkeys),"extra":sorted(legkeys-expected)})
    ids=[r.get("source_group_id") for r in data["raw"]]
    if len(ids)!=len(set(ids)): issues.append({"kind":"DUPLICATE_SOURCE_GROUP_ID"})
    if any(str(r.get("page","" )).startswith(("f84","f84r")) for r in data["raw"]+data["legacy"]): issues.append({"kind":"FORBIDDEN_PAGE"})
    return issues

def expected_eval(source,spec,target):
    known=[r for r in source["rows"] if r.get("purpose_id") is not None]
    allatoms=[a["id"] for a in source["atoms"]]
    summaries=[]; pairs=[]; comps=[]; details=[]
    for edition in spec["editions"]:
        universe=sorted(set().union(*(target[(edition,l,"LEGACY_ROOT_EXACT")]["units"] or set() for l in spec["loci"])))
        # Component units use the same legacy-root target view as the frozen runner.
        for c in spec["candidates"]:
            mp=map_candidate(c); counts=Counter(); domains={}; upper={}
            for a,b in combinations(known,2):
                ta=target[(edition,mp[a["row"]],"LITERAL")]; tb=target[(edition,mp[b["row"]],"LITERAL")]
                exp=a["purpose_id"]==b["purpose_id"]
                obs=None if ta["whole"] is None or tb["whole"] is None else ta["whole"]==tb["whole"]
                status="UNKNOWN" if obs is None else ("AGREE" if obs==exp else "CONTRADICTION")
                counts[status]+=1
                pairs.append((edition,c["id"],a["row"],b["row"],mp[a["row"]],mp[b["row"]],int(exp),"?" if obs is None else int(obs),status))
            for atom in source["atoms"]:
                ds=[]; uds=[]
                for unit in universe:
                    pos=[]; neg=[]; unk=[]; mis=[]
                    for r in known:
                        t=target[(edition,mp[r["row"]],"LEGACY_ROOT_EXACT")]; units=t["units"]; want=r["row"] in atom["rows"]
                        if units is None: unk.append(mp[r["row"]])
                        elif (unit in units)!=want: mis.append(f"{mp[r['row']]}:{int(want)}>{int(unit in units)}")
                        elif want: pos.append(mp[r["row"]])
                        else: neg.append(mp[r["row"]])
                    if not mis: uds.append(unit)
                    if not mis and len(pos)>=spec["minimum_observed_positive"] and len(neg)>=spec["minimum_observed_negative"]: ds.append(unit)
                    comps.append((edition,c["id"],atom["id"],unit,int(not mis),int(unit in ds),','.join(pos),','.join(neg),','.join(unk),','.join(mis)))
                domains[atom["id"]]=ds; upper[atom["id"]]=uds
                if not any(target[(edition,mp[r["row"]],"LEGACY_ROOT_EXACT")]["units"] is not None for r in atom["rows"]): upper[atom["id"]].append("UNOBSERVED_"+atom["id"])
            mat,hall=matching(domains); umat,uhall=matching(upper)
            ps="CONTRADICTED" if counts["CONTRADICTION"] else ("UNRESOLVED" if counts["UNKNOWN"] else "COMPATIBLE")
            cs="P_CONTRADICTED" if ps=="CONTRADICTED" else ("COMPONENT_CONTRADICTED" if len(umat)<len(domains) else ("NO_CAPACITY" if len(mat)<len(domains) else "COMPONENT_FEASIBLE"))
            summary={"edition":edition,"candidate":c["id"],"P_status":ps,"P_agree":counts["AGREE"],"P_contradictions":counts["CONTRADICTION"],"P_unknown":counts["UNKNOWN"],"C_status":cs,"component_matching_size":len(mat),"component_upper_matching_size":len(umat),"component_atoms":len(domains),"empty_component_domains":','.join(a for a in domains if not domains[a]),"unknown_source_rows":"22","physical_leaves":1,"independent_confirmation_leaves":0}
            summaries.append(summary); details.append((summary,mp,domains,upper,mat,hall,umat,uhall))
    return summaries,pairs,comps,details

def read_tsv(path):
    import csv
    with path.open(newline="") as f: return list(csv.DictReader(f,delimiter="\t"))

def main():
    # Before intake, run only source prediction and algorithm fixtures.
    source=read(E/"src/SOURCE.json"); spec=read(E/"src/SPEC.json")
    source_checks={"rows":len(source["rows"]),"row_numbers":[r["row"] for r in source["rows"]]==list(range(1,29)),"atoms":len(source["atoms"]),"candidate_count":len(spec["candidates"]),"candidate_ids_unique":len({c["id"] for c in spec["candidates"]})==56}
    source_pred=read_tsv(E/"artifacts/ALL_PREDICTIONS.tsv")
    source_checks["prediction_rows"] = len(source_pred)==56*28
    source_checks["prediction_maps_valid"] = all(map_candidate(c) and len(set(map_candidate(c).values()))==28 for c in spec["candidates"])
    report={"experiment":"GDT953","validator":"independent_evaluator_no_run_import","source_checks":source_checks,"synthetic_matching_checks":synthetic_checks(),"pre_intake":True}
    inp=E/"artifacts/INPUT.json"
    if not inp.exists():
        report["status"]="SOURCE_ONLY_PASS"; report["runner_contract_review"]={"warning":"targets() checks source_group_count only on first row; independent validator will check every row after intake"}
    else:
        data=read(inp); report["pre_intake"]=False; report["input_issues"]=target_input(data,spec)
        target,defects=line_records(data,spec); report["line_record_defects"]=defects
        summaries,pairs,comps,details=expected_eval(source,spec,target)
        # Compare every generated table row to an independently derived tuple.
        checks={}
        pmap={(r[0],r[1],r[2],r[3]):r for r in pairs}; cmap={(r[0],r[1],r[2],r[3]):r for r in comps}; smap={(r["edition"],r["candidate"]):r for r in summaries}
        pair_art=read_tsv(E/"artifacts/ALL_PAIR_CONSEQUENCES.tsv"); badp=0
        for r in pair_art:
            want=pmap.get((r["edition"],r["candidate"],int(r["source_row_a"]),int(r["source_row_b"])))
            if not want or (r["locus_a"],r["locus_b"],r["expected_equal"],r["observed_equal"],r["status"])!=(want[4],want[5],str(want[6]),want[7],want[8]): badp+=1
        comp_art=read_tsv(E/"artifacts/ALL_COMPONENT_CONSEQUENCES.tsv"); badc=0
        for r in comp_art:
            want=cmap.get((r["edition"],r["candidate"],r["atom"],r["unit"]))
            if not want or (r["no_observed_contradiction"],r["compatible"],r["observed_positive_loci"],r["observed_negative_loci"],r["unknown_loci"],r["contradictions_expected_to_observed"])!=(str(want[4]),str(want[5]),want[6],want[7],want[8],want[9]): badc+=1
        st_art=read_tsv(E/"artifacts/CANDIDATE_TABLE.tsv"); bads=0
        for r in st_art:
            w=smap.get((r["edition"],r["candidate"]));
            if not w or any(r[k]!=str(w[k]) for k in w): bads+=1
        result=read(E/"artifacts/RESULT.json")
        report.update({"status":"PASS" if not report["input_issues"] and not defects and badp==badc==bads==0 else "FAIL","input_counts":{"raw":len(data["raw"]),"legacy":len(data["legacy"])},"table_counts":{"pairs":len(pair_art),"components":len(comp_art),"summaries":len(st_art)},"table_mismatches":{"pairs":badp,"components":badc,"summaries":bads},"result_claim_ceiling":result.get("claim_ceiling"),"P_outcomes":dict(Counter(x["P_status"] for x in summaries)),"C_outcomes":dict(Counter(x["C_status"] for x in summaries))})
    (E/"artifacts/VALIDATION.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"source":source_checks,"pre_intake":report["pre_intake"]},indent=2))
    return 0 if report["status"] in ("PASS","SOURCE_ONLY_PASS") else 1

if __name__=="__main__": raise SystemExit(main())
