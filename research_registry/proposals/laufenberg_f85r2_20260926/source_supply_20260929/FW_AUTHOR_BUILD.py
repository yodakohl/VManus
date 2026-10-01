"""Write one authored, literal C0 annotation; no search, fitting or raw acquisition.

Reads only the root-bound discovery packet. This is the author's annotation
materializer, not an independent validator or a general manuscript decoder.
"""
import csv
import hashlib
import json
import re
from pathlib import Path

D = Path(__file__).parent
packet = json.loads((D / 'FW_DISCOVERY_PACKET.json').read_text())
assert hashlib.sha256((D/'FW_DISCOVERY_PACKET.json').read_bytes()).hexdigest() == '518d03e887d788e4b3da0ec702d7df95c338cb71f14a40faad9d65be8d2e59e1'
controls = {
    'tchedy':'REGISTER', 'pchedas':'REGISTER', 'pchedar':'REGISTER',
    'pchor':'REGISTER', 'qokeed':'REGISTER', 'qokaiin':'DECLARE_WORKPIECE',
    'qokedy':'GRIND', 'qokeedy':'KNEAD', 'qokeey':'PRESS',
    'chedy':'SHAPE', 'shedy':'PREPARE', 'qokal':'NOTE',
    'shcthy':'CHECK_RECORD', 'shedal':'STORE_RECORD',
}
forms = sorted(packet['exact_whole_priors'])
names = [w for w in forms if w not in controls]
lexicon = {w:{'entry_id':'FW_W_' + w, 'whole':w,
    'value':controls.get(w,'OPAQUE_MATERIAL_KIND_MENTION'),
    'type': 'Operator' if w in controls else 'MaterialKindName',
    'cost':1, 'frame':'INSTRUCTION' if w in controls else 'FINITE_CATALOGUE',
    'confirmed':False} for w in forms}
rules = [
 ('R01','Each bounded unit begins with an empty paragraph catalogue; only the explicitly enumerated nominal whole values enter it.'),
 ('R02','A finite-catalogue nominal mention declares Kind NAME:<raw> and Spec SPEC:<raw> with exact literal identity; it does not allocate material or change the workpiece.'),
 ('R03','Recognized instruction entries interrupt the nominal frame; after each complete instruction the same finite catalogue frame is again available. Unknown/marked values never enter it.'),
 ('R04','Previous-unit mode records written instructions as a Plan, without physically executing them. Current-unit mode symbolically executes its instructions.'),
 ('R05','The one formal slot x:MaterialInstance is declared by written qokaiin in previous mode; repeated declarations co-refer to x.'),
 ('R06','A previous written instruction may precede the slot declaration; its x reference stays pending until qokaiin. Closure requires the declaration and no unresolved source.'),
 ('R07','Current first qokaiin means take a workpiece: construct a generic unnamed MaterialKind, its Spec, and a fresh MaterialInstance from this written expression.'),
 ('R08','Current later qokaiin co-refers to that same unit workpiece; it neither reallocates nor resets state or output.'),
 ('R09','Current instructions before the first qokaiin are deferred in source order; first qokaiin discharges this queue. Missing introduction blocks the unit.'),
 ('R10','Every unary treatment or REGISTER instruction receives the declared workpiece x. This omitted-operand convention is paid, not a written biological name.'),
 ('R11','REGISTER records the current state of the same workpiece; it does not reload an original physical state or allocate a portion.'),
 ('R12','GRIND/KNEAD/PRESS/SHAPE/PREPARE are unary authored treatment instructions, with one action and one fresh event/result record each. No second ingredient or tool is implicit.'),
 ('R13','NOTE/CHECK_RECORD/STORE_RECORD consume the immediately previous ResultRecord and emit a fresh note/check/store ResultRecord about the same material. They do not prove achieved physical quality.'),
 ('R14','Every treatment result preserves material identity and appends its declared action to symbolic intended-action history; observed efficacy is never inferred.'),
 ('R15','The previous unit closes and publishes its Plan only at the paid unit-end convention, after all groups and slots resolve. ZL/IT use their native end; RF uses the disclosed external window end.'),
 ('R16','The Plan contains every recognized previous instruction in order, except formal-slot declarations; nominal catalogue descriptions remain source-linked Plan documentation, not captured ingredient arguments.'),
 ('R17','Exactly one global whole-Plan stage policy: all recorded executable steps, in order. No selected subset, stage repair or inherited fire operation.'),
 ('R18','The reference domain is only the closed Plan of the immediately preceding admitted complete unit; no older unit/current result is considered. Singleton domain needs no truth-aware tie-break.'),
 ('R19','Only adjacent raw chey tal in the same locus across matching DEFINITE_SPACE or UNCERTAIN_SMALL_SPACE is the CALL construction. Else each whole retains its finite nominal value, if that exact value is in the whitelist.'),
 ('R20','The chey portion opens a pending call; tal closes it and retrieves the previous Plan. A missing Plan or input stops the dependent trace at tal.'),
 ('R21','CALL substitutes current x into the single formal slot, captures no constants, preserves all step order, and generates fresh Call/Execution/Event/Result identities.'),
 ('R22','Each call step returns a ResultRecord; the final step result is the CALL output. Records remain distinct even if equal in material value.'),
 ('R23','Output-consumer operands use the actual last-result identity, not an equal ambient workpiece or old result. Downstream records retain ancestry.'),
 ('R24','The prior Plan is read nonconsumingly, published only after previous closure; current execution never publishes a candidate Plan early.'),
 ('R25','Unknown/unlisted/marked groups are first source/control barriers; preserve remaining rows but do not restart semantic flow within that unit.'),
 ('R26','Each unit begins a separately paid scope with no current material or output; previous catalogue and execution records are not initial bindings. Only the previously derived immutable Plan crosses the pair boundary.'),
 ('R27','No morph semantic split: unchanged supplied alternatives are retained as formal views. Whole identities have additional C0 choices; their productive compositional meanings remain unknown.'),
 ('R28','Generic workpiece is an unnamed input type, not an inferred named substance; nominal catalogue identities are descriptions, not translations of plant/mineral names.'),
 ('R29','Across UNCERTAIN_SMALL_SPACE the two-group CALL is an explicit C0 seam choice; retain the joined formal chunk alternative and source uncertainty. It is not a transcription correction or proven segmentation.'),
]

