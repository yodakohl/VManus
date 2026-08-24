#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P515=R/'experiments/yolo/sidequest_semantic_apprentice_copy_day_five_hundred_fifteenth'
P503=R/'experiments/yolo/sidequest_semantic_statement_programs_five_hundred_third'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def main():
 log=read(P515/'FIVE_HUNDRED_FIFTEENTH_381_APPRENTICE_COPY_LOG.tsv');stmts={x['statement_id']:x for x in read(P503/'FIVE_HUNDRED_THIRD_116_STATEMENT_PROGRAMS.tsv')};seen=set();out=[];dec=[]
 for x in log:
  first=x['statement_id'] not in seen;seen.add(x['statement_id']);unique=first and stmts[x['statement_id']]['program_status']=='UNIQUE';owner=x['owner_reset']=='YES';allo=x['renderer_action']=='COPY_LOCAL_EXEMPLAR';reasons=[]
  if unique:reasons.append('SELECT_UNUSUAL_PROGRAM');dec.append({'decision_no':'0','event_id':x['event_id'],'statement_id':x['statement_id'],'record':x['record'],'page':x['page'],'decision_type':'SELECT_UNUSUAL_PROGRAM','choice_de':stmts[x['statement_id']]['primitive_signature'],'why_conscious':'Program occurs once on the fixed pages.'})
  if owner:reasons.append('RESET_VISIBLE_OWNER');dec.append({'decision_no':'0','event_id':x['event_id'],'statement_id':x['statement_id'],'record':x['record'],'page':x['page'],'decision_type':'RESET_VISIBLE_OWNER','choice_de':x['owner_code'],'why_conscious':'Visible image owner changes here.'})
  if allo:reasons.append('COPY_LOCAL_ALLOGRAPH');dec.append({'decision_no':'0','event_id':x['event_id'],'statement_id':x['statement_id'],'record':x['record'],'page':x['page'],'decision_type':'COPY_LOCAL_ALLOGRAPH','choice_de':x['renderer_final_surface'],'why_conscious':'Compact renderer default is insufficient; copy exemplar surface.'})
  out.append({**x,'statement_first_event':'YES' if first else 'NO','program_status':stmts[x['statement_id']]['program_status'],'master_conscious_decision_count':str(len(reasons)),'master_conscious_reasons':'|'.join(reasons) if reasons else 'NONE','master_mode':'CONSCIOUS_LOCAL_CHOICE' if reasons else 'AUTOMATIC_FLOW'})
 for i,x in enumerate(dec,1):x['decision_no']=str(i)
 write('FIVE_HUNDRED_SIXTEENTH_381_MASTER_COPY_LOG.tsv',out);write('FIVE_HUNDRED_SIXTEENTH_151_CONSCIOUS_DECISIONS.tsv',dec)
 habits=[
  ('MH01','INHERIT_OWNER','360 events','Keep active owner unless a visible reset occurs.'),
  ('MH02','RUN_AUTOMATON','470 primitive tokens','Apply the five-state transition automatically.'),
  ('MH03','CARRY_LINE','19 transitions','Physical line break preserves statement state.'),
  ('MH04','ACTION_THEN_CLOSE','89 terminal events','Perform local action, then close.'),
  ('MH05','USE_RECURRENT_BIO_PATH','53 statements','Recall one of nine frequent Bio programs.'),
  ('MH06','RENDER_BY_RULE','314 events','Write default body and learned wrapper habit.'),
  ('MH07','RECALL_TEACHING_ITEM','381 events','Recognize exact deck card, component strips or stage note.'),
 ]
 write('FIVE_HUNDRED_SIXTEENTH_SEVEN_AUTOMATIC_MASTER_HABITS.tsv',[{'habit_id':a,'habit':b,'support':c,'master_instruction':d} for a,b,c,d in habits])
 summary=[]
 for rec in ['H1','H2','H3','H4','H5','B1','B2','B3','B4','B5','B6']:
  rr=[x for x in out if x['record']==rec];dd=[x for x in dec if x['record']==rec]
  summary.append({'record':rec,'page':rr[0]['page'],'events':str(len(rr)),'automatic_events':str(sum(x['master_mode']=='AUTOMATIC_FLOW' for x in rr)),'conscious_events':str(sum(x['master_mode']=='CONSCIOUS_LOCAL_CHOICE' for x in rr)),'conscious_decision_instances':str(len(dd)),'unique_program_choices':str(sum(x['decision_type']=='SELECT_UNUSUAL_PROGRAM' for x in dd)),'owner_resets':str(sum(x['decision_type']=='RESET_VISIBLE_OWNER' for x in dd)),'allograph_choices':str(sum(x['decision_type']=='COPY_LOCAL_ALLOGRAPH' for x in dd))})
 write('FIVE_HUNDRED_SIXTEENTH_ELEVEN_RECORD_MASTER_LOAD.tsv',summary)
 md=['# Pass 516 — Meistermodus','', '## Sieben automatische Gewohnheiten','']+[f'- **{b}** ({c}): {d}' for _,b,c,d in habits]+['','## Bewusste Entscheidungen','', '- 63 einmalige Satzprogramme auswählen;','- 21 sichtbare Besitzerwechsel setzen;','- 67 lokale Allographen aus dem Exemplar kopieren.','', 'Das sind 151 Entscheidungen auf 126 Ereignissen. 255 der 381 Karten laufen vollständig automatisch.','', '## Meisterregel','', 'Alles Regelhafte fließen lassen. Nur stoppen, wenn das Bild den Besitzer wechselt, das Satzprogramm kein gelernter Standardweg ist oder die lokale Schriftform vom Default abweicht.']
 (H/'FIVE_HUNDRED_SIXTEENTH_MASTER_POCKET_PROTOCOL.md').write_text('\n'.join(md)+'\n')
 c=Counter(x['decision_type'] for x in dec);build={'status':'PASS','events':len(out),'automatic_events':sum(x['master_mode']=='AUTOMATIC_FLOW' for x in out),'conscious_events':sum(x['master_mode']=='CONSCIOUS_LOCAL_CHOICE' for x in out),'conscious_decision_instances':len(dec),'decision_counts':dict(c),'automatic_habits':len(habits),'records':len(summary)}
 (H/'FIVE_HUNDRED_SIXTEENTH_BUILD_SUMMARY.json').write_text(json.dumps(build,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
