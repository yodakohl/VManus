#!/usr/bin/env python3
"""Independent reconstruction of GDT145."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;UNITS=R/'gdt112_o_ot_units.tsv';META=R/'gdt137_herbal_visual_feature_inventory.tsv';INV=R/'gdt140_herbal_relation_inventory.tsv';SENS=R/'gdt145_sensitivities.tsv';COUNTER=R/'gdt145_counterexamples.tsv';RESULT=R/'gdt145_result.json';OUT=R/'gdt145_validation.json'
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v),'detail':''})
meta={x['page']:x for x in read(META)};e0={p for p,x in meta.items() if x['currier']=='A' and x['hand']=='1'};by=defaultdict(set);units=read(UNITS)
for x in units:
 if x['page'] in e0:by[x['page']].add(x['page_host'])
e=sorted(p for p in e0 if p in by);df=Counter(h for p in e for h in by[p]);s='f6r';t='f51r';c=[p for p in e if p!=s and meta[p]['physical_folio']!=meta[s]['physical_folio']]
def idf(h):return math.log((len(e)+.5)/(df[h]+.5))
def wj(a,b):
 u=a|b;return sum(idf(h) for h in a&b)/sum(idf(h) for h in u) if u else 0
sc=wj(by[s],by[t]);v=[wj(by[s],by[p]) for p in c];rank=1+sum(x>sc+1e-12 for x in v);tail=sum(x>=sc-1e-12 for x in v)/len(v);matched=[p for p in c if len(by[p])==len(by[t])];vm=[wj(by[s],by[p]) for p in matched];mt=sum(x>=sc-1e-12 for x in vm)/len(vm)
ck('eligible_93',len(e)==93);ck('host_sets',by[s]=={'d','l'} and by[t]=={'l'});ck('document_frequency',df['l']==84 and df['d']==48);ck('idf_rank',rank==29 and abs(tail-.32967032967032966)<1e-12);ck('size_match',len(matched)==5 and abs(mt-.4)<1e-12);ck('long_capacity_absent',not {h for h in by[s] if len(h)>=2} and not {h for h in by[t] if len(h)>=2})
res=json.loads(RESULT.read_text());g={'shared_host_page_prevalence_gt_0_8':df['l']/len(e)>.8,'idf_rank_outside_top_decile':rank>math.ceil(.1*len(c)),'length_two_pair_capacity_absent':True};ck('decision',res['status']=='MHI004_O_OT_LEAD_EXPLAINED_BY_UBIQUITOUS_SINGLETON_HOST' and res['gates']==g);ck('sensitivity_rows',len(read(SENS))==4);ck('counterexamples',len(read(COUNTER))==4)
for group in ('inputs','outputs','documents','implementation'):
 for name,h in res[group].items():ck(group+'_'+name,sha(R/name)==h)
tmp=dict(res);got=tmp.pop('result_content_sha256');ck('content_hash',csha(tmp)==got)
ok=all(x['pass'] for x in checks);out={'schema':'GDT145_MHI004_RETRIEVAL_MECHANISM_VALIDATION_V1','status':'PASS_INDEPENDENT_RECONSTRUCTION' if ok else 'FAIL','checks_passed':sum(x['pass'] for x in checks),'checks_total':len(checks),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'checks':checks};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'checks':f"{out['checks_passed']}/{out['checks_total']}"},sort_keys=True));raise SystemExit(0 if ok else 1)
