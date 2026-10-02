#!/usr/bin/env python3
"""Independent census from six bound snapshots; never imports root run.py.

Only artifacts/VALIDATION.json is written. Original1137 functions are called
without overrides; their type results do not validate English meanings.
"""
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
EXP=Path(__file__).resolve().parents[1]
ROOT=EXP.parents[2]
PLAN='1064e26f59beae2f06dacd2dc50fe5d4ba59028ddc79331a362261670ecee167'
CONTRACT={'METHOD.md':'15ece3a578befe9d4d7fb06c115e5b65aae403ac1f9e7f49c704d35dcf865f48',
 'src/SOURCE.json':'5269c0a5270e795c3404f385644e73dcb3fdcbb5c8cee36a2d5e57fa38cc3f8a',
 'src/PREDICTIONS.json':'464768a943555af9a961fc49d75c9d49ba96bc156ab57ca41ad81112eba7f1c0'}
DOMAIN=frozenset(['chedy','shedy','cheey','sheey'])
REASONS=['LINE_END','INDEX_GAP','UNCERTAIN_SEAM','OUTSIDE_FOUR_LICENSE_DOMAIN','ELIGIBLE']

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(p):
    return json.loads(p.read_text())

def safe(s):
    p=Path(s)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('unsafe bound path')
    return ROOT/p

def classify(left,right):
    # Select the earliest failed predicate, not a successful neighbour subset.
    gates=[right is not None]
    if right is not None:
        gates += [int(right['source_group_index'])==int(left['source_group_index'])+1,
                  (left['right_separator'],right['left_separator'])==('DEFINITE_SPACE','DEFINITE_SPACE'),
                  right['ivtff_group_raw'] in DOMAIN]
    else:
        gates += [False,False,False]
    return next((REASONS[i] for i,ok in enumerate(gates) if not ok),'ELIGIBLE')

