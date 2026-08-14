#!/usr/bin/env python3
"""Independent retained-corpus validator for GDT014."""
from __future__ import annotations
import csv,hashlib,json,random
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RES=ROOT/"gdt014_result.json";VAL=ROOT/"gdt014_validation.json";PERMS=20000
VARIANTS=("ar","oar","otar","al","oal","otal","ol","ool","otol");CONTRASTS=(("ar","oar"),("ar","otar"),("oar","otar"),("al","otal"),("ol","otol"))
def read(name):
 with (ROOT/name).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def pos(r):return (int(r["group_index"])-1)/(int(r["group_count"])-1)if int(r["group_count"])>1 else .5
def effect(parts):
 num=den=0.
 for _,a,b in parts:w=len(a)*len(b)/(len(a)+len(b));num+=w*(sum(b)/len(b)-sum(a)/len(a));den+=w
 return num/den if den else 0.
def main():
 checks=[];result=json.loads(RES.read_text());copy=dict(result);digest=copy.pop("result_content_sha256");checks.extend([("schema",result["schema"]=="GDT014_LOCAL_REFERENCE_MICROGRAMMAR_RESULT_V1"),("content",digest==csha(copy))])
 for part in("inputs","implementation","outputs"):
  for name,value in result[part].items():checks.append((part+":"+name,sha(ROOT/name)==value))
 profiles=read("gdt014_core_ladder_profiles.tsv");tests=read("gdt014_position_tests.tsv");ladders=read("gdt014_complete_ladders.tsv");examples=read("gdt014_context_examples.tsv")
 # Reconstruct the retained corpus from the committed GDT013 prose propagation source function output contract via source tables is checked by exact profile totals and examples.
 from run_gdt013_latent_role_propagation import all_strict_groups
 rows=[r for r in all_strict_groups()if r["grammar_scope"]=="CONFIRMED_PROSE"]
 checks.extend([("corpus",len(rows)==result["strict_prose_groups"]==15592),("f84",not any(r["locus"].startswith("f84r")for r in rows)and result["f84r"]=={"retained":False,"joined":False,"scored":False}),("profile_grid",{r["variant"]for r in profiles}=={x.upper()for x in VARIANTS})])
 pmap={r["variant"].lower():r for r in profiles}
 for v in VARIANTS:
  x=[r for r in rows if r["residual_host"]==v];pre=Counter(r["stripped_prefix"]for r in x);p=pmap[v]
  checks.append(("profile:"+v,len(x)==int(p["prose_groups"])and len({r["physical_folio"]for r in x})==int(p["physical_folios"])and pre["q"]==int(p["q_prefix"])and sum(int(r["dy_closure"])for r in x)==int(p["dy_closure"])and p["core"]==v[-2:]))
 stored={(r["form_a"],r["form_b"]):r for r in tests}
 for j,(a,b)in enumerate(CONTRASTS,1):
  by=defaultdict(lambda:[[],[]])
  for r in rows:
   if r["residual_host"]==a:by[r["page"]][0].append(pos(r))
   if r["residual_host"]==b:by[r["page"]][1].append(pos(r))
  parts=[(p,x,y)for p,(x,y)in sorted(by.items())if x and y];obs=effect(parts);rng=random.Random(14000+j);ext=0
  for _ in range(PERMS):
   z=[]
   for page,x,y in parts:values=x+y;rng.shuffle(values);z.append((page,values[:len(x)],values[len(x):]))
   ext+=abs(effect(z))>=abs(obs)-1e-15
  pv=(ext+1)/(PERMS+1);s=stored[(a,b)];checks.append(("test:"+a+":"+b,abs(obs-float(s["position_effect_b_minus_a"]))<6e-13 and abs(pv-float(s["local_p"]))<6e-13 and len(parts)==int(s["shared_pages"])))
 counts=Counter(r["residual_host"]for r in rows);bases={h for h in counts if"o"+h in counts and"ot"+h in counts};checks.extend([("ladders",len(ladders)==result["complete_ladders"]==len(bases)==52 and{r["base_host"]for r in ladders}==bases),("q_counts",result["q_on_bare_ar_al"]==0 and result["q_on_otar_otal"]==62),("examples",len(examples)==sum(min(10,counts[v])for v in VARIANTS)==76 and all(r["residual_host"]==r["variant"].lower()for r in examples)),("ledger",(ROOT/"GDT002_YOLO_LEDGER.tsv").read_text().count("GDT014_CKPT001")==1)])
 report=(ROOT/"GDT014_LOCAL_REFERENCE_MICROGRAMMAR_REPORT.md").read_text().lower();checks.extend([("orthotactic_caveat","qo"in report and"not independent"in report and"semantic evidence"in report),("claim",all(x in report for x in("no word","translation","f84r was not retained")))])
 failures=[n for n,ok in checks if not ok];v={"schema":"GDT014_LOCAL_REFERENCE_MICROGRAMMAR_VALIDATION_V1","status":"PASS"if not failures else"FAIL","checks":len(checks),"failures":failures,"result_sha256":sha(RES),"validator_sha256":sha(Path(__file__)),"scope":"Independent retained-corpus profiles, five deterministic within-page permutation tests, 52 complete ladders, q/DY counts, examples, f84 exclusion, hashes, ledger, and claim ceiling. Reuses the independently validated GDT013 strict-group loader."};VAL.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n");print(json.dumps(v,sort_keys=True));
 if failures:raise SystemExit(1)
if __name__=="__main__":main()
