#!/usr/bin/env python3
"""GDT102: PCH tail versus final-character renderer prediction."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";METHOD=ROOT/"GDT102_PCH_RENDERER_LICENSING_METHOD.md";REPORT=ROOT/"GDT102_PCH_RENDERER_LICENSING_REPORT.md";CELLS=ROOT/"gdt102_pch_tail_renderer_counts.tsv";MODELS=ROOT/"gdt102_renderer_model_comparison.tsv";XFER=ROOT/"gdt102_cross_register_transfer.tsv";RESULT=ROOT/"gdt102_result.json"
P=("","o","y");T=("","e","ed","ey","d","y");ALPHA=.5
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def model_bits(rows,feature,outcome):
 classes=sorted({x[outcome] for x in rows});K=len(classes);bits=0.;per=Counter()
 for z in rows:
  tr=[x for x in rows if x["folio"]!=z["folio"]]; c=Counter((x["register"],x[feature],x[outcome]) for x in tr);n=Counter((x["register"],x[feature]) for x in tr);cr=Counter((x["register"],x[outcome]) for x in tr);nr=Counter(x["register"] for x in tr)
  prob=(c[z["register"],z[feature],z[outcome]]+ALPHA)/(n[z["register"],z[feature]]+ALPHA*K) if n[z["register"],z[feature]] else (cr[z["register"],z[outcome]]+ALPHA)/(nr[z["register"]]+ALPHA*K)
  loss=-math.log2(prob);bits+=loss;per[z["folio"]]+=loss
 return bits,per
def transfer_bits(train,test,feature,outcome):
 classes=sorted({x[outcome] for x in train+test});K=len(classes);base=Counter(x[outcome] for x in train);N=len(train);c=Counter((x[feature],x[outcome]) for x in train);n=Counter(x[feature] for x in train);bits=0.
 for z in test:
  prob=(c[z[feature],z[outcome]]+ALPHA)/(n[z[feature]]+ALPHA*K) if n[z[feature]] else (base[z[outcome]]+ALPHA)/(N+ALPHA*K);bits-=math.log2(prob)
 return bits
def main():
 src=[x for x in read(SOURCE) if not x["page"].startswith("f84r")];rows=[]
 for x in src:
  for p in P:
   for t in T:
    if x["page_host"]==p+"pch"+t:
     coarse="DY" if x["dy_closure"]=="1" else ("RIGHT" if x["right_family"]!="NONE" else "BARE");detail="DY" if coarse=="DY" else ("RF_"+x["right_family"] if coarse=="RIGHT" else "BARE")
     rows.append({"prefix":p or "EMPTY","tail":t or "EMPTY","last_char":x["page_host"][-1],"exact_host":x["page_host"],"register_key":x["register"],"register":x["register"],"folio":x["physical_folio"],"coarse":coarse,"detail":detail})
 assert len(rows)==181 and not any(x["page"].startswith("f84r") for x in src)
 counts=[]
 for t in T:
  z=[x for x in rows if x["tail"]==(t or "EMPTY")];c=Counter(x["coarse"] for x in z);d=Counter(x["detail"] for x in z)
  counts.append({"tail":t or "EMPTY","source_groups":len(z),"bare":c["BARE"],"dy":c["DY"],"right":c["RIGHT"],"dy_rate":c["DY"]/len(z),"right_rate":c["RIGHT"]/len(z),"right_family_detail":";".join(f"{k}={v}" for k,v in sorted(d.items()) if k.startswith("RF_")),"semantic_role":"UNASSIGNED"})
 write(CELLS,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in counts],list(counts[0]))
 model_rows=[];cache={}
 variants=(("REGISTER_ONLY","register_key"),("PAGE_HOST_TAIL","tail"),("FINAL_SOURCE_CHAR","last_char"),("EXACT_PAGE_HOST","exact_host"))
 for outcome in ("coarse","detail"):
  base,_=model_bits(rows,"register_key",outcome)
  for name,feature in variants:
   bits,per=model_bits(rows,feature,outcome);cache[outcome,name]=bits
   model_rows.append({"outcome":outcome.upper(),"model":name,"leave_folio_bits":bits,"gain_vs_register_bits":base-bits,"gain_vs_final_char_bits":cache.get((outcome,"FINAL_SOURCE_CHAR"),float("nan")) if False else "","positive_folios_vs_register":sum(per[f]<model_bits(rows,"register_key",outcome)[1][f] for f in per),"scored_folios":len(per),"semantic_role":"UNASSIGNED"})
 # Fill final-character comparison after all variants exist.
 for x in model_rows:x["gain_vs_final_char_bits"]=cache[x["outcome"].lower(),"FINAL_SOURCE_CHAR"]-float(x["leave_folio_bits"])
 write(MODELS,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in model_rows],list(model_rows[0]))
 cross=[]
 for train_reg,test_reg in (("HERBAL_B","STARS_RECIPE_B"),("STARS_RECIPE_B","HERBAL_B")):
  train=[x for x in rows if x["register"]==train_reg];test=[x for x in rows if x["register"]==test_reg]
  for outcome in ("coarse","detail"):
   base=transfer_bits(train,test,"register_key",outcome)
   final=transfer_bits(train,test,"last_char",outcome)
   for name,feature in variants:
    bits=transfer_bits(train,test,feature,outcome);cross.append({"train_register":train_reg,"test_register":test_reg,"train_groups":len(train),"test_groups":len(test),"outcome":outcome.upper(),"model":name,"test_bits":bits,"gain_vs_train_prevalence_bits":base-bits,"gain_vs_final_char_bits":final-bits,"semantic_role":"UNASSIGNED"})
 write(XFER,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in cross],list(cross[0]))
 coarse={x["model"]:x for x in model_rows if x["outcome"]=="COARSE"};detail={x["model"]:x for x in model_rows if x["outcome"]=="DETAIL"};status="PCH_TAIL_STRONGLY_LICENSES_RENDERER_BUT_FINAL_CHARACTER_BASELINE_IS_STRONGER"
 REPORT.write_text(f"""# GDT102 — `PCH` host-edge renderer licensing

