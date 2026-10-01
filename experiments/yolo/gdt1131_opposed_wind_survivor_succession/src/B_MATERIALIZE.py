#!/usr/bin/env python3
"""Bounded author B symbolic accounting of explicit hypothetical physical claims.
No parser fitting, new corpus access, image access or semantic validation.
"""
import collections,copy,hashlib,json,pathlib
BASE=pathlib.Path(__file__).resolve().parents[1]
def load(p):return json.loads((BASE/p).read_text())
def sha(p):return hashlib.sha256((BASE/p).read_bytes()).hexdigest()
f=load('src/B_CONSTRUCTORS.json');ext=load('src/B_EXTENSIONS.json');source=load('src/SOURCE.json');dictionary=ext['dictionary']
assert sha('src/B_CONSTRUCTORS.json')==ext['constructor_sha256']
assert sha('src/SOURCE.json')==f['source_sha256']
assert len(f['core_families'])<=12 and len(f['opaque_constants'])<=8
for raw,entry in f['core_dictionary'].items():assert dictionary[raw]==entry
allowed={x['id'] for x in f['core_families']}
for entry in dictionary.values():
 assert entry['family'] in allowed
 for op in entry.get('operations',[]):assert op['family'] in allowed
rows=[];objects={};all_claims=[];all_events=[];all_anchors=[]

def blank(reader):
 return {'reader':reader,'initialized':False,'phase':None,'cursor':None,'selected':None,'old':None,'latest_generation':None,'anchor':None,'sun_source':None,'lift':None,'winds':{},'episode':None,'claims':[],'event_ids':[],'unknown_rows':[],'semantic_barrier':None,'producer':{}}

def snap(st):
 return {k:copy.deepcopy(st[k]) for k in ['initialized','phase','cursor','selected','old','latest_generation','anchor','sun_source','lift','episode','claims','event_ids','semantic_barrier']}|{'unknown_context':{'row_count':len(st['unknown_rows']),'first_source_id':st['unknown_rows'][0] if st['unknown_rows'] else None,'latest_source_id':st['unknown_rows'][-1] if st['unknown_rows'] else None},'winds':{k:{'source':v['source'],'status':v['status'],'phase':v['phase'],'generation_event':v['generation_event'],'cessation_event':v['cessation_event']} for k,v in st['winds'].items()}}

def obj(value):return copy.deepcopy(objects[value]) if isinstance(value,str) and value in objects else copy.deepcopy(value)

def use(step,role,value,producer=None):
 v=obj(value)
 if producer is None and isinstance(v,dict):producer=v.get('source_group_id') or v.get('producer_source_id')
 step['arguments'].append({'role':role,'type':v.get('type') if isinstance(v,dict) else type(v).__name__,'value':v,'producer_source_ids':[] if producer is None else ([producer] if isinstance(producer,str) else list(producer))})
 return v

def need(st):
 if not st['initialized']:raise ValueError('MISSING_EXPLICIT_INITIAL_CASE')

def wind(st,which='selected'):
 need(st);wid=st[which]
 if wid not in st['winds']:raise ValueError('MISSING_'+which.upper()+'_PHYSICAL_WIND')
 return st['winds'][wid]

def current_anchor(st,step):
 need(st)
 if not st['anchor']:raise ValueError('MISSING_WRITTEN_A_N_WIND_ANCHOR')
 a=use(step,'current_written_WindAnchor',st['anchor'])
 if a['wind_id']!=st['selected']:raise ValueError('ANCHOR_SELECTED_PARTICIPANT_MISMATCH_NO_AUTOMATIC_CAST')
 return a

def event(st,row,step,kind,**values):
 eid=st['reader']+':EV'+str(len(st['event_ids'])+1)
 e={'id':eid,'type':'PhysicalEvent','kind':kind,'phase':st['phase'],'mode':'GENERIC_CONDITIONAL','source_group_id':row['source_group_id'],**values}
 objects[eid]=e;st['event_ids'].append(eid);all_events.append(e);step['returns'].append(copy.deepcopy(e));return e

def claim(st,row,step,predicate,truth,**values):
 c={'id':st['reader']+':CLAIM'+str(sum(x['reader']==st['reader'] for x in all_claims)+1),'type':'WorldPredicate','reader':st['reader'],'mode':'GENERIC_CONDITIONAL','observer':'O','horizon':'H','phase_of_assertion':st['phase'],'predicate':predicate,'truth_under_declared_inputs':bool(truth),'source_group_id':row['source_group_id'],**values}
 objects[c['id']]=c;all_claims.append(c);st['claims'].append(c['id']);step['returns'].append(copy.deepcopy(c));return c

