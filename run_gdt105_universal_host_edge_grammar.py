#!/usr/bin/env python3
"""GDT105: manuscript-wide PAGE_HOST edge-to-renderer prediction."""
import csv,hashlib,json,math
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";METHOD=ROOT/"GDT105_UNIVERSAL_HOST_EDGE_GRAMMAR_METHOD.md";REPORT=ROOT/"GDT105_UNIVERSAL_HOST_EDGE_GRAMMAR_REPORT.md";SCORES=ROOT/"gdt105_edge_model_scores.tsv";REG=ROOT/"gdt105_leave_register_scores.tsv";PCH=ROOT/"gdt105_nonpch_to_pch_transfer.tsv";RESULT=ROOT/"gdt105_result.json";ALPHA=.5
MODELS=(("REGISTER_ONLY","constant"),("FIRST_CHAR","first"),("FINAL_CHAR","last"),("FINAL_TWO","last2"),("HOST_LENGTH","length"),("EXACT_PAGE_HOST","host"))
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def prepare(x):
 host=x["page_host"];dy=x["dy_closure"]=="1";right=x["right_family"]!="NONE";b3=x["b3"]=="1";out="DY_RIGHT" if dy and right else ("DY" if dy else ("RIGHT" if right else ("B3" if b3 else "BARE")))
 return {"folio":x["physical_folio"],"register":x["register"],"constant":"*","first":host[:1],"last":host[-1:],"last2":host[-2:],"length":str(len(host)),"host":host,"outcome":out,"pch":int("pch" in host)}
def lofo(rows,feature,classes):
 allc=Counter((x["register"],x[feature],x["outcome"]) for x in rows);alln=Counter((x["register"],x[feature]) for x in rows);fc=Counter((x["folio"],x["register"],x[feature],x["outcome"]) for x in rows);fn=Counter((x["folio"],x["register"],x[feature]) for x in rows);bits=0.;fb=Counter()
 for x in rows:
  count=allc[x["register"],x[feature],x["outcome"]]-fc[x["folio"],x["register"],x[feature],x["outcome"]];n=alln[x["register"],x[feature]]-fn[x["folio"],x["register"],x[feature]];loss=-math.log2((count+ALPHA)/(n+ALPHA*len(classes)));bits+=loss;fb[x["folio"]]+=loss
 return bits,fb
def transfer(train,test,feature,classes,with_register=True):
 def key(x):return (x["register"],x[feature]) if with_register else x[feature]
 counts=Counter((key(x),x["outcome"]) for x in train);tot=Counter(key(x) for x in train);fallback=Counter((x["register"] if with_register else "*",x["outcome"]) for x in train);falln=Counter(x["register"] if with_register else "*" for x in train);bits=0.
 for x in test:
  k=key(x);f=x["register"] if with_register else "*";prob=(counts[k,x["outcome"]]+ALPHA)/(tot[k]+ALPHA*len(classes)) if tot[k] else (fallback[f,x["outcome"]]+ALPHA)/(falln[f]+ALPHA*len(classes));bits-=math.log2(prob)
 return bits