def compact(x): return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def pair_start(gs,i):
    return (gs[i]['ivtff_group_raw']=='chey' and i+1<len(gs)
        and gs[i+1]['ivtff_group_raw']=='tal'
        and gs[i]['locus']==gs[i+1]['locus']
        and gs[i]['right_separator'] in ['DEFINITE_SPACE','UNCERTAIN_SMALL_SPACE']
        and gs[i+1]['left_separator']==gs[i]['right_separator'])

rows=[]; unit_records=[]; plans={}; calls=[]
nativecols=list(csv.DictReader((D/'FW_DISCOVERY_GROUPS.tsv').open(),delimiter='\t').fieldnames)

for side in ['F83R','F83V']:
 for ed in packet['editions']:
  for role in ['PREVIOUS','CURRENT']:
   uid='FW_'+side+'_'+role
   gs=[g for g in packet['groups'] if g['unit_id']==uid and g['edition']==ed]
   key=uid+'_'+ed
   state={'mode':'DEFINE' if role=='PREVIOUS' else 'EXECUTE',
      'catalogue_mentions':0,'slot':None,'input':None,'last_result':None,
      'step_count':0,'event_count':0,'pending_count':0,'pending_call':None,
      'material_revision':None,'material_revision_count':0,
      'published_plan_id':None,
      'stopped':False,'barrier':None}
   steps=[]; pending=[]; events=[]; results=[]; mentions=[]; declarations=[]
   consumers=[]; pair_tail=None; input_record=None
   def apply_step(op,source,plan_step=None,parent_call=None):
    old=state['last_result']; eid=key+'__E'+str(len(events)+1)
    oid=key+'__O'+str(len(results)+1)
    if op in ['NOTE','CHECK_RECORD','STORE_RECORD'] and old is None:
     raise ValueError('readout without a preceding result')
    inp=old if op in ['NOTE','CHECK_RECORD','STORE_RECORD'] else state['input']
    old_revision=state['material_revision']
    treatment=op in ['GRIND','KNEAD','PRESS','SHAPE','PREPARE']
    if treatment:
     state['material_revision_count']+=1
     state['material_revision']=state['input']+'__V'+str(state['material_revision_count'])
    e={'id':eid,'operation':op,'source_id':source,'plan_step_id':plan_step,
       'call_id':parent_call,'execution_id':parent_call+'__EXECUTION' if parent_call else key+'__CURRENT_EXECUTION',
       'input_id':inp,'material_id':state['input'],
       'output_id':oid,'before_result':old,'after_result':oid,
       'effect':'SYMBOLIC_INSTRUCTION_RECORD; no measured efficacy',
       'result_ancestry':[old] if op in ['NOTE','CHECK_RECORD','STORE_RECORD'] else [],
       'material_revision_before':old_revision,'material_revision_after':state['material_revision'],
       'symbolic_material_action':treatment,'kind':'ExecutionEvent'}
    events.append(e);results.append({'id':oid,'type':'ResultRecord',
       'event_id':eid,'material_id':state['input'],
       'material_revision':state['material_revision'],
       'parent_result':old if op in ['NOTE','CHECK_RECORD','STORE_RECORD'] else None,
       'call_id':parent_call,'source_id':source,'intended_action':op})
    state['last_result']=oid;state['event_count']=len(events)
    if op in ['NOTE','CHECK_RECORD','STORE_RECORD']:
     consumers.append({'source_id':source,'operation':op,'operand_id':inp,
        'operand_type':'ResultRecord','output_id':oid,'event_id':eid,
        'plan_step_id':plan_step,'call_id':parent_call})
    return e
   for i,g in enumerate(gs):
    w=g['ivtff_group_raw'];sid=g['source_group_id'];before=dict(state)
    row={k:g[k] for k in nativecols};row.update(unit_id=uid,mode=state['mode'],
      lexical_entry=lexicon.get(w,{}).get('entry_id','UNLISTED'),
      formal_gdt012_062=compact(g['formal_gdt012_062']),
      formal_gdt605_chunk_id=g['formal_gdt605_chunk_id'],
      native_paragraph_flags_available=str(g['native_paragraph_flags_available']).lower(),
      rule_ids='',contribution='',arguments='[]',preconditions='',
      delta='{}',plan_id=key+'__PLAN' if role=='PREVIOUS' else '',call_id='',event_ids='[]',result_ids='[]',status='')
    delta={};new_events=[]; args=[]
    if state['stopped']:
     row.update(status='BLOCKED_AFTER_FIRST_BARRIER',contribution='RAW_PRESERVED_NOT_EXECUTED',rule_ids='R25')
    elif not re.fullmatch('[a-z]+',w) or w not in lexicon:
     state['stopped']=True;state['barrier']=sid
     row.update(status='UNKNOWN_SOURCE_OR_WHOLE_VALUE',contribution='CONTROL_SCOPE_UNKNOWN',rule_ids='R25')
     delta={'first_barrier':sid,'raw':w}
    elif pair_start(gs,i):
     pair_tail=gs[i+1]['source_group_id'];state['pending_call']=sid
     row.update(status='PENDING_CALL_RIGHT_GROUP',contribution='CALL_OPEN',rule_ids='R19,R20',lexical_entry='FW_CHEY_CALL_OVERLOAD')
     delta={'pending_call_opened':sid,'expected_right':pair_tail}
    elif sid==pair_tail:
     start=state['pending_call'];pid=plans.get((side,ed),{}).get('id')
     row.update(contribution='METHOD_REFERENCE_AND_INVOCATION',rule_ids='R18,R20,R21,R22,R24',lexical_entry='FW_TAL_PLAN_OVERLOAD')
     args=[{'id':pid,'type':'ProcessPlan'},{'id':state['input'],'type':'MaterialInstance','slot':'x'}]
     if role=='PREVIOUS' or not pid or not state['input']:
      state['stopped']=True;state['barrier']=sid
      row['status']='NO_CAPACITY_CALL_PLAN_OR_INPUT'
      delta={'missing_plan':not bool(pid),'missing_input':not bool(state['input'])}
     else:
      cid=key+'__CALL'+str(1+sum(c['unit']==key for c in calls))
      exid=cid+'__EXECUTION';pl=plans[(side,ed)];start_event=len(events)
      input_revision=state['material_revision']
      for st in pl['steps']:
       new_events.append(apply_step(st['operation'],sid,st['id'],cid))
      state['pending_call']=None
      c={'id':cid,'execution_id':exid,'unit':key,'source_ids':[start,sid],
         'plan_id':pid,'stage_id':pid+'__WHOLE','step_indexes':list(range(1,len(pl['steps'])+1)),
         'input_id':state['input'],'input_producer_id':input_record['source_id'],
         'input_revision_before':input_revision,'output_material_revision':state['material_revision'],
         'slot_bindings':{'x':state['input']},'captured_constants':[],
         'event_ids':[e['id'] for e in events[start_event:]],
         'output_id':state['last_result'],'result_ids':[e['output_id'] for e in new_events],
         'source_plan_step_ids':[st['source_id'] for st in pl['steps']]}
      calls.append(c);row.update(status='BOUND_C0_CALL',plan_id=pid,call_id=cid)
      delta={'call':c}
    elif w=='qokaiin':
     declarations.append(sid);state['slot']='x:MaterialInstance'
     row.update(rule_ids='R05,R06' if role=='PREVIOUS' else 'R07,R08,R09',contribution='WRITTEN_WORKPIECE_DECLARATION')
     if role=='PREVIOUS':
      state['pending_count']=0;row['status']='FORMAL_SLOT_DECLARED_OR_REAFFIRMED'
      delta={'formal_slot':'x','source':sid,'existing':len(declarations)>1}
     elif state['input'] is None:
      inp=key+'__INPUT';state['input']=inp
      state['material_revision']=inp+'__V0'
      input_record={'id':inp,'type':'MaterialInstance','source_id':sid,
        'kind_id':key+'__GENERIC_KIND','spec_id':key+'__GENERIC_SPEC',
        'named_material':None,'fresh_from_written_expression':True,
        'earlier_result_or_material':False,'allocation_rule':'R07'}
      row['status']='WRITTEN_INPUT_CREATED_PENDING_DISCHARGED'
      delta={'input':input_record,'discharged_sources':[s['source_id'] for s in pending]}
      for st in pending:new_events.append(apply_step(st['operation'],st['source_id']))
      pending=[];state['pending_count']=0
     else:
      row['status']='WORKPIECE_COREFERENCE';delta={'same_input':state['input'],'no_allocation':True}
     args=[{'id':state['input'] or 'x','type':'MaterialInstance'}]
    elif w in controls:
     op=controls[w];st={'id':key+'__STEP'+str(len(steps)+1),
       'source_id':sid,'operation':op,'operand':'LAST_RESULT' if op in ['NOTE','CHECK_RECORD','STORE_RECORD'] else 'x',
       'input_type':'ResultRecord' if op in ['NOTE','CHECK_RECORD','STORE_RECORD'] else 'MaterialInstance',
       'output_type':'ResultRecord',
       'abstract_input_id':steps[-1]['abstract_output_id'] if op in ['NOTE','CHECK_RECORD','STORE_RECORD'] and steps else 'x',
       'abstract_output_id':key+'__ABSTRACT_R'+str(len(steps)+1),
       'omitted_operand_rule':'R10' if op not in ['NOTE','CHECK_RECORD','STORE_RECORD'] else 'R13',
       'macro_substeps':[op,'CREATE_EVENT','CREATE_RESULT_RECORD']}
     steps.append(st);state['step_count']=len(steps)
     row.update(rule_ids='R10,R11,R12,R13,R14',contribution=op)
     if role=='PREVIOUS':
      row['status']='WRITTEN_PLAN_STEP';delta={'recorded_step':st}
      state['pending_count']=0 if state['slot'] else len(steps)
     elif state['input'] is None:
      pending.append(st);state['pending_count']=len(pending)
      row['status']='PENDING_WRITTEN_CURRENT_INPUT';delta={'deferred_step':st}
     else:
      new_events=[apply_step(op,sid)];row['status']='SYMBOLIC_C0_INSTRUCTION';delta={'events':new_events}
     args=[{'id':before['last_result'] if st['operand']=='LAST_RESULT' else (state['input'] or 'x'), 'type':st['input_type']}]
    else:
     m={'source_id':sid,'raw':w,'kind_id':'NAME:'+w,'spec_id':'SPEC:'+w,
       'type':'MaterialKindDescription','frame':'FINITE_CATALOGUE',
       'executed_or_captured':False,'opaque_identity':True}
     mentions.append(m);state['catalogue_mentions']=len(mentions)
     row.update(status='OPAQUE_NOMINAL_ROLE_ONLY',rule_ids='R01,R02,R03,R28',contribution='DECLARE_CATALOGUE_KIND_AND_SPEC')
     delta={'nominal_declaration':m};args=[{'id':'NAME:'+w,'type':'MaterialKindName'}]
    row['preconditions']=compact({'recognized_exact_value':w in lexicon,
       'unmarked':bool(re.fullmatch('[a-z]+',w)), 'scope_active':not before['stopped']})
    row['arguments']=compact(args);row['state_before']=compact(before)
    row['delta']=compact(delta);row['state_after']=compact(state)
    row['event_ids']=compact([e['id'] for e in new_events]);row['result_ids']=compact([e['output_id'] for e in new_events])
    row['pending_opening_discharge']=compact({'before':before['pending_count'],'after':state['pending_count'],
       'call_before':before['pending_call'],'call_after':state['pending_call']})
    rows.append(row)
   closure_source=gs[-1]['source_group_id'];closure=None
   if role=='PREVIOUS' and not state['stopped'] and state['slot'] and steps:
    # Validate the abstract ResultRecord flow with no target material donation.
    abstract_result=False
    for st in steps:
     if st['operation'] in ['NOTE','CHECK_RECORD','STORE_RECORD'] and not abstract_result:
      raise ValueError('unbound abstract readout')
     abstract_result=True
    pid=key+'__PLAN';closure={'source_id':closure_source,'rule':'R15','native':ed!='RF1b'}
    plans[(side,ed)]={'id':pid,'signature':{'input_slots':{'x':'MaterialInstance'},'return':'ResultRecord'},
       'slot_declaration_source_ids':declarations,'steps':steps,'captured_constants':[],
       'nominal_documentation':mentions,'closure':closure,'stage_policy':'WHOLE_PLAN_R17',
       'stage_id':pid+'__WHOLE','result_schema':'final step fresh ResultRecord about supplied x',
       'mode':'DEFINE_ONLY_NO_EARLIER_PHYSICAL_EXECUTION'}
    state['published_plan_id']=pid
   elif role=='CURRENT' and not state['stopped'] and (not state['input'] or pending or state['pending_call']):
    state['stopped']=True;state['barrier']=closure_source
   # Add closure annotations to the final raw row rather than inventing a raw word.
   rows[-1]['closure']=compact(closure or {'not_published':True,'barrier':state['barrier']})
   final_delta=json.loads(rows[-1]['delta'])
   final_delta['unit_end']={'closure':closure,'published_plan_id':state['published_plan_id'],
     'stopped':state['stopped'],'barrier':state['barrier']}
   rows[-1]['delta']=compact(final_delta);rows[-1]['state_after']=compact(state)
   ur={'unit_id':uid,'reader':ed,'key':key,'raw_groups':len(gs),
       'mode':state['mode'],'first_barrier':state['barrier'],'final_state':state,
       'steps':steps,'nominal_documentation':mentions,'written_declarations':declarations,
       'input_record':input_record,'events':events,'result_records':results,'consumers':consumers,
       'closure':closure,'whole_role_coverage':not state['stopped'],
       'named_material_translations':0,'native_paragraph_contract':ed!='RF1b'}
   unit_records.append(ur)

