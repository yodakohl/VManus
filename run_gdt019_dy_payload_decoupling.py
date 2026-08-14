#!/usr/bin/env python3
"""Held-folio DY payload to next-state dependency screen."""
from __future__ import annotations

import csv, hashlib, json, math
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent; ALPHA=.5
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(n,rows):
 rows=list(rows)
 with (ROOT/n).open("w",encoding="utf-8",newline="")as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def core(h):
 for x in("ar","al","ol","ed","kal"):
  if x in h:return x.upper()
 return"OTHER"
def main():
 inv=read("gdt016_group_state_inventory.tsv");assert len(inv)==15592 and not any(r["locus"].startswith("f84r")for r in inv)
 by=defaultdict(list)
 for r in inv:by[r["locus"]].append(r)
 events=[]
 for line in by.values():
  line.sort(key=lambda r:int(r["group_index"]))
  for i in range(1,len(line)):
   p,r=line[i-1],line[i]
   if p["record_state"]!="DY_RESOLUTION":continue
   pos=min(3,int(((int(r["group_index"])-1)/(int(r["group_count"])-1))*4));h=p["residual_host"];c=core(h)
   events.append({"folio":r["physical_folio"],"position":pos,"next":r["record_state"],"Q_FLAG":int(p["stripped_prefix"]=="q"),"PREFIX_CLASS":p["stripped_prefix"],"HAS_CANDIDATE_CORE":int(c!="OTHER"),"CORE_CLASS":c,"LONG_HOST":int(len(h)>=4),"HOST_LENGTH_BIN":min(5,len(h)),"FAMILY_INITIAL":p["family_surface"][0],"EXACT_FAMILY":p["family_surface"],"EXACT_HOST":h})
 assert len(events)==2344
 feature_names=("POSITION_ONLY","Q_FLAG","PREFIX_CLASS","HAS_CANDIDATE_CORE","CORE_CLASS","LONG_HOST","HOST_LENGTH_BIN","FAMILY_INITIAL","EXACT_FAMILY","EXACT_HOST")
 targets={"NEXT_STATE":lambda e:e["next"],"NEXT_Q":lambda e:int(e["next"]=="Q_OUTER_STATE"),"NEXT_OT_LOCAL":lambda e:int(e["next"].startswith("OT_")),"NEXT_DY":lambda e:int(e["next"]=="DY_RESOLUTION"),"NEXT_CARRIER":lambda e:int(e["next"]=="CARRIER_STATE")}
 folios=sorted({e["folio"]for e in events});rows=[]
 for target_name,target in targets.items():
  classes=sorted({target(e)for e in events});K=len(classes);scores={}
  for feature in feature_names:
   total=0.;positive=0
   for held in folios:
    counts=defaultdict(Counter);totals=Counter()
    for e in events:
     if e["folio"]==held:continue
     ctx=(e["position"],)if feature=="POSITION_ONLY"else(e["position"],e[feature]);counts[ctx][target(e)]+=1;totals[ctx]+=1
    b=0.
    for e in events:
     if e["folio"]!=held:continue
     ctx=(e["position"],)if feature=="POSITION_ONLY"else(e["position"],e[feature]);b-=math.log2((counts[ctx][target(e)]+ALPHA)/(totals[ctx]+ALPHA*K))
    total+=b
   scores[feature]=total
  base=scores["POSITION_ONLY"]
  for feature in feature_names:
   levels=1 if feature=="POSITION_ONLY"else len({e[feature]for e in events});extra=0 if feature=="POSITION_ONLY"else 4*(levels-1)*(K-1);penalty=extra/2*math.log2(len(events));raw=base-scores[feature]
   rows.append({"target":target_name,"feature":feature,"target_classes":K,"feature_levels":levels,"held_bits":f"{scores[feature]:.12f}","position_baseline_bits":f"{base:.12f}","raw_gain_bits":f"{raw:.12f}","selector_paid_gain_bits":f"{raw-math.log2(len(feature_names)):.12f}","bic_extra_parameters":extra,"bic_penalty_bits":f"{penalty:.12f}","bic_net_gain_bits":f"{raw-penalty:.12f}","claim_state":"EXPLORATORY_PAYLOAD_DEPENDENCY_SCREEN"})
 write("gdt019_payload_dependency_models.tsv",rows)
 best={}
 for target in targets:
  z=[r for r in rows if r["target"]==target and r["feature"]!="POSITION_ONLY"];best[target]=max(z,key=lambda r:float(r["raw_gain_bits"]))
 any_bic=any(float(r["bic_net_gain_bits"])>0 for r in rows if r["feature"]!="POSITION_ONLY")
 status="DY_PAYLOAD_NEXT_STATE_DECOUPLED_AT_TESTED_RESOLUTION"if not any_bic else"DY_PAYLOAD_CONTINUATION_LEAD"
 lines=[]
 for target,r in best.items():lines.append(f"- `{target}`: best raw addition `{r['feature']}` gains {float(r['raw_gain_bits']):+.3f} bits; BIC-net {float(r['bic_net_gain_bits']):+.3f} bits.")
 report=f"""# GDT019 DY-payload continuation report

Status: **{status.replace('_',' ')}**

The presence of DY predicts the next formal state, but the tested payload
inside the DY-bearing group does not.  Across 2,344 post-DY boundaries and
{len(folios)} held physical folios, no prefix, host, length, family-initial, exact-family, or
exact-host addition beats the position baseline after its parameter cost.

"""+"\n".join(lines)+f"""

The two largest raw binary gains are only about seven bits: candidate-core
presence for next-Q and long-host status for next-carrier.  Each needs four
additional binary parameters and loses after the approximately
{4/2*math.log2(len(events)):.2f}-bit BIC penalty, even before the ten-model
selector.  Exact host and exact family are substantially worse out of folio.

This suggests a layered generator: a DY checkpoint carries a local payload,
while DY itself—not the identity of that payload—licenses the next transition.
That is compatible with an abbreviated technical register in which content
and control are partly separated.  It is also compatible with a nonsemantic
templatic source process, so it is not meaning evidence by itself.

The result is limited to the tested low-capacity features and next-state
targets.  f84r was absent from the sole input and was not opened, retained,
joined, or scored.  No morpheme, word, syntax, sound, language, plaintext,
meaning, or translation is confirmed.
""";(ROOT/"GDT019_DY_PAYLOAD_DECOUPLING_REPORT.md").write_text(report)
 outputs=("gdt019_payload_dependency_models.tsv","GDT019_DY_PAYLOAD_DECOUPLING_REPORT.md");inputs=("gdt016_group_state_inventory.tsv","gdt018_result.json","GDT019_DY_PAYLOAD_DECOUPLING_METHOD.md")
 result={"schema":"GDT019_DY_PAYLOAD_DECOUPLING_RESULT_V1","status":status,"events":len(events),"physical_folios":len(folios),"features":list(feature_names),"targets":list(targets),"best_raw_models":best,"any_bic_positive":any_bic,"f84r":{"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Low-capacity checkpoint-payload/next-state decoupling only; no morpheme, word, syntax, sound, language, plaintext, meaning, or translation.","inputs":{n:sha(ROOT/n)for n in inputs},"implementation":{"run_gdt019_dy_payload_decoupling.py":sha(Path(__file__))},"outputs":{n:sha(ROOT/n)for n in outputs}};result["result_content_sha256"]=csha(result);(ROOT/"gdt019_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"best":best},sort_keys=True))
if __name__=="__main__":main()
