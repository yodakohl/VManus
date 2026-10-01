#!/usr/bin/env python3
"""Read-only registered source/case accounting; no visual/semantic validation."""
from pathlib import Path
import json,hashlib
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
def check():
 m=json.loads((BASE/'experiment.json').read_text())
 for b in m['inputs']:
  assert hashlib.sha256((ROOT/b['path']).read_bytes()).hexdigest()==b['sha256'],b['path']
 p=json.loads((BASE/'src/CASE_PLAN.json').read_text())
 assert [x['id'] for x in p['pairs']]==['C1','C2']
 assert [x['pharma_canvas'] for x in p['pairs']]==['1006234','1006253']
 assert p['sealed']==['f84','f84r'] and p['f116v_forbidden']
 f=BASE/'artifacts/RESULT.json'
 if not f.exists():return {'status':'PREREG_ACCOUNTING_PASS_OBSERVATIONS_PENDING','semantic_validation':False}
 q=json.loads(f.read_text());assert [x['id'] for x in q['cases']]==['C1','C2']
 for b in q['pins']:
  assert hashlib.sha256((ROOT/b['path']).read_bytes()).hexdigest()==b['sha256'],b['path']
 return {'status':'CASE_AND_PIN_ACCOUNTING_PASS','semantic_validation':False,'visual_validation':False}
if __name__=='__main__':print(json.dumps(check(),indent=2))
