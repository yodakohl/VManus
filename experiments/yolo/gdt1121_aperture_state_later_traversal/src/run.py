#!/usr/bin/env python3
"""Scoped fixed-inventory diagnostic; does not search new manuscript content."""
import csv, hashlib, json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
def write(name,data):
    (E/'artifacts'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
    spec=json.loads((E/'src/SPEC.json').read_text())
    loaded={}
    for key,b in spec['inputs'].items():
        raw=(ROOT/b['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==b['sha256'],key
        loaded[key]=json.loads(raw)
    a,t,p,s=[loaded[k] for k in ('author','target','priors','signatures')]
    assert a['lexical_roots']==s['lexical_roots'] and a['whole_form_residuals']==s['whole_form_residuals']
    lex={x['surface']:x for x in a['lexical_roots']+a['whole_form_residuals']}
    prefix=[]
    for x in a['positions'][:13]:
        if x['paid_kind']=='hypothetical_composition':
            assert x['segmentation']==['d','shedy']
            sort=lex['shedy']['sort']
        else: sort=lex[x['raw_surface']]['sort']
        prefix.append(dict(position=x['position'],source_id=x['id'],surface=x['raw_surface'],segmentation=x['segmentation'],declared_sort=sort))
    events=[x for x in prefix if x['declared_sort'].startswith(('UnaryProcess(','Motion(','Partition('))]
    domain=s['common_G3_finite_domains']['qocthdy']['domain']
    assert domain==spec['checks']['accepted_event_sorts']
    compatible=[x for x in events if x['declared_sort'] in domain]
    modifier=a['positions'][13]
    assert modifier['position']==14 and modifier['raw_surface']=='qocthdy'
    trace=dict(prefix=prefix,events=events,accepted_sorts=domain,compatible_events=compatible,modifier=modifier,conflict=not compatible,scope='Nominated prefix sort projection, not a full grammar derivation')
    profiles={x['form']:x for x in p['profiles']}
    rawrows=[dict(zip(line['columns'],g)) for line in t['raw_lines'] for g in line['groups']]
    init=[]
    for x in lex.values():
        if x['sort'] not in spec['checks']['whole_initialization_sorts']: continue
        for edition in ('ZL3b','IT2a','RF1b'):
            owned=[r for r in rawrows if r['edition']==edition and r['ivtff_group_raw']==x['surface']]
            count=profiles[x['surface']]['editions'][edition]['count']
            assert count==len(owned)==1 and all(r['page']=='f85r1' for r in owned)
            init.append(dict(form=x['surface'],sort=x['sort'],edition=edition,admitted_exact_count=count,owned_seed_count=len(owned),outside_occurrences=count-len(owned),source_ids=[r['source_group_id'] for r in owned]))
    positions={w:[x['position'] for x in a['positions'] if x['raw_surface']==w] for w in ('chy','qokeey','chor')}
    assert positions=={'chy':[27],'qokeey':[57],'chor':[58]}
    later=any(x>58 for x in positions['chy'])
    candidates=[dict(candidate=k,qokeey=v,predicted_state_if_completed_and_bound=state,local_signature_conflict_position=14,outside_whole_initialization_capacity=0,seed_later_traversal=later,aperture_test_scored=False,decision='NEW_SIGNATURE_TUPLE_STOPPED; ORIGINAL_FK_C0_UNCHANGED',confirmed_words=0,independent_confirmation_capacity=0) for k,v,state in [('A','seal','CLOSED'),('B','open','OPEN')]]
    result=dict(experiment='GDT1121',status='NO_STATE_TEST_CAPACITY__NEW_SIGNATURE_CONFLICT',local_conflict_position=14,outside_whole_initialization_upper_bound=0,seed_positions=positions,aperture_tests_scored=0,external_paragraph_search=False,new_assumptions=s['new_assumption_count'],candidates=candidates,confirmed_words=0,independent_confirmation_capacity=0,significance_claim=False,claim_ceiling='Failure of new strict signature tuple and necessary fixed initialization capacity; original FK interpretations remain unverified, not refuted wholesale.')
    write('TRACE.json',trace);write('INITIALIZATION.json',init);write('RESULT.json',result)
    with (E/'artifacts/CANDIDATE_TABLE.tsv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(candidates[0]),delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(candidates)
    print(json.dumps(result))
if __name__=='__main__':main()
