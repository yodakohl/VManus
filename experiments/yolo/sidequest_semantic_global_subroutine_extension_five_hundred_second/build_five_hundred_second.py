#!/usr/bin/env python3
from __future__ import annotations
import csv,json,collections
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P481=R/'experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first'
P500=R/'experiments/yolo/sidequest_semantic_procedure_primitive_grammar_five_hundredth'
P501=R/'experiments/yolo/sidequest_semantic_shared_subroutines_five_hundred_first'
SUBS={'SUB01':('ACTIVATE_CHARGE','ACTIVATE_CHARGE','TARGET_HANDOFF'),'SUB02':('MOVE_PASS','ACTIVATE_CHARGE','CONTINUE_USE'),'SUB03':('CONTINUE_USE','METER_CHECK')}
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def classify(x,override):
 if x['event_id'] in override:return override[x['event_id']],'PASS500_OVERRIDE'
 if x['closes_step']=='YES':return 'CLOSE','EXPLICIT_CLOSE'
 cp=x['component_parse'];st=x['state_transition'];ap=x['action_phase']
 if cp=='WHOLE[ches]':return 'ACTIVATE_CHARGE','WHOLE_TEILEN'
 if cp=='WHOLE[daiiin]':return 'METER_CHECK','WHOLE_STUFE_II'
 if cp=='WHOLE[cheey|shey]':return 'HOLD_STATE','WHOLE_EMPFANGSBESTAND'
 if st in {'BATCH_ACTIVATED','PORTION_CREATED','ADDITION_ACTIVATED','NEXT_ITEM_ACTIVATED'}:return 'ACTIVATE_CHARGE',st
 if st=='FRACTION_CREATED':return 'SOURCE_DRAW',st
 if st=='FLOW_ACTIVATED':return ('SOURCE_DRAW' if cp.startswith('CH+') else 'MOVE_PASS'),st
 if st in {'COLLECTION_CREATED','RESULT_CREATED'}:return 'HOLD_STATE',st
 if st=='TARGET_ONLY':return 'TARGET_HANDOFF',st
 if ap in {'HOLD','CHECK'}:return 'HOLD_STATE','ACTION_'+ap
 roots=set(cp.replace('WHOLE[','').replace(']','').split('+'))
 if roots&{'AIIN','IIN'}:return 'METER_CHECK','MEASURE_ROOT'
 if ap=='MEASURE':return 'ACTIVATE_CHARGE','MEASURE_PHASE_WITHOUT_MEASURE_ROOT'
 if 'AL' in roots:return 'TARGET_HANDOFF','AL_TARGET'
 if 'AR' in roots:return 'SOURCE_DRAW','AR_SOURCE'
 if 'CH' in roots or cp=='CFHY':return 'SOURCE_DRAW','DRAW_ROOT_OR_WHOLE'
 if roots&{'CTH','SHED','SH','CHK','SOLK'}:return 'HOLD_STATE','STATE_ROOT'
 if roots&{'OK','OR','AIN','HO','K'}:return 'ACTIVATE_CHARGE','ACTIVATION_ROOT'
 if roots&{'CHD','CKH','L','P','AIR'}:return 'MOVE_PASS','MOVEMENT_ROOT'
 return 'CONTINUE_USE','REFERENCE_OR_CONTINUATION'
