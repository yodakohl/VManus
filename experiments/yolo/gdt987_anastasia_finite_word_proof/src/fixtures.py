#!/usr/bin/env python3
"""Small brute Cartesian oracle and unpinned complete-source controls."""
import itertools
import json
from pathlib import Path
from finite import solve
from validate import replay

E=Path(__file__).resolve().parents[1]


def ground(atoms,words,code):
    if set(code)!=set(atoms) or any(not v for v in code.values()):return False
    if any(a.startswith(b) or b.startswith(a) for a,b in itertools.combinations(code.values(),2)):return False
    if ''.join(code[a] for a in atoms)!=''.join(words):return False
    ends=set(itertools.accumulate(len(code[a]) for a in atoms))
    return set(itertools.accumulate(map(len,words)))<=ends


def oracle(atoms,words):
    symbols=sorted(set(atoms))
    pieces={w[i:j] for w in words for i in range(len(w)) for j in range(i+1,len(w)+1)}
    for values in itertools.product(pieces,repeat=len(symbols)):
        code=dict(zip(symbols,values))
        if ground(atoms,words,code):return code
    return None


def partitions(text):
    for mask in range(1<<(len(text)-1)):
        words=[];start=0
        for i in range(1,len(text)):
            if mask&(1<<(i-1)):words.append(text[start:i]);start=i
        words.append(text[start:]);yield words


def main():
    counts={'SAT':0,'UNSAT_FINITE':0}
    for size in range(1,5):
        for raw in itertools.product('ab',repeat=size):
            for words in partitions(''.join(raw)):
                for length in range(1,5):
                    for atoms in itertools.product('AB',repeat=length):
                        expected=oracle(atoms,words)
                        actual=solve(atoms,words,seconds=2,max_nodes=50000)
                        reverse=replay((atoms,words))
                        assert actual['status'] in ('SAT','UNSAT_FINITE')
                        assert reverse['status'] in ('SAT_REPLAY','UNSAT_REPLAY')
                        assert (actual['status']=='SAT')==(expected is not None),(atoms,words,actual,expected)
                        assert (reverse['status']=='SAT_REPLAY')==(expected is not None)
                        if expected is not None:assert ground(atoms,words,actual['code'])
                        counts[actual['status']]+=1
    source=json.loads((E.parent/'gdt986_anastasia_complete_condition_trees/src/SOURCE.json').read_text())
    code={a:chr(97+i//26)+chr(97+i%26) for i,a in enumerate(sorted(source['arities']))}
    full=[]
    for order,stream in source['streams'].items():
        atoms=stream['atoms'];parts=[code[a] for a in atoms]
        words=[''.join(parts[i:i+2]) for i in range(0,len(parts),2)]
        actual=solve(atoms,words)
        assert actual['status']=='SAT',(order,actual)
        assert ground(atoms,words,actual['code'])
        reverse=replay((atoms,words))
        assert reverse['status']=='SAT_REPLAY' and ground(atoms,words,reverse['code'])
        full.append(dict(writer=order,status=actual['status'],nodes=actual['nodes'],code=actual['code'],words=words))
        alternate=solve(atoms,words,seconds=1,max_nodes=50000,forbidden=('BATH',actual['code']['BATH']))
        if alternate['status']=='SAT':assert ground(atoms,words,alternate['code']) and alternate['code']['BATH']!=actual['code']['BATH']
        collision=solve(atoms,['a'*len(atoms)])
        assert collision['status']=='UNSAT_FINITE'
    result=dict(status='PASS',scope='Algorithm controls only; no manuscript fit or meaning test',small_complete_oracle_cases=sum(counts.values()),small_statuses=counts,full_unpinned_positive_codes=full)
    (E/'artifacts/PRE_RUN_FIXTURES.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='full_unpinned_positive_codes'},indent=2))


if __name__=='__main__':main()
