#!/usr/bin/env python3
"""Nonimporting reconstruction of the GDT143 nested relation test."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;INV=R/'gdt140_herbal_relation_inventory.tsv';PAIR=R/'gdt140_pair_similarities.tsv';ORBIT=R/'gdt140_assignment_orbit.tsv';RESULT=R/'gdt143_result.json';MODELS=R/'gdt143_model_scores.tsv';FOLDS=R/'gdt143_fold_predictions.tsv';NULL=R/'gdt143_assignment_scores.tsv';WEIGHTS=R/'gdt143_fold_weights.tsv';COUNTER=R/'gdt143_counterexamples.tsv';OUT=R/'gdt143_validation.json'
REPS=('PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','RAW_CHAR3','COMPILER_SIGNATURE');MODEL_COLS={'HOST_IDENTITY':(0,),'HOST_CHAR3':(1,),'HOST_BOTH':(0,1),'RAW_CHAR3':(2,),'COMPILER':(3,),'ALL_FOUR':(0,1,2,3)};METRICS=('MEAN_RECIPROCAL_RANK','MEAN_LOG2_PROBABILITY','TOP1_COUNT')
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def calc(x,mapping,cols,detail=False):
 rr=[];lp=[];top=[];rows=[];ws=[]
 for hold in range(5):
  tr=[i for i in range(5) if i!=hold];raw=np.array([x[i,j,list(cols)] for i in tr for j in range(5)],float);mu=raw.mean(0);sd=raw.std(0);sd[sd<1e-12]=1
  a=np.array([np.r_[1,(x[i,j,list(cols)]-mu)/sd] for i in tr for j in range(5)]);y=np.array([j==mapping[i] for i in tr for j in range(5)],float);w=np.linalg.solve(a.T@a+np.diag(np.r_[1e-9,np.ones(len(cols))]),a.T@y)
  z=np.array([np.r_[1,(x[hold,j,list(cols)]-mu)/sd]@w for j in range(5)]);p=np.exp(z-z.max());p/=p.sum();actual=mapping[hold];rank=1+int(np.sum(p>p[actual]+1e-12));rr.append(1/rank);lp.append(np.log2(max(p[actual],1e-300)));top.append(rank==1)
  if detail:rows.append((hold,actual,rank,p));ws.append((hold,w,mu,sd))
 return (float(np.mean(rr)),float(np.mean(lp)),int(sum(top))),rows,ws
checks=[]
def ck(n,v,d=''):checks.append({'check':n,'pass':bool(v),'detail':d})
rels=read(INV);pairs=read(PAIR);orbit=read(ORBIT);res=json.loads(RESULT.read_text());src=[x['source_page'] for x in rels];tgt=[x['target_page'] for x in rels]
ck('dimensions',len(rels)==5 and len(pairs)==100 and len(orbit)==120);ck('sealed_absent',not any(x.startswith('f84') for x in src+tgt))
cube=np.zeros((5,5,4))
for q in pairs:cube[src.index(q['source_page']),tgt.index(q['candidate_target_page']),REPS.index(q['representation'])]=float(q['similarity'])
maps=[]
for q in orbit:d=dict(z.split('->') for z in q['mapping'].split('|'));maps.append([tgt.index(d[s]) for s in src])
ti=next(i for i,q in enumerate(orbit) if q['is_true']=='1');scores={}
for m,c in MODEL_COLS.items():
 for i,a in enumerate(maps):scores[(m,i)]=calc(cube,a,c)[0]
published={(x['model'],x['metric']):x for x in read(MODELS)};zall=[];computed={}
for m in MODEL_COLS:
 a=np.array([scores[(m,i)] for i in range(120)],float)
 for k,metric in enumerate(METRICS):
  v=a[:,k];z=(v-v.mean())/(v.std() or 1);computed[(m,metric)]=(v,z);zall.append(z);q=published[(m,metric)]
  exp=(v[ti],v.mean(),v.std(),z[ti],1+int(np.sum(v>v[ti]+1e-12)),float(np.mean(v>=v[ti]-1e-12)))
  got=(float(q['true_value']),float(q['null_mean']),float(q['null_sd']),float(q['true_z']),int(q['inclusive_rank_of_120']),float(q['local_inclusive_p']))
  ck(f'model_{m}_{metric}',all(abs(got[i]-exp[i])<1e-9 for i in range(4)) and got[4]==exp[4] and abs(got[5]-exp[5])<1e-9)
mx=np.max(np.stack(zall),axis=0);max18=float(np.mean(mx>=mx[ti]-1e-12));ck('max18',abs(max18-float(res['max_18_inclusive_p']))<1e-12)
folds={(x['model'],x['held_relation_id']):x for x in read(FOLDS)};weights=read(WEIGHTS)
for m,c in MODEL_COLS.items():
 _,rows,ws=calc(cube,maps[ti],c,True)
 for hold,actual,rank,p in rows:
  q=folds[(m,rels[hold]['relation_id'])];order=sorted(range(5),key=lambda j:(-p[j],tgt[j]));ck(f'fold_{m}_{rels[hold]["relation_id"]}',q['actual_target_page']==tgt[actual] and q['predicted_target_page']==tgt[order[0]] and int(q['actual_rank_of_5'])==rank and abs(float(q['actual_probability'])-p[actual])<1e-9)
 for hold,w,mu,sd in ws:
  got=[q for q in weights if q['model']==m and q['held_relation_id']==rels[hold]['relation_id']];ck(f'weights_{m}_{rels[hold]["relation_id"]}',len(got)==len(w) and all(abs(float(q['weight'])-w[k])<1e-9 for k,q in enumerate(got)))
nrows=read(NULL);ck('null_row_count',len(nrows)==18*120)
for q in nrows:
 i=next(k for k,a in enumerate(orbit) if a['assignment_id']==q['assignment_id']);v,z=computed[(q['model'],q['metric'])];ck(f'null_{q["model"]}_{q["metric"]}_{q["assignment_id"]}',abs(float(q['value'])-v[i])<1e-9 and abs(float(q['standardized_value'])-z[i])<1e-9 and abs(float(q['max_18_standardized_value'])-mx[i])<1e-9)
g={'host_char3_top1_at_least_3':scores[('HOST_CHAR3',ti)][2]>=3,'all_four_top1_at_least_3':scores[('ALL_FOUR',ti)][2]>=3,'host_char3_mrr_local_p_le_0_05':float(published[('HOST_CHAR3','MEAN_RECIPROCAL_RANK')]['local_inclusive_p'])<=.05,'all_four_mrr_local_p_le_0_05':float(published[('ALL_FOUR','MEAN_RECIPROCAL_RANK')]['local_inclusive_p'])<=.05,'max_18_inclusive_p_le_0_05':max18<=.05};status='NESTED_RELATION_PAIR_STRUCTURE_TRANSFERS_WITHIN_EXPOSED_POOL' if all(g.values()) else 'NESTED_RELATION_PAIR_STRUCTURE_NOT_SUPPORTED';ck('status',res['status']==status and res['gates']==g);ck('counterexamples',len(read(COUNTER))==5)
for group in ('inputs','outputs','documents','implementation'):
 for name,h in res[group].items():ck(f'{group}_{name}',sha(R/name)==h)
tmp=dict(res);got=tmp.pop('result_content_sha256');ck('content_hash',csha(tmp)==got)
ok=all(q['pass'] for q in checks);out={'schema':'GDT143_NESTED_RELATION_PAIR_PREDICTION_VALIDATION_V1','status':'PASS_INDEPENDENT_NESTED_REFIT' if ok else 'FAIL','checks_passed':sum(q['pass'] for q in checks),'checks_total':len(checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'checks':checks};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'checks':f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));raise SystemExit(0 if ok else 1)
