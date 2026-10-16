#!/usr/bin/env python3
"""Independent finite lexical-key checking and Z3 UNSAT confirmation."""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import time
import z3

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n')


def collapse(units):return [u for i,u in enumerate(units) if i==0 or u not in ('e','i') or u!=units[i-1]]


def parse(raw,signs):
    paths=[[] for _ in range(len(raw)+1)];paths[0]=[()]
    for i in range(len(raw)):
        for unit in signs:
            if paths[i] and raw.startswith(unit,i):
                j=i+len(unit);paths[j]=(paths[j]+[p+(unit,) for p in paths[i]])[:2]
    return list(paths[-1][0]) if len(paths[-1])==1 and paths[-1][0] else None


def source_words(spec,only_deot=False):
    deot=read(ROOT/spec['deot_path'])
    result={'deot':[word for section in deot['source_sections'] for word in section['words']]}
    if only_deot:return result
    recipes=read(ROOT/spec['recipe_path']);other=read(ROOT/spec['other_path'])
    for name in ('b4','w1','bs1','gr1'):result[name]=[word for record in recipes[name] for word in record['words']]
    for name in ('OLD_ITALIAN_UD_CONTROL','LATIN_PROIEL_CONTROL','ANCIENT_GREEK_PROIEL_CONTROL'):
        result[name]=[entry['unit'] for entry in other[name]['PRIMARY']['units']]
        assert len(result[name])==8000
    assert set(result)==set(spec['source_names'])
    assert all(isinstance(word,str) and word for words in result.values() for word in words)
    return result


def solve_independent(groups,words,signs,mode,seconds=30):
    deadline=time.monotonic()+seconds
    alphabet=sorted(set(''.join(words)));W=set(words)
    if len(alphabet)<len(signs):return {'status':'UNSAT','reason':'Insufficient source alphabet for full injective map'}
    solver=z3.Solver();variables={unit:z3.Int('source_character_'+str(i)) for i,unit in enumerate(signs)}
    solver.add(z3.Distinct(list(variables.values())))
    for var in variables.values():solver.add(z3.Or([var==ord(c) for c in alphabet]))
    bylength={}
    for word in sorted(W):
        bylength.setdefault(len(word),set()).add(word)
        if mode=='BIDIR':bylength[len(word)].add(word[::-1])
    assert mode in ('FWD','BIDIR')
    clauses=0
    tracked={}
    for group_index,group in enumerate(sorted(set(map(tuple,groups)))):
        options=[]
        for output in sorted(bylength.get(len(group),set())):
            if time.monotonic()>=deadline:return {'status':'UNKNOWN','reason':'Independent model-build budget reached'}
            # Pairwise equality check, independent of the primary canonical-pattern tables.
            if any((group[i]==group[j])!=(output[i]==output[j]) for i in range(len(group)) for j in range(i)):continue
            options.append(z3.And([variables[unit]==ord(character) for unit,character in zip(group,output)]))
        label='word_constraint_'+str(group_index)
        solver.assert_and_track(z3.Or(options),z3.Bool(label))
        tracked[label]={'units':list(group),'positions_zero_based':[i for i,original in enumerate(groups) if tuple(original)==group]}
        clauses+=len(options)
    remaining=int(1000*(deadline-time.monotonic()))
    if remaining<=0:return {'status':'UNKNOWN','reason':'Independent model-build budget reached'}
    solver.set(timeout=remaining)
    answer=solver.check();result={'status':str(answer).upper(),'candidate_clauses':clauses,'backend':'z3 '+z3.get_version_string()}
    if answer==z3.unknown:result['reason']=solver.reason_unknown()
    elif answer==z3.unsat:
        result['nonminimal_word_core']=[tracked[name] for name in sorted((str(label) for label in solver.unsat_core()),key=lambda name:int(name.rsplit('_',1)[1]))]
        result['core_permanent_constraints']='Full source-alphabet domains and all22-unit injection remain permanent.'
    elif answer==z3.sat:
        model=solver.model();key={u:chr(model.eval(v,model_completion=True).as_long()) for u,v in variables.items()}
        assert len(set(key.values()))==len(signs)
        assert all(''.join(key[u] for u in group) in W or (mode=='BIDIR' and ''.join(key[u] for u in group)[::-1] in W) for group in groups)
        result['counterexample_key']=key
    return result


def brute(groups,words,signs,mode):
    chars=sorted(set(''.join(words)));W=set(words)
    for chosen in itertools.permutations(chars,len(signs)):
        key=dict(zip(signs,chosen))
        if all(''.join(key[u] for u in group) in W or mode=='BIDIR' and ''.join(key[u] for u in group)[::-1] in W for group in groups):return True
    return False


