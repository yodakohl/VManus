#!/usr/bin/env python3
"""Target-free calibration of the within-group Markov increment."""

from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
import hashlib,json,math,multiprocessing as mp
from pathlib import Path
import numpy as np
from source_native_within_group_markov_core import evaluate,load_panel,passes,synthetic_sequences

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_within_group_stage_masked.tsv";CAPACITY_VALIDATION=RESULTS/"source_native_within_group_stage_capacity_validation.json";CORE=BASE/"source_native_within_group_markov_core.py";SPEC=BASE/"SOURCE_NATIVE_WITHIN_GROUP_MARKOV_INCREMENT_TEST_SPEC.md";RUNNER=Path(__file__).resolve();TARGET_SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";TARGET_OUT=RESULTS/"source_native_within_group_markov_target.json";TARGET_REPORT=RESULTS/"source_native_within_group_markov_target_report.md";OUT=RESULTS/"source_native_within_group_markov_preflight.json";REPORT=RESULTS/"source_native_within_group_markov_preflight_report.md"
FROZEN={PANEL_PATH:"16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",CAPACITY_VALIDATION:"2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",CORE:"8bc3020e69bea9f50854fd1b512a327bb9322a513000e13f267bb65315fd787e",SPEC:"7a923c422b143dc4187c56a940a691959016c258bc1b83468a2cc598fd9a1b66"}
TASKS=([('POSITION_ONLY',w) for w in range(64)]+[('MARKOV',100+w) for w in range(8)]+[('CURRIER_ONE',200+w) for w in range(8)]+[('ONE_FOLIO',300+w) for w in range(8)]+[('FOLIO_RANDOM',400+w) for w in range(8)]);PANEL=None
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def compact(result):return {**result,'MARKOV_INCREMENT_PASS':passes(result)}
def task(payload):
 mode,world,reverse=payload;sequences=synthetic_sequences(PANEL,world,mode)
 if reverse:sequences=[tuple(reversed(s)) for s in sequences]
 return {'mode':mode,'world':world,'reverse':reverse,**compact(evaluate(PANEL,sequences))}
def numeric_max(a,b):
 if isinstance(a,dict):return math.inf if set(a)!=set(b) else max((numeric_max(a[k],b[k]) for k in a),default=0.)
 if isinstance(a,list):return math.inf if len(a)!=len(b) else max((numeric_max(x,y) for x,y in zip(a,b)),default=0.)
 if isinstance(a,(int,float)) and not isinstance(a,bool):return abs(float(a)-float(b))
 return 0. if a==b else math.inf
def main():
 global PANEL
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite Markov preflight')
 if TARGET_OUT.exists() or TARGET_REPORT.exists():raise SystemExit('Markov target artifact exists')
 for path,expected in FROZEN.items():
  if sha(path)!=expected:raise SystemExit(f'frozen Markov input mismatch: {path.name}')
 if json.loads(CAPACITY_VALIDATION.read_text())['status']!='PASS_INDEPENDENT_SCORE_BLIND_STAGE_CAPACITY_RECONSTRUCTION':raise SystemExit('capacity validation not PASS')
 if not TARGET_SOURCE.exists():raise SystemExit('target source absent')
 PANEL=load_panel(PANEL_PATH);payloads=[(m,w,r) for r in (False,True) for m,w in TASKS]
 with mp.get_context('fork').Pool(32) as pool:records=pool.map(task,payloads)
 records.sort(key=lambda row:(row['reverse'],TASKS.index((row['mode'],row['world']))));indexed={(r['mode'],r['world'],r['reverse']):r for r in records}
 counts={}
 for reverse in (False,True):
  name='reversed' if reverse else 'forward';counts[name]={m:{'worlds':sum(x==m for x,_ in TASKS),'passes':sum(indexed[(m,w,reverse)]['MARKOV_INCREMENT_PASS'] for x,w in TASKS if x==m)} for m in ('POSITION_ONLY','MARKOV','CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM')}
 mismatch=[f'{m}:{w}' for m,w in TASKS if indexed[(m,w,False)]['MARKOV_INCREMENT_PASS']!=indexed[(m,w,True)]['MARKOV_INCREMENT_PASS']]
 refseq=synthetic_sequences(PANEL,100,'MARKOV');ref=compact(evaluate(PANEL,refseq));perm=np.asarray([(7*x+3)%24 for x in range(24)],dtype=np.int64);rel=compact(evaluate(PANEL,[tuple(int(perm[x]) for x in s) for s in refseq]));label_delta=numeric_max(ref,rel)
 mutations={}
 for name,altered in (('missing_sequence',refseq[:-1]),('length_mismatch',[tuple()]+refseq[1:]),('invalid_symbol',[(-1,)+refseq[0][1:]]+refseq[1:])):
  try:evaluate(PANEL,altered)
  except ValueError:mutations[name]=True
  else:mutations[name]=False
 ids=[r['unit_id'] for r in PANEL.rows];mutations['duplicate_unit_id']=len(set(ids+[ids[0]]))!=len(ids)+1
 def finite(value):
  if isinstance(value,dict):return all(finite(x) for x in value.values())
  if isinstance(value,list):return all(finite(x) for x in value)
  return not isinstance(value,float) or math.isfinite(value)
 pattern=lambda name:counts[name]['POSITION_ONLY']['passes']<=1 and counts[name]['MARKOV']['passes']>=7 and all(counts[name][m]['passes']==0 for m in ('CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM'))
 gates={'forward_expected_pattern':pattern('forward'),'reversed_expected_pattern':pattern('reversed'),'all_96_decisions_reversal_stable':not mismatch,'label_relabel_invariance':label_delta<=1e-10,'finite_values':all(finite(r) for r in records),'mutation_guards':all(mutations.values()),'exact_capacity':len(PANEL.rows)==21899 and sum(PANEL.splits=='TEST')==5630 and len(set(PANEL.folios))==94,'target_absent':not TARGET_OUT.exists() and not TARGET_REPORT.exists()}
 passed=all(gates.values());status='PASS_TARGET_FREE_WITHIN_GROUP_MARKOV_PREFLIGHT' if passed else 'STOP_WITHIN_GROUP_MARKOV_PREFLIGHT';decision='GO_INDEPENDENTLY_VALIDATE_MARKOV_PREFLIGHT' if passed else 'STOP_BEFORE_MARKOV_TARGET'
 result={'experiment':'SOURCE_NATIVE_WITHIN_GROUP_MARKOV_PREFLIGHT','status':status,'decision':decision,'inputs':{p.name:sha(p) for p in (*FROZEN,RUNNER)},'workers':32,'records':records,'counts':counts,'reversal_decision_mismatches':mismatch,'label_relabel_max_abs':label_delta,'mutations':mutations,'gates':gates,'target_source_opened':False,'target_sequences_accessed':0,'target_scores_computed':0,'target_outputs_absent':not TARGET_OUT.exists() and not TARGET_REPORT.exists(),'english_glosses':0,'claim_ceiling':'Synthetic calibration of a first-order family increment beyond exact length, five-position bins, and Currier only; no syntax, morphology, sound, word, language, meaning, plaintext, cipher, or translation follows.'}
 OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Source-native within-group Markov-increment preflight

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
""");print(json.dumps({'status':status,'counts':counts,'gates':gates,'decision':decision},sort_keys=True))
if __name__=='__main__':main()
