#!/usr/bin/env python3
"""Execute only the registered60 retained traces; no world enumeration."""
import collections
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from model import POLICIES, aN, derive_person, execute, late_bodily_diagnostic

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]

def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name, value):
    (D/'artifacts'/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def candidate(name):
    return {'id':name,'quantity':name.split('_')[0],
            'knowledge':'DIFFERENT_OBJECTS' if 'DIFFERENT_OBJECTS' in name else 'SAME_OBJECT',
            'purity':name.rsplit('_',1)[1]}

def engineering_probes(graph, stored):
    counts, world = stored['counts'], stored['world']
    foreign = world['recipient']
    fixtures = []
    for position, expected in [(9,'EXTRACT_SOURCE_ACTOR'),(18,'ACTOR_KNOWLEDGE'),(35,'CLAIM_SOURCE_ACTOR')]:
        out = execute(graph, counts, world, 'ORIGIN', forced_person={position:foreign})
        ref = next(x for x in out['reference_bindings'] if x['position']==position)
        assert ref['actual_consumed_person']==foreign and expected in out['first_violations']
        if position==9:
            assert out['trace'][-1]['operation']['using']==f'NAILS({foreign})'
            assert not out['final']['loose']
        elif position==18:
            assert out['knowledge_assertions'][0]['subject']==foreign
            assert out['knowledge_assertions'][0]['actual_value'] is False
        else:
            assert ref['actual_attempted_claim_content']['actor']==foreign
            assert ref['actual_attempted_claim_content']['content']==f'RELEASE({foreign},{foreign},Q) BY_GRACE(GOD)'
            assert not out['final']['claims']
        fixtures.append({'engineering_only':True,'name':'FORCED_PERSON_'+str(position),
                         'expected_violation':expected,'output':out})
    out = execute(graph,counts,world,'ORIGIN',instrument_owner_override=foreign)
    assert out['first_violations']==['INSTRUMENT_OWNER']
    fixtures.append({'engineering_only':True,'name':'WRONG_NAIL_OWNER','output':out})
    baseline = execute(graph,counts,world,'ORIGIN')
    material={'id':'G','type':'SeedGroup','members':baseline['provenance']['initial_contains']['R']['G']}
    state=baseline['final'];prov=baseline['provenance']
    missing=derive_person('ORIGIN',material,state,[],prov,world['actor'])
    assert missing['status']=='MISSING' and missing['value'] is None
    duplicate=deepcopy(baseline['completed_history'][0]);duplicate['actor']=foreign;duplicate['event']='ENGINEERING_ONLY_SECOND_TAKE'
    ambiguous=derive_person('ORIGIN',material,state,[baseline['completed_history'][0],duplicate],prov,world['actor'])
    assert ambiguous['status']=='AMBIGUOUS' and ambiguous['value'] is None
    wrong=aN({'id':'C','type':'Cloth','members':material['members']})
    assert wrong['status']=='TYPE_MISMATCH' and wrong['value'] is None
    fixtures.extend([{'engineering_only':True,'name':'NO_COMPLETED_TAKE','result':missing},
                     {'engineering_only':True,'name':'AMBIGUOUS_ACQUISITION_ACTORS','result':ambiguous},
                     {'engineering_only':True,'name':'CLOTH_NOT_SEED_GROUP','result':wrong}])
    return fixtures

def main():
    registration=read(D/'src/REGISTRATION.json')
    for pin in registration['inputs']:
        assert sha(ROOT/pin['path'])==pin['sha256'],pin['path']
    assert sha(D/'PREREGISTRATION.md')==registration['preregistration_sha256']
    release=read(D/'artifacts/PUBLIC_REGISTRATION.json')
    assert release.get('commit'), 'Root public registration must precede candidate execution'
    sys.dont_write_bytecode=True
    old=ROOT/'experiments/yolo/gdt1027_seed_rite_scope_and_identity'
    spec=importlib.util.spec_from_file_location('gdt1132_pinned_compiler',old/'src/model.py')
    legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    source=read(old/'src/SOURCE.json'); stored=read(old/'artifacts/TRACES.json')
    assert len(stored)==60
    lex=source['all_30_new_lexical_entries']; assert len(lex)==30
    records={'ZL3b':source['target']['complete_raw_record'],
             'IT2a':source['target']['IT2a_complete_alternative']}
    graphs={name:legacy.compile_reading(records['ZL3b']['lines'],lex,candidate(name))
            for name in sorted({r['candidate'] for r in stored})}
    assert len(graphs)==8 and all(g['status']=='COMPLETE' for g in graphs.values())
    scope={ed:{'raw_record':deepcopy(rec), 'derivation':legacy.compile_reading(rec['lines'],lex,candidate(next(iter(graphs))))}
           for ed,rec in records.items()}
    assert scope['IT2a']['derivation']['status']=='UNBOUND_FORMS'
    groups=[]
    for ed,rec in records.items():
        position=0
        for line in rec['lines']:
            for i,(raw,sid) in enumerate(zip(line['words'],line['source_ids']),1):
                position+=1
                groups.append({'edition':ed,'position':position,'source_group_id':sid,'raw_form':raw,
                               'within_line_index':i,'native_line_metadata':{k:deepcopy(v) for k,v in line.items() if k not in {'words','source_ids'}},
                               'original_entry':deepcopy(lex.get(raw)),
                               'status':'UNBOUND_EXACT_FORM' if raw not in lex else 'PROVISIONAL_OLD_ENTRY',
                               'derivation_scope':'COMPLETE_ZL_SCHEMA' if ed=='ZL3b' else 'PARTIAL_READER_NO_ALIAS'})
        assert position==rec['groups']
    outputs=[];diagnostics=[];summaries=[]
    for policy in POLICIES:
        statuses=collections.Counter(); coherent=0; matches=0
        for index,row in enumerate(stored):
            graph=graphs[row['candidate']]
            out=execute(graph,row['counts'],row['world'],policy,row['case'])
            oldout=row['output']
            same=all(out[k]==oldout[k] for k in ['coherent','first_failure_step','first_violations','completed_actions','unexecuted'])
            if policy in {'ORIGIN','LAST_WORKING','ADDRESSEE'}:
                assert same,(policy,index,out['first_violations'],oldout['first_violations'])
                assert all(ref['actual_consumed_person']==row['world']['actor'] for ref in out['reference_bindings'])
            else:
                assert out['status']=='MISSING_REFERENCE' and out['first_failure_position']==9
                assert out['completed_actions']==1 and out['unexecuted_daiin_positions']==[18,35]
            assert all(r['root']['value']['id']=='G' for r in out['bare_root_bindings'])
            if out['coherent']:
                assert [r['position'] for r in out['bare_root_bindings']]==[5,13,23]
                assert [r['position'] for r in out['reference_bindings']]==[9,18,35]
            outputs.append({'stored_trace_index':index,'candidate':row['candidate'],'case':row['case'],
                            'counts':deepcopy(row['counts']),'world':deepcopy(row['world']),
                            'legacy_outcome':{k:deepcopy(oldout[k]) for k in ['coherent','first_failure_step','first_violations','completed_actions','unexecuted']},
                            'same_legacy_outcome':same,'output':out})
            statuses[out['status']]+=1;coherent+=out['coherent'];matches+=same
        summaries.append({'policy':policy,'stored_traces':60,'coherent_complete':coherent,
                          'legacy_outcome_matches':matches,'status_counts':dict(statuses)})
    # Eligibility is the unchanged complete legacy prefix, not a restarted support candidate.
    for index,row in enumerate(stored):
        if row['output']['coherent']:
            assert row['case'] in {'NONE','SELF_WITNESS'}
            baseline=next(x['output'] for x in outputs if x['stored_trace_index']==index and x['output']['policy']=='ADDRESSEE')
            diagnostic=late_bodily_diagnostic(baseline)
            assert diagnostic['status']=='CONDITIONAL_LOCAL_DIAGNOSTIC_ONLY'
            assert diagnostic['derivation']['value']==row['world']['recipient']
            diagnostics.append({'stored_trace_index':index,'candidate':row['candidate'],'case':row['case'],
                                'world':deepcopy(row['world']),'diagnostic':diagnostic})
    assert len(diagnostics)==12
    positive=next(r for r in stored if r['candidate']=='TOTAL_SAME_OBJECT_ACTOR' and r['case']=='NONE')
    probes=engineering_probes(graphs[positive['candidate']],positive)
    result={'experiment':'GDT1132','status':'AUTHOR_EXECUTED_PENDING_INDEPENDENT_VALIDATION',
            'utc':datetime.now(timezone.utc).isoformat(),'public_registration':release,
            'policy_summary':summaries,'source_groups':{'ZL3b':37,'IT2a':35},'source_exact_lexical_entries':30,
            'old_clause_schemas':5,'old_scope_variants':8,'stored_trace_inputs':60,'evaluations':len(outputs),
            'positive_self_inputs':12,'negative_instruction_inputs':48,
            'conditional_late_diagnostics':len(diagnostics),
            'late_distinct_actor_contrasts':sum(r['diagnostic']['actor_changed'] for r in diagnostics),
            'late_self_equivalences':sum(not r['diagnostic']['actor_changed'] for r in diagnostics),
            'engineering_probes':len(probes),'new_whole_values':0,'new_clause_rules':0,'new_world_enumeration':0,
            'paid_changes':['replace direct YOU=A reference recipe at three positions','retain initial G→R membership',
                            'retain actual completed action history and independently supplied initial imperative actor',
                            'typed material/person gating and policy-specific uniqueness/recency/support projections',
                            'bind returned Person into EXTRACT/instrument owner, KNOWS lookup and attempted attributed RELEASE',
                            'one case-scoped persistent G register and explicit t_bind staged assertion'],
            'retained_costs':{'old_whole_guesses':30,'old_fitted_clauses':5,'old_baseline_binding_assumptions':11,
                              'quantity_knowledge_purity_scopes':8,'different_object_macro_change':1},
            'claims':['ORIGIN/LAST_WORKING/ADDRESSEE equivalent on this one-actor supplied history; unselected.',
                      'BODILY_SUPPORT missing at9; late diagnostic cannot complete it.',
                      'Recipient-purity scope remains internally coherent but omits source actor purity.',
                      'IT nine unknown exact forms and fused/separated differences remain unresolved.'],
            'independent_confirmation_capacity':0,'confirmed_translated_words':0,'medical_effects_observed':0,
            'semantic_validation':False,'input_pins_verified':True}
    result['contract_sha256']={f:sha(D/f) for f in ['PREREGISTRATION.md','METHOD.md','src/REGISTRATION.json',
                                                     'src/DESIGN_NOTE.json','artifacts/PUBLIC_REGISTRATION.json']}
    write('AUTHOR_SOURCE_ACCOUNT.json',{'source_sha256':sha(old/'src/SOURCE.json'),'scope':scope,
                                      'all_groups':groups,'original_dictionary':lex,'compiled_ZL_graphs':graphs,
                                      'no_new_aliases':True,'RF':'NO_COMPLETE_PACKET_IN_REGISTERED_INPUT_NOT_SEARCHED'})
    write('AUTHOR_TRACES.json',outputs);write('AUTHOR_LATE_DIAGNOSTICS.json',diagnostics)
    write('AUTHOR_ENGINEERING_PROBES.json',probes);write('AUTHOR_RESULT.json',result)
    write('AUTHOR_HASH_RECEIPT.json',{'phase':'FINAL_AUTHOR_OUTPUT','utc':result['utc'],
          'files':{f:sha(D/f) for f in ['src/model.py','src/run.py','artifacts/AUTHOR_SOURCE_ACCOUNT.json',
                  'artifacts/AUTHOR_TRACES.json','artifacts/AUTHOR_LATE_DIAGNOSTICS.json',
                  'artifacts/AUTHOR_ENGINEERING_PROBES.json','artifacts/AUTHOR_RESULT.json']},
          'registered_input_pins':registration['inputs'],'independent_validator_outputs_read':False})
    print(json.dumps({k:result[k] for k in ['status','evaluations','policy_summary','conditional_late_diagnostics',
                                         'late_distinct_actor_contrasts','late_self_equivalences','engineering_probes']}))
    return 0

if __name__=='__main__':raise SystemExit(main())
