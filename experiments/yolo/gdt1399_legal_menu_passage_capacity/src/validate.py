#!/usr/bin/env python3
"""Independent legal-menu simulation and finite-table confirmation; no runner import."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import z3

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
INITIAL=(1,1,1,1,1)
NAMES='ABCDE'


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def parse(raw,signs):
    ways=[[] for _ in range(len(raw)+1)];ways[0]=[()]
    for i in range(len(raw)):
        for sign in signs:
            if ways[i] and raw.startswith(sign,i):
                j=i+len(sign);ways[j]=(ways[j]+[w+(sign,) for w in ways[i]])[:2]
    return list(ways[-1][0]) if len(ways[-1])==1 and ways[-1][0] else None


def menu(state):
    actions=[]
    for source in range(5):
        if state[source]>0:
            for target in range(5):
                if target!=source:actions.append(('MOVE',source,target))
    return actions+[('WAIT',),('ROTATE',)]


def advance(state,action):
    counts=list(state)
    if action[0]=='MOVE':
        _,source,target=action;assert source!=target and counts[source]>0
        counts[source]-=1;counts[target]+=1
    elif action[0]=='ROTATE':counts=counts[-1:]+counts[:-1]
    else:assert action==('WAIT',)
    assert min(counts)>=0 and sum(counts)==5
    return tuple(counts)


def action_name(action):
    return NAMES[action[1]]+'->'+NAMES[action[2]] if action[0]=='MOVE' else action[0]


def simulate(ranks):
    states=[INITIAL];actions=[];waits=0
    for rank in ranks:
        legal=menu(states[-1])
        if not 0<=rank<len(legal):return None
        action=legal[rank]
        assert legal.index(action)==rank
        actions.append(action_name(action));waits+=action==('WAIT',)
        states.append(advance(states[-1],action))
    return {'states':[list(s) for s in states],'actions':actions,'wait_count':waits}


def states_table():
    states=[]
    for a in range(6):
        for b in range(6-a):
            for c in range(6-a-b):
                for d in range(6-a-b-c):states.append((a,b,c,d,5-a-b-c-d))
    assert len(states)==126 and len(set(states))==126
    index={s:i for i,s in enumerate(states)}
    table=[]
    for state in states:
        legal=menu(state)
        table.append([index[advance(state,legal[r])] if r<len(legal) else 126 for r in range(22)])
    return states,index,table


def dfa_check(symbols,timeout_ms=60000,fixed=None):
    states,index,table=states_table()
    solver=z3.Solver();solver.set(timeout=timeout_ms)
    key=[z3.Int('ind_key_'+str(i)) for i in range(22)]
    solver.add(z3.Distinct(key),*[z3.And(k>=0,k<22) for k in key])
    if fixed is not None:
        assert sorted(fixed)==list(range(22))
        solver.add(*[key[i]==fixed[i] for i in range(22)])
    transition=z3.Function('ind_finite_transition',z3.IntSort(),z3.IntSort())
    solver.add(*[transition(22*s+r)==table[s][r] for s in range(126) for r in range(22)])
    trajectory=[z3.Int('ind_state_'+str(i)) for i in range(len(symbols)+1)]
    solver.add(trajectory[0]==index[INITIAL],*[z3.And(s>=0,s<126) for s in trajectory])
    for i,symbol in enumerate(symbols):solver.add(trajectory[i+1]==transition(22*trajectory[i]+key[symbol]))
    answer=solver.check()
    result={'status':str(answer).upper(),'backend':'z3 '+z3.get_version_string(),
            'encoding':'126 explicitly enumerated inventory states; ground finite transition function; integer state indices and permutation key',
            'independent_theorem_kernel':False}
    if answer==z3.unknown:result['reason_unknown']=solver.reason_unknown()
    elif answer==z3.sat:
        model=solver.model();values=[model.eval(k,model_completion=True).as_long() for k in key]
        assert sorted(values)==list(range(22)) and simulate([values[s] for s in symbols]) is not None
        result['counter_key']=values
    return result


def controls():
    states,index,table=states_table();checked=0
    for state in states:
        legal=menu(state)
        assert len(legal)==4*sum(value>0 for value in state)+2
        assert len(set(legal))==len(legal) and len(legal)>=6
        for rank,action in enumerate(legal):
            result=advance(state,action)
            assert table[index[state]][rank]==index[result]
            assert menu(state).index(action)==rank;checked+=1
        assert all(table[index[state]][rank]==126 for rank in range(len(legal),22))
    assert simulate([16,16])['actions']==['E->A','WAIT']
    assert simulate([16,18]) is None
    assert simulate([20,20,20])['wait_count']==3
    assert simulate([15,15])['states'][-1]==list(INITIAL)
    assert advance((5,0,0,0,0),('ROTATE',))==(0,5,0,0,0)
    assert dfa_check([16,16],5000,list(range(22)))['status']=='SAT'
    assert dfa_check([16,18],5000,list(range(22)))['status']=='UNSAT'
    return {'status':'PASS_SOURCE_FREE_CONTROLS','states':126,'legal_transitions_checked':checked,
            'fixed_rank_valid_invalid_checks':True,'finite_table_SAT_UNSAT_controls':True,'native_access':False}


def original_groups(spec):
    worksheet=read(ROOT/spec['worksheet'])
    units=[unit for unit in worksheet['units'] if unit['unit_id']==spec['unit_id']]
    assert len(units)==1 and spec['unit_id']=='f75v_IT2a'
    lines=units[0]['lines']
    assert [line['metadata']['locus'] for line in lines]==['f75v.'+str(i) for i in range(43,50)]
    assert str(lines[0]['metadata']['paragraph_start'])=='1' and str(lines[-1]['metadata']['paragraph_end'])=='1'
    output=[]
    for line in lines:
        meta=line['metadata'];groups=line['original_groups']
        assert meta['page']=='f75v' and meta['edition']=='IT2a' and meta['kind']=='P'
        assert len(groups)==int(meta['source_group_count'])
        assert [int(group[1]) for group in groups]==list(range(1,len(groups)+1))
        for group in groups:
            assert len(group)==5
            parsed=parse(group[2],spec['signs'])
            assert parsed is not None,'Original group is unparseable; do not silently omit it'
            output.append({'id':group[0],'source_group_index':group[1],'raw':group[2],'units':parsed})
    assert len(output)==77 and len({group['id'] for group in output})==77
    return output


def validate():
    lockpath=E/'LOCK.json';lock=read(lockpath)
    pins=lock['files'] if isinstance(lock['files'],dict) else {x['path']:x['sha256'] for x in lock['files']}
    for path in (E/'src/run.py',Path(__file__),E/'src/SPEC.json',E/'METHOD.md'):
        key=str(path.relative_to(ROOT));assert pins[key]==sha(path),key
    spec=read(E/'src/SPEC.json')
    for key in ('worksheet','raw_proposal','selection_plan'):
        assert pins[spec[key]]==sha(ROOT/spec[key])
    assert spec['experiment']=='GDT1399' and spec['initial']==list(INITIAL)
    assert spec['timeout_ms']==60000 and spec['random_seed']==1399
    assert spec['cases']==[{'id':'NATIVE','shuffle_seed':None}]+[{'id':'SHUFFLE_'+str(i),'shuffle_seed':139900+i} for i in range(1,4)]
    assert len(spec['signs'])==len(set(spec['signs']))==22
    assert z3.get_version_string()==spec['z3_version']=='4.15.3'
    originals=original_groups(spec);result=read(A/'RESULT.json')
    assert result['experiment']=='GDT1399' and result['z3_version']==spec['z3_version']
    assert result['status']=='RAW_BOUNDED_SEARCH_REQUIRES_INDEPENDENT_VALIDATION'
    assert set(result['cases'])=={c['id'] for c in spec['cases']}
    certificates={}
    for definition in spec['cases']:
        name=definition['id'];case=result['cases'][name]
        order=list(range(77))
        if definition['shuffle_seed'] is not None:random.Random(definition['shuffle_seed']).shuffle(order)
        groups=[originals[i] for i in order]
        flat=[unit for group in groups for unit in group['units']]
        assert case['id']==name and case['shuffle_seed']==definition['shuffle_seed']
        assert case['group_order']==order and case['groups']==groups and case['units']==flat
        assert case['status'] in ('SAT','UNSAT','UNKNOWN')
        record={'primary_status':case['status'],'groups_checked':77,'working_units_checked':len(flat)}
        if case['status']=='SAT':
            key=case['key'];assert set(key)==set(spec['signs'])
            assert all(type(value) is int for value in key.values()) and sorted(key.values())==list(range(22))
            unused=[sign for sign in spec['signs'] if sign not in set(flat)]
            assert [key[sign] for sign in unused]==sorted(key[sign] for sign in unused)
            ranks=[key[unit] for unit in flat]
            trace=simulate(ranks);assert trace is not None
            assert all(len(state)==5 and all(type(value) is int for value in state) for state in case['states'])
            assert case['states']==trace['states']
            reverse={rank:sign for sign,rank in key.items()}
            encoded=[]
            for i,name_of_action in enumerate(trace['actions']):
                legal=menu(tuple(trace['states'][i]))
                action=next(action for action in legal if action_name(action)==name_of_action)
                encoded.append(reverse[legal.index(action)])
            assert encoded==flat
            record.update(status='SAT_CERTIFICATE_VERIFIED',key_bijection_verified=True,
                          all_states_verified=True,no_internal_resets=True,exact_reencoding_verified=True,
                          wait_count=trace['wait_count'],final_state=trace['states'][-1])
        elif case['status']=='UNSAT':
            secondary=dfa_check([spec['signs'].index(unit) for unit in flat],60000)
            record['secondary']=secondary
            record['status']='UNSAT_INDEPENDENT_ENCODING_CONFIRMED' if secondary['status']=='UNSAT' else 'UNSAT_DISAGREEMENT' if secondary['status']=='SAT' else 'UNSAT_UNCONFIRMED_SECONDARY_UNKNOWN'
        else:
            assert isinstance(case.get('reason',case.get('reason_unknown')),str)
            record['status']='ORIGINAL_UNKNOWN_RETAINED'
        certificates[name]=record
    states=[record['status'] for record in certificates.values()]
    native=certificates['NATIVE']['status']
    controls_states=[certificates['SHUFFLE_'+str(i)]['status'] for i in range(1,4)]
    if 'UNSAT_DISAGREEMENT' in states:decision='VALIDATION_DISAGREEMENT_NO_EXCLUSION'
    elif native=='UNSAT_INDEPENDENT_ENCODING_CONFIRMED':decision='FIXED_NATIVE_FRAME_EXCLUDED'
    elif native=='SAT_CERTIFICATE_VERIFIED' and all(s=='SAT_CERTIFICATE_VERIFIED' for s in controls_states):decision='NATIVE_AND_ALL_SHUFFLES_COMPATIBLE_NO_READING_LEAD'
    elif native=='SAT_CERTIFICATE_VERIFIED' and all(s=='UNSAT_INDEPENDENT_ENCODING_CONFIRMED' for s in controls_states):decision='BOUNDED_ORDER_CONTRAST_ONLY'
    elif native=='SAT_CERTIFICATE_VERIFIED':decision='NATIVE_COMPATIBLE_CONTROL_CONTRAST_UNRESOLVED'
    else:decision='UNRESOLVED_NO_EXCLUSION'
    receipt={'experiment':'GDT1399','status':'VALIDATION_DISAGREEMENT' if 'UNSAT_DISAGREEMENT' in states else 'INDEPENDENT_CERTIFICATE_ACCOUNTING_COMPLETE',
             'decision':decision,'cases':certificates,'source_free_controls':controls(),
             'pins':{'validator_sha256':sha(Path(__file__)),'lock_sha256':sha(lockpath),
                     'result_sha256':sha(A/'RESULT.json'),'worksheet_sha256':sha(ROOT/spec['worksheet'])},
             'implementation':'Explicit donor/recipient ordered menus and exact independent re-encoding. UNSAT confirmation uses separately enumerated126-state transition function, not primary count-vector equations.',
             'limits':['Same Z3 backend is not an independent theorem kernel. Secondary UNKNOWN never confirms UNSAT.',
                       'Original UNKNOWN outcomes are preserved; certificates do not establish historical meaning.',
                       'Paragraph-as-program framing, supplied source phases and22working units are premises.',
                       'Rank and count-vector tags are structural certificates, not translated native actions.']}
    assert not (A/'VALIDATION.json').exists()
    save(A/'VALIDATION.json',receipt)
    print(json.dumps({'status':receipt['status'],'decision':decision,'cases':{k:v['status'] for k,v in certificates.items()}},sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');args=p.parse_args()
    if args.controls:print(json.dumps(controls(),sort_keys=True))
    else:validate()