for c in calls:
 u=next(x for x in unit_records if x['key']==c['unit'])
 # Every later direct/derived consumer is listed; no ambient equivalence credit.
 lineage={c['output_id']}; found=[]
 for e in u['events']:
  if e['operation'] in ['NOTE','CHECK_RECORD','STORE_RECORD'] and e['input_id'] in lineage:lineage.add(e['output_id'])
  if e['input_id'] in lineage and e['operation'] in ['NOTE','CHECK_RECORD','STORE_RECORD'] and e['call_id']!=c['id']:
   found.append({'source_id':e['source_id'],'event_id':e['id'],'operation':e['operation'],
      'operand_id':e['input_id'],'relation':'DIRECT' if e['input_id']==c['output_id'] else 'DERIVED',
      'output_id':e['output_id']})
 c['later_written_consumers']=found
 assert found, c

predictions=[]
for page,previous,current in [('f75v',[38,42],[43,49]),('f104v',[19,21],[22,26])]:
 for ed in packet['editions']:
  predictions.append({'page':page,'reader':ed,'previous_window':previous,'current_window':current,
   'forecast':'CONDITIONAL_NO_SUCCESS_PREDICTED_WITHOUT_BODY',
   'frozen_requirements':[
      'All earlier/current raw wholes must be unmarked members of the frozen214whole whitelist; no new nominal values.',
      'Earlier whole unit must contain written qokaiin formal declaration and at least one REGISTER/treatment step, with readouts having a preceding result.',
      'Earlier unit must finish without unknown/control barrier; close at R15 and select every recorded step under R17.',
      'Current first qokaiin must produce input and discharge any earlier instruction queue; repeated qokaiin co-refers.',
      'Exact same-locus matching DEFINITE_SPACE or UNCERTAIN_SMALL_SPACE chey tal must retrieve the immediate previous closed Plan; small-space choice stays C0 uncertain. No alias or older unit.',
      'Fresh call execution/result must have an actual later qokal/shcthy/shedal consumer using direct/derived record under R13/R23.',
      'All source groups remain in literal transfer, even after first barrier.'],
   'missing_pair':'NO_CAPACITY_NOT_APPLICABLE_EXACT_CALL; no spelling repair',
   'unknown':'FIRST_BARRIER_NO_CAPACITY_DEPENDENT_CHAIN; later raw rows retained',
   'bound_wrong_signature_or_order':'CONTRADICTION_FIXED_FW',
   'RF_scope':'External matching-locus window only; native paragraph capacity unavailable' if ed=='RF1b' else 'Native paragraph metadata',
   'independent_confirmation_capacity':0})