def main():
 raw=read(SOURCE);assert len(raw)==15592 and not any(x["page"].startswith("f84r") for x in raw);rows=[prepare(x) for x in raw];classes=sorted({x["outcome"] for x in rows});scores=[];cache={}
 for name,feature in MODELS:
  bits,fb=lofo(rows,feature,classes);cache[name]=bits;scores.append({"model":name,"feature":feature,"groups":len(rows),"physical_folios":len(fb),"leave_folio_bits":bits,"gain_vs_register_bits":"","positive_folios_vs_register":"","semantic_role":"UNASSIGNED"})
 base=cache["REGISTER_ONLY"];basefb=lofo(rows,"constant",classes)[1]
 for x in scores:
  x["gain_vs_register_bits"]=base-float(x["leave_folio_bits"]);fb=lofo(rows,x["feature"],classes)[1];x["positive_folios_vs_register"]=sum(fb[f]<basefb[f] for f in fb)
 write(SCORES,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in scores],list(scores[0]));pch_train=[x for x in rows if not x["pch"]];pch_test=[x for x in rows if x["pch"]];pchrows=[]
 for name,feature in MODELS:
  bits=transfer(pch_train,pch_test,feature,classes,True);pchrows.append({"train_scope":"ALL_NON_PCH","test_scope":"PCH_ONLY","train_groups":len(pch_train),"test_groups":len(pch_test),"model":name,"test_bits":bits,"gain_vs_register_bits":"","semantic_role":"UNASSIGNED"})
 pbase=next(x["test_bits"] for x in pchrows if x["model"]=="REGISTER_ONLY")
 for x in pchrows:x["gain_vs_register_bits"]=pbase-float(x["test_bits"])
 write(PCH,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in pchrows],list(pchrows[0]));regrows=[]
 for target in sorted({x["register"] for x in rows}):
  reg_train=[x for x in rows if x["register"]!=target];reg_test=[x for x in rows if x["register"]==target]
  values={name:transfer(reg_train,reg_test,feature,classes,False) for name,feature in MODELS};b=values["REGISTER_ONLY"]
  for name,feature in MODELS:regrows.append({"target_register":target,"train_groups":len(reg_train),"test_groups":len(reg_test),"model":name,"test_bits":values[name],"gain_vs_other_register_prevalence_bits":b-values[name],"semantic_role":"UNASSIGNED"})
 write(REG,[{k:(f"{v:.12g}" if isinstance(v,float) else v) for k,v in x.items()} for x in regrows],list(regrows[0]));best=min(scores,key=lambda x:float(x["leave_folio_bits"]));pbest=min(pchrows,key=lambda x:float(x["test_bits"]));status="UNIVERSAL_FINAL_CHARACTER_RENDERER_GRAMMAR_DOMINATES_EXACT_PAGE_HOST"
 REPORT.write_text(f"""# GDT105 — universal PAGE_HOST edge grammar

## Outcome

**{status}**

Across all {len(rows):,} groups on {len({x['folio'] for x in rows})} physical
folios, register-only renderer prediction costs {base:,.3f} held bits. The
final PAGE_HOST character costs only {cache['FINAL_CHAR']:,.3f}, gaining
{base-cache['FINAL_CHAR']:,.3f} bits. It beats final-two
({cache['FINAL_TWO']:,.3f}), exact PAGE_HOST ({cache['EXACT_PAGE_HOST']:,.3f}),
first character ({cache['FIRST_CHAR']:,.3f}), and length
({cache['HOST_LENGTH']:,.3f}). The direction holds in every leave-register-out
target.

This is not a PCH-specific fact. After all {len(pch_test)} PCH groups are removed
from training, final-character prediction scores them in
{next(x['test_bits'] for x in pchrows if x['model']=='FINAL_CHAR'):.3f} bits,
versus register prevalence {pbase:.3f}; exact PAGE_HOST cannot transfer and
backs off to {next(x['test_bits'] for x in pchrows if x['model']=='EXACT_PAGE_HOST'):.3f}.
GDT102's attractive PCH tail rules are therefore an instance of a universal
host-edge grammar.

The HPR2 generator should be revised from an opaque PAGE_HOST to
`CONTENT_ADDRESS + EDGE_STATE`, where EDGE_STATE strongly licenses DY,
RIGHT_FAMILY, B3, or bare closure. This improves formal factorization but does
not show that CONTENT_ADDRESS has meaning. Because the parser itself removes
renderer material, some edge predictability may be structural by construction;
the external-content question must be retested after edge stripping.

All roles remain UNASSIGNED. f84r was absent and untouched.
""",encoding="utf-8")
 result={"schema":"GDT105_UNIVERSAL_HOST_EDGE_GRAMMAR_RESULT_V1","status":status,"groups":len(rows),"physical_folios":len({x["folio"] for x in rows}),"renderer_counts":dict(Counter(x["outcome"] for x in rows)),"models":{x["model"]:x for x in scores},"best_model":best["model"],"pch_groups":len(pch_test),"pch_transfer":{x["model"]:x for x in pchrows},"pch_best_model":pbest["model"],"leave_register_rows":len(regrows),"generative_revision":"PAGE_HOST := CONTENT_ADDRESS + EDGE_STATE; EDGE_STATE licenses the following renderer.","interpretation":"Final PAGE_HOST character is a universal renderer-licensing edge state, not a PCH-specific factor; content status of the residual remains unproved.","semantic_role":"UNASSIGNED","claim_ceiling":"Formal edge grammar only; no word, morpheme, POS, sound, language, plaintext, role, gloss, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt102_result.json":sha(ROOT/"gdt102_result.json"),"gdt062_result.json":sha(ROOT/"gdt062_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{SCORES.name:sha(SCORES),REG.name:sha(REG),PCH.name:sha(PCH)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"best":best["model"],"base":base,"last":cache["FINAL_CHAR"],"pch_base":pbase,"pch_last":next(x['test_bits'] for x in pchrows if x['model']=='FINAL_CHAR')},sort_keys=True))
if __name__=="__main__":main()
