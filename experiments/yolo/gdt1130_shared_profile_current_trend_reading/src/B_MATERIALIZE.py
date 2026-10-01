#!/usr/bin/env python3
"""GDT1130 author B finite frozen-dictionary materialization, no trained parser.
Replays only the already registered bounded SOURCE.json; no new corpus access.
"""
import collections,copy,hashlib,json,pathlib
BASE=pathlib.Path(__file__).resolve().parents[1]
def read(name):return json.loads((BASE/name).read_text())
def sha(name):return hashlib.sha256((BASE/name).read_bytes()).hexdigest()
f=read('src/B_CONSTRUCTORS.json');e=read('src/B_EXTENSIONS.json');s=read('src/SOURCE.json');dictionary=e['full_dictionary']
assert sha('src/B_CONSTRUCTORS.json')==e['frozen_core_sha256']
assert sha('src/SOURCE.json')==f['source_sha256']
assert len(f['core_families'])<=12 and len(f['opaque_content_constants'])<=8
for raw,v in f['core_dictionary'].items():assert dictionary[raw]==v
FAMILIES={x['id'] for x in f['core_families']}
for v in dictionary.values():
 assert v['family'] in FAMILIES
 if v['family']=='EXACT_SEQUENCE':assert all(x['family'] in FAMILIES for x in v['operations'])
ledger=[];unit_results=[]

def snapshot(state):
 return {'owner':state['owner'],'owner_source':state['owner_source'],'field':copy.deepcopy(state['field']),'last_world_id':state['last_world']['id'] if state['last_world'] else None,'last_instruction_id':state['last_instruction']['id'] if state['last_instruction'] else None,'antecedent_ids':[p['id'] for p in state['antecedent']],'pending_connective_source_ids':[c['source_group_id'] for c in state['pending_connectives']],'world_proposition_ids':[p['id'] for p in state['propositions']],'instruction_ids':[p['id'] for p in state['instructions']]}

def initial():
 return {'owner':None,'owner_source':None,'field':None,'last_world':None,'last_instruction':None,'antecedent':[],'pending_connectives':[],'propositions':[],'instructions':[]}

def require(state):
 if state['owner'] is None or state['field'] is None:raise ValueError('MISSING_WRITTEN_OWNER_OR_PROFILE_FIELD')

def use(steps,role,value,producer):
 steps['operands'].append({'role':role,'value':copy.deepcopy(value),'producer_source_id':producer})

def world(state,row,steps,payload):
 require(state)
 n=len(state['propositions'])+1
 p={'id':row['source_group_id']+'#P'+str(n),'source_group_id':row['source_group_id'],'owner':state['owner'],'time':'tau','mode':state['field']['mode'],**payload}
 use(steps,'retained_owner',state['owner'],state['owner_source'])
 use(steps,'retained_profile_field',state['field'],state['field']['source_group_id'])
 if state['pending_connectives']:
  p['written_connections']=copy.deepcopy(state['pending_connectives'])
  for c in state['pending_connectives']:
   use(steps,'written_connective',c,c['source_group_id']);use(steps,'connected_prior_world_proposition',c['left'],c['left']['source_group_id'])
  state['pending_connectives']=[]
 state['last_world']=p;state['propositions'].append(p)
 if p['mode']=='HYPOTHETICAL_ANTECEDENT':state['antecedent'].append(p)
 steps['outputs'].append(copy.deepcopy(p))
 return p

