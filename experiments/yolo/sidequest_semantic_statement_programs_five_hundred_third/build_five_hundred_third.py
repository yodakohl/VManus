#!/usr/bin/env python3
from __future__ import annotations
import csv,json,collections
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P502=R/'experiments/yolo/sidequest_semantic_global_subroutine_extension_five_hundred_second'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def close_operation(x):
 cp=x['component_parse'];st=x['state_transition'];ap=x['action_phase'];roots=set(cp.replace('WHOLE[','').replace(']','').split('+'))
 if st in {'BATCH_ACTIVATED','PORTION_CREATED','ADDITION_ACTIVATED','NEXT_ITEM_ACTIVATED'}:return 'ACTIVATE_CHARGE'
 if st=='FRACTION_CREATED':return 'SOURCE_DRAW'
 if st=='FLOW_ACTIVATED':return 'SOURCE_DRAW' if cp.startswith('CH+') else 'MOVE_PASS'
 if st in {'COLLECTION_CREATED','RESULT_CREATED'} or ap in {'HOLD','CHECK'}:return 'HOLD_STATE'
 if roots&{'AIIN','IIN'}:return 'METER_CHECK'
 if ap=='MEASURE':return 'ACTIVATE_CHARGE'
 if 'AL' in roots:return 'TARGET_HANDOFF'
 if 'AR' in roots:return 'SOURCE_DRAW'
 if 'CH' in roots:return 'SOURCE_DRAW'
 if roots&{'CTH','SHED','SH','CHK','SOLK'}:return 'HOLD_STATE'
 if roots&{'OK','OR','AIN','HO','K'}:return 'ACTIVATE_CHARGE'
 if roots&{'CHD','CKH','L','P','AIR'}:return 'MOVE_PASS'
 return 'CONTINUE_USE'
def main():
 e=read(P502/'FIVE_HUNDRED_SECOND_381_EVENT_PRIMITIVE_MAP.tsv')
 expanded=[]
 for x in e:
  if x['closes_step']=='YES':op=close_operation(x);tokens=op+'>CLOSE'
  else:op=x['procedure_primitive'];tokens=op
  expanded.append({**x,'operation_primitive':op,'emitted_procedure_tokens':tokens,'emitted_token_count':len(tokens.split('>'))})
 write('FIVE_HUNDRED_THIRD_381_EVENT_EXPANDED_TOKENS.tsv',expanded)
 statement_rows=[];sig_to_statements=collections.defaultdict(list)
 for st in dict.fromkeys(x['statement_id'] for x in expanded):
  rr=[x for x in expanded if x['statement_id']==st];sig='>'.join(t for x in rr for t in x['emitted_procedure_tokens'].split('>'));sig_to_statements[sig].append(st)
  statement_rows.append({'statement_id':st,'record':rr[0]['record'],'page':rr[0]['page'],'events':len(rr),'emitted_tokens':sum(int(x['emitted_token_count']) for x in rr),'closed':'YES' if rr[-1]['closes_step']=='YES' else 'NO','primitive_signature':sig,'event_ids':'|'.join(x['event_id'] for x in rr),'surfaces':'|'.join(x['surface'] for x in rr)})
 ordered=sorted(sig_to_statements,key=lambda s:(-len(sig_to_statements[s]),s));pid={s:f'PG{i:03d}' for i,s in enumerate(ordered,1)}
 for x in statement_rows:x['program_id']=pid[x['primitive_signature']];x['program_support']=len(sig_to_statements[x['primitive_signature']]);x['program_status']='RECURRENT' if x['program_support']>1 else 'UNIQUE'
 write('FIVE_HUNDRED_THIRD_116_STATEMENT_PROGRAMS.tsv',statement_rows)
 programs=[]
 for sig in ordered:
  sts=sig_to_statements[sig]
  programs.append({'program_id':pid[sig],'support':len(sts),'registers':'|'.join(sorted({('HERBAL' if s.startswith('H') else 'BIOLOGICAL') for s in sts})),'records':len({s.split('-')[0] for s in sts}),'primitive_signature':sig,'statements':'|'.join(sts),'status':'RECURRENT_PROGRAM' if len(sts)>1 else 'UNIQUE_PROGRAM'})
 write('FIVE_HUNDRED_THIRD_72_PROGRAM_INVENTORY.tsv',programs)
 recurrent=[x for x in programs if x['status']=='RECURRENT_PROGRAM']
 write('FIVE_HUNDRED_THIRD_NINE_RECURRENT_PROGRAMS.tsv',recurrent)
 terminal=collections.Counter(x['operation_primitive'] for x in expanded if x['closes_step']=='YES')
 write('FIVE_HUNDRED_THIRD_TERMINAL_OPERATION_COUNTS.tsv',[{'operation_before_close':k,'events':v,'emitted_form':k+'>CLOSE'} for k,v in sorted(terminal.items())])
 manual=read(P502/'FIVE_HUNDRED_SECOND_120_ITEM_GLOBAL_SUBROUTINE_MANUAL.tsv');m2=[]
 for x in manual:
  n=dict(x)
  if x['item_id']=='PROC_G01':n['teaching_value_or_rule_de']='Acht Prozessprimitive kombinieren; eine Endkarte führt zuerst ihre örtliche Handlung aus und emittiert danach CLOSE; konkrete Karten folgen ihrer Komponentenfolge.';n['support_or_instances']='381 cards;470 emitted tokens;116 statements';n['source_artifact']='PASS503_ACTION_PLUS_CLOSE'
  m2.append(n)
 write('FIVE_HUNDRED_THIRD_120_ITEM_STATEMENT_PROGRAM_MANUAL.tsv',m2)
 ledger=read(P502/'FIVE_HUNDRED_SECOND_776_GLOBAL_SUBROUTINE_LEDGER.tsv');emap={x['event_id']:x for x in expanded};sp={x['statement_id']:x for x in statement_rows};out=[]
 for x in ledger:
  n=dict(x)
  if x['domain']=='PROSE':z=emap[x['item_id']];n['operation_primitive']=z['operation_primitive'];n['emitted_procedure_tokens']=z['emitted_procedure_tokens'];n['statement_program']=sp[x['statement_or_locus']]['program_id']
  else:n['operation_primitive']='NONE';n['emitted_procedure_tokens']='NONE';n['statement_program']='NONE'
  out.append(n)
 write('FIVE_HUNDRED_THIRD_776_STATEMENT_PROGRAM_LEDGER.tsv',out)
 s={'status':'PASS','events':len(expanded),'emitted_tokens':sum(int(x['emitted_token_count']) for x in expanded),'statements':len(statement_rows),'programs':len(programs),'recurrent_programs':len(recurrent),'recurrent_statements':sum(int(x['support']) for x in recurrent),'unique_programs':sum(x['status']=='UNIQUE_PROGRAM' for x in programs),'unique_herbal_statements':sum(x['program_status']=='UNIQUE' and x['record'].startswith('H') for x in statement_rows),'herbal_statements':sum(x['record'].startswith('H') for x in statement_rows),'unique_bio_statements':sum(x['program_status']=='UNIQUE' and x['record'].startswith('B') for x in statement_rows),'bio_statements':sum(x['record'].startswith('B') for x in statement_rows),'close_events':sum(x['closes_step']=='YES' for x in expanded),'manual':len(m2),'ledger':len(out)}
 (H/'FIVE_HUNDRED_THIRD_BUILD_SUMMARY.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
