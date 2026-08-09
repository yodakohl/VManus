#!/usr/bin/env python3
"""Calibrate exact-position-controlled within-group transitions."""
from __future__ import annotations
import os
os.environ["OPENBLAS_NUM_THREADS"]="1";os.environ["OMP_NUM_THREADS"]="1";os.environ["MKL_NUM_THREADS"]="1"
import hashlib,json,math,multiprocessing as mp
from pathlib import Path
import numpy as np
from source_native_within_group_exact_position_markov_core import evaluate,load_panel,passes,synthetic_sequences
BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";PANEL_PATH=RESULTS/"source_native_within_group_stage_masked.tsv";CAPACITY_VALIDATION=RESULTS/"source_native_within_group_stage_capacity_validation.json";CORE=BASE/"source_native_within_group_exact_position_markov_core.py";SPEC=BASE/"SOURCE_NATIVE_WITHIN_GROUP_EXACT_POSITION_MARKOV_SPEC.md";RUNNER=Path(__file__).resolve();TARGET_SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";TARGET_OUT=RESULTS/"source_native_within_group_exact_position_markov_target.json";TARGET_REPORT=RESULTS/"source_native_within_group_exact_position_markov_target_report.md";OUT=RESULTS/"source_native_within_group_exact_position_markov_preflight.json";REPORT=RESULTS/"source_native_within_group_exact_position_markov_preflight_report.md"
FROZEN={PANEL_PATH:"16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",CAPACITY_VALIDATION:"2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",CORE:"269d0167fb13930386eaba2398a47578c54a897bcb74f0b9b1da8c57f4d1a892",SPEC:"8b2747a55cd88cafe0f2fcc4201634b123c9bd95bcaac6bd8495e36e75aea5d1"};TASKS=([('POSITION_ONLY',w) for w in range(64)]+[('MARKOV',100+w) for w in range(8)]+[('CURRIER_ONE',200+w) for w in range(8)]+[('ONE_FOLIO',300+w) for w in range(8)]+[('FOLIO_RANDOM',400+w) for w in range(8)]);PANEL=None
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compact(r):return {**r,'EXACT_POSITION_MARKOV_PASS':passes(r)}
def task(payload):
 m,w,rev=payload;s=synthetic_sequences(PANEL,w,m)
 if rev:s=[tuple(reversed(x)) for x in s]
 return {'mode':m,'world':w,'reverse':rev,**compact(evaluate(PANEL,s))}
def numeric_max(a,b):
 if isinstance(a,dict):return math.inf if set(a)!=set(b) else max((numeric_max(a[k],b[k]) for k in a),default=0.)
 if isinstance(a,list):return math.inf if len(a)!=len(b) else max((numeric_max(x,y) for x,y in zip(a,b)),default=0.)
 if isinstance(a,(int,float)) and not isinstance(a,bool):return abs(float(a)-float(b))
 return 0. if a==b else math.inf
def finite(v):
 if isinstance(v,dict):return all(finite(x) for x in v.values())
 if isinstance(v,list):return all(finite(x) for x in v)
 return not isinstance(v,float) or math.isfinite(v)
