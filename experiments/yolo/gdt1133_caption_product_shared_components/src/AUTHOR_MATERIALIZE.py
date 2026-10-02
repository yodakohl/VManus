#!/usr/bin/env python3
"""One frozen finite semantic account, not a parser or general decoder."""
import collections,copy,hashlib,json,pathlib
B=pathlib.Path(__file__).resolve().parents[1]
def load(p):return json.loads((B/p).read_text())
def sha(p):return hashlib.sha256((B/p).read_bytes()).hexdigest()
core=load('src/CORE.json');ext=load('src/EXTENSIONS.json');src=load('src/SOURCE.json');receipt=load('artifacts/AUTHOR_INITIAL_FREEZE_RECEIPT.json')
assert sha('src/CORE.json')==ext['core_sha256']==receipt['files']['src/CORE.json']
assert sha('src/EXTENSIONS.json')==receipt['files']['src/EXTENSIONS.json']
assert sha('src/SOURCE.json')==core['source_sha256']
objects={};steps=[];groups=[];chunks=[];seq=collections.Counter()
def make(reader,typ,sid,**kw):
 seq[reader]+=1;v={'id':reader+':V'+str(seq[reader]),'type':typ,'producer_source_ids':sid if isinstance(sid,list) else [sid],**copy.deepcopy(kw)};objects[v['id']]=v;return v

def arg(stp,role,v):
 if v is None:raise ValueError('MISSING_'+role.upper())
 stp['arguments'].append({'role':role,'value':copy.deepcopy(v)});return v

def need(st,key,stp):return arg(stp,key,st.get(key))
def ret(stp,v):stp['returns'].append(copy.deepcopy(v));return v

def proposition(st,stp,sid,name,truth,**kw):
 if not truth:raise ValueError('CONTRADICTED_'+name)
 return ret(stp,make(st['reader'],'WorldPredicate',sid,predicate=name,truth_under_declared_inputs=True,mode='GENERIC_CONDITIONAL',**kw))

caption={}
for native in src['caption_native_rows']:
 reader=native['edition'];spec=src['caption'][reader];sid=[native['source_group_id']];value=None;rr={'native':copy.deepcopy(native),'fixed_units':spec['fixed_units'],'substeps':[],'status':'ACCOUNTED_C0','returns':[],'arguments':[],'is_caption':True}
 for i,u in enumerate(spec['fixed_units']):
  stp={'source_ids':sid,'unit_index':i,'unit':u,'function':core['fixed_caption_functions'].get(u,core['unit_functions'].get(u)),'arguments':[],'returns':[],'is_caption':True}
  try:
   if u=='l':
    owner=arg(stp,'paid_picture_source_owner',{'type':'OwnerSourceRelation','owner':'Owner240','source_kind':'K19','status':'PAID_C0'})
    value=ret(stp,make(reader,'SourceKindRef',sid,kind=owner['source_kind'],owner=owner['owner'],paid_picture_source_slot=True))
   elif u=='or':
    x=arg(stp,'SourceKindRef',value)
    if x['type']!='SourceKindRef':raise ValueError('FROM_SOURCE_INPUT_TYPE')
    value=ret(stp,make(reader,'FromSourceSpec',sid,source_kind=x['kind'],input_source_ref=x))
   elif u=='al':
    x=arg(stp,'FromSourceSpec',value)
    if x['type']!='FromSourceSpec':raise ValueError('DECOCTION_KIND_INPUT_TYPE')
    value=ret(stp,make(reader,'MaterialKindSpec',sid,kind='S19',source_kind=x['source_kind'],form='DECOCTION',provenance=x,physical_instance=None))
   elif u=='ody':
    x=arg(stp,'MaterialKindSpec',value)
    if x['type']!='MaterialKindSpec':raise ValueError('APPELLATION_INPUT_TYPE')
    value=ret(stp,make(reader,'Appellation',sid,denotation=x['kind'],source_kind=x['source_kind'],form=x['form'],material_spec=x,owner='Owner240'))
   else:raise ValueError('RF_OS_IS_ASSERT_INPUT_SOURCE_NOT_OR_NO_BOTANICAL_BODY_INPUT_IN_CAPTION')
   stp['status']='ACCOUNTED_C0'
  except ValueError as e:
   stp['status']='PARTIAL_MISSING_INPUT';stp['reason']=str(e);rr['status']='PARTIAL_MISSING_INPUT';rr['first_barrier']={'unit':u,'unit_index':i,'reason':str(e)}
  rr['substeps'].append(stp);steps.append(stp);rr['returns']+=copy.deepcopy(stp['returns']);rr['arguments']+=copy.deepcopy(stp['arguments'])
  if stp['status']!='ACCOUNTED_C0':break
 caption[reader]=value if value and value['type']=='Appellation' else None;groups.append(rr)

