from pathlib import Path
import hashlib,json
d=Path(__file__).resolve().parents[1]
m=json.loads((d/'experiment.json').read_text())
checks={x['path']:hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'] for x in m['inputs']}
checks['exact_three_cases']=len(json.loads((d/'src/CASE_PLAN.json').read_text())['cases'])==3
checks['both_seals']=m['sealed_data']=={'f84':'FORBIDDEN','f84r':'FORBIDDEN'}
result={'status':'PASS' if all(checks.values()) else 'FAIL','claim_ceiling':'File identity and case accounting only, not native reading or semantic validation','checks':checks}
(d/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(checks)}))
assert all(checks.values())
