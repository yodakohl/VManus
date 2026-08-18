#!/usr/bin/env python3
"""Freeze target-blind source-wrapper host features for GDT310."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';PAIR=R/'gdt303_pair_deltas.tsv';BASE=R/'gdt309_host_features.tsv';METHOD=R/'GDT310_SOURCE_SIDE_OPERATION_LICENSE_METHOD.md';FEATURES=R/'gdt310_source_side_features.tsv';CAP=R/'gdt310_capacity.tsv';DESIGN=R/'gdt310_design.json';OPS={'wrapper:NONE>q':'NONE','wrapper:ch>s':'ch','wrapper:d>s':'d'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 allowed_hash={x['host_id_sha256'] for x in read(BASE)};rows=[];f84=0
 with SOURCE.open(encoding='utf8',newline='') as h:
  for x in csv.DictReader(h,delimiter='\t'):
   if x['control_id']!='VOYNICH_REFERENCE' or int(x['group_count'])<2:continue
   f84+=x['page'].startswith('f84') or x['locus'].startswith('f84')
   if hashlib.sha256(x['page_host'].encode()).hexdigest() in allowed_hash:rows.append(x)
 assert not f84;licenses={op:{x['page_host'] for x in read(PAIR) if x['operation']==op} for op in OPS};cats={k:sorted({x[k] for x in rows}) for k in ('section','register','currier','hand')};out=[];cap=[]
 for op,source_wrapper in OPS.items():
  by=defaultdict(list)
  for x in rows:
   if x['wrapper']==source_wrapper:by[x['page_host']].append(x)
  eligible={h:z for h,z in by.items() if len(z)>=5 and len({x['physical_folio'] for x in z})>=3};cap.append({'operation':op,'source_wrapper':source_wrapper,'hosts':len(eligible),'licensed_hosts':sum(h in licenses[op] for h in eligible),'unlicensed_hosts':sum(h not in licenses[op] for h in eligible),'source_events':sum(map(len,eligible.values()))})
  for host,z in eligible.items():
   n=len(z);folios=len({x['physical_folio'] for x in z});line=Counter('FIRST' if int(x['group_index'])==1 else 'LAST' if int(x['group_index'])==int(x['group_count']) else 'MIDDLE' for x in z);row={'operation':op,'source_wrapper':source_wrapper,'host_id_sha256':hashlib.sha256(host.encode()).hexdigest(),'licensed':int(host in licenses[op]),'source_events':n,'source_folios':folios,'frequency_log_events':f'{math.log1p(n):.12f}','frequency_log_folios':f'{math.log1p(folios):.12f}','layout_line_first':f'{line["FIRST"]/n:.12f}','layout_line_middle':f'{line["MIDDLE"]/n:.12f}','layout_line_last':f'{line["LAST"]/n:.12f}','layout_field_first':f'{sum(x["within_field_position"]=="FIRST" for x in z)/n:.12f}','layout_field_last':f'{sum(x["within_field_position"]=="LAST" for x in z)/n:.12f}','layout_record1':f'{sum(int(x["record_ordinal"])==1 for x in z)/n:.12f}','layout_relative_position':f'{sum((int(x["group_index"])-1)/(int(x["group_count"])-1) for x in z)/n:.12f}','compiler_inner_d':f'{sum(x["inner_d"]=="1" for x in z)/n:.12f}','compiler_frame_o':f'{sum(x["local_frame"]=="O" for x in z)/n:.12f}','compiler_frame_ot':f'{sum(x["local_frame"]=="OT" for x in z)/n:.12f}','compiler_right_present':f'{sum(x["right_family"]!="NONE" for x in z)/n:.12f}','compiler_dy':f'{sum(x["dy_closure"]=="1" for x in z)/n:.12f}','compiler_b3':f'{sum(x["b3"]=="1" for x in z)/n:.12f}','compiler_line_close':f'{sum(x["line_close"]=="1" for x in z)/n:.12f}','compiler_paragraph_close':f'{sum(x["paragraph_close"]=="1" for x in z)/n:.12f}'}
   for k in ('section','register','currier','hand'):
    c=Counter(x[k] for x in z)
    for value in cats[k]:row[f'register_{k}_{value}']=f'{c[value]/n:.12f}'
   out.append(row)
 out.sort(key=lambda x:(x['operation'],x['host_id_sha256']));write(FEATURES,out);write(CAP,cap);names=[k for k in out[0] if k.startswith(('frequency_','layout_','compiler_','register_'))];models={'FREQUENCY':[k for k in names if k.startswith('frequency_')],'LAYOUT':[k for k in names if k.startswith(('frequency_','layout_'))],'COMPILER':[k for k in names if k.startswith(('frequency_','compiler_'))],'REGISTER':[k for k in names if k.startswith(('frequency_','register_'))],'FULL':names};design={'schema':'GDT310_SOURCE_SIDE_OPERATION_LICENSE_DESIGN_V1','status':'FROZEN_BEFORE_TARGET_BLIND_LICENSE_SCORING','operations':OPS,'minimum_source_events':5,'minimum_source_folios':3,'models':models,'forbidden_predictors':['TARGET_WRAPPER_EVENTS','WRAPPER_COUNTS','PAGE_HOST_IDENTITY','HOST_GLYPHS_OR_SUBSTRINGS','EXACT_SURFACE_IDENTITIES'],'ridge':10.0,'prediction_clip':[.01,.99],'null_worlds':8192,'null_seed':31020260818,'null_strata':'OPERATION_SPECIFIC_SOURCE_EVENT_COUNT_QUARTILE','decision':{'full_brier_gain_positive':True,'full_auc_minimum':.65,'full_max12_p_le':.05},'claim_ceiling':'Target-blind formal alternant-license prediction only; no lexical class grammar semantics sound language plaintext meaning or translation.','f84':{'authorized':False,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (SOURCE,PAIR,BASE,METHOD)},'outputs':{p.name:sha(p) for p in (FEATURES,CAP)},'implementation':{Path(__file__).name:sha(Path(__file__))}};design['content_sha256']=can(design);DESIGN.write_text(json.dumps(design,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':design['status'],'capacity':cap,'rows':len(out)},sort_keys=True))
if __name__=='__main__':main()
