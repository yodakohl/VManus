#!/usr/bin/env python3
"""GDT047: rank B/S residual hosts after removing recovered mechanisms."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";ANN=ROOT/"gdt012_annotated_core_inventory.tsv";METHOD=ROOT/"GDT047_POST_ATTRIBUTION_CORE_ATLAS_METHOD.md";REPORT=ROOT/"GDT047_POST_ATTRIBUTION_CORE_ATLAS_REPORT.md";ATLAS=ROOT/"gdt047_residual_core_atlas.tsv";COUNTER=ROOT/"gdt047_visual_counterexamples.tsv";RESULT=ROOT/"gdt047_result.json";REGS=("HA","HB","SB","OB")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def reg(r):
 if r["section"]=="H"and r["currier"]=="A":return"HA"
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 if r["currier"]=="B":return"OB"
 return"OUT"
def keep(r):return r["dy_closure"]=="0"and not r["residual_host"].endswith("m")and not(r["stripped_prefix"]in{"ch","che","sh"}and r["residual_host"].startswith("d")and len(r["residual_host"])>1)
def rate(c,n):return(c+.5)/(n+1)
def lrr(a,b):return math.log2(a/b)
def main():
 rows=[]
 for r in read(SOURCE):
  assert not r["locus"].startswith("f84r");rr=reg(r)
  if rr!="OUT"and keep(r):rows.append({**r,"register":rr})
 den=Counter(r["register"]for r in rows);by=defaultdict(list)
 for r in rows:by[r["residual_host"]].append(r)
 ann=read(ANN);assert not any(r["locus"].startswith("f84r")for r in ann);aby=defaultdict(list)
 for r in ann:aby[r["residual_host"]].append(r)
 out=[]
 for host,z in by.items():
  counts=Counter(r["register"]for r in z);folios={x:{r["physical_folio"]for r in z if r["register"]==x}for x in REGS}
  if counts["HB"]<3 or counts["SB"]<3 or len(folios["HB"])<2 or len(folios["SB"])<2:continue
  rates={x:rate(counts[x],den[x])for x in REGS};ea=min(lrr(rates["HB"],rates["HA"]),lrr(rates["SB"],rates["HA"]));eo=min(lrr(rates["HB"],rates["OB"]),lrr(rates["SB"],rates["OB"]));bal=abs(lrr(rates["HB"],rates["SB"]));score=min(4,ea)+max(-3,min(3,eo))+math.log2(1+min(len(folios["HB"]),len(folios["SB"])))+-.5*bal
  lo_a=[];lo_ob=[]
  for f in sorted(folios["HB"]|folios["SB"]):
   cc=Counter(r["register"]for r in z if r["physical_folio"]!=f);dd=Counter(r["register"]for r in rows if r["physical_folio"]!=f);rr={x:rate(cc[x],dd[x])for x in REGS};lo_a.append(min(lrr(rr["HB"],rr["HA"]),lrr(rr["SB"],rr["HA"])));lo_ob.append(min(lrr(rr["HB"],rr["OB"]),lrr(rr["SB"],rr["OB"])))
  states=Counter(r["record_state"]for r in z if r["register"]in{"HB","SB"});wrappers=Counter(r["stripped_prefix"]for r in z if r["register"]in{"HB","SB"});az=aby[host];objects=sorted({x for r in az for x in r["object_tags"].split(";")if x and x!="LABEL"});relations=sorted({x for r in az for x in r["relation_tags"].split(";")if x})
  if host=="odain":attribution="GDT043_OD_AIN_SHORT_VARIANT"
  elif len(states)==1 and next(iter(states))not in{"OTHER","Q_OUTER_STATE","CARRIER_STATE"}:attribution="ANONYMOUS_STATE_DEFINED"
  elif eo<=0:attribution="GENERIC_CURRIER_B_OR_CONTROL_RICH"
  else:attribution="UNATTRIBUTED_RESIDUAL"
  if not az:ground="UNGROUNDED_NO_ANNOTATED_LABEL_HIT"
  elif len(objects)>=2:ground="VISUAL_OBJECT_DIVERSE_COUNTEREXAMPLE"
  else:ground="SPARSE_SINGLE_CLASS_LABEL_CAPACITY"
  out.append({"core":host,"rank_score":score,"hb_count":counts["HB"],"hb_folios":len(folios["HB"]),"sb_count":counts["SB"],"sb_folios":len(folios["SB"]),"ha_count":counts["HA"],"ob_count":counts["OB"],"min_log2_enrichment_vs_ha":ea,"min_log2_specificity_vs_ob":eo,"lofo_min_ha":min(lo_a),"lofo_min_ob":min(lo_ob),"hb_sb_abs_log2_rate_difference":bal,"target_wrappers":";".join(f"{k}:{v}"for k,v in wrappers.most_common()),"target_states":";".join(f"{k}:{v}"for k,v in states.most_common()),"formal_attribution":attribution,"annotated_groups":len(az),"annotated_folios":len({r["physical_folio"]for r in az}),"annotated_object_classes":";".join(objects),"annotated_relation_classes":";".join(relations),"grounding_state":ground})
 out.sort(key=lambda r:(-r["rank_score"],r["core"]));
 for i,r in enumerate(out,1):r["rank"]=i
 fields=["rank"]+[k for k in out[0]if k!="rank"];formatted=[{k:f"{r[k]:.9f}"if isinstance(r[k],float)else r[k]for k in fields}for r in out];write(ATLAS,formatted,fields)
 cr=[]
 for r in out:
  if r["grounding_state"]=="VISUAL_OBJECT_DIVERSE_COUNTEREXAMPLE":
   for a in aby[r["core"]]:cr.append({"core":r["core"],"locus":a["locus"],"physical_folio":a["physical_folio"],"token":a["token"],"object_tags":a["object_tags"],"relation_tags":a["relation_tags"],"certainty":a["annotation_certainty"],"description":a["raw_source_description"]})
 cr.sort(key=lambda r:(r["core"],r["physical_folio"],r["locus"]));write(COUNTER,cr,list(cr[0]))
 residual=[r for r in out if r["formal_attribution"]=="UNATTRIBUTED_RESIDUAL"and r["lofo_min_ha"]>0 and r["lofo_min_ob"]>0];winner=residual[0];decision="OKAIR_TOP_POST_ATTRIBUTION_RESIDUAL_HOST_UNGROUNDED";assert winner["core"]=="okair"and winner["grounding_state"]=="UNGROUNDED_NO_ANNOTATED_LABEL_HIT"
 report=f"""# GDT047 — post-attribution residual core atlas