def old_end(st,step):
 w=wind(st,'old');use(step,'original_preceding_participant',w,st['producer'].get('old'))
 if not w['cessation_event']:raise ValueError('MISSING_OLD_CESSATION')
 return w,use(step,'old_cessation_event',w['cessation_event'])

def generation(st,step,a=None):
 wid=a['wind_id'] if a else wind(st)['id'];w=st['winds'][wid]
 if not w['generation_event']:raise ValueError('MISSING_ACTUAL_GENERATION_PROVENANCE')
 return w,use(step,'generation_event',w['generation_event'])

def causal_origin(st,step,w,g):
 lift=use(step,'material_raised_event',g['material_raised_event'])
 approach=use(step,'solar_approach_event',lift['solar_approach_event'])
 return lift,approach,(g['wind_id']==w['id'] and g['source']==w['source'] and lift['source']==w['source'] and approach['to_source']==w['source'] and lift['material']=='M' and approach['agent']=='Sun' and approach['phase']==lift['phase']<g['phase'])

def operate(st,row,op):
 step={'family':op['family'],'parameters':{k:v for k,v in op.items() if k not in ('entry_id','whole_residual','price','parts','operations','formal_structure','root_policy')},'arguments':[],'returns':[]}
 family=op['family'];sid=row['source_group_id']
 if family=='CASE_SETUP':
  st.update({'initialized':True,'phase':0,'cursor':'P','selected':'u','old':'u','latest_generation':None,'anchor':None,'sun_source':'P','lift':None,'winds':{},'episode':0,'claims':[],'event_ids':[],'unknown_rows':[],'semantic_barrier':None,'producer':{}})
  w={'id':'u','type':'PhysicalWind','kind':'K','source':'P','horizon':'H','status':'BLOWING','phase':0,'generation_event':None,'cessation_event':None,'producer_source_id':sid,'original_conditional_antecedent':True};st['winds']['u']=w;st['producer'].update({x:sid for x in ['old','selected','cursor','phase','sun_source','world']})
  step['returns'].append(copy.deepcopy(w))
  claim(st,row,step,'IF_WIND_U_BLOWS_FROM_P_UNDER_DECLARED_SOLAR_FRAME',True,wind_id='u',source='P',condition={'wind_blowing':True,'Sun_source':'P','dry_material_available':'M','adjacent_sources':['P','Q'],'initial_phase':0})
 elif family=='SOURCE_NEXT':
  need(st);oldcursor=st['cursor'];use(step,'source_cursor',{'type':'SourceSlot','source':oldcursor,'horizon':'H'},st['producer'].get('cursor'));use(step,'declared_adjacent_pair',{'type':'ObserverHorizon','horizon':'H','observer':'O','adjacent':['P','Q']},st['producer'].get('world'))
  other='Q' if oldcursor=='P' else 'P';matches=[w for w in st['winds'].values() if w['source']==other]
  if len(matches)>1:raise ValueError('MULTIPLE_REGISTERED_WINDS_AT_NEXT_SOURCE')
  st['cursor']=other;st['producer']['cursor']=sid
  if len(matches)==1:st['selected']=matches[0]['id'];st['producer']['selected']=sid;use(step,'unique_registered_participant_at_new_source',matches[0],matches[0]['producer_source_id'])
  else:use(step,'retained_existing_selected_identity_no_source_match',wind(st),st['producer'].get('selected'))
  step['returns'].append({'type':'SourceFocus','source':other,'horizon':'H','selected_wind':st['selected'],'selected_source_matches':wind(st)['source']==other,'unique_match_count':len(matches),'producer_source_id':sid})
 elif family=='SELECT_WIND':
  need(st)
  if op['selection']=='PREVIOUS':w=wind(st,'old');use(step,'preceding_WindReference',w,st['producer'].get('old'))
  else:
   if not st['latest_generation']:raise ValueError('MISSING_LATEST_GENERATED_REFERENCE')
   g=use(step,'latest_generation',st['latest_generation']);w=st['winds'][g['wind_id']]
  st['selected']=w['id'];st['cursor']=w['source'];st['producer']['selected']=sid;st['producer']['cursor']=sid
  step['returns'].append({'type':'PhysicalWindReference','wind_id':w['id'],'source':w['source'],'state_phase':w['phase'],'status':w['status'],'origin_generation_event':w['generation_event'],'producer_source_id':sid})
 elif family=='A_N_ANCHOR':
  w=wind(st);use(step,'selected_physical_wind',w,st['producer'].get('selected'));use(step,'source_cursor',{'type':'SourceSlot','source':st['cursor'],'horizon':'H'},st['producer'].get('cursor'));use(step,'current_ordered_phase',{'type':'PhaseCursor','phase':st['phase']},st['producer'].get('phase'))
  if w['source']!=st['cursor']:raise ValueError('A_N_WIND_SOURCE_CURSOR_MISMATCH')
  for kind in ['generation_event','cessation_event']:
   if w[kind]:use(step,kind,w[kind])
  aid=st['reader']+':ANCHOR'+str(sum(x['reader']==st['reader'] for x in all_anchors)+1)
  a={'id':aid,'type':'WindAnchor','reader':st['reader'],'wind_id':w['id'],'kind':'K','source':w['source'],'horizon':'H','observer':'O','reference_phase':st['phase'],'wind_state_phase':w['phase'],'status':w['status'],'generation_event':w['generation_event'],'cessation_event':w['cessation_event'],'mode':'GENERIC_CONDITIONAL','source_group_id':sid}
  objects[aid]=a;all_anchors.append(a);st['anchor']=aid;step['returns'].append(a)
 elif family=='SOLAR_CHANGE':
  need(st)
  if op['change']=='WITHDRAW':
   a=current_anchor(st,step);w=wind(st,'old');use(step,'old_wind_to_cease',w,st['producer'].get('old'));use(step,'Sun_current_source',{'type':'SunState','source':st['sun_source'],'phase':st['phase']},st['producer'].get('sun_source'))
   if a['wind_id']!=w['id'] or w['status']!='BLOWING' or st['sun_source']!=w['source']:raise ValueError('WITHDRAWAL_REQUIRES_ORIGINAL_BLOWING_ANCHORED_WIND_AND_SUN_AT_ITS_SOURCE')
   st['phase']+=1;st['producer']['phase']=sid
   withdrawal=event(st,row,step,'SOLAR_WITHDRAW',agent='Sun',from_source=w['source'],material='M',previous_phase=a['reference_phase'])
   stop=event(st,row,step,'WIND_CEASES',wind_id=w['id'],source=w['source'],cause_event=withdrawal['id'])
   w['status']='CEASED';w['phase']=st['phase'];w['cessation_event']=stop['id'];st['sun_source']=None;st['lift']=None;st['producer']['sun_source']=sid
   claim(st,row,step,'SOLAR_WITHDRAWAL_CAUSES_OLD_WIND_CESSATION',True,wind_id=w['id'],source=w['source'],cessation_event=stop['id'],cause_event=withdrawal['id'],old_anchor=a['id'])
  else:
   w,stop=old_end(st,step);other='Q' if w['source']=='P' else 'P';use(step,'adjacent_source_in_same_H',{'type':'SourceSlot','old':w['source'],'new':other,'horizon':'H'},st['producer'].get('world'))
   if st['sun_source'] is not None:raise ValueError('SOLAR_APPROACH_WITHOUT_PRECEDING_WITHDRAWAL')
   st['phase']+=1;st['producer']['phase']=sid;st['cursor']=other;st['producer']['cursor']=sid;st['sun_source']=other;st['producer']['sun_source']=sid
   approach=event(st,row,step,'SOLAR_APPROACH',agent='Sun',to_source=other,preceding_cessation=stop['id'])
   lift=event(st,row,step,'DRY_MATERIAL_RAISED',material='M',source=other,solar_approach_event=approach['id']);st['lift']=lift['id']
   claim(st,row,step,'SUN_APPROACH_RAISES_DRY_MATERIAL_AT_ADJACENT_SOURCE',stop['phase']<st['phase'],old_wind=w['id'],old_source=w['source'],new_source=other,material='M',material_raised_event=lift['id'],solar_approach_event=approach['id'])
 elif family=='GENERATE_WIND':
  need(st);old,stop=old_end(st,step)
  if not st['lift']:raise ValueError('MISSING_WRITTEN_MATERIAL_RAISED_BY_SOLAR_APPROACH')
  lift=use(step,'current_material_raised',st['lift']);approach=use(step,'solar_approach',lift['solar_approach_event'])
  if not (stop['phase']<lift['phase'] and lift['source']==st['cursor']==st['sun_source']):raise ValueError('GENERATION_ORDER_OR_SOURCE_INPUT_MISMATCH')
  st['phase']+=1;st['producer']['phase']=sid
  wid='v'+str(sum(w['generation_event'] is not None for w in st['winds'].values())+1)
  assert wid not in st['winds']
  g=event(st,row,step,'WIND_GENERATED',wind_id=wid,wind_kind='K',source=st['cursor'],material_raised_event=lift['id'],solar_approach_event=approach['id'],preceding_cessation=stop['id'])
  w={'id':wid,'type':'PhysicalWind','kind':'K','source':st['cursor'],'horizon':'H','status':'BLOWING','phase':st['phase'],'generation_event':g['id'],'cessation_event':None,'producer_source_id':sid,'original_conditional_antecedent':False};st['winds'][wid]=w;st['selected']=wid;st['producer']['selected']=sid;st['latest_generation']=g['id'];step['returns'].append(copy.deepcopy(w))
  claim(st,row,step,'A_DISTINCT_WIND_IS_GENERATED_AFTER_OLD_CESSATION_BY_SOLAR_RAISED_MATERIAL',wid!=old['id'],new_wind=wid,old_wind=old['id'],generation_event=g['id'],old_cessation=stop['id'],source=w['source'])
 elif family=='MATERIAL_SOURCE_CERTIFY':
  need(st)
  if not st['latest_generation']:raise ValueError('MISSING_FRESH_GENERATION_FOR_SO_SE_HEAD')
  g=use(step,'latest_generation_result',st['latest_generation']);w=st['winds'][g['wind_id']]
  if op['head']=='So':
   lift,approach,truth=causal_origin(st,step,w,g);claim(st,row,step,'FRESH_WIND_HAS_SOLAR_LIFTED_DRY_MATERIAL_ORIGIN',truth,wind_id=w['id'],source=w['source'],generation_event=g['id'],lift_event=lift['id'],Sun_event=approach['id'])
  else:
   old,stop=old_end(st,step);withdraw=use(step,'old_solar_withdrawal_cause',stop['cause_event']);truth=(withdraw['kind']=='SOLAR_WITHDRAW' and withdraw['from_source']==old['source'] and stop['wind_id']==old['id'] and stop['phase']<g['phase'])
   claim(st,row,step,'PRIOR_WIND_ENDED_FROM_SOLAR_WITHDRAWAL_BEFORE_THIS_GENERATION',truth,old_wind=old['id'],new_wind=w['id'],old_cessation=stop['id'],withdrawal_event=withdraw['id'],new_generation=g['id'])
 elif family=='WORLD_PREDICATE':
  need(st);pred=op['predicate']
  if pred=='BLOWING':
   a=current_anchor(st,step);w=st['winds'][a['wind_id']];use(step,'physical_wind_state',w,w['producer_source_id']);truth=w['status']=='BLOWING';values={'wind_id':w['id'],'state_phase':w['phase'],'source':w['source'],'anchor':a['id']}
  elif pred in ('OLD_CEASED','OLD_SOLAR_WITHDRAWAL_CAUSE'):
   w,stop=old_end(st,step);values={'old_wind':w['id'],'cessation_event':stop['id'],'source':w['source'],'cessation_phase':stop['phase']};truth=w['status']=='CEASED'
   if pred=='OLD_SOLAR_WITHDRAWAL_CAUSE':
    cause=use(step,'solar_withdrawal_cause',stop['cause_event']);truth=truth and cause['kind']=='SOLAR_WITHDRAW' and cause['from_source']==w['source'];values['cause_event']=cause['id']
  elif pred=='MATERIAL_RAISED':
   if not st['lift']:raise ValueError('MISSING_SOLAR_RAISED_MATERIAL')
   lift=use(step,'written_material_raised',st['lift']);truth=lift['source']==st['cursor']==st['sun_source'];values={'material':'M','source':lift['source'],'material_raised_event':lift['id'],'state_phase':lift['phase']}
  elif pred in ('GENERATED_FRESH','SOLAR_MATERIAL_ORIGIN_AT_CURSOR'):
   w,g=generation(st,step);use(step,'selected_physical_wind',w,st['producer'].get('selected'));truth=not w['original_conditional_antecedent'];values={'wind_id':w['id'],'source':w['source'],'generation_event':g['id'],'generation_phase':g['phase']}
   if pred=='SOLAR_MATERIAL_ORIGIN_AT_CURSOR':
    lift,approach,origin=causal_origin(st,step,w,g);truth=truth and origin and st['cursor']==w['source'];use(step,'source_cursor',{'type':'SourceSlot','source':st['cursor'],'horizon':'H'},st['producer'].get('cursor'));values|={'lift_event':lift['id'],'solar_approach':approach['id']}
  else:raise ValueError('UNDECLARED_WORLD_PREDICATE')
  claim(st,row,step,pred,truth,**values)
 elif family=='COMPARE_PHYSICAL':
  a=current_anchor(st,step);w,g=generation(st,step,a);old,stop=old_end(st,step);pred=op['predicate'];values={'new_wind':w['id'],'preceding_wind':old['id'],'anchor':a['id'],'generation_event':g['id'],'old_cessation':stop['id'],'new_generation_phase':g['phase'],'old_cessation_phase':stop['phase'],'new_source':w['source'],'old_source':old['source']}
  if pred=='ADJACENT_SOURCE':
   use(step,'same_observer_horizon_adjacency',{'type':'ObserverHorizon','horizon':'H','observer':'O','adjacent':['P','Q']},st['producer'].get('world'));truth=w['source']!=old['source'] and {w['source'],old['source']}=={'P','Q'}
  elif pred=='DISTINCT_IDENTITY':truth=w['id']!=old['id']
  elif pred=='CESSATION_BEFORE_GENERATION':truth=stop['phase']<g['phase']
  elif pred=='SOLAR_MATERIAL_ORIGIN':
   lift,approach,truth=causal_origin(st,step,w,g);values|={'lift_event':lift['id'],'solar_approach_event':approach['id']}
  elif pred=='DISTINCT_IDENTITY_AND_ORDER':truth=w['id']!=old['id'] and stop['phase']<g['phase']
  elif pred=='GENERATION_AT_OR_BEFORE_CURRENT_PHASE':use(step,'current_phase',{'type':'PhaseCursor','phase':st['phase']},st['producer'].get('phase'));truth=g['phase']<=st['phase']
  else:raise ValueError('UNDECLARED_COMPARISON')
  claim(st,row,step,pred,truth,**values)
 elif family=='SEAL_SUCCESSION':
  a=current_anchor(st,step);w,g=generation(st,step,a);old,stop=old_end(st,step);lift,approach,origin=causal_origin(st,step,w,g)
  for cid in st['claims']:use(step,'written_world_condition_or_comparison',cid)
  truth=(w['id']!=old['id'] and stop['phase']<g['phase'] and w['source']!=old['source'] and {w['source'],old['source']}=={'P','Q'} and origin)
  claim(st,row,step,'SOLAR_SUCCESSOR_OF',truth,new_wind=w['id'],previous_wind=old['id'],anchor=a['id'],prior_cessation=stop['id'],generation_event=g['id'],old_source=old['source'],new_source=w['source'],old_cessation_phase=stop['phase'],new_generation_phase=g['phase'],causal_chain=[approach['id'],lift['id'],g['id']],comparison_and_condition_ids=list(st['claims']))
 elif family=='BEGIN_NEXT_SUCCESSION':
  a=current_anchor(st,step);w,g=generation(st,step,a)
  if w['status']!='BLOWING':raise ValueError('NEXT_CASE_REQUIRES_GENERATED_PARTICIPANT_STILL_BLOWING')
  st['old']=w['id'];st['producer']['old']=sid;st['episode']+=1;st['claims']=[];st['cursor']=w['source'];st['producer']['cursor']=sid
  step['returns'].append({'type':'EpisodeReference','episode':st['episode'],'same_physical_predecessor':w['id'],'input_generation_event':g['id'],'input_anchor':a['id'],'retained_phase':st['phase'],'retained_source':w['source'],'source_group_id':sid})
 else:raise ValueError('UNDECLARED_FAMILY')
 return step

