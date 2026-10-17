#!/usr/bin/env python3
"""Independent core selection with frozen independent1414 solver reuse."""
import argparse,hashlib,importlib.util,itertools,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
    if p.exists():assert read(p)==x
    else:p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def keep(units):
    return bool(units) and units[-2:]!=['d','y'] and not any(x==y and x in ('e','i') for x,y in zip(units,units[1:]))
def controls():
    fixtures=[([],False),(None,False),(['e'],True),(['i'],True),(['e','e'],False),(['i','i'],False),(['d','y'],False),(['d','y','a'],True),(['e','i'],True),(['a','a'],True),(['a','d','y'],False),(['e','a','e'],True),(['e','e','a'],False)]
    for u,want in fixtures:assert keep(u)==want
    return {'status':'PASS','predicate_cases':len(fixtures),'new_solver_regression':False}
def setup():
    lock=read(E/'LOCK.json')
    for p,h in lock['files'].items():assert not Path(p).is_absolute() and sha(ROOT/p)==h,p
    s=read(E/'src/SPEC.json')
    for p in [Path(__file__),E/'src/run.py',E/'src/SPEC.json',ROOT/s['independent_library_path']]:assert p.relative_to(ROOT).as_posix() in lock['files']
    ms=importlib.util.spec_from_file_location('frozen_independent1414',ROOT/s['independent_library_path']);lib=importlib.util.module_from_spec(ms);ms.loader.exec_module(lib)
    return s,lock,lib

def parse(raw,signs):
    ways=[[] for _ in range(len(raw)+1)];ways[0]=[[]]
    for end in range(1,len(raw)+1):
        for sign in signs:
            begin=end-len(sign)
            if begin>=0 and raw[begin:end]==sign:
                ways[end]=(ways[end]+[prefix+[sign] for prefix in ways[begin]])[:2]
    return ways[-1][0] if len(ways[-1])==1 else None

def native_rows(s,lib):
    w=read(ROOT/s['worksheet_path']);selected=[u for u in w['units'] if u['unit_id']==s['passage_unit']];assert len(selected)==1
    lines=selected[0]['lines'];assert [l['metadata']['locus'] for l in lines]==['f75v.'+str(i) for i in range(43,50)]
    assert str(lines[0]['metadata']['paragraph_start'])=='1' and str(lines[-1]['metadata']['paragraph_end'])=='1'
    originals=[];parsed=[]
    for line in lines:
        rows=line['original_groups'];meta=line['metadata']
        assert meta['page']=='f75v' and meta['edition']=='IT2a' and len(rows)==int(meta['source_group_count'])
        assert [int(r[1]) for r in rows]==list(range(1,len(rows)+1))
        for r in rows:
            assert len(r)==5
            originals.append(r);parsed.append(parse(r[2],s['signs']));assert parsed[-1] is not None
    assert len(originals)==77==s['expected_passage_groups']
    return originals,parsed

def gate():
    s,lock,lib=setup();old=read(ROOT/s['old_control_path']);subset=read(A/'CONTROL_SUBSET.json')
    assert subset['experiment_id']=='GDT1417' and subset['source']=='deot'
    assert subset['old_control_sha256']==sha(ROOT/s['old_control_path'])
    encoded=old['encoded_groups'];indices=[i for i,g in enumerate(encoded) if keep(g)];groups=[encoded[i] for i in indices]
    assert subset['selected_indices']==indices and subset['groups']==groups
    assert subset['candidate_scope']=='ANYordinarykey control subset only'
    assert subset['predicate_controls']['status']=='PASS'
    for i in indices:assert ''.join(old['planted_key'][u] for u in encoded[i])==old['source_words'][i]
    sufficient=len(groups)>=2 and len(set(map(tuple,groups)))>=2
    primary=subset['result'];assert primary['status'] in ['SAT','UNSAT','UNKNOWN']
    passed=sufficient and primary['status']=='SAT'
    certificate=lib.direct(primary,groups,lib.sources(s,True)['deot'],s['signs'],'BIDIR') if passed else None
    receipt={'experiment_id':'GDT1417','status':'PASS' if passed else 'STOP','primary_status':primary['status'],'controls':controls(),'positions':indices,'sufficient_control':sufficient,'certificate':certificate,'native_access':False,'pins':{'lock_sha256':sha(E/'LOCK.json'),'control_subset_sha256':sha(A/'CONTROL_SUBSET.json'),'old_control_sha256':sha(ROOT/s['old_control_path']),'validator_sha256':sha(Path(__file__))},'scope':'Filtered old positive writer; any valid ordinary function suffices. STOP is not native model exclusion.'}
    save(A/'GATE_VALIDATION.json',receipt);print(json.dumps({'status':receipt['status']}))