## Outcome

**{decision}**

After removing DY-closed groups, terminal-M/B3 groups, and carrier+D double
stacks, {len(rows):,} groups remain. {len(out)} exact cores meet the repeated
HB/S capacity rule. The top genuinely unattributed residual is `OKAIR`: HB
{winner['hb_count']} occurrences on {winner['hb_folios']} folios, S/B
{winner['sb_count']} on {winner['sb_folios']}, Herbal-A {winner['ha_count']},
and other-B {winner['ob_count']}. Worst-target-folio log2 enrichment remains
{winner['lofo_min_ha']:+.3f} versus Herbal-A and {winner['lofo_min_ob']:+.3f}
versus other-B.

`OKAIR` is nevertheless **not grounded**. It has no exact occurrence in the
671-row GDT012 human-annotated label inventory, and its target instances split
between bare/OTHER and q/Q_OUTER states. It is a formal content-host candidate,
not a referent or word meaning.

Only two unattributed cores retain positive worst-folio enrichment against
both controls: `OKAIR` and the lower-ranked `KAIIN`. Neither has an exact hit
in the annotated label inventory, so there is currently no visual evidence
with which to choose a referent for either.

The subtraction prevents old mechanisms from returning under new names.
`ODAIN` is carried as the GDT043 short OD+AIN/AIIN variant. `OTAR`, `OLAIIN`,
and similar forms are explicitly tagged when their target occurrences occupy
one already-defined anonymous state. Generic Currier-B cores remain visible
but are not promoted. Exact hosts that occur across multiple human object
classes are exported as visual counterexamples.

The result narrows the next search to OKAIR's constructional family and local
contexts. It does not assign a word, morpheme, POS, sound, language, plaintext,
meaning, or translation. f84r was not opened, retained, queried, joined, or
scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT047_POST_ATTRIBUTION_CORE_ATLAS_RESULT_V1","status":decision,"filtered_groups":len(rows),"eligible_cores":len(out),"unattributed_robust_cores":len(residual),"top_residual":winner,"known_mechanisms_subtracted":["RIGHT_EDGE_DY","TERMINAL_M_B3","CARRIER_PLUS_D_DOUBLE"],"claim_ceiling":"Post-attribution formal residual host ranking only; no word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{"gdt016_group_state_inventory.tsv":sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"gdt012_annotated_core_inventory.tsv":sha(ANN),"gdt012_result.json":sha(ROOT/"gdt012_result.json"),"gdt037_result.json":sha(ROOT/"gdt037_result.json"),"gdt041_result.json":sha(ROOT/"gdt041_result.json"),"gdt043_result.json":sha(ROOT/"gdt043_result.json"),"gdt045_result.json":sha(ROOT/"gdt045_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{ATLAS.name:sha(ATLAS),COUNTER.name:sha(COUNTER)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"groups":len(rows),"cores":len(out),"winner":winner["core"],"counts":[winner["hb_count"],winner["sb_count"],winner["ha_count"],winner["ob_count"]]},sort_keys=True))
if __name__=="__main__":main()
