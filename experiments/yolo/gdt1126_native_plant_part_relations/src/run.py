#!/usr/bin/env python3
"""Read-only source/case accounting; does not validate visual or semantic claims."""
import json,hashlib,pathlib,sys
BASE=pathlib.Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
def check():
 m=json.loads((BASE/'experiment.json').read_text())
 for row in m['inputs']:
  f=ROOT/row['path']
  assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256'], row['path']
 plan=json.loads((BASE/'src/CASE_PLAN.json').read_text())
 assert len(plan['pairs'])==7
 assert plan['sealed']==['f84','f84r'] and plan['f116v_forbidden']
 out=BASE/'artifacts/OBSERVATIONS.json'
 if not out.exists():
  return {'status':'PREREG_ACCOUNTING_PASS_OBSERVATIONS_PENDING','cases':7,'semantic_validation':False}
 observations=json.loads(out.read_text())
 assert [r['id'] for r in observations['cases']]==[r['id'] for r in plan['pairs']]
 for row in observations.get('pins',[]):
  f=ROOT/row['path']
  assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256'],row['path']
 return {'status':'CASE_AND_PIN_ACCOUNTING_PASS','cases':7,'semantic_validation':False,'visual_claims_validated':False}
if __name__=='__main__':
 try:print(json.dumps(check(),indent=2))
 except Exception as e:print('ACCOUNTING_FAIL',str(e));sys.exit(1)
