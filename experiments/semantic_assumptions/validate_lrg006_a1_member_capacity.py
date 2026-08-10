#!/usr/bin/env python3
"""Independent byte reconstruction of LRG006 capacity."""
from __future__ import annotations
import csv,hashlib,json,re
from collections import Counter,defaultdict
from io import StringIO
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;R=HERE/'results';G=R/'source_sta_family_consensus_groups.tsv';C=R/'lrg001_label_register_capacity.tsv';P=R/'lrg006_a1_member_capacity.tsv';Q=R/'lrg006_a1_member_quotas.tsv';PROD=R/'lrg006_a1_member_capacity.json';REPORT=R/'lrg006_a1_member_capacity_report.md';OUT=R/'lrg006_a1_member_capacity_validation.json';OUTR=R/'lrg006_a1_member_capacity_validation_report.md';F=('zl_sta_codes','it_sta_codes','rf_sta_codes');checks=0
def need(x,m):
 global checks;checks+=1
 if not x:raise RuntimeError(m)
def tab(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def fol(p):m=re.fullmatch(r'(f\d+)(?:[rv](?:\d+)?)?',p);need(m is not None,'page');return m.group(1)
def uid(x):return 'LRG006-U'+hashlib.sha256(('LRG006-A1|'+x).encode()).hexdigest()[:20]
def txt(fields,rows):h=StringIO(newline='');w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return h.getvalue()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 cells={(r['page'],int(r['symbol_count'])) for r in tab(C) if r['section'] in {'B','P'}};groups=tab(G);bf={x:defaultdict(list) for x in ('A','D')}
 for r in groups:
  role='L' if r['kind']=='L' else 'P' if r['kind']=='P' and r['grammar_scope']=='CONFIRMED_PROSE' else ''
  if r['strict_zero_alternative']=='1' and role and (r['page'],int(r['symbol_count'])) in cells:
   for f in ('A','D'):
    if r['family_surface'].startswith(f):bf[f][r['page'],int(r['symbol_count'])].append((r,role))
 mixed={f:{k:v for k,v in bf[f].items() if {z for _,z in v}=={'L','P'}} for f in ('A','D')};d=[z for v in mixed['D'].values() for z in v];dc={tuple(r[f].split()[0] for f in F) for r,_ in d};keys=sorted(mixed['A'],key=lambda k:(fol(k[0]),k[0],k[1]));panel=[];quotas=[];x=[];var=set();seen=set()
 for n,k in enumerate(keys,1):
  cid=f'LRG006-C{n:03d}';vals=sorted(mixed['A'][k],key=lambda z:uid(z[0]['consensus_group_id']));roles=Counter(z for _,z in vals);states=[]
  for r,_ in vals:
   u=uid(r['consensus_group_id']);need(u not in seen,'collision');seen.add(u);s=all(r[f].split()[0]=='A1' for f in F);states.append(s);x.append(s);panel.append({'unit_id':u,'cell_id':cid,'physical_folio':fol(r['page']),'section':r['section']})
  if len(set(states))==2:var.add(cid)
  quotas.append({'cell_id':cid,'label_rows':roles['L'],'prose_rows':roles['P'],'total_rows':len(vals)})
 need(P.read_text()==txt(('unit_id','cell_id','physical_folio','section'),panel),'panel');need(Q.read_text()==txt(('cell_id','label_rows','prose_rows','total_rows'),quotas),'quota');qm={r['cell_id']:r for r in quotas};vr=sum(int(qm[c]['total_rows']) for c in var);vf={r['physical_folio'] for r in panel if r['cell_id'] in var};vs=Counter(next(r['section'] for r in panel if r['cell_id']==c) for c in var);labels=sum(int(r['label_rows']) for r in quotas);controls=sum(int(r['prose_rows']) for r in quotas);a=np.asarray(x,dtype=np.int8);prod=json.loads(PROD.read_text());counts={'A_rows':len(panel),'A_label_rows_aggregate_only':labels,'A_prose_rows_aggregate_only':controls,'A_cells':len(quotas),'A_folios':len({r['physical_folio'] for r in panel}),'A1_rows_aggregate_only':int(a.sum()),'other_A_rows_aggregate_only':int(len(a)-a.sum()),'variable_cells':len(var),'variable_rows':vr,'variable_folios':len(vf),'variable_cells_by_section':dict(sorted(vs.items())),'D_mixed_rows':len(d),'D_label_rows':sum(z=='L' for _,z in d),'D_cells':len(mixed['D']),'D_folios':len({fol(r['page']) for r,_ in d}),'D_member_triplets':len(dc)};need(prod['counts']==counts,'counts');need(prod['feature_vector_sha256']==hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest(),'feature');need(prod['panel_sha256']==sha(P) and prod['quotas_sha256']==sha(Q),'hashes');need(prod['status']=='PASS_ASSOCIATION_UNOPENED_A1_MEMBER_CAPACITY_D_MEMBER_STOP' and all(prod['gates'].values()),'status');need(prod['role_feature_contrast_computed'] is False,'boundary');expected='\n'.join(['# LRG006 A1 member capacity','',f"Status: **{prod['status']}**.",'',f"The A branch retains **{len(panel)}** rows (**{labels}** label / **{controls}** prose aggregate quotas) in **{len(quotas)}** cells on **13** folios. A1 totals **{int(a.sum())}** rows versus **{int(len(a)-a.sum())}** other-A rows; the feature varies in **{len(var)}** cells containing **{vr}** rows.",'',f"The D branch stops: **{len(d)}** rows, **{sum(z=='L' for _,z in d)}** labels, **{len(mixed['D'])}** cells, **{len({fol(r['page']) for r,_ in d})}** folios, and **{len(dc)}** member triplet.",'','No role-by-feature contrast was computed. Decision: **GO_TARGET_FREE_A1_CALIBRATION_ONLY**.','','No sound, word, POS, function, meaning, plaintext, or translation follows.','']);need(REPORT.read_text()==expected,'report');result={'status':'PASS_CLEAN_LRG006_CAPACITY_RECONSTRUCTION','checks':checks,'discrepancies':0,'production_sha256':sha(PROD),'panel_sha256':sha(P),'quotas_sha256':sha(Q),'feature_vector_sha256':prod['feature_vector_sha256'],'association_computed':False};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');OUTR.write_text('\n'.join(['# LRG006 capacity validation','',f"Status: **{result['status']}**.",'',f"Independent code reconstructs the A and D branches, opaque panel, quotas, feature hash, gates, stop, and report in **{checks}** checks with zero discrepancies.",'','The A1 role association remains unopened.','']),encoding='utf8',newline='\n');print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