for reader in ['ZL3b','IT2a','RF1b']:
 st=blank(reader)
 for native in [r for r in source['rows'] if r['edition']==reader]:
  r=copy.deepcopy(native);raw=r['ivtff_group_raw'];entry=dictionary.get(raw);r.update({'entry_id':entry['entry_id'] if entry else None,'interpretation':copy.deepcopy(entry),'cost':{'dictionary_entry':entry['entry_id'] if entry else None,'kind':entry.get('price','INITIAL_CORE_EXACT_VALUE') if entry else 'UNASSIGNED_UNKNOWN'},'state_before':snap(st),'arguments':[],'returns':[],'substeps':[],'consumer_source_ids':[]})
  if entry is None:
   r['status']='UNKNOWN';r['reason']='UNASSIGNED_EXACT_FORM_NOT_INERT';st['unknown_rows'].append(r['source_group_id'])
  elif entry['family']!='CASE_SETUP' and not st['initialized']:
   r['status']='BLOCKED_MISSING_INITIAL_INPUTS';r['reason']='NO_EXPLICIT_INITIAL_CONDITIONAL_CASE';r['unresolved_prior_unknown_rows']=list(st['unknown_rows'])
  elif entry['family']!='CASE_SETUP' and st['unknown_rows']:
   r['status']='BLOCKED_UNPROVEN_UNKNOWN_BRIDGE';r['reason']='NO_FREE_CARRY_ACROSS_UNKNOWN_ROWS';r['unknown_bridge_source_ids']=list(st['unknown_rows']);r['unknown_bridge_row_count']=len(st['unknown_rows']);r['available_but_unproven_references']={'selected_wind':st['selected'],'old_wind':st['old'],'anchor':st['anchor'],'phase':st['phase'],'cursor':st['cursor']}
  elif entry['family']!='CASE_SETUP' and st['semantic_barrier']:
   r['status']='BLOCKED_AFTER_MISSING_INPUT';r['reason']=st['semantic_barrier']
  else:
   try:
    ops=entry['operations'] if entry['family']=='EXACT_SEQUENCE' else [entry]
    for op in ops:
     step=operate(st,r,op);r['substeps'].append(step);r['arguments'].extend(copy.deepcopy(step['arguments']));r['returns'].extend(copy.deepcopy(step['returns']))
    false=[x for x in r['returns'] if x.get('type')=='WorldPredicate' and not x['truth_under_declared_inputs']]
    r['status']='CONTRADICTION' if false else 'ACCOUNTED_C0';r['false_world_predicates']=false
   except ValueError as error:
    st['semantic_barrier']=r['source_group_id']+':'+str(error);r['status']='PARTIAL_MISSING_INPUT';r['reason']=str(error)
  r['state_after']=snap(st);r['delta']={k:{'before':r['state_before'].get(k),'after':v} for k,v in r['state_after'].items() if r['state_before'].get(k)!=v};rows.append(r)

