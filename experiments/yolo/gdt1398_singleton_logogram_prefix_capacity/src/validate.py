#!/usr/bin/env python3
"""Independent mixed-logogram prefix closure validator; no primary imports."""
import argparse
from collections import Counter,defaultdict
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import re
import time

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')


def parse(raw,signs):
    paths=[[] for _ in range(len(raw)+1)];paths[0]=[()]
    for i in range(len(raw)):
        for sign in signs:
            if paths[i] and raw.startswith(sign,i):
                j=i+len(sign);paths[j]=(paths[j]+[p+(sign,) for p in paths[i]])[:2]
    assert len(paths[-1])==1 and paths[-1][0]
    return paths[-1][0]


def seeds(words):
    result={tuple(w) for w in words if len(w)>=2}
    for w in words:
        if len(w)==2:
            result.update((unit,) for unit in w)
    return result


def closure(initial,seconds=120):
    stop=time.monotonic()+seconds;known=set(initial)
    # Complete repeated scans, rather than the primary's dependency-driven worklist.
    while True:
        new=set()
        for word in tuple(known):
            if time.monotonic()>stop:raise TimeoutError('Independent closure budget exhausted')
            for cut in range(1,len(word)):
                if word[:cut] in known:new.add(word[cut:])
        new-=known
        if not new:return known
        known.update(new)


def decode(word,codes):
    pending=[0];seen={0}
    while pending:
        pos=pending.pop()
        if pos==len(word):return True
        for code in codes:
            end=pos+len(code)
            if tuple(word[pos:end])==tuple(code) and end not in seen:
                seen.add(end);pending.append(end)
    return False


def controls():
    # Ordinary literal mixed writer: singleton logogram z supplies no letter seed.
    literal=[tuple(x) for x in ('z','ab','bb')]
    first=seeds(literal);assert ('z',) not in first
    closed=closure(first);assert {w[0] for w in closed if len(w)==1}=={'a','b'}
    # Compound prefix table remains feasible when long outputs contain >=2 codes.
    table=[tuple(c) for c in ('a','bc')]
    words=[tuple(w) for w in ('x','y','abc','bca','aa')]
    closed=closure(seeds(words));assert ('bc',) not in closed
    assert ('b',) not in closed and ('c',) not in closed
    assert all(decode(word,table) for word in closed)
    assert ('b','c') in closed
    # A source singleton B must use its logogram y, never sole compound code bc.
    T={'A':'x','B':'y'};C={'A':'a','B':'bc'}
    assert T['B']!='bc' and C['B']=='bc'
    invalid=closure(seeds([tuple('bc')]))
    assert ('b',) in invalid and ('c',) in invalid
    assert not all(decode(word,table) for word in invalid)
    # A three-entry compound table saturates the direct H+branches-1 bound.
    table=[tuple(c) for c in ('ab','ac','d')]
    words=[tuple(w) for w in ('abd','acd','dab','dac','dd')]
    closed=closure(seeds(words));heads={w[0] for w in closed}
    followers={w[1] for w in closed if len(w)>=2 and w[0]=='a'}
    assert len(heads|{'a'})+max(1,len(followers))-1==3==len(table)
    assert all(decode(w,table) for w in closed)
    checked=0
    codewords=[tuple('a'),tuple('bc')]
    strings={sum((codewords[i] for i in indices),()) for n in range(1,5) for indices in itertools.product(range(2),repeat=n)}
    for u in strings:
        for v in strings:
            if len(u)<len(v) and v[:len(u)]==u:
                assert decode(v[len(u):],codewords);checked+=1
    assert not decode(tuple('b'),[tuple('a'),tuple('ab')])
    assert parse('ckhey',['ckh','e','y'])==('ckh','e','y')
    return {'status':'PASS_SOURCE_FREE_CONTROLS','literal_mixed_writer':True,
            'compound_mixed_writer':True,'one_compound_cannot_encode_nonlogogram_single_letter':True,
            'prefix_cancellations_checked':checked,'direct_branch_bound_fixture':True,'native_access':False}