account={'schema':'FW-authored-single-method-C0-v1','status':'CANDIDATE_COMPLETE_FOR_IT_DISCOVERY_OTHER_READERS_BARRIERS',
 'candidate_count':1,'source_packet_sha256':hashlib.sha256((D/'FW_DISCOVERY_PACKET.json').read_bytes()).hexdigest(),
 'input_receipt_sha256':hashlib.sha256((D/'FW_AUTHOR_INPUT_RECEIPT.json').read_bytes()).hexdigest(),
 'dictionary':lexicon,'controls':controls,'nominal_whitelist':names,
 'types':['MaterialKind','MaterialSpec','MaterialInstance','MaterialKindName','MaterialKindDescription','Operator',
  'ProcessPlan','FormalSlot','Call','Execution','ExecutionEvent','ResultRecord'],
 'rules':[{'id':rid,'text':txt,'cost':1} for rid,txt in rules],
 'cost':{'whole_values':len(lexicon),'operator_whole_values':len(controls),'opaque_nominal_whole_values':len(names),
   'chey_tal_contextual_value_overloads':2,'chey_tal_pair_production':1,'global_rules':len(rules),
   'type_schemas':12,'REGISTER_synonym_residual_choices':4,
   'treatment_event_result_macro_substeps':15,'REGISTER_event_result_macro_substeps':3,
   'three_readout_event_result_macro_substeps':9,'initial_bindings':0,'captured_constants':0,
   'generic_kind_spec_instance_lift_substeps':3,'generic_kind_default':1,
   'declare_mode_overload':1,'catalogue_kind_spec_lift_substeps':2,
   'closure_publish_substeps':2,'call_resolve_bind_execute_return_substeps':4,
   'cost_unit':'one authored choice; descriptive counts not probabilities',
   'note':'Lexical values and production/macro/type costs charged separately; repeated exact names reuse identity. Every whitelist name paid once.'},
 'plan_records':list(plans.values()),'unit_records':unit_records,'calls':calls,
 'application_predictions':predictions,'application_bodies_opened':False,
 'assumptions':[
  '214 finite whole values are stipulated, not learned or confirmed; catalogue role for200exact values is a large paid interpretation.',
  'No uniform noun classifier, control bypass, new name admission or marked-form alias; unknowns stop.',
  'Nominal declarations are material catalogue descriptions, not added ingredients; none are captured into the operation list.',
  'Whole-Plan scope and unit mode/closure/omitted-primary-operand conventions are authored choices, not demonstrated sentence or paragraph semantics.',
  'qokaiin first introduction/repeated co-reference and generic input default are paid readings, not an independently bound producer.',
  'All action results are symbolic C0 execution records; no physical efficacy or achieved condition is observed.',
  'Whole lexicon does not decode productive morphology; formal alternatives are conserved, with compositional semantic debt unresolved.',
  'ZL/IT native boundaries and RF external windows remain separate.',
  'All discovery is same physical leaf83; exposed application paragraphs on75/104 have0independent meaning capacity.'
 ],
 'comparison':{
   'material_replacement':'Cannot generate this stipulated ordered earlier-Plan execution graph without separately paid replay/bridge. No actual FV dictionary was read.',
   'prior_result_reuse':'There is no earlier physical execution/result; current input producer is current qokaiin, hence not old result ancestry.',
   'attached_protocol_rival':'Associate a nominal MaterialSpec with the same written Plan; add association+lookup+activation+input binding+output bridge costs. Projecting away association/attachment nodes reproduces identical call/event/output graph.',
   'full_graph_difference':'Attached-protocol rival has MaterialSpec/association/lookup nodes; direct Method graph has earlier Plan-reference edge.',
   'named_projection':'Erase attachment/association/lookup nodes and replace their resolved Plan edge by direct reference; retain event order, material identity, slot bindings, source Plan-step IDs and ResultRecord ancestry.',
   'ceiling':'Operational equivalence leaves METHOD semantics unresolved; no semantic ranking by author fit, costs or agreement.'},
 'confirmed_lexemes':0,'independent_confirmation_capacity':0,
 'no_legacy_model_changed':True,'no_decoder_search':True,
 'validation_scope':'Author literal annotation/transition materialization only; independent grammar/dependency/source checks pending.'}
