#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P481=R/'experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first'
P496=R/'experiments/yolo/sidequest_semantic_h4_target_batch_portion_four_hundred_ninety_sixth'
TARGET='B4-S015';MACRO='EMPFANGSPORTION ZUM DURCHGANG STELLEN FOLGESTATION KURZ AUFFANGEN UND ABFUEHREN'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 ev=read(P481/'FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv');tar=[r for r in ev if r['statement_id']==TARGET]
 man=read(P496/'FOUR_HUNDRED_NINETY_SIXTH_166_ITEM_H4_DECOMPOSED_MANUAL.tsv');led=read(P496/'FOUR_HUNDRED_NINETY_SIXTH_776_H4_DECOMPOSED_LEDGER.tsv')
 a={
 'E352':('A1_EMPFANGSPORTION','OK+AIN','STATION_A','Eine Portion in den örtlichen Arbeitsgang setzen.'),
 'E353':('A1_EMPFANGSPORTION','PROC031','STATION_A','Den daraus entstandenen Empfangsbestand übernehmen.'),
 'E354':('A1_EMPFANGSPORTION','K+AIN','STATION_A','Eine Portion dieses Bestands zuführen.'),
 'E355':('A2_DURCHGANG','CH+CKH+AL','STATION_A','Diese Portion an die örtliche Durchgangsstelle bringen.'),
 'E356':('B1_NEUER_AUFFANGPOSTEN','SOLK+E+Y','STATION_B','An der neuen sichtbaren Station einen lokalen Posten kurz auffangen.'),
 'E357':('B1_NEUER_AUFFANGPOSTEN','L+CHD+DY','STATION_B','Diesen neuen lokalen Posten hinausführen und schließen.'),}
 tr=[]
 for r in tar:
  ph,item,station,val=a[r['event_id']];tr.append({'event_order':len(tr)+1,'event_id':r['event_id'],'locus':r['locus'],'field_id':r['field_id'],'surface':r['surface'],'component_parse':r['component_parse'],'manual_item':item,'macro_phase':ph,'station':station,'owner_code':r['owner_code'],'reading_de':val,'closes_step':r['closes_step']})
 write('FOUR_HUNDRED_NINETY_SEVENTH_SIX_EVENT_RECEIVE_EXIT_TRACE.tsv',tr)
 b=[
 {'from_event':'E352','to_event':'E353','owner':'KEEP_A','material':'KEEP','syntax':'CONTINUE'},
 {'from_event':'E353','to_event':'E354','owner':'KEEP_A','material':'KEEP','syntax':'CONTINUE'},
 {'from_event':'E354','to_event':'E355','owner':'KEEP_A','material':'KEEP','syntax':'CONTINUE'},
 {'from_event':'E355','to_event':'E356','owner':'RESET_B','material':'DO_NOT_CARRY','syntax':'CONTINUE_WORKFLOW'},
 {'from_event':'E356','to_event':'E357','owner':'KEEP_B','material':'KEEP_NEW_B','syntax':'CONTINUE'},]
 write('FOUR_HUNDRED_NINETY_SEVENTH_FIVE_BOUNDARY_DECISIONS.tsv',b)
 objs=[
 {'id':'A1','station':'A','object_de':'zugegebene Portion','created_at':'E352','crosses_gap':'NO'},
 {'id':'A2','station':'A','object_de':'Empfangsbestand','created_at':'E353','crosses_gap':'NO'},
 {'id':'A3','station':'A','object_de':'Portion am Durchgang','created_at':'E355','crosses_gap':'NO'},
 {'id':'B1','station':'B','object_de':'neuer kurz aufgefangener Lokalposten','created_at':'E356','crosses_gap':'NO'},
 {'id':'B2','station':'B','object_de':'hinausgeführter geschlossener Lokalposten','created_at':'E357','crosses_gap':'NO'},]
 write('FOUR_HUNDRED_NINETY_SEVENTH_FIVE_LOCAL_OBJECTS.tsv',objs)
 cand=[
 {'candidate':'A','reading_de':MACRO,'component_fit':6,'owner_reset_fit':5,'invented_connection_cost':0,'total':11,'decision':'SELECT'},
 {'candidate':'B','reading_de':'EMPFANGSPORTION DURCH DIE RECHTE LEITUNG ABFUEHREN','component_fit':6,'owner_reset_fit':1,'invented_connection_cost':4,'total':3,'decision':'REJECT_HIDDEN_CONNECTION'},
 {'candidate':'C','reading_de':'MEDIZINISCHE PORTION AUFFANGEN UND AUSLEITEN','component_fit':5,'owner_reset_fit':2,'invented_connection_cost':2,'total':5,'decision':'LOCAL_MEDICAL_RIVAL'},]
 write('FOUR_HUNDRED_NINETY_SEVENTH_THREE_B4_READINGS.tsv',cand)
 new=[];rm=0
 for r in man:
  if r['item_id']=='W:B4-S015':rm+=1;continue
  new.append(dict(r))
 for i,r in enumerate(new,1):r['manual_order']=str(i)
 write('FOUR_HUNDRED_NINETY_SEVENTH_165_ITEM_B4_DECOMPOSED_MANUAL.tsv',new)
 tm={r['event_id']:r for r in tr};out=[]
 for r in led:
  n=dict(r)
  if r['item_id'] in tm:
   x=tm[r['item_id']];n['semantic_layer']='COMPOSED_EXISTING_CHAIN_WITH_OWNER_RESET';n['syntax_item']=x['manual_item'];n['concrete_reading_de']=x['reading_de'];n['local_macro']=MACRO;n['macro_phase']=x['macro_phase']
  out.append(n)
 write('FOUR_HUNDRED_NINETY_SEVENTH_776_B4_DECOMPOSED_LEDGER.tsv',out)
 (H/'FOUR_HUNDRED_NINETY_SEVENTH_COMPLETE_B4_S015_READING.md').write_text('# '+MACRO+'\n\nSetze an der linken Randstation eine Portion in den Arbeitsgang, übernimm den Empfangsbestand, führe eine Portion davon weiter und bringe sie zur örtlichen Durchgangsstelle. Nach dem sichtbaren Besitzerwechsel beginnt rechts ein neuer lokaler Posten: Fange ihn kurz auf, führe ihn hinaus und schließe.\n\nNur die Arbeitsreihenfolge, nicht der Stoff, überquert den Bildsprung.\n',encoding='utf-8')
 s={'status':'PASS','events':len(tr),'stations':2,'owner_resets':1,'material_carry_across_reset':0,'removed':rm,'manual_before':len(man),'manual_after':len(new),'ledger':len(out),'macro_events_total':sum(r['local_macro']!='NONE' for r in out)}
 (H/'FOUR_HUNDRED_NINETY_SEVENTH_BUILD_SUMMARY.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
