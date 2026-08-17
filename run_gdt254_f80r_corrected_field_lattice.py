#!/usr/bin/env python3
"""Rebuild f80r HPR2 fields on five corrected paragraphs and coarse analogies."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent
SRC="gdt016_group_state_inventory.tsv";CENS="gdt246_f80r_complete_locus_inventory.tsv";COORD="gdt244_f80r_paragraph_coordinate.tsv";PROJ="gdt002_grammar_projection.tsv";EXT="gdt176_external_role_units.tsv"
OUTS=["gdt254_f80r_hpr2_fields.tsv","gdt254_f80r_line_coverage.tsv","gdt254_f80r_paragraph_uncertainty.tsv","gdt254_f80r_role_projection.tsv","gdt254_f80r_role_summary.tsv","gdt254_counterexamples.tsv"]
DOCS=["GDT254_F80R_CORRECTED_FIELD_LATTICE_METHOD.md","GDT254_F80R_CORRECTED_FIELD_LATTICE_REPORT.md"]
RIGHT=("aiin","air","ain","ar","al");CLASSES=("OPENER","OPERATION","INGREDIENT","TOOL","CLOSER");AB={"OPENER":"UNRESOLVED_EDGE_CLASS","OPERATION":"INSTRUCTION_CLAUSE_LIKE","INGREDIENT":"SHORT_ARGUMENT_LIKE","TOOL":"SHORT_ARGUMENT_LIKE","CLOSER":"RECORD_CLOSER_LIKE"}
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def rd(p):
 with (R/p).open(encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def wr(p,z):
 with (R/p).open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(z[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(z)
def pre(x):
 h=x["residual_host"];b3=int(h.endswith("m") and len(h)>1);h=h[:-1] if b3 else h;right="NONE"
 for s in RIGHT:
  if h.endswith(s) and len(h)>len(s):h=h[:-len(s)];right=s;break
 inner=int(x["stripped_prefix"] in {"ch","che","sh"} and h.startswith("d") and len(h)>1);h=h[1:] if inner else h
 return h,b3,right,inner
def fit(X,y):
 mean=X.mean(0);scale=X.std(0);scale[scale<1e-9]=1;Z=np.column_stack([np.ones(len(X)),(X-mean)/scale]);Y=np.eye(5)[y];b=np.zeros((5,5));b[0]=np.log(np.bincount(y,minlength=5)/len(y)+1e-12);m=np.zeros_like(b);v=np.zeros_like(b)
 for step in range(1,801):
  z=Z@b;z-=z.max(1,keepdims=True);p=np.exp(z);p/=p.sum(1,keepdims=True);g=Z.T@(p-Y)/len(y);g[1:]+=.001*b[1:];m=.9*m+.1*g;v=.999*v+.001*g*g;b-=.03*(m/(1-.9**step))/(np.sqrt(v/(1-.999**step))+1e-8)
 return b,mean,scale
def pred(X,m):
 b,a,s=m;z=np.column_stack([np.ones(len(X)),np.clip((X-a)/s,-4,4)])@b;return z.argmax(1)
def main():
 prose={x["locus"] for x in rd(CENS) if x["page"]=="f80r" and x["kind"]=="P"};coord=rd(COORD);assert len(prose)==43 and len(coord)==43
 allrows=[];target=[]
 with (R/SRC).open(encoding="utf-8") as f:
  h=f.readline().rstrip("\n").split("\t");pi=h.index("page")
  for raw in f:
   a=raw.rstrip("\n").split("\t");page=a[pi]
   if page.startswith("f84"):continue
   x=dict(zip(h,a));allrows.append(x)
   if page=="f80r" and x["locus"] in prose:target.append(x)
 assert target and all(not x["page"].startswith("f84") for x in allrows)
 cnt=Counter(pre(x)[0] for x in allrows);licensed={h for h in cnt if cnt[h] and cnt["o"+h] and cnt["ot"+h]}|{"ar","al","ol"}
 def parse(x):
  h,b,r,i=pre(x);frame="NONE"
  if h.startswith("ot") and h[2:] in licensed:h=h[2:];frame="OT"
  elif h.startswith("o") and h[1:] in licensed:h=h[1:];frame="O"
  return h or "EMPTY",b,r,i,frame
 by=defaultdict(list)
 for x in target:by[x["locus"]].append(x)
 fields=[];coverage=[]
 for locus in sorted(by,key=lambda x:int(x.split(".")[1])):
  gg=sorted(by[locus],key=lambda x:int(x["group_index"]));fs=[];cur=[]
  for g in gg:
   cur.append(g)
   if g["dy_closure"]=="1":fs.append(cur);cur=[]
  if cur:fs.append(cur)
  for i,z in enumerate(fs,1):
   pp=[parse(g) for g in z];fields.append({"page":"f80r","locus":locus,"line_field_ordinal":i,"line_field_count":len(fs),"field_group_count":len(z),"source_tokens":"|".join(g["token"] for g in z),"page_hosts":"|".join(p[0] for p in pp),"compiler_cells":"|".join(f"{g['stripped_prefix']}:{p[4]}:{p[3]}:{p[2]}:{g['dy_closure']}:{p[1]}" for p,g in zip(pp,z)),"line_field_end":"DY" if z[-1]["dy_closure"]=="1" else "LINE_END","semantic_role":"UNASSIGNED"})
  coverage.append({"page":"f80r","locus":locus,"source_group_count":len(gg),"hpr2_field_count":len(fs),"coverage_state":"HPR2_FORMAL_FIELD_SEGMENTED_NO_SEMANTIC_ROLE"})
 wr(OUTS[0],fields);wr(OUTS[1],coverage)
 maxg=defaultdict(int)
 with (R/PROJ).open(encoding="utf-8") as f:
  h=f.readline().rstrip("\n").split("\t");pi=h.index("page")
  for raw in f:
   a=raw.rstrip("\n").split("\t")
   if a[pi]!="f80r":continue
   x=dict(zip(h,a))
   if x["kind"]=="P":maxg[x["locus"]]=max(maxg[x["locus"]],int(x["source_group_count"]))
 er=rd(EXT);X=np.array([[float(x["relative_position"]),float(x["relative_position"])**2,math.log2(1+int(x["span_token_count"])),math.log2(1+int(x["record_unit_count"]))] for x in er]);y=np.array([CLASSES.index(x["oracle_role"]) for x in er]);model=fit(X,y)
 byline=defaultdict(list)
 for x in fields:byline[x["locus"]].append(x)
 covered_loci=set(byline)
 para=[];out=[]
 for pid in [f"P{i}" for i in range(1,6)]:
  lines=sorted((x for x in coord if x["paragraph_id"]==pid),key=lambda x:int(x["paragraph_line_ordinal"]));known=sum(len(byline.get(x["locus"],[])) for x in lines);missing=[x for x in lines if x["locus"] not in covered_loci];mn=len(missing);mx=sum(maxg[x["locus"]] for x in missing)
  para.append({"paragraph_id":pid,"physical_lines":len(lines),"covered_lines":len(lines)-mn,"known_fields":known,"missing_lines":mn,"missing_field_min":mn,"missing_field_max":mx,"total_field_min":known+mn,"total_field_max":known+mx})
  known_before=0
  for line in lines:
   locus=line["locus"]
   if locus not in covered_loci:continue
   n=int(line["paragraph_line_ordinal"]);before=[x for x in missing if int(x["paragraph_line_ordinal"])<n];after=[x for x in missing if int(x["paragraph_line_ordinal"])>n];bmin=len(before);bmax=sum(maxg[x["locus"]] for x in before);amin=len(after);amax=sum(maxg[x["locus"]] for x in after)
   for local,x in enumerate(sorted(byline[locus],key=lambda q:int(q["line_field_ordinal"])),1):
    cases=[]
    for bm in range(bmin,bmax+1):
     for am in range(amin,amax+1):
      total=known+bm+am;ordinal=known_before+bm+local;rel=ordinal/total;cases.append([rel,rel*rel,math.log2(1+int(x["field_group_count"])),math.log2(1+total)])
    ids=pred(np.array(cases),model);classes=sorted({CLASSES[int(i)] for i in ids});abstract=sorted({AB[c] for c in classes});robust=len(abstract)==1
    out.append({"page":"f80r","paragraph_id":pid,"locus":locus,"line_field_ordinal":x["line_field_ordinal"],"field_group_count":x["field_group_count"],"source_tokens":x["source_tokens"],"page_hosts":x["page_hosts"],"line_field_end":x["line_field_end"],"missing_before_min":bmin,"missing_before_max":bmax,"missing_after_min":amin,"missing_after_max":amax,"feasible_coordinates":len(cases),"predicted_five_way_classes":"|".join(classes),"predicted_abstract_classes":"|".join(abstract),"robust_abstract_role_like":abstract[0] if robust else "UNRESOLVED_MISSINGNESS_SENSITIVE","robust_under_missingness":int(robust),"semantic_value":"UNASSIGNED"})
   known_before+=len(byline[locus])
 wr(OUTS[2],para);wr(OUTS[3],out)
 count=Counter(x["robust_abstract_role_like"] for x in out);summary=[{"role_like":k,"fields":v,"fraction":f"{v/len(out):.12f}"} for k,v in sorted(count.items())];wr(OUTS[4],summary)
 counter=[{"counterexample":"MISSING_LINE_RANGE","value":f"{sum(x['missing_lines'] for x in para)} of 43 prose lines lack HPR2 field parses","consequence":"coordinates of covered fields are intervals rather than exact ranks"},{"counterexample":"LENGTH_POSITION_INSTRUMENT","value":"classes are generated from relative position field size and record size only","consequence":"role-like labels are analogies and cannot identify ingredients operations or meanings"},{"counterexample":"FIVE_SMALL_PARAGRAPHS","value":"five paragraph-specific coordinates replace two invalid merged records","consequence":"old GDT229 f80r role sequence is not restored"},{"counterexample":"NO_VISUAL_FIELD_OWNERSHIP","value":"page-level figures do not bind individual prose fields","consequence":"no semantic assignment is executable"}];wr(OUTS[5],counter)
 status="F80R_FIVE_PARAGRAPH_HPR2_LATTICE_REBUILT_FORMAL_ANALOGY_ONLY"
 result={"experiment":"GDT254_F80R_CORRECTED_FIELD_LATTICE","status":status,"physical_prose_loci":43,"paragraphs":5,"hpr2_covered_loci":len(coverage),"hpr2_fields":len(fields),"missing_loci":43-len(coverage),"robust_fields":sum(int(x["robust_under_missingness"]) for x in out),"unresolved_fields":sum(not int(x["robust_under_missingness"]) for x in out),"role_counts":dict(sorted(count.items())),"paragraph_uncertainty":para,"interpretation":"The corrected five-paragraph page supports a reproducible formal field lattice, but its external classes remain length/position analogies with zero semantic assignments.","active_semantic_assignments":0,"claim_ceiling":"Corrected paragraph/HPR2 architecture and coarse external analogy only; no field ownership ingredient operation object word language plaintext or translation.","f84r":{"input_rows":0,"retained":False,"joined":False,"scored":False,"new_access":False},"inputs":{p:sha(p) for p in [SRC,CENS,COORD,PROJ,EXT]},"outputs":{},"documents":{},"implementation":{}}
 for p in OUTS:result["outputs"][p]=sha(p)
 for p in DOCS:result["documents"][p]=sha(p)
 result["implementation"][Path(__file__).name]=sha(Path(__file__).name)
 report=(R/DOCS[1]).read_text().split("\n## Reproducible result",1)[0].rstrip()+f"\n\n## Reproducible result\n\nStatus: **{status}**.\n\nThe five paragraphs contain **43** physical prose loci. HPR2 covers **{len(coverage)}** loci and produces **{len(fields)}** fields; **{43-len(coverage)}** loci remain explicit missing intervals. Coarse retained classes are "+", ".join(f"**{k}: {v}**" for k,v in sorted(count.items()))+f"; **{result['unresolved_fields']}** fields are missingness-sensitive.\n\nThis restores formal coordinates, not semantics. No f84r row was accessed or used.\n"
 (R/DOCS[1]).write_text(report,encoding="utf-8")
 result["documents"][DOCS[1]]=sha(DOCS[1]);core=dict(result);result["content_hash"]=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(",",":")).encode()).hexdigest();(R/"gdt254_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":status,"covered":len(coverage),"fields":len(fields),"counts":dict(count),"paragraphs":para},sort_keys=True))
if __name__=="__main__":main()