def init(reader):return {'reader':reader,'initialized':False,'w':None,'water':None,'wet':None,'p':None,'d':None,'selected':None,'use_selected':None,'source_ref':None,'from_spec':None,'e':None,'definition':None,'body_appellation':None,'drink':None,'caption_appellation':caption[reader],'events':[],'claims':[],'unknown_ids':[],'barrier':None}
def state(st):return {'initialized':st['initialized'],'w':st['w'],'p':st['p'],'d':st['d'],'selected':st['selected'],'use_selected':st['use_selected'],'e':st['e'],'source_ref':st['source_ref'],'from_spec':st['from_spec'],'definition':st['definition'],'body_appellation':st['body_appellation'],'drink':st['drink'],'event_ids':[v['id'] for v in st['events']],'unknown_ids':st['unknown_ids'],'barrier':st['barrier']}

def operate(st,sid,u,index):
 fn=core['unit_functions'][u];x={'source_ids':sid,'unit_index':index,'unit':u,'function':fn,'arguments':[],'returns':[],'is_caption':False}
 if fn=='OPEN_BOTANICAL_CASE':
  if st['initialized']:raise ValueError('NO_UNWRITTEN_CASE_RESET')
  owner=arg(x,'paid_owner_source_coidentity',{'type':'OwnerSourceRelation','owner':'Owner240','caption_source_kind':'K19','body_input_kind':'K19','status':'PAID_C0'})
  st['w']=ret(x,make(st['reader'],'BotanicalInput',sid,physical_id='w',source_kind=owner['body_input_kind'],phase='SOLID_PHASE',mode='GENERIC_CONDITIONAL'));st['selected']=st['w'];st['initialized']=True
 elif not st['initialized']:raise ValueError('NO_WRITTEN_BOTANICAL_INPUT')
 elif fn in ['SOURCE_OF_WRITTEN_INPUT','SOURCE_OF_SELECTED_MATERIAL','CAPTION_SOURCE']:
  if fn=='CAPTION_SOURCE':v=arg(x,'explicit_owner_slot',{'type':'OwnerRef','owner':'Owner240','source_kind':'K19'})
  else:v=need(st,'w' if fn=='SOURCE_OF_WRITTEN_INPUT' else 'selected',x)
  k=v.get('source_kind');st['source_ref']=ret(x,make(st['reader'],'SourceKindRef',sid,kind=k,source_material=v,owner='Owner240'))
  if fn=='SOURCE_OF_WRITTEN_INPUT':proposition(st,x,sid,'BODY_INPUT_SOURCE',k=='K19',input_id=st['w']['id'],source_kind=k)
 elif fn=='FROM_SOURCE':
  v=need(st,'source_ref',x)
  if v['type']!='SourceKindRef':raise ValueError('FROM_SOURCE_INPUT_TYPE_NO_IDEMPOTENCE')
  st['from_spec']=ret(x,make(st['reader'],'FromSourceSpec',sid,source_kind=v['kind'],input_source_ref=v))
 elif fn=='INTRODUCE_WATER':st['water']=ret(x,make(st['reader'],'WaterInput',sid,physical_id='h',kind='WATER_KIND'))
 elif fn=='WET_INPUT':
  w=need(st,'w',x);h=need(st,'water',x);st['wet']=ret(x,make(st['reader'],'PhysicalEvent',sid,event='WET',input=w,water=h,mode='GENERIC_CONDITIONAL'));st['events'].append(st['wet'])
 elif fn=='BOIL_CURRENT_MIXTURE':
  wet=need(st,'wet',x);w=need(st,'w',x);h=need(st,'water',x);provenance=arg(x,'written_source_provenance',st['from_spec'] or st['source_ref'])
  if provenance.get('source_kind',provenance.get('kind'))!=w['source_kind']:raise ValueError('PREPARATION_SOURCE_MISMATCH')
  prior=[]
  if st['p']:prior=[need(st,'p',x),need(st,'d',x)]
  e=ret(x,make(st['reader'],'PhysicalEvent',sid,event='BOIL_SEPARATE' if not prior else 'REBOIL_SAME_OUTPUTS',input=w,water=h,wet_event=wet,source_kind=w['source_kind'],provenance=provenance,prior_outputs=prior,form='DECOCTION',mode='GENERIC_CONDITIONAL'))
  st['e']=e;st['events'].append(e)
  st['p']=ret(x,make(st['reader'],'PhysicalMaterial',sid,physical_id='p',source_kind=w['source_kind'],phase='SOLID_PHASE',form='BOILED_SOLID',origin_input=w,preparation=e,kind=None))
  st['d']=ret(x,make(st['reader'],'PhysicalMaterial',sid,physical_id='d',source_kind=w['source_kind'],phase='LIQUID_PHASE',form='DECOCTION',origin_input=w,preparation=e,kind=st['d'].get('kind') if st['d'] else None))
  # Physical IDs survive actual reboil; reference values and preparation histories update.
 elif fn in ['VIEW_SOLID','VIEW_LIQUID','SELECT_LIQUID_FOR_USE','MARK_OTHER_SOLID_OUTPUT']:
  if fn=='VIEW_SOLID':v=arg(x,'current_solid',st['p'] or st['w']);st['selected']=v
  elif fn=='MARK_OTHER_SOLID_OUTPUT':
   v=need(st,'p',x);d=need(st,'d',x);proposition(st,x,sid,'SOLID_IS_OTHER_OUTPUT',v['physical_id']!=d['physical_id'],solid=v,liquid=d);return x
  else:v=need(st,'d',x);st['selected']=v
  out=ret(x,make(st['reader'],'MaterialReference',sid,physical_id=v['physical_id'],source_kind=v['source_kind'],phase=v['phase'],form=v.get('form','RAW_BOTANICAL'),material=v));st['selected']=out
  if fn=='SELECT_LIQUID_FOR_USE':st['use_selected']=out;proposition(st,x,sid,'SELECTED_LIQUID_FOR_DRINKING',v['phase']=='LIQUID_PHASE',selected=out)
  else:proposition(st,x,sid,'CURRENT_SOLID_VIEW' if fn=='VIEW_SOLID' else 'CURRENT_LIQUID_VIEW',True,material=out)
 elif fn=='RETAIN_SELECTED_OUTPUT':v=need(st,'selected',x);proposition(st,x,sid,'RETAIN_THIS_SELECTED_MATERIAL',True,material=v)
 elif fn in ['ASSERT_OUTPUT_DISTINCTION','ASSERT_OUTPUT_PROVENANCE','ASSERT_DECOCTION_FORM','ASSERT_INPUT_SOURCE']:
  if fn=='ASSERT_INPUT_SOURCE':w=need(st,'w',x);proposition(st,x,sid,'INPUT_HAS_SOURCE_K19',w['source_kind']=='K19',input=w)
  elif fn=='ASSERT_DECOCTION_FORM':d=need(st,'d',x);e=need(st,'e',x);proposition(st,x,sid,'LIQUID_FORM_IS_PERFORMED_DECOCTION',d['form']==e['form']=='DECOCTION',liquid=d,preparation=e)
  else:
   p=need(st,'p',x);d=need(st,'d',x);e=need(st,'e',x);proposition(st,x,sid,'DISTINCT_SOLID_LIQUID' if fn=='ASSERT_OUTPUT_DISTINCTION' else 'SAME_INPUT_PREPARATION_PROVENANCE',p['physical_id']!=d['physical_id'] and p['phase']=='SOLID_PHASE' and d['phase']=='LIQUID_PHASE',solid=p,liquid=d,preparation=e)
 elif fn=='EXPANDED_CAPTION_DEFINITION':
  d=need(st,'d',x);e=need(st,'e',x);pr=need(st,'from_spec',x);chosen=need(st,'use_selected',x);cap=need(st,'caption_appellation',x)
  cref=ret(x,make(st['reader'],'CaptionDenotationReference',sid,owner='Owner240',denotation=cap['denotation'],source_kind=cap['source_kind'],form=cap['form'],caption_appellation=cap));arg(x,'written_caption_denotation_reference',cref)
  if chosen['physical_id']!=d['physical_id'] or d['phase']!='LIQUID_PHASE':raise ValueError('WRITTEN_OUTPUT_SELECTION_NOT_LIQUID_D')
  if pr['source_kind']!=d['source_kind'] or cap['source_kind']!=pr['source_kind'] or cap['form']!=d['form'] or d['form']!=e['form']:raise ValueError('EXPANDED_DEFINITION_SOURCE_FORM_MISMATCH')
  if cap['denotation']!='S19':raise ValueError('CAPTION_DENOTATION_NOT_MATERIAL_KIND')
  st['definition']=ret(x,make(st['reader'],'MaterialKindSpec',sid,kind=cref['denotation'],source_kind=pr['source_kind'],form=d['form'],provenance=pr,physical_output=d,preparation=e,caption_reference=cref,selected_output=chosen));st['d']['kind']=st['definition']['kind'];proposition(st,x,sid,'KIND_OF_SELECTED_DECOCTION_IS_CAPTION_DENOTATION',True,definition=st['definition'])
 elif fn=='APPELLATION':
  v=need(st,'definition',x)
  if v['type']!='MaterialKindSpec':raise ValueError('APPELLATION_REQUIRES_MATERIAL_KIND_SPEC')
  st['body_appellation']=ret(x,make(st['reader'],'Appellation',sid,denotation=v['kind'],source_kind=v['source_kind'],form=v['form'],material_spec=v,owner='Owner240'))
 elif fn=='ASSERT_LIQUID_AND_AVAILABLE_APPELLATION':
  d=need(st,'d',x);kw={'liquid':d}
  if st['body_appellation']:
   ap=need(st,'body_appellation',x);kw['read_returned_body_appellation']=ap
   if not(ap['denotation']==d['kind'] and ap['source_kind']==d['source_kind'] and ap['form']==d['form']):raise ValueError('APPELLATION_NOT_THIS_ACTUAL_LIQUID')
  proposition(st,x,sid,'ACTUAL_LIQUID_WITH_EXPLICIT_APPELLATION_IF_WRITTEN',d['phase']=='LIQUID_PHASE',**kw)
 elif fn=='DRINK_LIQUID_PORTION':
  d=need(st,'d',x);chosen=need(st,'use_selected',x)
  if d['physical_id']!=chosen['physical_id'] or chosen['phase']!='LIQUID_PHASE':raise ValueError('DRINK_REQUIRES_EXPLICIT_LIQUID_SELECTION')
  st['drink']=ret(x,make(st['reader'],'PhysicalEvent',sid,event='DRINK_POSITIVE_PORTION',liquid=d,selected_output=chosen,amount='UNSPECIFIED_POSITIVE_PORTION',mode='GENERIC_CONDITIONAL'));st['events'].append(st['drink'])
 elif fn=='CONFIRM_SAME_LIQUID_CONSUMPTION':
  e=need(st,'drink',x);d=need(st,'d',x);proposition(st,x,sid,'CONTINUATION_IS_SAME_DRUNK_LIQUID',e['liquid']['physical_id']==d['physical_id'],liquid=d,drink_event=e)
 else:raise ValueError('UNIMPLEMENTED_FROZEN_FAMILY_'+fn)
 return x