def main():
 events=read(P481/'FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv');old=read(P500/'FIVE_HUNDREDTH_58_EVENT_PRIMITIVE_MAP.tsv');override={x['event_id']:x['procedure_primitive'] for x in old}
 mapped=[]
 for x in events:
  p,reason=classify(x,override);mapped.append({'event_id':x['event_id'],'statement_id':x['statement_id'],'record':x['record_unit_id'],'page':x['page'],'locus':x['locus'],'surface':x['surface'],'component_parse':x['component_parse'],'state_transition':x['state_transition'],'action_phase':x['action_phase'],'closes_step':x['closes_step'],'procedure_primitive':p,'classification_reason':reason,'reading_de':x['pass481_event_de']})
 write('FIVE_HUNDRED_SECOND_381_EVENT_PRIMITIVE_MAP.tsv',mapped)
 oldocc=read(P501/'FIVE_HUNDRED_FIRST_SEVEN_SUBROUTINE_OCCURRENCES.tsv');oldkeys={(x['subroutine'],x['start_event'],x['end_event']) for x in oldocc}
 occ=[];assigned={}
 for sid,seq in SUBS.items():
  for st in dict.fromkeys(x['statement_id'] for x in mapped):
   rr=[x for x in mapped if x['statement_id']==st];v=[x['procedure_primitive'] for x in rr]
   for i in range(len(v)-len(seq)+1):
    if tuple(v[i:i+len(seq)])==seq:
     part=rr[i:i+len(seq)];key=(sid,part[0]['event_id'],part[-1]['event_id'])
     occ.append({'subroutine':sid,'statement_id':st,'record':part[0]['record'],'page':part[0]['page'],'start_event':part[0]['event_id'],'end_event':part[-1]['event_id'],'event_ids':'|'.join(x['event_id'] for x in part),'surfaces':'|'.join(x['surface'] for x in part),'primitive_sequence':'>'.join(seq),'status':'PASS501_ORIGINAL' if key in oldkeys else 'NEW_OUTSIDE_FIVE_MACROS'})
     for x in part:
      if x['event_id'] in assigned:raise ValueError('overlapping subroutines')
      assigned[x['event_id']]=sid
 write('FIVE_HUNDRED_SECOND_14_GLOBAL_SUBROUTINE_OCCURRENCES.tsv',occ)
 summary=[]
 for sid in SUBS:
  z=[x for x in occ if x['subroutine']==sid];new=sum(x['status'].startswith('NEW') for x in z);regs={('HERBAL' if x['record'].startswith('H') else 'BIOLOGICAL') for x in z}
  status='GENERAL_WORKSHOP_ROUTINE' if new and len(regs)==2 else 'GENERAL_WITHIN_HERBAL' if new else 'FIVE_MACRO_PAIR_ONLY'
  summary.append({'subroutine':sid,'calls':len(z),'statements':len({x['statement_id'] for x in z}),'new_outside_five_macros':new,'records':len({x['record'] for x in z}),'registers':'|'.join(sorted(regs)),'classification':status})
 write('FIVE_HUNDRED_SECOND_THREE_SUBROUTINE_STATUS.tsv',summary)
 manual=read(P501/'FIVE_HUNDRED_FIRST_120_ITEM_SUBROUTINE_MANUAL.tsv');m2=[]
 ss={x['subroutine']:x for x in summary}
 for x in manual:
  n=dict(x)
  if x['item_id']=='PROC_G01':n['support_or_instances']='381 prose events';n['source_artifact']='PASS502_GLOBAL_PRIMITIVE_MAP'
  if x['item_id'] in ss:
   z=ss[x['item_id']];n['support_or_instances']=str(z['calls'])+' calls;'+str(z['statements'])+' statements;'+z['classification'];n['source_artifact']='PASS502_GLOBAL_SUBROUTINE_EXTENSION'
  m2.append(n)
 write('FIVE_HUNDRED_SECOND_120_ITEM_GLOBAL_SUBROUTINE_MANUAL.tsv',m2)
 ledger=read(P501/'FIVE_HUNDRED_FIRST_776_SUBROUTINE_LEDGER.tsv');mp={x['event_id']:x for x in mapped};out=[]
 for x in ledger:
  n=dict(x)
  if x['domain']=='PROSE':n['procedure_primitive']=mp[x['item_id']]['procedure_primitive'];n['procedure_subroutine']=assigned.get(x['item_id'],'NONE')
  out.append(n)
 write('FIVE_HUNDRED_SECOND_776_GLOBAL_SUBROUTINE_LEDGER.tsv',out)
 counts=collections.Counter(x['procedure_primitive'] for x in mapped);write('FIVE_HUNDRED_SECOND_EIGHT_PRIMITIVE_COUNTS.tsv',[{'primitive':k,'events':counts[k],'fraction':f'{counts[k]/381:.4f}'} for k in sorted(counts)])
 s={'status':'PASS','prose_events':len(mapped),'primitive_types':len(counts),'subroutine_calls_before':len(oldocc),'subroutine_calls_after':len(occ),'new_calls':sum(x['status'].startswith('NEW') for x in occ),'covered_events':len(assigned),'sub01_calls':next(int(x['calls']) for x in summary if x['subroutine']=='SUB01'),'sub02_calls':next(int(x['calls']) for x in summary if x['subroutine']=='SUB02'),'sub03_calls':next(int(x['calls']) for x in summary if x['subroutine']=='SUB03'),'manual':len(m2),'ledger':len(out)}
 (H/'FIVE_HUNDRED_SECOND_BUILD_SUMMARY.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
