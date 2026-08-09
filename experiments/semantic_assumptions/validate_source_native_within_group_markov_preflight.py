#!/usr/bin/env python3
"""Independent reconstruction of the within-group Markov preflight."""

from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
import hashlib,json,math,multiprocessing as mp
from collections import defaultdict
from pathlib import Path
import numpy as np
import validate_source_native_within_group_stage_preflight_v2 as clean

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_within_group_stage_masked.tsv";CAPACITY_VALIDATION=RESULTS/"source_native_within_group_stage_capacity_validation.json";CLEAN_VALIDATOR=BASE/"validate_source_native_within_group_stage_preflight_v2.py";CORE=BASE/"source_native_within_group_markov_core.py";SPEC=BASE/"SOURCE_NATIVE_WITHIN_GROUP_MARKOV_INCREMENT_TEST_SPEC.md";RUNNER=BASE/"run_source_native_within_group_markov_preflight.py";PRODUCTION=RESULTS/"source_native_within_group_markov_preflight.json";PRODUCTION_REPORT=RESULTS/"source_native_within_group_markov_preflight_report.md";TARGET_OUT=RESULTS/"source_native_within_group_markov_target.json";TARGET_REPORT=RESULTS/"source_native_within_group_markov_target_report.md";OUT=RESULTS/"source_native_within_group_markov_preflight_validation.json";REPORT=RESULTS/"source_native_within_group_markov_preflight_validation_report.md"
FROZEN={PANEL_PATH:"16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",CAPACITY_VALIDATION:"2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",CLEAN_VALIDATOR:"9d33a815fc10b75aa02a57568207691cdb33daf1165c5060c463cb811f8ed30a",CORE:"8bc3020e69bea9f50854fd1b512a327bb9322a513000e13f267bb65315fd787e",SPEC:"7a923c422b143dc4187c56a940a691959016c258bc1b83468a2cc598fd9a1b66",RUNNER:"a52840900597fd7cd772dfd7190d76d90aa5f6d2ca03df8e3b392a9979c86ade",PRODUCTION:"978363232bb3e2213013ac63f99dcee1b1de437ce04c5f61940039f11ea5cff3",PRODUCTION_REPORT:"3130bddec3c1341f4fce8bb89eba86904898e8fb1e456e0a9c0264f71b88f9c5"}
TASKS=([('POSITION_ONLY',w) for w in range(64)]+[('MARKOV',100+w) for w in range(8)]+[('CURRIER_ONE',200+w) for w in range(8)]+[('ONE_FOLIO',300+w) for w in range(8)]+[('FOLIO_RANDOM',400+w) for w in range(8)]);PANEL=None;ALPHA=.5
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def bins(length):return np.minimum(4,(np.arange(length,dtype=np.int64)*5)//length)
def fit(panel,sequences,markov):
 contexts=25 if markov else 1;counts={(c,l):np.full((5,contexts,24),ALPHA,dtype=np.float64) for c in 'AB' for l in range(1,12)}
 for row,seq,length in zip(panel.rows,sequences,panel.lengths):
  if row['split']!='TRAIN':continue
  cell=counts[(row['currier'],int(length))];prev=24
  for slot,symbol in zip(bins(len(seq)),seq):context=prev if markov else 0;cell[slot,context,symbol]+=1.;prev=symbol
 return {k:v/v.sum(axis=2,keepdims=True) for k,v in counts.items()}
def probability(seq,length,currier,model,markov):
 theta=model[(currier,length)];total=0.;prev=24
 for slot,symbol in zip(bins(len(seq)),seq):context=prev if markov else 0;total+=math.log(theta[slot,context,symbol]);prev=symbol
 return total
def sign_p(pos,total):return sum(math.comb(total,k) for k in range(pos,total+1))/(2**total)
def summary(values):
 effects=[]
 for folio in sorted(values,key=lambda v:int(v[1:])):effects.append(sum(x for x,_ in values[folio])/sum(n for _,n in values[folio]))
 a=np.asarray(effects,dtype=np.float64);deletion=(a.sum()-a)/(len(a)-1);den=float(np.abs(a).sum())
 return {'effect_equal_folio':float(a.mean()),'positive_folios':int((a>0).sum()),'folios':len(a),'sign_p':sign_p(int((a>0).sum()),len(a)),'minimum_leave_one_folio_out':float(deletion.min()),'max_abs_contribution_fraction':float(np.abs(a).max()/den) if den else 1.}
def evaluate(panel,sequences):
 if len(sequences)!=len(panel.rows) or any(len(s)!=n for s,n in zip(sequences,panel.lengths)):raise ValueError('geometry')
 if any(not s or any(x<0 or x>=24 for x in s) for s in sequences):raise ValueError('symbol')
 base=fit(panel,sequences,False);full=fit(panel,sequences,True);cal=0.;cs=0
 for row,seq,length in zip(panel.rows,sequences,panel.lengths):
  if row['split']=='CAL':cal+=probability(seq,int(length),row['currier'],full,True)-probability(seq,int(length),row['currier'],base,False);cs+=len(seq)
 by,unseen_by=defaultdict(list),defaultdict(list);cur={'A':defaultdict(list),'B':defaultdict(list)};train={(r['currier'],int(n),s) for r,n,s in zip(panel.rows,panel.lengths,sequences) if r['split']=='TRAIN'};total=ut=0.;tg=ts=ug=us=0
 for row,seq,length in zip(panel.rows,sequences,panel.lengths):
  if row['split']!='TEST':continue
  gain=probability(seq,int(length),row['currier'],full,True)-probability(seq,int(length),row['currier'],base,False);n=len(seq);f=row['physical_folio'];by[f].append((gain,n));cur[row['currier']][f].append((gain,n));total+=gain;tg+=1;ts+=n
  if (row['currier'],int(length),seq) not in train:unseen_by[f].append((gain,n));ut+=gain;ug+=1;us+=n
 return {'cal_gain_per_symbol':cal/cs,'test_groups':tg,'test_symbols':ts,'gain_equal_symbol':total/ts,'gain':summary(by),'unseen':{'groups':ug,'symbols':us,'gain_equal_symbol':ut/us,**summary(unseen_by)},'currier':{c:{'gain':summary(cur[c])} for c in 'AB'}}
def passes(r):return r['cal_gain_per_symbol']>0 and r['test_groups']==5630 and r['gain']['folios']==24 and r['gain']['effect_equal_folio']>=.01 and r['gain']['positive_folios']>=18 and r['gain']['sign_p']<=.01 and r['gain']['minimum_leave_one_folio_out']>0 and r['gain']['max_abs_contribution_fraction']<=.15 and r['unseen']['groups']>=500 and r['unseen']['effect_equal_folio']>=.005 and r['unseen']['minimum_leave_one_folio_out']>0 and all(r['currier'][c]['gain']['effect_equal_folio']>=.003 and r['currier'][c]['gain']['minimum_leave_one_folio_out']>0 and r['currier'][c]['gain']['positive_folios']/r['currier'][c]['gain']['folios']>=.65 for c in 'AB')
def synthetic(panel,world,mode):
 if mode not in {'POSITION_ONLY','MARKOV','CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM'}:raise ValueError('mode')
 folios=sorted(set(panel.folios),key=lambda v:int(v[1:]));active_folio=folios[world%len(folios)];maps={c:tuple(sorted(range(24),key=lambda x:clean.stable_u64(f"SNWGM001|{world}|MAP|{c}|{x}"))) for c in 'AB'};out=[]
 for row,length_value in zip(panel.rows,panel.lengths):
  length=int(length_value);bucket=clean.stable_u64(f"SNWGM001|BUCKET|{row['unit_id']}")%128;base_maps={slot:sorted(range(24),key=lambda x:clean.stable_u64(f"SNWGM001|{world}|BASE|{row['currier']}|{length}|{slot}|{x}")) for slot in range(5)};transition=maps[row['currier']]
  if mode=='FOLIO_RANDOM':transition=tuple(sorted(range(24),key=lambda x:clean.stable_u64(f"SNWGM001|{world}|FMAP|{row['physical_folio']}|{row['currier']}|{x}")))
  seq=[];prev=clean.stable_u64(f"SNWGM001|{world}|START|{row['split']}|{row['currier']}|{length}|{bucket}")%24
  for position,slot in enumerate(bins(length)):
   u=(clean.stable_u64(f"SNWGM001|{world}|U|{row['split']}|{row['currier']}|{length}|{bucket}|{position}")+.5)/(1<<64);base=base_maps[int(slot)];symbol=base[0] if u<.36 else (base[1] if u<.57 else clean.stable_u64(f"SNWGM001|{world}|R|{row['split']}|{row['currier']}|{length}|{bucket}|{position}")%24);active=mode in {'MARKOV','CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM'} and (mode!='CURRIER_ONE' or row['currier']=='B') and (mode!='ONE_FOLIO' or row['physical_folio']==active_folio)
   if active and position>0 and u<.45:symbol=transition[prev]
   seq.append(int(symbol));prev=int(symbol)
  out.append(tuple(seq))
 return out
def compact(r):return {**r,'MARKOV_INCREMENT_PASS':passes(r)}
def worker(payload):
 m,w,rev=payload;s=synthetic(PANEL,w,m)
 if rev:s=[tuple(reversed(x)) for x in s]
 return m,w,rev,compact(evaluate(PANEL,s))
def numeric_max(a,b):
 if isinstance(a,dict):return math.inf if set(a)!=set(b) else max((numeric_max(a[k],b[k]) for k in a),default=0.)
 if isinstance(a,list):return math.inf if len(a)!=len(b) else max((numeric_max(x,y) for x,y in zip(a,b)),default=0.)
 if isinstance(a,(int,float)) and not isinstance(a,bool):return abs(float(a)-float(b))
 return 0. if a==b else math.inf
def finite(v):
 if isinstance(v,dict):return all(finite(x) for x in v.values())
 if isinstance(v,list):return all(finite(x) for x in v)
 return not isinstance(v,float) or math.isfinite(v)
def expected_report(status,decision,counts,passed):return f"""# Source-native within-group Markov-increment preflight

Status: **{status}**

Forward/reversed grids yield **{counts['forward']['POSITION_ONLY']['passes']}/64**
and **{counts['reversed']['POSITION_ONLY']['passes']}/64** position-only false
passes, with **{counts['forward']['MARKOV']['passes']}/8** and
**{counts['reversed']['MARKOV']['passes']}/8** Markov-plant passes. Currier-one,
one-folio, and folio-random adversaries yield zero passes in both orientations.
All 96 decisions are reversal-stable and all remaining gates are
**{'passing' if passed else 'not all passing'}**.

The target was existence-tested only; zero family sequences or scores were
opened. Decision: **{decision}**. No syntax, morphology, sound, word, language,
meaning, plaintext, cipher, or translation follows.
"""
def main():
 global PANEL
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
 failures=[];checks=0
 def check(ok,name):
  nonlocal checks;checks+=1
  if not ok:failures.append(name)
 for path,expected in FROZEN.items():check(sha(path)==expected,f'hash:{path.name}')
 PANEL=clean.load_panel();payloads=[(m,w,r) for r in (False,True) for m,w in TASKS]
 with mp.get_context('fork').Pool(32) as pool:rebuilt=pool.map(worker,payloads)
 idx={(m,w,r):v for m,w,r,v in rebuilt};prod=json.loads(PRODUCTION.read_text());stored={(x['mode'],x['world'],x['reverse']):x for x in prod['records']};check(set(idx)==set(stored),'identities');max_delta=0.
 for key,value in idx.items():delta=numeric_max({'mode':key[0],'world':key[1],'reverse':key[2],**value},stored[key]);max_delta=max(max_delta,delta);check(delta<=1e-12,f'record:{key}')
 counts={}
 for rev in (False,True):
  name='reversed' if rev else 'forward';counts[name]={m:{'worlds':sum(x==m for x,_ in TASKS),'passes':sum(idx[(m,w,rev)]['MARKOV_INCREMENT_PASS'] for x,w in TASKS if x==m)} for m in ('POSITION_ONLY','MARKOV','CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM')}
 check(prod['counts']==counts,'counts');mismatch=[f'{m}:{w}' for m,w in TASKS if idx[(m,w,False)]['MARKOV_INCREMENT_PASS']!=idx[(m,w,True)]['MARKOV_INCREMENT_PASS']];check(prod['reversal_decision_mismatches']==mismatch,'reversal')
 refseq=synthetic(PANEL,100,'MARKOV');ref=compact(evaluate(PANEL,refseq));perm=np.asarray([(7*x+3)%24 for x in range(24)],dtype=np.int64);rel=compact(evaluate(PANEL,[tuple(int(perm[x]) for x in s) for s in refseq]));label=numeric_max(ref,rel);check(abs(prod['label_relabel_max_abs']-label)<=1e-12,'label')
 mutations={}
 for name,altered in (('missing_sequence',refseq[:-1]),('length_mismatch',[tuple()]+refseq[1:]),('invalid_symbol',[(-1,)+refseq[0][1:]]+refseq[1:])):
  try:evaluate(PANEL,altered)
  except ValueError:mutations[name]=True
  else:mutations[name]=False
 ids=[r['unit_id'] for r in PANEL.rows];mutations['duplicate_unit_id']=len(set(ids+[ids[0]]))!=len(ids)+1;check(prod['mutations']==mutations,'mutations')
 pattern=lambda name:counts[name]['POSITION_ONLY']['passes']<=1 and counts[name]['MARKOV']['passes']>=7 and all(counts[name][m]['passes']==0 for m in ('CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM'))
 gates={'forward_expected_pattern':pattern('forward'),'reversed_expected_pattern':pattern('reversed'),'all_96_decisions_reversal_stable':not mismatch,'label_relabel_invariance':label<=1e-10,'finite_values':all(finite(v) for v in idx.values()),'mutation_guards':all(mutations.values()),'exact_capacity':len(PANEL.rows)==21899 and sum(PANEL.splits=='TEST')==5630 and len(set(PANEL.folios))==94,'target_absent':not TARGET_OUT.exists() and not TARGET_REPORT.exists()}
 check(prod['gates']==gates,'gates');check(all(gates.values()),'pass');check(prod['status']=='PASS_TARGET_FREE_WITHIN_GROUP_MARKOV_PREFLIGHT' and prod['decision']=='GO_INDEPENDENTLY_VALIDATE_MARKOV_PREFLIGHT','decision');check(prod['target_source_opened'] is False and prod['target_sequences_accessed']==0 and prod['target_scores_computed']==0 and prod['target_outputs_absent'] is True,'isolation');check(PRODUCTION_REPORT.read_text()==expected_report(prod['status'],prod['decision'],counts,True),'report')
 if failures:raise SystemExit('validation failed: '+failures[0])
 result={'experiment':'SOURCE_NATIVE_WITHIN_GROUP_MARKOV_PREFLIGHT_VALIDATION','status':'PASS_INDEPENDENT_192_WORLD_MARKOV_PREFLIGHT_RECONSTRUCTION','checks':checks,'failures':[],'reconstructed_worlds':192,'counts':counts,'max_record_numeric_delta':max_delta,'target_source_opened':False,'target_sequences_accessed':0,'target_scores_computed':0,'target_outputs_absent':True,'inputs':{p.name:sha(p) for p in FROZEN},'claim_ceiling':'Independent synthetic reconstruction only; no syntax, morphology, sound, word, language, meaning, plaintext, cipher, or translation follows.'}
 OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Within-group Markov preflight validation

Status: **{result['status']}**

A production-free implementation reconstructs all **192** synthetic records,
counts, invariance, mutations, gates, decision, and report in **{checks} checks**
with maximum numeric discrepancy **{max_delta:.3g}**. The target remains absent.

This validates calibration only and supplies no syntax, morphology, sound,
word, language, meaning, plaintext, cipher, or translation.
""");print(json.dumps({'status':result['status'],'checks':checks,'max_delta':max_delta},sort_keys=True))
if __name__=='__main__':main()