# Source conservation and actual producer/consumer edges. No origin ID is a meaning-selection key.
byid={r['source_group_id']:r for r in rows};consumers=collections.defaultdict(set)
def nested(x):
 if isinstance(x,dict):
  found={x[k] for k in ('source_group_id','producer_source_id') if x.get(k) in byid}
  for v in x.values():found|=nested(v)
  return found
 if isinstance(x,list):
  found=set()
  for v in x:found|=nested(v)
  return found
 return set()
for r in rows:
 for arg in r['arguments']:
  ids=nested(arg['value'])|set(arg['producer_source_ids']);arg['producer_source_ids']=sorted(ids)
  for sid in ids:
   if sid in byid and sid!=r['source_group_id']:consumers[sid].add(r['source_group_id'])
for r in rows:
 r['consumer_source_ids']=sorted(consumers[r['source_group_id']])
 if r['status']=='ACCOUNTED_C0' and not r['consumer_source_ids']:r['terminal_contribution']='Terminal physical world proposition or reference focus, explicitly visible; not asserted as a later discriminator.'
assert len(rows)==473 and len(byid)==473
assert all(all(byid[r['source_group_id']][k]==v for k,v in r.items()) for r in source['rows'])
primary=[]
for reader in ['IT2a','ZL3b','RF1b']:
 for block in ['N','E']:
  rr=[r for r in rows if r['edition']==reader and r['block']==block];bad=next((r for r in rr if r['status']!='ACCOUNTED_C0'),None)
  primary.append({'reader':reader,'block':block,'native_ids':[r['source_group_id'] for r in rr],'count':len(rr),'accounted_count':sum(r['status']=='ACCOUNTED_C0' for r in rr),'complete':bad is None,'status':'COMPLETE_CONDITIONAL_C0' if bad is None else 'PARTIAL','first_barrier':{'source_group_id':bad['source_group_id'],'raw':bad['ivtff_group_raw'],'status':bad['status'],'reason':bad.get('reason')} if bad else None,'scope':'E is explicit paid continuation of N, not independent unit premise or physical confirmation' if block=='E' else 'lexical sain opens generic case; outside prefix is not presumed inert'})

