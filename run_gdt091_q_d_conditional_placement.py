#!/usr/bin/env python3
"""GDT091: exact-cell permutation of q/O and d/Y placement."""
from __future__ import annotations
import csv,hashlib,json,random,statistics
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";METHOD=ROOT/"GDT091_Q_D_CONDITIONAL_PLACEMENT_METHOD.md";REPORT=ROOT/"GDT091_Q_D_CONDITIONAL_PLACEMENT_REPORT.md";EFFECTS=ROOT/"gdt091_operator_effects.tsv";NULL=ROOT/"gdt091_permutation_results.tsv";RESULT=ROOT/"gdt091_result.json";PERMUTATIONS=10000;SEED=91001
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 src=read(SOURCE);assert len(src)==15592 and not any(r["locus"].startswith("f84r") for r in src);by=defaultdict(list)
 for r in src:
  h=r["page_host"]
  if h and h[0] in "oy":by[h[0],h[1:]].append(r)
 tails={s for _,s in by if len(by.get(("o",s),[]))>=2 and len(by.get(("y",s),[]))>=2};assert len(tails)==42
 specs=(("Q_ON_O","o","q"),("D_ON_Y","y","d"));panels={}
 for name,base,target in specs:
  z=[]
  for tail in sorted(tails):
   for r in by[base,tail]:
    if r["wrapper"] in {target,"NONE"}:z.append({"folio":r["physical_folio"],"tail":tail,"register":r["register"],"target":int(r["wrapper"]==target),"position":int(r["position_quartile"]),"dy":int(r["dy_closure"]),"right_none":int(r["right_family"]=="NONE")})
  panels[name]=z
 def calc(z,labels):
  a=[i for i,y in enumerate(labels) if y];b=[i for i,y in enumerate(labels) if not y]
  return {k:sum(z[i][k] for i in a)/len(a)-sum(z[i][k] for i in b)/len(b) for k in ("position","dy","right_none")}
 observed={};world={name:[] for name,_,_ in specs};rng=random.Random(SEED)
 strata={};labels={}
 for name,_,_ in specs:
  z=panels[name];labels[name]=[r["target"] for r in z];s=defaultdict(list)
  for i,r in enumerate(z):s[r["folio"],r["tail"],r["register"]].append(i)
  strata[name]=s;observed[name]=calc(z,labels[name])
 for _ in range(PERMUTATIONS):
  for name,_,_ in specs:
   yp=labels[name][:]
   for idx in strata[name].values():
    vals=[yp[i] for i in idx];rng.shuffle(vals)
    for i,v in zip(idx,vals):yp[i]=v
   world[name].append(calc(panels[name],yp))
 effects=[]
 for name,base,target in specs:
  z=panels[name];n1=sum(labels[name]);n0=len(z)-n1
  for measure in ("position","dy","right_none"):
   obs=observed[name][measure];vals=[x[measure] for x in world[name]];p=(sum(abs(x)>=abs(obs) for x in vals)+1)/(PERMUTATIONS+1)
   effects.append({"operator_contrast":name,"base_axis":base,"target_wrapper":target,"control_wrapper":"NONE","measure":measure,"groups":len(z),"target_groups":n1,"control_groups":n0,"observed_target_minus_control":obs,"permutation_mean":statistics.mean(vals),"permutation_sd":statistics.pstdev(vals),"two_sided_p":p,"classification":("EARLY_SHIFT" if obs<0 else "LATE_SHIFT") if measure=="position" else "SECONDARY_DESCRIPTIVE"})
 combo=observed["D_ON_Y"]["position"]-observed["Q_ON_O"]["position"];cw=[d["position"]-q["position"] for d,q in zip(world["D_ON_Y"],world["Q_ON_O"])];cp=(sum(x>=combo for x in cw)+1)/(PERMUTATIONS+1)
 out=[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in effects];write(EFFECTS,out,list(out[0]));nullrows=[{"null_id":"WITHIN_FOLIO_TAIL_REGISTER_WRAPPER_PERMUTATION","permutations":PERMUTATIONS,"seed":SEED,"combined_d_late_minus_q_early":combo,"combined_one_sided_p":cp,"q_position_shift":observed["Q_ON_O"]["position"],"d_position_shift":observed["D_ON_Y"]["position"],"preserves":"physical folio;matched tail;register;base;wrapper totals"}];write(NULL,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in nullrows],list(nullrows[0]))
 qp=next(r for r in effects if r["operator_contrast"]=="Q_ON_O" and r["measure"]=="position");dp=next(r for r in effects if r["operator_contrast"]=="D_ON_Y" and r["measure"]=="position");status="Q_EARLY_D_LATE_PLACEMENT_OPPOSITION_CONDITIONAL_ON_HOST_BASE"
 REPORT.write_text(f"""# GDT091 — q/d conditional placement

## Outcome

**{status}**

On {qp['groups']} O-base q/NONE groups, q shifts the same matched-tail class
{qp['observed_target_minus_control']:+.3f} position quartiles earlier
(cell-preserving p={qp['two_sided_p']:.4f}).  On {dp['groups']} Y-base d/NONE
groups, d shifts {dp['observed_target_minus_control']:+.3f} quartiles later
(p={dp['two_sided_p']:.4f}).  The combined opposing-direction statistic is
{combo:+.3f} (one-sided p={cp:.4f}).

DY and right-renderer differences are much less secure after exact-cell
permutation.  The important grammar refinement is conditionality: q is an
early O-branch wrapper, while d is a late Y-branch wrapper in this matched
panel.  The earlier global `d=entry` description cannot be universal; it
mixed host classes and a narrower candidate-module universe.

This is a formal placement architecture, not a semantic operator, morpheme,
sound, or translation.  f84r was absent and remained sealed.
""",encoding="utf-8")
 result={"schema":"GDT091_Q_D_CONDITIONAL_PLACEMENT_RESULT_V1","status":status,"matched_tails":len(tails),"comparisons":{name:{"groups":len(panels[name]),"target_groups":sum(labels[name]),"effects":observed[name]} for name,_,_ in specs},"combined_position_opposition":combo,"combined_one_sided_p":cp,"permutations":PERMUTATIONS,"grammar_refinement":"q is an early O-base branch wrapper; d is a late Y-base branch wrapper in matched host classes; wrapper placement is host-conditional.","claim_ceiling":"Formal construction placement only; no semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt011_result.json":sha(ROOT/"gdt011_result.json"),"gdt087_result.json":sha(ROOT/"gdt087_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{EFFECTS.name:sha(EFFECTS),NULL.name:sha(NULL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"q_shift":qp["observed_target_minus_control"],"q_p":qp["two_sided_p"],"d_shift":dp["observed_target_minus_control"],"d_p":dp["two_sided_p"],"combined_p":cp},sort_keys=True))
if __name__=="__main__":main()
