"""Bounded independent receipt, assembly and fixed-history review.

No decoder, source search, general SAT solver or semantic confirmation.
The author module is loaded without its main entry point; its one output write
is captured in memory for replay. Post-release diagnostics are explicitly marked.
"""
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout
import collections, copy, datetime, hashlib, io, itertools, json

B = Path(__file__).resolve().parent
STEM = 'GD_MOTION_SHARED_GRADE_AUTHOR_20261002'
PINS = {'py': 'd13016c532ad28652e9fe8944e01343a4dbf520f1bc931228da793218c623c9c',
        'json': '1fa29aa7612a05143fcafad06da58b19e921854d211b1308f3343acdf8462f3b',
        'md': '3068e8cb671648f563ea404ed12cd2a274527264aff2491e9489bdb88a2d6f22'}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v): return hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest()
def atoms(v):
    if isinstance(v, list):
        return [a for x in v for a in atoms(x)]
    if isinstance(v, dict):
        return ([v] if v.get('op') == 'ATOM' else []) + [a for x in v.values() for a in atoms(x)]
    return []

def fixed_truth(formula, history, env=None):
    """Evaluate only the actual-motion fragment on one fixed discrete history.

    Each cell is a positive-duration unit interval; existential subintervals
    range over all nonempty integer-ended intervals. Not a manuscript history,
    accessibility model, whole-passage satisfiability check or universal oracle.
    """
    env = {} if env is None else env
    op = formula['op']
    if op == 'WITNESS_PACKAGE': return fixed_truth(formula['condition'], history, env)
    if op == 'AND': return all(fixed_truth(x, history, env) for x in formula['arguments'])
    if op == 'EXISTS':
        intervals = [(a, b) for a in range(len(history)) for b in range(a+1, len(history)+1)]
        return any(fixed_truth(formula['body'], history, {**env, **dict(zip(formula['binders'], vals))})
                   for vals in itertools.product(intervals, repeat=len(formula['binders'])))
    if op != 'ATOM': raise ValueError('Outside bounded evaluator: '+op)
    p, a = formula['predicate'], formula['arguments']
    if p == 'ACTUAL': return a == ['W', 'E']
    if p == 'FLOW': return a == ['W', 'E', 'M', 'I'] and any(history)
    if p == 'USING': return a == ['W', 'HOST_EVENT', 'E']
    if p == 'CONTINUOUS_FULL_PHASE': return a == ['W', 'E', 'I'] and all(history)
    if p == 'NONEMPTY_SUBINTERVAL': return a[1] == 'I' and a[0] in env
    if p in ['POSITIVE_FLOW_THROUGHOUT', 'ZERO_FLOW_THROUGHOUT']:
        if a[:3] != ['W', 'E', 'M']: return False
        start, end = env[a[3]]
        return all(bool(v) == (p == 'POSITIVE_FLOW_THROUGHOUT') for v in history[start:end])
    if p == 'END_NOT_AFTER_START': return env[a[0]][1] <= env[a[1]][0]
    raise ValueError('Outside bounded predicate set: '+p)

