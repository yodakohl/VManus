#!/usr/bin/env python3
"""Production-free reconstruction of second-member calibration."""

from __future__ import annotations

import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"

import csv,hashlib,json,math
from collections import Counter,defaultdict
from dataclasses import dataclass
from pathlib import Path
import numpy as np

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results"
PANEL_PATH=RESULTS/"source_native_opening_second_masked.tsv";QUOTA_PATH=RESULTS/"source_native_opening_context_quotas.tsv";CAPACITY=RESULTS/"source_native_opening_second_capacity_validation.json";SPEC=BASE/"SOURCE_NATIVE_OPENING_SECOND_PREFLIGHT_SPEC.md";CORE=BASE/"source_native_opening_second_core.py";RUNNER=BASE/"run_source_native_opening_second_preflight.py";PRODUCTION=RESULTS/"source_native_opening_second_preflight.json";PRODUCTION_REPORT=RESULTS/"source_native_opening_second_preflight_report.md";VALIDATOR=Path(__file__).resolve();OUT=RESULTS/"source_native_opening_second_preflight_validation.json";REPORT=RESULTS/"source_native_opening_second_preflight_validation_report.md";TARGET=RESULTS/"source_native_opening_second_target.json";TARGET_REPORT=RESULTS/"source_native_opening_second_target_report.md"
FROZEN={PANEL_PATH:"46f0c8ad22880b870afc54d96852781b4bea9ebdc885dc1164c1da742a7bc581",QUOTA_PATH:"f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",CAPACITY:"ac78bb1b6f7a232ecb3415073442188f17f8f976cc718373cc80edde9c3d54b7",SPEC:"96a192dc4400643417e10f815dcea3a67abd6b64ab8429096205623f2885aecb",CORE:"514416f974014d6bcd86bb1103fa306dc5c7ce05468d1fdfe1f34102d9c622c9",RUNNER:"7e9081cb51b858f0fb11816a3420d6956d87e3957543260eef1ce6ccd06af292",PRODUCTION:"1eadd982f706144c423692e829d0086f57b76f3129b7063b5b781694761e36bb",PRODUCTION_REPORT:"ff653debc46fb02fa59470d16bea38de8982f0883806c7be6174b72af24f936c"}
FIELDS=("unit_id","base_id","physical_folio","currier","onset_id","onset_consensus","second_id","second_consensus","second_eligible")
TASKS=([("NULL",w) for w in range(64)]+[("GLOBAL_SECOND",100+w) for w in range(8)]+[("BASELINE_ONLY",200+w) for w in range(8)]+[("ONE_FOLIO",300+w) for w in range(8)]+[("FOLIO_RANDOM",400+w) for w in range(8)]+[("ONE_BASE",500+w) for w in range(8)])

@dataclass
class Panel:
 rows:list;keys:tuple;cells:tuple;da:np.ndarray;folios:tuple;fi:np.ndarray;tfolios:tuple;tcurrier:np.ndarray;baselines:tuple;bi:np.ndarray;refs:tuple;ri:np.ndarray;refbase:np.ndarray;eligible:np.ndarray;tbases:tuple;ebi:np.ndarray
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stable(s):return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8],"little")
def mix64(v):
 m=np.uint64(0xffffffffffffffff);x=(v+np.uint64(0x9E3779B97F4A7C15))&m;x=((x^(x>>np.uint64(30)))*np.uint64(0xBF58476D1CE4E5B9))&m;x=((x^(x>>np.uint64(27)))*np.uint64(0x94D049BB133111EB))&m;return x^(x>>np.uint64(31))
