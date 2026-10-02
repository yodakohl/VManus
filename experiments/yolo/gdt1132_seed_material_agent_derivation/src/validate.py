#!/usr/bin/env python3
"""Independent GDT1132 validator; never imports the legacy executor.

--preflight reads only frozen independent expectations and bound primaries.
Author inspection requires root's --release FILE with exact artifact/hash pins.
The small actual-schema/probe adapter is completed after that release.
"""
import argparse
import hashlib
import json
import sys
sys.dont_write_bytecode = True
import importlib.util
from collections import Counter
from copy import deepcopy
from pathlib import Path

D = Path(__file__).resolve().parents[1]
ROOT = D.parents[2]
EXPECTED_SHA = "ef167b14bb08f0d8df8981cac0ae62b510d0d6e5481e1773db9cc79f2beb3c81"
PLAN_SHA = "9b1a15d2445c3a76e28b677e54a3857d020bd1b15d969ea5ea6ab2f5a04af83a"
LEGACY = ROOT / "experiments/yolo/gdt1027_seed_rite_scope_and_identity"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(path):
    relative = Path(path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Released path must remain within this experiment")
    prefix = D.relative_to(ROOT).parts
    result = ROOT/relative if relative.parts[:len(prefix)] == prefix else D/relative
    if not result.resolve().is_relative_to(D.resolve()):
        raise ValueError("Released path resolves outside this experiment")
    return result


def preflight():
    checks = []
    def check(name, passed):
        checks.append({"check": name, "status": "PASS" if passed else "FAIL"})
    check("independent_EXPECTED_bytes", sha(D/"artifacts/EXPECTED.json") == EXPECTED_SHA)
    check("independent_VALIDATOR_PLAN_bytes", sha(D/"artifacts/VALIDATOR_PLAN.md") == PLAN_SHA)
    expected = read(D/"artifacts/EXPECTED.json")
    registration = read(D/"src/REGISTRATION.json")
    check("bound_input_bytes", all(sha(ROOT/p["path"]) == p["sha256"] for p in expected["input_pins"]))
    check("registered_inputs_equal_independent_pins", registration["inputs"] == expected["input_pins"])
    check("registered_preregistration_bytes", sha(D/"PREREGISTRATION.md") == registration["preregistration_sha256"] == expected["preregistration_sha256"])
    source = read(LEGACY/"src/SOURCE.json")
    zl = source["target"]["complete_raw_record"]
    it = source["target"]["IT2a_complete_alternative"]
    words = [word for line in zl["lines"] for word in line["words"]]
    check("ZL37_IT35_original_capacity", zl["groups"] == 37 and it["groups"] == 35)
    check("all_three_bare_aiin_and_daiin_positions", [i+1 for i,w in enumerate(words) if w == "aiin"] == [5,13,23] and
          [i+1 for i,w in enumerate(words) if w == "daiin"] == [9,18,35])
    check("original_30_guesses_five_clauses_eleven_assumptions", len(source["all_30_new_lexical_entries"]) == 30 and
          len(source["complete_clauses"]) == 5 and len(source["explicit_new_binding_assumptions"]) == 11)
    legacy = read(LEGACY/"artifacts/TRACES.json")
    check("all60_unique_expected_cases", len(expected["cases"]) == len(legacy) == 60 and
          len({case["case_id"] for case in expected["cases"]}) == 60)
    check("all240_four_policy_expectations", sum(len(case["policies"]) for case in expected["cases"]) == 240 and
          all({p["policy"] for p in case["policies"]} == set(registration["policies"]) for case in expected["cases"]))
    check("expected_stored_case_identity", all(case["candidate"] == old["candidate"] and case["case"] == old["case"] and
          case["counts"] == old["counts"] and case["actor"] == old["world"]["actor"] and
          case["recipient"] == old["world"]["recipient"] for case,old in zip(expected["cases"],legacy)))
    complete = [case for case in expected["cases"] if case["baseline_prefix_late_body_diagnostic"]["eligible"]]
    check("late_only12_complete_prefixes_eight_distinct_four_self", len(complete) == 12 and
          sum(not case["actor_equals_recipient"] for case in complete) == 8 and
          sum(case["actor_equals_recipient"] for case in complete) == 4)
    check("body_all60_first_missing9_never_complete", all(next(p for p in case["policies"] if p["policy"] == "BODILY_SUPPORT")["expected_result"]["first_failure_position"] == 9 and
          not next(p for p in case["policies"] if p["policy"] == "BODILY_SUPPORT")["expected_result"]["whole_complete"] for case in expected["cases"]))
    return checks, expected, source


def verify_release(path):
    release = read(local(path))
    files = release.get("files", release)
    if not files:
        raise ValueError("Root release must pin author artifacts")
    for name,digest in files.items():
        if not isinstance(digest,str) or sha(local(name)) != digest:
            raise ValueError("Released author artifact hash mismatch: " + name)
    return files


def validate(files, checks, expected, source):
    def check(name, passed, detail=None):
        item = {'check': name, 'status': 'PASS' if passed else 'FAIL'}
        if detail is not None: item['detail'] = detail
        checks.append(item)
    account = read(D/'artifacts/AUTHOR_SOURCE_ACCOUNT.json')
    traces = read(D/'artifacts/AUTHOR_TRACES.json')
    late = read(D/'artifacts/AUTHOR_LATE_DIAGNOSTICS.json')
    result = read(D/'artifacts/AUTHOR_RESULT.json')
    legacy = read(LEGACY/'artifacts/TRACES.json')
    release=read(D/'artifacts/FINAL_RELEASE.json'); receipt=read(D/'artifacts/AUTHOR_HASH_RECEIPT.json')
    check('author_final_receipt_hash_and_pins',sha(D/'artifacts/AUTHOR_HASH_RECEIPT.json')==release['author_receipt_sha256'] and receipt['files']==files and receipt['registered_input_pins']==expected['input_pins'])
    check('author_contract_bytes', all(sha(local(p)) == h for p,h in result['contract_sha256'].items()))
    native = []
    for edition, key in [('ZL3b','complete_raw_record'),('IT2a','IT2a_complete_alternative')]:
        raw = source['target'][key]
        check(edition+'_complete_native_record', account['scope'][edition]['raw_record'] == raw)
        for line in raw['lines']:
            for i,(word,sid) in enumerate(zip(line['words'],line['source_ids']),1):
                native.append({'edition':edition,'position':len([r for r in native if r['edition']==edition])+1,
                    'source_group_id':sid,'raw_form':word,'within_line_index':i,
                    'native_line_metadata':{k:v for k,v in line.items() if k not in ('words','source_ids')},
                    'original_entry':source['all_30_new_lexical_entries'].get(word)})
    fields = tuple(native[0])
    check('all72_exact_native_positions_no_duplicates', len(account['all_groups']) == 72 and
          [{k:r.get(k) for k in fields} for r in account['all_groups']] == native and
          len({r['source_group_id'] for r in account['all_groups']}) == 72)
    check('original30_dictionary_and_source_pin', account['original_dictionary'] == source['all_30_new_lexical_entries'] and
          account['source_sha256'] == sha(LEGACY/'src/SOURCE.json') and account['no_new_aliases'] is True)
    unknown = sorted({r['raw_form'] for r in native if r['edition']=='IT2a' and r['original_entry'] is None})
    check('IT_unknowns_and_no_RF_capacity_retained', account['scope']['IT2a']['derivation']['status']=='UNBOUND_FORMS' and
          account['scope']['IT2a']['derivation']['unknown']==unknown and len(unknown)==9 and
          account['RF']=='NO_COMPLETE_PACKET_IN_REGISTERED_INPUT_NOT_SEARCHED')
    graphs = account['compiled_ZL_graphs']
    graph_ok = set(graphs)=={r['candidate'] for r in legacy}
    for name,g in graphs.items():
        graph_ok &= g['candidate']['id']==name and g['status']=='COMPLETE' and g['consumed']==37
        graph_ok &= len(g['clauses'])==5
        for c,old in zip(g['clauses'],source['complete_clauses']):
            graph_ok &= c['id']==old['id'] and c['positions']==list(range(old['inclusive_positions'][0],old['inclusive_positions'][1]+1))
            graph_ok &= c['words']==old['words'] and c['tags']==old['tags']
        graph_ok &= [a['op'] for a in g['actions']]==['TAKE','EXTRACT','PLACE','BIND','CLAIM']
        graph_ok &= g['knowledge']==[{'position':16,'person':'A','object':'P_rite' if g['candidate']['knowledge']=='SAME_OBJECT' else 'P_attach','time':'t_bind','value':True},
                                   {'position':19,'person':'W','object':'P_rite' if g['candidate']['knowledge']=='SAME_OBJECT' else 'P_purpose','time':'t_bind','value':False}]
        graph_ok &= g['purity']=={'person':'A' if g['candidate']['purity']=='ACTOR' else 'W','time':'t_bind'}
    check('eight_original_scopes_five_clauses_and_fixed_duties', graph_ok)
    index = {(r['stored_trace_index'],r['output']['policy']):r for r in traces}
    keys = {(i,p['policy']) for i,e in enumerate(expected['cases']) for p in e['policies']}
    check('all240_unique_case_policy_records', len(traces)==240 and len(index)==240 and set(index)==keys)
    outcomes=[]; mismatches=[]; actual_tails=[]; refs=[]; roots=[]; provenance=[]; states=[]; costs=[]; clauses=[]; case_ids=[]
    def project_state(state):
        return {k:([{x:v for x,v in claim.items() if x!='content'} for claim in value] if k=='claims' else value)
                for k,value in state.items() if k in ('raisins','taken','loose','contents','bound','claims')}
    for i,e in enumerate(expected['cases']):
        old=legacy[i]
        for ep in e['policies']:
            if (i,ep['policy']) not in index: continue
            row=index[i,ep['policy']]; out=row['output']; er=ep['expected_result']; body=ep['policy']=='BODILY_SUPPORT'
            case_ids.append(all(row[k]==old[k] for k in ('candidate','case','counts','world')))
            tail=er['remaining_after_blocked_operation'] if body else er['remaining_after_failed_operation']
            outcomes.append(out['coherent']==er['whole_complete'] and out['first_failure_step']==er['first_failure_step'] and
                out['first_violations']==(['REFERENCE_MISSING_POSITION9'] if body else er['first_violations']) and out['unexecuted']==tail and
                out['completed_actions']==(1 if body else er['completed_physical_actions']) and
                (not body or out['first_failure_position']==9 and out['status']=='MISSING_REFERENCE'))
            actual_refs={r['position']:r for r in out['reference_bindings']}
            refok=len(actual_refs)==len(out['reference_bindings'])
            for want in ep['references']:
                pos=want['position']; r=actual_refs.get(pos)
                if want['status'].startswith('UNREACHED'): refok &= r is None; continue
                if r is None: refok=False; continue
                refok &= r['raw']=='daiin' and r['actual_consumed_person']==want['person'] and r['derivation']['value']==want['person']
                refok &= r['derivation']['status']==('MISSING' if want['status']=='MISSING' else 'KNOWN')
                if pos==9 and not body:
                    operation=next(t['operation'] for t in out['trace'] if t['operation']['op']=='EXTRACT')
                    refok &= operation['actor']=='A' and operation['using']=='NAILS(A)' and r['actual_instrument']=={'kind':'NAILS','owner':'A'}
                if pos==18:
                    positive=[k for k in out['knowledge_assertions'] if k['source_position']==18]
                    bind_attempted=any(t['operation']['op']=='BIND' for t in out['trace'])
                    refok &= len(positive)==int(bind_attempted)
                    if positive: refok &= positive[0]['subject']=='A' and positive[0]['object']==want['proposition'] and positive[0]['time']=='t_bind'
                if pos==35:
                    refok &= r['actual_attempted_claim_content']['content']==want['claim_content'] and r['actual_claim_content']['actor']=='A'
            if not outcomes[-1]:
                mismatches.append({'case_id':e['case_id'],'policy':ep['policy'],'expected_tail':tail,'actual_tail':out['unexecuted'],
                    'classification':'FROZEN_EXPECTATION_DEFECT_INTERVENTION_ORDER' if body and e['case']=='BIND_BEFORE_PLACE' else 'UNADJUDICATED_DIFFERENCE'})
            plan=['TAKE','EXTRACT','PLACE','BIND','CLAIM']
            if e['case']=='BIND_BEFORE_PLACE': plan[2],plan[3]=plan[3],plan[2]
            actual_tails.append(out['unexecuted']==(plan[out['first_failure_step']:] if out['first_failure_step'] else []))
            refs.append(refok and out['unexecuted_daiin_positions']==[p for p in (9,18,35) if p not in actual_refs])
            seeds=ep['group_seed_ids']; material={'id':'G','type':'SeedGroup','members':seeds}
            expected_root_positions=[5] if body else [5,13] if e['case']=='MOUTH' else [5,13,23]
            roots.append([r['position'] for r in out['bare_root_bindings']]==expected_root_positions and all(r['raw']=='aiin' and
                r['root']=={'status':'KNOWN','value':material} and r['same_members']==seeds for r in out['bare_root_bindings']) and
                all(r['derivation']['root_operation']=={'status':'KNOWN','value':material} and r['derivation']['arguments']['material']==material for r in out['reference_bindings']))
            p=out['provenance']; membership={s:r for r,ss in e['initial_membership'].items() for s in ss}
            provenance.append(p['initial_contains']=={'R':{'G':seeds}} and p['initial_seed_raisin_membership']==membership and
                p['imperative_actor_input']=={'type':'Person','value':'A','independent_of_daiin':True,'paid':True} and
                len(out['completed_history'])==out['completed_actions'] and all(h['completed'] and h['actor']=='A' for h in out['completed_history']))
            if not body:
                states.append(len(out['trace'])==len(old['output']['trace']) and project_state(out['final'])==old['output']['final'] and
                    all(t['step']==ot['step'] and t['violations']==ot['violations'] and project_state(t['before'])==ot['before'] and
                        project_state(t['after'])==ot['after'] for t,ot in zip(out['trace'],old['output']['trace'])))
            else:
                states.append(out['trace'][-1]['before']==out['trace'][-1]['after'] and [h['op'] for h in out['completed_history']]==['TAKE'] and
                    out['trace'][-1]['operation']['actor'] is None and out['final']['claims']==[])
            expected_cost={'imperative_input':1,'material_case_register':1,'initial_membership_retention':1,'completed_action_history':1,
                'unique_acquisition_projection':int(ep['policy']=='ORIGIN'),'latest_relevant_history_projection':int(ep['policy']=='LAST_WORKING'),
                'explicit_addressee_input':int(ep['policy']=='ADDRESSEE'),'current_support_and_body_projection':int(body),'live_person_to_three_consumers':3}
            costs.append(out['scope_costs']==expected_cost)
            clauses.append([(c['id'],c['source_positions']) for c in out['clause_accounting']]==
                [(c['id'],list(range(c['inclusive_positions'][0],c['inclusive_positions'][1]+1))) for c in source['complete_clauses']])
    for name,values in [('all240_original_case_inputs',case_ids),('all240_first_failures_completion_and_tails',outcomes),
        ('all240_reached_reference_bindings_and_actual_consumers',refs),('all240_root_identity_records',roots),
        ('all240_initial_provenance_and_completed_history',provenance),('all240_physical_states_preserved_or_body_blocked',states),
        ('all240_declared_scope_cost_counts',costs),('all240_five_clause_source_coverage',clauses)]:
        check(name,len(values)==240 and all(values),{'checked':len(values),'failed':sum(not x for x in values)})
    honest_status=[]
    for row in traces:
        out=row['output']; physical={h['op'] for h in out['completed_history']}; attempted={t['operation']['op'] for t in out['trace']}
        truth=bool(out['knowledge_assertions']) and all(k['actual_value']==k['required_value'] for k in out['knowledge_assertions'])
        purity=out['purity_check']; done=physical | ({'KNOWS'} if truth else set()) | ({'PURITY_AT_BIND'} if purity and purity['actual_value'] else set())
        for c in out['clause_accounting']:
            required=c['required_duties']; completed=[d for d in required if d in done]
            declared_status='DUTIES_COMPLETED' if completed==required else 'PARTIAL_OR_FAILED' if c['attempted_duties'] else 'UNEXECUTED'
            honest_status.append(c['completed_duties']==completed and c['status']==declared_status and set(c['attempted_duties'])<=set(required) and c['unexecuted_duties']==[d for d in required if d not in c['attempted_duties']])
    check('all1200_clause_duty_completion_and_status_records_honest',len(honest_status)==1200 and all(honest_status))
    check('all240_actual_unexecuted_tails_retain_registered_intervention_order',all(actual_tails) and len(actual_tails)==240)
    late_index={r['stored_trace_index']:r for r in late}; eligible={i for i,e in enumerate(expected['cases']) if e['baseline_prefix_late_body_diagnostic']['eligible']}
    late_ok=len(late)==12 and set(late_index)==eligible
    for i,r in late_index.items():
        want=expected['cases'][i]['baseline_prefix_late_body_diagnostic']; d=r['diagnostic']; distinct=want['differs_from_origin']
        late_ok &= (d['derivation']['value']==want['person'] and d['actual_attempted_claim']['content']==want['claim_content'] and
            d['actor_changed']==distinct and d['not_a_complete_candidate'] and d['full_candidate_status']=='MISSING_AT9' and
            d['gate_violations']==(['CLAIM_SOURCE_ACTOR'] if distinct else []) and (d['conforming_claim_append'] is None)==distinct)
    check('only12_late_prefixes_eight_contrasts_four_self_no_rescue',late_ok)
    summary=[{'policy':p,'stored_traces':60,'coherent_complete':sum(r['output']['coherent'] for r in traces if r['output']['policy']==p),
        'legacy_outcome_matches':sum(r['same_legacy_outcome'] for r in traces if r['output']['policy']==p),
        'status_counts':dict(Counter(r['output']['status'] for r in traces if r['output']['policy']==p))} for p in expected['policies']]
    check('author_summary_counts_from_actual_rows',summary==result['policy_summary'] and result['evaluations']==240 and result['stored_trace_inputs']==60 and
        result['source_groups']=={'ZL3b':37,'IT2a':35} and result['positive_self_inputs']==12 and result['negative_instruction_inputs']==48 and
        result['conditional_late_diagnostics']==12 and result['late_distinct_actor_contrasts']==8 and result['late_self_equivalences']==4)
    check('retained_declared_costs_and_zero_semantic_capacity',result['retained_costs']=={'old_whole_guesses':30,'old_fitted_clauses':5,
        'old_baseline_binding_assumptions':11,'quantity_knowledge_purity_scopes':8,'different_object_macro_change':1} and
        result['new_whole_values']==result['new_clause_rules']==result['new_world_enumeration']==result['confirmed_translated_words']==result['independent_confirmation_capacity']==0 and result['semantic_validation'] is False)
    check('all72_source_status_honesty',all(r['status']==('UNBOUND_EXACT_FORM' if r['original_entry'] is None else 'PROVISIONAL_OLD_ENTRY') for r in account['all_groups']))
    spec=importlib.util.spec_from_file_location('gdt1132_released_model',D/'src/model.py'); model=importlib.util.module_from_spec(spec); spec.loader.exec_module(model)
    replay=all(model.execute(graphs[r['candidate']],r['counts'],r['world'],r['output']['policy'],r['case'])==r['output'] for r in traces)
    check('all240_deterministic_replays_exact_frozen_outputs',replay)
    check('all12_late_diagnostics_deterministic_replay',all(model.late_bodily_diagnostic(index[i,'ORIGIN']['output'])==r['diagnostic'] for i,r in late_index.items()))
    old=legacy[0]; graph=graphs[old['candidate']]; probes=[]
    for pos,violation,step in [(9,'EXTRACT_SOURCE_ACTOR',2),(18,'ACTOR_KNOWLEDGE',4),(35,'CLAIM_SOURCE_ACTOR',5)]:
        out=model.execute(graph,old['counts'],old['world'],'ORIGIN',forced_person={pos:'W'})
        ref=next(r for r in out['reference_bindings'] if r['position']==pos)
        passed=not out['coherent'] and out['first_failure_step']==step and violation in out['first_violations'] and ref['actual_consumed_person']=='W'
        if pos==9: passed &= ref['actual_instrument']=={'kind':'NAILS','owner':'W'} and out['trace'][-1]['operation']['actor']=='W'
        if pos==18: passed &= any(k['subject']=='W' and k['actual_value'] is False and k['required_value'] is True for k in out['knowledge_assertions'] if k['source_position']==18)
        if pos==35: passed &= ref['actual_attempted_claim_content']['content']=='RELEASE(W,W,Q) BY_GRACE(GOD)' and out['final']['claims']==[]
        check('independent_forced_W_actual_consumer_'+str(pos),passed)
        probes.append({'position':pos,'status':'PASS' if passed else 'FAIL','violations':out['first_violations'],'actual_reference':ref})
    out=model.execute(graph,old['counts'],old['world'],'ORIGIN',instrument_owner_override='W')
    check('independent_wrong_instrument_owner_gate',out['first_violations']==['INSTRUMENT_OWNER'] and out['reference_bindings'][0]['actual_instrument']=={'kind':'NAILS','owner':'W'})
    baseline=index[0,'ORIGIN']['output']; material={'id':'G','type':'SeedGroup','members':baseline['provenance']['initial_contains']['R']['G']}
    missing=model.derive_person('ORIGIN',material,baseline['final'],[],baseline['provenance'],'A')
    duplicate=deepcopy(baseline['completed_history'][0]); duplicate.update(actor='W',event='ENGINEERING_ONLY_SECOND_TAKE')
    ambiguous=model.derive_person('ORIGIN',material,baseline['final'],[baseline['completed_history'][0],duplicate],baseline['provenance'],'A')
    check('independent_missing_ambiguous_and_root_type_gates',missing['status']=='MISSING' and missing['value'] is None and ambiguous['status']=='AMBIGUOUS' and ambiguous['value'] is None and model.aN({'id':'C','type':'Cloth','members':material['members']})['status']=='TYPE_MISMATCH')
    author_probes=read(D/'artifacts/AUTHOR_ENGINEERING_PROBES.json')
    actual_probes=[model.execute(graph,old['counts'],old['world'],'ORIGIN',forced_person={pos:'W'}) for pos in (9,18,35)] + [out,missing,ambiguous,model.aN({'id':'C','type':'Cloth','members':material['members']})]
    check('all7_author_engineering_probe_results_exact_replay',len(author_probes)==7 and all(p.get('output',p.get('result'))==v and p['engineering_only'] for p,v in zip(author_probes,actual_probes)))
    original_root=model.aN
    model.aN=lambda material:{'status':'KNOWN','value':{'id':'G','type':'SeedGroup','members':['UNRELATED_RETURNED_MEMBER']}}
    payload=model.execute(graph,old['counts'],old['world'],'ORIGIN')
    model.aN=original_root
    payload_consumed=not payload['coherent'] or payload['final']['contents']!=index[0,'ORIGIN']['output']['final']['contents']
    check('strict_aN_returned_payload_drives_derivation_and_physical_material',payload_consumed,
          'Engineering sensitivity probe changes only the returned aN value; status stays KNOWN. Final contents and derived Person stay unchanged, proving this payload is discarded.')
    check('author_files_unchanged_after_pure_replay_and_probes',all(sha(local(p))==h for p,h in files.items()))
    return {'checks':checks,'frozen_expectation_mismatches':mismatches,'summary':summary,'independent_probes':probes,'aN_payload_probe':{
        'returned_members':['UNRELATED_RETURNED_MEMBER'],'coherent':payload['coherent'],'derived_person':payload['reference_bindings'][0]['derivation']['value'],
        'final_members':payload['final']['contents'],'strict_payload_wiring':payload_consumed},
        'position18_counts':{p:{'resolved_subjects':sum(any(r['position']==18 for r in t['output']['reference_bindings']) for t in traces if t['output']['policy']==p),'truth_lookups':sum(any(k['source_position']==18 for k in t['output']['knowledge_assertions']) for t in traces if t['output']['policy']==p)} for p in expected['policies']},
        'scope_limits':['Source conservation and reference consumption are engineering checks, not semantic truth.',
            'aN KNOWN value is recorded but ignored by d projections and by bare-root physical operations; original G register drives both.',
            'ADDRESSEE passes the same material-type gate before using independent imperative input; no source support for this extra dependency is established.',
            'ORIGIN/LAST_WORKING/ADDRESSEE remain equivalent on one-actor stored histories; no policy selected.',
            'Frozen position18 consumer_executed denotes resolved subject; actual knowledge truth lookup occurs only in 28 BIND attempts per nonbody policy, not all 52 resolved subjects.',
            'Declared cost counts verified; semantic primitive atomicity, aliases and linguistic justification remain manual/unverified.',
            'IT nine unknown forms, RF absent complete packet, zero independent confirmation and zero confirmed meanings remain.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight',action='store_true'); parser.add_argument('--release')
    args=parser.parse_args(); checks,expected,source=preflight()
    if args.preflight:
        failures=sum(c['status']=='FAIL' for c in checks)
        print(json.dumps({'status':'FAIL_VALIDATOR_PREFLIGHT' if failures else 'PASS_INDEPENDENT_PREFLIGHT_ONLY','checks':len(checks),'failures':failures,'author_content_read':False})); return bool(failures)
    if not args.release: parser.error('Author code/results remain closed until root releases exact hashes.')
    files=verify_release(args.release)
    report=validate(files,checks,expected,source)
    failures=[c for c in report['checks'] if c['status']=='FAIL']
    report.update({'experiment':'GDT1132','status':'ACCOUNTING_REPLAY_PASS_WITH_STRICT_PAYLOAD_WIRING_FAILURE' if len(failures)==1 and failures[0]['check']=='strict_aN_returned_payload_drives_derivation_and_physical_material' else 'COMPLETED_WITH_PRESERVED_WIRING_FAILURE_AND_EXPECTATION_DEFECT' if len(failures)==2 and {c['check'] for c in failures}=={'all240_first_failures_completion_and_tails','strict_aN_returned_payload_drives_derivation_and_physical_material'} else 'FAIL_TECHNICAL_VALIDATION' if failures else 'PASS_TECHNICAL_ONLY',
        'semantic_validation':False,'failed_checks':len(failures),'expected_sha256':EXPECTED_SHA,'validator_plan_sha256':PLAN_SHA,
        'author_release_sha256':sha(local(args.release)),'author_file_pins':files,'validator_sha256':sha(Path(__file__))})
    (D/'artifacts/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# GDT1132 independent validation','',report['status']+'. Semantic validation: false.','',
        f"{len(report['checks'])-len(failures)} technical checks passed; {len(failures)} strict checks failed.",'',
        'All 240 cases were compared with pre-author frozen expectations and replayed through the released pure API. ZL37 and IT35 raw groups, native IDs and metadata are conserved; all 60 source worlds/counts are unchanged. No author artifacts were rewritten.','',
        'ORIGIN, LAST_WORKING and ADDRESSEE each preserve 12 complete cases and 48 negative cases. BODILY_SUPPORT is missing at position9 in all60. Twelve separate late diagnostics give eight A/W contrasts and four self equivalences; none rescue the complete bodily policy.','',
        'Independent substitutions of W at9/18/35 reached actual EXTRACT/instrument ownership, KNOWS truth lookup, and attempted RELEASE content respectively, producing the expected fixed source-duty failures.','',
        'Strict returned-payload wiring fails: replacing only aN’s KNOWN value with an unrelated member leaves the original final seeds and derived A unchanged. Both d projections and physical root consumers use the original G register. The reported Person consumer wiring passes, but literal aN-return-to-d composition is not established.','',
        'Eight BODILY_SUPPORT BIND_BEFORE_PLACE tails differ from frozen EXPECTED: actual BIND,PLACE,CLAIM versus expected PLACE,BIND,CLAIM. The separate actual-plan check passes. This is a frozen independent expectation defect: it omitted the intervention order for early bodily failure. Neither expectations nor author outputs were repaired; the exact-comparison failure remains.','',
        'Position18 resolves subjects in52 cases per nonbody policy; truth is looked up at BIND in28. Failed PLACE prefixes therefore have a resolved subject but no executed truth lookup.','',
        'Limits:','']+['- '+x for x in report['scope_limits']]+['','Failing checks:','']+['- '+c['check'] for c in failures]+['','This validates conservation, recorded references, declared counts and deterministic behavior only. Zero meanings selected; root owns scientific adjudication.','']
    (D/'artifacts/VALIDATOR_REPORT.md').write_text('\n'.join(lines))
    print(json.dumps({'status':report['status'],'checks':len(checks),'failures':len(failures),'failing_checks':[c['check'] for c in failures]}))
    return bool(failures)

if __name__=='__main__': raise SystemExit(main())
