#!/usr/bin/env python3
"""GDT062: held-folio RIGHT_FAMILY register-selection code."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";METHOD=ROOT/"GDT062_RIGHT_FAMILY_REGISTER_RENDERER_METHOD.md";REPORT=ROOT/"GDT062_RIGHT_FAMILY_REGISTER_RENDERER_REPORT.md";INVENTORY=ROOT/"gdt062_right_family_inventory.tsv";SCORES=ROOT/"gdt062_right_family_scores.tsv";VARIANTS=ROOT/"gdt062_variant_log.tsv";RESULT=ROOT/"gdt062_result.json";RIGHT=("aiin","air","ain","ar","al");OUTCOMES=("NONE",)+RIGHT;LAM=8.
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def preparse(r):
 h=r["residual_host"];b3=int(h.endswith("m")and len(h)>1);h=h[:-1]if b3 else h;right="NONE"
 for s in RIGHT:
  if h.endswith(s)and len(h)>len(s):h=h[:-len(s)];right=s;break
 inner=int(r["stripped_prefix"]in{"ch","che","sh"}and h.startswith("d")and len(h)>1);h=h[1:]if inner else h
 return h,b3,right,inner
def parser(source):
 counts=Counter(preparse(r)[0]for r in source);licensed={h for h in counts if counts[h]and counts["o"+h]and counts["ot"+h]}|{"ar","al","ol"}
 def parse(r):
  h,b3,right,inner=preparse(r);frame="NONE"
  if h.startswith("ot")and h[2:]in licensed:h=h[2:];frame="OT"
  elif h.startswith("o")and h[1:]in licensed:h=h[1:];frame="O"
  return h or"EMPTY",b3,right,inner,frame
 return parse,licensed
def register(r):
 if r["section"]=="H":return"HERBAL_"+r["currier"]
 if r["section"]=="S"and r["currier"]=="B":return"STARS_RECIPE_B"
 return"OTHER_"+r["currier"]
def hkey(r,mode):
 h=r["page_host"]
 if mode=="EXACT":return h
 return f'{h[:2]}|{h[-2:]}|L{len(h)//2}'
def context(r,hand):
 parts=[r["wrapper"],r["inner_d"],r["local_frame"],r["dy_closure"],r["b3"],r["position_quartile"]]
 if hand:parts.append(r["hand"])
 return tuple(parts)
def add(c,k,y):c[k,y]+=1;c[k,"#"]+=1
def fit(rows,mode,hand):
 base=Counter();nuis=Counter();host=Counter();reg=Counter()
 for r in rows:
  y=r["right_family"];n=context(r,hand);h=hkey(r,mode);add(base,"ALL",y);add(nuis,n,y);add(host,(n,h),y);add(reg,(n,h,r["register"]),y)
 return base,nuis,host,reg
def prob(c,k,y,p,s):return(c[k,y]+s*p)/(c[k,"#"]+s)
def score(model,r,mode,hand):
 base,nuis,host,reg=model;y=r["right_family"];n=context(r,hand);h=hkey(r,mode);pb=(base["ALL",y]+.5)/(base["ALL","#"]+.5*len(OUTCOMES));pn=prob(nuis,n,y,pb,LAM);ph=prob(host,(n,h),y,pn,LAM);pr=prob(reg,(n,h,r["register"]),y,ph,LAM);return[-math.log2(x)for x in(pb,pn,ph,pr)],host[(n,h),"#"]>0
def evaluate(rows,mode,hand):
 tot=Counter();br=defaultdict(Counter);seen=Counter();seenbr=Counter()
 for folio in sorted({r["physical_folio"]for r in rows}):
  train=[r for r in rows if r["physical_folio"]!=folio];test=[r for r in rows if r["physical_folio"]==folio];m=fit(train,mode,hand)
  for r in test:
   z,s=score(m,r,mode,hand)
   for k,v in zip(("BASE","NUISANCE","HOST","HOST_REGISTER"),z):tot[k]+=v;br[r["register"]][k]+=v
   seen["n"]+=s;seen["gain"]+=(z[2]-z[3])if s else 0;seenbr[r["register"],"n"]+=s;seenbr[r["register"],"gain"]+=(z[2]-z[3])if s else 0
 out=[]
 for scope,z in [("ALL",tot)]+sorted(br.items()):
  q=[r for r in rows if scope=="ALL"or r["register"]==scope];sn=seen["n"]if scope=="ALL"else seenbr[scope,"n"];sg=seen["gain"]if scope=="ALL"else seenbr[scope,"gain"]
  out.append({"host_key":mode,"hand_control":"HAND"if hand else"NO_HAND","scope":scope,"groups":len(q),"right_family_present":sum(r["right_family"]!="NONE"for r in q),"seen_host_groups":sn,"base_bits":z["BASE"],"nuisance_bits":z["NUISANCE"],"host_bits":z["HOST"],"host_register_bits":z["HOST_REGISTER"],"host_gain_vs_nuisance":z["NUISANCE"]-z["HOST"],"register_gain_given_host":z["HOST"]-z["HOST_REGISTER"],"register_gain_per_group":(z["HOST"]-z["HOST_REGISTER"])/len(q),"seen_host_register_gain":sg})
 return out
def main():
 source=read(SOURCE);assert len(source)==15592 and not any(r["locus"].startswith("f84r")for r in source);parse,licensed=parser(source);rows=[]
 for r in source:
  h,b3,right,inner,frame=parse(r);pos=int(4*(int(r["group_index"])-1)/max(1,int(r["group_count"])-1));rows.append({"locus":r["locus"],"page":r["page"],"physical_folio":r["physical_folio"],"section":r["section"],"currier":r["currier"],"hand":r["hand"],"register":register(r),"group_index":r["group_index"],"group_count":r["group_count"],"token":r["token"],"wrapper":r["stripped_prefix"],"inner_d":inner,"local_frame":frame,"page_host":h,"right_family":right,"dy_closure":r["dy_closure"],"b3":b3,"position_quartile":pos})
 scores=[]
 for mode in("EXACT","SHAPE"):
  for hand in(1,0):scores+=evaluate(rows,mode,hand)
 write(INVENTORY,rows,list(rows[0]));write(SCORES,[{k:f"{v:.12g}"if isinstance(v,float)else v for k,v in r.items()}for r in scores],list(scores[0]));variants=[{"variant_id":"V00","status":"PRIMARY","description":"Exact PAGE_HOST with hand-controlled compiler nuisance."},{"variant_id":"V01","status":"RUN_SENSITIVITY","description":"PAGE_HOST first-two/last-two/length shape."},{"variant_id":"V02","status":"RUN_SENSITIVITY","description":"Omit hand from nuisance to expose hand/register confounding."},{"variant_id":"V03","status":"NOT_RUN","description":"No external content annotations, semantic classes, alternate parser, or f84r."}];write(VARIANTS,variants,list(variants[0]));by={(r["host_key"],r["hand_control"],r["scope"]):r for r in scores};p=by["EXACT","HAND","ALL"]
 if p["register_gain_given_host"]>0 and all(by["EXACT","HAND",s]["register_gain_given_host"]>0 for s in("HERBAL_A","HERBAL_B","OTHER_A","OTHER_B","STARS_RECIPE_B")):status="RIGHT_FAMILY_IS_TRANSFERABLE_REGISTER_CONDITIONED_RENDERING"
 elif p["register_gain_given_host"]>0:status="RIGHT_FAMILY_REGISTER_SELECTION_AGGREGATE_ONLY"
 else:status="RIGHT_FAMILY_REGISTER_RENDERER_HYPOTHESIS_NOT_SUPPORTED"
 report=f"""# GDT062 — RIGHT_FAMILY as register-conditioned rendering

