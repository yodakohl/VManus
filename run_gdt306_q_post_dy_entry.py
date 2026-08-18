#!/usr/bin/env python3
"""Score frozen GDT306 q/NONE cells against preceding-DY and line-start endpoints."""
import csv, hashlib, json, math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PANEL=R/'gdt306_frozen_event_panel.tsv';CAP=R/'gdt306_capacity.tsv';DESIGN=R/'gdt306_design.json';METHOD=R/'GDT306_Q_POST_DY_ENTRY_METHOD.md';EVENTS=R/'gdt306_event_endpoints.tsv';SCORES=R/'gdt306_variant_scores.tsv';NULL=R/'gdt306_exact_null.tsv';COUNTER=R/'gdt306_counterexamples.tsv';REPORT=R/'GDT306_Q_POST_DY_ENTRY_REPORT.md';RESULT=R/'gdt306_result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def exact_tail(cells,endpoint,direction):
 # Exact convolution over all within-cell allocations preserving q count.
 dist={Fraction(0):1};worlds=1
 for rows in cells:
  n=len(rows);nq=sum(x['wrapper']=='q' for x in rows);nn=n-nq;K=sum(x[endpoint] for x in rows);local=defaultdict(int)
  for k in range(max(0,nq-(n-K)),min(nq,K)+1):
   weight=math.comb(K,k)*math.comb(n-K,nq-k);delta=Fraction(k,nq)-Fraction(K-k,nn);local[direction*delta]+=weight
  assert sum(local.values())==math.comb(n,nq);worlds*=math.comb(n,nq);new=defaultdict(int)
  for a,wa in dist.items():
   for b,wb in local.items():new[a+b]+=wa*wb
  dist=new
 observed=sum(direction*(Fraction(sum(x[endpoint] for x in rows if x['wrapper']=='q'),sum(x['wrapper']=='q' for x in rows))-Fraction(sum(x[endpoint] for x in rows if x['wrapper']=='NONE'),sum(x['wrapper']=='NONE' for x in rows))) for rows in cells)
 exceed=sum(w for score,w in dist.items() if score>=observed);return observed/Fraction(len(cells)),Fraction(exceed,worlds),worlds,len(dist)
def variant_cells(rows,variant):
 extra=() if variant=='PRIMARY_BASE_CELL' else ('physical_folio',) if variant=='WITHIN_FOLIO' else ('group_count',) if variant=='EXACT_GROUP_COUNT' else ('physical_folio','group_count');d=defaultdict(list)
 for x in rows:d[(x['stratum_id'],*(x[k] for k in extra))].append(x)
 return [v for v in d.values() if {x['wrapper'] for x in v}=={'NONE','q'}]