# Manual contribution gate: keep reference/focus outputs that are overwritten unused.
retention_gaps=[]
for r in rows:
 if r['block'] in ('N','E') and r['status']=='ACCOUNTED_C0' and not r['consumer_source_ids'] and any(x.get('type') in ('WindAnchor','SourceFocus','PhysicalWindReference') for x in r['returns']):
  r.pop('terminal_contribution',None)
  r['contribution_status']='UNUSED_REFERENCE_OUTPUT_BEFORE_OVERWRITE'
  gap={'source_group_id':r['source_group_id'],'raw':r['ivtff_group_raw'],'returned_types':[x.get('type') for x in r['returns']],'reason':'Written reference/focus has no actual later consumer; known overwrite or native uncertainty leaves retention unestablished. No reader/constructor repair.'}
  retention_gaps.append(gap)
for unit in primary:
 unit['operational_complete']=unit['complete'];unit['operational_first_barrier']=unit['first_barrier']
 unit['strict_contribution_gaps']=[x for x in retention_gaps if byid[x['source_group_id']]['edition']==unit['reader'] and byid[x['source_group_id']]['block']==unit['block']]
 if unit['strict_contribution_gaps']:
  unit['complete']=False;unit['status']='PARTIAL_STRICT_CONTRIBUTION_GATE';unit['first_barrier']=unit['strict_contribution_gaps'][0]

