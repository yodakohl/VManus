#!/usr/bin/env python3
"""Nested leave-one-relation prediction over the exact GDT140 assignment orbit."""
import csv,hashlib,json
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parent;INV=R/'gdt140_herbal_relation_inventory.tsv';PAIR=R/'gdt140_pair_similarities.tsv';ORBIT=R/'gdt140_assignment_orbit.tsv';PARENT=R/'gdt140_result.json';ROBUST=R/'gdt142_result.json';METHOD=R/'GDT143_NESTED_RELATION_PAIR_PREDICTION_METHOD.md';REPORT=R/'GDT143_NESTED_RELATION_PAIR_PREDICTION_REPORT.md';MODELS=R/'gdt143_model_scores.tsv';FOLDS=R/'gdt143_fold_predictions.tsv';NULL=R/'gdt143_assignment_scores.tsv';WEIGHTS=R/'gdt143_fold_weights.tsv';COUNTER=R/'gdt143_counterexamples.tsv';RESULT=R/'gdt143_result.json'
REPS=('PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','RAW_CHAR3','COMPILER_SIGNATURE')
MODEL_COLS={'HOST_IDENTITY':(0,),'HOST_CHAR3':(1,),'HOST_BOTH':(0,1),'RAW_CHAR3':(2,),'COMPILER':(3,),'ALL_FOUR':(0,1,2,3)}
METRICS=('MEAN_RECIPROCAL_RANK','MEAN_LOG2_PROBABILITY','TOP1_COUNT')
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def clean(rows):return [{k:f'{v:.12g}' if isinstance(v,float) else v for k,v in x.items()} for x in rows]
def fit_world(x,mapping,cols,details=False):
 rr=[];lp=[];top=[];folds=[];weights=[]
 for hold in range(5):
  train=[i for i in range(5) if i!=hold]
  raw=np.array([x[i,j,list(cols)] for i in train for j in range(5)],float);mu=raw.mean(0);sd=raw.std(0);sd[sd<1e-12]=1
  a=np.array([np.r_[1,(x[i,j,list(cols)]-mu)/sd] for i in train for j in range(5)])
  y=np.array([j==mapping[i] for i in train for j in range(5)],float)
  penalty=np.diag(np.r_[1e-9,np.ones(len(cols))]);w=np.linalg.solve(a.T@a+penalty,a.T@y)
  z=np.array([np.r_[1,(x[hold,j,list(cols)]-mu)/sd]@w for j in range(5)])
  p=np.exp(z-z.max());p/=p.sum();actual=mapping[hold];rank=1+int(np.sum(p>p[actual]+1e-12))
  rr.append(1/rank);lp.append(float(np.log2(max(p[actual],1e-300))));top.append(rank==1)
  if details:
   folds.append((hold,actual,rank,p,z));weights.append((hold,w,mu,sd))
 return (float(np.mean(rr)),float(np.mean(lp)),int(sum(top))),folds,weights

rels=read(INV);pairs=read(PAIR);orbit=read(ORBIT);sources=[x['source_page'] for x in rels];targets=[x['target_page'] for x in rels]
assert len(rels)==5 and len(pairs)==100 and len(orbit)==120 and not any(x.startswith('f84') for x in sources+targets)
cube=np.zeros((5,5,4))
for q in pairs:cube[sources.index(q['source_page']),targets.index(q['candidate_target_page']),REPS.index(q['representation'])]=float(q['similarity'])
maps=[]
for q in orbit:
 d=dict(z.split('->') for z in q['mapping'].split('|'));maps.append([targets.index(d[s]) for s in sources])
ti=next(i for i,q in enumerate(orbit) if q['is_true']=='1')

scores={};fold_rows=[];weight_rows=[]
for model,cols in MODEL_COLS.items():
 for i,m in enumerate(maps):scores[(model,i)]=fit_world(cube,m,cols)[0]
 vals=scores[(model,ti)];detail=fit_world(cube,maps[ti],cols,True)
 for hold,actual,rank,p,z in detail[1]:
  order=sorted(range(5),key=lambda j:(-p[j],targets[j]));fold_rows.append({'model':model,'held_relation_id':rels[hold]['relation_id'],'held_source_page':sources[hold],'actual_target_page':targets[actual],'predicted_target_page':targets[order[0]],'actual_rank_of_5':rank,'actual_probability':float(p[actual]),'top2_targets':'|'.join(targets[j] for j in order[:2]),'candidate_probabilities':'|'.join(f'{targets[j]}:{p[j]:.12g}' for j in range(5))})
 for hold,w,mu,sd in detail[2]:
  for k,val in enumerate(w):weight_rows.append({'model':model,'held_relation_id':rels[hold]['relation_id'],'coefficient':'INTERCEPT' if k==0 else REPS[cols[k-1]],'weight':float(val),'training_mean':'NA' if k==0 else float(mu[k-1]),'training_sd':'NA' if k==0 else float(sd[k-1])})

zs=[];model_rows=[];assignment_rows=[]
for model in MODEL_COLS:
 arr=np.array([scores[(model,i)] for i in range(120)],float)
 for k,metric in enumerate(METRICS):
  v=arr[:,k];z=(v-v.mean())/(v.std() or 1);zs.append(z);tv=float(v[ti]);model_rows.append({'model':model,'metric':metric,'true_value':tv,'null_mean':float(v.mean()),'null_sd':float(v.std()),'true_z':float(z[ti]),'inclusive_rank_of_120':1+int(np.sum(v>tv+1e-12)),'local_inclusive_p':float(np.mean(v>=tv-1e-12)),'max_18_inclusive_p':'PENDING'})
  for i,q in enumerate(orbit):assignment_rows.append({'model':model,'metric':metric,'assignment_id':q['assignment_id'],'is_true':q['is_true'],'value':float(v[i]),'standardized_value':float(z[i]),'max_18_standardized_value':'PENDING'})