def controls():
    checked=0
    fixtures=[([['a','b'],['b','a']],['xy','yx'],['a','b']),
              ([['a','b'],['b','c'],['a','c']],['xy','xz','xw'],['a','b','c']),
              ([['a','a'],['b']],['xx','y'],['a','b']),
              ([['a','b']],['xx'],['a','b']),
              ([['a'],['b']],['x'],['a','b']),
              ([['a','b'],['a','a']],['xy','yy'],['a','b']),
              ([['a','b']],['xy','xZ'],['a','b','c'])]
    for groups,words,signs in fixtures:
        for mode in ('FWD','BIDIR'):
            expected=brute(groups,words,signs,mode)
            got=solve_independent(groups,words,signs,mode,3)
            assert got['status']==('SAT' if expected else 'UNSAT');checked+=1
    assert collapse(['e','e','a','a','i','i'])==['e','a','a','i']
    assert parse('qocheey',['q','o','ch','e','y'])==['q','o','ch','e','e','y']
    return {'status':'PASS_SOURCE_FREE_CONTROLS','exhaustive_brute_vs_Z3_fixtures':checked,
            'joint_triangle_star_unsat':True,'full_key_extendability_checked':True,'native_access':False}


def check_lock(gate_only=False):
    lockpath=E/'LOCK.json';lock=read(lockpath)
    pins=lock['files'] if isinstance(lock['files'],dict) else {x['path']:x['sha256'] for x in lock['files']}
    spec=read(E/'src/SPEC.json')
    for path in (E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'METHOD.md'):
        key=str(path.relative_to(ROOT));assert pins[key]==sha(path),key
    for field in (('deot_path',) if gate_only else ('recipe_path','deot_path','other_path','worksheet_path')):
        assert pins[spec[field]]==sha(ROOT/spec[field])
    assert spec['experiment_id']=='GDT1404' and spec['modes']==['FWD','BIDIR']
    assert spec['nodes_cap']==100000 and spec['candidate_checks_cap']==2000000
    assert spec['seconds_per_case']==10 and spec['independent_seconds_per_case']==30
    assert len(spec['signs'])==len(set(spec['signs']))==22
    return spec,lockpath


def check_sat(result,groups,words,signs,mode):
    W=set(words);alphabet=set(''.join(words));key=result['key']
    assert set(key)==set(signs)
    assert all(isinstance(c,str) and len(c)==1 and c in alphabet for c in key.values())
    assert len(set(key.values()))==len(signs)
    used={u for group in groups for u in group}
    if 'active_key' in result:assert result['active_key']=={u:key[u] for u in used}
    if 'arbitrary_extension_units' in result:assert set(result['arbitrary_extension_units'])==set(signs)-used
    certificate=result['certificate'];assert len(certificate)==len(groups)
    for group,entry in zip(groups,certificate):
        assert entry['units']==group and entry['source_word'] in W
        assert entry['direction'] in (('FWD',) if mode=='FWD' else ('FWD','REV'))
        output=entry['source_word'] if entry['direction']=='FWD' else entry['source_word'][::-1]
        assert ''.join(key[u] for u in group)==output
    return {'status':'SAT_CERTIFICATE_VERIFIED','groups':len(groups),'full_key_size':len(key),
            'observed_key_units':len(used),'arbitrary_extension_units':len(signs)-len(used)}


def rebuild_gate(spec,words):
    chars=sorted(set(''.join(words)));assert len(chars)==22
    planted={unit:chars[(7*j+3)%22] for j,unit in enumerate(spec['signs'])}
    target={planted['e'],planted['i']};start=None
    for j in range(len(words)-76):
        window=words[j:j+77]
        if not target<=set(''.join(window)):continue
        if any(word[k]==word[k-1] and word[k] in target for word in window for k in range(1,len(word))):continue
        start=j;break
    assert start is not None,'No declared-domain source control; native testing must stop'
    window=words[start:start+77];inverse={char:unit for unit,char in planted.items()}
    plain=[[inverse[char] for char in word] for word in window]
    encoded=[[unit for index,unit in enumerate(group) for _ in range(1+(wordindex+index)%3 if unit in ('e','i') else 1)] for wordindex,group in enumerate(plain)]
    assert [collapse(group) for group in encoded]==plain
    for group in encoded:assert parse(''.join(group),spec['signs'])==group
    return {'window_start':start,'source_words':window,'planted_key':planted,
            'encoded_groups':encoded,'collapsed_groups':plain}


def gate():
    spec,lockpath=check_lock(gate_only=True);words=source_words(spec,only_deot=True)['deot']
    expected=rebuild_gate(spec,words);control=read(A/'CONTROL.json')
    assert control['status']=='GENERATED' and control['source']=='deot'
    for key,value in expected.items():assert control[key]==value,key
    assert control['result']['status']=='SAT','Primary gate did not pass; no native release'
    checked=check_sat(control['result'],expected['collapsed_groups'],words,spec['signs'],'BIDIR')
    receipt={'experiment_id':'GDT1404','status':'PASS','kind':'INDEPENDENT_GENERATED_CONTROL_CERTIFICATE_VALIDATION',
             'window_start':expected['window_start'],'source_words':77,'known_writer_exact':True,
             'recovered_key_need_not_equal_planted':True,'certificate':checked,
             'source_free_controls':controls(),'native_access':False,
             'pins':{'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(lockpath),
                     'control_sha256':sha(A/'CONTROL.json'),'deot_projection_sha256':sha(ROOT/spec['deot_path'])}}
    assert not (A/'GATE_VALIDATION.json').exists();save(A/'GATE_VALIDATION.json',receipt)
    print(json.dumps({'status':'PASS','gate_words':77,'native_access':False},sort_keys=True))