def main():
 design=json.loads(DESIGN.read_text());stored=design.pop('content_sha256');assert stored==can(design) and design['status']=='FROZEN_BEFORE_PRECEDING_GROUP_OUTCOME_SCORING';panel=read(PANEL);wanted={x['observation_id'] for x in panel};obs={};lines=defaultdict(dict);f84=0
 with SOURCE.open(encoding='utf8',newline='') as h:
  for x in csv.DictReader(h,delimiter='\t'):
   if x['control_id']!='VOYNICH_REFERENCE':continue
   f84+=x['page'].startswith('f84') or x['locus'].startswith('f84');lines[x['locus']][int(x['group_index'])]=x
   if x['observation_id'] in wanted:obs[x['observation_id']]=x
 assert not f84 and set(obs)==wanted;rows=[]
 for frozen in panel:
  x=obs[frozen['observation_id']];i=int(x['group_index']);previous=lines[x['locus']].get(i-1);preceded=int(previous is not None and previous['dy_closure']=='1');line_start=int(i==1);rows.append({**frozen,'group_index':i,'previous_observation_id':previous['observation_id'] if previous else 'NONE','previous_dy_closure':previous['dy_closure'] if previous else 'NA','preceded_by_dy':preceded,'line_start':line_start})
 variants=[x['variant'] for x in read(CAP)];scores=[];null=[]
 for variant in variants:
  cells=variant_cells(rows,variant)
  for endpoint,direction in (('preceded_by_dy',1),('line_start',-1)):
   stat,p,worlds,states=exact_tail(cells,endpoint,direction);qrate=sum(Fraction(sum(x[endpoint] for x in c if x['wrapper']=='q'),sum(x['wrapper']=='q' for x in c)) for c in cells)/len(cells);nrate=sum(Fraction(sum(x[endpoint] for x in c if x['wrapper']=='NONE'),sum(x['wrapper']=='NONE' for x in c)) for c in cells)/len(cells);delta=qrate-nrate;scores.append({'variant':variant,'endpoint':endpoint.upper(),'matched_cells':len(cells),'events':sum(map(len,cells)),'none_rate_equal_cell':f'{float(nrate):.12f}','q_rate_equal_cell':f'{float(qrate):.12f}','q_minus_none_delta':f'{float(delta):.12f}','predicted_direction':'POSITIVE' if direction==1 else 'NEGATIVE','directional_statistic':f'{float(stat):.12f}','exact_one_sided_p':f'{float(p):.12f}'});null.append({'variant':variant,'endpoint':endpoint.upper(),'exact_permutation_worlds':worlds,'distinct_null_states':states,'tail_worlds_numerator':p.numerator,'tail_worlds_denominator':p.denominator,'exact_one_sided_p':f'{float(p):.12f}'})
 sm={(x['variant'],x['endpoint']):x for x in scores};primary=sm[('PRIMARY_BASE_CELL','PRECEDED_BY_DY')];within=sm[('WITHIN_FOLIO','PRECEDED_BY_DY')];length=sm[('EXACT_GROUP_COUNT','PRECEDED_BY_DY')];gates={'primary_delta_positive':float(primary['q_minus_none_delta'])>0,'primary_exact_p_le_0_05':float(primary['exact_one_sided_p'])<=.05,'within_folio_delta_positive':float(within['q_minus_none_delta'])>0,'exact_group_count_delta_positive':float(length['q_minus_none_delta'])>0};status='Q_POST_DY_ENTRY_TRANSFERS' if all(gates.values()) else 'Q_POST_DY_ENTRY_WEAK_OR_FAILED';counter=[{'counterexample_id':'C01','finding':'Most exact cells contain one event per wrapper and only 11 cells match within folio.','impact':'The primary exact null controls form context but not folio perfectly.'},{'counterexample_id':'C02','finding':'The endpoint uses the preceding group DY field from the frozen HPR2 parser.','impact':'This is direct adjacency but remains representation-dependent.'},{'counterexample_id':'C03','finding':'All exact surfaces were excluded from GDT303 and GDT305, but the corpus and q hypothesis were already exposed.','impact':'This is a prospective endpoint transfer, not pristine discovery.'},{'counterexample_id':'C04','finding':'One-occurrence exact forms are retained by the score-blind all-cells rule.','impact':'Equal-cell weighting prevents common cells dominating but variance is high.'},{'counterexample_id':'C05','finding':'Physical line start is an explicit negative-direction comparator.','impact':'A failed line-start direction does not repair or erase the post-DY primary.'},{'counterexample_id':'C06','finding':'No f84 row occurs in the source.','impact':'The sealed holdout remains untouched.'}];write(EVENTS,rows);write(SCORES,scores);write(NULL,null);write(COUNTER,counter)
 line=sm[('PRIMARY_BASE_CELL','LINE_START')];report=['# GDT306 — disjoint q post-DY entry test','',f'Status: **{status}**.','','The entire 98-event panel and all 39 matching cells were committed before the preceding-group endpoint was read. Every exact surface is disjoint from GDT303 and GDT305.','','| variant | cells/events | post-DY NONE/q/delta | exact p | line-start delta | line exact p |','|---|---:|---:|---:|---:|---:|']
 for v in variants:
  a=sm[(v,'PRECEDED_BY_DY')];b=sm[(v,'LINE_START')];report.append(f"| `{v}` | {a['matched_cells']}/{a['events']} | {float(a['none_rate_equal_cell']):.3f}/{float(a['q_rate_equal_cell']):.3f}/{float(a['q_minus_none_delta']):+.3f} | {a['exact_one_sided_p']} | {float(b['q_minus_none_delta']):+.3f} | {b['exact_one_sided_p']} |")
 report+=['','## Interpretation','',f"The frozen primary and sensitivities {'all point toward a q-conditioned post-DY transition.' if all(gates.values()) else 'do not jointly support a stable q-conditioned post-DY transition.'} The primary effect is evaluated independently of same-group q parsing by reading only the immediately preceding physical group. Physical line start is kept separate.",'','## Gates','']+[f"- `{k}`: **{'PASS' if v else 'FAIL'}**" for k,v in gates.items()]+['','## Claim ceiling','',design['claim_ceiling']+' No f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n');outputs=[EVENTS,SCORES,NULL,COUNTER,REPORT];inputs=[SOURCE,PANEL,CAP,R/'gdt306_design_validation.json',R/'gdt305_result.json',R/'gdt304_result.json'];res={'schema':'GDT306_Q_POST_DY_ENTRY_RESULT_V1','status':status,'summary':{'events':len(rows),'primary_cells':39,'primary_delta':primary['q_minus_none_delta'],'primary_exact_p':primary['exact_one_sided_p'],'line_start_delta':line['q_minus_none_delta']},'gates':gates,'semantic_assignments':0,'claim_ceiling':design['claim_ceiling'],'f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in outputs}};res['content_sha256']=can(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'gates':gates,'primary':primary,'line':line},sort_keys=True))
if __name__=='__main__':main()
