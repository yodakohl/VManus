#!/usr/bin/env python3
"""Independent exact reconstruction of GDT140."""
import csv,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt062_right_family_inventory.tsv';INV=R/'gdt140_herbal_relation_inventory.tsv';ORBIT=R/'gdt140_assignment_orbit.tsv';SCORE=R/'gdt140_representation_scores.tsv';PAIR=R/'gdt140_pair_similarities.tsv';DIAG=R/'gdt140_true_pair_diagnostics.tsv';NULL=R/'gdt140_assignment_scores.tsv';WIT=R/'gdt140_exact_host_witnesses.tsv';LAY=R/'gdt140_layout_assignment_controls.tsv';LEAVE=R/'gdt140_leave_one_relation.tsv';RESULT=R/'gdt140_result.json';OUT=R/'gdt140_validation.json';REPS=('PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3','RAW_CHAR3','COMPILER_SIGNATURE')
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def add3(c,s):
 s='^'+s+'$'
 for i in range(max(1,len(s)-2)):c[s[i:i+3]]+=1
def sim(a,b):
 k=set(a)|set(b);d=sum(max(a[x],b[x]) for x in k)
 return sum(min(a[x],b[x]) for x in k)/d if d else 0
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
rels=read(INV);orbit=read(ORBIT);result=json.loads(RESULT.read_text());ck('status',result['status']=='HERBAL_RELATION_PAGE_HOST_TRANSFER_SUPPORTED');ck('panel',[x['relation_id'] for x in rels]==['MHI002','MHI003','MHI004','MHI006','MHI007'] and len(orbit)==120)
sources=[x['source_page'] for x in rels];targets=[x['target_page'] for x in rels];pages=set(sources+targets);data=[]
with SOURCE.open(encoding='utf8',newline='') as h:
 for x in csv.DictReader(h,delimiter='\t'):
  if x['page'].startswith('f84'):continue
  if x['page'] in pages:data.append(x)
ck('source',set(x['page'] for x in data)==pages and not any(x['page'].startswith('f84') for x in data));by=defaultdict(list)
for x in data:by[x['page']].append(x)
feat={p:{r:Counter() for r in REPS} for p in pages}
for p in pages:
 for x in sorted(by[p],key=lambda x:(x['locus'],int(x['group_index']))):feat[p]['PAGE_HOST_IDENTITY']['H='+x['page_host']]+=1;add3(feat[p]['PAGE_HOST_CHAR3'],x['page_host']);add3(feat[p]['RAW_CHAR3'],x['token']);feat[p]['COMPILER_SIGNATURE']['|'.join((x['wrapper'],x['inner_d'],x['local_frame'],x['right_family'],x['dy_closure'],x['b3']))]+=1
mat={r:np.array([[sim(feat[a][r],feat[b][r]) for b in targets] for a in sources]) for r in REPS};mapping=[]
for x in orbit:
 d=dict(y.split('->') for y in x['mapping'].split('|'));mapping.append([targets.index(d[s]) for s in sources])
ti=next(i for i,x in enumerate(orbit) if x['is_true']=='1');scores={r:np.array([sum(mat[r][i,j] for i,j in enumerate(m))/5 for m in mapping]) for r in REPS};zs={r:(scores[r]-scores[r].mean())/(scores[r].std() or 1) for r in REPS};maxz=np.max(np.stack([zs[r] for r in REPS]),axis=0);sm={x['representation']:x for x in read(SCORE)};pair={(x['representation'],x['source_page'],x['candidate_target_page']):x for x in read(PAIR)};diag={(x['relation_id'],x['representation']):x for x in read(DIAG)};an={(x['assignment_id'],x['representation']):x for x in read(NULL)}
for rep in REPS:
 s=scores[rep];ts=float(s[ti]);rank=1+int(np.sum(s>ts+1e-12));p=float(np.mean(s>=ts-1e-12));x=sm[rep];ck('score_'+rep,abs(ts-float(x['true_assignment_score']))<2e-9 and rank==int(x['inclusive_rank_of_120']) and abs(p-float(x['local_inclusive_p']))<2e-9 and abs(float(np.mean(maxz>=maxz[ti]-1e-12))-float(x['max_four_z_inclusive_p']))<2e-9)
 for i,a in enumerate(sources):
  for j,b in enumerate(targets):ck('pair_'+rep+a+b,abs(float(mat[rep][i,j])-float(pair[rep,a,b]['similarity']))<2e-9)
  rr=mat[rep][i];tv=float(rr[targets.index(rels[i]['target_page'])]);d=diag[rels[i]['relation_id'],rep];ck('diag_'+rep+rels[i]['relation_id'],1+int(np.sum(rr>tv+1e-12))==int(d['true_partner_rank_of_5']) and abs(tv-float(d['true_similarity']))<2e-9 and abs(tv-float(rr.mean())-float(d['centered_leave_pair_effect']))<2e-9)
 for i,a in enumerate(orbit):q=an[a['assignment_id'],rep];ck('world_'+rep+a['assignment_id'],abs(float(s[i])-float(q['mean_pair_similarity']))<2e-9 and abs(float(zs[rep][i])-float(q['standardized_score']))<2e-9 and abs(float(maxz[i])-float(q['max_four_standardized_score']))<2e-9)