def native_groups(spec):
    worksheet=read(ROOT/spec['worksheet_path']);selected=[u for u in worksheet['units'] if u['unit_id']==spec['passage_unit']]
    assert len(selected)==1 and spec['passage_unit']=='f75v_IT2a'
    lines=selected[0]['lines'];groups=[]
    assert [line['metadata']['locus'] for line in lines]==['f75v.'+str(n) for n in range(43,50)]
    assert str(lines[0]['metadata']['paragraph_start'])=='1' and str(lines[-1]['metadata']['paragraph_end'])=='1'
    for line in lines:
        meta=line['metadata'];rows=line['original_groups']
        assert meta['page']=='f75v' and meta['edition']=='IT2a'
        assert len(rows)==int(meta['source_group_count']) and [int(row[1]) for row in rows]==list(range(1,len(rows)+1))
        for row in rows:
            assert len(row)==5
            units=parse(row[2],spec['signs']);assert units is not None,'Unparseable original group; cannot drop it'
            groups.append(collapse(units))
    assert len(groups)==spec['expected_passage_groups']==77
    return groups


def validate():
    spec,lockpath=check_lock();gate_receipt=read(A/'GATE_VALIDATION.json')
    assert gate_receipt['status']=='PASS' and gate_receipt['pins']['lock_sha256']==sha(lockpath)
    assert gate_receipt['pins']['control_sha256']==sha(A/'CONTROL.json')
    sources=source_words(spec);groups=native_groups(spec);result=read(A/'RESULT.json')
    assert result['groups']==groups
    cases=result['cases'];assert [(c['source'],c['mode']) for c in cases]==[(name,mode) for name in spec['source_names'] for mode in spec['modes']]
    checked=[]
    for case in cases:
        name,mode=case['source'],case['mode'];primary=case['result'];status=primary['status']
        assert status in ('SAT','UNSAT','UNKNOWN')
        if status=='SAT':entry=check_sat(primary,groups,sources[name],spec['signs'],mode)
        elif status=='UNKNOWN':entry={'status':'ORIGINAL_UNKNOWN_PRESERVED','independent_search':'NOT_RUN'}
        else:
            independent=solve_independent(groups,sources[name],spec['signs'],mode,spec['independent_seconds_per_case'])
            entry={'status':'UNSAT_INDEPENDENTLY_CONFIRMED' if independent['status']=='UNSAT' else 'UNSAT_DISAGREEMENT' if independent['status']=='SAT' else 'UNSAT_UNCONFIRMED',
                   'independent':independent}
        checked.append({'source':name,'mode':mode,'primary_status':status,**entry})
    disagreement=any(c['status']=='UNSAT_DISAGREEMENT' for c in checked)
    unconfirmed=any(c['status']=='UNSAT_UNCONFIRMED' for c in checked)
    receipt={'experiment_id':'GDT1404','status':'VALIDATION_DISAGREEMENT' if disagreement else 'VALIDATION_INCOMPLETE_UNSAT_UNCONFIRMED' if unconfirmed else 'PASS_INDEPENDENT_CERTIFICATE_AND_STATUS_ACCOUNTING',
             'cases':checked,'groups':77,'source_free_controls':controls(),
             'implementation':'Independent original-source extraction and parsing; untouched source-codepoint domains; full22Distinct Z3 variables with finite lexical clauses, not primary DFS.',
             'pins':{'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(lockpath),'result_sha256':sha(A/'RESULT.json'),
                     'gate_validation_sha256':sha(A/'GATE_VALIDATION.json')},
             'limits':['SAT is local lexical capacity, not source choice, grammar, meaning or translation.',
                       'Primary UNKNOWN remains UNKNOWN; independent validation does not launch an alternate recovery search for those cases.',
                       'The eight fixed full-manuscript source models remain excluded by1403.',
                       'BIDIR allows independent direction choices perword; it is a generous relaxation, not a historical writing claim.']}
    assert not (A/'VALIDATION.json').exists();save(A/'VALIDATION.json',receipt)
    print(json.dumps({'status':receipt['status'],'cases':[{k:c[k] for k in ('source','mode','primary_status','status')} for c in checked]},sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group();group.add_argument('--controls',action='store_true');group.add_argument('--gate',action='store_true');args=parser.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    elif args.gate:gate()
    else:validate()
