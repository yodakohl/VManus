#!/usr/bin/env python3
"""Validate the finite primary rollup and its independent full-enumeration receipt."""
import collections,gzip,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    for p,h in read(E/'artifacts/BINDINGS.json')['files'].items():assert sha(ROOT/p)==h,p
    scope=read(E/'artifacts/SCOPE.json');assert sha(E/'artifacts/PLAN.json.gz')==scope['plan_sha256']
    plan=read(E/'artifacts/PLAN.json.gz');expected={}
    for p in plan['paragraphs']:
        for g in p['groups']:
            for vi,v in enumerate('aeiouy'):
                if g['inherent_bits']&(1<<vi):
                    key=p['edition']+'_'+p['paragraph_id']+'_'+str(g['mask'])+'_'+v
                    assert key not in expected;expected[key]=(p['edition'],p['paragraph_id'],g['mask'],v)
    assert len(expected)==scope['cases']
    rows=read(E/'artifacts/CASES.json.gz');seen=set();lexical=accepted=reused=0
    for r in rows:
        key=r['case_id'];assert key in expected and key not in seen;seen.add(key)
        assert tuple(r[f] for f in ('edition','paragraph_id','mask','inherent'))==expected[key]
        assert r['status']=='COMPLETE'
        assert len(r['values'])==len(r['grammar_accepted'])==r['stats']['complete_assignments']
        assert len({tuple(v) for v in r['values']})==len(r['values'])
        assert sum(r['grammar_accepted'])==r['stats']['solutions_accepted']
        lexical+=len(r['values']);accepted+=sum(r['grammar_accepted']);reused+=r['origin']=='GDT905_REUSED'
    assert seen==set(expected) and reused==scope['reused_complete_cases']
    independent=read(E/'artifacts/INDEPENDENT_COMPLETE_VALIDATION.json')
    assert independent['status']=='PASS_COMPLETE'
    assert independent['expected_cases']==independent['independently_complete_cases']==len(rows)
    assert independent['pending_cases']==0 and not independent['failures']
    assert independent['validator_sha256']==sha(E/'src/validate_complete.py')
    assert independent['plan_logical_sha256']==hashlib.sha256(gzip.decompress((E/'artifacts/PLAN.json.gz').read_bytes())).hexdigest()
    result=read(E/'artifacts/RESULT.json')
    assert result['cases']==len(rows) and result['lexical_keys']==lexical and result['grammar_accepted']==accepted
    assert result['cases_sha256']==sha(E/'artifacts/CASES.json.gz')
    receipt=dict(status='PASS',cases=len(rows),lexical_keys=lexical,grammar_accepted=accepted,confirmed_meanings=0,cases_sha256=sha(E/'artifacts/CASES.json.gz'),independent_receipt_sha256=sha(E/'artifacts/INDEPENDENT_COMPLETE_VALIDATION.json'),validator_sha256=sha(Path(__file__)))
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