# Source uncertainty is a paid boundary hypothesis, never a transcription repair.
uncertain_seams=[];boundary_assumptions=[]
for reader in ['IT2a','ZL3b','RF1b']:
 rr=[r for r in rows if r['edition']==reader]
 for index,left in enumerate(rr[:-1]):
  if left['right_separator']!='UNCERTAIN_SMALL_SPACE':continue
  right=rr[index+1]
  assert left['locus']==right['locus']
  executed=left['status']=='ACCOUNTED_C0' and right['status']=='ACCOUNTED_C0'
  seam={'id':'B_BOUNDARY_'+str(len(uncertain_seams)+1),'left_source_id':left['source_group_id'],'right_source_id':right['source_group_id'],'left_raw':left['ivtff_group_raw'],'right_raw':right['ivtff_group_raw'],'reader':reader,'block':left['block'],'native_separator':left['right_separator'],'execution_uses_separate_lexical_boundary':executed,'assumption':'Provisional separate lexical boundary at native small gap; combined hardchunk reading remains unresolved.' if executed else None,'price':'ONE_SOURCE_BOUNDARY_ASSUMPTION' if executed else 'UNRESOLVED_NO_EXECUTION_ASSUMPTION'}
  uncertain_seams.append(seam)
  if executed:
   boundary_assumptions.append(seam)
   for r in [left,right]:r.setdefault('boundary_assumption_ids',[]).append(seam['id'])