def execute(state,row,op):
 steps={'family':op['family'],'parameters':{k:v for k,v in op.items() if k not in ('price','internal_parts','parts','operations')},'operands':[],'outputs':[]}
 family=op['family'];sid=row['source_group_id']
 if family=='INTRO_OWNER':
  if state['owner'] is not None:use(steps,'previous_owner',state['owner'],state['owner_source'])
  state['owner']=op['owner'];state['owner_source']=sid
  state['field']={'owner':op['owner'],'axis':'Substance','basis':'owner-relative ordinary norm','time':'tau','mode':'ACTUAL','source_group_id':sid}
  world(state,row,steps,{'predicate':'EXISTS_AS_BODY_OR_PREPARATION','value':True})
 elif family in ('A_N_BIND','SELECT_FIELD'):
  require(state);use(steps,'prior_field_for_same_owner_basis_time',state['field'],state['field']['source_group_id'])
  mode=op['mode'];antecedent=copy.deepcopy(state['antecedent'])
  if mode=='CONSEQUENT_OBSERVATION':
   if state['last_world'] is None:raise ValueError('MISSING_PRECEDING_WORLD_PREDICATE_FOR_CH_CONSEQUENT')
   use(steps,'preceding_written_world_predicate',state['last_world'],state['last_world']['source_group_id']);mode='ACTUAL'
  state['field']={'owner':state['owner'],'axis':op['axis'],'basis':'owner-relative ordinary norm','time':'tau','mode':mode,'source_group_id':sid}
  steps['outputs'].append({'kind':'OWNER_BOUND_PROFILE_FIELD','value':copy.deepcopy(state['field'])})
  if family=='A_N_BIND':
   payload={'predicate':'PROPERTY_IS_OBSERVED' if op['mode']=='CONSEQUENT_OBSERVATION' else 'HAS_PREDICABLE_PROPERTY','axis':op['axis'],'basis':state['field']['basis'],'value':True,'host':op['host'],'interface':'aiin'}
   if mode=='ACTUAL' and antecedent:
    payload['written_if_context']=antecedent
    for p in antecedent:use(steps,'written_antecedent',p,p['source_group_id'])
   world(state,row,steps,payload)
  if mode=='ACTUAL':state['antecedent']=[]
 elif family=='ASSERT_GRADE':
  require(state);world(state,row,steps,{'predicate':'GRADE','axis':state['field']['axis'],'basis':state['field']['basis'],'value':op['grade']})
 elif family=='ASSERT_QUALITY':
  world(state,row,steps,{'predicate':'QUALITY','quality':op['quality'],'value':True})
 elif family=='DIRECT':
  require(state)
  if state['last_world'] is None:raise ValueError('MISSING_WRITTEN_WORLD_CONDITION_FOR_DIRECTIVE')
  use(steps,'owner',state['owner'],state['owner_source']);use(steps,'written_condition',state['last_world'],state['last_world']['source_group_id']);use(steps,'retained_field',state['field'],state['field']['source_group_id'])
  p={'id':sid+'#I'+str(len(state['instructions'])+1),'source_group_id':sid,'owner':state['owner'],'action':op['action'],'condition':copy.deepcopy(state['last_world']),'mode':state['field']['mode'],'type':'INSTRUCTION_NOT_EXECUTED'}
  state['last_instruction']=p;state['instructions'].append(p);steps['outputs'].append(p)
 elif family in ('SEAL','QUALIFY'):
  require(state)
  p=state['last_world']
  if p is None:raise ValueError('MISSING_WRITTEN_WORLD_PREDICATE_FOR_ENDORSEMENT')
  use(steps,'written_world_predicate',p,p['source_group_id'])
  if state['last_instruction'] is not None:use(steps,'retained_instruction',state['last_instruction'],state['last_instruction']['source_group_id'])
  if op.get('qualification')=='RESTRICTED_TO_WRITTEN_CONDITION':
   if not state['antecedent']:raise ValueError('MISSING_WRITTEN_RESTRICTION_CONDITION')
   for prior in state['antecedent']:use(steps,'restriction_condition',prior,prior['source_group_id'])
  world(state,row,steps,{'predicate':'ENDORSED_WORLD_CONTENT','content':copy.deepcopy(p),'qualification':op.get('qualification','VALID_UNDER_RETAINED_PROFILE'),'value':True})
 elif family=='CONNECT':
  require(state)
  if state['last_world'] is None:raise ValueError('MISSING_WRITTEN_LEFT_WORLD_PROPOSITION')
  use(steps,'left_world_proposition',state['last_world'],state['last_world']['source_group_id'])
  c={'source_group_id':sid,'relation':op['relation'],'left':copy.deepcopy(state['last_world'])}
  state['pending_connectives'].append(c);steps['outputs'].append({'kind':'PENDING_WORLD_CONNECTION','value':c})
 else:raise ValueError('UNKNOWN_FAMILY')
 return steps