def panel_rows(rows,panel):
    leaves=defaultdict(set)
    for row in rows:
        match=re.fullmatch(r'f(\d+)[rv].*',row['page']);assert match
        leaves[tuple(row['units'])].add(int(match.group(1)))
    return list(rows) if panel=='FULL' else [row for row in rows if len(leaves[tuple(row['units'])])>=2]


def summaries(words,multiplicities,closed,cap):
    used={u for word in words if len(word)>=2 for u in word}
    heads={word[0] for word in closed}
    forced={word[0] for word in closed if len(word)==1}
    branches={h:{w[1] for w in closed if len(w)>=2 and w[0]==h} for h in used}
    values={h:{'followers':sorted(branches[h]),'forced_singleton':h in forced,
               'necessary_bound':None if h in forced else len(heads|{h})+max(1,len(branches[h]))-1} for h in sorted(used)}
    possible=[v['necessary_bound'] for v in values.values() if v['necessary_bound'] is not None]
    minimum=min(possible) if possible else None
    status='ALL_USED_CODES_SINGLETON' if not possible else 'EXCLUDED_AT_CAP22' if minimum>cap else 'UNRESOLVED_AT_CAP22'
    fully=[word for word in words if len(word)>=2 and set(word)<=forced]
    return {'heads':values,'H':sorted(heads),'F':sorted(forced),'minimum_head_bound':minimum,
            'nontrivial_status':status,'fully_forced_long_groups':sum(multiplicities[w] for w in fully),
            'fully_forced_long_types':len(fully)}


def check_case(reader,panel,rows,case,certificate,spec):
    chosen=panel_rows(rows,panel)
    by_word=defaultdict(list)
    for row in chosen:by_word[tuple(row['units'])].append(row)
    words=set(by_word);counts={word:len(group) for word,group in by_word.items()}
    seedset=seeds(words)
    wholeseeds={word:min(g['id'] for g in by_word[word]) for word in words if len(word)>=2}
    singletonseeds={}
    for word in sorted(words):
        if len(word)==2:
            witness=min(g['id'] for g in by_word[word])
            for unit in word:singletonseeds.setdefault((unit,),{'witness':witness,'whole_word':list(word)})
    expectedseeds={word:{'word':list(word),'seed':'whole_long','witness':witness} for word,witness in wholeseeds.items()}
    for word,data in singletonseeds.items():expectedseeds.setdefault(word,{'word':list(word),'seed':'two_unit_obligation',**data})
    orderedseeds=[expectedseeds[word] for word in sorted(seedset,key=lambda w:(len(w),w))]
    nodes=certificate['nodes'];assert nodes[:len(orderedseeds)]==orderedseeds
    observed=set()
    for index,node in enumerate(nodes):
        word=tuple(node['word']);assert word and word not in observed
        if index>=len(orderedseeds):
            assert set(node)=={'word','parents'}
            uindex,vindex=node['parents'];assert 0<=uindex<index and 0<=vindex<index
            u,v=tuple(nodes[uindex]['word']),tuple(nodes[vindex]['word'])
            assert len(u)<len(v) and v[:len(u)]==u and v[len(u):]==word
        observed.add(word)
    assert case['reader']==reader and case['panel']==panel
    assert case['groups']==len(chosen) and case['types']==len(words)
    assert case['singleton_groups_ignored']==sum(len(g) for w,g in by_word.items() if len(w)==1)
    assert case['two_unit_types']==sum(len(word)==2 for word in words)
    assert case['two_unit_forced']==sorted({unit for word in words if len(word)==2 for unit in word})
    assert case['closure_status']==certificate['status']
    assert case['closure_size']==len(nodes)
    assert certificate['status'] in ('COMPLETE','UNKNOWN_TIMEOUT')
    if certificate['status']=='UNKNOWN_TIMEOUT':
        return {'status':'ORIGINAL_UNKNOWN_TIMEOUT_RETAINED','validated_derivations':len(nodes),'complete_closure_checked':False}
    independent=closure(seedset,spec['seconds_per_case'])
    assert independent==observed
    expected=summaries(words,counts,independent,spec['letter_cap'])
    assert case['summary']==expected
    return {'status':'PASS_COMPLETE_CLOSURE','groups':len(chosen),'types':len(words),
            'seed_nodes':len(seedset),'closure_nodes':len(independent),
            'nontrivial_status':expected['nontrivial_status'],'H':expected['H'],'F':expected['F'],
            'minimum_head_bound':expected['minimum_head_bound'],'complete_closure_checked':True}