w={x['relation_id']:x for x in read(WIT)}
for x in rels:common=sorted(set(feat[x['source_page']]['PAGE_HOST_IDENTITY'])&set(feat[x['target_page']]['PAGE_HOST_IDENTITY']));ck('witness_'+x['relation_id'],'|'.join(h[2:] for h in common)==w[x['relation_id']]['shared_exact_page_hosts'])
layout={(x['metric'],x['assignment_id']):x for x in read(LAY)};ls={}
counts={p:{'FORMAL_LINES':len({x['locus'] for x in by[p]}),'SOURCE_GROUPS':len(by[p])} for p in pages}
for metric in ('FORMAL_LINES','SOURCE_GROUPS'):
 vals=[sum(1-abs(counts[sources[i]][metric]-counts[targets[j]][metric])/max(counts[sources[i]][metric],counts[targets[j]][metric],1) for i,j in enumerate(m))/5 for m in mapping];ts=vals[ti];ls[metric]={'true_similarity':ts,'inclusive_rank_of_120':1+sum(x>ts+1e-12 for x in vals),'inclusive_better_p':sum(x>=ts-1e-12 for x in vals)/120}
 for i,a in enumerate(orbit):ck('layout_'+metric+a['assignment_id'],abs(vals[i]-float(layout[metric,a['assignment_id']]['mean_count_similarity']))<2e-9)
ck('layout_summary',ls==result['layout_opportunity_audit']);sl={(x['representation'],x['dropped_relation_id']):x for x in read(LEAVE)};leave_summary={r:[] for r in REPS}
for rep in REPS:
 for drop,x in enumerate(rels):
  ii=[i for i in range(5) if i!=drop];ss=[sources[i] for i in ii];tt=[targets[i] for i in ii];vals=[sum(mat[rep][sources.index(s),targets.index(p[i])] for i,s in enumerate(ss))/4 for p in itertools.permutations(tt)];ts=float(vals[0]);row={'representation':rep,'dropped_relation_id':x['relation_id'],'remaining_relations':4,'assignment_worlds':24,'true_score':ts,'inclusive_rank_of_24':int(1+sum(v>ts+1e-12 for v in vals)),'inclusive_p':float(sum(v>=ts-1e-12 for v in vals)/24)};leave_summary[rep].append(row);q=sl[rep,x['relation_id']];ck('leave_'+rep+x['relation_id'],abs(ts-float(q['true_score']))<2e-9 and row['inclusive_rank_of_24']==int(q['inclusive_rank_of_24']) and abs(row['inclusive_p']-float(q['inclusive_p']))<2e-9)
ck('leave_summary',leave_summary==result['leave_one_relation']);best=max(('PAGE_HOST_IDENTITY','PAGE_HOST_CHAR3'),key=lambda r:(float(sm[r]['true_z']),r));b=sm[best];g={'page_host_inclusive_rank_le_6_of_120':int(b['inclusive_rank_of_120'])<=6,'page_host_beats_raw_and_compiler':float(b['true_z'])>max(float(sm['RAW_CHAR3']['true_z']),float(sm['COMPILER_SIGNATURE']['true_z'])),'at_least_4_of_5_true_partner_ranks_le_2':int(b['true_partner_rank_le_2_count'])>=4,'leave_one_pair_score_positive_at_least_4_of_5':int(b['positive_centered_pair_effects'])>=4};ck('gates',best==result['best_page_host_representation'] and g==result['gates']);ck('hashes',all(sha(R/n)==d for n,d in {**result['inputs'],**result['implementation'],**result['outputs'],**result['documents']}.items()));q=dict(result);d=q.pop('result_content_sha256');ck('content',csha(q)==d);ck('f84',result['f84']['all_rows_rejected_before_retention'] and not result['f84']['new_f84r_access']);v={'schema':'GDT140_VALIDATION_V1','status':'PASS_INDEPENDENT_EXACT_120_ASSIGNMENT_RECONSTRUCTION','checks':len(checks),'passed':sum(x['pass'] for x in checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'check_rows':checks};OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':v['status'],'checks':v['checks']},sort_keys=True))
