#!/usr/bin/env python3
"""Freeze opaque host features and operation labels for GDT309."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PAIR=R/'gdt303_pair_deltas.tsv';METHOD=R/'GDT309_OPERATION_LICENSE_PREDICTION_METHOD.md';FEATURES=R/'gdt309_host_features.tsv';DESIGN=R/'gdt309_design.json';CAP=R/'gdt309_capacity.tsv'
OPS=('wrapper:ch>s','wrapper:d>s','wrapper:NONE>q')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 rows=[];f84=0
 with SOURCE.open(encoding='utf8',newline='') as h:
  for x in csv.DictReader(h,delimiter='\t'):
   if x['control_id']!='VOYNICH_REFERENCE' or int(x['group_count'])<2:continue
   f84+=x['page'].startswith('f84') or x['locus'].startswith('f84');rows.append(x)
 assert not f84;hf=defaultdict(set);sf=defaultdict(set);sn=Counter()
 for x in rows:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio']);sn[x['source_surface_sha256']]+=1
 forms=defaultdict(set)
 for x in rows:
  if len(hf[x['page_host']])>1 and sn[x['source_surface_sha256']]>=5 and len(sf[x['source_surface_sha256']])>=3:forms[x['page_host']].add(x['source_surface_sha256'])
 universe=sorted(h for h,v in forms.items() if len(v)>=2);assert len(universe)==58;licenses={o:{x['page_host'] for x in read(PAIR) if x['operation']==o} for o in OPS};cats={k:sorted({x[k] for x in rows}) for k in ('section','register','currier','hand')};by=defaultdict(list)
 for x in rows:
  if x['page_host'] in universe:by[x['page_host']].append(x)
 out=[]
 for host in universe:
  z=by[host];n=len(z);folios=len({x['physical_folio'] for x in z});line=Counter('FIRST' if int(x['group_index'])==1 else 'LAST' if int(x['group_index'])==int(x['group_count']) else 'MIDDLE' for x in z);row={'host_id_sha256':hashlib.sha256(host.encode()).hexdigest(),'events':n,'folios':folios,'eligible_forms':len(forms[host]),'frequency_log_events':f'{math.log1p(n):.12f}','frequency_log_folios':f'{math.log1p(folios):.12f}','layout_line_first':f'{line["FIRST"]/n:.12f}','layout_line_middle':f'{line["MIDDLE"]/n:.12f}','layout_line_last':f'{line["LAST"]/n:.12f}','layout_field_first':f'{sum(x["within_field_position"]=="FIRST" for x in z)/n:.12f}','layout_field_last':f'{sum(x["within_field_position"]=="LAST" for x in z)/n:.12f}','layout_record1':f'{sum(int(x["record_ordinal"])==1 for x in z)/n:.12f}','layout_relative_position':f'{sum((int(x["group_index"])-1)/(int(x["group_count"])-1) for x in z)/n:.12f}','compiler_inner_d':f'{sum(x["inner_d"]=="1" for x in z)/n:.12f}','compiler_frame_o':f'{sum(x["local_frame"]=="O" for x in z)/n:.12f}','compiler_frame_ot':f'{sum(x["local_frame"]=="OT" for x in z)/n:.12f}','compiler_right_present':f'{sum(x["right_family"]!="NONE" for x in z)/n:.12f}','compiler_dy':f'{sum(x["dy_closure"]=="1" for x in z)/n:.12f}','compiler_b3':f'{sum(x["b3"]=="1" for x in z)/n:.12f}','compiler_line_close':f'{sum(x["line_close"]=="1" for x in z)/n:.12f}','compiler_paragraph_close':f'{sum(x["paragraph_close"]=="1" for x in z)/n:.12f}'}
  for k in ('section','register','currier','hand'):
   c=Counter(x[k] for x in z)
   for value in cats[k]:row[f'register_{k}_{value}']=f'{c[value]/n:.12f}'
  for op in OPS:row['license_'+op.replace(':','_').replace('>','_to_')]=int(host in licenses[op])
  out.append(row)
 out.sort(key=lambda x:x['host_id_sha256']);write(FEATURES,out);cap=[{'operation':op,'hosts':len(out),'licensed_hosts':sum(host in licenses[op] for host in universe),'unlicensed_hosts':sum(host not in licenses[op] for host in universe)} for op in OPS];write(CAP,cap);feature_names=[k for k in out[0] if k.startswith(('frequency_','layout_','compiler_','register_'))];models={'FREQUENCY':[k for k in feature_names if k.startswith('frequency_')],'LAYOUT':[k for k in feature_names if k.startswith(('frequency_','layout_'))],'COMPILER':[k for k in feature_names if k.startswith(('frequency_','compiler_'))],'REGISTER':[k for k in feature_names if k.startswith(('frequency_','register_'))],'FULL':feature_names};design={'schema':'GDT309_OPERATION_LICENSE_PREDICTION_DESIGN_V1','status':'FROZEN_BEFORE_LICENSE_PREDICTION_SCORING','operations':list(OPS),'host_universe':{'hosts':58,'minimum_eligible_forms':2,'form_minimum_events':5,'form_minimum_folios':3},'models':models,'forbidden_predictors':['PAGE_HOST_IDENTITY','HOST_GLYPHS_OR_SUBSTRINGS','WRAPPER_VALUES_OR_COUNTS','EXACT_SURFACE_IDENTITIES'],'ridge':10.0,'null_worlds':8192,'null_seed':30920260818,'null_strata':'HOST_EVENT_COUNT_QUARTILE','decision':{'full_brier_gain_positive':True,'full_auc_minimum':.65,'full_max12_p_le':.05},'claim_ceiling':'Opaque operation-license structural prediction only; no lexical class grammar semantics sound language plaintext meaning or translation.','f84':{'authorized':False,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (SOURCE,PAIR,METHOD)},'outputs':{p.name:sha(p) for p in (FEATURES,CAP)},'implementation':{Path(__file__).name:sha(Path(__file__))}};design['content_sha256']=can(design);DESIGN.write_text(json.dumps(design,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':design['status'],'hosts':58,'capacity':cap,'features':len(feature_names)},sort_keys=True))
if __name__=='__main__':main()