for edition in ['IT2a','ZL3b','RF1b']:
 for name,loci in [('UPPER_RING',['f68r2.6']),('LOWER_RING',['f68r2.31']),('PROSE',['f89v1.'+str(i) for i in range(13,21)])]:
  state=initial();barrier=None;unitrows=[]
  native=[g for g in s['groups'] if g['edition']==edition and g['locus'] in loci]
  for source in native:
   row=copy.deepcopy(source);raw=row['raw'];row['unit']=name;row['frozen_dictionary_entry']=copy.deepcopy(dictionary.get(raw));row['state_before']=snapshot(state);row['substeps']=[];row['operands']=[];row['outputs']=[]
   if barrier:
    row['status']='BLOCKED_AFTER_FIRST_BARRIER';row['first_barrier']=copy.deepcopy(barrier)
   elif raw not in dictionary:
    barrier={'source_group_id':row['source_group_id'],'raw':raw,'reason':'UNINTERPRETED_EXACT_RAW_FORM_NO_REPAIR'};row['status']='UNKNOWN_FIRST_BARRIER';row['first_barrier']=barrier
   else:
    entry=dictionary[raw]
    ops=entry['operations'] if entry['family']=='EXACT_SEQUENCE' else [entry]
    try:
     for op in ops:
      step=execute(state,row,op);row['substeps'].append(step);row['operands'].extend(step['operands']);row['outputs'].extend(copy.deepcopy(step['outputs']))
     row['status']='DERIVED_C0_WORLD_CONTENT'
    except ValueError as error:
     barrier={'source_group_id':row['source_group_id'],'raw':raw,'reason':str(error)};row['status']='MISSING_INPUT_FIRST_BARRIER';row['first_barrier']=barrier
   row['state_after']=snapshot(state);row['later_consumption_source_ids']=[];unitrows.append(row);ledger.append(row)
  closure=[]
  if not barrier and state['pending_connectives']:closure.append('UNCONSUMED_WRITTEN_CONNECTIVE')
  if not barrier and state['antecedent']:closure.append('OPEN_HYPOTHETICAL_ANTECEDENT_AT_SCOPE_END')
  unit_results.append({'edition':edition,'unit':name,'groups':len(unitrows),'materialized_groups':sum(r['status']=='DERIVED_C0_WORLD_CONTENT' for r in unitrows),'first_barrier':barrier,'closure_obligations':closure,'complete':not barrier and not closure,'last_owner':state['owner'],'final_field':state['field'],'world_propositions':state['propositions'],'instructions':state['instructions'],'native_paragraph_status':'RF comparison window, not native complete paragraph' if edition=='RF1b' and name=='PROSE' else 'native unit as registered; no physical independent confirmation'})
# Actual source-level output consumption: inspect every declared operand, preserving all source IDs.
def nested_sources(x):
 if isinstance(x,dict):
  out={x['source_group_id']} if x.get('source_group_id') in rowmap else set()
  for value in x.values():out|=nested_sources(value)
  return out
 if isinstance(x,list):
  out=set()
  for value in x:out|=nested_sources(value)
  return out
 return set()
rowmap={r['source_group_id']:r for r in ledger};consumers=collections.defaultdict(set)
for row in ledger:
 for op in row['operands']:
  ids=nested_sources(op['value'])
  if op.get('producer_source_id') in rowmap:ids.add(op['producer_source_id'])
  op['actual_producer_source_ids']=sorted(ids)
  for sid in ids:
   if sid!=row['source_group_id']:consumers[sid].add(row['source_group_id'])
for row in ledger:
 row['later_consumption_source_ids']=sorted(consumers[row['source_group_id']])
 if row['status']=='DERIVED_C0_WORLD_CONTENT' and not row['later_consumption_source_ids']:
  row['terminal_contribution']='A world statement/directive terminal output, not claimed as a later numerical/signature consumer.'
# Validate source conservation exactly and no line resets in prose.
assert len(ledger)==288 and len(rowmap)==288
for row in ledger:
 source=next(g for g in s['groups'] if g['source_group_id']==row['source_group_id'])
 assert all(row[k]==v for k,v in source.items())
repeat=[]
for raw,entry in dictionary.items():
 occurrences=[r for r in ledger if r['raw']==raw]
 if len(occurrences)>1:repeat.append({'raw':raw,'positions':[r['source_group_id'] for r in occurrences],'same_exact_entry':all(r['frozen_dictionary_entry']==entry for r in occurrences),'materialized_positions':[r['source_group_id'] for r in occurrences if r['status']=='DERIVED_C0_WORLD_CONTENT'],'blocked_positions_not_treated_as_derived':[r['source_group_id'] for r in occurrences if r['status']!='DERIVED_C0_WORLD_CONTENT']})
# Detect only opposed HIGH/LOW actual grades at exactly same owner/axis/norm/time.
grades=collections.defaultdict(list)
for row in ledger:
 for p in row['outputs']:
  if p.get('predicate')=='GRADE' and p['mode']=='ACTUAL':grades[(row['edition'],row['unit'],p['owner'],p['axis'],p['basis'],p['time'])].append(p)
contradictions=[{'profile':list(key),'values':[x['value'] for x in value],'positions':[x['source_group_id'] for x in value]} for key,value in grades.items() if {'HIGH','LOW'}<=set(x['value'] for x in value)]
for unit in unit_results:
 unit['operational_complete']=unit['complete']
 unit['exact_actual_grade_contradictions']=[x for x in contradictions if x['profile'][:2]==[unit['edition'],unit['unit']]]
 unit['complete']=unit['complete'] and not unit['exact_actual_grade_contradictions']
 unit['semantic_coherence_assessment']='EXACT_CONTRADICTION' if unit['exact_actual_grade_contradictions'] else ('NO_OPPOSED_ACTUAL_GRADE_IN_MATERIALIZED_ROWS' if unit['first_barrier'] else 'NO_OPPOSED_ACTUAL_GRADE')
