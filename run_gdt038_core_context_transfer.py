#!/usr/bin/env python3
"""GDT038: full field-local context comparison for four GDT037 cores."""
from __future__ import annotations
import csv,hashlib,itertools,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv"
METHOD=ROOT/"GDT038_CORE_CONTEXT_TRANSFER_METHOD.md";REPORT=ROOT/"GDT038_CORE_CONTEXT_TRANSFER_REPORT.md"
OCC=ROOT/"gdt038_occurrence_contexts.tsv";CLUSTERS=ROOT/"gdt038_context_clusters.tsv";COMPARE=ROOT/"gdt038_role_comparison.tsv";RESULT=ROOT/"gdt038_result.json"
CORES=("daiin","dam","okam","odain");SECTIONS=("HB","SB")
FEATURES=("target_state","wrapper","field_position","field_role","previous_state","next_state","previous_field_shape","next_field_shape","micro_context","masked_field_template","neighbor_field_context")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sec(r):
 if r["section"]=="H"and r["currier"]=="B":return"HB"
 if r["section"]=="S"and r["currier"]=="B":return"SB"
 return"OUT"
def shape(field,closed):
 states=[x[1]["record_state"]for x in field];n=len(field);bucket=str(n)if n<=3 else"4PLUS"
 return f'{"CLOSED"if closed else"OPEN"}|LEN_{bucket}|{states[0]}>{states[-1]}'
def jsd(a,b):
 na=sum(a.values());nb=sum(b.values());keys=set(a)|set(b);ans=0.
 for k in sorted(keys):
  p=a[k]/na;q=b[k]/nb;m=(p+q)/2
  if p:ans+=.5*p*math.log2(p/m)
  if q:ans+=.5*q*math.log2(q/m)
 return ans
def overlap(a,b):
 na=sum(a.values());nb=sum(b.values());shared=sum(min(a[k]/na,b[k]/nb)for k in sorted(set(a)|set(b)));return shared/(2-shared)if shared<2 else 1.

def contexts(rows):
 lines=defaultdict(list)
 for r in rows:
  assert not r["locus"].startswith("f84r");lines[r["locus"]].append(r)
 output=[]
 for locus,line in lines.items():
  line.sort(key=lambda r:int(r["group_index"]));section=sec(line[0])
  if section not in SECTIONS:continue
  fields=[];current=[]
  for i,r in enumerate(line):
   current.append((i,r))
   if r["record_state"]=="DY_RESOLUTION":fields.append((current,True));current=[]
  if current:fields.append((current,False))
  loc={i:(fi,j)for fi,(field,closed)in enumerate(fields)for j,(i,r)in enumerate(field)}
  for i,r in enumerate(line):
   core=r["residual_host"]
   if core not in CORES:continue
   fi,j=loc[i];field,closed=fields[fi];states=[x[1]["record_state"]for x in field];flen=len(field)
   prev=line[i-1]if i else None;nxt=line[i+1]if i+1<len(line)else None
   if flen==1:fpos="SINGLE"
   elif j==0:fpos="FIELD_START"
   elif j==flen-1:fpos="FIELD_CLOSE"if closed else"OPEN_FIELD_END"
   elif closed and j==flen-2:fpos="PRECLOSE"
   else:fpos="FIELD_INTERNAL"
   prev_field_shape="BOL"if fi==0 else shape(*fields[fi-1]);next_field_shape="EOL"if fi+1==len(fields)else shape(*fields[fi+1])
   prev_field_states="BOL"if fi==0 else">".join(x[1]["record_state"]for x in fields[fi-1][0]);next_field_states="EOL"if fi+1==len(fields)else">".join(x[1]["record_state"]for x in fields[fi+1][0])
   masked=states[:];masked[j]=f'TARGET[{r["record_state"]}]';masked=(">".join(masked)+(""if closed else">OPEN"))
   ps="BOS"if prev is None else prev["record_state"];ns="EOS"if nxt is None else nxt["record_state"]
   role=f'{"CLOSED"if closed else"OPEN"}|LEN_{flen if flen<=3 else "4PLUS"}|{fpos}|{r["record_state"]}'
   out={"locus":locus,"page":r["page"],"physical_folio":r["physical_folio"],"section":section,"hand":r["hand"],"group_index":r["group_index"],"group_count":r["group_count"],"token":r["token"],"wrapper":r["stripped_prefix"],"core":core,"wrapper_core":r["stripped_prefix"]+"|"+core,"target_state":r["record_state"],"line_position":f'{i+1}/{len(line)}',"field_index":str(fi+1),"field_count":str(len(fields)),"field_length":str(flen),"field_closed":str(int(closed)),"field_position":fpos,"field_role":role,"previous_token":"BOS"if prev is None else prev["token"],"previous_core":"BOS"if prev is None else prev["residual_host"],"previous_state":ps,"next_token":"EOS"if nxt is None else nxt["token"],"next_core":"EOS"if nxt is None else nxt["residual_host"],"next_state":ns,"previous_field_states":prev_field_states,"previous_field_shape":prev_field_shape,"current_field_states":">".join(states),"masked_field_template":masked,"next_field_states":next_field_states,"next_field_shape":next_field_shape,"micro_context":ps+">TARGET["+r["record_state"]+"]>"+ns,"neighbor_field_context":prev_field_shape+"||"+next_field_shape}
   output.append(out)
 output.sort(key=lambda r:(CORES.index(r["core"]),r["locus"],int(r["group_index"])))
 return output

