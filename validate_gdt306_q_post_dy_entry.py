#!/usr/bin/env python3
"""Validate GDT306 joins, endpoints, exact null and result bindings."""
import csv,hashlib,json,math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PANEL=R/'gdt306_frozen_event_panel.tsv';EVENTS=R/'gdt306_event_endpoints.tsv';SCORES=R/'gdt306_variant_scores.tsv';NULL=R/'gdt306_exact_null.tsv';RESULT=R/'gdt306_result.json';OUT=R/'gdt306_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
checks=[]
def ck(n,v):
 if not v:raise AssertionError(n)
 checks.append(n)
def cells(rows,variant):
 extra=() if variant=='PRIMARY_BASE_CELL' else ('physical_folio',) if variant=='WITHIN_FOLIO' else ('group_count',) if variant=='EXACT_GROUP_COUNT' else ('physical_folio','group_count');d=defaultdict(list)
 for x in rows:d[(x['stratum_id'],*(x[k] for k in extra))].append(x)
 return [v for v in d.values() if {x['wrapper'] for x in v}=={'NONE','q'}]
def tail(cs,endpoint,direction):
 dist={Fraction(0):1};worlds=1
 for rows in cs:
  n=len(rows);nq=sum(x['wrapper']=='q' for x in rows);nn=n-nq;K=sum(int(x[endpoint]) for x in rows);loc=defaultdict(int)
  for k in range(max(0,nq-(n-K)),min(nq,K)+1):loc[direction*(Fraction(k,nq)-Fraction(K-k,nn))]+=math.comb(K,k)*math.comb(n-K,nq-k)
  worlds*=math.comb(n,nq);new=defaultdict(int)
  for a,wa in dist.items():
   for b,wb in loc.items():new[a+b]+=wa*wb
  dist=new
 obs=sum(direction*(Fraction(sum(int(x[endpoint]) for x in r if x['wrapper']=='q'),sum(x['wrapper']=='q' for x in r))-Fraction(sum(int(x[endpoint]) for x in r if x['wrapper']=='NONE'),sum(x['wrapper']=='NONE' for x in r))) for r in cs);ex=sum(w for s,w in dist.items() if s>=obs);return Fraction(ex,worlds),worlds,len(dist)
def main():
 panel={x['observation_id']:x for x in read(PANEL)};source={};line=defaultdict(dict);f84=0
 with SOURCE.open(encoding='utf8',newline='') as h:
  for x in csv.DictReader(h,delimiter='\t'):
   if x['control_id']!='VOYNICH_REFERENCE':continue
   f84+=x['page'].startswith('f84') or x['locus'].startswith('f84');line[x['locus']][int(x['group_index'])]=x
   if x['observation_id'] in panel:source[x['observation_id']]=x
 ck('source_f84_zero',f84==0);out={x['observation_id']:x for x in read(EVENTS)};ck('event_inventory',set(out)==set(panel)==set(source));rows=[]
 for oid,p in panel.items():
  x=source[oid];i=int(x['group_index']);prev=line[x['locus']].get(i-1);dy=int(prev is not None and prev['dy_closure']=='1');start=int(i==1);z=out[oid];ck('event_endpoint',int(z['preceded_by_dy'])==dy and int(z['line_start'])==start and z['previous_observation_id']==(prev['observation_id'] if prev else 'NONE'));rows.append(z)
 sm={(x['variant'],x['endpoint']):x for x in read(SCORES)};nm={(x['variant'],x['endpoint']):x for x in read(NULL)}
 for variant in ('PRIMARY_BASE_CELL','WITHIN_FOLIO','EXACT_GROUP_COUNT','WITHIN_FOLIO_EXACT_GROUP_COUNT'):
  cs=cells(rows,variant)
  for endpoint,direction in (('preceded_by_dy',1),('line_start',-1)):
   p,w,s=tail(cs,endpoint,direction);a=sm[(variant,endpoint.upper())];n=nm[(variant,endpoint.upper())];ck('cell_counts',len(cs)==int(a['matched_cells']) and sum(map(len,cs))==int(a['events']));ck('exact_null',abs(float(a['exact_one_sided_p'])-float(p))<5e-12 and int(n['exact_permutation_worlds'])==w and int(n['distinct_null_states'])==s)
 primary=sm[('PRIMARY_BASE_CELL','PRECEDED_BY_DY')];within=sm[('WITHIN_FOLIO','PRECEDED_BY_DY')];length=sm[('EXACT_GROUP_COUNT','PRECEDED_BY_DY')];g={'primary_delta_positive':float(primary['q_minus_none_delta'])>0,'primary_exact_p_le_0_05':float(primary['exact_one_sided_p'])<=.05,'within_folio_delta_positive':float(within['q_minus_none_delta'])>0,'exact_group_count_delta_positive':float(length['q_minus_none_delta'])>0};status='Q_POST_DY_ENTRY_TRANSFERS' if all(g.values()) else 'Q_POST_DY_ENTRY_WEAK_OR_FAILED';res=json.loads(RESULT.read_text());stored=res.pop('content_sha256');ck('content_hash',stored==can(res));ck('status_gates',res['status']==status and res['gates']==g);ck('input_hashes',all(res['inputs'][n]==sha(R/n) for n in res['inputs']));ck('output_hashes',all(res['outputs'][n]==sha(R/n) for n in res['outputs']));ck('document_hashes',all(res['documents'][n]==sha(R/n) for n in res['documents']));ck('implementation_hash',all(res['implementation'][n]==sha(R/n) for n in res['implementation']));ck('f84_flags',not any(res['f84'].values()));v={'schema':'GDT306_Q_POST_DY_ENTRY_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'result_sha256':sha(RESULT),'reconstructed_status':status,'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'reconstructed_status':status},sort_keys=True))
if __name__=='__main__':main()