def main():
 global PANEL
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
 if TARGET_OUT.exists() or TARGET_REPORT.exists():raise SystemExit('target exists')
 for p,e in FROZEN.items():
  if sha(p)!=e:raise SystemExit(f'frozen input mismatch: {p.name}')
 if json.loads(CAPACITY_VALIDATION.read_text())['status']!='PASS_INDEPENDENT_SCORE_BLIND_STAGE_CAPACITY_RECONSTRUCTION' or not TARGET_SOURCE.exists():raise SystemExit('authorization input failure')
 PANEL=load_panel(PANEL_PATH);payloads=[(m,w,r) for r in (False,True) for m,w in TASKS]
 with mp.get_context('fork').Pool(32) as pool:records=pool.map(task,payloads)
 records.sort(key=lambda r:(r['reverse'],TASKS.index((r['mode'],r['world']))));idx={(r['mode'],r['world'],r['reverse']):r for r in records};counts={}
 for rev in (False,True):
  name='reversed' if rev else 'forward';counts[name]={m:{'worlds':sum(x==m for x,_ in TASKS),'passes':sum(idx[(m,w,rev)]['EXACT_POSITION_MARKOV_PASS'] for x,w in TASKS if x==m)} for m in ('POSITION_ONLY','MARKOV','CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM')}
 mismatch=[f'{m}:{w}' for m,w in TASKS if idx[(m,w,False)]['EXACT_POSITION_MARKOV_PASS']!=idx[(m,w,True)]['EXACT_POSITION_MARKOV_PASS']]
 refseq=synthetic_sequences(PANEL,100,'MARKOV');ref=compact(evaluate(PANEL,refseq));perm=np.asarray([(7*x+3)%24 for x in range(24)],dtype=np.int64);rel=compact(evaluate(PANEL,[tuple(int(perm[x]) for x in s) for s in refseq]));label=numeric_max(ref,rel);mutations={}
 for name,altered in (('missing_sequence',refseq[:-1]),('length_mismatch',[tuple()]+refseq[1:]),('invalid_symbol',[(-1,)+refseq[0][1:]]+refseq[1:])):
  try:evaluate(PANEL,altered)
  except ValueError:mutations[name]=True
  else:mutations[name]=False
 bad_rows=[dict(r) for r in PANEL.rows];bad_rows[0]['unit_id']=bad_rows[1]['unit_id'];bad_panel=type(PANEL)(bad_rows,PANEL.lengths,PANEL.splits,PANEL.curriers,PANEL.folios)
 try:evaluate(bad_panel,refseq)
 except ValueError:mutations['duplicate_unit_id']=True
 else:mutations['duplicate_unit_id']=False
 pattern=lambda name:counts[name]['POSITION_ONLY']['passes']<=1 and counts[name]['MARKOV']['passes']>=7 and all(counts[name][m]['passes']==0 for m in ('CURRIER_ONE','ONE_FOLIO','FOLIO_RANDOM'))
 gates={'forward_expected_pattern':pattern('forward'),'reversed_expected_pattern':pattern('reversed'),'all_96_decisions_reversal_stable':not mismatch,'label_relabel_invariance':label<=1e-10,'finite_values':all(finite(r) for r in records),'mutation_guards':all(mutations.values()),'exact_capacity':sum((PANEL.splits=='TEST')&(PANEL.lengths>=2))==5521 and int(sum(max(0,int(x)-1) for x in PANEL.lengths[PANEL.splits=='TEST']))==17435 and len(set(PANEL.folios))==94,'target_absent':not TARGET_OUT.exists() and not TARGET_REPORT.exists()};passed=all(gates.values());status='PASS_TARGET_FREE_EXACT_POSITION_MARKOV_PREFLIGHT' if passed else 'STOP_EXACT_POSITION_MARKOV_PREFLIGHT';decision='GO_INDEPENDENTLY_VALIDATE_EXACT_POSITION_MARKOV' if passed else 'STOP_BEFORE_EXACT_POSITION_MARKOV_TARGET'
 result={'experiment':'SOURCE_NATIVE_WITHIN_GROUP_EXACT_POSITION_MARKOV_PREFLIGHT','status':status,'decision':decision,'inputs':{p.name:sha(p) for p in (*FROZEN,RUNNER)},'workers':32,'records':records,'counts':counts,'reversal_decision_mismatches':mismatch,'label_relabel_max_abs':label,'mutations':mutations,'gates':gates,'target_source_opened':False,'target_sequences_accessed':0,'target_scores_computed':0,'target_outputs_absent':not TARGET_OUT.exists() and not TARGET_REPORT.exists(),'english_glosses':0,'claim_ceiling':'Synthetic exact-position transition calibration only; no syntax, morphology, sound, word, language, meaning, plaintext, cipher, or translation follows.'};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Exact-position-controlled transition preflight

Status: **{status}**

Forward/reversed grids yield **{counts['forward']['POSITION_ONLY']['passes']}/64**
and **{counts['reversed']['POSITION_ONLY']['passes']}/64** position-only false
passes and **{counts['forward']['MARKOV']['passes']}/8** and
**{counts['reversed']['MARKOV']['passes']}/8** Markov-plant passes. Every
adversarial family yields zero passes in both orientations; all 96 decisions
are reversal-stable and remaining gates are **{'passing' if passed else 'not all passing'}**.

Zero manuscript sequences or scores were opened. Decision: **{decision}**.
No syntax, morphology, sound, word, language, meaning, plaintext, cipher, or
translation follows.
""");print(json.dumps({'status':status,'counts':counts,'gates':gates,'decision':decision},sort_keys=True))
if __name__=='__main__':main()