def family_stats(core_rows,feature):
 a=Counter(r[feature]for r in core_rows if r["section"]=="HB");b=Counter(r[feature]for r in core_rows if r["section"]=="SB")
 obsj=jsd(a,b);obso=overlap(a,b);folios=sorted({r["physical_folio"]for r in core_rows});hb_n=len({r["physical_folio"]for r in core_rows if r["section"]=="HB"})
 null=[]
 for chosen in itertools.combinations(folios,hb_n):
  chosen=set(chosen);x=Counter(r[feature]for r in core_rows if r["physical_folio"]in chosen);y=Counter(r[feature]for r in core_rows if r["physical_folio"]not in chosen);null.append(jsd(x,y))
 local=(sum(v>=obsj-1e-15 for v in null))/len(null)
 lofo=[]
 for held in folios:
  rr=[r for r in core_rows if r["physical_folio"]!=held];x=Counter(r[feature]for r in rr if r["section"]=="HB");y=Counter(r[feature]for r in rr if r["section"]=="SB")
  if x and y:lofo.append((overlap(x,y),jsd(x,y)))
 h3=[r for r in core_rows if r["hand"]=="3"];h3a=Counter(r[feature]for r in h3 if r["section"]=="HB");h3b=Counter(r[feature]for r in h3 if r["section"]=="SB")
 return {"feature":feature,"levels":len(set(a)|set(b)),"hb_distribution":";".join(f"{k}:{v}"for k,v in sorted(a.items(),key=lambda z:(-z[1],z[0]))),"sb_distribution":";".join(f"{k}:{v}"for k,v in sorted(b.items(),key=lambda z:(-z[1],z[0]))),"weighted_jaccard":obso,"js_divergence_bits":obsj,"folio_permutation_local_p":local,"permutation_worlds":len(null),"lofo_min_weighted_jaccard":min(x[0]for x in lofo),"lofo_max_js_divergence_bits":max(x[1]for x in lofo),"hand3_weighted_jaccard":overlap(h3a,h3b)if h3a and h3b else float("nan"),"hand3_hb_count":sum(h3a.values()),"hand3_sb_count":sum(h3b.values()),"_null":null}

def role(core,stats,rows):
 by={x["feature"]:x for x in stats};state=by["target_state"];local=[by[x]["weighted_jaccard"]for x in("field_position","field_role","previous_state","next_state")];median=statistics.median(local);minfol=min(len({r["physical_folio"]for r in rows if r["section"]==s})for s in SECTIONS)
 if state["weighted_jaccard"]>=.8 and state["lofo_min_weighted_jaccard"]>=.75:
  if median>=.4:return"ABSTRACT_ROLE_PRESERVED"if minfol>=4 else"ABSTRACT_ROLE_PRESERVED_LOW_CAPACITY"
  return"STATE_PRESERVED_CONTEXT_VARIABLE"
 if state["weighted_jaccard"]>=.3:return"CONDITIONALLY_COMPATIBLE_SECTION_SHIFT"
 return"ABSTRACT_ROLE_NOT_PRESERVED"

