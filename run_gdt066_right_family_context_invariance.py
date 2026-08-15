#!/usr/bin/env python3
"""GDT066: exact-host page context across RIGHT_FAMILY renderings."""
from __future__ import annotations
import csv, hashlib, json, math
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"gdt062_right_family_inventory.tsv"
METHOD=ROOT/"GDT066_RIGHT_FAMILY_CONTEXT_INVARIANCE_METHOD.md"
REPORT=ROOT/"GDT066_RIGHT_FAMILY_CONTEXT_INVARIANCE_REPORT.md"
PAIRS=ROOT/"gdt066_right_family_context_pairs.tsv"
CELLS=ROOT/"gdt066_right_family_context_cells.tsv"
VARIANTS=ROOT/"gdt066_variant_log.tsv"
RESULT=ROOT/"gdt066_result.json"

def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))
def write(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer=csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csha(value): return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def wj(a,b):
    keys=set(a)|set(b); den=sum(max(a[k],b[k]) for k in keys)
    return sum(min(a[k],b[k]) for k in keys)/den if den else 0.
def binom_two(k,n):
    lo=sum(math.comb(n,i) for i in range(k+1))/2**n
    hi=sum(math.comb(n,i) for i in range(k,n+1))/2**n
    return min(1.,2*min(lo,hi))

def main():
    rows=read(SOURCE)
    assert len(rows)==15592 and not any(r["locus"].startswith("f84r") for r in rows)
    pages=defaultdict(list)
    for row in rows: pages[row["page"]].append(row)
    units=[]
    for page,z in sorted(pages.items()):
        bag=Counter(r["page_host"] for r in z); grouped=defaultdict(list)
        for r in z: grouped[r["page_host"],r["right_family"],r["wrapper"],r["local_frame"]].append(r)
        for (host,right,wrapper,frame),q in sorted(grouped.items()):
            context=Counter(bag); del context[host]
            units.append({"unit_id":"|".join((page,host,right,wrapper,frame)),"page":page,
                          "physical_folio":q[0]["physical_folio"],"register":q[0]["register"],
                          "host":host,"right_family":right,"wrapper":wrapper,"frame":frame,
                          "host_len_bucket":len(host)//2,"page_size_bucket":len(z)//25,"context":context})
    pool=defaultdict(list); bycell=defaultdict(list)
    for u in units:
        pool[u["register"],u["wrapper"],u["frame"],u["right_family"],u["host_len_bucket"],u["page_size_bucket"]].append(u)
        bycell[u["host"],u["register"],u["wrapper"],u["frame"]].append(u)
    pairrows=[]; vals=defaultdict(lambda:{"diff":[],"same":[]})
    for cell,z in sorted(bycell.items()):
        host,reg,wrapper,frame=cell; candidates=defaultdict(list)
        for a,b in combinations(z,2):
            if a["physical_folio"]==b["physical_folio"]: continue
            pair_type="same" if a["right_family"]==b["right_family"] else "diff"
            key=hashlib.sha256((a["unit_id"]+"|"+b["unit_id"]).encode()).hexdigest()
            candidates[pair_type].append((key,a,b))
        for pair_type in ("diff","same"):
            for _,a,b in sorted(candidates[pair_type])[:200]:
                controls=[q for q in pool[b["register"],b["wrapper"],b["frame"],b["right_family"],a["host_len_bucket"],b["page_size_bucket"]]
                          if q["physical_folio"]!=a["physical_folio"] and q["host"]!=host]
                if not controls: continue
                sim=wj(a["context"],b["context"])
                control=sum(wj(a["context"],q["context"]) for q in controls)/len(controls)
                pairrows.append({"host":host,"register":reg,"wrapper":wrapper,"frame":frame,
                                 "pair_type":pair_type.upper()+"_RIGHT_FAMILY","left_unit":a["unit_id"],
                                 "right_unit":b["unit_id"],"left_right_family":a["right_family"],
                                 "right_right_family":b["right_family"],"context_similarity":sim,
                                 "matched_control_similarity":control,"gain_vs_control":sim-control,
                                 "control_units":len(controls)})
                vals[cell][pair_type].append((sim,control))
    cells=[]
    for (host,reg,wrapper,frame),value in sorted(vals.items()):
        if not value["diff"]: continue
        diff=sum(x for x,_ in value["diff"])/len(value["diff"])
        control=sum(y for _,y in value["diff"])/len(value["diff"])
        same=sum(x for x,_ in value["same"])/len(value["same"]) if value["same"] else 0.
        cells.append({"host":host,"register":reg,"wrapper":wrapper,"frame":frame,
                      "different_right_pairs":len(value["diff"]),"same_right_pairs":len(value["same"]),
                      "different_right_mean_similarity":diff,"matched_control_mean_similarity":control,
                      "same_right_mean_similarity":same,"different_minus_control":diff-control,
                      "different_minus_same":diff-same if value["same"] else 0.,
                      "same_right_available":int(bool(value["same"]))})
    pairrows.sort(key=lambda r:(r["host"],r["register"],r["wrapper"],r["frame"],r["pair_type"],r["left_unit"],r["right_unit"]))
    cells.sort(key=lambda r:(-r["different_minus_control"],r["host"],r["register"],r["wrapper"],r["frame"]))
    write(PAIRS,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in pairrows],list(pairrows[0]))
    write(CELLS,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in cells],list(cells[0]))
    n=len(cells); pos=sum(r["different_minus_control"]>0 for r in cells)
    diff=sum(r["different_right_mean_similarity"] for r in cells)/n
    control=sum(r["matched_control_mean_similarity"] for r in cells)/n
    both=[r for r in cells if r["same_right_available"]]
    same=sum(r["same_right_mean_similarity"] for r in both)/len(both)
    gain=diff-control; p=binom_two(pos,n)
    status="RIGHT_FAMILY_INTERNAL_CONTEXT_INVARIANCE_SUPPORTED" if gain>0 and p<.05 else "RIGHT_FAMILY_CONTEXT_INVARIANCE_WEAK_OR_UNSTABLE"
    regs={}
    for reg in sorted({r["register"] for r in cells}):
        q=[r for r in cells if r["register"]==reg]
        regs[reg]={"cells":len(q),"positive":sum(r["different_minus_control"]>0 for r in q),
                   "mean_gain":sum(r["different_minus_control"] for r in q)/len(q)}
    leads={h:[r for r in cells if r["host"]==h] for h in ("d","ok")}
    variants=[{"variant_id":"V00","status":"PRIMARY","description":"Exact host, different RIGHT_FAMILY, cross-folio context under fixed register/wrapper/frame."},
              {"variant_id":"V01","status":"RUN_CONTROL","description":"Different host matched on target RIGHT_FAMILY, register, wrapper, frame, host length, and page size; unsupported pairs dropped."},
              {"variant_id":"V02","status":"RUN_SENSITIVITY","description":"Same-host same-RIGHT_FAMILY cross-folio context where capacity exists."},
              {"variant_id":"V03","status":"POSTSELECTED_DISPLAY","description":"GDT063 d and ok cells displayed without setting the headline."},
              {"variant_id":"V04","status":"NOT_RUN","description":"No external annotation score, semantic role, alternate parser, or f84r."}]
    write(VARIANTS,variants,list(variants[0]))
    report=f"""# GDT066 — RIGHT_FAMILY context invariance conditional on PAGE_HOST

## Outcome

**{status}**

The inventory yields {len(units):,} page-level renderer units and {len(pairrows):,}
supported exact-host pairs.  Across {n} host×register×wrapper×frame cells,
different-RIGHT_FAMILY exact-host context similarity is {diff:.5f}, versus
{control:.5f} for matched different-host controls: gain {gain:+.5f}.
{pos}/{n} cells are positive (descriptive sign p={p:.6g}).  The
{len(both)} cells with a same-RIGHT_FAMILY comparison average {same:.5f};
different minus same is {diff-same:+.5f}.

Register diagnostics are {json.dumps(regs,sort_keys=True)}.  The postselected
`ok` lead is positive in {sum(r['different_minus_control']>0 for r in leads['ok'])}/{len(leads['ok'])}
cells and `d` in {sum(r['different_minus_control']>0 for r in leads['d'])}/{len(leads['d'])};
neither sets the headline.  The test concerns internal page ecology and cannot
establish that RIGHT_FAMILY lacks independent content.  GDT059 remains the
external-content warning.  No role, gloss, word, morpheme, POS, sound,
language, plaintext, meaning, or translation is assigned.  f84r was excluded
and not opened, retained, queried, joined, or scored.
"""
    REPORT.write_text(report,encoding="utf-8")
    result={"schema":"GDT066_RIGHT_FAMILY_CONTEXT_INVARIANCE_RESULT_V1","status":status,
            "groups":len(rows),"units":len(units),"supported_pairs":len(pairrows),"cells":n,
            "positive_cells":pos,"sign_test_p":p,"mean_different_right_similarity":diff,
            "mean_matched_control_similarity":control,"different_minus_control":gain,
            "same_right_cells":len(both),"mean_same_right_similarity":same,
            "different_minus_same":diff-same,"register_diagnostics":regs,
            "postselected_lead_cells":{h:len(z) for h,z in leads.items()},
            "postselected_lead_positive":{h:sum(r["different_minus_control"]>0 for r in z) for h,z in leads.items()},
            "interpretation":"Tests internal exact-host context stability across RIGHT_FAMILY renderings; external content neutrality remains unconfirmed.",
            "claim_ceiling":"No role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
            "f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},
            "inputs":{SOURCE.name:sha(SOURCE),"gdt059_result.json":sha(ROOT/"gdt059_result.json"),"gdt062_result.json":sha(ROOT/"gdt062_result.json"),"gdt063_result.json":sha(ROOT/"gdt063_result.json")},
            "implementation":{Path(__file__).name:sha(Path(__file__))},
            "outputs":{PAIRS.name:sha(PAIRS),CELLS.name:sha(CELLS),VARIANTS.name:sha(VARIANTS)},
            "documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
    result["result_content_sha256"]=csha(result)
    RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,"units":len(units),"pairs":len(pairrows),"cells":n,"positive":pos,"p":p,"gain":gain,"same_delta":diff-same},sort_keys=True))

if __name__=="__main__": main()
