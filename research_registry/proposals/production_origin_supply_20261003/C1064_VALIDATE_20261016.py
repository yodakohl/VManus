#!/usr/bin/env python3
"""Independent symbolic state-difference accounting; no primary imports."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SIGNS=('a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh')
INPUT=HERE/'E1063_SCAFFOLD_20261016.json'
HITS=ROOT/'experiments/yolo/gdt857_cyclic_inventory_triple_bound/artifacts/HITS.json'
PLAN=HERE/'C1064_PLAN_20261016.json'
LOCK=HERE/'C1064_CODE_LOCK_20261016.json'
OUT=HERE/'C1064_DERIVATION_20261016.json'
VALIDATION=HERE/'C1064_VALIDATION_20261016.json'


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(raw):
    paths=[[] for _ in range(len(raw)+1)]
    paths[0]=[()]
    for at in range(len(raw)):
        for prefix in paths[at]:
            for unit in SIGNS:
                if raw.startswith(unit,at):
                    end=at+len(unit);value=prefix+(unit,)
                    if value not in paths[end] and len(paths[end])<2:paths[end].append(value)
    if not raw or len(paths[-1])!=1:return None
    return list(paths[-1][0])


def combine(*terms):
    values={}
    for multiplier,term in terms:
        for variable,n in term.items():values[variable]=values.get(variable,0)+multiplier*n
    return {k:n%27 for k,n in sorted(values.items()) if n%27}


def difference(current,previous,b):return combine((1,current),(-1,previous),(1,{b:1}))


def expression(coefficients):
    return '('+' + '.join(str(n)+'*'+v for v,n in sorted(coefficients.items()))+') mod 27'


def controls():
    checked=0
    for incoming,h,b in itertools.product(range(27),repeat=3):
        states=[h,h,h]
        outputs=[(states[i]-(states[i-1] if i else incoming)+b)%27 for i in range(3)]
        assert outputs[1:]==[b,b]
        assert (sum(outputs)-3*b)%27==(h-incoming)%27
        checked+=1
    base=[2,7,19,4]
    for incoming,b,change in itertools.product(range(27),repeat=3):
        altered=base[:];altered[1]=(altered[1]+change)%27
        before=[(x-(base[i-1] if i else incoming)+b)%27 for i,x in enumerate(base)]
        after=[(x-(altered[i-1] if i else incoming)+b)%27 for i,x in enumerate(altered)]
        assert [(a-z)%27 for a,z in zip(after,before)]==[0,change,(-change)%27,0]
        checked+=1
    a={'w0':3,'w1':1};u={'u':1};b='b'
    cs=[difference(a,{'IN':1},b),difference(u,a,b),difference(a,u,b)]
    assert combine(*[(1,c) for c in cs],(-3,{b:1}))==combine((1,a),(-1,{'IN':1}))
    assert cs[1]['u']==1 and cs[2]['u']==26
    # Physical line partition carries state rather than resetting it.
    assert difference({'h_after':1},{'h_before':1},'b')=={'b':1,'h_after':1,'h_before':26}
    assert difference({'h_after':1},{'h_before':1},'b')!=difference({'h_after':1},{},'b')
    assert parse('qokeedy')==['q','o','k','e','e','d','y']
    assert parse('qoke@152;y') is None
    return {'status':'PASS_SOURCE_FREE_ONLY','numeric_cases':checked,'opaque_state_reused':True,'initial_state_not_assumed_for_triple':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--controls',action='store_true');args=parser.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True));return
    lock=read(LOCK)
    pins={p['path']:p['sha256'] for p in lock['files']}
    assert len(pins)==len(lock['files'])
    for p,h in pins.items():assert sha(ROOT/p)==h,p
    for p in [PLAN,Path(__file__).resolve(),HERE/'C1064_BUILD_20261016.py',INPUT,HITS]:assert str(p.relative_to(ROOT)) in pins
    plan=read(PLAN)
    assert tuple(plan['signs'])==SIGNS and plan['modulus']==27
    assert plan['source']==str(INPUT.relative_to(ROOT)) and plan['triple_source']==str(HITS.relative_to(ROOT))
    for p in plan.get('inputs',[]):assert sha(ROOT/p['path'])==p['sha256']
    source=read(INPUT);out=read(OUT)
    assert out['status']=='RELAXED_CUMULATIVE_STATE_EQUATIONS_NO_KEY_OR_PLAINTEXT'
    assert out['modulus']==27 and tuple(out['signs'])==SIGNS
    assert out['pins']==[{'path':p,'sha256':h} for p,h in sorted(pins.items())]
    assert out['code_lock']=={'path':str(LOCK.relative_to(ROOT)),'sha256':sha(LOCK),'locked_utc':lock['locked_utc']}
    assert out['source_units']==source['source_units']
    originals=source['source_units'];assert len(originals)==6 and len(out['units'])==6
    seen=set();source_groups=unique_groups=opaque_groups=known_zero=0
    parameters={}
    telescopes=[]
    for wrapped,actual in zip(originals,out['units']):
        unit=wrapped['source_unit'];uid=wrapped['unit_id'];reader=unit['edition']
        weights=['w_'+reader+'_'+str(i) for i in range(22)];b='b_'+reader
        parameters[reader]={'weights':weights,'b':b}
        initial={'kind':'INCOMING','coefficients':{'IN:'+uid:1}} if reader=='RF1b' else {'kind':'RESET','coefficients':{}}
        assert actual['unit_id']==uid and actual['reader']==reader
        assert actual['boundary_status']==unit['boundary_status']
        assert actual['initial_state']==initial
        original_rows=[]
        for line in unit['lines']:
            assert line['metadata']['page'] in ('f75r','f75v')
            for rawrow in line['groups']:
                original_rows.append((line['metadata']['locus'],dict(zip(unit['group_columns'],rawrow))))
        assert len(actual['rows'])==len(original_rows)
        previous=initial;sum_coeff={};zeros=[];opaque_vars=[]
        for index,((locus,g),r) in enumerate(zip(original_rows,actual['rows']),1):
            sid=g['source_group_id'];raw=g['ivtff_group_raw']
            assert sid not in seen;seen.add(sid)
            assert r['source_group_id']==sid and r['locus']==locus and r['raw']==raw and r['source_group']==g
            assert r['index_in_message']==index
            units=parse(raw)
            if units is None:
                vector=None;variable='u_'+uid+'_'+str(index)
                state={'kind':'OPAQUE','coefficients':{variable:1}}
                status='OPAQUE';opaque_groups+=1;opaque_vars.append((index-1,variable))
            else:
                vector=[units.count(s) for s in SIGNS]
                state={'kind':'SUM','coefficients':{w:n for w,n in zip(weights,vector) if n}}
                status='UNIQUE';unique_groups+=1
            assert r['parse_status']==status and r['units']==units and r['count_vector']==vector
            assert r['current_state']==state and r['previous_state']==previous
            coefficients=difference(state['coefficients'],previous['coefficients'],b)
            assert r['source_coefficients_mod27']==coefficients
            assert r['source_expression']==expression(coefficients)
            zero=(previous['kind']=='SUM' and state['kind']=='SUM' and previous['coefficients']==state['coefficients'])
            assert r['zero_difference_known_same_counts']==zero
            if zero:zeros.append(sid)
            sum_coeff=combine((1,sum_coeff),(1,coefficients))
            previous=state;source_groups+=1
        assert actual['zero_difference_source_ids']==zeros
        known_zero+=len(zeros)
        total=combine((1,sum_coeff),(-len(original_rows),{b:1}))
        expected=combine((1,previous['coefficients']),(-1,initial['coefficients']))
        assert total==expected
        for index,variable in opaque_vars:
            appearances=[(i,r['source_coefficients_mod27'].get(variable,0)) for i,r in enumerate(actual['rows']) if variable in r['source_coefficients_mod27']]
            expected_appearances=[(index,1)]+([(index+1,26)] if index+1<len(original_rows) else [])
            assert appearances==expected_appearances
        telescopes.append({'unit_id':uid,'groups':len(original_rows),'remaining_state_coefficients_mod27':total,'initial_kind':initial['kind']})
    assert out['reader_parameters']==parameters
    hitlist=read(HITS)
    triple=out['triple_obligation']
    assert triple['source_path']==str(HITS.relative_to(ROOT)) and triple['source_sha256']==sha(HITS)
    assert triple['witnesses']==hitlist and triple['no_new_census'] is True
    for h in hitlist:
        assert not h['page'].startswith('f84') and h['page']!='f116v'
        groups=h['groups'];assert len(groups)==3
        assert all(g['ivtff_group_raw']==h['raw'] for g in groups)
        assert parse(h['raw']) is not None
        for left,right in zip(groups,groups[1:]):
            assert int(right['source_group_index'])==int(left['source_group_index'])+1
            assert left['right_separator']==right['left_separator']=='DEFINITE_SPACE'
        vector=[parse(h['raw']).count(s) for s in SIGNS]
        state={str(i):n for i,n in enumerate(vector) if n}
        assert difference(state,state,'b')=={'b':1}
    accounting={'source_units':6,'source_groups':source_groups,'unique_groups':unique_groups,'opaque_groups':opaque_groups,'known_zero_differences':known_zero}
    assert out['accounting']==accounting
    assert source_groups==588
    result={'status':'PASS_SOURCE_AND_SYMBOLIC_ACCOUNTING_ONLY','code_lock_sha256':sha(LOCK),'plan_sha256':sha(PLAN),'derivation_sha256':sha(OUT),
            'implementation_lock_utc':lock['locked_utc'],'accounting':accounting,'telescoping':telescopes,'retained_triple_records_checked':len(hitlist),
            'method':'Independent complete-unit segmentation DP, sparse coefficient subtraction modulo27, explicit opaque-variable occurrence accounting and telescoping.',
            'limits':['No key, plaintext, source language, probabilistic channel or word meaning identified.','b=0 is incompatible only with the future no-adjacent-source-spaces contract at retained exact triples; no exclusion of b!=0 or arbitrary messages.','RF windows have free incoming state, not independently marked paragraph resets.']}
    VALIDATION.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
