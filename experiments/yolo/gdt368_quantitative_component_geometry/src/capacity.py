#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.vmanus_experiment import canonical_json_bytes,sha256_file  # noqa:E402
EXP=ROOT/'experiments/yolo/gdt368_quantitative_component_geometry';ART=EXP/'artifacts';TARGET=ROOT/'experiments/yolo/gdt367_joint_cell_visual_acquisition/artifacts/gdt367_target_manifest.tsv';OBS=ART/'gdt368_visual_observations.tsv';FREEZE=ART/'gdt368_freeze.json';OUT=ART/'gdt368_capacity.tsv';RESULT=ART/'gdt368_capacity_result.json'
def read(p):
 with p.open(newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 t={r['gdt367_target_id']:r for r in read(TARGET)};o={r['gdt367_target_id']:r for r in read(OBS)};assert len(t)==len(o)==27 and set(t)==set(o)
 axes=['major_body_count','terminal_arm_count','dominant_hue'];out=[]
 for scope,key in [('GLOBAL',None),('FOLIO','physical_folio'),('ARRAY','array_id')]:
  groups={'ALL':list(t)} if key is None else defaultdict(list)
  if key:
   for i,r in t.items():groups[r[key]].append(i)
  for sid,ids in sorted(groups.items()):
   for a in axes:
    c=Counter(o[i][a] for i in ids);secure=[x for x in c if x!='UNCERTAIN'];out.append({'scope':scope,'scope_id':sid,'axis':a.upper(),'n':len(ids),'state_counts_json':json.dumps(dict(sorted(c.items())),separators=(',',':')),'secure_state_count':len(secure),'mobile':int(len(secure)>=2)})
 with OUT.open('w',newline='') as h:w=csv.DictWriter(h,list(out[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(out)
 admitted=[]
 for a in [x.upper() for x in axes]:
  mf=sum(r['mobile'] for r in out if r['scope']=='FOLIO' and r['axis']==a);ma=sum(r['mobile'] for r in out if r['scope']=='ARRAY' and r['axis']==a)
  if mf>=2 and ma>=2:admitted.append(a)
 p={'schema':'GDT368_CAPACITY_V1','status':'QUANTITATIVE_AXES_ADMITTED_FOR_POSTSELECTED_FORMAL_ATLAS' if len(admitted)>=2 else 'INSUFFICIENT_QUANTITATIVE_AXIS_CAPACITY','target_count':27,'admitted_axes':admitted,'formal_rows_loaded_or_joined':False,'formal_search_run':False,'post_image_selection':True,'f84_accessed':False,'inputs':{str(x.relative_to(ROOT)):sha256_file(x) for x in (TARGET,OBS,FREEZE,EXP/'METHOD.md')},'outputs':{str(OUT.relative_to(ROOT)):sha256_file(OUT)},'implementation':{str(Path(__file__).relative_to(ROOT)):sha256_file(Path(__file__))},'claim_ceiling':'VISUAL_CAPACITY_ONLY_BEFORE_FORMAL_ACCESS'};p['content_hash']=hashlib.sha256(canonical_json_bytes(p)).hexdigest();RESULT.write_bytes(canonical_json_bytes(p))
if __name__=='__main__':main()
