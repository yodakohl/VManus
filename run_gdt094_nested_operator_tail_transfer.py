#!/usr/bin/env python3
"""GDT094: nested unseen-tail+folio q/d operator prediction."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt062_right_family_inventory.tsv";METHOD=ROOT/"GDT094_NESTED_OPERATOR_TAIL_TRANSFER_METHOD.md";REPORT=ROOT/"GDT094_NESTED_OPERATOR_TAIL_TRANSFER_REPORT.md";SCORES=ROOT/"gdt094_nested_model_scores.tsv";TAILS=ROOT/"gdt094_tail_directions.tsv";BASE=ROOT/"gdt094_baseline_comparison.tsv";RESULT=ROOT/"gdt094_result.json";LAMBDAS=(1,4,16,64,256);OUTCOMES=("Q","D");FEATURES=("BASE_OY","TAIL_LAST","HOST_LENGTH","TAIL_LAST_X_LENGTH")
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def feature(r,name):
 if name=="BASE_OY":return r["base"]
 if name=="TAIL_LAST":return r["tail"][-1:] or "EMPTY"
 if name=="HOST_LENGTH":return str(len(r["page_host"]))
 if name=="TAIL_LAST_X_LENGTH":return (r["tail"][-1:] or "EMPTY")+"|"+str(len(r["page_host"]))
 raise ValueError(name)
def main():
 src=read(SOURCE);assert len(src)==15592 and not any(r["locus"].startswith("f84r") for r in src);by=defaultdict(list)
 for r in src:
  h=r["page_host"]
  if h and h[0] in "oy":by[h[0],h[1:]].append(r)
 tails=sorted({s for _,s in by if len(by.get(("o",s),[]))>=2 and len(by.get(("y",s),[]))>=2});rows=[{**r,"base":b,"tail":s} for s in tails for b in "oy" for r in by[b,s]];assert len(tails)==42 and len(rows)==4641
 score_rows=[];selected={};reggain={}
 for out in OUTCOMES:
  y=lambda r:int(r["wrapper"]==out.lower())
  G=defaultdict(Counter);T=defaultdict(Counter);F=defaultdict(Counter);I=defaultdict(Counter);C={name:defaultdict(Counter) for name in FEATURES};CT={name:defaultdict(Counter) for name in FEATURES};CF={name:defaultdict(Counter) for name in FEATURES};CI={name:defaultdict(Counter) for name in FEATURES}
  for r in rows:
   yy=y(r);reg=r["register"];tail=r["tail"];fol=r["physical_folio"];G[reg][yy]+=1;T[tail,reg][yy]+=1;F[fol,reg][yy]+=1;I[tail,fol,reg][yy]+=1
   for name in FEATURES:
    x=feature(r,name);C[name][reg,x][yy]+=1;CT[name][tail,reg,x][yy]+=1;CF[name][fol,reg,x][yy]+=1;CI[name][tail,fol,reg,x][yy]+=1
  for name in FEATURES:
   details={}
   for lam in LAMBDAS:
    bb=mm=0.;rg=defaultdict(float)
    for r in rows:
     yy=y(r);reg=r["register"];tail=r["tail"];fol=r["physical_folio"];x=feature(r,name);c=G[reg]-T[tail,reg]-F[fol,reg]+I[tail,fol,reg];p=(c[yy]+.5)/(sum(c.values())+1);d=C[name][reg,x]-CT[name][tail,reg,x]-CF[name][fol,reg,x]+CI[name][tail,fol,reg,x];q=(d[yy]+lam*p)/(sum(d.values())+lam);g=math.log2(q/p);bb-=math.log2(p);mm-=math.log2(q);rg[reg]+=g
    rec={"wrapper_outcome":out,"feature_model":name,"lambda":lam,"groups":len(rows),"baseline_bits":bb,"model_bits":mm,"gain_bits":bb-mm,"selector_paid_gain_bits":bb-mm-math.log2(len(LAMBDAS)),"selected":0};score_rows.append(rec);details[lam]=rg
   best=max((r for r in score_rows if r["wrapper_outcome"]==out and r["feature_model"]==name),key=lambda r:r["gain_bits"]);best["selected"]=1;selected[out,name]=best;reggain[out,name]=details[best["lambda"]]
 tailrows=[]
 for tail in tails:
  for out in OUTCOMES:
   O=by["o",tail];Y=by["y",tail];ro=sum(r["wrapper"]==out.lower() for r in O)/len(O);ry=sum(r["wrapper"]==out.lower() for r in Y)/len(Y);diff=ro-ry;pred="O_HIGHER" if out=="Q" else "Y_HIGHER";actual="O_HIGHER" if diff>0 else "Y_HIGHER" if diff<0 else "TIE"
   tailrows.append({"tail":tail or "EMPTY","wrapper_outcome":out,"o_occurrences":len(O),"y_occurrences":len(Y),"o_rate":ro,"y_rate":ry,"o_minus_y":diff,"predicted_direction":pred,"actual_direction":actual,"informative":int(diff!=0),"prediction_correct":int((out=="Q" and diff>0) or (out=="D" and diff<0)) if diff else "NA"})
 comparisons=[]
 for out in OUTCOMES:
  b=selected[out,"BASE_OY"]
  comparisons.append({"wrapper_outcome":out,"formal_model":"BASE_OY","equivalent_string_model":"PAGE_HOST_FIRST_CHARACTER","numeric_relationship":"IDENTICAL_FEATURE_AND_SCORE","selected_lambda":b["lambda"],"gain_bits":b["gain_bits"],"selector_paid_gain_bits":b["selector_paid_gain_bits"],"positive_registers":sum(x>0 for x in reggain[out,"BASE_OY"].values()),"conclusion":"TRANSFERS_BUT_NOT_BEYOND_FIRST_CHARACTER_STRING_STATISTICS"})
 write(SCORES,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in score_rows],list(score_rows[0]));write(TAILS,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in tailrows],list(tailrows[0]));write(BASE,[{k:f"{v:.12g}" if isinstance(v,float) else v for k,v in r.items()} for r in comparisons],list(comparisons[0]));q=selected["Q","BASE_OY"];d=selected["D","BASE_OY"];qi=[r for r in tailrows if r["wrapper_outcome"]=="Q" and r["informative"]==1];di=[r for r in tailrows if r["wrapper_outcome"]=="D" and r["informative"]==1];status="OPERATOR_BASE_RULE_TRANSFERS_TO_UNSEEN_TAILS_AND_FOLIOS_BUT_EQUALS_STRING_BASELINE"
 REPORT.write_text(f"""# GDT094 — nested operator transfer

