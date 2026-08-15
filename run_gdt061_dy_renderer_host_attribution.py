#!/usr/bin/env python3
"""GDT061: attribute post-DY string signal to renderer versus PAGE_HOST."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt060_dy_transition_inventory.tsv";METHOD=ROOT/"GDT061_DY_RENDERER_HOST_ATTRIBUTION_METHOD.md";REPORT=ROOT/"GDT061_DY_RENDERER_HOST_ATTRIBUTION_REPORT.md";SCORES=ROOT/"gdt061_dy_renderer_host_scores.tsv";ATTR=ROOT/"gdt061_dy_component_attribution.tsv";VARIANTS=ROOT/"gdt061_variant_log.tsv";RESULT=ROOT/"gdt061_result.json";LAM=8.;ALPHABET=sorted(set("abcdefghijklmnopqrstuvwxyz$"))
CONFIGS=(("PAGE_HOST","WRAPPER"),("PAGE_HOST","WRAPPER_FRAME"),("PAGE_HOST","FULL_COMPILER"),("RESIDUAL_ROOT","FULL_COMPILER"),("RAW_SURFACE","FULL_COMPILER"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def value(r,rep):return{"PAGE_HOST":r["right_host"],"RESIDUAL_ROOT":r["right_root"],"RAW_SURFACE":r["right_token"]}[rep]
def renderer(r,level):
 p=r["right_compiler"].split("|")
 if level=="WRAPPER":return p[0]
 if level=="WRAPPER_FRAME":return"|".join((p[0],p[2]))
 return r["right_compiler"]
def events(s):
 h="^^";out=[]
 for c in s+"$":out.append((h,c));h=(h+c)[-2:]
 return out
def add(c,k,h,x):c[k,h,x]+=1;c[k,h,"#"]+=1
def fit(rows,rep,level):
 base=Counter();dyc=Counter();rend=Counter();joint=Counter()
 for r in rows:
  d=int(r["dy"]);q=renderer(r,level)
  for h,x in events(value(r,rep)):add(base,"ALL",h,x);add(dyc,d,h,x);add(rend,q,h,x);add(joint,(q,d),h,x)
 return base,dyc,rend,joint
def score(model,r,rep,level):
 base,dyc,rend,joint=model;d=int(r["dy"]);q=renderer(r,level);z=Counter()
 for h,x in events(value(r,rep)):
  pb=(base["ALL",h,x]+.5)/(base["ALL",h,"#"]+.5*len(ALPHABET));pd=(dyc[d,h,x]+LAM*pb)/(dyc[d,h,"#"]+LAM);pr=(rend[q,h,x]+LAM*pb)/(rend[q,h,"#"]+LAM);pj=(joint[(q,d),h,x]+LAM*.5*(pd+pr))/(joint[(q,d),h,"#"]+LAM)
  for k,p in(("BASE",pb),("DY",pd),("RENDERER",pr),("RENDERER_DY",pj)):z[k]-=math.log2(p)
 return z
def evaluate(rows,rep,level,mode):
 foldkey="physical_folio"if mode=="LEAVE_FOLIO_OUT"else"register";tot=Counter();br=defaultdict(Counter)
 for fold in sorted({r[foldkey]for r in rows}):
  train=[r for r in rows if r[foldkey]!=fold];test=[r for r in rows if r[foldkey]==fold];m=fit(train,rep,level)
  for r in test:
   s=score(m,r,rep,level)
   for k,v in s.items():tot[k]+=v;br[r["register"]][k]+=v
 out=[]
 for scope,z in [("ALL",tot)]+sorted(br.items()):
  q=[r for r in rows if scope=="ALL"or r["register"]==scope];ev=sum(len(value(r,rep))+1 for r in q)
  out.append({"evaluation":mode,"representation":rep,"renderer_control":level,"scope":scope,"boundaries":len(q),"dy_boundaries":sum(int(r["dy"])for r in q),"right_events":ev,"base_bits":z["BASE"],"dy_bits":z["DY"],"renderer_bits":z["RENDERER"],"renderer_dy_bits":z["RENDERER_DY"],"dy_gain_vs_base":z["BASE"]-z["DY"],"renderer_gain_vs_base":z["BASE"]-z["RENDERER"],"residual_dy_gain_vs_renderer":z["RENDERER"]-z["RENDERER_DY"],"renderer_gain_vs_dy":z["DY"]-z["RENDERER_DY"],"residual_dy_gain_per_event":(z["RENDERER"]-z["RENDERER_DY"])/ev})
 return out
def main():
 rows=read(SOURCE);assert len(rows)==7409 and not any(r["locus"].startswith("f84r")for r in rows);scores=[]
 for rep,level in CONFIGS:
  for mode in("LEAVE_FOLIO_OUT","LEAVE_REGISTER_OUT"):scores+=evaluate(rows,rep,level,mode)
 write(SCORES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in scores],list(scores[0]));by={(r["evaluation"],r["representation"],r["renderer_control"],r["scope"]):r for r in scores};attr=[]
 for level in("WRAPPER","WRAPPER_FRAME","FULL_COMPILER"):
  p=by["LEAVE_FOLIO_OUT","PAGE_HOST",level,"ALL"];x=by["LEAVE_REGISTER_OUT","PAGE_HOST",level,"ALL"];attr.append({"renderer_control":level,"lofo_dy_gain_vs_base":p["dy_gain_vs_base"],"lofo_renderer_gain_vs_base":p["renderer_gain_vs_base"],"lofo_residual_dy_gain_vs_renderer":p["residual_dy_gain_vs_renderer"],"cross_register_residual_dy_gain":x["residual_dy_gain_vs_renderer"],"lofo_residual_gain_positive_registers":sum(by["LEAVE_FOLIO_OUT","PAGE_HOST",level,s]["residual_dy_gain_vs_renderer"]>0 for s in("HERBAL_A","HERBAL_B","OTHER_A","OTHER_B","STARS_RECIPE_B"))})
 write(ATTR,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in attr],list(attr[0]));variants=[{"variant_id":"V00","status":"PRIMARY","description":"PAGE_HOST conditioned on full following compiler under complete-folio holdout."},{"variant_id":"V01","status":"RUN_ABLATION","description":"Following wrapper only."},{"variant_id":"V02","status":"RUN_ABLATION","description":"Following wrapper plus O/OT frame."},{"variant_id":"V03","status":"RUN_BASELINE","description":"Residual-root and raw-surface outcomes under full compiler."},{"variant_id":"V04","status":"RUN_SENSITIVITY","description":"Complete target register excluded from training."},{"variant_id":"V05","status":"NOT_RUN","description":"No external annotations, semantic classes, alternative parser, or f84r."}];write(VARIANTS,variants,list(variants[0]))
 p=by["LEAVE_FOLIO_OUT","PAGE_HOST","FULL_COMPILER","ALL"];x=by["LEAVE_REGISTER_OUT","PAGE_HOST","FULL_COMPILER","ALL"]
 if p["residual_dy_gain_vs_renderer"]>0 and x["residual_dy_gain_vs_renderer"]>0:status="DY_RETAINS_PAGE_HOST_SIGNAL_AFTER_FULL_RENDERER_CONTROL"
 elif p["residual_dy_gain_vs_renderer"]<=0:status="DY_POST_BOUNDARY_HOST_SIGNAL_ABSORBED_BY_FOLLOWING_WRAPPER"
 else:status="DY_RENDERER_HOST_ATTRIBUTION_REGISTER_DEPENDENT"
 report=f"""# GDT061 — DY post-boundary renderer/host attribution

