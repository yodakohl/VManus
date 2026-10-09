#!/usr/bin/env python3
"""Separate fixed-variable search and direct witness accounting; same author."""
import gzip, hashlib, itertools, json, time
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
P=ROOT/'experiments/yolo/gdt1096_dioscorides_finite_recurrent_domains/artifacts'
EXPECTED={528:('f17v','INFEASIBLE'),764:('f46r','UNKNOWN'),784:('f48v','INFEASIBLE'),788:('f49r','INFEASIBLE'),792:('f49v','UNKNOWN'),892:('f8r','UNKNOWN'),904:('f93r','UNKNOWN')}

def conflict(a,b):
    n=min(len(a),len(b)); return a[:n]==b[:n]

def replay(domains,limit=200000,seconds=5):
    # Fixed reverse lexical variable order, no forward filtering or runner import.
    names=sorted(domains,reverse=True); used=[]; nodes=0; started=time.monotonic()
    class Bound(Exception): pass
    def rec(i):
        nonlocal nodes
        nodes+=1
        if nodes>limit or time.monotonic()-started>seconds: raise Bound
        if i==len(names): return True
        for s in sorted(set(domains[names[i]]),reverse=True):
            if any(conflict(s,t) for t in used): continue
            used.append(s)
            if rec(i+1): return True
            used.pop()
        return False
    try: state='SAT' if rec(0) else 'EXHAUSTED'
    except Bound: state='UNKNOWN_LIMIT'
    return dict(status=state,nodes=nodes,seconds=time.monotonic()-started)

def controls():
    u=('a','ab','b'); sets=[tuple(u[i] for i in range(3) if m>>i&1) for m in range(1,8)]; ncheck=0
    for n in (1,2,3,4):
        for sets_i in itertools.product(sets,repeat=n):
            valid=False
            for seq in itertools.product(*sets_i):
                if all(not conflict(seq[i],seq[j]) for i in range(n) for j in range(i)):
                    valid=True; break
            got=replay(dict(zip(map(str,range(n)),sets_i)))
            assert got['status']!='UNKNOWN_LIMIT' and (got['status']=='SAT')==valid
            ncheck+=1
    assert replay({'x':[]})['status']=='EXHAUSTED'
    assert replay({'x':['a']},limit=0)['status']=='UNKNOWN_LIMIT'
    return ncheck

def main():
    lock=json.loads((E/'artifacts/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    saved=json.loads((E/'artifacts/INPUT_DOMAINS.json').read_text())
    results=json.loads((E/'artifacts/RESULT.json').read_text())['cases']
    original=json.loads(gzip.decompress((P/'CERTIFICATES.json.gz').read_bytes()))
    rows=json.loads((P/'CASES.json').read_text())
    assert [r['case'] for r in saved]==list(EXPECTED)==[r['case'] for r in results]
    validated=[]
    for projection,r in zip(saved,results):
        i=r['case']; page,status=EXPECTED[i]; d=original[str(i)]['final_domains']
        assert projection['domains']==d and rows[i]['page']==page and rows[i]['edition']=='IT2a'
        for x in (projection,r):
            assert x['page']==page and x['old_status']==status and x['primary']==(status=='UNKNOWN')
        assert r['atoms']==len(d) and r['values']==sum(len(v) for v in d.values())
        v=dict(case=i,page=page,primary=r['primary'])
        if r['status']=='SAT_PROJECTION':
            w=r['witness']; assert set(w)==set(d)
            assert all(s in d[a] and s for a,s in w.items())
            values=list(w.values())
            assert all(not conflict(values[j],values[k]) for j in range(len(values)) for k in range(j))
            v['status']='VERIFIED_SAT_PROJECTION'
        elif r['status']=='EXHAUSTED':
            assert r['witness'] is None
            v['replay']=replay(d)
            assert v['replay']['status']!='SAT','Contradictory implementations'
            v['status']='CERTIFIED_NEGATIVE' if v['replay']['status']=='EXHAUSTED' else 'UNVERIFIED_NEGATIVE'
        else:
            assert r['status']=='UNKNOWN_LIMIT' and r['witness'] is None
            v['status']='UNKNOWN_LIMIT'
        validated.append(v)
    primary=[x['status'] for x in validated if x['primary']]
    if all(s=='VERIFIED_SAT_PROJECTION' for s in primary): decision='ALL_FOUR_OPEN_CASES_PASS_WEAK_PROJECTION'
    elif all(s=='CERTIFIED_NEGATIVE' for s in primary): decision='ALL_FOUR_OPEN_CASES_CERTIFIED_NEGATIVE'
    elif 'CERTIFIED_NEGATIVE' in primary: decision='PARTIAL_CERTIFIED_EXCLUSIONS'
    else: decision='UNRESOLVED_NO_CERTIFIED_EXCLUSIONS'
    report=dict(status='PASS',decision=decision,cases=validated,same_author=True,meanings_confirmed=0,scope='Projection only; old stronger INFEASIBLE cases never revived.')
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    import sys
    if '--controls' in sys.argv: print(json.dumps(dict(status='PASS',exhaustive_cases=controls())))
    else: main()
