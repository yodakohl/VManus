#!/usr/bin/env python3
"""Reproduce only the source-free witness/stop audit; no solver or native data."""
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parents[1];A=E/'artifacts'
FROZEN_VALIDATOR='1b5f3fb72794019b998bb8b7008db7df40659ca76c0c04a8581b9bf6036e1468'


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def menu(state):
    result=[]
    for donor in range(5):
        if state[donor]:
            for receiver in range(5):
                if donor!=receiver:
                    changed=list(state);changed[donor]-=1;changed[receiver]+=1
                    result.append(tuple(changed))
    return result+[tuple(state),(state[-1],)+tuple(state[:-1])]


def arithmetic_step(state,rank):
    occupied=[j for j,value in enumerate(state) if value>0]
    moves=4*len(occupied)
    if rank<moves:
        donor=occupied[rank//4]
        receiver=[j for j in range(5) if j!=donor][rank%4]
        changed=list(state);changed[donor]-=1;changed[receiver]+=1
        return tuple(changed)
    if rank==moves:return tuple(state)
    if rank==moves+1:return (state[-1],)+tuple(state[:-1])
    return None


def main():
    stop=read(A/'CAPACITY_STOP.json');failure=read(A/'CONTROL_FAILURE.json');fixture=read(A/'FIXTURE.json')
    assert stop['experiment']=='GDT1399'
    assert stop['status']=='SOURCE_FREE_SEARCH_BENCHMARK_TIMEOUT_NO_NATIVE_RUN'
    assert stop['code_sha256']==sha(E/'src/run.py')
    assert stop['method_sha256']==sha(E/'METHOD.md') and stop['spec_sha256']==sha(E/'src/SPEC.json')
    assert stop['fixture_sha256']==sha(A/'FIXTURE.json')
    assert sha(E/'src/validate.py')==FROZEN_VALIDATOR
    assert stop['primary_control_outcome']['returned_status']=='UNKNOWN'
    assert stop['primary_control_outcome']['reason']=='timeout'
    assert stop['primary_control_outcome']['timeout_ms']==10000
    assert stop['primary_control_outcome']['fixture_steps']==42
    assert stop['native_solver_run'] is False and stop['independent_native_validation_run'] is False
    assert stop['native_result_exists'] is False
    assert failure['status']=='FAILED_REQUIRED_SOURCE_FREE_BENCHMARK' and failure['exit_code']==1
    assert failure['native_test']=='NOT_RUN' and failure['original_runner_preserved'] is True
    assert all(not (E/name).exists() for name in ('LOCK.json','artifacts/RESULT.json','artifacts/VALIDATION.json','artifacts/PRELOCK_CONTROLS.json'))
    assert fixture['domain']=='ARTIFICIAL_SOURCE_FREE_FULL_ALPHABET_TRACE' and fixture['native_payload'] is False
    assert fixture['identity_key']==list(range(22))
    ranks=fixture['ranks'];assert len(ranks)==42 and set(ranks)==set(range(22))
    state=(1,1,1,1,1);trace=[list(state)]
    for rank in ranks:
        options=menu(state)
        assert type(rank) is int and 0<=rank<len(options)
        following=options[rank]
        assert following==arithmetic_step(state,rank)
        assert sum(following)==5 and min(following)>=0
        state=following;trace.append(list(state))
    assert trace==fixture['states'] and fixture['known_satisfiability']=='SAT_BY_EXPLICIT_WITNESS'
    checked=legal=0
    for a in range(6):
        for b in range(6-a):
            for c in range(6-a-b):
                for d in range(6-a-b-c):
                    stock=(a,b,c,d,5-a-b-c-d);options=menu(stock)
                    assert len(options)==4*sum(v>0 for v in stock)+2
                    for rank in range(22):
                        expected=options[rank] if rank<len(options) else None
                        assert arithmetic_step(stock,rank)==expected
                        checked+=1;legal+=expected is not None
    assert checked==2772 and legal==1652
    receipt={'experiment':'GDT1399','status':'SOURCE_FREE_STOP_RECORD_AND_WITNESS_VERIFIED',
             'original_benchmark_status':'UNKNOWN_TIMEOUT_REQUIRED_SAT_NOT_REACHED',
             'original_benchmark_reclassified':False,'original_benchmark_rerun':False,
             'fixture':{'steps':42,'distinct_ranks':22,'identity_key_bijection':True,
                        'all_states_exactly_verified':True,'known_satisfiability':'SAT_BY_EXPLICIT_WITNESS'},
             'independent_definition_checks':{'states':126,'state_rank_pairs':checked,'legal_transitions':legal,
                                               'invalid_rank_slots':checked-legal,'solver_used':False},
             'native_evaluation':'NOT_RUN','independent_native_validator':'PRESERVED_NOT_EXECUTED_ON_NATIVE_INPUT',
             'prior_native_validator_source_free_controls':{'status':'PASS_RECORDED_BEFORE_STOP',
                 'provenance':'Earlier tool execution of src/validate.py --controls; not rerun by this stop audit.',
                 'fixed_16_16_SAT_and_16_18_UNSAT':True},
             'decision':'Preserve the benchmark stop; no native fitting, larger solver or model exclusion follows.',
             'interpretation':'A concrete legal42-step path exists; UNKNOWN under the search budget is a computational stop, not evidence that the source model is inconsistent.',
             'pins':{name:sha(E/name) for name in ('src/run.py','src/validate.py','src/validate_stop.py','METHOD.md','src/SPEC.json','artifacts/FIXTURE.json','artifacts/CAPACITY_STOP.json','artifacts/CONTROL_FAILURE.json')},
             'limits':['No native worksheet, transcription cache or physical-source payload was opened.',
                       'This receipt does not turn the failed required benchmark into a PASS.',
                       'The stop record is post-benchmark provenance, not a prospective registration lock.']}
    target=A/'STOP_REVIEW.json'
    serialized=json.dumps(receipt,indent=2,sort_keys=True)+'\n'
    if target.exists():assert target.read_text()==serialized
    else:target.write_text(serialized)
    print(json.dumps({'status':receipt['status'],'fixture_steps':42,'native_evaluation':'NOT_RUN'},sort_keys=True))

if __name__=='__main__':main()