def validate():
    lockpath=E/'LOCK.json';lock=read(lockpath)
    if isinstance(lock.get('files'),dict):pins=lock['files']
    else:pins={item['path']:item['sha256'] for item in lock['files']}
    spec=read(E/'src/SPEC.json')
    required=[E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'METHOD.md',ROOT/spec['source']]
    for path in required:
        key=str(path.relative_to(ROOT));assert pins[key]==sha(path),key
    assert spec['experiment']=='GDT1398' and spec['readers']==['IT2a','RF1b','ZL3b']
    assert spec['panels']==['FULL','GE2'] and spec['letter_cap']==22 and spec['seconds_per_case']==120
    cache=read(ROOT/spec['source']);result=read(A/'RESULT.json');evidence={};certificate_hashes={}
    assert set(result['cases'])=={reader+'_'+panel for reader in spec['readers'] for panel in spec['panels']}
    for reader in spec['readers']:
        rows=cache[reader]
        assert len({row['id'] for row in rows})==len(rows)
        for row in rows:
            assert row['edition']==reader and row['kind']=='P'
            assert not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v')
            assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
            assert parse(row['ivtff_group_raw'],spec['signs'])==tuple(row['units'])
        for panel in spec['panels']:
            key=reader+'_'+panel;path=A/('CERTIFICATE_'+key+'.json.gz')
            evidence[key]=check_case(reader,panel,rows,result['cases'][key],read(path),spec)
            certificate_hashes[path.name]=sha(path)
    assert result['experiment']=='GDT1398'
    complete=all(entry['complete_closure_checked'] for entry in evidence.values())
    full_excluded=complete and all(evidence[reader+'_FULL']['nontrivial_status'] in ('ALL_USED_CODES_SINGLETON','EXCLUDED_AT_CAP22') for reader in spec['readers'])
    expected_status='UNKNOWN_INCOMPLETE' if not complete else 'NONTRIVIAL_PREFIX_CAP22_EXCLUDED_ALL_READERS' if full_excluded else 'SOME_UNRESOLVED'
    assert result['status']==expected_status
    receipt={'experiment':'GDT1398','status':'PASS_INDEPENDENT_COMPLETE_VALIDATION' if complete else 'PARTIAL_VALIDATION_ORIGINAL_TIMEOUT_RETAINED',
             'scientific_status':expected_status,'cases':evidence,'source_free_controls':controls(),
             'implementation':'Independent repeated proper-prefix closure scans and raw-unit parsing; full seed/proof-chain/closure-set verification; no primary import or runner reading.',
             'pins':{'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(lockpath),'result_sha256':sha(A/'RESULT.json'),
                     'source_sha256':sha(ROOT/spec['source']),'certificates':certificate_hashes},
             'limits':['Mixed singleton-logogram/prefix-letter necessary capacity only; no decoded values or meanings.',
                       'GE2 means >=2physical leaves perwholeform, not two tokens or independent confirmation.',
                       'No observed singleton group enters the letter seeds; native length2words imply two singleton letter codes.',
                       'Unused codes outside observed longer-word support are not identified by this test.']}
    assert not (A/'VALIDATION.json').exists()
    save(A/'VALIDATION.json',receipt)
    print(json.dumps({'status':receipt['status'],'cases':evidence},sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');a=p.parse_args()
    if a.controls:print(json.dumps(controls(),sort_keys=True))
    else:validate()
