#!/usr/bin/env python3
"""Primary whole-equation search; preserves every journal result immediately."""
import collections,json,sys,time
from pathlib import Path
from shared import A,E,R,TARGET,OLD,LIMITS,module,read,put,utc,verify_lock,work,journal

def cases_and_jobs():
    source=read(E/'src/SOURCE.json');cases=[];jobs=[]
    for edition,panel in read(R/TARGET).items():
        for p in panel:
            assert not p['page'].startswith('f84') and p['page']!='f116v'
            eligible=all(x['anchor_eligible'] for x in p['lines'])
            words=[w for x in p['lines'] for w in x['words']];assert len(words)==p['groups']
            for writer,stream in source['streams'].items():
                c=dict(case=len(cases)+1,edition=edition,paragraph=p['id'],page=p['page'],leaf=p['leaf'],writer=writer,
                    source_atoms=122,source_types=27,target_groups=len(words),independent_meaning_confirmation_capacity=0)
                if eligible:
                    c.update(status='PENDING',words=words,loci=[x['locus'] for x in p['lines']],source_ids=[x['source_ids'] for x in p['lines']])
                    jobs.append((c['case'],dict(atoms=stream['atoms'],words=words)))
                else:c.update(status='UNKNOWN_SOURCE',ineligible_lines=[x['locus'] for x in p['lines'] if not x['anchor_eligible']])
                cases.append(c)
    assert len(cases)==2698
    return cases,jobs

def main():
    if '--worker' in sys.argv:
        j=json.load(sys.stdin);f=module('frozen987finite',OLD/'finite.py')
        out=f.solve(j['atoms'],j['words'],seconds=3,max_nodes=200000)
        if out['status']=='SAT':module('frozen987ground',OLD/'validate.py').ground(j['atoms'],j['words'],out['code'])
        print(json.dumps(out,separators=(',',':')));return
    verify_lock();cases,jobs=cases_and_jobs()
    if '--assemble' not in sys.argv:
        started=time.time();receipt=dict(started_utc=utc(),started_unix=started,deadline_unix=started+900,limits=LIMITS,eligible_jobs=len(jobs),completion='RUNNING')
        put('EXECUTION_RECEIPT.json',receipt)
        print(json.dumps(dict(cases=len(cases),eligible_jobs=len(jobs))),flush=True)
        work(Path(__file__).resolve(),jobs,receipt['deadline_unix'],8,'PRIMARY_JOURNAL.jsonl')
        receipt.update(primary_completed_utc=utc(),primary_elapsed_seconds=time.time()-started,completion='PRIMARY_COMPLETED');put('EXECUTION_RECEIPT.json',receipt)
    outcomes=journal('PRIMARY_JOURNAL.jsonl');assert set(outcomes).issubset({i for i,j in jobs})
    for c in cases:
        if c['status']=='PENDING':
            c['primary']=outcomes.get(c['case'],dict(status='UNKNOWN_UNRETAINED'))
            c['status']=c['primary']['status']
    put('PRIMARY_CASES.json.gz',cases)
    result=dict(cases=len(cases),eligible_jobs=len(jobs),retained_jobs=len(outcomes),counts=dict(collections.Counter(c['status'] for c in cases)))
    put('PRIMARY_RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
