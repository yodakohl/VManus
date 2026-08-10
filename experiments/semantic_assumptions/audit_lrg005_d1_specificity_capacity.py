#!/usr/bin/env python3
"""Bind the label-blind two-channel LRG005 target score matrix."""
from __future__ import annotations
import csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent;R=HERE/"results";GROUPS=R/"source_sta_family_consensus_groups.tsv";PANEL=R/"lrg005_d1_extension_capacity.tsv";QUOTAS=R/"lrg005_d1_extension_quotas.tsv";OUT=R/"lrg005_d1_specificity_capacity.json";REPORT=R/"lrg005_d1_specificity_capacity_report.md";FIELDS=("zl_sta_codes","it_sta_codes","rf_sta_codes")
EXPECTED={"groups":"a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225","panel":"4d5c977aa76ba2284f3c70554c59621cb4c9d9ffd1013ad3d579f964470f954f","quotas":"73637c27d64494210974d48f463eb2c9a65cb9fb9b4b837cd8463d5bebc99246"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tab(p):
 with p.open(encoding="utf8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def folio(p):
 m=re.fullmatch(r"(f\d+)(?:[rv](?:\d+)?)?",p)
 if not m:raise RuntimeError("page")
 return m.group(1)
def uid(x):return "LRG005-U"+hashlib.sha256(("LRG005-D1|"+x).encode()).hexdigest()[:20]
def seq(r):return tuple(r[f] for f in FIELDS)
def main():
 if OUT.exists() or REPORT.exists():raise RuntimeError("output exists")
 observed={"groups":sha(GROUPS),"panel":sha(PANEL),"quotas":sha(QUOTAS)}
 if observed!=EXPECTED:raise RuntimeError("input drift")
 groups=tab(GROUPS);panel=tab(PANEL);quotas=tab(QUOTAS);lookup={uid(r["consensus_group_id"]):r for r in groups}
 if len(panel)!=536 or len(quotas)!=68 or any(r["unit_id"] not in lookup for r in panel):raise RuntimeError("panel join")
 prose=[r for r in groups if r["strict_zero_alternative"]=="1" and r["kind"]=="P" and r["grammar_scope"]=="CONFIRMED_PROSE"]
 bare=Counter();any_extension=Counter();d1_extension=Counter()
 for r in prose:
  f=folio(r["page"]);s=seq(r);bare[f,s]+=1;parts=[x.split() for x in s]
  if min(map(len,parts))>=2:
   suffix=tuple(" ".join(x[1:]) for x in parts);any_extension[f,suffix]+=1
   if all(x[0]=="D1" for x in parts):d1_extension[f,suffix]+=1
 def totals(c):
  out=Counter()
  for (_f,s),n in c.items():out[s]+=n
  return out
 tb,ta,td=map(totals,(bare,any_extension,d1_extension));scores=[];support=Counter();by_cell=defaultdict(list)
 for p in panel:
  r=lookup[p["unit_id"]];f=p["physical_folio"];s=seq(r);nb=tb[s]-bare[f,s];na=ta[s]-any_extension[f,s];nd=td[s]-d1_extension[f,s];no=na-nd
  if min(nb,nd,no)<0:raise RuntimeError("negative count")
  values=(math.log((nd+.5)/(nb+.5)),math.log((nd+.5)/(no+.5)))
  if not all(map(math.isfinite,values)):raise RuntimeError("nonfinite")
  scores.append(values);by_cell[p["cell_id"]].append(values);support["D1"]+=nd>0;support["BARE"]+=nb>0;support["OTHER"]+=no>0;support["D1_AND_BARE"]+=nd>0 and nb>0;support["D1_AND_OTHER"]+=nd>0 and no>0
 matrix=np.asarray(scores,dtype=np.float64);variable={name:{c for c,v in by_cell.items() if max(x[j] for x in v)-min(x[j] for x in v)>1e-12} for j,name in enumerate(("D1_BARE","D1_OTHER"))};joint=variable["D1_BARE"]&variable["D1_OTHER"];q={r["cell_id"]:r for r in quotas};joint_rows=sum(int(q[c]["total_rows"]) for c in joint);joint_folios={p["physical_folio"] for p in panel if p["cell_id"] in joint};joint_sections=Counter(next(p["section"] for p in panel if p["cell_id"]==c) for c in joint)
 result={"status":"PASS_LABEL_BLIND_TWO_CHANNEL_SCORE_CAPACITY","decision":"GO_TARGET_REGISTRATION_ONLY","claim_ceiling":"This binds only a label-blind D1-versus-bare and D1-versus-other exact-member score matrix. No role association prefix classifier morpheme word POS sound meaning plaintext or translation follows.","inputs":observed,"counts":{"rows":len(panel),"cells":len(quotas),"folios":len(set(p["physical_folio"] for p in panel)),"D1_BARE_unique_scores":len(set(matrix[:,0])),"D1_OTHER_unique_scores":len(set(matrix[:,1])),"D1_BARE_variable_cells":len(variable["D1_BARE"]),"D1_OTHER_variable_cells":len(variable["D1_OTHER"]),"joint_variable_cells":len(joint),"joint_variable_rows":joint_rows,"joint_variable_folios":len(joint_folios),"joint_variable_cells_by_section":dict(sorted(joint_sections.items())),"support":dict(support)},"score_matrix_sha256":hashlib.sha256(np.ascontiguousarray(matrix).tobytes()).hexdigest(),"label_prose_contrast_computed":False,"row_scores_emitted":False,"member_sequences_emitted":False}
 gates={"at_least_50_joint_variable_cells":len(joint)>=50,"at_least_475_joint_variable_rows":joint_rows>=475,"all_13_folios":len(joint_folios)==13,"at_least_25_joint_cells_each_section":min(joint_sections.values())>=25,"at_least_250_D1_other_joint_support":support["D1_AND_OTHER"]>=250};result["gates"]=gates
 if not all(gates.values()):raise RuntimeError(gates)
 OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8",newline="\n");REPORT.write_text("\n".join(["# LRG005 D1-specificity score capacity","",f"Status: **{result['status']}**.","",f"The label-blind 536-by-2 target matrix has **{result['counts']['D1_BARE_unique_scores']}** D1/bare and **{result['counts']['D1_OTHER_unique_scores']}** D1/other values. Both vary jointly in **{len(joint)}** cells containing **{joint_rows}** rows on all **13** folios; **{support['D1_AND_OTHER']}** rows have held-folio support for both D1 and other extensions.","","No role contrast, row score, or member sequence was emitted. Decision: **GO_TARGET_REGISTRATION_ONLY**.","","This supplies no prefix, classifier, morpheme, word, POS, sound, meaning, plaintext, or translation.",""]),encoding="utf8",newline="\n");print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