def main():
 rows=read(SOURCE);occ=contexts(rows);assert len(occ)==65 and Counter(r["core"]for r in occ)==Counter({"daiin":23,"dam":8,"okam":16,"odain":18})
 occ_fields=list(occ[0]);write(OCC,occ,occ_fields)
 comparisons=[];summaries={};cluster_rows=[]
 for core in CORES:
  rr=[r for r in occ if r["core"]==core];stats=[family_stats(rr,f)for f in FEATURES]
  # maxT standardization over all context families within this core.
  means=[statistics.mean(x["_null"])for x in stats];sds=[statistics.stdev(x["_null"])if len(x["_null"])>1 else 0 for x in stats];zs=[(x["js_divergence_bits"]-m)/s if s else 0 for x,m,s in zip(stats,means,sds)];worlds=len(stats[0]["_null"]);maxz=[]
  for i in range(worlds):maxz.append(max(((x["_null"][i]-m)/s if s else 0)for x,m,s in zip(stats,means,sds)))
  for x,z in zip(stats,zs):
   x["folio_permutation_maxT_p"]=sum(v>=z-1e-15 for v in maxz)/worlds;x["core"]=core;x.pop("_null");comparisons.append(x)
  decision=role(core,stats,rr);summaries[core]={"decision":decision,"hb_occurrences":sum(r["section"]=="HB"for r in rr),"sb_occurrences":sum(r["section"]=="SB"for r in rr),"hb_folios":len({r["physical_folio"]for r in rr if r["section"]=="HB"}),"sb_folios":len({r["physical_folio"]for r in rr if r["section"]=="SB"}),"cross_section_recurring_clusters":0}
  for feature in FEATURES:
   grouped=defaultdict(list)
   for r in rr:grouped[r[feature]].append(r)
   for value,items in grouped.items():
    hc=sum(r["section"]=="HB"for r in items);sc=sum(r["section"]=="SB"for r in items);hf=len({r["physical_folio"]for r in items if r["section"]=="HB"});sf=len({r["physical_folio"]for r in items if r["section"]=="SB"});tf=len({r["physical_folio"]for r in items})
    if hc and sc and hf and sf:klass="CROSS_SECTION_CROSS_FOLIO";summaries[core]["cross_section_recurring_clusters"]+=1
    elif len(items)>=2:klass="SECTION_SPECIFIC_RECURRENT"
    else:klass="SINGLETON"
    cluster_rows.append({"core":core,"feature":feature,"template":value,"hb_count":hc,"sb_count":sc,"hb_folios":hf,"sb_folios":sf,"total_folios":tf,"classification":klass})
 cluster_rows.sort(key=lambda r:(CORES.index(r["core"]),FEATURES.index(r["feature"]),-int(r["hb_count"])-int(r["sb_count"]),r["template"]));write(CLUSTERS,cluster_rows,list(cluster_rows[0]))
 comp_fields=["core","feature","levels","hb_distribution","sb_distribution","weighted_jaccard","js_divergence_bits","folio_permutation_local_p","folio_permutation_maxT_p","permutation_worlds","lofo_min_weighted_jaccard","lofo_max_js_divergence_bits","hand3_weighted_jaccard","hand3_hb_count","hand3_sb_count"]
 write(COMPARE,[{k:(f"{x[k]:.9f}"if isinstance(x[k],float)else x[k])for k in comp_fields}for x in comparisons],comp_fields)
 result={"schema":"GDT038_CORE_CONTEXT_TRANSFER_RESULT_V1","status":"DAM_FIELD_ROLE_PROVISIONAL_LOW_CAPACITY_DAIIN_STATE_ONLY_OKAM_ODAIN_SECTION_CONDITIONED","scope":"Full available formal local contexts for exact residual cores DAIIN, DAM, OKAM, ODAIN in Herbal-B versus Currier-B Stars/Recipe S.","cores":summaries,"features":list(FEATURES),"occurrences":len(occ),"controls":{"folio_unit":"Exact section-label permutation across target-positive physical folios; all occurrences on a folio move together.","maxT":"Per-core maximum standardized JS divergence across eleven declared context families.","lofo":"Worst overlap and divergence after deleting each target-positive physical folio.","hand":"Hand-3-only overlap reported separately; capacity remains only two Herbal-B hand-3 folios."},"important_dependency":"GDT016 CARRIER_STATE is induced from the ch/che/sh renderer family. DAIIN/DAM state invariance is therefore not independent evidence beyond wrapper stability; field position and neighbors are tested separately.","claim_ceiling":"Tests preservation of anonymous state/field roles only. No concrete function, word, morpheme, POS, referent, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{"gdt016_group_state_inventory.tsv":sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"gdt037_result.json":sha(ROOT/"gdt037_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{OCC.name:sha(OCC),CLUSTERS.name:sha(CLUSTERS),COMPARE.name:sha(COMPARE)}}
 by={(x["core"],x["feature"]):x for x in comparisons}
 report="""# GDT038 — local-context transfer of DAIIN, DAM, OKAM, and ODAIN

## Outcome

**DAM_FIELD_ROLE_PROVISIONAL_LOW_CAPACITY; DAIIN_STATE_ONLY; OKAM/ODAIN_SECTION_CONDITIONED**

Every one of the 65 Herbal-B or Currier-B Stars/Recipe occurrences is aligned as preceding field and immediate state → observed wrapper+core → immediate state and following field. Fields are segmented only by the frozen GDT016 `DY_RESOLUTION` state.

| Core | HB/S occurrences | HB/S folios | target-state overlap | local-context median overlap | Worst LOFO state overlap | Decision |
|---|---:|---:|---:|---:|---:|---|
"""
 for core in CORES:
  s=summaries[core];state=by[core,"target_state"];local=statistics.median(by[core,x]["weighted_jaccard"]for x in("field_position","field_role","previous_state","next_state"));report+=f"| `{core}` | {s['hb_occurrences']}/{s['sb_occurrences']} | {s['hb_folios']}/{s['sb_folios']} | {state['weighted_jaccard']:.3f} | {local:.3f} | {state['lofo_min_weighted_jaccard']:.3f} | {s['decision']} |\n"
 report+="""

## Core findings

### DAIIN

All 23 DAIIN occurrences—6 Herbal-B and 17 S, spread across 4 and 5 folios—are `CARRIER_STATE`, despite renderer variation (`ch/che/sh` in Herbal-B and `ch/che` in S). This identity survives every folio deletion. It is **not**, however, independent role evidence: `CARRIER_STATE` is induced from that same renderer family. Independent context is variable: field-position overlap is 0.619, but previous-state overlap is 0.214, next-state overlap is 0.172, and exact micro-context and masked-field-template overlap are both zero. DAIIN is therefore a stable wrapped host/state association, not yet a stable full field role.

### DAM

All eight DAM occurrences are `CARRIER_STATE`: four `ch|dam` in Herbal-B and three `ch|dam` plus one `che|dam` in S. More importantly, every occurrence is in the final open field of its line; five are at the open-field end and three are internal. The target-state overlap is 1.000, field-position and combined field-role overlap are each 0.600, and next-field shape is identically `EOL`. Exact neighbours remain variable, and only 3 Herbal-B versus 2 S physical folios support the pattern. DAM is the best provisional abstract field-role lead, explicitly low-capacity and renderer-dependent.

### OKAM

OKAM does not preserve one state distribution. Herbal-B is dominated by `OTHER` (5/6, plus one `Q_OUTER_STATE`), while S distributes the host across `Q_OUTER_STATE` (5), `OTHER` (3), `CARRIER_STATE` (1), and `DY_RESOLUTION` (1). It remains a reusable host, but its renderer/state role is section-conditioned rather than invariant.

### ODAIN

ODAIN is also section-conditioned. Herbal-B supplies two `OTHER` and one `Q_OUTER_STATE`; S adds seven `CARRIER_STATE` alongside four `OTHER` and four `Q_OUTER_STATE`. The overlap in local/Q roles is real, but the S-only carrier realization prevents a single preserved abstract-role claim.

## Template clusters and tests

`gdt038_context_clusters.tsv` retains every singleton and recurrent template. Cross-section clusters require occurrences on at least one physical folio in each section; no repeated token on one page is treated as transfer. `gdt038_role_comparison.tsv` reports distribution overlap, JS divergence, exact folio-label permutations, per-core maxT over all eleven context views, worst leave-one-folio-out behavior, and hand-3-only sensitivity.

The strongest invariants are renderer-derived target state for DAIIN/DAM and final-open-field placement for DAM. Exact previous/next field templates are much sparser and often section-specific. This is compatible with a core selecting a broad constructional role while neighbouring material supplies record-specific content, but it is equally compatible with a constrained formal generator. No semantic choice between those accounts is made. The exact folio permutations provide diagnostics rather than confirmation: no positive preservation claim is inferred from a small p-value.

No concrete function, word, morpheme, POS, referent, sound, language, plaintext, meaning, or translation is assigned. f84r was not opened, retained, queried, joined, or scored.
"""
 REPORT.write_text(report,encoding="utf-8");result["documents"]={METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)};body=dict(result);result["result_content_sha256"]=csha(body);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],"occurrences":len(occ),"cores":summaries},sort_keys=True))
if __name__=="__main__":main()