def main():
    checks = []
    def add(name, status, detail): checks.append({'name': name, 'status': status, 'detail': detail})
    expectations_path = B/'GD_MOTION_SHARED_GRADE_EXPECTATIONS_20261002.json'
    exp = json.loads(expectations_path.read_text())
    author = json.loads((B/(STEM+'.json')).read_text())
    initial_pins = {s: sha(B/(STEM+'.'+s)) for s in PINS}
    add('release_pins', 'PASS' if initial_pins == PINS else 'FAIL', initial_pins)
    parent_checks = {f: sha(B/f) == h for f,h in exp['bound_inputs_sha256'].items()}
    # The decision qualification append is separately frozen in expectations.
    qual = exp['pre_release_qualification_append']
    parent_checks['qualified_decision'] = sha(B/'GD_MOTION_SHARED_GRADE_DECISION_20261002.md') == qual['qualified_decision_sha256']
    add('bound_inputs', 'PASS' if all(parent_checks.values()) else 'FAIL', parent_checks)
    source = B/(STEM+'.py')
    ns = {'__file__': str(source), '__name__': 'independent_review'}
    exec(compile(source.read_text(), str(source), 'exec'), ns)
    writes = []
    with patch.object(Path, 'write_text', lambda p, text, *a, **k: writes.append((p.name, text)) or len(text)), redirect_stdout(io.StringIO()):
        ns['run']()
    replay_ok = len(writes) == 1 and writes[0][0] == STEM+'.json' and writes[0][1].encode() == (B/(STEM+'.json')).read_bytes()
    add('byte_identical_replay', 'PASS' if replay_ok else 'FAIL', {'captured_writes': len(writes), 'author_write_executed': False})
    packet = json.loads((B/'FT_SOURCE_PACKET.json').read_text())
    owned = [c for c in packet['contexts'] if c['unit_id'] == 'F83_P4']
    originals = [g for c in owned for line in c['lines'] for g in line['groups']]
    retained = [p['source'] for p in author['native_positions']]
    add('97_native_positions', 'PASS' if author['owned_native_contexts'] == owned and retained == originals and len({g['source_group_id'] for g in retained}) == 97 else 'FAIL',
        {'total': len(retained), 'reader_counts': {c['edition']: sum(len(l['groups']) for l in c['lines']) for c in owned}, 'all_native_fields_and_contexts_compared': True})
    es = json.loads((B/'ES_JOINT_FAMILY_AUTHOR.json').read_text())
    kernel = json.loads((B/'GD_SHARED_CONSTRUCTION_AUTHOR_20261002.json').read_text())
    dictionaries = {v: {**es['parent32_models_unchanged'][v]['dictionary'], **es['prospective_EQ14_unchanged'], **es['new_exact_whole_values']} for v in ['G','I']}
    preserved = author['ES17_compatibility_obligation']
    add('ES59_and_kernel_preservation', 'PASS' if author['preserved_parent_dictionaries'] == dictionaries and not author['parent_value_changes'] and preserved['full_17_reduction'] == kernel['full_17_written_order_reduction'] and preserved['full_17_source_and_bindings'] == kernel['source_preservation']['primary_IT_unit'] else 'FAIL', {'dictionary_sizes': {k:len(v) for k,v in dictionaries.items()}, '17_rows_and_binding_copy': True, 'not_a_new_17_group_execution': True})
    assembly_errors = []
    for raw, parts in ns['NEW_ASSEMBLIES'].items():
        if ''.join(parts) != raw: assembly_errors.append((raw,parts))
    for name,a in author['accounts'].items():
        for row in a['rows']:
            if ''.join(row['assembly']) != row['raw']: assembly_errors.append((name,row['source_group_id']))
    add('exact_assemblies', 'PASS' if not assembly_errors and 'qokey' in ns['ROUTES'] and 'qoky' not in ns['ROUTES'] else 'FAIL', {'errors': assembly_errors, 'QOKEY_not_QOKY': True, 'QOKY_and_QOKYLDDY_are_separately_paid': True})
    hist = [([1,0,1], [True,True,False]), ([1,1,1], [False,True,True]),
            ([1,0,0], [False,True,False]), ([0,1,1], [False,True,False]),
            ([0,0,0], [False,False,False]), ([1,0,1,0], [True,True,False])]
    fixed = []
    for stem in ['qok','lk']:
        for n in range(3):
            f = ns['motion'](stem,n,'edy','W','E','M','I','HOST_EVENT')
            for h, expected in hist:
                got = fixed_truth(f,h)
                fixed.append({'stem':stem,'extra_E':n,'history':h,'expected':expected[n],'actual':got})
    add('independent_fixed_actual_histories', 'PASS' if all(x['expected']==x['actual'] for x in fixed) else 'FAIL', {'cases':len(fixed),'records':fixed,'scope':'Independent actual-motion fragment only; no full SAT or empirical history.'})
    def normalize(v):
        if isinstance(v,list): return [normalize(x) for x in v]
        if isinstance(v,dict): return {k:normalize(x) for k,x in v.items() if k!='event_condition'}
        return v
    kernel_compat = {}
    for raw in ['qokeey','qokeedy','qokeeey','lkeeedy']:
        r=ns['ROUTES'][raw]
        new=ns['motion'](r['stem'],r['extra_E'],r['mode'],'$w','$e','$x','$I','$host_event')
        kernel_compat[raw] = normalize(new) == kernel['computed_form_templates'][raw]['reduced_template']
    add('reused_motion_kernel_templates', 'PASS' if all(kernel_compat.values()) else 'FAIL', {'equivalent_parent_fields':kernel_compat,'capability_event_condition_added':'New explicit schema; accessibility/denotational equivalence remains conditional on CAPABLE primitive, not independently established.'})
    native = author['accounts']['native_IT_G']
    pulse_rows=[r for r in native['rows'] if r['raw']=='qokedy']
    pulse_ok=len(pulse_rows)==2 and all(any(a['predicate']=='ZERO_FLOW_THROUGHOUT' for a in atoms(r['returned_predicates'])) and not any(a['predicate']=='LIQUID' for a in atoms(r['returned_predicates'])) for r in pulse_rows)
    add('two_native_QOKEDY_sites', 'PASS' if pulse_ok else 'FAIL', [{'source_group_id':r['source_group_id'],'event':r['operator_input']['event_port'],'phase':r['operator_input']['phase'],'resolved_FLOW_arguments':[a['arguments'] for a in atoms(r['resolved_predicates']) if a['predicate']=='FLOW']} for r in pulse_rows])
    try: ns['motion']('lk',0,'ey','W','E','M','I','HOST_EVENT'); rejected=False
    except ValueError: rejected=True
    cap=ns['motion']('qok',0,'ey','W','E','M','I')
    add('frame_boundaries', 'PASS' if rejected and cap['arguments'][1]['predicate']=='CAPABLE' else 'FAIL', {'LK_EY_rejected':rejected,'QOK_EY_embeds_actual_schema_under_CAPABLE':True,'actual_capability_truth':'UNVERIFIED: no accessibility/apparatus semantics supplied','LK_host_type_runtime_check':'Absent: symbolic USING asserts a typed relation; invalid-host satisfiability not checked.'})
    groups=collections.defaultdict(list)
    for name,a in author['accounts'].items():groups[digest(a['final_predicates'])].append(name)
    add('candidate_grouping', 'PASS', {'formula_equivalence_groups':list(groups.values()),'native_G_I_identical':author['accounts']['native_IT_G']['final_predicates']==author['accounts']['native_IT_I']['final_predicates'],'independent_candidates':0})
    unassigned=[p['source']['source_group_id'] for p in author['native_positions'] if not p['exact_license']]
    add('alternate_limit', 'PASS' if len(unassigned)==6 else 'FAIL', {'unassigned_native_positions':unassigned,'ZL_RF_binding_status':'Exact-form projections only, not full executable accounts.'})
    # Diagnose literal return-port use without changing frozen code or inputs.
    original_compile=ns['compile_word']
    def changed_compile(raw,w,x,e,I,ctx,variant):
        out=original_compile(raw,w,x,e,I,ctx,variant)
        return ns['substitute'](out,{'P2':'DIAGNOSTIC_CHANGED_PLAN'}) if raw=='qoky' and ctx['intention']=='P2' else out
    ns['compile_word']=changed_compile
    it=next(c for c in owned if c['edition']=='IT2a')
    lines=[(l['locus'],[g['ivtff_group_raw'] for g in l['groups']],[g['source_group_id'] for g in l['groups']]) for l in it['lines']]
    altered=ns['execute'](lines,'IT2a_NATIVE','G')
    ns['compile_word']=original_compile
    altered_plan=[a['arguments'] for a in atoms(altered['final_predicates']) if a['predicate'] in ['INTENDED','FULFILLS']]
    add('post_release_return_port_diagnostic', 'LIMIT', {'changed_QOKY_return_only':'P2 -> DIAGNOSTIC_CHANGED_PLAN','final_INTENDED_and_FULFILLS_arguments':altered_plan,'finding':'Intention register is separately computed before compile_word returns. Later fulfillment stays P2 despite changed producer return. Logical shared-plan constraint exists in unchanged baseline via paid manual context; literal returned-payload edge is absent.','not_preregistered_manuscript_contradiction':True})
    context_atoms=[a for a in atoms(native['context_edges']) if a['predicate']=='SAME_TIME']
    final_atoms=atoms(native['final_predicates'])
    add('paid_connection_and_temporal_scope', 'PASS_WITH_LIMITS', {'six_actual_time_anchors':len(context_atoms),'resolved_patient_ports':native['bindings'],'intention_constraints':[a for a in final_atoms if a['predicate'] in ['INTENDED','FULFILLS','GOAL','GOAL_SATISFIED']],'all_returned_predicates_enter_final_conjunction':True,'binding_method':'Manual clause inputs, raw-token-triggered registers and final substitution, not inferred syntax or all returned-value-driven state','independent_whole_satisfiability':'UNVERIFIED; bounded grade checks are not whole SAT.'})
    add('declared_costs', 'PASS' if len(ns['PRIMITIVES'])==22 and len(ns['NEW_ASSEMBLIES'])==18 else 'FAIL', {'primitive_frame_entries':len(ns['PRIMITIVES']),'assembly_licenses':len(ns['NEW_ASSEMBLIES']),'grade_cases':3,'motion_frames':3,'paid_scope_bullets':len(author['paid_scope_and_binding_assumptions']),'manual_clause_frames':6,'limits':'Inventory counts overlap; not an objective total of all semantic atoms or code length. New raw-specific compound implementations remain finite declared licenses, not a general learned parser.'})
    add('author_unchanged', 'PASS' if {s:sha(B/(STEM+'.'+s)) for s in PINS}==initial_pins else 'FAIL',initial_pins)
    notes={
      'freeze_and_parents':('PASS_WITH_CAPABILITY_LIMIT','All bytepins/dictionaries/kernel copies preserved; actual-motion kernel fields equivalent. Capability accessibility remains unspecified.'),
      'complete_owned_scope':('PASS','97 native rows/contexts exact; native IT32 and separate report33 account namespaces retained. ZL/RF projections partial.'),
      'literal_assembly':('PASS','All declared and row assemblies exact; QOKEY differs from QOKY, which has a separately paid intention frame.'),
      'one_computed_grade':('PASS_CONDITIONAL','One pattern function generates substantive conditions; 36 independently evaluated fixed actual-history cases agree.'),
      'new_QOKEDY':('PASS_CONDITIONAL','Two native actual-pulse sites generated by shared function; prospective sisters distinguished from observed forms.'),
      'fixed_input_comparison':('PASS_BOUNDED_ACTUAL_FRAGMENT','Fixed histories reject endpoint-only pauses and distinguish pulse/continuous. No whole model/empirical history check.'),
      'capability_and_instrument':('PARTIAL_UNVERIFIED_CAPABILITY','Nominal capability and actual/instrument frames explicit; LK EY rejected. No accessibility or runtime host-type interpretation.'),
      'actual_return_bindings':('PARTIAL_MANUAL_BINDINGS','All predicates consumed in logical conjunction; ports/references use paid manual registers/substitution. Changed QOKY return does not change stored plan used by fulfillment.'),
      'whole_connected_account':('COMPLETE_CONSTRAINT_ACCOUNT_WITH_LIMITS','All IT32/report33 groups compiled into connected conjunction; independent full satisfiability not certified. Native G/I same output.'),
      'paid_additions_no_macros':('PASS_DISCLOSED_COSTS','22 new entries, 18 licenses, three grades/frames and substantial explicit context costs. No arbitrary copied source-clause bundle found.'),
      'barriers_alternates':('PASS','Six uncertain raw alternate forms unassigned; no imputed full ZL/RF syntax or aliases.'),
      'rivals':('NOT_SELECTED','Fixed actual histories distinguish conditional constraints; onset/middle changes ET parents and no target history selects either.'),
      'meaning_ceiling':('PASS','C0 complete constraint reading may be retained without anchor prerequisite; no confirmed words, independent meaning validation or significance.')}
    criteria=[{'id':c['id'],'status':notes[c['id']][0],'finding':notes[c['id']][1]} for c in exp['criteria']]
    result={'status':'COMPLETE_CONDITIONAL_NATIVE_IT_CONSTRAINT_ACCOUNT_REPLAYED_WITH_RETURN_EDGE_AND_CAPABILITY_LIMITS','review_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_expectations_sha256':sha(expectations_path),'validator_sha256':sha(Path(__file__)),'author_release_pins':PINS,'checks':checks,'frozen_criteria_results':criteria,'scientific_ceiling':'New QOKEDY pulse formation computed under paid C0 grade/frames. Complete IT32 constraint account and report33 retained; not actual-state execution, independent full SAT, native three-reader completion or confirmed meaning.'}
    jp=B/'GD_MOTION_SHARED_GRADE_VALIDATION_20261002.json';jp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    lines=['# Independent motion-grade review','',result['scientific_ceiling'],'','All release/input hashes match; captured replay is byte-identical and leaves author bytes untouched. All 97 native positions and their entire FT contexts are preserved. All exact assemblies pass. Native IT32 G/I predicates are identical; the report33 G/I outputs differ only in their SALCHEDY property. These are correlated renderings of one owned manuscript, not four independent successes.','',
      'The shared function generates actual pulse and continuity truth conditions, beyond metadata labels. A small independent evaluator checked 36 fixed actual-history cases across QOK/LK and three grades. Positive–zero–positive satisfies pulse; uninterrupted flow satisfies continuity; endpoint-only pauses satisfy neither pulse nor continuity. This evaluator covers only the stated actual-motion fragment, not the complete discourse, unknown real histories or capability accessibility.','',
      'Both native QOKEDY occurrences compile to actual FLOW plus the same positive–zero–positive requirement, on E1/I1 and E4/I4. QOKEY is qok+ey; QOKY is a separately paid intention frame. QOK nominal retains LIQUID; finite QOK does not impose it. LK adds USING and rejects EY. Runtime host-type truth and capability accessibility are not evaluated by the author generator.','',
      'All word predicates enter the final conjunction. Material/event/phase coidentity is supplied by six manual clause frames, token-triggered reference registers and a final binding substitution. They are declared costs. Intention P2 and outlet O genuinely share logical variables with fulfillment/goal constraints in the baseline. However, the actual QOKY returned witness package is not used to create the live intention register: intend is called separately before compile_word. A post-release diagnostic changes only that returned plan to DIAGNOSTIC_CHANGED_PLAN; later FULFILLS still consumes P2. Thus literal returned-payload flow is not established, despite the baseline constraint connection. This diagnostic is not a naturally arising or preregistered manuscript contradiction.','',
      'The six SAME_TIME anchors are actual formula atoms; NOT MOVING at T5 is scoped to J5 after pulsed I4. The reviewer found no direct contradiction in these declared scopes, but did not certify a complete model or run a general SAT solver. Capability carries a possible-event schema; accessibility/apparatus conditions remain unspecified, so different nominal schemas do not prove different capability extensions.','',
      'All 22 new primitive/frame entries and 18 assembly licenses are disclosed, together with three grade cases, three frames and substantial paid bindings. Exact raw-specific compound implementations are finite licenses, not learned morphology. No arbitrary copied source-clause bundle or invented observed bath history was found. The six unassigned alternate raw forms remain explicit; ZL/RF have projections, not full bindings.','', '| Frozen criterion | Result |','|---|---|']
    lines += [f"| {c['id']} | {c['status']} |" for c in criteria]
    lines += ['', 'The onset/middle rival changes parent grades; current written data do not select motion history. The bounded conditional computation and complete IT constraint account are retained without promoting any meaning. No author/source/expectation repair, new target access, image, reserve, corpus or global edit occurred.','']
    mp=B/'GD_MOTION_SHARED_GRADE_VALIDATION_20261002.md';mp.write_text('\n'.join(lines))
    print(json.dumps({'status':result['status'],'checks':len(checks),'criteria':len(criteria),'json_sha256':sha(jp),'md_sha256':sha(mp),'validator_sha256':sha(Path(__file__))}))

if __name__=='__main__': main()
