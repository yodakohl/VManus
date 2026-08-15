#!/usr/bin/env python3
"""Post-hoc exact decomposition of the GDT140 PAGE_HOST lead."""
import csv,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SOURCE=R/'gdt062_right_family_inventory.tsv';INV=R/'gdt140_herbal_relation_inventory.tsv';ORBIT=R/'gdt140_assignment_orbit.tsv';METHOD=R/'GDT141_RELATION_SIGNAL_HOST_DECOMPOSITION_METHOD.md';REPORT=R/'GDT141_RELATION_SIGNAL_HOST_DECOMPOSITION_REPORT.md';VS=R/'gdt141_variant_scores.tsv';AS=R/'gdt141_assignment_scores.tsv';HS=R/'gdt141_host_contributions.tsv';COUNTER=R/'gdt141_counterexamples.tsv';RESULT=R/'gdt141_result.json'
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def clean(rows):return [{k:f'{v:.12g}' if isinstance(v,float) else v for k,v in x.items()} for x in rows]
def sim(a,b,keep):
 k={x for x in set(a)|set(b) if keep(x)};d=sum(max(a[x],b[x]) for x in k)
 return sum(min(a[x],b[x]) for x in k)/d if d else 0.
rels=read(INV);orbit=read(ORBIT);S=[x['source_page'] for x in rels];T=[x['target_page'] for x in rels];P=set(S+T);by=defaultdict(Counter);glob=Counter();host_pages=defaultdict(set)
with SOURCE.open(encoding='utf8',newline='') as h:
 for x in csv.DictReader(h,delimiter='\t'):
  if x['page'].startswith('f84'):continue
  glob[x['page_host']]+=1;host_pages[x['page_host']].add(x['page'])
  if x['page'] in P:by[x['page']][x['page_host']]+=1
assert set(by)==P
maps=[]
for x in orbit:d=dict(z.split('->') for z in x['mapping'].split('|'));maps.append([T.index(d[s]) for s in S])
ti=next(i for i,x in enumerate(orbit) if x['is_true']=='1');top5={x for x,_ in glob.most_common(5)};top10={x for x,_ in glob.most_common(10)};variants={'ALL':lambda x:True,'LEN_GE2':lambda x:len(x)>=2,'LEN_GE3':lambda x:len(x)>=3,'LEN_GE4':lambda x:len(x)>=4,'DROP_GLOBAL_TOP5':lambda x:x not in top5,'DROP_GLOBAL_TOP10':lambda x:x not in top10};vrows=[];arows=[];zall=[]
for name,keep in variants.items():
 m=np.array([[sim(by[a],by[b],keep) for b in T] for a in S]);vals=np.array([sum(m[i,j] for i,j in enumerate(q))/5 for q in maps]);z=(vals-vals.mean())/(vals.std() or 1);zall.append(z);ts=float(vals[ti]);vrows.append({'variant':name,'true_score':ts,'null_mean':float(vals.mean()),'null_sd':float(vals.std()),'true_z':float(z[ti]),'inclusive_rank_of_120':1+int(np.sum(vals>ts+1e-12)),'local_inclusive_p':float(np.mean(vals>=ts-1e-12)),'max_six_inclusive_p':'PENDING'})
 for i,x in enumerate(orbit):arows.append({'variant':name,'assignment_id':x['assignment_id'],'is_true':x['is_true'],'score':float(vals[i]),'standardized_score':float(z[i])})
mx=np.max(np.stack(zall),axis=0);max6=float(np.mean(mx>=mx[ti]-1e-12))
for x in vrows:x['max_six_inclusive_p']=max6
hosts=sorted(set().union(*(set(by[p]) for p in P)));hcalc=[];zhosts=[]
for host in hosts:
 vals=np.array([sum(min(by[S[i]][host],by[T[q[i]]][host]) for i in range(5)) for q in maps],float)
 if vals.std()==0:continue
 z=(vals-vals.mean())/vals.std();zhosts.append(z);hcalc.append((host,vals,z))