for unit in primary:
 unit['boundary_assumption_ids']=[x['id'] for x in boundary_assumptions if x['reader']==unit['reader'] and x['block']==unit['block']]
 if unit['boundary_assumption_ids'] and unit['complete']:unit['status']='COMPLETE_CONDITIONAL_C0_WITH_PAID_UNCERTAIN_BOUNDARIES'

repeats=[]
for raw,entry in dictionary.items():
 rr=[r for r in rows if r['ivtff_group_raw']==raw]
 repeats.append({'raw_form':raw,'entry_id':entry['entry_id'],'occurrences':len(rr),'exact_positions':[r['source_group_id'] for r in rr],'same_entry_all_occurrences':all(r['interpretation']==entry for r in rr),'statuses':dict(collections.Counter(r['status'] for r in rr)),'outside_primary_positions':[r['source_group_id'] for r in rr if r['block'] not in ('N','E')]})
shared=[]
for r in rows:
 if r['ivtff_group_raw'] not in ('aiin','daiin','shodaiin','oraiin','shedaiin'):continue
 anchors=[x for x in r['returns'] if x.get('type')=='WindAnchor']
 for anchor in anchors:
  consumers_of_anchor=[other['source_group_id'] for other in rows if any(isinstance(arg['value'],dict) and arg['value'].get('id')==anchor['id'] for arg in other['arguments']) and other['source_group_id']!=r['source_group_id']]
  step=next(x for x in r['substeps'] if x['family']=='A_N_ANCHOR')
  shared.append({'source_group_id':r['source_group_id'],'raw_form':r['ivtff_group_raw'],'interface_id':'B_A_N_ANCHOR','arguments':step['arguments'],'returned_value':anchor,'consumer_source_ids':consumers_of_anchor,'effect':'Written participant/source/phase/provenance binding required by physical comparisons or withdrawal; no selector-to-anchor automatic cast. Truth of manuscript meaning is not implied.','status':r['status'],'formal_parts':r['interpretation'].get('parts')})
 if not anchors:shared.append({'source_group_id':r['source_group_id'],'raw_form':r['ivtff_group_raw'],'interface_id':'B_A_N_ANCHOR','arguments':r['arguments'],'returned_value':None,'consumer_source_ids':[],'effect':'No execution due explicit missing inputs/unknown continuity; not a successful shared-part use.','status':r['status'],'formal_parts':r['interpretation'].get('parts')})
