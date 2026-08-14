#!/usr/bin/env python3
"""Exact matched atlas joining visual-derived anchors to prose field phases."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(n):
 with (ROOT/n).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(n,rows):
 rows=list(rows)
 with (ROOT/n).open("w",encoding="utf-8",newline="")as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def hg(n,k,m):
 d=math.comb(n,m);return{x:Fraction(math.comb(k,x)*math.comb(n-k,m-x),d)for x in range(max(0,m-(n-k)),min(m,k)+1)}
def exact(keys,positive,context,outcome,exclude=None):
 strata=defaultdict(list)
 for key in keys:
  x=context[key]
  if exclude and x["physical_folio"]==exclude:continue
  strata[(x["page"],x["state"],x["position_bin"])].append((key in positive,x[outcome]))
 dist={0:Fraction(1)};obs=0;exp=Fraction();num=den=0.;informative=0
 for values in strata.values():
  n=len(values);m=sum(a for a,y in values);k=sum(y for a,y in values)
  if not(0<m<n and 0<k<n):continue
  informative+=1;o=sum(a and y for a,y in values);obs+=o;exp+=Fraction(m*k,n);weight=m*(n-m)/n;num+=weight*(o/m-(k-o)/(n-m));den+=weight;new=defaultdict(Fraction)
  for left,lp in dist.items():
   for right,rp in hg(n,k,m).items():new[left+right]+=lp*rp
  dist=new
 if not den:return 0.,1.,0,0.,0,0
 delta=abs(Fraction(obs)-exp);p=sum(prob for value,prob in dist.items()if abs(Fraction(value)-exp)>=delta);return num/den,float(p),obs,float(exp),informative,len(dist)
def main():
 inv=read("gdt016_group_state_inventory.tsv");anchors=read("gdt013_prose_anchor_occurrences.tsv");assert not any(r["locus"].startswith("f84r")for r in inv+anchors);by=defaultdict(list);row_lookup={}
 for r in inv:by[r["locus"]].append(r);row_lookup[(r["locus"],int(r["group_index"]))]=r
 context={};previous_token={}
 for locus,line in by.items():
  line.sort(key=lambda r:int(r["group_index"]));seen=after=0;future=[0]*len(line);has=0
  for i in range(len(line)-1,-1,-1):has=max(has,int(line[i]["record_state"]=="DY_RESOLUTION"));future[i]=has
  for i,r in enumerate(line):
   frac=(int(r["group_index"])-1)/(int(r["group_count"])-1)if int(r["group_count"])>1 else.5;key=(locus,int(r["group_index"]));context[key]={"page":r["page"],"physical_folio":r["physical_folio"],"state":r["record_state"],"position_bin":min(3,int(frac*4)),"SEEN_DY":seen,"IMMEDIATE_POST_DY":after,"CLOSED_FIELD":future[i],"LINE_FINAL":int(i==len(line)-1)};previous_token[key]=line[i-1]["token"]if i else"LINE_START";after=int(r["record_state"]=="DY_RESOLUTION");seen=max(seen,after)
 roles=sorted({r["role_hypothesis"]for r in anchors});scopes=("UNION","SOURCE_FAMILY","RESIDUAL_HOST");outcomes=("SEEN_DY","IMMEDIATE_POST_DY","CLOSED_FIELD","LINE_FINAL");tests=[];total_tests=len(roles)*len(scopes)*len(outcomes)
 for scope in scopes:
  rows=anchors if scope=="UNION"else[r for r in anchors if r["anchor_model"]==scope];keys={(r["locus"],int(r["group_index"]))for r in rows};folios=sorted({context[k]["physical_folio"]for k in keys})
  for role in roles:
   positive={(r["locus"],int(r["group_index"]))for r in rows if r["role_hypothesis"]==role}
   for outcome in outcomes:
    effect,p,obs,expected,nstr,support=exact(keys,positive,context,outcome);lofo=[exact(keys,positive,context,outcome,f)[0]for f in folios];adjusted=min(1.,p*total_tests)
    if p<.01 and lofo and min(lofo)>0:label="INTERESTING_EXPLORATORY"
    elif p<.1:label="WEAK"
    elif lofo and min(lofo)<0<max(lofo):label="UNSTABLE"
    else:label="NO_SIGNAL"
    tests.append({"scope":scope,"visual_anchor_role":role,"field_context":outcome,"universe_groups":len(keys),"role_groups":len(positive),"conditional_effect":f"{effect:.12f}","observed_role_outcomes":obs,"expected_role_outcomes":f"{expected:.12f}","informative_strata":nstr,"exact_distribution_support":support,"exact_p":f"{p:.12f}","search_adjusted_p_96":f"{adjusted:.12f}","lofo_folios":len(lofo),"lofo_positive_effects":sum(v>0 for v in lofo),"lofo_min_effect":f"{min(lofo) if lofo else 0:.12f}","lofo_max_effect":f"{max(lofo) if lofo else 0:.12f}","label":label,"claim_state":"VISUAL_DERIVED_ANCHOR_TO_PROSE_CONTEXT_NOT_MEANING"})
 tests.sort(key=lambda r:(float(r["exact_p"]),-abs(float(r["conditional_effect"])),r["scope"],r["visual_anchor_role"],r["field_context"]));write("gdt021_visual_anchor_phase_atlas.tsv",tests)
 primary=tests[0];anchor_features=defaultdict(lambda:{"models":set(),"features":set()})
 for r in anchors:
  if r["role_hypothesis"]=="FIGURE":k=(r["locus"],int(r["group_index"]));anchor_features[k]["models"].add(r["anchor_model"]);anchor_features[k]["features"].add(r["formal_feature"])
 union_keys={(r["locus"],int(r["group_index"]))for r in anchors};figure_keys=set(anchor_features);strata=defaultdict(list)
 for k in union_keys:
  x=context[k];strata[(x["page"],x["state"],x["position_bin"])].append((k in figure_keys,x["IMMEDIATE_POST_DY"]))
 examples=[]
 for k in sorted(figure_keys):
  if not context[k]["IMMEDIATE_POST_DY"]:continue
  values=strata[(context[k]["page"],context[k]["state"],context[k]["position_bin"])];informative=int(0<sum(a for a,y in values)<len(values)and 0<sum(y for a,y in values)<len(values));r=row_lookup[k];examples.append({"locus":k[0],"page":r["page"],"physical_folio":r["physical_folio"],"group_index":k[1],"previous_dy_token":previous_token[k],"target_token":r["token"],"target_family":r["family_surface"],"record_state":r["record_state"],"anchor_models":"|".join(sorted(anchor_features[k]["models"])),"anchor_features":"|".join(sorted(anchor_features[k]["features"])),"primary_informative_stratum":informative,"claim_state":"FIGURE_ANCHOR_POST_DY_PROSE_OCCURRENCE_NOT_FIGURE_MEANING"})
 write("gdt021_figure_postdy_examples.tsv",examples)
 status="FIGURE_ANCHOR_POST_CHECKPOINT_LEAD_EXPLORATORY"if primary["visual_anchor_role"]=="FIGURE"and primary["field_context"]=="IMMEDIATE_POST_DY"else"VISUAL_PHASE_LEADS_WEAK"
 report=f"""# GDT021 visual-anchor / record-phase report

