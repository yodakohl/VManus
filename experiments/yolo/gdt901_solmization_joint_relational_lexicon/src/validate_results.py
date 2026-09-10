#!/usr/bin/env python3
"""Bind and aggregate the complete fixed-case results from two independent engines."""
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((BASE/'artifacts'/name).read_text())
def main():
    gate=read('RESULT.json');run=read('FIT_RUN_RECEIPT.json');independent_run=read('COUNT_RELAX_RUN_RECEIPT.json')
    assert len(run['cases'])==10 and {r['case'] for r in run['cases']}==set(range(10))
    assert all(r['exit_code']==0 and not r['stderr'] for r in run['cases'])
    cases=[]
    for i in range(10):
        fp=BASE/'artifacts'/f'FIT_IT2a_{i:02}.json';bp=BASE/'artifacts'/f'COUNT_RELAX_IT2a_{i:02}.json'
        f=json.loads(fp.read_text());b=json.loads(bp.read_text());a=read(f'WITNESS_AUDIT_IT2a_{i:02}.json')
        assert f['case']==b['case_index']==i and f['panel']==b['panel']=='IT2a'
        for field,name in [('source','SOURCE_INPUT.json'),('target','TARGET_INPUT.json'),('model_spec','MODEL_SPEC.json')]:
            assert f[field+'_sha256']==b['bindings'][field+'_sha256']==sha(BASE/'artifacts'/name)
        assert f['code_sha256']==sha(BASE/'src/fit.py') and b['code_sha256']==sha(BASE/'src/independent_count_relaxation.py')
        assert b['bindings']['observer_sha256']==sha(BASE/'artifacts/SOURCE_OBSERVER_B.json')
        assert b['bindings']['domains_sha256']==sha(BASE/'artifacts/INDEPENDENT_ROLE_DOMAINS.json')
        assert a['status']=='PASS' and a['fit_sha256']==sha(fp)
        assert f['status']==f['initial']['status']=='UNSAT' and not f['projections'] and not f['cuts']
        assert b['solver_status']=='UNSAT' and b['status']=='FULL_CASE_UNSAT_BY_COUNT_HEAD_RELAXATION'
        assert f['workers']==2 and b['solver_threads']==1 and f['budget_seconds']==1800 and b['budget_seconds']==1200
        assert f['elapsed_seconds']<1800 and b['elapsed_total_seconds']<1200
        cases.append({'case':i,'role_partition':b['partition'],'primary':'UNSAT','independent_count_head':'UNSAT',
                      'primary_seconds':f['elapsed_seconds'],'independent_seconds':b['elapsed_total_seconds'],
                      'primary_sha256':sha(fp),'independent_sha256':sha(bp),'witness_audit_sha256':sha(BASE/'artifacts'/f'WITNESS_AUDIT_IT2a_{i:02}.json')})
    capacity=[c for c in gate['cases'] if c['panel']!='IT2a']
    assert len(capacity)==30 and all(c['status']=='CAPACITY_STOP' and c['available']<c['required']==22 for c in capacity)
    out={'schema':'GDT901_COMPLETE_MODEL_RESULT_V1','status':'ALL_TEN_CASES_UNSAT_INDEPENDENT_COUNT_HEAD_CONFIRMATION','validation':'PASS',
         'source_sha256':sha(BASE/'artifacts/SOURCE_INPUT.json'),'target_sha256':sha(BASE/'artifacts/TARGET_INPUT.json'),'model_spec_sha256':sha(BASE/'artifacts/MODEL_SPEC.json'),
         'cases':cases,'other_panels':{'CONSENSUS':1,'RF1b':11,'ZL3b':14},'required_records':22,
         'independent_run_receipt_sha256':sha(BASE/'artifacts/COUNT_RELAX_RUN_RECEIPT.json'),'primary_run_receipt_sha256':sha(BASE/'artifacts/FIT_RUN_RECEIPT.json'),
         'primary_wall_seconds':run['wall_seconds'],'complete_witnesses':0,'order_cuts':0,'confirmed_meanings':0,
         'conclusion':'The complete ten-partition source/head/global-word projection model is excluded already by independent count/head constraints. No reliance on morphology or order is necessary for exclusion.',
         'limits':'Two independently coded solver results, not an exported machine-checkable universal proof certificate. No general music, grammar, or translation conclusion; no held data evaluated.'}
    (BASE/'artifacts/FULL_RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'validation':'PASS','cases':10}))
if __name__=='__main__':main()
