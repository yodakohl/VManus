"""Exact exposed-source control; no manuscript intake or decoder."""
from pathlib import Path
from fractions import Fraction
from itertools import permutations
import datetime
import hashlib
import json
import time

E = Path(__file__).resolve().parents[1]
R = E.parents[2]
NUMERALS = ('1','2','3','4','5','6','7','9','10','11','16','20','25','45','80','100')


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def number(s, p):
    v = 0
    for c in s:
        v = 10*v+p[int(c)]
    return v


def account(weights, grades, desired, mass=None, silver=None):
    total = sum(weights)
    fine = sum(x*g for x,g in zip(weights, grades))
    return ((mass is None or total == mass) and fine == total*desired
            and (silver is None or fine == silver))


def values(p):
    n = {s: number(s,p) for s in NUMERALS}
    g = (n['3'],n['4'],n['6'])
    weights = {
      'A': (n['1'],n['1'],n['3']),
      'B': (n['2'],n['5'],n['9']),
      'P': (n['2']+Fraction(n['1'],n['2']),n['6']+Fraction(n['1'],n['4']),n['11']+Fraction(n['1'],n['4'])),
      'D': (n['10'],n['25'],n['45']),
      'Q': (n['2'],n['7'],n['11'])}
    return n,g,weights


def main():
    lock = json.loads((E/'PREREG_LOCK.json').read_text())
    for name,digest in lock['files'].items():
        assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest, name
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    t0 = time.monotonic()
    leading = {int(s[0]) for s in NUMERALS}
    assert leading == set(range(1,10))
    counts = dict(enumerated=0,L0=0,L1=0,L2=0,L3=0)
    failures = dict(L0=0,L1=0,L2=0,L3=0)
    survivors = {key:[] for key in ('L1','L2','L3')}
    domains = {key:[set() for _ in range(10)] for key in ('L0','L1','L2','L3')}
    # L0 is exactly p[0]==0: every other digit is a positive leading digit.
    for p in permutations(range(10)):
        counts['enumerated']+=1
        if p[0] != 0:
            failures['L0']+=1
            continue
        counts['L0']+=1
        for i,v in enumerate(p): domains['L0'][i].add(v)
        n = {s:number(s,p) for s in NUMERALS}
        g = (n['3'],n['4'],n['6'])
        if not account((n['2'],n['7'],n['11']),g,n['5'],n['20'],n['100']):
            failures['L1']+=1
            continue
        mapping=''.join(map(str,p))
        counts['L1']+=1; survivors['L1'].append(mapping)
        for i,v in enumerate(p): domains['L1'][i].add(v)
        _,_,w=values(p)
        if not account(w['P'],g,n['5'],n['20']):
            failures['L2']+=1
            continue
        counts['L2']+=1; survivors['L2'].append(mapping)
        for i,v in enumerate(p): domains['L2'][i].add(v)
        if not (account(w['A'],g,n['5'],n['5'],n['25'])
                and account(w['B'],g,n['5'],n['16'],n['80'])
                and account(w['D'],g,n['5'])):
            failures['L3']+=1
            continue
        counts['L3']+=1; survivors['L3'].append(mapping)
        for i,v in enumerate(p): domains['L3'][i].add(v)
    assert counts['enumerated']==3628800
    assert sum(failures.values())+counts['L3']==counts['enumerated']
    assert '0123456789' in survivors['L3'], 'SOURCE_IDENTITY_CONTROL_INVALID'
    table=[]
    for mapping in survivors['L3']:
        n,g,w=values(tuple(map(int,mapping)))
        for name in ('A','B','P','D','Q'):
            total=sum(w[name]); fine=sum(x*y for x,y in zip(w[name],g))
            table.append(dict(mapping=mapping,account=name,grades=list(g),target=n['5'],weights=list(map(str,w[name])),mass=str(total),fine=str(fine),mean=str(Fraction(fine,total))))
    # Already disclosed rational countermodel, preserving six distinct labels.
    free=[]
    for w in ((Fraction(1),Fraction(12),Fraction(7)),(Fraction(5),Fraction(20,3),Fraction(25,3))):
        assert account(w,(3,4,7),5,20,100)
        free.append(dict(weights=list(map(str,w)),mass=str(sum(w)),fine=str(sum(x*y for x,y in zip(w,(3,4,7))))))
    assert len(set(Fraction(v) for row in free for v in row['weights']))==6
    P=(Fraction(5,2),Fraction(25,4),Fraction(45,4)); Q=(Fraction(2),Fraction(7),Fraction(11))
    diff=[4*(a-b) for a,b in zip(P,Q)]
    assert diff==[2,-3,1]
    # Substitution c=3b-2a in Q/20 gives t=2b-a.
    assert (Q[0]-2*Q[2])/20==-1 and (Q[1]+3*Q[2])/20==2
    elapsed=time.monotonic()-t0
    result=dict(experiment='GDT971',status='SOURCE_NUMERAL_VALUES_UNIQUE' if counts['L3']==1 else 'SOURCE_NUMERAL_VALUES_NONUNIQUE',scope='exposed source control only; no Voynich data',started_utc=started,elapsed_seconds=elapsed,counts=counts,first_failure_counts=failures,digit_domains={k:[sorted(x) for x in v] for k,v in domains.items()},surviving_mappings=survivors,source_identity_pass=True,final_accounts=table,free_label_countermodel=free,relative_grade_relation=dict(coefficients=[2,-3,1],target_coefficients=[-1,2,0],affine_normalized=[0,1,2,3]),confirmed_words=0,independent_manuscript_confirmation=0)
    write(E/'artifacts/RESULT.json',result)
    lines=['mapping\taccount\tgrades\tdesired_grade\tcomponent_weights\tmass\tfine_content\tmean']
    for x in table:
        lines.append('\t'.join([x['mapping'],x['account'],','.join(map(str,x['grades'])),str(x['target']),','.join(x['weights']),x['mass'],x['fine'],x['mean']]))
    (E/'artifacts/CANDIDATE_VALUES.tsv').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(status=result['status'],counts=counts,elapsed_seconds=elapsed)))


if __name__=='__main__': main()