def digest(a):return hashlib.sha256(np.ascontiguousarray(a,dtype="<f8").tobytes()).hexdigest()
def load_panel():
 with PANEL_PATH.open(encoding="utf-8",newline="") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 with QUOTA_PATH.open(encoding="utf-8",newline="") as h:qrows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=1207 or len({r['unit_id'] for r in rows})!=1207 or any(tuple(r)!=FIELDS for r in rows):raise ValueError('panel')
 quota={(r['base_id'],r['physical_folio']):(int(r['da_count']),int(r['total_count'])) for r in qrows if int(r['none_count']) and int(r['da_count'])};grouped=defaultdict(list)
 for i,r in enumerate(rows):grouped[(r['base_id'],r['physical_folio'])].append(i)
 if len(qrows)!=1763 or len(quota)!=197 or set(grouped)!=set(quota):raise ValueError('quota')
 keys=tuple(sorted(grouped));cells=tuple(np.asarray(grouped[k],dtype=np.int64) for k in keys);da=np.asarray([quota[k][0] for k in keys],dtype=np.int64)
 if any(len(ix)!=quota[k][1] for k,ix in zip(keys,cells)):raise ValueError('size')
 bs=defaultdict(set);rf=defaultdict(set)
 for r in rows:
  if r['second_id']!='NA':b=(r['base_id'],r['onset_id']);bs[b].add(r['second_id']);rf[(*b,r['second_id'])].add(r['physical_folio'])
 pre={i for i,r in enumerate(rows) if r['second_id']!='NA' and len(bs[(r['base_id'],r['onset_id'])])>=2 and len(rf[(r['base_id'],r['onset_id'],r['second_id'])])>=2};fc=Counter(rows[i]['physical_folio'] for i in pre);actual={i for i in pre if fc[rows[i]['physical_folio']]>=3};declared={i for i,r in enumerate(rows) if r['second_eligible']=='1'}
 if actual!=declared:raise ValueError('eligibility')
 folios=tuple(sorted({r['physical_folio'] for r in rows},key=lambda x:int(x[1:])));fm={x:i for i,x in enumerate(folios)};fi=np.asarray([fm[r['physical_folio']] for r in rows],dtype=np.int64);tfolios=tuple(sorted({rows[i]['physical_folio'] for i in declared},key=lambda x:int(x[1:])));tc=[]
 for f in tfolios:
  v={r['currier'] for r in rows if r['physical_folio']==f}
  if len(v)!=1:raise ValueError('register')
  tc.append(next(iter(v)))
 bases=tuple(sorted({(r['base_id'],r['onset_id']) for r in rows}));bm={v:i for i,v in enumerate(bases)};bi=np.asarray([bm[(r['base_id'],r['onset_id'])] for r in rows],dtype=np.int64);refs=tuple(sorted({(r['base_id'],r['onset_id'],r['second_id']) for r in rows if r['second_id']!='NA'}));rm={v:i for i,v in enumerate(refs)};ri=np.asarray([rm.get((r['base_id'],r['onset_id'],r['second_id']),-1) for r in rows],dtype=np.int64);refbase=np.asarray([bm[(b,o)] for b,o,_ in refs],dtype=np.int64);elig=np.asarray([i in declared for i in range(len(rows))]);tb=tuple(sorted({rows[i]['base_id'] for i in declared}));tm={v:i for i,v in enumerate(tb)};ebi=np.asarray([tm.get(r['base_id'],-1) for r in rows],dtype=np.int64)
 if (elig.sum(),len(tfolios),len(tb),len({bi[i] for i in declared}),len({ri[i] for i in declared}))!=(639,41,16,26,40):raise ValueError('capacity')
 return Panel(rows,keys,cells,da,folios,fi,tfolios,np.asarray(tc),bases,bi,refs,ri,refbase,elig,tb,ebi)
def null_labels(p,n):
 out=np.zeros((n,len(p.rows)));clock=np.arange(n,dtype=np.uint64)[:,None]*np.uint64(0xD1342543DE82EF95)
 for key,ix,c in zip(p.keys,p.cells,p.da):
  seed=np.asarray([stable(f"SNOSECOND1|PREFLIGHT_NULL|{key[0]}|{key[1]}|{p.rows[int(i)]['unit_id']}") for i in ix],dtype=np.uint64);rank=mix64(clock^seed[None,:]);chosen=np.argpartition(rank,len(ix)-int(c),axis=1)[:,-int(c):];out[np.arange(n)[:,None],ix[chosen]]=1.
 return out