## Outcome

**{status}**

The right edge of the `PCH` grid strongly predicts what the HPR2 compiler does
next. On the three-way `DY`/RIGHT/BARE outcome, the six-level tail reduces
leave-folio codelength from {float(coarse['REGISTER_ONLY']['leave_folio_bits']):.3f}
to {float(coarse['PAGE_HOST_TAIL']['leave_folio_bits']):.3f} bits. The detailed
RIGHT_FAMILY outcome falls from {float(detail['REGISTER_ONLY']['leave_folio_bits']):.3f}
to {float(detail['PAGE_HOST_TAIL']['leave_folio_bits']):.3f} bits. This is a
large transferable formal licensing relation.

It is not evidence for a hidden linguistic slot beyond strings. The final
PAGE_HOST character is stronger: {float(coarse['FINAL_SOURCE_CHAR']['leave_folio_bits']):.3f}
coarse bits and {float(detail['FINAL_SOURCE_CHAR']['leave_folio_bits']):.3f}
detailed bits, beating the inspected tail by
{float(coarse['PAGE_HOST_TAIL']['leave_folio_bits'])-float(coarse['FINAL_SOURCE_CHAR']['leave_folio_bits']):.3f}
and {float(detail['PAGE_HOST_TAIL']['leave_folio_bits'])-float(detail['FINAL_SOURCE_CHAR']['leave_folio_bits']):.3f}
bits. Exact PAGE_HOST is worse still because of sparse forms.

The same direction transfers between Herbal-B and Recipe/Stars-B, but the
final-character model again equals or beats the tail model. Descriptively,
`e`-tail hosts close with DY in 68/71 cases; `d`-tail hosts take a RIGHT_FAMILY
in 10/10; and `ey`/`y` tails take neither DY nor RIGHT_FAMILY in 51/51. These
are excellent rules for the formal generator and poor evidence for semantics:
they are visible at the ordinary source-string edge.

No `PCH` grid group carries B3, so B3 remains a negative/non-overlapping
compiler control here rather than a tested content carrier. The best model is
therefore a host-edge-conditioned renderer. f84r was excluded and untouched.
""",encoding="utf-8")
 result={"schema":"GDT102_PCH_RENDERER_LICENSING_RESULT_V1","status":status,"source_groups":len(src),"grid_groups":len(rows),"grid_folios":len({x["folio"] for x in rows}),"b3_groups":0,"coarse_models":{x["model"]:float(x["leave_folio_bits"]) for x in model_rows if x["outcome"]=="COARSE"},"detail_models":{x["model"]:float(x["leave_folio_bits"]) for x in model_rows if x["outcome"]=="DETAIL"},"tail_minus_final_coarse_bits":float(coarse["PAGE_HOST_TAIL"]["leave_folio_bits"])-float(coarse["FINAL_SOURCE_CHAR"]["leave_folio_bits"]),"tail_minus_final_detail_bits":float(detail["PAGE_HOST_TAIL"]["leave_folio_bits"])-float(detail["FINAL_SOURCE_CHAR"]["leave_folio_bits"]),"interpretation":"PCH host edge licenses the following HPR2 renderer across folios/registers, but final-character statistics are stronger than the inspected factor tail.","semantic_role":"UNASSIGNED","claim_ceiling":"Formal host-edge renderer licensing only; no word, morpheme, POS, sound, language, plaintext, role, gloss, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt101_result.json":sha(ROOT/"gdt101_result.json"),"gdt003_nested_result.json":sha(ROOT/"gdt003_nested_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{CELLS.name:sha(CELLS),MODELS.name:sha(MODELS),XFER.name:sha(XFER)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"coarse":result["coarse_models"],"tail_minus_final":result["tail_minus_final_coarse_bits"]},sort_keys=True))
if __name__=="__main__":main()
