#!/usr/bin/env python3
"""Independent reconstruction of the LRG005 two-channel score-capacity binding."""
from __future__ import annotations
import csv,hashlib,json,math,re
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;R=HERE/"results";G=R/"source_sta_family_consensus_groups.tsv";P=R/"lrg005_d1_extension_capacity.tsv";Q=R/"lrg005_d1_extension_quotas.tsv";PROD=R/"lrg005_d1_specificity_capacity.json";REPORT=R/"lrg005_d1_specificity_capacity_report.md";OUT=R/"lrg005_d1_specificity_capacity_validation.json";OUTR=R/"lrg005_d1_specificity_capacity_validation_report.md";F=("zl_sta_codes","it_sta_codes","rf_sta_codes");checks=0
def need(x,m):
 global checks;checks+=1
 if not x:raise RuntimeError(m)
def tab(p):
 with p.open(encoding="utf8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def fol(p):
 m=re.fullmatch(r"(f\d+)(?:[rv](?:\d+)?)?",p);need(m is not None,"page");return m.group(1)
def uid(x):return "LRG005-U"+hashlib.sha256(("LRG005-D1|"+x).encode()).hexdigest()[:20]
def seq(r):return tuple(r[x] for x in F)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 groups=tab(G);panel=tab(P);quotas=tab(Q);lookup={uid(r['consensus_group_id']):r for r in groups};need(len(panel)==536 and len(quotas)==68,"geometry");need(all(r['unit_id'] in lookup for r in panel),"join");prose=[r for r in groups if r['strict_zero_alternative']=='1' and r['kind']=='P' and r['grammar_scope']=='CONFIRMED_PROSE'];b=Counter();a=Counter();d=Counter()
 for r in prose:
  f=fol(r['page']);s=seq(r);b[f,s]+=1;parts=[x.split() for x in s]
  if all(len(x)>=2 for x in parts):
   suffix=tuple(' '.join(x[1:]) for x in parts);a[f,suffix]+=1
   if all(x[0]=='D1' for x in parts):d[f,suffix]+=1
 def total(c):
  z=Counter()
  for (_f,s),n in c.items():z[s]+=n
  return z
 tb,ta,td=map(total,(b,a,d));matrix=[];support=Counter();bc=defaultdict(list)
 for p in panel:
  r=lookup[p['unit_id']];f=p['physical_folio'];s=seq(r);nb=tb[s]-b[f,s];na=ta[s]-a[f,s];nd=td[s]-d[f,s];no=na-nd;need(min(nb,no,nd)>=0,"counts");v=(math.log((nd+.5)/(nb+.5)),math.log((nd+.5)/(no+.5)));need(all(map(math.isfinite,v)),"finite");matrix.append(v);bc[p['cell_id']].append(v);support['D1']+=nd>0;support['BARE']+=nb>0;support['OTHER']+=no>0;support['D1_AND_BARE']+=nd>0 and nb>0;support['D1_AND_OTHER']+=nd>0 and no>0
 m=np.asarray(matrix);var=[{c for c,v in bc.items() if max(x[j] for x in v)-min(x[j] for x in v)>1e-12} for j in range(2)];joint=var[0]&var[1];qm={r['cell_id']:r for r in quotas};jr=sum(int(qm[c]['total_rows']) for c in joint);jf={p['physical_folio'] for p in panel if p['cell_id'] in joint};js=Counter(next(p['section'] for p in panel if p['cell_id']==c) for c in joint);prod=json.loads(PROD.read_text());counts={"rows":536,"cells":68,"folios":13,"D1_BARE_unique_scores":len(set(m[:,0])),"D1_OTHER_unique_scores":len(set(m[:,1])),"D1_BARE_variable_cells":len(var[0]),"D1_OTHER_variable_cells":len(var[1]),"joint_variable_cells":len(joint),"joint_variable_rows":jr,"joint_variable_folios":len(jf),"joint_variable_cells_by_section":dict(sorted(js.items())),"support":dict(support)};need(prod['counts']==counts,"summary");need(prod['score_matrix_sha256']==hashlib.sha256(np.ascontiguousarray(m).tobytes()).hexdigest(),"matrix hash");need(prod['status']=='PASS_LABEL_BLIND_TWO_CHANNEL_SCORE_CAPACITY' and prod['decision']=='GO_TARGET_REGISTRATION_ONLY',"status");need(prod['label_prose_contrast_computed'] is False and prod['row_scores_emitted'] is False and prod['member_sequences_emitted'] is False,"boundary");need(all(prod['gates'].values()),"gates");need(prod['inputs']=={'groups':sha(G),'panel':sha(P),'quotas':sha(Q)},"inputs");expected="\n".join(["# LRG005 D1-specificity score capacity","",f"Status: **{prod['status']}**.","",f"The label-blind 536-by-2 target matrix has **{counts['D1_BARE_unique_scores']}** D1/bare and **{counts['D1_OTHER_unique_scores']}** D1/other values. Both vary jointly in **{len(joint)}** cells containing **{jr}** rows on all **13** folios; **{support['D1_AND_OTHER']}** rows have held-folio support for both D1 and other extensions.","","No role contrast, row score, or member sequence was emitted. Decision: **GO_TARGET_REGISTRATION_ONLY**.","","This supplies no prefix, classifier, morpheme, word, POS, sound, meaning, plaintext, or translation.",""]);need(REPORT.read_text()==expected,"report");result={'status':'PASS_CLEAN_LRG005_D1_SPECIFICITY_CAPACITY_RECONSTRUCTION','checks':checks,'discrepancies':0,'production_sha256':sha(PROD),'report_sha256':sha(REPORT),'score_matrix_sha256':prod['score_matrix_sha256'],'association_computed':False};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');OUTR.write_text('\n'.join(['# LRG005 D1-specificity capacity validation','',f"Status: **{result['status']}**.",'',f"Independent code reconstructs the complete held-folio two-channel matrix, capacity, gates, hashes, and report in **{checks}** checks with zero discrepancies.",'','No role association was computed.','']),encoding='utf8',newline='\n');print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
