#!/usr/bin/env python3
import json,itertools
from pathlib import Path
from matcher import solve,encode,dictionary_unique,join
from validate import replay
E=Path(__file__).resolve().parents[1]
s=json.loads((E/'src/SOURCE.json').read_text());lim=s['limits']
keys=sorted({k for r in s['traces'].values() for c in r for k in c})
code={k:chr(97+i) for i,k in enumerate(keys)}
checks=[]
for writer in s['writers']:
    fits={}
    for name,record in s['traces'].items():
        words=encode(record,code,writer); got=solve(record,words,writer,lim)
        assert got['status']=='LOCAL_FIT' and dict(sorted({k:code[k] for c in record for k in c}.items())) in got['codes']
        fits[name]=got['codes']
        bad=words.copy();bad[-1]+='z';assert solve(record,bad,writer,lim)['status']=='REPEAT_CONFLICT'
        checks.append(f'{writer}/{name}: complete planted code and changed conclusion')
    assert any(join(a,b,writer) for a in fits['FAPESMO'] for b in fits['FRISESOMORUM'])
# Changed repeated conversion opcode must be rejected in the Frisesomorum record.
for writer in s['writers']:
    record=s['traces']['FRISESOMORUM'];words=encode(record,code,writer)
    pos=5 if writer=='FUSED' else 13
    # FUSED positions3/5; SEPARATE positions9/13 are the two S instructions.
    assert words[pos]==code['OP:S']
    words[pos]+='z'
    assert solve(record,words,writer,lim)['status']=='REPEAT_CONFLICT'
checks.append('changed repeated S opcode rejected in both writers')
# Explicit type overlap: Q and term use identical strings; fixed typed slots disambiguate.
overlap={'Q:A':'a','Q:E':'b','T:X':'a','T:Y':'b'}
tiny=[['Q:A','T:X','T:Y'],['Q:E','T:Y','T:X']]
assert overlap in solve(tiny,encode(tiny,overlap,'FUSED'),'FUSED',lim)['codes']
assert dictionary_unique(overlap)
# Exhaustive oracle: words of length3/4 imply each of three nonempty pieces has length<=2.
vals=['a','b','aa','ab','ba','bb']; names=['Q:A','Q:E','T:X','T:Y'];oracle={}
for combo in itertools.product(vals,repeat=4):
    c=dict(zip(names,combo))
    if c['Q:A']==c['Q:E'] or c['T:X']==c['T:Y'] or not dictionary_unique(c):continue
    words=tuple(encode(tiny,c,'FUSED'))
    if all(len(w) in (3,4) for w in words):oracle.setdefault(words,set()).add(tuple(sorted(c.items())))
words=[''.join(p) for n in (3,4) for p in itertools.product('ab',repeat=n)]
for pair in itertools.product(words,repeat=2):
    got=solve(tiny,list(pair),'FUSED',lim)
    assert got['status']!='UNKNOWN_COMPUTATION'
    assert {tuple(c.items()) for c in got['codes']}==oracle.get(pair,set()),pair
    independently,nodes=replay(tiny,list(pair),'FUSED')
    assert independently==oracle.get(pair,set()),pair
out={'status':'PASS','planted_checks':checks,'typed_overlap':True,'brute_force_cases':len(words)**2,'same_author_engineering_only':True}
(E/'artifacts/PRE_RUN_FIXTURES.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
