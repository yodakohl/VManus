from common import *
from independent import facts,verify_joint
import csv

def main():
    check_lock();s=source();sp=spec();oldsp=read(OLD/'src/SPEC.json');ind=module('old_independent',OLD/'src/independent.py')
    parent_source=read(R/s['source_bindings'][0]['path'])['design']
    assert s['frozen_parent']['all_24_meanings_exact']=={**parent_source['fixed_inherited_hypotheses'],**parent_source['new_hypotheses']}
    assert s['frozen_parent']['all_eight_clauses']==parent_source['clauses'] and s['frozen_parent']['all_nine_grammar_rows']==parent_source['grammar']
    assert {k:sp['lexicon'][k] for k in oldsp['lexicon']}==oldsp['lexicon']
    newwords=[w for c in s['new_complete_clauses'] for w in c['raw'].split()];oldwords=[w for l in s['target']['old_complete_projection'] for w in l['raw'].split()]
    parses=ind.parses(newwords,sp);oldparses=ind.parses(oldwords,oldsp)
    assert len(parses)==len(oldparses)==1
    assert len(newwords+oldwords)==96 and len(set(newwords+oldwords))==64
    assert len(set(newwords)&set(oldsp['lexicon']))==7 and sum(w in oldsp['lexicon'] for w in newwords)==17
    assert [i for c in parses[0] for i in range(c['start'],c['end'])]==list(range(63))
    original=read(OLD/'artifacts/ROWS.json');rows=read(A/'ROWS.json');pred=list(csv.DictReader((A/'PREDICTIONS.tsv').open(),delimiter='\t'));checks=[]
    assert len(rows)==len(pred)==4
    for r in rows:
        old=next(x['result']['parses'][0]['graph'] for x in original if x['pairing']==r['pairing'])
        ind.validate_graph(oldparses[0],old,r['pairing'])
        assert r['complete_parse_count']==len(parses) and len(r['readings'])==1
        one=r['readings'][0];assert one['parse']==parses[0]
        expected=facts(parses[0]);assert expected==one['new_graph']
        errors=verify_joint(expected,old,r['mode'],one['joint'])
        p=next(x for x in pred if x['pairing']==r['pairing'] and x['mode']==r['mode'])
        assert one['joint']['status']==p['predicted_status']
        assert errors==(['SHARED_V_SOLE_PHASE'] if r['mode']=='SHARED_FRAME' and r['pairing']=='reversed' else [])
        assert sum(x['truth'] for x in expected['states'])==1
        assert expected['requirements'][0]['asserted_truth'] is False
        assert expected['progress'][0]['before']=='Z3' and expected['bounded'][0]['endpoint']==dict(predicate='FINISHED',cloth=old['cloth'])
        assert expected['recurrence'][0]['count'] is None and expected['recurrence'][0]['amount'] is None
        checks.append(dict(pairing=r['pairing'],mode=r['mode'],status='PASS',errors=errors))
    scope=read(A/'DIPLOMATIC_SCOPE.json');assert [x['raw'] for x in scope['IT_unknown']]==['pdal','qokedal','sor']
    assert scope['new_ZL_ineligible_lines']==['f83r.21']
    write(A/'INDEPENDENT.json',dict(status='PASS',checks=checks,scope='Separate relational new facts/joint constraints and unchanged old graph validator; same author, no independent meaning.'))
    write(A/'VALIDATION.json',dict(status='PASS',executed_utc=now(),candidate_models=4,whole_groups=96,old_types_retained=24,old_types_reused=7,new_types=40,confirmed_words=0,independent_meaning_capacity=0))
    print(json.dumps(read(A/'VALIDATION.json'),indent=2))

if __name__=='__main__':main()