def native():
    s,lock,lib=setup();gr=read(A/'GATE_VALIDATION.json')
    assert gr['status']=='PASS' and gr['pins']['lock_sha256']==sha(E/'LOCK.json')
    assert gr['pins']['control_subset_sha256']==sha(A/'CONTROL_SUBSET.json')
    originals,parsed=native_rows(s,lib)
    indices=[i for i,u in enumerate(parsed) if keep(u)];freed=[i for i in range(77) if i not in indices];groups=[parsed[i] for i in indices]
    result=read(A/'RESULT.json')
    assert result['experiment_id']=='GDT1417' and result['status']=='JOINT_UNCHANGED_CORE_CAPACITY'
    assert result['original_groups']==originals and result['original_units']==parsed
    assert result['positions_zero_based']==indices and result['freed_positions']==freed and result['groups']==groups
    assert result['claim_ceiling']==s['claim_ceiling']
    assert [(c['source'],c['mode']) for c in result['cases']]==list(itertools.product(s['source_names'],s['modes']))
    words=lib.sources(s);checked=[]
    for c in result['cases']:
        primary=c['result'];status=primary['status'];assert status in ['SAT','UNSAT','UNKNOWN']
        if status=='SAT':answer=lib.direct(primary,groups,words[c['source']],s['signs'],c['mode'])
        elif status=='UNKNOWN':answer={'status':'ORIGINAL_UNKNOWN_PRESERVED'}
        else:
            independent=lib.solve(groups,words[c['source']],s['signs'],c['mode'],s['independent_seconds_per_case'])
            answer={'status':{'UNSAT':'UNSAT_INDEPENDENTLY_CONFIRMED','UNKNOWN':'UNSAT_UNCONFIRMED','SAT':'DISAGREEMENT'}[independent['status']],'independent':independent}
        checked.append({'source':c['source'],'mode':c['mode'],'primary_status':status,**answer})
    status='DISAGREEMENT' if any(x['status']=='DISAGREEMENT' for x in checked) else 'INCOMPLETE_UNSAT_UNCONFIRMED' if any(x['status']=='UNSAT_UNCONFIRMED' for x in checked) else 'PASS_INDEPENDENT_CORE_AND_STATUS_ACCOUNTING'
    receipt={'experiment_id':'GDT1417','status':status,'controls':controls(),'retained_positions':indices,'freed_positions':freed,'cases':checked,'pins':{'lock_sha256':sha(E/'LOCK.json'),'result_sha256':sha(A/'RESULT.json'),'gate_validation_sha256':sha(A/'GATE_VALIDATION.json'),'validator_sha256':sha(Path(__file__)),'reused_independent_library_sha256':sha(ROOT/s['independent_library_path'])},'scope':'Independent raw-source DP and core selection; frozen1414 independent many-to-one solver/certificate code reused without modification. All freed groups unconstrained. No whole reading, general minim, phonetic, source-language or meaning claim.'}
    save(A/'VALIDATION.json',receipt);print(json.dumps({'status':status}))

if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    for name in ['gate','native','controls']:g.add_argument('--'+name,action='store_true')
    a=p.parse_args()
    if a.controls:print(json.dumps(controls()))
    elif a.gate:gate()
    else:native()
