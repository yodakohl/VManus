from common import *
import grammar,independent
s=read(E/'src/SPEC.json');g=read(R/s['grammar']);old=read(R/s['old_cases']);draft=read(R/s['source_draft']);lex={x['raw']:x['symbol'] for x in draft['lexicon']}
# Only previously executed pinned source assignment, never the free search.
raw=[w for r in draft['owned_target']['records'] for w in r['raw'].split()]
rows=[]
for family in s['families']:
    b=grammar.build(raw,g,family,pinned=lex,timeout=5000);assert str(b['solver'].check())=='sat';w=grammar.extract(b);grammar.ground(w,raw,g,family)
    v=independent.build(raw,g,family,pinned=lex,timeout=5000);assert str(v['solver'].check())=='sat'
    a=evaluate(w['parse'],g,s);z=evaluate(w['parse'],g,s,independent=True);assert a==z and a['coherent_variants']==[0,2,4,6]
    for i,r in enumerate(a['replays']):assert (r['status']=='COHERENT')==(old[i]['status']=='CONDITIONAL_CONSISTENT')
    grammar.block_exact(b,w);independent.block_exact(v,w);assert str(b['solver'].check())==str(v['solver'].check())=='unsat'
    bad=dict(lex);bad[raw[0]]='HOME'
    x=grammar.build(raw,g,family,pinned=bad,timeout=5000);y=independent.build(raw,g,family,pinned=bad,timeout=5000)
    assert str(x['solver'].check())==str(y['solver'].check())=='unsat'
    # Projection blocking of this pinned old assignment must also remove it.
    x=grammar.build(raw,g,family,pinned=lex,timeout=5000);y=independent.build(raw,g,family,pinned=lex,timeout=5000)
    grammar.block_projection(x,{'qokedy':lex['qokedy']});independent.block_projection(y,{'qokedy':lex['qokedy']})
    assert str(x['solver'].check())==str(y['solver'].check())=='unsat'
    # A blocked role/variant tuple must leave other variants syntactically open.
    x=grammar.build(raw,g,family,pinned=lex,timeout=5000);y=independent.build(raw,g,family,pinned=lex,timeout=5000)
    grammar.block_projection(x,{'qokedy':lex['qokedy']},0);independent.block_projection(y,{'qokedy':lex['qokedy']},0)
    assert str(x['solver'].check())==str(y['solver'].check())=='sat'
    assert grammar.extract(x)['solver_variant']!=0
    rows.append(dict(family=family,pinned_legacy_assignment='PASS',old32world_outcomes='REPRODUCED',wrong_initial_value='REJECTED',exact_and_projection_blocking='PASS'))
# New whole-clause orders and reference arguments stress the existing replayers.
base=old[0]['parse'];body=base[1:-1];variants=[]
for shift in range(len(body)):
    variants.append([base[0],*body[shift:],*body[:shift],base[-1]])
import copy
for left in ('W','G','C','FIRST_CARGO','OTHER_CARGO'):
    for right in ('W','G','C','FIRST_CARGO','OTHER_CARGO'):
        changed=copy.deepcopy(base);p=next(p for p in changed if p['kind']=='PAIR');p['symbols'][0]=left;p['symbols'][3]=right;variants.append(changed)
for parsed in variants:
    parsed=copy.deepcopy(parsed);cursor=0
    for p in parsed:p['start']=cursor;cursor+=len(p['symbols']);p['end']=cursor
    a=evaluate(parsed,g,s);b=evaluate(parsed,g,s,independent=True);assert a==b
out=dict(status='PASS',fixtures=rows,source_semantic_stress_programs=len(variants),source_semantic_stress_variants=32*len(variants),unfixed_search_run=False,scope='Previously known pinned example only; no blind recovery or free-dictionary target result.');put('PREFLIGHT.json',out);print(out)