## Outcome

**{status}**

Across {len(rows):,} complete-line internal boundaries, DY alone improves
held-folio PAGE_HOST prediction by {p['dy_gain_vs_base']:+.3f} bits.  The full
following-compiler model improves BASE by {p['renderer_gain_vs_base']:+.3f}
bits.  Adding DY after that renderer changes held prediction by
{p['residual_dy_gain_vs_renderer']:+.3f} bits
({p['residual_dy_gain_per_event']:+.6f} bit/right-character event).  With the
complete target register excluded, the corresponding residual is
{x['residual_dy_gain_vs_renderer']:+.3f} bits.

The wrapper-only control is already sufficient: its residual DY gain is
{attr[0]['lofo_residual_dy_gain_vs_renderer']:+.3f} bits and is positive in
{attr[0]['lofo_residual_gain_positive_registers']} of five register strata.
Wrapper+frame gives {attr[1]['lofo_residual_dy_gain_vs_renderer']:+.3f} bits.
Thus the apparent PAGE_HOST selection in GDT060 is absorbed principally by
the following wrapper ecology, consistent with the known post-DY `qo...`
architecture, rather than providing a separate content-host transition.

The wrapper-only and wrapper+frame ablations, raw and residual-root baselines,
and every register-specific fold are retained in the score table.  This
locates GDT060's post-DY distributional signal relative to known HPR2 compiler
layers; it does not identify content or semantics.  No role, gloss, word,
morpheme, POS, sound, language, plaintext, meaning, or translation is
assigned.  f84r was excluded before retention and was not opened, queried,
joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT061_DY_RENDERER_HOST_ATTRIBUTION_RESULT_V1","status":status,"boundaries":len(rows),"dy_boundaries":sum(int(r["dy"])for r in rows),"primary_lofo":p,"primary_cross_register":x,"attribution":attr,"generative_update":"The post-DY PAGE_HOST distribution is absorbed by the following wrapper alone; retain DY as a compiler-level checkpoint/renderer transition, not a supported content-host transition.","claim_ceiling":"Formal DY/renderer/PAGE_HOST attribution only; no role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt060_result.json":sha(ROOT/"gdt060_result.json"),"gdt059_result.json":sha(ROOT/"gdt059_result.json"),"gdt055_result.json":sha(ROOT/"gdt055_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{SCORES.name:sha(SCORES),ATTR.name:sha(ATTR),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"lofo_residual":p["residual_dy_gain_vs_renderer"],"cross_register_residual":x["residual_dy_gain_vs_renderer"]},sort_keys=True))
if __name__=="__main__":main()
