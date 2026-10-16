#!/usr/bin/env python3
"""Post-unblinding accounting only: frozen engine scores, no optimization."""
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
A=E/'artifacts';R=E/'runtime';TOLERANCE=1e-7


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')


def score(index,key,b):
    command=[str(R/'engine'),'--score',str(R/'model.bin'),str(R/'cases.bin'),str(index),str(b)]+[str(w) for w in key]
    return json.loads(subprocess.run(command,check=True,capture_output=True,text=True).stdout)


def rank_mod3(rows):
    matrix=[[n%3 for n in row] for row in rows]
    pivot=0
    for col in range(23):
        chosen=next((i for i in range(pivot,len(matrix)) if matrix[i][col]),None)
        if chosen is None:continue
        matrix[pivot],matrix[chosen]=matrix[chosen],matrix[pivot]
        inv=1 if matrix[pivot][col]==1 else 2
        matrix[pivot]=[(n*inv)%3 for n in matrix[pivot]]
        for i in range(len(matrix)):
            if i!=pivot and matrix[i][col]:
                q=matrix[i][col]
                matrix[i]=[(a-q*b)%3 for a,b in zip(matrix[i],matrix[pivot])]
        pivot+=1
        if pivot==len(matrix):break
    return pivot


def components(result):
    return {key:result[key] for key in ['score','source_mixture_logp','source_component_logp','sum_log_shape','sum_log_state_normalizers']}