mandatory=[r['source_group_id'] for r in rows if r['locus']=='f85r2.13']
unknown=collections.Counter(r['edition'] for r in rows if r['status']=='UNKNOWN');coverage=collections.Counter((r['edition'],r['status']) for r in rows)
result={'schema':'GDT1131_B_ACCOUNT_v1','candidate_id':'B','status':'PARTIAL_STRICT_WHOLE_ACCOUNT_IT_N_COMPLETE_E_OPERATIONAL_WITH_UNUSED_REFERENCES','source_sha256':sha('src/SOURCE.json'),'constructor_sha256':sha('src/B_CONSTRUCTORS.json'),'extension_sha256':sha('src/B_EXTENSIONS.json'),'dictionary':dictionary,'rows':rows,'primary_units':primary,'shared_part_uses':shared,'strict_contribution_gaps':retention_gaps,'world_propositions':all_claims,'physical_events':all_events,'physical_anchors':all_anchors,'types':ext['typed_schemas'],'costs':{'initial':f['initial_costs'],'added_exact_forms':len(ext['added_exact_forms']),'total_assigned_exact_forms':len(dictionary),'additional':ext['additional_prices'],'initial_opaque_constants':8,'core_families':12,'additional_constructor_families':0,'fresh_physical_participant_factory':'two generated IDs v1/v2 in IT case, not new opaque lexical names','initial_setup_scope_opening':'sain explicitly supersedes unknown outside prefix; no boundary reset','N_to_E_reference_bridge_count':1,'unknown_carry_assumptions_used':0,'rows_blocked_by_unproved_unknown_bridge':sum(r['status']=='BLOCKED_UNPROVEN_UNKNOWN_BRIDGE' for r in rows),'known_entry_unknown_bridge_row_counts':[{'source_group_id':r['source_group_id'],'count':r.get('unknown_bridge_row_count',0),'intervening_unknown_ids':r.get('unknown_bridge_source_ids',[])} for r in rows if r['status']=='BLOCKED_UNPROVEN_UNKNOWN_BRIDGE'],'unused_instruction_count':0,'unused_reference_outputs':retention_gaps,'instructions':'No imperative output in this candidate; all phase changes are executed conditional-event clauses.','aliases':'Literal aliases all priced separately; no automatic alternate substitution.','semantic_null_rules':0,'global_new_parser':False},'recurrence_audit':repeats,'mandatory_or_shedy_tedy_case':{'source_ids':mandatory,'row_results':[{'source_group_id':sid,'raw':byid[sid]['ivtff_group_raw'],'entry_id':byid[sid]['entry_id'],'status':byid[sid]['status'],'unknown_bridge_row_count':byid[sid].get('unknown_bridge_row_count',0)} for sid in mandatory],'interpretation_limit':'All assigned interfaces are retained. Unknown .12 and later context prevent carrying a case into .13; no asserted conversion/type success. IDEA582 original or Assertable / shedy DescriptionRef failure remains unchanged. Literal RF marked form is not equated with shedy.'},'source_conservation':{'rows':473,'all12_native_fields_preserved':True,'reader_counts':dict(collections.Counter(r['edition'] for r in rows)),'physical_leaf':'f85','independent_confirmation_leaves':[],'sealed':['f84','f84r'],'unadmitted':['f116v']},'literal_coverage_by_reader_status':[{'reader':k[0],'status':k[1],'rows':v} for k,v in sorted(coverage.items())],'same_world_counterfactual':{'statement':'Keeping predecessor identity/source/frame and solar phases fixed, replace the purported new participant by continued same-ID blowing of the predecessor. This fails distinct-ID and prior-cessation/generation claims; replace adjacent source by the same/nonadjacent source and adjacency claims fail; replace solar-lift origin by unexplained generation and causal claims fail. These are authored physical consequences, not a manuscript-owned meaning test.','IT_nonseed_written_bindings':['IT2a|f85r2.5|G001','IT2a|f85r2.5|G002','IT2a|f85r2.5|G003','IT2a|f85r2.6|G001','IT2a|f85r2.8|G006','IT2a|f85r2.10|G003','IT2a|f85r2.11|G001','IT2a|f85r2.11|G004'],'remaining_equivalence':'An explicit static two-time-state relation with the same participant IDs, before/after activity, generation/cause and adjacency represents the same conditional content. Fresh factories and anchors do not supply a semantic advantage.'},'meaning_ceiling':'All meanings are C0. No actual storm, direction name, water, wind-name lexeme, confirmed translation, statistic, relation score, reserve, physical independent witness or predecessor reopening. N/E completeness is conditional on paid initial solar frame and one explicit cross-unit bridge; source preservation/replay cannot establish truth or semantic selection.','other_authors_read':False,'generated_from_extension_frozen_utc':ext['created_utc']}
result['native_uncertain_seams']=uncertain_seams
result['costs']['postfreeze_source_boundary_assumptions']=boundary_assumptions
result['costs']['source_boundary_assumption_count']=len(boundary_assumptions)
result['meaning_ceiling']+=' ZL execution additionally conditions on five individually paid uncertain native small-gap boundaries (three N, two E); no uniquely established segmentation.'
(BASE/'artifacts/B_ACCOUNT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'primary_units':primary,'source_status_counts':result['literal_coverage_by_reader_status'],'shared_anchor_uses':len(shared),'account_sha256':sha('artifacts/B_ACCOUNT.json')},ensure_ascii=False,indent=2))
