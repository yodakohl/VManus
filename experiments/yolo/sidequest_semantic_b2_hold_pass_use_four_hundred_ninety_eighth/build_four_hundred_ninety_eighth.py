#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P481=R/'experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first';P497=R/'experiments/yolo/sidequest_semantic_b4_receive_exit_four_hundred_ninety_seventh'
TARGET='B2-S006';MACRO='FOLGEPOSTEN AM BECKEN ANSETZEN IM DURCHLASS HALTEN UND VERWENDEN'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def main():
 e=read(P481/'FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv');t=[x for x in e if x['statement_id']==TARGET]
 m=read(P497/'FOUR_HUNDRED_NINETY_SEVENTH_165_ITEM_B4_DECOMPOSED_MANUAL.tsv');l=read(P497/'FOUR_HUNDRED_NINETY_SEVENTH_776_B4_DECOMPOSED_LEDGER.tsv')
 a={'E185':('P1_FOLGEPOSTEN_HALTEN','OT+EE+Y','Den nächsten Posten länger halten.'),'E186':('P1_FOLGEPOSTEN_HALTEN','OK+AL','Diesen Posten am oberen Becken ansetzen.'),'E187':('P2_DURCHLASS','SH+E+CKH+Y','Die geerbte Teilportion kurz im Durchlass halten.'),'E188':('P3_VERWENDEN','OK+Y','Diese Teilportion im laufenden Arbeitsgang verwenden.')}
 tr=[]
 for x in t:
  p,i,v=a[x['event_id']];tr.append({'order':len(tr)+1,'event_id':x['event_id'],'locus':x['locus'],'field_id':x['field_id'],'surface':x['surface'],'component_parse':x['component_parse'],'manual_item':i,'phase':p,'owner':x['owner_code'],'old_de':x['pass481_event_de'],'reading_de':v,'closes_step':x['closes_step']})
 write('FOUR_HUNDRED_NINETY_EIGHTH_FOUR_EVENT_HOLD_PASS_USE_TRACE.tsv',tr)
 obj=[{'state':'N1','object_de':'recordlokal geerbte Becken-Teilportion','at':'RECORD_STATE'},{'state':'N2','object_de':'länger gehaltener Folgeposten','at':'E185'},{'state':'N3','object_de':'am oberen Becken angesetzter Posten','at':'E186'},{'state':'N4','object_de':'kurz im Durchlass gehaltener Verwendungsposten','at':'E187|E188'}]
 write('FOUR_HUNDRED_NINETY_EIGHTH_FOUR_OBJECT_STATES.tsv',obj)
 cand=[{'candidate':'A','reading_de':MACRO,'component_fit':4,'station_fit':4,'invented_content_cost':0,'total':8,'decision':'SELECT'},{'candidate':'B','reading_de':'TEILBAD LAENGER HALTEN UND ANWENDEN','component_fit':3,'station_fit':3,'invented_content_cost':2,'total':4,'decision':'MEDICAL_RIVAL'},{'candidate':'C','reading_de':'OBERES BECKEN MIT WASSER FUELLEN','component_fit':1,'station_fit':3,'invented_content_cost':3,'total':1,'decision':'REJECT'}]
 write('FOUR_HUNDRED_NINETY_EIGHTH_THREE_B2_READINGS.tsv',cand)
 new=[];rm=0
 for x in m:
  if x['item_id']=='W:B2-S006':rm+=1;continue
  new.append(dict(x))
 for i,x in enumerate(new,1):x['manual_order']=str(i)
 write('FOUR_HUNDRED_NINETY_EIGHTH_164_ITEM_B2_DECOMPOSED_MANUAL.tsv',new)
 tm={x['event_id']:x for x in tr};out=[]
 for x in l:
  n=dict(x)
  if x['item_id'] in tm:
   z=tm[x['item_id']];n['semantic_layer']='COMPOSED_EXISTING_COMPONENT_CHAIN';n['syntax_item']=z['manual_item'];n['concrete_reading_de']=z['reading_de'];n['local_macro']=MACRO;n['macro_phase']=z['phase']
  out.append(n)
 write('FOUR_HUNDRED_NINETY_EIGHTH_776_B2_DECOMPOSED_LEDGER.tsv',out)
 (H/'FOUR_HUNDRED_NINETY_EIGHTH_COMPLETE_B2_S006_READING.md').write_text('# '+MACRO+'\n\nHalte den nächsten Posten länger und setze ihn am oberen Becken an. Halte die aus dem Record übernommene Teilportion kurz im Durchlass und verwende sie im laufenden Arbeitsgang.\n\nDie Karten nennen Becken, Durchlass, Haltung und Verwendung, aber keinen Körperteil und keine Krankheit.\n',encoding='utf-8')
 s={'status':'PASS','events':4,'phases':3,'objects':4,'removed':rm,'manual_before':len(m),'manual_after':len(new),'ledger':len(out),'macro_events_total':sum(x['local_macro']!='NONE' for x in out)};(H/'FOUR_HUNDRED_NINETY_EIGHTH_BUILD_SUMMARY.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
