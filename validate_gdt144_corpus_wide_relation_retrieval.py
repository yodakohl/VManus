#!/usr/bin/env python3
"""Independent reconstruction of the GDT144 corpus-wide retrieval sensitivity."""
import csv,hashlib,json,random
from collections import defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;UNITS=R/'gdt112_o_ot_units.tsv';META=R/'gdt137_herbal_visual_feature_inventory.tsv';INV=R/'gdt140_herbal_relation_inventory.tsv';PAIR=R/'gdt144_pair_ranks.tsv';NULL=R/'gdt144_null_results.tsv';CAP=R/'gdt144_capacity.tsv';COUNTER=R/'gdt144_counterexamples.tsv';RESULT=R/'gdt144_result.json';OUT=R/'gdt144_validation.json';REPS=('HOST_SET','HOST_CHAR3_SET','FRAME_HOST_SET','FRAME_HOST_CHAR3_SET');WORLDS=100000;SEED=144140
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def tri(s):
 s='^'+s+'$';return {s[i:i+3] for i in range(max(1,len(s)-2))}
def jac(a,b):return len(a&b)/len(a|b) if a|b else 0.
checks=[]
def ck(n,v,d=''):checks.append({'check':n,'pass':bool(v),'detail':d})
meta={x['page']:x for x in read(META)};units=read(UNITS);rels=read(INV);res=json.loads(RESULT.read_text());ck('f84r_absent',not any(x['page'].startswith('f84r') for x in units) and not any(x['page'].startswith('f84r') for x in meta.values()))
eligible0=sorted(p for p,x in meta.items() if x['currier']=='A' and x['hand']=='1');by=defaultdict(list)
for x in units:
 if x['page'] in eligible0:by[x['page']].append(x)
eligible=sorted(p for p in eligible0 if p in by);covered=[x for x in rels if x['source_page'] in by and x['target_page'] in by];excluded=[x for x in rels if x not in covered];ck('capacity_exact',len(eligible)==93 and [x['relation_id'] for x in covered]==['MHI003','MHI004','MHI006','MHI007'] and [x['relation_id'] for x in excluded]==['MHI002'])
feat={}
for p in eligible:
 h={x['page_host'] for x in by[p]};feat[p]={'HOST_SET':h,'HOST_CHAR3_SET':set().union(*(tri(x) for x in h)),'FRAME_HOST_SET':{x['frame']+'='+x['page_host'] for x in by[p]},'FRAME_HOST_CHAR3_SET':set().union(*({x['frame']+'='+z for z in tri(x['page_host'])} for x in by[p]))}
cands=[];zmat=[];computed={}
for i,x in enumerate(covered):
 s=x['source_page'];t=x['target_page'];c=[p for p in eligible if p!=s and meta[p]['physical_folio']!=meta[s]['physical_folio']];cands.append(c);zr=[]
 for rep in REPS:
  v=np.array([jac(feat[s][rep],feat[p][rep]) for p in c]);mu=v.mean();sd=v.std() or 1;score=jac(feat[s][rep],feat[t][rep]);z=(v-mu)/sd;zr.append(dict(zip(c,z)));computed[(x['relation_id'],rep)]=(score,len(c),1+int(np.sum(v>score+1e-12)),float(np.mean(v>=score-1e-12)),float((score-mu)/sd))
 zmat.append(zr)
published={(x['relation_id'],x['representation']):x for x in read(PAIR)}
for key,v in computed.items():
 q=published[key];got=(float(q['similarity']),int(q['candidate_pages']),int(q['true_target_rank']),float(q['inclusive_candidate_tail']),float(q['source_standardized_similarity']));ck('pair_'+key[0]+'_'+key[1],all(abs(got[k]-v[k])<1e-9 for k in (0,3,4)) and got[1:3]==v[1:3])
obs=np.array([np.mean([zmat[i][k][covered[i]['target_page']] for i in range(4)]) for k in range(4)]);rng=random.Random(SEED);world=np.zeros((WORLDS,4))
for w in range(WORLDS):
 while True:
  draw=[rng.choice(cands[i]) for i in range(4)]
  if len(set(draw))==4:break
 for k in range(4):world[w,k]=np.mean([zmat[i][k][draw[i]] for i in range(4)])
mu=world.mean(0);sd=world.std(0);zo=(obs-mu)/sd;zn=(world-mu)/sd;max4=float(np.mean(zn.max(1)>=zo.max()-1e-12));pn={x['representation']:x for x in read(NULL)}
for k,rep in enumerate(REPS):
 q=pn[rep];exp=(obs[k],mu[k],sd[k],zo[k],float(np.mean(world[:,k]>=obs[k]-1e-12)),max4);got=tuple(float(q[x]) for x in ('true_mean_source_z','null_mean','null_sd','true_null_standardized_z','local_monte_carlo_p','max_four_monte_carlo_p'));ck('null_'+rep,all(abs(a-b)<1e-9 for a,b in zip(got,exp)) and int(q['worlds'])==WORLDS and int(q['seed'])==SEED)
top=max(sum(int(published[(x['relation_id'],rep)]['top_decile']) for x in covered) for rep in REPS);g={'at_least_three_of_four_top_decile_in_one_fixed_representation':top>=3,'max_four_p_le_0_05':max4<=.05};status='O_OT_PAGE_HOST_CORPUS_WIDE_RELATION_RETRIEVAL_SUPPORTED' if all(g.values()) else 'O_OT_PAGE_HOST_CORPUS_WIDE_RELATION_RETRIEVAL_NOT_SUPPORTED';ck('decision',res['status']==status and res['gates']==g and abs(res['null_results'][0]['max_four_monte_carlo_p']-max4)<1e-12);ck('capacity_rows',len(read(CAP))==3);ck('counterexamples',len(read(COUNTER))>=5)
for group in ('inputs','outputs','documents','implementation'):
 for name,h in res[group].items():ck(group+'_'+name,sha(R/name)==h)
tmp=dict(res);got=tmp.pop('result_content_sha256');ck('content_hash',csha(tmp)==got)
ok=all(x['pass'] for x in checks);out={'schema':'GDT144_CORPUS_WIDE_RELATION_RETRIEVAL_VALIDATION_V1','status':'PASS_INDEPENDENT_100000_WORLD_RECONSTRUCTION' if ok else 'FAIL','checks_passed':sum(x['pass'] for x in checks),'checks_total':len(checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'checks':checks};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'checks':f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));raise SystemExit(0 if ok else 1)
