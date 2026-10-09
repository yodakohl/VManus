#!/usr/bin/env python3
"""Finite necessary-domain projection. No complete decoding or word assignments."""
import gzip, hashlib, itertools, json, time
from pathlib import Path
E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
P = ROOT / 'experiments/yolo/gdt1096_dioscorides_finite_recurrent_domains/artifacts'
CASES = {528:('f17v','INFEASIBLE'),764:('f46r','UNKNOWN'),784:('f48v','INFEASIBLE'),788:('f49r','INFEASIBLE'),792:('f49v','UNKNOWN'),892:('f8r','UNKNOWN'),904:('f93r','UNKNOWN')}
LIMIT = 200000
SECONDS = 5

def compatible(a,b):
    return not (a.startswith(b) or b.startswith(a))

class Limit(Exception): pass

def solve(domains, limit=LIMIT, seconds=SECONDS):
    start=time.monotonic(); nodes=0
    def visit(todo, chosen):
        nonlocal nodes
        nodes+=1
        if nodes>limit or time.monotonic()-start>seconds: raise Limit
        if not todo: return chosen
        a=min(todo, key=lambda a:(len(todo[a]),a))
        if not todo[a]: return None
        for v in sorted(todo[a],key=lambda v:(len(v),v)):
            rest={b:tuple(w for w in ws if compatible(v,w)) for b,ws in todo.items() if b!=a}
            if any(not ws for ws in rest.values()): continue
            answer=visit(rest,{**chosen,a:v})
            if answer is not None: return answer
        return None
    try:
        witness=visit({a:tuple(sorted(set(v))) for a,v in domains.items()}, {})
        status='SAT_PROJECTION' if witness is not None else 'EXHAUSTED'
    except Limit:
        witness=None; status='UNKNOWN_LIMIT'
    return dict(status=status,witness=witness,nodes=nodes,seconds=time.monotonic()-start)

def controls():
    universe=('a','ab','b')
    subsets=[tuple(universe[i] for i in range(3) if m>>i&1) for m in range(1,8)]
    count=0
    for n in (1,2,3,4):
        for lists in itertools.product(subsets,repeat=n):
            expected=any(all(compatible(a,b) for a,b in itertools.combinations(values,2)) for values in itertools.product(*lists))
            result=solve({str(i):v for i,v in enumerate(lists)})
            assert result['status']!='UNKNOWN_LIMIT'
            assert (result['status']=='SAT_PROJECTION')==expected
            count+=1
    assert solve({'A':universe,'B':universe,'C':universe})['status']=='EXHAUSTED'
    assert solve({'A':[]})['status']=='EXHAUSTED'
    assert solve({'A':['a'],'B':['b']},limit=0)['status']=='UNKNOWN_LIMIT'
    return count

def main():
    out=E/'artifacts/RESULT.json'
    assert not out.exists(), 'Use isolated copy for a rerun; no overwrite.'
    lock=json.loads((E/'artifacts/REGISTRATION_LOCK.json').read_text())
    for path, expected in lock['files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
    certificates=json.loads(gzip.decompress((P/'CERTIFICATES.json.gz').read_bytes()))
    old=json.loads((P/'CASES.json').read_text())
    projections=[]; results=[]
    for index,(page,status) in CASES.items():
        row=old[index]
        assert row['page']==page and row['edition']=='IT2a'
        assert not page.startswith('f84') and page!='f116v'
        domains=certificates[str(index)]['final_domains']
        assert domains and all(isinstance(v,list) and all(isinstance(s,str) and s for s in v) for v in domains.values())
        projection=dict(case=index,page=page,edition='IT2a',old_status=status,primary=status=='UNKNOWN',domains=domains)
        projections.append(projection)
        result=solve(domains)
        results.append({k:v for k,v in projection.items() if k!='domains'} | dict(atoms=len(domains),values=sum(map(len,domains.values())),**result))
        print(index,page,result['status'],result['nodes'],flush=True)
    (E/'artifacts/INPUT_DOMAINS.json').write_text(json.dumps(projections,indent=2,sort_keys=True)+'\n')
    out.write_text(json.dumps(dict(scope='Necessary prefix-free representatives only; raw exhaustion awaits separate replay.',cases=results),indent=2,sort_keys=True)+'\n')

if __name__=='__main__':
    import sys
    if '--controls' in sys.argv: print(json.dumps(dict(status='PASS',exhaustive_cases=controls())))
    else: main()
