#!/usr/bin/env python3
"""GDT1125 pre-open literal FW adapter.

The compact/pair_start, unit state, instruction/Plan/call/result transitions and
consumer ancestry blocks are mechanically copied from frozen FW_AUTHOR_BUILD.py
(270d116f889f7dc966e5590a319d61a2bb658496b8e97e0115042261bd03b765).
Changes: frozen-model dictionary/control/rule loading; F75V/F104V scope; gated
application packet IO; native-column constant; scoped reporting of the original
R13 readout exception and missing later consumer. No new lexical values, names,
parser, macro, context exception, donor result or reset. Successful transitions
retain the original operations, signatures and state. The original author file
is untouched. This adapter is not independent semantic or full-grammar validation.
"""
import csv
import hashlib
import json
import re
from pathlib import Path

EXPERIMENT = Path(__file__).resolve().parents[1]
ROOT = EXPERIMENT.parents[2]
MODEL_REL = 'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/FW_AUTHOR_METHOD.json'
MODEL_SHA256 = 'b02a2d38eaf1c8822d946761fb1727a23557686b589205d2b344f4f267bcfa09'
AUTHOR_BUILD_SHA256 = '270d116f889f7dc966e5590a319d61a2bb658496b8e97e0115042261bd03b765'
COPIED_CORE_SHA256 = '7e1ee22f8448fa0da9e0c6d67bdc34dfd5dd52c58d5b8b8db507adaefc6543b8'
SOURCE_COLUMNS = ['source_group_id','edition','locus','page','section','currier','hand','code','kind','grammar_scope','source_row_index','source_group_index','source_group_count','paragraph_start','paragraph_end','left_separator','right_separator','ivtff_group_raw']
ALLOWED_WINDOWS = {'FW_F75V_PREVIOUS':('f75v',38,42),'FW_F75V_CURRENT':('f75v',43,49),'FW_F104V_PREVIOUS':('f104v',19,21),'FW_F104V_CURRENT':('f104v',22,26)}

class ReadoutConflict(Exception):
    def __init__(self, source_id, operation, reason):
        self.source_id, self.operation, self.reason = source_id, operation, reason
        super().__init__(reason)

def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()