account['cost']['total_declared_choice_units']=sum(v for k,v in account['cost'].items() if isinstance(v,int) and k not in ['operator_whole_values','opaque_nominal_whole_values'])
(D/'FW_AUTHOR_METHOD.json').write_text(json.dumps(account,ensure_ascii=False,indent=2)+'\n')
(D/'FW_APPLICATION_PREDICTIONS.json').write_text(json.dumps({'candidate':'FW_SINGLE_WHOLE_PLAN_C0','predictions':predictions,'application_bodies_opened':False},ensure_ascii=False,indent=2)+'\n')
cols=nativecols+['unit_id','mode','lexical_entry','formal_gdt012_062','formal_gdt605_chunk_id','native_paragraph_flags_available',
 'rule_ids','contribution','arguments','preconditions','state_before','delta','state_after','plan_id','call_id',
 'event_ids','result_ids','pending_opening_discharge','status','closure']
with (D/'FW_DERIVATION.tsv').open('w',newline='') as f:
 source_order={g['source_group_id']:i for i,g in enumerate(packet['groups'])}
 rows.sort(key=lambda r:source_order[r['source_group_id']])
 w=csv.DictWriter(f,fieldnames=cols,delimiter='\t');w.writeheader();w.writerows(rows)
assert len(rows)==1016 and len({r['source_group_id'] for r in rows})==1016
print(compact({'groups':len(rows),'lexical_values':len(lexicon),'nominal_values':len(names),'plans':len(plans),'calls':len(calls),
  'units':[{'unit':u['key'],'groups':u['raw_groups'],'barrier':u['first_barrier'],'role_coverage':u['whole_role_coverage']} for u in unit_records],
  'call_summaries':[{'id':c['id'],'steps':len(c['event_ids']),'output':c['output_id'],'consumers':c['later_written_consumers']} for c in calls]}))
