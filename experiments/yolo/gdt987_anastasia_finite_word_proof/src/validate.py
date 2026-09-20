#!/usr/bin/env python3
"""Separate reverse finite replay; imports neither finite.py nor the runner."""
import collections
import concurrent.futures
import csv
import hashlib
import itertools
import json
from pathlib import Path
import time

E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
OLD=E.parent/'gdt986_anastasia_complete_condition_trees'


def read(p):return json.loads(p.read_text())


def serial(tree,order):
    if isinstance(tree,str):return [tree]
    middle=[a for child in tree[1:] for a in serial(child,order)]
    return [tree[0]]+middle if order=='PREFIX' else middle+[tree[0]]


def ground(atoms,words,code):
    assert set(code)==set(atoms) and all(isinstance(x,str) and x for x in code.values())
    for x,y in itertools.combinations(code.values(),2):
        assert not x.startswith(y) and not y.startswith(x)
    assert ''.join(code[a] for a in atoms)==''.join(words)
    ends=set();offset=0
    for a in atoms:offset+=len(code[a]);ends.add(offset)
    seam=0
    for word in words:seam+=len(word);assert seam in ends


def replay(job):
    atoms,words=job
    deadline=time.monotonic()+20
    text=''.join(words);N=len(text);frequencies=collections.Counter(atoms)
    word_start=[0]*(N+1);start=0
    for word in words:
        for end in range(start+1,start+len(word)+1):word_start[end]=start
        start+=len(word)
    pieces=set()
    for word in words:
        for length in range(1,len(word)+1):
            for begin in range(len(word)-length+1):pieces.add(word[begin:begin+length])
    domains={}
    for a,frequency in frequencies.items():
        maxlen=min(max(map(len,words)),(N-len(atoms)+frequency)//frequency)
        domains[a]=sorted(p for p in pieces if len(p)<=maxlen
                          and sum(w.count(p) for w in words)>=frequency
                          and sum(w.startswith(p) for w in words)<=frequency)
    if any(not d for d in domains.values()):return dict(status='UNSAT_REPLAY',nodes=0,reason='empty_necessary_domain')
    lo={a:min(map(len,d)) for a,d in domains.items()};hi={a:max(map(len,d)) for a,d in domains.items()}
    left=[{}]
    for a in atoms:
        next_counts=left[-1].copy();next_counts[a]=next_counts.get(a,0)+1;left.append(next_counts)
    mapping={};nodes=0;found=None
    class Deadline(Exception):pass
    def visit(i,end):
        nonlocal nodes,found
        nodes+=1
        if nodes>1000000 or (nodes%128==0 and time.monotonic()>=deadline):raise Deadline
        if i==0:
            if end==0:found=dict(mapping);return True
            return False
        if end==0:return False
        lower=sum(count*(len(mapping[a]) if a in mapping else lo[a]) for a,count in left[i].items())
        upper=sum(count*(len(mapping[a]) if a in mapping else hi[a]) for a,count in left[i].items())
        if not lower<=end<=upper:return False
        a=atoms[i-1]
        if a in mapping:
            value=mapping[a];begin=end-len(value)
            return begin>=word_start[end] and text[begin:end]==value and visit(i-1,begin)
        for value in domains[a]:
            begin=end-len(value)
            if begin<word_start[end] or text[begin:end]!=value:continue
            if any(value.startswith(other) or other.startswith(value) for other in mapping.values()):continue
            mapping[a]=value
            if visit(i-1,begin):return True
            del mapping[a]
        return False
    try:status='SAT_REPLAY' if visit(len(atoms),N) else 'UNSAT_REPLAY'
    except Deadline:status='UNKNOWN_REPLAY_LIMIT'
    result=dict(status=status,nodes=nodes)
    if found is not None:ground(atoms,words,found);result['code']=found
    return result


def main():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():
        assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    source=read(OLD/'src/SOURCE.json');streams={}
    for order in ('PREFIX','POSTFIX'):
        seq=['BEGIN_RECORD']+[a for c in source['clauses'] for a in serial(c['tree'],order)]
        assert seq==source['streams'][order]['atoms'] and len(seq)==111 and len(set(seq))==47
        streams[order]=seq
    previous=read(OLD/'artifacts/CASES.json');cases=read(A/'CASES.json')
    assert len(cases)==len(previous)==314
    pending=[];main_codes=alternate_codes=0
    for i,(c,old) in enumerate(zip(cases,previous)):
        for k in ('edition','paragraph','page','leaf','writer','target_groups','independent_confirmation_capacity'):
            assert c[k]==old[k]
        assert c['gdt986_status']==old['status']
        if old['status']=='UNKNOWN_SOURCE':
            assert c['status']=='UNKNOWN_SOURCE' and c['ineligible_lines']==old['ineligible_lines'];continue
        for k in ('words','loci','source_ids'):assert c[k]==old[k]
        assert c['status'] in ('SAT','UNSAT_FINITE','UNKNOWN_FINITE_LIMIT','UNKNOWN_WALL_LIMIT','ERROR_WORKER','ERROR_PROTOCOL')
        atoms=streams[c['writer']]
        if c['status']=='SAT':
            ground(atoms,c['words'],c['code']);main_codes+=1
            assert old['status'] not in ('UNSAT_SOLVER','CONTRADICTED_NONEMPTY_LENGTH','CONTRADICTED_WORD_BOUNDARIES','CONTRADICTED_PREFIX_LENGTH','CONTRADICTED_REPEATED_DOMAIN')
            expected={a for a,n in collections.Counter(atoms).items() if n>1}
            assert set(c['projections'])==expected
            for a,q in c['projections'].items():
                assert q['status'] in ('SAT','UNSAT_FINITE','UNKNOWN_FINITE_LIMIT')
                if q['status']=='SAT':
                    ground(atoms,c['words'],q['code']);assert q['code'][a]!=c['code'][a];alternate_codes+=1
                # Projection UNSAT is a primary finite result, not independently replayed here.
        if c['status']=='UNSAT_FINITE':pending.append((i,(atoms,c['words'])))
    replays=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=16) as pool:
        work={pool.submit(replay,j):i for i,j in pending}
        for done,f in enumerate(concurrent.futures.as_completed(work),1):
            index=work[f];result=f.result();assert result['status']!='SAT_REPLAY',(index,result)
            result.update(case_index=index,edition=cases[index]['edition'],paragraph=cases[index]['paragraph'],writer=cases[index]['writer'])
            replays.append(result)
            if done%16==0 or done==len(pending):print(json.dumps(dict(replayed=done,of=len(pending))),flush=True)
    replays.sort(key=lambda r:r['case_index'])
    (A/'INDEPENDENT_REPLAYS.json').write_text(json.dumps(replays,separators=(',',':'))+'\n')
    result=read(A/'RESULT.json')
    assert result['case_status_counts']==dict(collections.Counter(c['status'] for c in cases))
    assert result['original_unknown_statuses']==dict(collections.Counter(c['status'] for c in cases if c['gdt986_status']=='UNKNOWN_SOLVER'))
    for ed in ('ZL3b','IT2a','RF1b'):
        for order in streams:
            assert result['panels'][ed][order]==dict(collections.Counter(c['status'] for c in cases if c['edition']==ed and c['writer']==order))
    with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
    assert len(table)==314
    for t,c in zip(table,cases):
        for k in ('edition','paragraph','writer','gdt986_status','status'):assert t[k]==str(c[k])
        assert int(t['source_atoms'])==111 and int(t['source_types'])==47
        assert int(t['groups'])==c['target_groups'] and int(t['independent_confirmation_capacity'])==0
    counts=dict(collections.Counter(r['status'] for r in replays))
    output=dict(status='PASS',scope='Separate same-author input/case/ground-code checks and reverse finite replay; explicit unknown replays retained; no meaning validation',cases=314,
        full_codes_checked=main_codes,alternative_codes_checked=alternate_codes,exhaustion_replay_counts=counts,
        unverified_primary_exhaustions=counts.get('UNKNOWN_REPLAY_LIMIT',0),confirmed_words=0,independent_confirmation_capacity=0)
    (A/'VALIDATION.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))


if __name__=='__main__':main()