def main():
    # Gate before reading/materializing any application source bytes.
    spec_path = EXPERIMENT / 'src/SPEC.json'
    open_path = EXPERIMENT / 'artifacts/OPEN_RECEIPT.json'
    if not spec_path.is_file() or not open_path.is_file():
        raise SystemExit('PREOPEN_GATE_CLOSED: SPEC or OPEN_RECEIPT missing; no source read')
    spec_bytes = spec_path.read_bytes()
    spec = json.loads(spec_bytes)
    opening = json.loads(open_path.read_text())
    if spec.get('status') != 'PREOPEN_FROZEN':
        raise SystemExit('PREOPEN_GATE_CLOSED: SPEC status; no source read')
    if opening.get('status') != 'ROOT_EXPLICIT_APPLICATION_GO' or opening.get('spec_sha256') != sha_bytes(spec_bytes):
        raise SystemExit('PREOPEN_GATE_CLOSED: explicit opening/spec binding; no source read')
    source_sha = opening.get('source_packet_sha256')
    if not isinstance(source_sha,str) or not re.fullmatch('[0-9a-f]{64}',source_sha):
        raise SystemExit('PREOPEN_GATE_CLOSED: application packet hash missing; no source read')
    model_bytes = (ROOT / MODEL_REL).read_bytes()
    if sha_bytes(model_bytes) != MODEL_SHA256:
        raise SystemExit('FROZEN_MODEL_MISMATCH: no source read')
    model = json.loads(model_bytes)
    controls = model['controls']
    lexicon = model['dictionary']
    rules = model['rules']
    names = model['nominal_whitelist']
    assert len(lexicon)==214 and len(controls)==14 and len(rules)==29
    assert set(lexicon)==set(names)|set(controls)
    source_bytes = (EXPERIMENT / 'artifacts/APPLICATION_PACKET.json').read_bytes()
    if sha_bytes(source_bytes) != source_sha:
        raise SystemExit('OPEN_SOURCE_HASH_MISMATCH')
    packet = json.loads(source_bytes)
    assert set(packet['editions'])=={'ZL3b','IT2a','RF1b'}
    assert set(g['unit_id'] for g in packet['groups'])==set(ALLOWED_WINDOWS)
    assert len({g['source_group_id'] for g in packet['groups']})==len(packet['groups'])
    for g in packet['groups']:
        page,lo,hi=ALLOWED_WINDOWS[g['unit_id']]
        assert g['page']==page and g['locus'].startswith(page+'.')
        assert lo<=int(g['locus'].split('.')[1])<=hi
        assert all(k in g for k in SOURCE_COLUMNS)
    errors=[]
    def compact(x): return json.dumps(x,ensure_ascii=False,separators=(',',':'))
    def pair_start(gs,i):
        return (gs[i]['ivtff_group_raw']=='chey' and i+1<len(gs)
            and gs[i+1]['ivtff_group_raw']=='tal'
            and gs[i]['locus']==gs[i+1]['locus']
            and gs[i]['right_separator'] in ['DEFINITE_SPACE','UNCERTAIN_SMALL_SPACE']
            and gs[i+1]['left_separator']==gs[i]['right_separator'])

    rows=[]; unit_records=[]; plans={}; calls=[]
    nativecols=SOURCE_COLUMNS

    for side in ['F75V','F104V']:
     for ed in packet['editions']:
      for role in ['PREVIOUS','CURRENT']:
       uid='FW_'+side+'_'+role
       gs=[g for g in packet['groups'] if g['unit_id']==uid and g['edition']==ed]
       key=uid+'_'+ed
       if not gs:
        # IO capacity reporting only: there is no source state to invent.
        errors.append({'classification':'NO_CAPACITY_SOURCE_UNIT','unit':key,'source_id':None})
        unit_records.append({'unit_id':uid,'reader':ed,'key':key,'raw_groups':0,
          'mode':'DEFINE' if role=='PREVIOUS' else 'EXECUTE','first_barrier':None,
          'final_state':None,'steps':[],'nominal_documentation':[],
          'written_declarations':[],'input_record':None,'events':[],
          'result_records':[],'consumers':[],'closure':None,
          'whole_role_coverage':False,'named_material_translations':0,
          'native_paragraph_contract':ed!='RF1b','source_capacity':'NO_CAPACITY_SOURCE_UNIT'})
        continue
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
         raise ReadoutConflict(source, op, 'readout without a preceding ResultRecord')
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
        delta={};new_events=[]; args=[];before_event_ids={e['id'] for e in events}
        try:
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
          op=controls[w]
          if role=='PREVIOUS' and op in ['NOTE','CHECK_RECORD','STORE_RECORD'] and not steps:
           raise ReadoutConflict(sid, op, 'unbound abstract readout')
          st={'id':key+'__STEP'+str(len(steps)+1),
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
        except ReadoutConflict as failure:
         # A rejected signature leaves all existing partial state intact. No reset,
         # synthetic result, new input, producer or alternate operation is added.
         state['stopped']=True;state['barrier']=failure.source_id
         row['status']='CONTRADICTION_FIXED_FW'
         delta.pop('discharged_sources',None)
         delta['readout_failure']={'source_id':failure.source_id,
           'activation_source_id':sid,'operation':failure.operation,
           'reason':failure.reason,'rule':'R13','result_created_for_failed_step':False}
         errors.append(dict(delta['readout_failure'],classification='CONTRADICTION_FIXED_FW',unit=key))
         # Successful operations before a queued failure are retained and disclosed.
         new_events=[e for e in events if e['id'] not in before_event_ids]
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
     c['dependency_status']='CONDITIONAL_FLOW_PRESENT' if found else 'NO_CAPACITY_LATER_WRITTEN_CONSUMER'
     if not found:
      errors.append({'classification':'NO_CAPACITY_LATER_WRITTEN_CONSUMER','source_id':c['source_ids'][-1],'unit':c['unit']})

    # Whole-pair dependencies are reported separately from raw role accounting.
    pairs=[]
    for side in ['F75V','F104V']:
        for ed in packet['editions']:
            prev=next(u for u in unit_records if u['unit_id']=='FW_'+side+'_PREVIOUS' and u['reader']==ed)
            cur=next(u for u in unit_records if u['unit_id']=='FW_'+side+'_CURRENT' and u['reader']==ed)
            applicable=[c for c in calls if c['unit']==cur['key']]
            contradictions=[e for e in errors if e.get('classification')=='CONTRADICTION_FIXED_FW' and e.get('unit') in [prev['key'],cur['key']]]
            if not prev['raw_groups'] or not cur['raw_groups']:
                status='NO_CAPACITY_SOURCE_UNIT'
            elif contradictions:
                status='CONTRADICTION_FIXED_FW'
            elif prev['first_barrier'] or cur['first_barrier']:
                status='NO_CAPACITY_FIRST_BARRIER'
            elif (side,ed) not in plans:
                status='NO_CAPACITY_EARLIER_PLAN_SLOT_OR_STEPS'
            elif not applicable:
                status='NO_CAPACITY_NOT_APPLICABLE_EXACT_CALL'
            elif any(not c['later_written_consumers'] for c in applicable):
                status='NO_CAPACITY_LATER_WRITTEN_CONSUMER'
            else:
                status='CONDITIONAL_WRITTEN_FLOW_PRESENT_UNDER_FROZEN_MODEL'
            pairs.append({'side':side,'reader':ed,'previous_unit':prev['key'],'current_unit':cur['key'],
                'classification':status,'previous_first_barrier':prev['first_barrier'],'current_first_barrier':cur['first_barrier'],
                'call_ids':[c['id'] for c in applicable],'contradictions':contradictions,'semantic_validation':False,
                'native_paragraph_capacity':ed!='RF1b','independent_confirmation_capacity':0})
    account={'schema':'GDT1125-FW-literal-transfer-v1','status':'LITERAL_APPLICATION_NOT_SEMANTIC_PASS',
        'spec_sha256':sha_bytes(spec_bytes),'source_packet_sha256':source_sha,
        'model_path':MODEL_REL,'model_sha256':MODEL_SHA256,
        'frozen_core_source_sha256':AUTHOR_BUILD_SHA256,'copied_core_sha256':COPIED_CORE_SHA256,
        'adapter_sha256':sha_bytes(Path(__file__).read_bytes()),
        'dictionary':lexicon,'controls':controls,'rules':rules,'nominal_whitelist':names,
        'plan_records':list(plans.values()),'unit_records':unit_records,'calls':calls,
        'pair_results':pairs,'errors':errors,'raw_group_count':len(rows),
        'first_barriers':[{'unit':u['key'],'source_id':u['first_barrier']} for u in unit_records],
        'application_predictions':model['application_predictions'],
        'named_material_translations':0,'independent_confirmation_capacity':0,
        'semantic_validation':False,'adapter_notes':__doc__}
    artifacts=EXPERIMENT/'artifacts'
    (artifacts/'FW_TRANSFER.json').write_text(json.dumps(account,ensure_ascii=False,indent=2)+'\n')
    cols=SOURCE_COLUMNS+['unit_id','mode','lexical_entry','formal_gdt012_062','formal_gdt605_chunk_id','native_paragraph_flags_available',
        'rule_ids','contribution','arguments','preconditions','state_before','delta','state_after','plan_id','call_id',
        'event_ids','result_ids','pending_opening_discharge','status','closure']
    source_order={g['source_group_id']:i for i,g in enumerate(packet['groups'])}
    rows.sort(key=lambda r:source_order[r['source_group_id']])
    assert len(rows)==len(packet['groups'])
    assert all(all(row[k]==group[k] for k in SOURCE_COLUMNS) for row,group in zip(rows,packet['groups']))
    with (artifacts/'FW_TRANSFER.tsv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=cols,delimiter='\t');writer.writeheader();writer.writerows(rows)
    print(json.dumps({'status':account['status'],'groups':len(rows),'pairs':pairs,'semantic_validation':False},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