def main():
    # Verify immutable blind output before opening the released truth.
    recovery_lock=read(A/'RECOVERY_LOCK.json')
    for item in recovery_lock['files']:assert sha(ROOT/item['path'])==item['sha256'],item['path']
    release=read(A/'UNBLIND_RECEIPT.json')
    assert release['recovery_lock_sha256']==sha(A/'RECOVERY_LOCK.json')
    assert release['recovery_frozen_utc']==recovery_lock['frozen_utc']
    assert datetime.fromisoformat(recovery_lock['frozen_utc'])<datetime.fromisoformat(release['unblind_utc'])
    assert release['no_search_changes_after_recovery'] is True
    lockpath=E/'src/REGISTRATION_LOCK.json';registration=read(lockpath)
    for path,h in registration['hashes'].items():assert sha(ROOT/path)==h,path
    recovery=read(A/'RECOVERY.json');restarts=read(A/'RESTARTS.json')
    assert recovery['status']=='BLIND_RECOVERY_OUTPUT_COMPLETE' and recovery['completed_restarts']==recovery['required_restarts']==576
    assert recovery['truth_access'] is False
    assert recovery['cases_sha256']==sha(A/'CASES.json')
    assert release['released_truth_sha256']==sha(A/'TRUTH.json')
    truths=read(A/'TRUTH.json')['cases']
    anonymous=read(A/'CASES.json')['cases']
    truth_by_id={t['id']:t for t in truths}
    assert len(truth_by_id)==len(truths)==len(anonymous)==18
    by_id={c['id']:c for c in recovery['cases']};assert set(by_id)==set(truth_by_id)
    records=[]
    for index,public in enumerate(anonymous):
        identity=public['id'];true=truth_by_id[identity];found=by_id[identity]
        assert true['units']==public['units']
        assert true['length']==found['message_length']==len(public['units'])==len(true['text'])
        assert found['case_index']==index
        true_score=score(index,true['weights'],true['b'])
        winner_score=score(index,found['weights'],found['b'])
        assert true_score['plaintext']==true['text']
        assert winner_score['plaintext']==found['plaintext']
        assert winner_score['source_characters']==found['source_characters']
        for field in ['score','source_mixture_logp','sum_log_shape','sum_log_state_normalizers']:
            assert abs(winner_score[field]-found[field])<=TOLERANCE,(identity,field)
        for a,b in zip(winner_score['source_component_logp'],found['source_component_logp']):assert abs(a-b)<=TOLERANCE
        matches=sum(a==b for a,b in zip(found['plaintext'],true['text']))
        message_exact=found['plaintext']==true['text']
        key_exact=found['weights']==true['weights'] and found['b']==true['b']
        gap=winner_score['score']-true_score['score']
        relation='LOWER_THAN_TRUE' if gap < -TOLERANCE else 'HIGHER_THAN_TRUE' if gap>TOLERANCE else 'TIED_WITHIN_TOLERANCE'
        if gap < -TOLERANCE:classification='SEARCH_FAILURE_TRUE_KEY_OUTSCORES_WINNER'
        elif not message_exact and gap>TOLERANCE:classification='BETTER_WRONG_WINNER_MODEL_OR_FINITE_MESSAGE_AMBIGUITY'
        elif not message_exact:classification='WRONG_MESSAGE_SCORE_TIE_UNRESOLVED'
        else:classification='EXACT_SOURCE_RECOVERY'
        used=set();previous=[0]*22;equations=[]
        for packet in public['units']:
            counts=[packet.count(i) for i in range(22)]
            used.update(packet)
            equations.append([a-b for a,b in zip(counts,previous)]+[1])
            previous=counts
        rank=rank_mod3(equations)
        if message_exact and rank==23:assert key_exact
        runs=[r for r in restarts['results'] if r['case_index']==index]
        assert len(runs)==32 and all(r['status']=='COMPLETE' and r['proposals']==256 for r in runs)
        assert all(r['seed']==1390000+index*1000+r['start_index'] for r in runs)
        chosen=min(runs,key=lambda r:(-r['winner']['score'],r['winner']['weights'],r['winner']['b']))
        assert chosen['start_index']==found['winning_start_index']
        records.append({'id':identity,'case_index':index,'kind':true['kind'],'source_component':true['language'],'length':true['length'],
                        'exact_source':message_exact,'matching_characters':matches,'character_agreement':matches/true['length'],
                        'exact_effective_key':key_exact,'observed_message_equivalent_key':message_exact,'different_key_same_message':message_exact and not key_exact,
                        'difference_matrix_rank_mod3':rank,'unobserved_weight_indices':sorted(set(range(22))-used),
                        'observed_character_equations_unique_key':rank==23,
                        'winner':components(winner_score),'true_key':components(true_score),'winner_minus_true_score':gap,
                        'score_relation':relation,'failure_classification':classification,
                        'restart_evaluations':sum(r['evaluations'] for r in runs),'restart_cpu_seconds':sum(r['cpu_seconds'] for r in runs)})
    summaries={}
    for kind,count in [('POSITIVE',12),('NEGATIVE',6)]:
        rows=[r for r in records if r['kind']==kind];assert len(rows)==count
        summaries[kind]={'cases':len(rows),'exact_sources':sum(r['exact_source'] for r in rows),'exact_keys':sum(r['exact_effective_key'] for r in rows),
                         'matching_characters':sum(r['matching_characters'] for r in rows),'total_characters':sum(r['length'] for r in rows),
                         'character_agreement':sum(r['matching_characters'] for r in rows)/sum(r['length'] for r in rows),
                         'source_agreement_range':[min(r['character_agreement'] for r in rows),max(r['character_agreement'] for r in rows)],
                         'winner_minus_true_score_range':[min(r['winner_minus_true_score'] for r in rows),max(r['winner_minus_true_score'] for r in rows)],
                         'classifications':dict(Counter(r['failure_classification'] for r in rows)),
                         'rank_mod3_range':[min(r['difference_matrix_rank_mod3'] for r in rows),max(r['difference_matrix_rank_mod3'] for r in rows)]}
    success=summaries['POSITIVE']['exact_sources']==12
    result={'experiment_id':'GDT1390','status':'ALL_POSITIVE_MESSAGES_RECOVERED' if success else 'COMPLETE_SOURCE_RECOVERY_GATE_FAILED',
            'post_unblind_accounting':True,'primary_gate':success,'primary_requirement':'All12positive complete sources recovered exactly; no native attempt in this experiment.',
            'truth_score_tolerance':TOLERANCE,'summaries':summaries,'cases':records,
            'recovery_wall_seconds':recovery['wall_seconds'],'completed_restarts':576,
            'key_evaluations':sum(r['evaluations'] for r in restarts['results']),
            'pins':{name:sha(A/name) for name in ['RECOVERY.json','RESTARTS.json','RECOVERY_LOCK.json','RECOVERY_INPUT_LOCK.json','UNBLIND_RECEIPT.json','TRUTH.json','CASES.json','MODELS.json','BENCHMARK.json']},
            'registration_lock_sha256':sha(lockpath),'analysis_source_sha256':sha(Path(__file__)),
            'limits':['Synthetic controls under a complete paid model only; no Voynich plaintext, native language, word meaning or general cumulative-writer rejection.',
                      'Exact-message equivalence concerns only these observed packets, not equality of full channel laws.',
                      'Rank below23 proves dependence of observed character equations; the emission normalizer may still distinguish keys. No uniquely recovered key is inferred from message recovery.',
                      'True-key comparison uses the frozen primary engine after output sealing. Independent validator recomputes by a separate backward DP.',
                      'Negative controls are reported separately and are not readable-source evidence.'],
            'next_decision':'STOP_THIS_FIXED_ATTACK_NO_NATIVE_PILOT' if not success else 'SEPARATE_NATIVE_PILOT_SELECTION_REQUIRED'}
    assert not (A/'RESULT.json').exists()
    save(A/'RESULT.json',result)
    print(json.dumps({'status':result['status'],'primary_gate':success,'summaries':summaries},sort_keys=True))

if __name__=='__main__':main()