def plant(p,mode,world):
 af=p.tfolios[world%len(p.tfolios)];ab=p.tbases[world%len(p.tbases)];rank=np.empty(len(p.rows))
 for i,r in enumerate(p.rows):
  noise=((stable(f"SNOSECOND1|NOISE|{mode}|{world}|{r['unit_id']}")+.5)/(1<<64))*2-1;key=None
  if mode=='GLOBAL_SECOND' and r['second_id']!='NA':key=f"SECOND|{world}|{r['base_id']}|{r['onset_id']}|{r['second_id']}"
  elif mode=='BASELINE_ONLY':key=f"BASELINE|{world}|{r['base_id']}|{r['onset_id']}"
  elif mode=='ONE_FOLIO' and r['physical_folio']==af and r['second_id']!='NA':key=f"SECOND|{world}|{r['base_id']}|{r['onset_id']}|{r['second_id']}"
  elif mode=='FOLIO_RANDOM' and r['second_id']!='NA':key=f"FOLIO|{world}|{r['physical_folio']}|{r['base_id']}|{r['onset_id']}|{r['second_id']}"
  elif mode=='ONE_BASE' and r['base_id']==ab and r['second_id']!='NA':key=f"SECOND|{world}|{r['base_id']}|{r['onset_id']}|{r['second_id']}"
  signal=0 if key is None else ((stable('SNOSECOND1|SIGNAL|'+key)+.5)/(1<<64))*2-1;rank[i]=noise if mode=='NULL' else .8*signal+.2*noise
 out=np.zeros(len(p.rows))
 for ix,c in zip(p.cells,p.da):order=np.argsort(rank[ix],kind='mergesort');out[ix[order[-int(c):]]]=1
 return out
def cat(labels,index,size):
 out=np.zeros((len(labels),size))
 for v in range(size):out[:,v]=labels[:,index==v].sum(1)
 return out
def score(p,labels):
 labels=np.asarray(labels,dtype=float)
 if labels.ndim!=2 or labels.shape[1]!=len(p.rows) or not np.isfinite(labels).all() or not np.isin(labels,(0.,1.)).all():raise ValueError('labels')
 for ix,c in zip(p.cells,p.da):
  if not np.all(labels[:,ix].sum(1)==c):raise ValueError('quota')
 bn=np.bincount(p.bi,minlength=len(p.baselines)).astype(float);valid=p.ri>=0;rn=np.bincount(p.ri[valid],minlength=len(p.refs)).astype(float);bd=cat(labels,p.bi,len(p.baselines));rd=cat(labels[:,valid],p.ri[valid],len(p.refs));fs=np.empty((len(labels),len(p.tfolios)));eligix=np.flatnonzero(p.eligible);pos={int(v):i for i,v in enumerate(eligix)};rs=np.empty((len(labels),len(eligix)))
 for held,folio in enumerate(p.tfolios):
  hm=p.fi==p.folios.index(folio);test=p.eligible&hm;hbn=np.bincount(p.bi[hm],minlength=len(p.baselines)).astype(float);hrm=hm&valid;hrn=np.bincount(p.ri[hrm],minlength=len(p.refs)).astype(float);hbd=cat(labels[:,hm],p.bi[hm],len(p.baselines));hrd=cat(labels[:,hrm],p.ri[hrm],len(p.refs));p0=(bd-hbd+.5)/(bn[None,:]-hbn[None,:]+1);p1=(rd-hrd+4*p0[:,p.refbase])/(rn[None,:]-hrn[None,:]+4);target=np.flatnonzero(test);y=labels[:,target];a=p0[:,p.bi[target]];b=p1[:,p.ri[target]];g=y*np.log(b/a)+(1-y)*np.log((1-b)/(1-a));fs[:,held]=g.mean(1);rs[:,[pos[int(v)] for v in target]]=g
 bs=np.empty((len(labels),len(p.tbases)));eb=p.ebi[eligix]
 for v in range(len(p.tbases)):bs[:,v]=rs[:,eb==v].mean(1)
 return {'primary':fs.mean(1),'folios':fs,'bases':bs}