final_states={}
for reader in src['readers']:
 st=init(reader['edition'])
 for line in sorted(reader['lines'],key=lambda v:int(v['locus'].split('.')[-1])):
  for chunk in line['chunks']:
   sid=chunk['ids'];key=' + '.join(chunk['raw_groups']);license=ext['licenses'][key];r={'native_chunk':copy.deepcopy(chunk),'locus':line['locus'],'edition':reader['edition'],'license_id':key,'fixed_units':chunk['units'],'arguments':[],'returns':[],'substeps':[],'is_caption':False,'state_before':copy.deepcopy(state(st))}
   if license['operations'] is None:r['status']='UNKNOWN';r['reason']='UNPARSED_OR_UNASSIGNED_FIXED_FINAL_UNITS';st['unknown_ids']+=sid
   elif st['unknown_ids']:r['status']='BLOCKED_UNKNOWN_CONTINUITY';r['reason']='NO_CARRY_ACROSS_UNRESOLVED_RAW_GROUPS';r['unknown_ids']=list(st['unknown_ids'])
   elif st['barrier']:r['status']='BLOCKED_AFTER_FIRST_TYPED_BARRIER';r['reason']=st['barrier']
   else:
    r['status']='ACCOUNTED_C0'
    for i,u in enumerate(chunk['units']):
     try:x=operate(st,sid,u,i);x['status']='ACCOUNTED_C0'
     except ValueError as e:
      x={'source_ids':sid,'unit':u,'unit_index':i,'function':core['unit_functions'][u],'arguments':[],'returns':[],'status':'PARTIAL_MISSING_INPUT','reason':str(e),'is_caption':False};r['status']='PARTIAL_MISSING_INPUT';r['reason']=str(e);st['barrier']={'source_ids':sid,'unit':u,'reason':str(e)}
     r['substeps'].append(x);steps.append(x);r['arguments']+=copy.deepcopy(x['arguments']);r['returns']+=copy.deepcopy(x['returns'])
     if x['status']!='ACCOUNTED_C0':break
   r['state_after']=copy.deepcopy(state(st));chunks.append(r)
   for native in chunk['source_rows']:groups.append({'native':copy.deepcopy(native),'fixed_units':chunk['units'],'native_chunk_ids':sid,'account_chunk_index':len(chunks)-1,'license_id':key,'status':r['status'],'reason':r.get('reason'),'arguments':copy.deepcopy(r['arguments']),'returns':copy.deepcopy(r['returns']),'is_caption':False})
 final_states[reader['edition']]=state(st)

