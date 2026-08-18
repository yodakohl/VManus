#!/usr/bin/env python3
"""Build frozen GDT296 opaque-host renderer atlas."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'gdt296_design.json';METHOD=R/'GDT296_OPAQUE_HOST_RENDERER_ATLAS_METHOD.md';REPORT=R/'GDT296_OPAQUE_HOST_RENDERER_ATLAS_REPORT.md';RESULT=R/'gdt296_result.json';ATLAS=R/'gdt296_host_renderer_atlas.tsv';FOLDS=R/'gdt296_host_renderer_folds.tsv';COUNTER=R/'gdt296_counterexamples.tsv';C=('wrapper','local_frame','inner_d','right_family','dy_closure','b3');ALPHA=.5;PRIOR=11.
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rcsha(v):q=dict(v);q.pop('content_sha256',None);return csha(q)
def rows(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rr):
 ff=[]
 for r in rr:
  for k in r:
   if k not in ff:ff.append(k)
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,ff,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows([{k:r.get(k,'NA') for k in ff} for r in rr])
def target(r):return '|'.join(r[x] for x in C)
def entropy(c):
 n=sum(c.values());return -sum((v/n)*math.log2(v/n) for v in c.values() if v)
def main():
 d=json.loads(D.read_text());assert d['status']=='FROZEN_BEFORE_GDT296_ATLAS_SCORING' and d['content_sha256']==rcsha(d)
 for x in rows(R/'gdt296_freeze_manifest.tsv'):assert sha(R/x['artifact'])==x['frozen_sha256']
 native=rows(R/'gdt278_native_event_inventory.tsv');assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in native);ev=[x for x in native if x['control_id']=='VOYNICH_REFERENCE'];pop=rows(R/'gdt296_population.tsv');hosts={x['page_host'] for x in pop};alphabet=sorted({target(x) for x in ev});rank={x:i for i,x in enumerate(alphabet)};atlas=[];foldrows=[]
 for host in sorted(hosts):
  he=[x for x in ev if x['page_host']==host];folios=sorted({x['physical_folio'] for x in he});allc=Counter(target(x) for x in he);dom=max(alphabet,key=lambda y:(allc[y],-rank[y]));bits=Counter();tops=Counter();fg=defaultdict(float)
  for held in folios:
   train=[x for x in he if x['physical_folio']!=held];test=[x for x in he if x['physical_folio']==held];hc=Counter(target(x) for x in train);pc=defaultdict(Counter)
   for x in train:pc[x['within_field_position']][target(x)]+=1
   fb=Counter();ft=Counter()
   for x in test:
    actual=target(x);ph={y:(hc[y]+ALPHA)/(len(train)+ALPHA*len(alphabet)) for y in alphabet};a=pc[x['within_field_position']];pp={y:(a[y]+PRIOR*ph[y])/(sum(a.values())+PRIOR) for y in alphabet};ordered_h=sorted(alphabet,key=lambda y:(-ph[y],rank[y]));ordered_p=sorted(alphabet,key=lambda y:(-pp[y],rank[y]))
    for m,prob,ordered in (('HOST_CANONICAL',ph,ordered_h),('HOST_X_POSITION',pp,ordered_p)):
     z=-math.log2(prob[actual]);bits[m]+=z;fb[m]+=z;tops[m+'_TOP1']+=int(actual==ordered[0]);tops[m+'_TOP3']+=int(actual in ordered[:3]);ft[m+'_TOP1']+=int(actual==ordered[0]);ft[m+'_TOP3']+=int(actual in ordered[:3])
   fg[held]=fb['HOST_CANONICAL']-fb['HOST_X_POSITION'];foldrows.append({'page_host':host,'held_folio':held,'events':len(test),'host_bits':f"{fb['HOST_CANONICAL']:.12f}",'position_bits':f"{fb['HOST_X_POSITION']:.12f}",'position_gain_bits':f"{fg[held]:.12f}",'host_top1':ft['HOST_CANONICAL_TOP1'],'host_top3':ft['HOST_CANONICAL_TOP3'],'position_top1':ft['HOST_X_POSITION_TOP1'],'position_top3':ft['HOST_X_POSITION_TOP3']})
  n=len(he);ht1=tops['HOST_CANONICAL_TOP1']/n;pt1=tops['HOST_X_POSITION_TOP1']/n;ent=entropy(allc)
  if ht1>=d['labels']['canonical']['top1_min'] and ent<=d['labels']['canonical']['entropy_max_bits']:label='CANONICAL_RENDERER_CANDIDATE'
  elif pt1>=d['labels']['position_conditioned']['top1_min'] and pt1-ht1>=d['labels']['position_conditioned']['top1_improvement_min']:label='POSITION_CONDITIONED_CANDIDATE'
  else:label='VARIABLE_RENDERER'
  posdom={}
  for pos in sorted({x['within_field_position'] for x in he}):
   c=Counter(target(x) for x in he if x['within_field_position']==pos);z=max(alphabet,key=lambda y:(c[y],-rank[y]));posdom[pos]={'tuple':z,'events':sum(c.values()),'share':c[z]/sum(c.values())}
  atlas.append({'page_host':host,'classification':label,'events':n,'folios':len(folios),'sections':len({x['section'] for x in he}),'hands':len({x['hand'] for x in he}),'positions':len(posdom),'renderer_tuple_types':len(allc),'empirical_entropy_bits':f'{ent:.12f}','dominant_renderer_tuple':dom,'dominant_share':f'{allc[dom]/n:.12f}','lofo_host_bits_per_event':f"{bits['HOST_CANONICAL']/n:.12f}",'lofo_host_top1':f'{ht1:.12f}','lofo_host_top3':f"{tops['HOST_CANONICAL_TOP3']/n:.12f}",'lofo_position_bits_per_event':f"{bits['HOST_X_POSITION']/n:.12f}",'lofo_position_top1':f'{pt1:.12f}','lofo_position_top3':f"{tops['HOST_X_POSITION_TOP3']/n:.12f}",'position_gain_bits_per_event':f"{(bits['HOST_CANONICAL']-bits['HOST_X_POSITION'])/n:.12f}",'positive_position_folds':sum(v>0 for v in fg.values()),'position_dominants_json':json.dumps(posdom,sort_keys=True,separators=(',',':'))})
 order={'CANONICAL_RENDERER_CANDIDATE':0,'POSITION_CONDITIONED_CANDIDATE':1,'VARIABLE_RENDERER':2};atlas.sort(key=lambda x:(order[x['classification']],-float(x['lofo_host_top1']) if x['classification']=='CANONICAL_RENDERER_CANDIDATE' else -float(x['lofo_position_top1']),float(x['empirical_entropy_bits']),-int(x['events']),x['page_host']));write(ATLAS,atlas);write(FOLDS,foldrows)
 counters=sorted(atlas,key=lambda x:(float(x['lofo_position_top1']),-float(x['empirical_entropy_bits']),x['page_host']))[:15];write(COUNTER,[{'page_host':x['page_host'],'events':x['events'],'folios':x['folios'],'classification':x['classification'],'host_top1':x['lofo_host_top1'],'position_top1':x['lofo_position_top1'],'entropy_bits':x['empirical_entropy_bits'],'counterexample':'LOW_HELD_RENDERER_STABILITY'} for x in counters])
 counts=Counter(x['classification'] for x in atlas);top=atlas[:20];report=['# GDT296 — opaque host renderer atlas','', 'Status: **OPAQUE_HOST_RENDERER_ATLAS_BUILT**.','','## Classification census','',f"- `CANONICAL_RENDERER_CANDIDATE`: {counts['CANONICAL_RENDERER_CANDIDATE']}/59.",f"- `POSITION_CONDITIONED_CANDIDATE`: {counts['POSITION_CONDITIONED_CANDIDATE']}/59.",f"- `VARIABLE_RENDERER`: {counts['VARIABLE_RENDERER']}/59.",'','## Highest-ranked normalization candidates','', '| host | class | events | folios | entropy | host top-1 | position top-1 | position gain | dominant renderer |','|---|---|---:|---:|---:|---:|---:|---:|---|']
 for x in top:report.append(f"| `{x['page_host']}` | {x['classification']} | {x['events']} | {x['folios']} | {float(x['empirical_entropy_bits']):.3f} | {float(x['lofo_host_top1']):.3f} | {float(x['lofo_position_top1']):.3f} | {float(x['position_gain_bits_per_event']):+.3f} | `{x['dominant_renderer_tuple']}` |")
 report+=['','The atlas is a held-folio normalization instrument. Exact host IDs are printed because identity—not substring content—is the frozen unit. The labels are descriptive threshold classes, not semantic categories or p-valued discoveries.','','## Claim ceiling','','A row identifies only predictability of the parser-defined renderer tuple for an opaque host. It cannot establish lexicality, a word, meaning, code value, sound, language, plaintext, or translation. No host substring was mined and no f84 row was opened, parsed, retained, joined, or scored.'];REPORT.write_text('\n'.join(report)+'\n')
 outputs=[ATLAS,FOLDS,COUNTER,REPORT];inputs=['gdt296_design.json','gdt296_design_validation.json','gdt296_population.tsv','gdt296_freeze_manifest.tsv','gdt278_native_event_inventory.tsv','gdt295_result.json','gdt294_result.json','gdt293_result.json'];res={'schema':'GDT296_OPAQUE_HOST_RENDERER_ATLAS_RESULT_V1','status':'OPAQUE_HOST_RENDERER_ATLAS_BUILT','hosts':len(atlas),'events':sum(int(x['events']) for x in atlas),'classification_counts':dict(counts),'top_candidates':[{'page_host':x['page_host'],'classification':x['classification'],'events':int(x['events']),'folios':int(x['folios']),'host_top1':float(x['lofo_host_top1']),'position_top1':float(x['lofo_position_top1']),'entropy_bits':float(x['empirical_entropy_bits']),'dominant_renderer_tuple':x['dominant_renderer_tuple']} for x in top],'p_values':0,'host_substrings_mined':0,'semantic_assignments':0,'claim_ceiling':d['claim_ceiling'],'f84':d['f84'],'inputs':{x:sha(R/x) for x in inputs},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};res['content_sha256']=rcsha(res);RESULT.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':res['status'],'counts':dict(counts)},sort_keys=True))
if __name__=='__main__':main()