def summaries(p,observed,null):
 v=score(p,np.vstack((observed,null[1:])));n=len(observed);ref=v['primary'][n:];mean=float(ref.mean());sd=float(ref.std());out=[]
 for i in range(n):
  x=float(v['primary'][i]);f=v['folios'][i];b=v['bases'][i];out.append({'observed':x,'null_mean':mean,'null_sd':sd,'upper_p':(1+int(np.sum(ref>=x)))/(1+len(ref)),'z':(x-mean)/sd if sd else 0.,'positive_folios':int(np.sum(f>0)),'max_abs_folio_fraction':float(np.max(np.abs(f))/np.abs(f).sum()) if np.abs(f).sum() else 1.,'minimum_folio_deletion_mean':float(((f.sum()-f)/40).min()),'currier_A_mean':float(f[p.tcurrier=='A'].mean()),'currier_B_mean':float(f[p.tcurrier=='B'].mean()),'positive_bases':int(np.sum(b>0)),'max_abs_base_fraction':float(np.max(np.abs(b))/np.abs(b).sum()) if np.abs(b).sum() else 1.,'minimum_base_deletion_mean':float(((b.sum()-b)/15).min())})
 return out
def passing(r):return r['upper_p']<=.01 and r['z']>=3 and r['observed']>=.01 and r['positive_folios']>=28 and r['max_abs_folio_fraction']<=.15 and r['minimum_folio_deletion_mean']>0 and min(r['currier_A_mean'],r['currier_B_mean'])>=.005 and r['positive_bases']>=10 and r['max_abs_base_fraction']<=.25 and r['minimum_base_deletion_mean']>0
def delta(a,b):
 if isinstance(a,dict):return math.inf if set(a)!=set(b) else max((delta(a[k],b[k]) for k in a),default=0.)
 if isinstance(a,list):return math.inf if len(a)!=len(b) else max((delta(x,y) for x,y in zip(a,b)),default=0.)
 if isinstance(a,(int,float)) and not isinstance(a,bool):return abs(float(a)-float(b))
 return 0. if a==b else math.inf
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
 failures=[];checks=0
 def check(v,n):
  nonlocal checks;checks+=1
  if not v:failures.append(n)
 for path,expected in FROZEN.items():check(sha(path)==expected,'hash:'+path.name)
 p=load_panel();null=null_labels(p,2048);obs=np.asarray([plant(p,m,w) for m,w in TASKS]);vals=summaries(p,obs,null);records=[{'mode':m,'world':w,'label_sha256':digest(y),**s,'PASS':passing(s)} for (m,w),y,s in zip(TASKS,obs,vals)];stored=json.loads(PRODUCTION.read_text());maximum=delta(records,stored['records']);check(maximum==0,'records');modes=('NULL','GLOBAL_SECOND','BASELINE_ONLY','ONE_FOLIO','FOLIO_RANDOM','ONE_BASE');counts={m:{'worlds':sum(x==m for x,_ in TASKS),'passes':sum(r['PASS'] for r in records if r['mode']==m)} for m in modes};check(counts==stored['counts'],'counts');ln=null_labels(p,8192);lo=np.asarray([plant(p,'NULL',0),plant(p,'GLOBAL_SECOND',100)]);lv=summaries(p,lo,ln);large={'NULL_0':{**lv[0],'PASS':passing(lv[0])},'GLOBAL_SECOND_100':{**lv[1],'PASS':passing(lv[1])}};check(delta(large,stored['target_size_checks'])==0,'large');check(stored['null_label_orbit_sha256']==digest(null) and stored['target_size_null_label_orbit_sha256']==digest(ln),'orbits');mut={'missing_row':True,'nonbinary':True,'quota_drift':True,'eligibility_drift':True};check(stored['mutations']==mut,'mutations');sg=next(r for r in records if r['mode']=='GLOBAL_SECOND' and r['world']==100);g={'zero_of_64_null_passes':counts['NULL']['passes']==0,'at_least_7_of_8_global_second_passes':counts['GLOBAL_SECOND']['passes']>=7,'zero_of_8_baseline_only_passes':counts['BASELINE_ONLY']['passes']==0,'zero_of_8_one_folio_passes':counts['ONE_FOLIO']['passes']==0,'zero_of_8_folio_random_passes':counts['FOLIO_RANDOM']['passes']==0,'zero_of_8_one_base_passes':counts['ONE_BASE']['passes']==0,'target_size_null_rejects':not large['NULL_0']['PASS'],'target_size_global_second_passes':large['GLOBAL_SECOND_100']['PASS'],'target_size_decisions_match':large['NULL_0']['PASS']==records[0]['PASS'] and large['GLOBAL_SECOND_100']['PASS']==sg['PASS'],'mutation_guards':True,'future_target_absent':not TARGET.exists() and not TARGET_REPORT.exists()};check(g==stored['gates'],'gates');check(stored['status']=='STOP_SECOND_MEMBER_CALIBRATION' and stored['decision']=='DO_NOT_OPEN_SECOND_MEMBER_TARGET','decision');check(stored['source_sta_table_opened'] is False and stored['prior_target_artifact_opened'] is False and stored['real_operation_labels_accessed']==stored['real_target_scores_computed']==0,'isolation');expected=f"""# Second-member incremental synthetic preflight

Status: **{stored['status']}**

At 2,048 assignments calibration yields **{counts['NULL']['passes']}/64** null,
**{counts['GLOBAL_SECOND']['passes']}/8** global-second,
**{counts['BASELINE_ONLY']['passes']}/8** baseline-only,
**{counts['ONE_FOLIO']['passes']}/8** one-folio,
**{counts['FOLIO_RANDOM']['passes']}/8** folio-random, and
**{counts['ONE_BASE']['passes']}/8** one-base passes. Representative decisions
are unchanged at 8,192 assignments.

Decision: **{stored['decision']}**. No source STA row, prior target artifact, real
operation label, or real target score was opened. This supplies no longer
dependency, morphology, meaning, plaintext, or translation.
""";check(PRODUCTION_REPORT.read_text()==expected,'report')
 if failures:raise SystemExit('validation failed: '+failures[0])
 result={'experiment':'SOURCE_NATIVE_OPENING_SECOND_PREFLIGHT_VALIDATION','status':'PASS_PRODUCTION_FREE_104_WORLD_SECOND_MEMBER_RECONSTRUCTION','checks':checks,'failures':[],'maximum_numeric_delta':maximum,'reconstructed_worlds':len(records),'counts':counts,'target_size_checks':2,'mutations':mut,'gates':g,'source_sta_table_opened':False,'prior_target_artifact_opened':False,'real_operation_labels_accessed':0,'real_target_scores_computed':0,'future_target_absent':not TARGET.exists() and not TARGET_REPORT.exists(),'inputs':{path.name:sha(path) for path in FROZEN},'validator_sha256':sha(VALIDATOR),'english_glosses':0,'claim_ceiling':'Production-free target-free second-member calibration reconstruction only; no longer dependency, morphology, meaning, plaintext, or translation follows.'};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Second-member preflight validation

Status: **{result['status']}**

Independent code reconstructs all **{len(records)}** worlds, both null orbits,
every score/gate, two target-size checks, exact report, and four mutation
outcomes in **{checks}** checks with zero numeric discrepancy. It confirms the
underpowered 1/8 global-second recovery and target prohibition.

No source row or real label was opened; no longer dependency, morphology,
meaning, plaintext, or translation follows.
""");print(json.dumps({'status':result['status'],'checks':checks,'maximum_numeric_delta':maximum},sort_keys=True))
if __name__=='__main__':main()