# Actual downstream reads are object edges, not equality of independently rebuilt tags.
def ids(v):
 if isinstance(v,dict):
  z={v['id']} if v.get('id') in objects else set()
  for x in v.values():z|=ids(x)
  return z
 if isinstance(v,list):
  z=set()
  for x in v:z|=ids(x)
  return z
 return set()
consumers=collections.defaultdict(set)
for step in steps:
 for ar in step['arguments']:
  for oid in ids(ar['value']):
   if set(objects[oid]['producer_source_ids']).isdisjoint(step['source_ids']):consumers[oid].update(step['source_ids'])
for row in groups:
 row['consumer_source_ids']=sorted(set().union(*(consumers[v['id']] for v in row['returns'])) if row['returns'] else set())
 row['returned_value_consumers']=[{'value_id':v['id'],'type':v['type'],'consumer_source_ids':sorted(consumers[v['id']])} for v in row['returns']]
 if row['returns'] and not row['consumer_source_ids']:row['terminal_or_unused']='No later value consumer. Physical predicate/event may be a terminal contribution; reference-only unused results remain explicitly visible.'
reuse=[]
for step in steps:
 if step['unit'] in ['or','al','ody']:
  for v in step['returns']:
   reuse.append({'source_ids':step['source_ids'],'unit_index':step['unit_index'],'unit':step['unit'],'function':step['function'],'is_caption_seed':step['is_caption'],'actual_arguments':step['arguments'],'returned_value':v,'later_written_consumer_source_ids':sorted(consumers[v['id']]),'counts_for_nonseed_reuse':not step['is_caption'] and bool(consumers[v['id']])})
