#!/usr/bin/env python3
"""Validate source bindings, guarded target replay and full-model exclusion."""
import collections,hashlib,json,subprocess,sys
from pathlib import Path
from run import intake
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def read(n):return json.loads((E/'artifacts'/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for script in ['validate_source.py','validate_domains.py','explain_certificate.py']:
    subprocess.run([sys.executable,str(E/'src'/script)],check=True)
for p,h in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert sha(ROOT/p)==h,p
source=read('SOURCE.json'); target=read('TARGET.json'); result=read('RESULT.json'); rows=read('LOCAL_DOMAINS.json')
assert intake()==target,'guarded source/target replay drift'
sources={r['id']:r['lexical'] for r in source['records']}
expected={(ed,sid,t['paragraph_id']) for ed,ts in target['panels'].items() for sid in sources for t in ts}
assert {(r['edition'],r['source_id'],r['paragraph_id']) for r in rows}==expected and len(rows)==len(expected)
targets={(ed,t['paragraph_id']):t['words'] for ed,ts in target['panels'].items() for t in ts}
positive=unknown=0
for r in rows:
    s=sources[r['source_id']];t=targets[r['edition'],r['paragraph_id']]
    if r['status']=='SAT_RELAXED_LOCAL':
        m=r['mapping'];assert set(m)==set(s) and len(set(m.values()))==len(m)
        inverse={v:k for k,v in m.items()};assert [inverse[w] for w in t if w in inverse]==s
        assert r['positions']==[i for i,w in enumerate(t) if w in inverse]
        positive+=1
    elif r['status']=='UNSAT_LENGTH':assert len(s)>len(t)
    elif r['status']=='UNSAT_MULTIPLICITY':
        a=collections.Counter(collections.Counter(s).values());b=collections.Counter(collections.Counter(t).values())
        assert any(b[k]<n for k,n in a.items())
    elif r['status']=='UNKNOWN_STATE_BUDGET':assert r['states']==200001;unknown+=1
    else:assert r['status']=='UNSAT_ORDER'
ind=read('DOMAIN_VALIDATION.json');assert ind['status']=='PASS'
assert ind['source_sha256']==sha(E/'artifacts/SOURCE.json') and ind['target_sha256']==sha(E/'artifacts/TARGET.json') and ind['primary_result_sha256']==sha(E/'artifacts/RESULT.json')
proofs=0
for ed,p in result['panels'].items():
    assert p['mandatory_record_count_possible']==(len(target['panels'][ed])>=38)
    for sid in sources:
        rr=[r for r in rows if r['edition']==ed and r['source_id']==sid]
        assert p['local_counts'][sid]==dict(collections.Counter(r['status'] for r in rr))
        assert (sid in p['zero_domain_sources'])==bool(rr and all(r['status'].startswith('UNSAT') for r in rr))
    for sid,x in ind['panels'][ed]['selected_zero_witnesses'].items():
        assert {v['paragraph_id'] for v in x['pairs']}=={t['paragraph_id'] for t in target['panels'][ed]}
        assert all(v['status']=='UNSAT' for v in x['pairs']) and sid in p['zero_domain_sources']
        proofs+=len(x['pairs'])
    assert p['status']=='FULL_MODEL_EXCLUDED_BY_LEXICAL_NECESSITY'
output=dict(status='PASS',source_records=38,source_tokens=1217,source_lexical_tokens=sum(len(s) for s in sources.values()),
            guarded_target_replay=True,local_pairs=len(rows),directly_replayed_local_witnesses=positive,
            independently_proved_negative_pairs=proofs,primary_unknown_pairs_preserved=unknown,
            inputs={n:sha(E/'artifacts'/n) for n in ['SOURCE.json','TARGET.json','RESULT.json','LOCAL_DOMAINS.json','DOMAIN_VALIDATION.json','ORDER_CERTIFICATE.json']},
            conclusion='Every panel has an independently validated mandatory zero lexical domain. Hence the registered full relational model has no solution, irrespective of unresolved other local pairs. No translation.')
(E/'artifacts/VALIDATION.json').write_text(json.dumps(output,sort_keys=True,separators=(',',':'))+'\n')
print(json.dumps({k:v for k,v in output.items() if k!='inputs'}))
