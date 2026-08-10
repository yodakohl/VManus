#!/usr/bin/env python3
"""Build the role-association-unopened LRG006 A1 member panel."""
from __future__ import annotations
import csv,hashlib,json,os,re
from collections import Counter,defaultdict
from io import StringIO
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;R=HERE/'results';SPEC=HERE/'LRG006_A1_MEMBER_CAPACITY_SPEC.md';G=R/'source_sta_family_consensus_groups.tsv';C=R/'lrg001_label_register_capacity.tsv';OUTP=R/'lrg006_a1_member_capacity.tsv';OUTQ=R/'lrg006_a1_member_quotas.tsv';OUT=R/'lrg006_a1_member_capacity.json';REPORT=R/'lrg006_a1_member_capacity_report.md';F=('zl_sta_codes','it_sta_codes','rf_sta_codes');EXPECTED={'groups':'a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225','capacity':'abec3385838cf9218db34bda108288f680a9b8482c7b7e47d3fb83c711998536'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tab(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def fol(p):
 m=re.fullmatch(r'(f\d+)(?:[rv](?:\d+)?)?',p)
 if not m:raise RuntimeError('page')
 return m.group(1)
def uid(x):return 'LRG006-U'+hashlib.sha256(('LRG006-A1|'+x).encode()).hexdigest()[:20]
def a1(r):return all(r[f].split()[0]=='A1' for f in F)
def text(fields,rows):
 h=StringIO(newline='');w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return h.getvalue()
def atomic(p,s):
 if p.exists():raise RuntimeError('output exists')
 q=p.with_suffix(p.suffix+'.tmp');q.write_text(s,encoding='utf8',newline='\n');os.link(q,p);q.unlink()
def main():
 outputs=(OUTP,OUTQ,OUT,REPORT)
 if any(p.exists() for p in outputs):raise RuntimeError('outputs exist')
 observed={'groups':sha(G),'capacity':sha(C)}
 if observed!=EXPECTED:raise RuntimeError('input drift')
 cells={(r['page'],int(r['symbol_count'])) for r in tab(C) if r['section'] in {'B','P'}};groups=tab(G);byfam={x:defaultdict(list) for x in ('A','D')}
 for r in groups:
  role='L' if r['kind']=='L' else 'P' if r['kind']=='P' and r['grammar_scope']=='CONFIRMED_PROSE' else ''
  if r['strict_zero_alternative']!='1' or not role or (r['page'],int(r['symbol_count'])) not in cells:continue
  for family in ('A','D'):
   if r['family_surface'].startswith(family):byfam[family][r['page'],int(r['symbol_count'])].append((r,role))
 mixed={f:{k:v for k,v in byfam[f].items() if {role for _,role in v}=={'L','P'}} for f in ('A','D')};drows=[z for v in mixed['D'].values() for z in v];dcats={tuple(r[f].split()[0] for f in F) for r,_ in drows};dstop=len(drows)<100 or sum(role=='L' for _,role in drows)<10 or len({fol(r['page']) for r,_ in drows})<5 or len(dcats)<2
 keys=sorted(mixed['A'],key=lambda k:(fol(k[0]),k[0],k[1]));panel=[];quotas=[];feature=[];seen=set();variable=set()
 for n,k in enumerate(keys,1):
  cid=f'LRG006-C{n:03d}';values=sorted(mixed['A'][k],key=lambda z:uid(z[0]['consensus_group_id']));roles=Counter(role for _,role in values);states=[]
  for r,_role in values:
   u=uid(r['consensus_group_id'])
   if u in seen:raise RuntimeError('collision')
   seen.add(u);state=a1(r);states.append(state);feature.append(state);panel.append({'unit_id':u,'cell_id':cid,'physical_folio':fol(r['page']),'section':r['section']})
  if len(set(states))==2:variable.add(cid)
  quotas.append({'cell_id':cid,'label_rows':roles['L'],'prose_rows':roles['P'],'total_rows':len(values)})
 qmap={r['cell_id']:r for r in quotas};vr=sum(int(qmap[c]['total_rows']) for c in variable);vf={r['physical_folio'] for r in panel if r['cell_id'] in variable};vs=Counter(next(r['section'] for r in panel if r['cell_id']==c) for c in variable);labels=sum(int(r['label_rows']) for r in quotas);controls=sum(int(r['prose_rows']) for r in quotas);x=np.asarray(feature,dtype=np.int8);gates={'at_least_650_rows':len(panel)>=650,'at_least_150_labels':labels>=150,'at_least_500_prose':controls>=500,'at_least_65_cells':len(quotas)>=65,'all_13_folios':len({r['physical_folio'] for r in panel})==13,'at_least_50_variable_cells':len(variable)>=50,'at_least_575_variable_rows':vr>=575,'both_sections_variable':set(vs)=={'B','P'},'D_member_branch_stopped':dstop,'association_not_computed':True}
 if not all(gates.values()):raise RuntimeError(gates)
 pt=text(('unit_id','cell_id','physical_folio','section'),panel);qt=text(('cell_id','label_rows','prose_rows','total_rows'),quotas);atomic(OUTP,pt);atomic(OUTQ,qt);result={'status':'PASS_ASSOCIATION_UNOPENED_A1_MEMBER_CAPACITY_D_MEMBER_STOP','decision':'GO_TARGET_FREE_A1_CALIBRATION_ONLY','claim_ceiling':'Capacity only for an A1-versus-other-A conditional member test; D member mining stops. No sound word POS function meaning plaintext or translation.','inputs':observed,'spec_sha256':sha(SPEC),'counts':{'A_rows':len(panel),'A_label_rows_aggregate_only':labels,'A_prose_rows_aggregate_only':controls,'A_cells':len(quotas),'A_folios':len({r['physical_folio'] for r in panel}),'A1_rows_aggregate_only':int(x.sum()),'other_A_rows_aggregate_only':int(len(x)-x.sum()),'variable_cells':len(variable),'variable_rows':vr,'variable_folios':len(vf),'variable_cells_by_section':dict(sorted(vs.items())),'D_mixed_rows':len(drows),'D_label_rows':sum(role=='L' for _,role in drows),'D_cells':len(mixed['D']),'D_folios':len({fol(r['page']) for r,_ in drows}),'D_member_triplets':len(dcats)},'gates':gates,'panel_sha256':sha(OUTP),'quotas_sha256':sha(OUTQ),'feature_vector_sha256':hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest(),'role_feature_contrast_computed':False,'row_roles_emitted':False,'member_codes_emitted':False};atomic(OUT,json.dumps(result,indent=2,sort_keys=True)+'\n');atomic(REPORT,'\n'.join(['# LRG006 A1 member capacity','',f"Status: **{result['status']}**.",'',f"The A branch retains **{len(panel)}** rows (**{labels}** label / **{controls}** prose aggregate quotas) in **{len(quotas)}** cells on **13** folios. A1 totals **{int(x.sum())}** rows versus **{int(len(x)-x.sum())}** other-A rows; the feature varies in **{len(variable)}** cells containing **{vr}** rows.",'',f"The D branch stops: **{len(drows)}** rows, **{sum(role=='L' for _,role in drows)}** labels, **{len(mixed['D'])}** cells, **{len({fol(r['page']) for r,_ in drows})}** folios, and **{len(dcats)}** member triplet.",'','No role-by-feature contrast was computed. Decision: **GO_TARGET_FREE_A1_CALIBRATION_ONLY**.','','No sound, word, POS, function, meaning, plaintext, or translation follows.','']));print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