def main():
    checks=[]
    def check(name,ok,evidence=None):
        checks.append({'name':name,'pass':bool(ok),'evidence':evidence})
    source=load(EXP/'src/SOURCE.json');lock=load(EXP/'src/PREREG_LOCK.json')
    inputs={b['path']:sha(safe(b['path'])) for b in source['inputs']}
    output_names=['PREDICTION_CHECK.json','OCCURRENCES.json','CASES.json','RESULT.json']
    watched={p:sha(EXP/p) for p in [*lock['hashes'],'src/run.py','artifacts/VALIDATION_PLAN.md',
             *['artifacts/'+n for n in output_names]]}
    check('unchanged_registered_contract_plan',all(watched[s]==h for s,h in CONTRACT.items()) and watched['artifacts/VALIDATION_PLAN.md']==PLAN)
    check('preregistration_lock_pins',all(watched[p]==h for p,h in lock['hashes'].items()),{'documented_lock_utc':lock['utc'],'public_predata_timestamp_certified':False})
    check('all_twelve_bound_input_pins',all(inputs[b['path']]==b['sha256'] for b in source['inputs']),inputs)
    scope=load(safe(next(p for p in inputs if p.endswith('/SPEC.json'))))
    check('179_owned_selectors_closed_scope',len(scope['allowed_selectors'])==179 and not any(p.startswith('f84') or p=='f116v' for p in scope['allowed_selectors']) and source['exclude_leaf']==83 and source['reserves']=='CLOSED')
    corepath=safe(next(p for p in inputs if p.endswith('/src/core.py')))
    module_spec=importlib.util.spec_from_file_location('independent_fixed1137',corepath)
    core=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(core)
    predictions=load(EXP/'src/PREDICTIONS.json')
    def call(surface,identity):
        recipe=core.lexical_nominal(surface)
        try:
            product=core.qokedy(recipe,identity)
        except ValueError as error:
            return {'outcome':'REJECT','recipe':recipe,'product':None,'error':str(error)},type(error).__name__
        return {'outcome':'ACCEPT','recipe':recipe,'product':product,'error':None},None
    truth={};exception_types={}
    for word in sorted(DOMAIN):
        truth[word],exception_types[word]=call(word,'PREDICTION_ONLY')
    check('four_frozen_predictions_exact_and_original_licenses',set(predictions)==DOMAIN and set(core.LICENSES)==DOMAIN and all(truth[w]['outcome']==predictions[w]['prediction'] and truth[w]['recipe']['stage']==predictions[w]['stage'] for w in DOMAIN))
    check('source_recipe_rejections_are_actual_ValueError',all(exception_types[w]=='ValueError' for w in ['cheey','sheey']) and all(exception_types[w] is None for w in ['chedy','shedy']),exception_types)
    check('complete_four_prediction_return_fields',truth==load(EXP/'artifacts/PREDICTION_CHECK.json'))
    independent=[];contexts={};den=defaultdict(Counter);snapshot_counts={};outside=defaultdict(Counter)
    structure_errors=[];all_group_ids=set();line_ids=set()
    snapshots=[p for p in inputs if '/SOURCE_' in p and p.endswith('.json')]
    check('all_six_snapshots_selected',len(snapshots)==6)
    for path in snapshots:
        data=load(safe(path));name=Path(path).stem;phase,edition=name.removeprefix('SOURCE_').split('_',1)
        columns=data['group_columns'];snapden=Counter()
        if columns!=scope['group_columns']:structure_errors.append([name,'group_columns'])
        for line in data['lines']:
            m=line['metadata'];page=m['page'];leaf=int(re.match(r'^f([0-9]+)',page).group(1))
            panel=den[edition];panel['snapshot_lines']+=1;snapden['snapshot_lines']+=1
            if page not in scope['allowed_selectors'] or page not in scope['partitions'][phase] or m['edition']!=edition:
                structure_errors.append([name,m['locus'],'scope_metadata'])
            identity=(edition,m['locus'])
            if identity in line_ids:structure_errors.append([name,m['locus'],'duplicate_line'])
            line_ids.add(identity)
            # Reject the whole development leaf before inspecting candidate text.
            if leaf==83:
                panel['development_leaf_lines']+=1;snapden['development_leaf_lines']+=1
                continue
            if m['kind']!='P':
                panel['nonprose_lines']+=1;snapden['nonprose_lines']+=1
                continue
            panel['prose_lines']+=1;snapden['prose_lines']+=1
            groups=[]
            for row in line['groups']:
                if len(row)!=len(columns):structure_errors.append([name,m['locus'],'field_width'])
                g=dict(zip(columns,row));groups.append(g)
                if g['source_group_id'] in all_group_ids:structure_errors.append([name,g['source_group_id'],'duplicate_group'])
                all_group_ids.add(g['source_group_id'])
            positions=[int(g['source_group_index']) for g in groups]
            if positions!=sorted(set(positions)):structure_errors.append([name,m['locus'],'native_order'])
            for left,right in zip(groups,groups[1:]+[None]):
                if left['ivtff_group_raw']!='qokedy':continue
                reason=classify(left,right)
                panel['qokedy_occurrences']+=1;panel[reason]+=1
                snapden['qokedy_occurrences']+=1;snapden[reason]+=1
                record={'edition':edition,'phase':phase,'page':page,'leaf':leaf,'locus':m['locus'],
                        'left':left,'right':right,'classification':reason}
                independent.append(record)
                if reason=='ELIGIBLE':contexts[left['source_group_id']]={'metadata':m,'complete_line_groups':groups}
        snapshot_counts[name]=dict(snapden)
    check('snapshot_scope_ids_field_width_native_order',not structure_errors,structure_errors)
    recorded_occurrences=load(EXP/'artifacts/OCCURRENCES.json');recorded_cases=load(EXP/'artifacts/CASES.json')
    key=lambda r:r['left']['source_group_id']
    ownmap={key(r):r for r in independent};rootmap={key(r):r for r in recorded_occurrences}
    check('all_classified_occurrences_exact_no_duplicates',len(ownmap)==len(independent) and len(rootmap)==len(recorded_occurrences) and ownmap==rootmap,dict(Counter(r['classification'] for r in independent)))
    check('per_reader_native_occurrence_order_retained',all([key(r) for r in independent if r['edition']==ed]==[key(r) for r in recorded_occurrences if r['edition']==ed] for ed in scope['editions']))
    expected_cases={};case_exceptions={}
    for r in independent:
        if r['classification']!='ELIGIBLE':continue
        outcome,error_type=call(r['right']['ivtff_group_raw'],key(r));case_exceptions[key(r)]=error_type
        expected_cases[key(r)]={**r,**outcome,**contexts[key(r)]}
    recorded_case_map={key(r):r for r in recorded_cases}
    check('all_eligible_cases_full_context_and_actual_return_fields',len(recorded_cases)==len(recorded_case_map)==len(expected_cases) and expected_cases==recorded_case_map)
    check('every_case_actual_prediction_and_exception_type',all(r['outcome']==predictions[r['right']['ivtff_group_raw']]['prediction'] and (case_exceptions[k]=='ValueError' if r['outcome']=='REJECT' else case_exceptions[k] is None) for k,r in expected_cases.items()))
    reconstructed_panels={}
    for edition in scope['editions']:
        cases=[r for r in expected_cases.values() if r['edition']==edition];counts=Counter()
        for r in cases:counts[r['outcome']]+=1;counts[r['right']['ivtff_group_raw']]+=1
        decision='CONTRADICTED_TRANSFER_ASSUMPTION' if counts['REJECT'] else 'COMPATIBLE_IN_FIXED_DOMAIN' if cases else 'NO_CAPACITY'
        reconstructed_panels[edition]={'denominators':dict(den[edition]),'counts':dict(counts),'decision':decision,
            'eligible_leaves':sorted({r['leaf'] for r in cases}),'reject_leaves':sorted({r['leaf'] for r in cases if r['outcome']=='REJECT'})}
    result=load(EXP/'artifacts/RESULT.json');global_reject=any(r['outcome']=='REJECT' for r in expected_cases.values())
    decision='CONTRADICTED_TRANSFER_ASSUMPTION' if global_reject else 'COMPATIBLE_IN_FIXED_DOMAIN' if expected_cases else 'NO_CAPACITY'
    check('all_per_reader_denominators_counts_decisions',reconstructed_panels==result['panels'],reconstructed_panels)
    check('global_case_leaf_arithmetic_and_decision',result['decision']==decision and result['total_reader_cases']==len(expected_cases)
          and result['unique_eligible_physical_leaves']==sorted({r['leaf'] for r in expected_cases.values()})
          and result['unique_reject_physical_leaves']==sorted({r['leaf'] for r in expected_cases.values() if r['outcome']=='REJECT'}))
    continuation={}
    for ed in scope['editions']:
        rr=[r for r in recorded_cases if r['edition']==ed]
        first=next((i for i,r in enumerate(rr) if r['outcome']=='REJECT'),None)
        continuation[ed]={'first_rejection_index':first,'subsequent_cases':len(rr)-first-1 if first is not None else None}
    check('complete_census_continues_after_countercases',ownmap==rootmap and expected_cases==recorded_case_map,continuation)
    check('honest_joint_binding_test_ceiling',result['old1137']=='UNCHANGED_LOCAL_C0' and result['full876_transfer']=='NOT_TESTED' and result['confirmed_words']==result['independent_meaning_confirmation_capacity']==0 and result['significance_claim'] is False)
    check('root_artifacts_core_and_all_inputs_unchanged',watched=={p:sha(EXP/p) for p in watched} and inputs=={p:sha(safe(p)) for p in inputs})
    shared=Counter(r['locus'] for r in expected_cases.values())
    output={'experiment':'GDT1146','validator_sha256':sha(Path(__file__)),'frozen_plan_sha256':PLAN,
       'accounting_pass':all(c['pass'] for c in checks),'checks':checks,'snapshot_census':snapshot_counts,
       'independent_decision':decision,'classified_qokedy':len(independent),'eligible_reader_cases':len(expected_cases),
       'accepted_cases':sum(r['outcome']=='ACCEPT' for r in expected_cases.values()),
       'rejected_cases':sum(r['outcome']=='REJECT' for r in expected_cases.values()),
       'shared_eligible_locus_counts':dict(shared),'unique_eligible_loci':len(shared),
       'shared_rejection_locus_counts':dict(Counter(r['locus'] for r in expected_cases.values() if r['outcome']=='REJECT')),
       'actual_rejection_ids':[k for k,r in expected_cases.items() if r['outcome']=='REJECT'],
       'classification_counts':dict(Counter(r['classification'] for r in independent)),
       'scope_counts':{ed:dict(d) for ed,d in den.items()},'input_pins':inputs,'root_artifact_pins':watched,
       'limits':['The rejection concerns new immediate-right binding H jointly with unchanged1137 core, not the local1137 result or QOKEDY meaning alone.',
         'Three reader rejections at one locus/physical leaf are alternatives of one manuscript, not independent counterexamples.',
         'DISCOVERY/EVALUATION labels are inherited exposed development metadata, not new confirmation partitions.',
         'Full retained physical lines are context, not complete paragraph readings or parsed argument syntax.',
         'Outside-domain neighbours and uncertain seams remain untested; no coercion/new meaning or domain repair.',
         'No native visual truth, source identification, semantic confirmation, significance, scored edge or reserve eligibility.'],
       'confirmed_words':0,'significance_claim':False,'reserves':'CLOSED'}
    (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'accounting_pass':output['accounting_pass'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['pass']],
       'classified':len(independent),'cases':len(expected_cases),'accepted':output['accepted_cases'],'rejected':output['rejected_cases'],'decision':decision}))
    return 0 if output['accounting_pass'] else 1

if __name__=='__main__':
    raise SystemExit(main())
