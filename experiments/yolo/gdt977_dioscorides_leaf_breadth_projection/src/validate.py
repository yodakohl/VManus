#!/usr/bin/env python3
"""Independent GDT977 certificate validator; never runs or overwrites run.py output."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, re
from pathlib import Path

HERE = Path(__file__).resolve(); EXP = HERE.parents[1]; ROOT = EXP.parents[2]
SPEC = EXP / "src/SPEC.json"
DOMAINS = ROOT / "experiments/yolo/gdt976_dioscorides_shared_referent_projection/artifacts/DOMAINS.json"
CANDIDATES = ROOT / "experiments/yolo/gdt976_dioscorides_shared_referent_projection/artifacts/CANDIDATES.json.gz"
SOURCE = ROOT / "experiments/yolo/gdt963_dioscorides_complete_content_code/src/SOURCE.json"
ART = EXP / "artifacts"
RECORDS = ("I.1", "I.2", "I.3", "IV.20")
SAT, UNSAT = "PARTIAL_FOUR_ATOM_WITNESS", "FOUR_ATOM_PROJECTION_CONTRADICTED"
UNKNOWN = {"UNKNOWN_CASE_CPU", "UNKNOWN_GLOBAL_WALL"}

def read_json(p): return json.loads(p.read_text(encoding="utf-8"))
def read_gz(p):
    with gzip.open(p, "rt", encoding="utf-8") as f: return json.load(f)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def starts(text, word): return [m.start() for m in re.finditer("(?="+re.escape(word)+")", text)] if word else []
def incomparable(a,b): return a != b and not a.startswith(b) and not b.startswith(a)
def atoms(record): return [a for t in record.get("tokens",[]) for a in t.get("atoms",[])]

def source_projection():
    if not SOURCE.exists() or not SPEC.exists(): return False,{"errors":["source_or_spec_missing"]}
    src,spec=read_json(SOURCE),read_json(SPEC); recs={r["id"]:r for r in src.get("records",[])}; errors=[]; out={}
    for rid,item in spec.get("projections",{}).items():
        if rid not in recs: errors.append({"record":rid,"error":"missing_source_record"}); continue
        flat=atoms(recs[rid]); pos=[i for i,x in enumerate(flat) if x in {"IRIS","XIPHION","LEAF","BROAD"}]
        events=[flat[i] for i in pos]; gaps=[]; prev=-1
        for i in pos: gaps.append(i-prev-1); prev=i
        tail=len(flat)-pos[-1]-1 if pos else len(flat)
        actual={"source_atoms":len(flat),"events":events,"indices":pos,"gaps":gaps,"tail":tail}
        expected={"source_atoms":item["source_atoms"],"events":item["events"],"indices":item["indices"],"gaps":item["gaps_before"],"tail":item["tail"]}
        if actual != expected: errors.append({"record":rid,"actual":actual,"expected":expected})
        out[rid]=actual
    if set(out)!=set(RECORDS): errors.append({"error":"projection_record_coverage","actual":sorted(out),"expected":sorted(RECORDS)})
    return not errors,{"errors":errors,"projections":out,"source_sha256":sha(SOURCE),"spec_sha256":sha(SPEC)}

def regex(text,words,gaps,tail):
    first=re.escape(words[0]) if gaps[0]==0 else ".{"+str(gaps[0]) + ",}" + re.escape(words[0])
    pattern="^"+first
    for gap,word in zip(gaps[1:],words[1:]): pattern += ".{"+str(gap)+",}"+re.escape(word)
    return re.fullmatch(pattern+".{"+str(tail)+",}$",text) is not None

def positions(text,words,gaps,tail):
    first=starts(text,words[0]); first=[q for q in first if q==0] if gaps[0]==0 else [q for q in first if q>=gaps[0]]
    if not first: return None
    out=[first[0]]; end=first[0]+len(words[0])
    for gap,word in zip(gaps[1:],words[1:]):
        q=next((q for q in starts(text,word) if q>=end+gap),None)
        if q is None: return None
        out.append(q); end=q+len(word)
    return out if len(text)-end>=tail else None

def positions_match(text,words,gaps,tail,supplied):
    if not isinstance(supplied,list) or len(supplied)!=len(words) or any(not isinstance(q,int) or q<0 for q in supplied): return False
    if (gaps[0]==0 and supplied[0]!=0) or (gaps[0]>0 and supplied[0]<gaps[0]): return False
    for i,word in enumerate(words):
        if supplied[i]+len(word)>len(text) or not text.startswith(word,supplied[i]): return False
        if i and supplied[i]<supplied[i-1]+len(words[i-1])+gaps[i]: return False
    return len(text)-supplied[-1]-len(words[-1])>=tail

def fixture_check():
    v,w,l,b="ab","cde","f","g"; t=v+"x"+l+"y"*2+w+"z"*3+b+"q"*3; u=w+"q"*2+l+"r"*3+v+"s"+b+"t"*2
    return regex(t,[v,l,w,b],[0,1,2,3],3) and regex(u,[w,l,v,b],[0,2,3,1],2) and not regex(t,[v,"fX",w,b],[0,1,2,3],3)

SUPPORT_CACHE={}
def all_supports(domains,record,words,p):
    key=(id(domains),record,tuple(words))
    if key in SUPPORT_CACHE: return SUPPORT_CACHE[key]
    out=[]
    for row in domains.get(record,[]):
        pos=positions(row["text"],words,p[record]["gaps"],p[record]["tail"])
        if pos is not None: out.append({"page":row["page"],"physical_leaf":row["physical_leaf"],"positions":pos})
    SUPPORT_CACHE[key]=out
    return out

def canonical(rows): return sorted({json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")) for x in rows})

def candidate_pages(dom,c):
    rs=dom[c["edition"]]; return (next((r for r in rs["I.1"] if r["page"]==c["iris_page"]),None),next((r for r in rs["IV.20"] if r["page"]==c["xiphion_page"]),None))

def expected_support(c,dom,p,leaf,broad):
    i1,iv=candidate_pages(dom,c)
    if i1 is None or iv is None: return None
    rs=dom[c["edition"]]; v,w=c["iris_code"],c["xiphion_code"]
    ac=all_supports(rs,"I.2",[leaf,v,broad,v],p); me=all_supports(rs,"I.3",[leaf],p)
    from collections import Counter
    excluded={i1['physical_leaf'],iv['physical_leaf']}
    if len(excluded)!=2:return i1,iv,[],[],0
    ac=[a for a in ac if a['physical_leaf'] not in excluded]
    me=[m for m in me if m['physical_leaf'] not in excluded]
    ac_counts=Counter(a['physical_leaf'] for a in ac);me_counts=Counter(m['physical_leaf'] for m in me)
    count=sum(len(me)-me_counts[a['physical_leaf']] for a in ac)
    useful_ac=[a for a in ac if len(me)>me_counts[a['physical_leaf']]]
    useful_me=[m for m in me if len(ac)>ac_counts[m['physical_leaf']]]
    return i1,iv,useful_ac,useful_me,count

def fixed_var(leaf,broad,v,w):
    if any(code.startswith(leaf) for code in (v,w)): return "L"
    if any(code.startswith(broad) for code in (v,w)): return "B"
    if broad.startswith(leaf): return "L"
    if leaf.startswith(broad): return "B"
    return None

def successors(texts,prefix):
    common=None
    for text in texts:
        chars={text[q+len(prefix)] for q in starts(text,prefix) if q+len(prefix)<len(text)}
        common=chars if common is None else common&chars
    return sorted(common or set())

def replay_negative(c,dom,p,row):
    proof=row.get("proof"); errors=[]
    if not isinstance(proof,list): return ["proof_not_list"]
    i1,iv=candidate_pages(dom,c)
    if i1 is None or iv is None: return ["candidate_page_missing"]
    v,w=c["iris_code"],c["xiphion_code"]; texts=(i1["text"],iv["text"])
    chars=set(i1["text"])&set(iv["text"]); roots={(a,b) for a in chars for b in chars}; nodes={}
    for node in proof:
        if not isinstance(node,list) or len(node)!=4 or not all(isinstance(x,str) for x in node):
            errors.append("malformed_proof_node"); continue
        key=(node[0],node[1])
        if key in nodes: errors.append("duplicate_proof_node")
        nodes[key]=node
    pending=set(roots); reached=set()
    while pending:
        key=pending.pop()
        if key in reached: continue
        reached.add(key)
        if key not in nodes: errors.append("missing_reachable_node"); continue
        leaf,broad,reason,children=nodes[key]
        expected_children=""
        if any(code.startswith(fixed) for code in (leaf,broad) for fixed in (v,w)):
            expected="FIXED_PREFIX"
        elif not regex(i1["text"],[v,leaf,w,broad],p["I.1"]["gaps"],p["I.1"]["tail"]) or not regex(iv["text"],[w,leaf,v,broad],p["IV.20"]["gaps"],p["IV.20"]["tail"]):
            expected="NO_LOCAL_FIT"
        else:
            support=expected_support(c,dom,p,leaf,broad)
            if not support[4]: expected="NO_FOUR_LEAF_SUPPORT"
            else:
                var=fixed_var(leaf,broad,v,w)
                if var is None: expected="SAT_WITNESS_EXISTS"; errors.append("negative_contains_sat_node")
                else:
                    expected="BRANCH_"+var
                    expected_children="".join(successors(texts,leaf if var=="L" else broad))
                    pending.update((leaf+x,broad) if var=="L" else (leaf,broad+x) for x in expected_children)
        if reason!=expected: errors.append("wrong_reason")
        if children!=expected_children: errors.append("wrong_children")
    if reached!=set(nodes): errors.append("unreachable_proof_nodes")
    if row.get("nodes")!=len(nodes): errors.append("proof_node_count")
    return errors

def validate_witness(c,dom,p,witness):
    errors=[]
    if not isinstance(witness,dict): return ["witness_not_object"]
    leaf,broad=witness.get("leaf_code"),witness.get("broad_code"); v,w=c.get("iris_code"),c.get("xiphion_code"); vals=(v,w,leaf,broad)
    if not all(isinstance(x,str) and x for x in vals): return ["empty_code"]
    if any(not incomparable(a,b) for i,a in enumerate(vals) for b in vals[i+1:]): errors.append("codes_not_prefix_incomparable")
    i1,iv=candidate_pages(dom,c)
    if i1 is None or iv is None: return errors+["candidate_page_missing"]
    if not regex(i1["text"],[v,leaf,w,broad],p["I.1"]["gaps"],p["I.1"]["tail"]): errors.append("iris_projection_regex_invalid")
    if not regex(iv["text"],[w,leaf,v,broad],p["IV.20"]["gaps"],p["IV.20"]["tail"]): errors.append("xiphion_projection_regex_invalid")
    if not positions_match(i1["text"],[v,leaf,w,broad],p["I.1"]["gaps"],p["I.1"]["tail"],witness.get("iris_positions")): errors.append("iris_positions_invalid")
    if not positions_match(iv["text"],[w,leaf,v,broad],p["IV.20"]["gaps"],p["IV.20"]["tail"],witness.get("xiphion_positions")): errors.append("xiphion_positions_invalid")
    support=expected_support(c,dom,p,leaf,broad)
    if support is None: return errors+["candidate_page_missing"]
    ac,me,valid=support[2],support[3],support[4]
    if not valid: errors.append("witness_has_no_four_leaf_completion")
    if canonical(witness.get("acorus",[]))!=canonical(ac): errors.append("acorus_support_mismatch")
    if canonical(witness.get("meum",[]))!=canonical(me): errors.append("meum_support_mismatch")
    if witness.get("four_page_assignments")!=valid: errors.append("assignment_count_mismatch")
    return errors

def table_result_errors(candidates,cases):
    from collections import Counter
    errors=[]; expected=[]
    columns=['id','edition','iris_page','xiphion_page','iris_code','xiphion_code','status','leaf_witness','broad_witness','acorus_pages','meum_pages','four_page_assignments','nodes']
    for c,row in zip(candidates,cases):
        w=row.get('witness',{})
        expected.append([str(x) if x is not None else '' for x in [row['id'],*[c[k] for k in columns[1:6]],row['status'],w.get('leaf_code',''),w.get('broad_code',''),','.join(z['page'] for z in w.get('acorus',[])),','.join(z['page'] for z in w.get('meum',[])),w.get('four_page_assignments',''),row['nodes']]])
    with (ART/'CANDIDATE_RESULTS.tsv').open() as f:
        if list(csv.reader(f,delimiter='\t'))!=[columns]+expected:errors.append('prediction_result_table_cells')
    result=read_json(ART/'RESULT.json');good=[(c,z) for c,z in zip(candidates,cases) if z.get('status')==SAT];counts=dict(Counter(z['status'] for z in cases))
    status='PARTIAL_FOUR_ATOM_BINDINGS_REMAIN' if good else 'UNRESOLVED_PROJECTION' if any(x.startswith('UNKNOWN') for x in counts) else 'ALL_LITERAL_BASE_ROWS_CONTRADICTED'
    derived=dict(status=status,cases=len(cases),counts=counts,surviving_name_classes=len({(c['edition'],c['iris_code'],c['xiphion_code']) for c,z in good}),witnessed_iris_values=len({c['iris_code'] for c,z in good}),witnessed_xiphion_values=len({c['xiphion_code'] for c,z in good}),saved_leaf_witness_values=len({z['witness']['leaf_code'] for c,z in good}),saved_broad_witness_values=len({z['witness']['broad_code'] for c,z in good}),enumerated_all_leaf_broad_codes=False,constrained_source_occurrences=13,source_occurrences=613,confirmed_words=0,independent_confirmation_leaves=0,reserve_access=False,full_code_tested=False)
    errors.extend('RESULT:'+k for k,v in derived.items() if result.get(k)!=v)
    with (ART/'CASE_PREDICTIONS.tsv').open() as f:pred=list(csv.DictReader(f,delimiter='\t'))
    if len(pred)!=len(candidates):errors.append('registered_prediction_count')
    for i,(c,r) in enumerate(zip(candidates,pred)):
        if r['id']!=str(i) or any(r[k]!=c[k] for k in ['edition','iris_page','xiphion_page','iris_code','xiphion_code']):errors.append('registered_prediction_identity:'+str(i))
    return errors

def full():
    ok,source=source_projection()
    if not ok: return {"status":"FAIL","source":source,"errors":["source_projection"]}
    primary=ART/"CASES.json.gz"
    if not (DOMAINS.exists() and CANDIDATES.exists() and primary.exists()): return {"status":"PRIMARY_RESULT_MISSING","source":source,"errors":["required_artifact_missing"]}
    dom,candidates,cases=read_json(DOMAINS),read_gz(CANDIDATES),read_gz(primary); p=source["projections"]; errors=[]; expected_ids=[c.get("id",i) for i,c in enumerate(candidates)]
    by_id={r.get("id"):r for r in cases if isinstance(r,dict)}
    if len(candidates)!=int(read_json(SPEC).get("expected_cases",len(candidates))): errors.append("candidate_count")
    if len(cases)!=len(candidates) or set(by_id)!=set(expected_ids): errors.append("case_coverage")
    lock=read_json(EXP/"PREREG_LOCK.json")
    errors.extend("registration_hash:"+n for n,h in lock["files"].items() if sha(ROOT/n)!=h)
    if [r.get("id") for r in cases]!=list(range(len(candidates))):errors.append("case_order")
    if any(x["page"].startswith("f84") or x["page"]=="f116v" for rs in dom.values() for xs in rs.values() for x in xs):errors.append("forbidden_domain")
    checked=0
    for i,c in enumerate(candidates):
        cid=c.get("id",i); row=by_id.get(cid)
        if row is None: continue
        status=row.get("status")
        if status==SAT: errors.extend(f"{cid}:{e}" for e in validate_witness(c,dom,p,row.get("witness")))
        elif status==UNSAT: errors.extend(f"{cid}:{e}" for e in replay_negative(c,dom,p,row))
        elif status not in UNKNOWN: errors.append(f"{cid}:unknown_status:{status}")
        checked+=1
    errors.extend(table_result_errors(candidates,cases))
    counts={s:sum(r.get("status")==s for r in cases) for s in sorted({r.get("status") for r in cases})}
    return {"status":"PASS" if not errors else "FAIL","source":source,"checked_cases":checked,"case_count":len(cases),"errors":errors,"primary_status_counts":counts,"claim_ceiling":"certificate and projection validation; no semantic evidence"}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--source-only",action="store_true"); ap.add_argument("--full",action="store_true"); args=ap.parse_args(); ok,source=source_projection(); fixture=fixture_check()
    if args.source_only or not args.full:
        out={"status":"PASS_SOURCE_ONLY" if ok and fixture else "FAIL_SOURCE_ONLY","source":source,"fixtures":fixture,"claim_ceiling":"mathematical projection validation; no semantic evidence"}; ART.mkdir(parents=True,exist_ok=True); (ART/"SOURCE_VALIDATION.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n"); print(json.dumps(out,ensure_ascii=False,indent=2)); return 0 if out["status"]=="PASS_SOURCE_ONLY" else 1
    out=full(); out["fixtures"]=fixture; out["status"]=out["status"] if fixture else "FAIL"; ART.mkdir(parents=True,exist_ok=True); (ART/"VALIDATION.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n"); print(json.dumps(out,ensure_ascii=False,indent=2)); return 0 if out.get("status")=="PASS" else 1

if __name__=="__main__": raise SystemExit(main())
