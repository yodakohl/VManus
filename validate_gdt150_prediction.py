#!/usr/bin/env python3
"""Independent source-only validation of the GDT150 freeze."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;OCC=R/'gdt149_candidate_host_occurrences.tsv';VIS=R/'gdt137_herbal_visual_feature_inventory.tsv';INV=R/'gdt150_kor_root_targets.tsv';PRED=R/'gdt150_prediction.json';OUT=R/'gdt150_prediction_validation.json'
F=('DAISY_CUP','BROAD_CALYX','GRASS','ROOT_PLATFORM','LEAVES_ONE_SIDE','FUSED_PARALLEL_LEAVES','BULB_OR_TUBER_ROOT','LARGE_OR_EXTENSIVE_ROOT','MULTIPLE_PLANTS','BLUE_FLOWERS_OR_BUDS','FINGERED_OR_FRILLED_LEAVES','MULTIPLE_STEMS_OR_STALKS')
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
checks=[]
def ck(n,x):checks.append({'check':n,'pass':bool(x)})
v={x['page']:x for x in read(VIS)};o=read(OCC);inv=read(INV);p=json.loads(PRED.read_text());pages=sorted({x['page'] for x in o if x['page_host']=='kor' and x['page'] not in {'f90r1','f3v'} and all(v[x['page']][f]=='0' for f in F)})
ck('targets_exact',pages==['f22r','f37r']==[x['page'] for x in inv]);ck('predictions_positive',all(x['frozen_prediction']=='POSITIVE' and x['visual_call']=='SEALED_NOT_REVIEWED' for x in inv));ck('one_kor_occurrence_each',all(sum(x['page_host']=='kor' and x['page']==q for x in o)==1 for q in pages));ck('no_f84',not any(x.startswith('f84') for x in pages));ck('status',p['status']=='FROZEN_BEFORE_TARGET_IMAGE_ACCESS');ck('f84_flags',not any(p['f84'].values()))
for group in ('inputs','outputs','documents','implementation'):
 for name,h in p[group].items():ck(group+'_hash_'+name,sha(R/name)==h)
t=dict(p);got=t.pop('prediction_content_sha256');ck('content_hash',csha(t)==got);ok=all(x['pass'] for x in checks);out={'schema':'GDT150_PREDICTION_VALIDATION_V1','status':'PASS_SOURCE_ONLY_FREEZE' if ok else 'FAIL','checks_passed':sum(x['pass'] for x in checks),'checks_total':len(checks),'prediction_sha256':sha(PRED),'validator_sha256':sha(Path(__file__)),'checks':checks};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'checks':f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));raise SystemExit(0 if ok else 1)
