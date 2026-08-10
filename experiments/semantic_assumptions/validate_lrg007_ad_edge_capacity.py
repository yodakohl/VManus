#!/usr/bin/env python3
"""Independent reconstruction of LRG007 association-unopened capacity."""
from __future__ import annotations
import csv,hashlib,json
from collections import Counter,defaultdict
from io import StringIO
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;R=HERE/'results';SPEC=HERE/'LRG007_AD_EDGE_TRANSFER_CAPACITY_SPEC.md';BASE=R/'lrg002_prose_slot_capacity.tsv';GROUPS=R/'source_sta_family_consensus_groups.tsv';BASEV=R/'lrg002_prose_slot_capacity_validation.json';PANEL=R/'lrg007_ad_edge_capacity.tsv';MARGINS=R/'lrg007_ad_edge_margins.tsv';PROD=R/'lrg007_ad_edge_capacity.json';REPORT=R/'lrg007_ad_edge_capacity_report.md';OUT=R/'lrg007_ad_edge_capacity_validation.json';OUTR=R/'lrg007_ad_edge_capacity_validation_report.md';checks=0
def need(x,m):
 global checks;checks+=1
 if not x:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ah(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def tab(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def uid(x):return 'LRG007-U'+hashlib.sha256(('LRG007-AD|'+x).encode()).hexdigest()[:20]
def render(fields,rows):
 h=StringIO(newline='');w=csv.DictWriter(h,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return h.getvalue()
def main():
 need(not OUT.exists() and not OUTR.exists(),'validation exists');base=[r for r in tab(BASE) if r['primary_slot_eligible']=='1'];by=defaultdict(list)
 for r in base:by[r['page'],int(r['symbol_count'])].append(r)
 keys=sorted((k for k,v in by.items() if {'FIRST','CORE','LAST'}<={r['segment_position'] for r in v}),key=lambda k:(k[0],k[1]));source={r['consensus_group_id']:r for r in tab(GROUPS)};panel=[];margins=[];features=[]
 for n,k in enumerate(keys,1):
  cid=f'LRG007-C{n:03d}';rows=sorted(by[k],key=lambda r:uid(r['consensus_group_id']));vals=[]
  for r in rows:
   need(r['consensus_group_id'] in source,'join');s=source[r['consensus_group_id']]['family_surface'];a=int(s[0]=='A');d=int(s[0]=='D');need(a+d<=1,'exclusive');vals.append((a,d));features.append((a,d));panel.append({'unit_id':uid(r['consensus_group_id']),'cell_id':cid,'physical_folio':r['physical_folio'],'section':r['section'],'position':r['segment_position']})
  margins.append({'cell_id':cid,'A_rows':sum(a for a,_ in vals),'D_rows':sum(d for _,d in vals),'other_rows':sum(not(a or d) for a,d in vals),'total_rows':len(vals)})
 x=np.asarray(features,dtype=np.int8);variable={f:sum(0<int(q[f'{f}_rows'])<int(q['total_rows']) for q in margins) for f in ('A','D')};folios={f:len({p['physical_folio'] for p,v in zip(panel,x[:,j],strict=True) if v}) for j,f in enumerate(('A','D'))};counts={'rows':len(panel),'cells':len(margins),'pages':len({r['page'] for k in keys for r in by[k]}),'folios':len({p['physical_folio'] for p in panel}),'sections':dict(sorted(Counter(p['section'] for p in panel).items())),'positions':dict(sorted(Counter(p['position'] for p in panel).items())),'A_rows_aggregate_only':int(x[:,0].sum()),'D_rows_aggregate_only':int(x[:,1].sum()),'A_variable_cells':variable['A'],'D_variable_cells':variable['D'],'A_folios':folios['A'],'D_folios':folios['D']};gates={'exact_geometry':(counts['rows'],counts['cells'],counts['pages'],counts['folios'])==(4911,132,34,16),'both_sections':set(counts['sections'])=={'B','P'},'all_positions':set(counts['positions'])=={'FIRST','CORE','LAST'},'A_capacity':counts['A_rows_aggregate_only']>=100 and variable['A']>=30 and folios['A']>=12,'D_capacity':counts['D_rows_aggregate_only']>=100 and variable['D']>=30 and folios['D']>=12,'mutually_exclusive':not np.any(x.sum(1)>1),'association_not_computed':True};pt=render(('unit_id','cell_id','physical_folio','section','position'),panel);qt=render(('cell_id','A_rows','D_rows','other_rows','total_rows'),margins);need(PANEL.read_text()==pt and MARGINS.read_text()==qt,'tables');expected={'status':'PASS_ASSOCIATION_UNOPENED_LRG007_CAPACITY','decision':'GO_TARGET_BLIND_AD_EDGE_CALIBRATION','claim_ceiling':'Capacity for an A/D initial-family prose-edge transfer test only; no position association opening closing word function meaning plaintext or translation.','inputs':{'base':sha(BASE),'groups':sha(GROUPS),'base_validation':sha(BASEV)},'spec_sha256':sha(SPEC),'counts':counts,'gates':gates,'panel_sha256':sha(PANEL),'margins_sha256':sha(MARGINS),'feature_matrix_sha256':ah(x),'family_position_association_computed':False,'row_families_emitted':False,'source_ids_emitted':False};need(json.loads(PROD.read_text())==expected,'result');report='\n'.join(['# LRG007 A/D edge-transfer capacity','',f"Status: **{expected['status']}**.",'',f"The immutable page-by-length geometry retains **{counts['rows']}** rows in **{counts['cells']}** cells on **{counts['folios']}** folios. Aggregate-only initial-family totals are A **{counts['A_rows_aggregate_only']}** and D **{counts['D_rows_aggregate_only']}**; they vary in **{variable['A']}** and **{variable['D']}** cells.",'','No family-by-position association was computed. Decision: **GO_TARGET_BLIND_AD_EDGE_CALIBRATION**.','','No opening, closing, word, function, meaning, plaintext, or translation follows.','']);need(REPORT.read_text()==report,'report');result={'status':'PASS_CLEAN_LRG007_CAPACITY_RECONSTRUCTION','checks':checks,'discrepancies':0,'production_sha256':sha(PROD),'panel_sha256':sha(PANEL),'margins_sha256':sha(MARGINS)};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');OUTR.write_text('\n'.join(['# LRG007 capacity validation','',f"Status: **{result['status']}**.",'',f"Independent code reconstructs selection, opaque rows, margins, feature hashes, gates, result, and report in **{checks}** checks with zero discrepancies.",'','No family-by-position association was computed.','']),encoding='utf8',newline='\n');print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
