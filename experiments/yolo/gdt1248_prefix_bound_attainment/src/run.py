#!/usr/bin/env python3
import gzip,hashlib,itertools,json
from collections import Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
SOURCE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
SIGNS=('a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh')
HEADS=('cfh','cph','q'); READERS=('IT2a','RF1b','ZL3b')

def parse(word,head):
    result=[]; i=0
    while i<len(word):
        size=2 if word[i]==head else 1
        if i+size>len(word): return None
        result.append(tuple(word[i:i+size])); i+=size
    return result

def controls():
    n=0
    for head in ('a','b'):
        codes=[(s,) for s in ('a','b') if s!=head]+[(head,s) for s in ('a','b')]
        def brute(w):
            if not w: return [()]
            return [(c,)+p for c in codes if w[:len(c)]==c for p in brute(w[len(c):])]
        for length in range(11):
            for w in itertools.product('ab',repeat=length):
                all_p=brute(w); got=parse(w,head)
                assert len(all_p)<=1
                assert (got is not None)==bool(all_p)
                if got is not None: assert tuple(got)==all_p[0]
                n+=1
    assert parse(('cfh','ch'),'cfh')==[('cfh','ch')]
    assert parse(('a','cfh'),'cfh') is None
    return n

def main():
    assert not (E/'artifacts/RESULT.json').exists()
    lock=json.loads((E/'artifacts/REGISTRATION_LOCK.json').read_text())
    for p,h in lock['files'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    data=json.loads(gzip.decompress((ROOT/SOURCE).read_bytes())); results=[]
    for reader in READERS:
        rows=data[reader]
        assert all(not r['page'].startswith('f84') and r['page']!='f116v' for r in rows)
        assert all(r['units'] and set(r['units'])<=set(SIGNS) for r in rows)
        for head in HEADS:
            failures=[]; failed_types=set(); usage=Counter(); active=0
            for r in rows:
                w=tuple(r['units']); pieces=parse(w,head)
                if pieces is None:
                    failures.append(r['id']);failed_types.add(w);continue
                assert tuple(itertools.chain.from_iterable(pieces))==w
                usage.update(pieces);active+=any(len(c)>1 for c in pieces)
            complete=not failures
            size=len(usage)
            decision=('EXACT_MINIMUM_27' if complete and size==27 and active else 'CONSTRUCTIVE_UPPER_BOUND' if complete and active else 'CONSTRUCTION_CONTRADICTED' if failures else 'TRIVIAL_ONLY')
            if complete and active: assert size>=27
            result=dict(reader=reader,head=head,groups=len(rows),types=len({tuple(r['units']) for r in rows}),offered_codes=43,accepted_groups=len(rows)-len(failures),active_groups=active,failed_groups=len(failures),failed_types=len(failed_types),failure_ids=failures,used_in_accepted_groups=size,complete_code_upper_bound=size if complete and active else None,code_usage=[dict(units=list(c),occurrences=n) for c,n in sorted(usage.items())],decision=decision)
            results.append(result)
            print(reader,head,decision,'failed',len(failures),'used',size,'active',active,flush=True)
    (E/'artifacts/RESULT.json').write_text(json.dumps(dict(experiment='GDT1248',cases=results),indent=2,sort_keys=True)+'\n')

if __name__=='__main__':
    import sys
    if '--controls' in sys.argv: print(json.dumps(dict(status='PASS',cases=controls())))
    else: main()