summary=[]
for reader in ['IT2a','RF1b','ZL3b']:
 rr=[r for r in groups if r['native']['edition']==reader and not r['is_caption']];bad=next((r for r in rr if r['status']!='ACCOUNTED_C0'),None)
 units=sorted({x['unit'] for x in reuse if x['counts_for_nonseed_reuse'] and x['source_ids'][0].startswith(reader+'|')})
 summary.append({'reader':reader,'native_body_groups':len(rr),'accounted_native_groups':sum(r['status']=='ACCOUNTED_C0' for r in rr),'full_body_operational':bad is None,'first_barrier':{'source_id':bad['native']['source_group_id'],'raw':bad['native']['ivtff_group_raw'],'status':bad['status'],'reason':bad['reason']} if bad else None,'nonseed_consumed_caption_functions':units,'required_two_functions_reached':len(units)>=2,'caption_complete':caption[reader] is not None})
assert len(groups)==233
native_source=[v for r in src['readers'] for l in r['lines'] for c in l['chunks'] for v in c['source_rows']]+src['caption_native_rows'];byid={r['native']['source_group_id']:r['native'] for r in groups}
assert len(byid)==len(native_source)==233
assert all(byid[n['source_group_id']]==n for n in native_source)
result={'schema':'GDT1133_AUTHOR_ACCOUNT_v1','status':'PARTIAL_ALL_READER_ACCOUNT_WITH_IT_OPERATIONAL_COMPONENT_REUSE_ATTEMPT','source_sha256':sha('src/SOURCE.json'),'core_sha256':sha('src/CORE.json'),'extensions_sha256':sha('src/EXTENSIONS.json'),'native_groups':groups,'chunks':chunks,'unit_steps':steps,'summary':summary,'actual_caption_function_reuse':reuse,'objects':objects,'final_states':final_states,'costs':ext['counts']|{'explicit_qol_atomic_predicates':2,'finite_alias_unit_assignments':core['unit_functions'],'paid_reference_and_scope_policies':core['paid_bindings'],'unknown_carry':0,'whole_episode_aliases':0,'new_parser':False,'no_body_al_final_unit':True,'unused_value_ids':[oid for oid in objects if not consumers[oid]],'terminal_predicates_not_automatically_instruction_gaps':True},'source_conservation':{'native_groups':233,'body_groups':230,'caption_groups':3,'every_native_field_unchanged':True,'every_fixed_final_unit_sequence_unchanged':True,'natural_line_execution_order':'Integer source locus order .1 through .13; original line/chunk data preserved. No semantic reset at line boundaries.'},'known_limits':['RF caption os not or and body d@222;/.1G004 unparsed','ZL @241;/.2G010 and other unparsed chunks stop continuity','No body al application; atomic dal not split','No global OR export, preposition proof or1131 OR-OR adapter','C2/body coidentity paid C0; no plant identification','Plant-name plus explicit preparation/definition remains wider rival','Full IT operational execution alone is not semantic completeness or translation','No historical two-fraction discard imported from II.107; actual output selection is written','Lightly cooked solid can share attributed loosening effect; no effect-based liquid identity used'],'other_C2_author_read':False,'generated_at_inventory_freeze_utc':ext['frozen_utc']}
# Retain wholly unconsumed reference expressions as strict contribution barriers.
whole_gaps=[]
for r in groups:
 if not r['is_caption'] and r['status']=='ACCOUNTED_C0' and not r['consumer_source_ids'] and not any(x['type'] in ['WorldPredicate','PhysicalEvent'] for x in r['returns']):
  gap={'source_id':r['native']['source_group_id'],'raw':r['native']['ivtff_group_raw'],'returned_types':[v['type'] for v in r['returns']],'reason':'Entire reference-only whole has no actual later written consumer; output overwritten. Frozen functions retained, no repair.'}
  whole_gaps.append(gap);r['strict_contribution_gap']=gap
