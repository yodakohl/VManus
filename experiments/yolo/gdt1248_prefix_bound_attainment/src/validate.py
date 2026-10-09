#!/usr/bin/env python3
"""Explicit codeword DP, no runner imports; same author."""
import gzip,hashlib,itertools,json
from collections import Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
SIGN=('a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh')
SOURCE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'

def decode(w,codes):
    paths=[0]*(len(w)+1); paths[0]=1; back={}
    for i in range(len(w)):
        if not paths[i]: continue
        for code in codes:
            j=i+len(code)
            if j<=len(w) and w[i:j]==code:
                paths[j]+=paths[i];back[j]=(i,code)
    assert paths[-1]<=1
    if not paths[-1]: return None
    p=[];j=len(w)
    while j: j,c=back[j];p.append(c)
    p.reverse();return p

def controls():
    count=0
    for h in 'ab':
        codes=[(s,) for s in 'ab' if s!=h]+[(h,s) for s in 'ab']
        for n in range(11):
            for w in itertools.product('ab',repeat=n):
                result=decode(w,codes)
                # Runs of h at word end must have even length. Interior runs always parse.
                k=0
                for s in reversed(w):
                    if s!=h: break
                    k+=1
                assert (result is not None)==(k%2==0)
                if result is not None: assert tuple(x for c in result for x in c)==w
                count+=1
    return count

def main():
    lock=json.loads((E/'artifacts/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    data=json.loads(gzip.decompress((ROOT/SOURCE).read_bytes()))
    result=json.loads((E/'artifacts/RESULT.json').read_text())
    assert [(r['reader'],r['head']) for r in result['cases']]==[(r,h) for r in ('IT2a','RF1b','ZL3b') for h in ('cfh','cph','q')]
    checks=[]
    for r in result['cases']:
        rows=data[r['reader']];h=r['head'];codes=[(s,) for s in SIGN if s!=h]+[(h,s) for s in SIGN]
        assert len(codes)==43
        assert all(a[:len(b)]!=b and b[:len(a)]!=a for i,a in enumerate(codes) for b in codes[:i])
        parsed={w:decode(w,codes) for w in {tuple(row['units']) for row in rows}}
        failures=[];f_types=set();used=Counter();active=0
        for row in rows:
            assert not row['page'].startswith('f84') and row['page']!='f116v'
            w=tuple(row['units']);p=parsed[w]
            if p is None: failures.append(row['id']);f_types.add(w)
            else:
                assert tuple(x for c in p for x in c)==w
                used.update(p);active+=any(len(c)==2 for c in p)
        assert r['groups']==len(rows) and r['types']==len(parsed)
        assert r['failure_ids']==failures and r['failed_groups']==len(failures) and r['failed_types']==len(f_types)
        assert r['accepted_groups']==len(rows)-len(failures) and r['active_groups']==active
        assert r['used_in_accepted_groups']==len(used)
        assert r['code_usage']==[dict(units=list(c),occurrences=n) for c,n in sorted(used.items())]
        complete=not failures
        upper=len(used) if complete and active else None
        assert r['complete_code_upper_bound']==upper
        if upper is not None:
            assert upper>=27
            retained=list(used)
            # Every whole type still has a unique parse after unused entries removed.
            for w in parsed: assert decode(w,retained) is not None
        decision='EXACT_MINIMUM_27' if upper==27 else 'CONSTRUCTIVE_UPPER_BOUND' if upper is not None else 'CONSTRUCTION_CONTRADICTED' if failures else 'TRIVIAL_ONLY'
        assert r['decision']==decision
        checks.append(dict(reader=r['reader'],head=h,decision=decision,complete_code_upper_bound=upper))
    report=dict(status='PASS',cases=checks,implementation='Separate explicit codeword DP; same author.',meanings_confirmed=0)
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':
    import sys
    if '--controls' in sys.argv: print(json.dumps(dict(status='PASS',cases=controls())))
    else: main()