mx=np.max(np.stack(zs),axis=0);max18=float(np.mean(mx>=mx[ti]-1e-12))
for q in model_rows:q['max_18_inclusive_p']=max18
for q in assignment_rows:q['max_18_standardized_value']=float(mx[next(i for i,a in enumerate(orbit) if a['assignment_id']==q['assignment_id'])])
sm={(q['model'],q['metric']):q for q in model_rows}
gates={'host_char3_top1_at_least_3':scores[('HOST_CHAR3',ti)][2]>=3,'all_four_top1_at_least_3':scores[('ALL_FOUR',ti)][2]>=3,'host_char3_mrr_local_p_le_0_05':float(sm[('HOST_CHAR3','MEAN_RECIPROCAL_RANK')]['local_inclusive_p'])<=.05,'all_four_mrr_local_p_le_0_05':float(sm[('ALL_FOUR','MEAN_RECIPROCAL_RANK')]['local_inclusive_p'])<=.05,'max_18_inclusive_p_le_0_05':max18<=.05}
status='NESTED_RELATION_PAIR_STRUCTURE_TRANSFERS_WITHIN_EXPOSED_POOL' if all(gates.values()) else 'NESTED_RELATION_PAIR_STRUCTURE_NOT_SUPPORTED'
counter=[{'type':'EXPOSED_POSTHOC_PANEL','item':'GDT140_5X5','value':'NA','detail':'All pages and similarities were exposed before this nested model was designed.'},{'type':'CANDIDATE_POOL_CONDITIONAL','item':'FIVE_TARGET_PAGES','value':5,'detail':'Held targets are ranked only among the five frozen candidates, not all Herbal pages.'},{'type':'HOST_BOTH_INTERFERENCE','item':'HOST_BOTH','value':scores[('HOST_BOTH',ti)][0],'detail':'Combining exact-host and host-char3 scores reduces MRR and produces zero top-one folds.'},{'type':'RAW_CONTROL_FAILURE','item':'RAW_CHAR3','value':scores[('RAW_CHAR3',ti)][0],'detail':'Raw character similarity does not transfer the relation pairing.'},{'type':'COMPILER_CONTROL_FAILURE','item':'COMPILER','value':scores[('COMPILER',ti)][0],'detail':'Compiler similarity does not transfer the relation pairing.'}]
write(MODELS,clean(model_rows));write(FOLDS,clean(fold_rows));write(NULL,clean(assignment_rows));write(WEIGHTS,clean(weight_rows));write(COUNTER,clean(counter))
hf=scores[('HOST_CHAR3',ti)];af=scores[('ALL_FOUR',ti)]
REPORT.write_text(f"""# GDT143 — nested relation-pair prediction

## Outcome

**{status}**

With each relation held out in turn, the PAGE_HOST-character-trigram model ranks the true target at {', '.join(str(x['actual_rank_of_5']) for x in fold_rows if x['model']=='HOST_CHAR3')} of five: mean reciprocal rank {hf[0]:.3f}, {hf[2]}/5 top-one, local exact MRR p={float(sm[('HOST_CHAR3','MEAN_RECIPROCAL_RANK')]['local_inclusive_p']):.4f}. The all-four model yields ranks {', '.join(str(x['actual_rank_of_5']) for x in fold_rows if x['model']=='ALL_FOUR')}, MRR {af[0]:.3f}, and {af[2]}/5 top-one. Repeating the complete nested fit for every one of 120 mappings gives a shared maximum-over-18 p={max18:.4f}.

The controls are informative: raw-character and compiler models produce zero top-one folds; naively combining exact PAGE_HOST and PAGE_HOST trigrams also produces zero, while the all-four ridge learns to downweight the misleading channels in four-relation training. This is genuine label holdout within the panel, but it remains conditional on five already exposed targets and therefore is not a fresh corpus holdout or manuscript-wide retrieval test.

Only published f84-free GDT140 artifacts were used; no source or image was opened. No botanical truth, plant/component identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation follows.
""",encoding='utf8')
result={'schema':'GDT143_NESTED_RELATION_PAIR_PREDICTION_RESULT_V1','status':status,'relations':5,'candidate_targets':5,'assignment_worlds':120,'models':list(MODEL_COLS),'metrics':list(METRICS),'max_18_inclusive_p':max18,'true_model_scores':{m:{'mean_reciprocal_rank':scores[(m,ti)][0],'mean_log2_probability':scores[(m,ti)][1],'top1_count':scores[(m,ti)][2]} for m in MODEL_COLS},'gates':gates,'interpretation':'Nested leave-one-relation target ranking inside the exposed GDT140 candidate pool.','claim_ceiling':'Internal pair-structure transfer only; no corpus-wide retrieval, independent visual panel, botanical truth, identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84':{'all_inputs_are_f84_free_published_gdt140_artifacts':True,'source_or_image_opened':False,'new_f84r_access':False},'inputs':{p.name:sha(p) for p in (INV,PAIR,ORBIT,PARENT,ROBUST)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (MODELS,FOLDS,NULL,WEIGHTS,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':status,'max18_p':max18,'host_char3':hf,'all_four':af},sort_keys=True))