part_effects=[]
for raw,entry in dictionary.items():
 if entry['family']=='A_N_BIND':
  effects={'aiin':'binds nominal axis to actual introduced owner/norm/time; changes field and contributes HAS_PREDICABLE_PROPERTY or observed-property proposition','host':entry['host']+' specifies '+entry['axis']+' as actual field argument'}
  if raw=='qokaiin':effects['q']='opens hypothetical rather than actual predication condition for subsequent grades'
  if raw=='chokaiin':effects['ch']='requires preceding owner world predicate and closes written antecedent into explicit property-observation consequent'
  if raw=='okoaiin':effects['internal_o']='paid exact oko host selects Substance rather than ok Appearance; no independent universal o operator'
  part_effects.append({'raw':raw,'exact_parts':entry['parts'],'semantic_effects':effects,'materialized_positions':[r['source_group_id'] for r in ledger if r['raw']==raw and r['status']=='DERIVED_C0_WORLD_CONTENT']})
 elif entry['family']=='EXACT_SEQUENCE' and entry.get('parts'):
  part_effects.append({'raw':raw,'exact_parts':entry['parts'],'operations':entry['operations'],'semantic_null_parts':0,'materialized_positions':[r['source_group_id'] for r in ledger if r['raw']==raw and r['status']=='DERIVED_C0_WORLD_CONTENT']})
# Report real .14/.16 predications, no fitted nonseed output signature.
pair=[p for r in ledger if r['edition']=='IT2a' for p in r['outputs'] if p.get('predicate')=='GRADE' and r['source_group_id'] in ('IT2a|f89v1.14|G008','IT2a|f89v1.16|G009')]
result={'schema':'GDT1130_B_ACCOUNT_v1','model':'STATIC_PROFILE','semantic_level':'C0','author_A_content_read':False,'constructor_sha256':sha('src/B_CONSTRUCTORS.json'),'extension_sha256':sha('src/B_EXTENSIONS.json'),'source_sha256':sha('src/SOURCE.json'),'generated_from_frozen_extension_utc':e['created_utc'],'status':'EXACT_IT_STATIC_CANDIDATE_CONTRADICTED_NATIVE_UNCERTAINTIES_PARTIAL','core_families':f['core_families'],'types':f['types'],'opaque_content_constants':f['opaque_content_constants'],'full_dictionary':dictionary,'reference_and_basis_policy':f['reference_and_basis_policy'],'costs':{'core_families':10,'opaque_constants':7,'core_words':15,'priced_added_exact_forms':len(e['extension_dictionary']),'total_exact_interpreted_forms':len(dictionary),'unknown_raw_form_types':len(e['uninterpreted_exact_raw_forms']),'literal_parameter_inventory':{'grades':3,'qualities':6,'actions':3,'axes':3},'paid_ambient_introduction_assignments':4,'extra_aliases_and_whole_residuals':'All83 extensions priced individually, even synonymous parameterizations; no calibrated scientific complexity ranking','time_change_rules':0,'new_opaque_extension_nouns':0,'new_constructor_families_after_freeze':0,'line_reset_defaults':0,'unknown_noun_fillers':0,'semantic_null_parts':0,'global_productive_prefix_rules':0,'same_body_across_rings_hypothesis':1,'extra_parts_unexplained':'Every unparsed whole residual retains its complete spelling cost; no automatic wrapper deletion or null internal glyphs','EQUABLE_interpretation_obligation':'Even distribution, not an ordinal middle between HIGH and LOW; this is an explicit lexical hypothesis.'},'source_conservation':{'groups':288,'counts':dict(collections.Counter(r['edition'] for r in ledger)),'all_native_source_fields_identical':True,'alternate_readers_independent_leaves':False,'RF_prose_native_complete_paragraph':False},'units':unit_results,'group_ledger':ledger,'exact_repeat_inventory':repeat,'semantic_part_effect_inventory':part_effects,'actual_opposed_grade_contradictions':contradictions,'IT_seed_pair':pair,'literal_extension_repair_after_counterexample':False,'low_but_rising_asserted':False,'pair_interpretation':'Same Preparation Y and tau/norm, distinct axes: Substance HIGH, Appearance LOW. Static constitution versus appearance. No signed change or body-lunar effect is asserted.','selection_limit':'Expensive C0 whole residual/alias inventory; shared interface and coherent predications do not identify words. Uncertainties make full native-scope construction partial. No domain FAIL, confirmed meaning, independent confirmation, reopening or reserve use.'}
(BASE/'artifacts/B_ACCOUNT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'units':[{k:u[k] for k in ('edition','unit','groups','materialized_groups','first_barrier','closure_obligations','complete')} for u in unit_results],'grade_contradictions':contradictions,'seed_pair':pair,'account_sha':sha('artifacts/B_ACCOUNT.json')},ensure_ascii=False,indent=2))
