#!/usr/bin/env python3
"""Independent exact reconstruction of GDT146."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;META=R/'gdt137_herbal_visual_feature_inventory.tsv';INV=R/'gdt140_herbal_relation_inventory.tsv';ORBIT=R/'gdt140_assignment_orbit.tsv';SCORES=R/'gdt146_visual_scores.tsv';MATRIX=R/'gdt146_visual_pair_matrix.tsv';NULL=R/'gdt146_assignment_scores.tsv';RESULT=R/'gdt146_result.json';OUT=R/'gdt146_validation.json';FEATURES=('DAISY_CUP','BROAD_CALYX','GRASS','ROOT_PLATFORM','LEAVES_ONE_SIDE','FUSED_PARALLEL_LEAVES','BULB_OR_TUBER_ROOT','LARGE_OR_EXTENSIVE_ROOT','MULTIPLE_PLANTS','BLUE_FLOWERS_OR_BUDS','FINGERED_OR_FRILLED_LEAVES','MULTIPLE_STEMS_OR_STALKS');MODES=('POSITIVE_JACCARD','BIT_AGREEMENT','EXACT_ILLUSTRATION_PROFILE')
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v),'detail':''})
meta={x['page']:x for x in read(META)};rels=read(INV);orbit=read(ORBIT);s=[x['source_page'] for x in rels];t=[x['target_page'] for x in rels];maps=[]
for x in orbit:d=dict(z.split('->') for z in x['mapping'].split('|'));maps.append([t.index(d[a]) for a in s])
ti=next(i for i,x in enumerate(orbit) if x['is_true']=='1');m={q:np.zeros((5,5)) for q in MODES}
for i,a in enumerate(s):
 av=np.array([int(meta[a][f]) for f in FEATURES])
 for j,b in enumerate(t):
  bv=np.array([int(meta[b][f]) for f in FEATURES]);u=np.sum((av==1)|(bv==1));m['POSITIVE_JACCARD'][i,j]=np.sum((av==1)&(bv==1))/u if u else 0;m['BIT_AGREEMENT'][i,j]=np.mean(av==bv);m['EXACT_ILLUSTRATION_PROFILE'][i,j]=meta[a]['illustration_profile']==meta[b]['illustration_profile']
pub={x['mode']:x for x in read(SCORES)};computed={}
for mode in MODES:
 v=np.array([sum(m[mode][i,j] for i,j in enumerate(q))/5 for q in maps]);tv=v[ti];exp=(tv,v.mean(),v.std(),1+int(np.sum(v>tv+1e-12)),float(np.mean(v>=tv-1e-12)));got=(float(pub[mode]['true_score']),float(pub[mode]['null_mean']),float(pub[mode]['null_sd']),int(pub[mode]['inclusive_rank_of_120']),float(pub[mode]['inclusive_p']));ck('score_'+mode,all(abs(got[k]-exp[k])<1e-9 for k in (0,1,2,4)) and got[3]==exp[3]);computed[mode]=v
ck('matrix_rows',len(read(MATRIX))==75);nrows=read(NULL);ck('null_rows',len(nrows)==360)
for q in nrows:
 i=next(k for k,a in enumerate(orbit) if a['assignment_id']==q['assignment_id']);ck('null_'+q['mode']+'_'+q['assignment_id'],abs(float(q['score'])-computed[q['mode']][i])<1e-9)
res=json.loads(RESULT.read_text());status='COARSE_VISUAL_PROFILE_DOES_NOT_EXPLAIN_RELATION_ASSIGNMENT' if all(float(pub[x]['inclusive_p'])>.05 for x in MODES) else 'COARSE_VISUAL_PROFILE_POTENTIAL_CONFOUND';ck('decision',res['status']==status);ck('sealed',not any(x.startswith('f84') for x in s+t))
for group in ('inputs','outputs','documents','implementation'):
 for name,h in res[group].items():ck(group+'_'+name,sha(R/name)==h)
tmp=dict(res);got=tmp.pop('result_content_sha256');ck('content_hash',csha(tmp)==got)
ok=all(x['pass'] for x in checks);out={'schema':'GDT146_RELATION_COARSE_VISUAL_CONFOUND_VALIDATION_V1','status':'PASS_INDEPENDENT_EXACT_RECONSTRUCTION' if ok else 'FAIL','checks_passed':sum(x['pass'] for x in checks),'checks_total':len(checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'checks':checks};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'checks':f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));raise SystemExit(0 if ok else 1)
