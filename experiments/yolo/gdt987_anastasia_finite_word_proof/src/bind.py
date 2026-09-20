#!/usr/bin/env python3
import argparse
import datetime
import hashlib
import json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
P='experiments/yolo/gdt986_anastasia_complete_condition_trees/'
INPUTS=[P+x for x in ('src/SOURCE.json','src/model.py','METHOD.md','PREREG_LOCK.json','artifacts/CASES.json','artifacts/VALIDATION.json','REPORT.md')]+['experiments/yolo/gdt919_complete_sator_word_equations/src/validate.py']
SCIENCE=['DECISION.md','METHOD.md','PREREGISTRATION.md','src/finite.py','src/run.py','src/fixtures.py','src/validate.py','artifacts/PRE_RUN_FIXTURES.json']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('--register',action='store_true');p.add_argument('--status',default='REGISTERED_UNSCORED');a=p.parse_args()
 lock=E/'PREREG_LOCK.json'
 if a.register:
  assert not lock.exists()
  names=INPUTS+[str((E/x).relative_to(R)) for x in SCIENCE]
  lock.write_text(json.dumps({'registered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{x:sha(R/x) for x in names}},indent=2)+'\n')
 else:
  for x,h in json.loads(lock.read_text())['files'].items():assert sha(R/x)==h,x
 m=json.loads((E/'experiment.json').read_text())
 m.update(title='Finite whole-word proof of unchanged Anastasia codes',question='Can bounded finite word-aligned enumeration settle the unchanged complete986equations and produce a full conditional code?',status=a.status,
  dependencies=['GDT919','GDT986'],claim_ceiling='Exact unchanged-code consequences and explicit computational unknowns only;0confirmed meanings or independent confirmation.',inputs=[dict(path=x,role='fixed_input',sha256=sha(R/x)) for x in INPUTS],outputs=[])
 for f in sorted(E.rglob('*')):
  if f.is_file() and f.name!='experiment.json' and '__pycache__' not in f.parts and 'runtime' not in f.parts:
   m['outputs'].append(dict(path=str(f.relative_to(R)),role='primary_report' if f.name=='REPORT.md' else 'source_or_artifact',sha256=sha(f)))
 v=E/'artifacts/VALIDATION.json'
 if v.exists():m['validation']=dict(artifact=str(v.relative_to(R)),status=json.loads(v.read_text())['status'])
 (E/'experiment.json').write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(status=m['status'],inputs=len(m['inputs']),outputs=len(m['outputs']))))

if __name__=='__main__':main()