hmx=np.max(np.stack(zhosts),axis=0);hmaxp=float(np.mean(hmx>=hmx[ti]-1e-12));hrows=[]
for host,vals,z in hcalc:
 ts=float(vals[ti]);hrows.append({'page_host':host,'host_length':len(host),'global_occurrences':glob[host],'global_pages':len(host_pages[host]),'true_overlap_count':int(ts),'true_relation_support':sum(by[S[i]][host]>0 and by[T[i]][host]>0 for i in range(5)),'true_z':float(z[ti]),'inclusive_rank_of_120':1+int(np.sum(vals>ts+1e-12)),'local_inclusive_p':float(np.mean(vals>=ts-1e-12)),'max_host_inclusive_p':hmaxp})
hrows.sort(key=lambda x:(-float(x['true_z']),x['page_host']));best=max(vrows,key=lambda x:float(x['true_z']));status='RELATION_SIGNAL_DISTRIBUTED_SHORT_HOST_PROFILE' if next(x for x in vrows if x['variant']=='LEN_GE3')['inclusive_rank_of_120']<=6 and next(x for x in vrows if x['variant']=='LEN_GE4')['inclusive_rank_of_120']>6 and hmaxp>.05 else 'RELATION_SIGNAL_MECHANISM_UNRESOLVED';counter=[{'type':'LONG_HOST_COLLAPSE','item':'LEN_GE4','value':next(x for x in vrows if x['variant']=='LEN_GE4')['inclusive_rank_of_120'],'detail':'Length-four-plus hosts alone do not preserve the assignment.'},{'type':'NO_SINGLE_HOST_SURVIVOR','item':hrows[0]['page_host'],'value':hmaxp,'detail':'Best individual exact host fails max-host assignment correction.'},{'type':'POSTHOC_SCOPE','item':'GDT140_EXPOSED','value':'NA','detail':'All decompositions were chosen after GDT140 and cannot validate it.'},{'type':'ALTERNATE_READING_SCOPE','item':'GDT062','value':'NA','detail':'One derived source-display view; no alternate-reading replication.'}]
write(VS,clean(vrows));write(AS,clean(arows));write(HS,clean(hrows));write(COUNTER,counter)
REPORT.write_text(f"""# GDT141 — relation-signal host decomposition\n\n## Outcome\n\n**{status}**\n\nThe GDT140 relation assignment survives removal of the ten globally most frequent hosts: rank {next(x for x in vrows if x['variant']=='DROP_GLOBAL_TOP10')['inclusive_rank_of_120']}/120, and survives length >=3 at rank {next(x for x in vrows if x['variant']=='LEN_GE3')['inclusive_rank_of_120']}/120. The six-variant maximum p is {max6:.4f}. It collapses for length >=4 to rank {next(x for x in vrows if x['variant']=='LEN_GE4')['inclusive_rank_of_120']}/120.\n\nNo exact host explains the result alone. The top individual-host local statistic is `{hrows[0]['page_host']}`, but each best singleton has local assignment p at least {min(float(x['local_inclusive_p']) for x in hrows):.3f}, and the exact max-host p is {hmaxp:.4f}. The signal therefore resides in a distributed profile dominated by two- and three-character PAGE_HOSTs, not a repeated long form or a candidate plant name.\n\nThis is an exposed post-hoc mechanism audit, not validation. All variants and all variable individual hosts are published. All f84 rows were rejected before retention and no new f84r access occurred. No botanical truth, plant/component identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation is assigned.\n""",encoding='utf8')
result={'schema':'GDT141_RELATION_SIGNAL_HOST_DECOMPOSITION_RESULT_V1','status':status,'variants':vrows,'global_top10_hosts':[x for x,_ in glob.most_common(10)],'best_variant':best,'best_individual_hosts':hrows[:12],'max_six_inclusive_p':max6,'max_host_inclusive_p':hmaxp,'interpretation':'Post-hoc localization of GDT140 relation similarity to a distributed short PAGE_HOST profile.','claim_ceiling':'Mechanism localization only; no botanical truth, plant/component identity, semantic role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.','f84':{'all_rows_rejected_before_retention':True,'new_f84r_access':False},'inputs':{p.name:sha(p) for p in (SOURCE,INV,ORBIT,R/'gdt140_result.json')},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (VS,AS,HS,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps({'status':status,'best':best['variant'],'max6_p':max6,'max_host_p':hmaxp},sort_keys=True))