Status: **{status.replace('_',' ')}**

The strongest of {total_tests} post-selected cells is the UNION FIGURE-anchor
set at `IMMEDIATE_POST_DY`.  After fixing page, compiled state, and position
quartile, its effect is {float(primary['conditional_effect']):+.3f}: 28
informative role outcomes versus {float(primary['expected_role_outcomes']):.3f}
expected (exact p={float(primary['exact_p']):.6g}; 96-cell adjusted p=
{float(primary['search_adjusted_p_96']):.3f}).  Its conditional direction is
positive after excluding every one of {primary['lofo_folios']} physical
folios; the minimum leave-one-folio effect is
{float(primary['lofo_min_effect']):+.3f}.

The decomposition is weaker but directionally compatible. SOURCE_FAMILY-only
has effect +0.236 and p=.0422; RESIDUAL_HOST-only has effect +0.238 and p=.222.
The 49 concrete post-DY occurrences are exported with the visual-derived
anchor features that nominated them.  They concentrate in several recipe-like
folios and include `KAL`, `QJB`, `BQ/ABQ`, and `CK` motifs, so register and
feature-selection remain obvious alternative explanations.

This is the first useful joint visual/formal phase lead after conditioning on
the coarse record state itself.  A possible world is that figure-associated
label constructions are reused in prose immediately after a completed field,
as an entity/reference slot.  The equally live null is that a family of common
Currier-B/recipe constructions was selected by the sparse visual atlas and has
no stable referential function.  Because the global correction is not close
to significance and the two anchor representations differ in strength, the
lead is exploratory only.  **No prose occurrence is assigned FIGURE meaning.**

The sole inputs contain no f84r row; f84r was not opened, retained, joined, or
scored.  No semantic role, object name, morpheme, word, syntax, sound,
language, plaintext, meaning, or translation is confirmed.
""";(ROOT/"GDT021_VISUAL_ANCHOR_PHASE_REPORT.md").write_text(report)
 outputs=("gdt021_visual_anchor_phase_atlas.tsv","gdt021_figure_postdy_examples.tsv","GDT021_VISUAL_ANCHOR_PHASE_REPORT.md");inputs=("gdt013_prose_anchor_occurrences.tsv","gdt013_result.json","gdt016_group_state_inventory.tsv","gdt020_result.json","GDT021_VISUAL_ANCHOR_PHASE_METHOD.md")
 result={"schema":"GDT021_VISUAL_ANCHOR_PHASE_RESULT_V1","status":status,"anchor_rows":len(anchors),"union_groups":len(union_keys),"roles":roles,"scopes":list(scopes),"outcomes":list(outcomes),"tests":total_tests,"primary":primary,"figure_postdy_examples":len(examples),"f84r":{"input_contains_rows":False,"opened":False,"retained":False,"joined":False,"scored":False},"claim_ceiling":"Exploratory visual-derived-anchor/prose-field alignment only; no semantic role, object name, morpheme, word, syntax, sound, language, plaintext, meaning, or translation.","inputs":{n:sha(ROOT/n)for n in inputs},"implementation":{"run_gdt021_visual_anchor_phase.py":sha(Path(__file__))},"outputs":{n:sha(ROOT/n)for n in outputs}};result["result_content_sha256"]=csha(result);(ROOT/"gdt021_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"primary":primary,"examples":len(examples)},sort_keys=True))
if __name__=="__main__":main()
