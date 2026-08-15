#!/usr/bin/env python3
"""Independent exact reconstruction of GDT141 variants and host scan."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt062_right_family_inventory.tsv';INV=R/'gdt140_herbal_relation_inventory.tsv';ORBIT=R/'gdt140_assignment_orbit.tsv';VS=R/'gdt141_variant_scores.tsv';AS=R/'gdt141_assignment_scores.tsv';HS=R/'gdt141_host_contributions.tsv';RESULT=R/'gdt141_result.json';OUT=R/'gdt141_validation.json'
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def sim(a,b,keep):
 k={x for x in set(a)|set(b) if keep(x)};d=sum(max(a[x],b[x]) for x in k)
 return sum(min(a[x],b[x]) for x in k)/d if d else 0.
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
rels=read(INV);orbit=read(ORBIT);result=json.loads(RESULT.read_text());ck('status',result['status']=='RELATION_SIGNAL_DISTRIBUTED_SHORT_HOST_PROFILE');S=[x['source_page'] for x in rels];T=[x['target_page'] for x in rels];P=set(S+T);by=defaultdict(Counter);glob=Counter();hp=defaultdict(set)
with SOURCE.open(encoding='utf8',newline='') as h:
 for x in csv.DictReader(h,delimiter='\t'):
  if x['page'].startswith('f84'):continue
  glob[x['page_host']]+=1;hp[x['page_host']].add(x['page'])
  if x['page'] in P:by[x['page']][x['page_host']]+=1
ck('panel',set(by)==P and len(orbit)==120);maps=[]
for x in orbit:d=dict(z.split('->') for z in x['mapping'].split('|'));maps.append([T.index(d[s]) for s in S])
ti=next(i for i,x in enumerate(orbit) if x['is_true']=='1');top5={x for x,_ in glob.most_common(5)};top10={x for x,_ in glob.most_common(10)};variants={'ALL':lambda x:True,'LEN_GE2':lambda x:len(x)>=2,'LEN_GE3':lambda x:len(x)>=3,'LEN_GE4':lambda x:len(x)>=4,'DROP_GLOBAL_TOP5':lambda x:x not in top5,'DROP_GLOBAL_TOP10':lambda x:x not in top10};sv={x['variant']:x for x in read(VS)};sa={(x['variant'],x['assignment_id']):x for x in read(AS)};zs=[];vbuild=[]
for name,keep in variants.items():
 m=np.array([[sim(by[a],by[b],keep) for b in T] for a in S]);vals=np.array([sum(m[i,j] for i,j in enumerate(q))/5 for q in maps]);z=(vals-vals.mean())/(vals.std() or 1);zs.append(z);ts=float(vals[ti]);row={'variant':name,'true_score':ts,'null_mean':float(vals.mean()),'null_sd':float(vals.std()),'true_z':float(z[ti]),'inclusive_rank_of_120':1+int(np.sum(vals>ts+1e-12)),'local_inclusive_p':float(np.mean(vals>=ts-1e-12))};vbuild.append(row);s=sv[name];ck('variant_'+name,abs(ts-float(s['true_score']))<2e-9 and row['inclusive_rank_of_120']==int(s['inclusive_rank_of_120']))
 for i,x in enumerate(orbit):q=sa[name,x['assignment_id']];ck('world_'+name+x['assignment_id'],abs(float(vals[i])-float(q['score']))<2e-9 and abs(float(z[i])-float(q['standardized_score']))<2e-9)
mx=np.max(np.stack(zs),axis=0);max6=float(np.mean(mx>=mx[ti]-1e-12));ck('max6',all(abs(float(x['max_six_inclusive_p'])-max6)<2e-9 for x in sv.values()));hosts=sorted(set().union(*(set(by[p]) for p in P)));calc=[];zh=[]
for host in hosts:
 vals=np.array([sum(min(by[S[i]][host],by[T[q[i]]][host]) for i in range(5)) for q in maps],float)
 if vals.std()==0:continue
 z=(vals-vals.mean())/vals.std();zh.append(z);calc.append((host,vals,z))
hmx=np.max(np.stack(zh),axis=0);hmax=float(np.mean(hmx>=hmx[ti]-1e-12));sh={x['page_host']:x for x in read(HS)}
for host,vals,z in calc:
 ts=float(vals[ti]);x=sh[host];ck('host_'+host,int(ts)==int(x['true_overlap_count']) and abs(float(z[ti])-float(x['true_z']))<2e-9 and 1+int(np.sum(vals>ts+1e-12))==int(x['inclusive_rank_of_120']) and abs(float(np.mean(vals>=ts-1e-12))-float(x['local_inclusive_p']))<2e-9 and abs(hmax-float(x['max_host_inclusive_p']))<2e-9)
ck('row_counts',len(sv)==6 and len(sa)==720 and len(sh)==len(calc));ck('result_numbers',abs(max6-float(result['max_six_inclusive_p']))<2e-12 and abs(hmax-float(result['max_host_inclusive_p']))<2e-12 and result['global_top10_hosts']==[x for x,_ in glob.most_common(10)]);ck('hashes',all(sha(R/n)==d for n,d in {**result['inputs'],**result['implementation'],**result['outputs'],**result['documents']}.items()));q=dict(result);d=q.pop('result_content_sha256');ck('content',csha(q)==d);ck('f84',result['f84']['all_rows_rejected_before_retention'] and not result['f84']['new_f84r_access']);v={'schema':'GDT141_VALIDATION_V1','status':'PASS_INDEPENDENT_SIX_VARIANT_AND_ALL_HOST_RECONSTRUCTION','checks':len(checks),'passed':sum(x['pass'] for x in checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'check_rows':checks};OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':v['status'],'checks':v['checks']},sort_keys=True))