for summary_unit in summary:
 summary_unit['wholly_unused_reference_gaps']=[g for g in whole_gaps if g['source_id'].startswith(summary_unit['reader']+'|')]
 summary_unit['strict_complete']=summary_unit['full_body_operational'] and not summary_unit['wholly_unused_reference_gaps'] and summary_unit['caption_complete']
result['status']='PARTIAL_REQUIRED_UNCONSUMED_WHOLES_AND_NATIVE_ALTERNATE_BARRIERS'
result['strict_whole_contribution_gaps']=whole_gaps
result['costs']['wholly_unconsumed_reference_count']=len(whole_gaps)
result['serialization']='Typed arguments/returns use compact ID plus actual scalar snapshots; object_table retains each typed payload and nested producer/value IDs. Compacting replaces repeated expansion only, not semantics or consumer edges.'
# Avoid exponential repetition of preparation provenance in snapshots and arguments.
def compact(v,keep_root=False):
 if isinstance(v,dict):
  if v.get('id') in objects and not keep_root:
   return {k:copy.deepcopy(x) for k,x in v.items() if not isinstance(x,(dict,list)) or k=='producer_source_ids'}|{'payload_lookup_id':v['id']}
  return {k:compact(x) for k,x in v.items()}
 if isinstance(v,list):return [compact(x) for x in v]
 return v
payloads={oid:compact(v,True) for oid,v in objects.items()}
result=compact(result)
result['objects']=payloads
(B/'artifacts/AUTHOR_ACCOUNT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'summary':summary,'account_sha256':sha('artifacts/AUTHOR_ACCOUNT.json'),'rows':len(groups),'chunks':len(chunks)},indent=2))
