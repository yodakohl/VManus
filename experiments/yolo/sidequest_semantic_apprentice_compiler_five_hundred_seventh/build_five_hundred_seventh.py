#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
P471=ROOT/'experiments/yolo/sidequest_semantic_compact_renderer_habits_four_hundred_seventy_first'
P474=ROOT/'experiments/yolo/sidequest_semantic_referent_propagation_four_hundred_seventy_fourth'
P503=ROOT/'experiments/yolo/sidequest_semantic_statement_programs_five_hundred_third'
P505=ROOT/'experiments/yolo/sidequest_semantic_statement_automaton_five_hundred_fifth'
P506=ROOT/'experiments/yolo/sidequest_semantic_register_habits_five_hundred_sixth'
P470=ROOT/'experiments/yolo/sidequest_semantic_two_stage_renderer_four_hundred_seventieth'

def read(path):
 with Path(path).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(name,rows):
 with (HERE/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def step(state,token):
 if state=='CLOSED':raise ValueError('token after close')
 if token=='CLOSE':
  if state in {'START','AFTER_METER'}:raise ValueError('illegal close')
  return 'CLOSED'
 if state=='AFTER_SOURCE' and token in {'MOVE_PASS','TARGET_HANDOFF'}:raise ValueError('illegal source exit')
 if token=='SOURCE_DRAW':return 'AFTER_SOURCE'
 if token=='METER_CHECK':return 'AFTER_METER'
 return 'WORK'
def main():
 owner=read(P474/'FOUR_HUNDRED_SEVENTY_FOURTH_381_REFERENT_TRACE.tsv');od={x['event_id']:x for x in owner}
 emit=read(P503/'FIVE_HUNDRED_THIRD_381_EVENT_EXPANDED_TOKENS.tsv');ed={x['event_id']:x for x in emit}
 renderer=[x for x in read(P471/'FOUR_HUNDRED_SEVENTY_FIRST_776_COMPACT_RENDERER_PREDICTIONS.tsv') if x['domain']=='PROSE'];rd={x['item_id']:x for x in renderer}
 bodies=read(P470/'FOUR_HUNDRED_SEVENTIETH_381_PROSE_TWO_STAGE_WRITER.tsv');bd={x['event_id']:x for x in bodies}
 habits=read(P506/'FIVE_HUNDRED_SIXTH_116_REGISTER_WORKFLOW_ASSIGNMENTS.tsv');hd={x['statement_id']:x for x in habits}
 stmts=read(P503/'FIVE_HUNDRED_THIRD_116_STATEMENT_PROGRAMS.tsv');sd={x['statement_id']:x for x in stmts}
 by_statement=defaultdict(list)
 for x in emit:by_statement[x['statement_id']].append(x)
 traces=[]
 for st in stmts:
  state='START'
  for index,event in enumerate(by_statement[st['statement_id']],1):
   o=od[event['event_id']];r=rd[event['event_id']];b=bd[event['event_id']];before=state
   for token in event['emitted_procedure_tokens'].split('>'):state=step(state,token)
   traces.append({
    'event_id':event['event_id'],'statement_id':event['statement_id'],'event_in_statement':str(index),'record':event['record'],'page':event['page'],'locus':event['locus'],
    'owner_code':o['owner_code'],'concrete_owner_de':o['concrete_owner_de'],'owner_reset':o['owner_reset'],'active_before_de':o['active_before_de'],'active_after_de':o['active_after_de'],
    'register_habit':hd[event['statement_id']]['register_habit'],'joint_tuple_id':o['joint_tuple_id'],'component_parse':event['component_parse'],'body_surface':b['body_surface'],
    'observed_surface':event['surface'],'renderer_mode':'RULE' if r['exact_without_exemplar']=='YES' else 'COPY_LOCAL_ALLOGRAPH','habit_applied':r['habit_applied'],
    'procedure_tokens':event['emitted_procedure_tokens'],'automaton_before':before,'automaton_after':state,
    'forward_scribe_instruction_de':f"Bei {o['owner_code']} {event['emitted_procedure_tokens']} als Karte {o['joint_tuple_id']} setzen und {event['surface']} schreiben.",
    'backward_reader_instruction_de':f"{event['surface']} an dieser Stelle als Karte {o['joint_tuple_id']} lesen; {event['emitted_procedure_tokens']} ausführen; Besitzer {o['owner_code']} beibehalten.",
    'roundtrip_card': 'YES' if o['joint_tuple_id']==b['joint_tuple_id'] else 'NO',
   })
 write('FIVE_HUNDRED_SEVENTH_381_FORWARD_BACKWARD_CARD_TRACES.tsv',traces)
 by_trace=defaultdict(list)
 for x in traces:by_trace[x['statement_id']].append(x)
 statement_rows=[]
 for st in stmts:
  rr=by_trace[st['statement_id']];habit=hd[st['statement_id']]
  statement_rows.append({
   'statement_id':st['statement_id'],'record':st['record'],'page':st['page'],'owner_start':rr[0]['owner_code'],'owner_resets':str(sum(x['owner_reset']=='YES' for x in rr)),
   'register_habit':habit['register_habit'],'cards':str(len(rr)),'emitted_tokens':st['emitted_tokens'],'card_ids':'|'.join(x['joint_tuple_id'] for x in rr),
   'surfaces':' '.join(x['observed_surface'] for x in rr),'primitive_program':st['primitive_signature'],'final_automaton_state':rr[-1]['automaton_after'],
   'rule_rendered_cards':str(sum(x['renderer_mode']=='RULE' for x in rr)),'exemplar_allographs':str(sum(x['renderer_mode']!='RULE' for x in rr)),
   'forward_result_de':f"{habit['register_habit']}: {st['primitive_signature']}.",
   'backward_result_de':f"{len(rr)} Karten ergeben {st['primitive_signature']} bei {rr[0]['owner_code']}.",
  })
 write('FIVE_HUNDRED_SEVENTH_116_STATEMENT_COMPILER_TRACES.tsv',statement_rows)
 rules=[
  ('C01','OWNER_SET','Wähle den sichtbaren Pflanzen-, Becken-, Gefäß- oder Stationsbesitzer; ohne neuen Besitzer erbe den aktiven.'),
  ('C02','REGISTER_SELECT','Herbal schreibt lange offene Artikelzüge; Biological kurze meist geschlossene Zellen.'),
  ('C03','PROGRAM_SELECT','Wähle einen häufigen Bio-Pfad oder bilde eine neue Folge aus den acht Prozessprimitiven.'),
  ('C04','AUTOMATON_START','Beginne im Zustand START mit genau einem Arbeitsprimitiv.'),
  ('C05','SOURCE_HOLD','Nach SOURCE_DRAW erst ansetzen, prüfen, halten oder fortführen; nicht sofort bewegen oder übergeben.'),
  ('C06','METER_HOLD','Nach METER_CHECK erst handeln oder Zustand setzen; nicht sofort schließen.'),
  ('C07','CARD_SELECT','Wähle für jedes Primitiv die gelernte Ganzkarte oder die passende Komponentenkarte.'),
  ('C08','TERMINAL_EXPAND','Eine terminale Karte führt zuerst ihre örtliche Handlung aus und emittiert danach CLOSE.'),
  ('C09','SURFACE_RENDER','Schreibe den Kartenkörper mit Register-/Positionswrapper; seltene Allographen werden vom Exemplar kopiert.'),
  ('C10','LINE_REFLOW','Ein physisches Zeilenende beendet weder Aussage noch Besitzer; nur markierte Besitzerwechsel setzen den Besitzer zurück.'),
  ('C11','OPEN_OR_CLOSE','Herbal darf im Arbeitszustand offen enden; Biological bevorzugt CLOSED.'),
  ('C12','READ_BACK','Lies Oberfläche und Position zurück zu Karte, Primitivfolge, Automatenzustand und lokalem Besitzer.'),
 ]
 rule_rows=[{'step':str(i),'rule_id':a,'stage':b,'apprentice_instruction_de':c,'scope':'FIXED_TEN_PAGES'} for i,(a,b,c) in enumerate(rules,1)]
 write('FIVE_HUNDRED_SEVENTH_TWELVE_STEP_APPRENTICE_COMPILER.tsv',rule_rows)
 manual=read(P506/'FIVE_HUNDRED_SIXTH_124_ITEM_REGISTER_MANUAL.tsv');pos=next(i for i,x in enumerate(manual) if x['layer']=='L8_RENDERER_HABIT')
 manual.insert(pos,{'manual_order':'0','layer':'L7_APPRENTICE_COMPILER','item_id':'COMPILER_G01','teaching_value_or_rule_de':'Zwölf Schritte: Besitzer wählen; Register wählen; Primitivefolge bilden; Karten setzen; Oberfläche rendern; offen fortführen oder schließen; rücklesen.','scope':'TEN_FIXED_PAGES','support_or_instances':'381 cards;116 statements','source_artifact':'PASS507_APPRENTICE_COMPILER'})
 for i,x in enumerate(manual,1):x['manual_order']=str(i)
 write('FIVE_HUNDRED_SEVENTH_125_ITEM_APPRENTICE_MANUAL.tsv',manual)
 lines=['# Pass 507 — vollständige Lehrlingsspuren','']
 for record in ['H1','H2','H3','H4','H5','B1','B2','B3','B4','B5','B6']:
  lines.extend([f'## {record}',''])
  for x in statement_rows:
   if x['record']==record:lines.append(f"- **{x['statement_id']}** · Besitzer `{x['owner_start']}` · {x['register_habit']} · `{x['surfaces']}` → `{x['primitive_program']}` → {x['final_automaton_state']}.")
  lines.append('')
 (HERE/'FIVE_HUNDRED_SEVENTH_ELEVEN_RECORD_WALKTHROUGH.md').write_text('\n'.join(lines).rstrip()+'\n')
 summary={'status':'PASS','events':len(traces),'statements':len(statement_rows),'records':len({x['record'] for x in statement_rows}),'emitted_tokens':sum(int(x['emitted_tokens']) for x in statement_rows),'owner_resets':sum(x['owner_reset']=='YES' for x in traces),'rule_rendered':sum(x['renderer_mode']=='RULE' for x in traces),'exemplar_allographs':sum(x['renderer_mode']!='RULE' for x in traces),'compiler_steps':len(rule_rows),'manual_items':len(manual)}
 (HERE/'FIVE_HUNDRED_SEVENTH_BUILD_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
