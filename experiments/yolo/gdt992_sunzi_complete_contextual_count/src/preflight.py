#!/usr/bin/env python3
"""Complete source/typed traversal and reused solver controls; no target data."""
import collections,importlib.util,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]

def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
f=module('fixed987finite',E.parent/'gdt987_anastasia_finite_word_proof/src/finite.py')
v=module('fixed987reverse',E.parent/'gdt987_anastasia_finite_word_proof/src/validate.py')
s=json.loads((E/'src/SOURCE.json').read_text())
expect=[[ ],[],[3,2],[5,3],[7,2],[],[23],[],[3,2,140],[5,3,63],[7,2,30],[233],[210],[],[3,1,70],[5,1,21],[7,1,15],[106,105]]
def numeric(t):return isinstance(t,str) and t.startswith('DIGIT_') or isinstance(t,list) and t[0]=='DECIMAL_APPEND'
def value(t):return int(t[6:]) if isinstance(t,str) else 10*value(t[1])+value(t[2])
def numbers(t):
    if numeric(t):return [value(t)]
    return [] if isinstance(t,str) else [n for x in t[1:] for n in numbers(x)]
for clause,expected in zip(s['clauses'],expect):assert numbers(clause['tree'])==expected,clause['id']
assert len(s['clauses'])==18
checks=[]
for order,stream in s['streams'].items():
    atoms=[a for c in s['clauses'] for a in v.serial(c['tree'],order)]
    assert atoms==stream['atoms'] and len(atoms)==122 and len(set(atoms))==27
    assert dict(collections.Counter(atoms))==stream['frequencies']
    code={a:f'{i:02x}' for i,a in enumerate(sorted(set(atoms)))}
    single=[code[a] for a in atoms]
    packed=[''.join(single[i:i+3]) for i in range(0,len(single),3)]
    for style,words in [('one_atom_per_word',single),('packed',packed)]:
        p=f.solve(atoms,words,seconds=5,max_nodes=500000);q=v.replay((atoms,words))
        assert p['status']=='SAT' and q['status']=='SAT_REPLAY',(order,style,p['status'],q['status'])
        v.ground(atoms,words,p['code']);v.ground(atoms,words,q['code'])
        checks.append(dict(writer=order,control=style,primary=p['status'],reverse=q['status']))
    bad=single.copy();pos=[i for i,a in enumerate(atoms) if a=='REF'][1];bad[pos]=code['OBJECTS']
    p=f.solve(atoms,bad,seconds=5,max_nodes=500000);q=v.replay((atoms,bad))
    assert p['status']=='UNSAT_FINITE' and q['status']=='UNSAT_REPLAY'
    checks.append(dict(writer=order,control='changed_second_reference',primary=p['status'],reverse=q['status']))
assert [23%m for m in (3,5,7)]==[2,3,2]
assert 140+63+30==233 and 233-210==23
assert 70+21+15==106 and 106-105==1
assert [128%m for m in (3,5,7)]==[2,3,2] and 233-105==128
assert [w%m for w,m in zip((70,21,15),(3,5,7))]==[1,1,1]
assert [[w%m for m in (3,5,7)] for w in (70,21,15)]==[[1,0,0],[0,1,0],[0,0,1]]
result=dict(status='PASS',source_units=18,source_numeric_clauses_checked=18,atoms=122,types=27,
    source_arithmetic='specific and stated general-step consequences agree; not a supplied complete general algorithm',
    controls=checks,scope='source/engineering only, no target/meaning finding',
    inherited_small_control='GDT987 5100 exhaustive oracle cases; implementation unchanged, not rerun here')
(E/'artifacts/PRE_RUN_FIXTURES.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