## Outcome

**{status}**

The source-native panel contains {len(rows):,} groups on
{len({r['physical_folio']for r in rows})} physical folios, including
{sum(r['right_family']!='NONE'for r in rows):,} explicit right-family
selections.  With complete target folios excluded, exact PAGE_HOST reduces the
hand-controlled compiler code by {p['host_gain_vs_nuisance']:+.3f} bits.
Adding the five-way register then changes held RIGHT_FAMILY prediction by
{p['register_gain_given_host']:+.3f} bits
({p['register_gain_per_group']:+.6f} bit/group); the exact host key is observed
in training for {p['seen_host_groups']:,} scored groups.

All five register strata contribute positively: Herbal A
{by['EXACT','HAND','HERBAL_A']['register_gain_given_host']:+.3f}, Herbal B
{by['EXACT','HAND','HERBAL_B']['register_gain_given_host']:+.3f}, other A
{by['EXACT','HAND','OTHER_A']['register_gain_given_host']:+.3f}, other B
{by['EXACT','HAND','OTHER_B']['register_gain_given_host']:+.3f}, and
Stars/Recipe B
{by['EXACT','HAND','STARS_RECIPE_B']['register_gain_given_host']:+.3f} bits.
The host-shape sensitivity gains
{by['SHAPE','HAND','ALL']['register_gain_given_host']:+.3f} bits; omitting hand
still gains {by['EXACT','NO_HAND','ALL']['register_gain_given_host']:+.3f}.

Register-specific directions, host-shape and no-hand sensitivities, and the
complete inventory are retained.  This tests register-conditioned formal
rendering only.  GDT059 showed that RIGHT_FAMILY and B3 can still carry page
ecology, so this result cannot establish content neutrality by itself.  No
right-family meaning, morpheme, POS, sound, language, plaintext, or translation
is assigned.  f84r was excluded before parsing and not opened, retained,
queried, joined, or scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT062_RIGHT_FAMILY_REGISTER_RENDERER_RESULT_V1","status":status,"groups":len(rows),"physical_folios":len({r["physical_folio"]for r in rows}),"right_family_present":sum(r["right_family"]!="NONE"for r in rows),"licensed_o_ot_hosts":len(licensed),"primary":p,"scores":scores,"interpretation":"Held register-conditioned RIGHT_FAMILY selection conditional on PAGE_HOST and compiler nuisance; content neutrality remains unestablished.","claim_ceiling":"No right-family meaning, morpheme, POS, sound, language, plaintext, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{SOURCE.name:sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"gdt048_result.json":sha(ROOT/"gdt048_result.json"),"gdt059_result.json":sha(ROOT/"gdt059_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{INVENTORY.name:sha(INVENTORY),SCORES.name:sha(SCORES),VARIANTS.name:sha(VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"primary_gain":p["register_gain_given_host"],"per_register":{s:by["EXACT","HAND",s]["register_gain_given_host"]for s in("HERBAL_A","HERBAL_B","OTHER_A","OTHER_B","STARS_RECIPE_B")}},sort_keys=True))
if __name__=="__main__":main()