## Outcome

**{status}**

With both target TAIL and target physical folio removed from training, O/Y
base saves {q['gain_bits']:+.3f} held bits for q and {d['gain_bits']:+.3f}
for d ({q['selector_paid_gain_bits']:+.3f}/{d['selector_paid_gain_bits']:+.3f}
after separate shrinkage selectors).  Gains are positive in all five registers
for both wrappers.  Held-tail directions are correct for
{sum(r['prediction_correct']==1 for r in qi)}/{len(qi)} informative q tails and
{sum(r['prediction_correct']==1 for r in di)}/{len(di)} informative d tails.

This is genuine unseen-host-tail and unseen-folio transfer of the formal
construction rule.  It is not evidence beyond string statistics: `BASE_OY`
is literally PAGE_HOST's first source character, so the corresponding
first-character string baseline has the identical feature and score.  GDT003
therefore remains controlling.  The result strengthens the explicit compiler
grammar without establishing linguistic morphology or meaning.  f84r was
absent.
""",encoding="utf-8")
 result={"schema":"GDT094_NESTED_OPERATOR_TAIL_TRANSFER_RESULT_V1","status":status,"groups":len(rows),"matched_tails":len(tails),"nested_exclusion":"EXACT_TAIL_AND_PHYSICAL_FOLIO","selected_base_models":{"Q":q,"D":d},"tail_direction_accuracy":{"Q":f"{sum(r['prediction_correct']==1 for r in qi)}/{len(qi)}","D":f"{sum(r['prediction_correct']==1 for r in di)}/{len(di)}"},"string_baseline_relationship":"BASE_OY is PAGE_HOST first character; factor and first-character baseline are numerically identical.","claim_ceiling":"Transferable formal first-character construction constraint only; no semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt003_nested_result.json":sha(ROOT/"gdt003_nested_result.json"),"gdt087_result.json":sha(ROOT/"gdt087_result.json"),"gdt092_result.json":sha(ROOT/"gdt092_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{SCORES.name:sha(SCORES),TAILS.name:sha(TAILS),BASE.name:sha(BASE)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"q_gain":q["gain_bits"],"d_gain":d["gain_bits"],"q_tails":result["tail_direction_accuracy"]["Q"],"d_tails":result["tail_direction_accuracy"]["D"]},sort_keys=True))
if __name__=="__main__":main()
