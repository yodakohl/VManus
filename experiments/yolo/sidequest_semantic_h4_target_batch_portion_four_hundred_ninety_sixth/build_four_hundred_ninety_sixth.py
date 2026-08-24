#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
P481=ROOT/'experiments/yolo/sidequest_semantic_direction_triad_four_hundred_eighty_first'
P495=ROOT/'experiments/yolo/sidequest_semantic_b3_two_station_decomposition_four_hundred_ninety_fifth'
TARGET='H4-S004'
MACRO='BEMESSENE PFLANZENPORTION AM ZIEL ANSETZEN UND PORTIONIEREN'

def read(p):
    with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rows):
    with (HERE/n).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
    events=read(P481/'FOUR_HUNDRED_EIGHTY_FIRST_381_DIRECTION_REVISED_PROSE_EVENTS.tsv')
    target=[r for r in events if r['statement_id']==TARGET]
    manual=read(P495/'FOUR_HUNDRED_NINETY_FIFTH_167_ITEM_TWO_STATION_MANUAL.tsv')
    ledger=read(P495/'FOUR_HUNDRED_NINETY_FIFTH_776_TWO_STATION_LEDGER.tsv')
    ana={
      'E068':('P1_BEMESSEN_UND_ZIEL_SETZEN','AIIN','Das Sollmaß für den neuen Posten setzen.'),
      'E069':('P1_BEMESSEN_UND_ZIEL_SETZEN','OK+AL','Den bemessenen Posten an der gelernten Zielstelle ansetzen.'),
      'E070':('P2_PFLANZENMATERIAL_EINTRAGEN','OL+T+Y','Pflanzenmaterial in diesen Zielarbeitsgang weiter eintragen.'),
      'E071':('P2_PFLANZENMATERIAL_EINTRAGEN','OR','Daraus einen Ansatz bilden.'),
      'E072':('P3_ANSATZ_PORTIONIEREN','Y','Diesen Pflanzenansatz als laufenden Posten halten.'),
      'E073':('P3_ANSATZ_PORTIONIEREN','OR+AIN','Eine Portion dieses Ansatzes abteilen.'),
    }
    trace=[]
    for r in target:
      ph,item,val=ana[r['event_id']]
      trace.append({'event_order':len(trace)+1,'event_id':r['event_id'],'locus':r['locus'],'field_id':r['field_id'],'surface':r['surface'],'component_parse':r['component_parse'],'manual_item':item,'macro_phase':ph,'old_event_reading_de':r['pass481_event_de'],'revised_event_reading_de':val,'state_transition':r['state_transition'],'closes_step':r['closes_step']})
    write('FOUR_HUNDRED_NINETY_SIXTH_SIX_EVENT_TARGET_BATCH_TRACE.tsv',trace)
    objects=[
      {'node':'N1','object_de':'recordlokal geerbtes Pflanzenmaterial','created_at':'RECORD_STATE','role':'SOURCE_MATERIAL'},
      {'node':'N2','object_de':'bemessener Zielposten','created_at':'E069','role':'TARGET_WORK_ITEM'},
      {'node':'N3','object_de':'mit Pflanzenmaterial beschickter Ansatz','created_at':'E071','role':'PREPARATION_BATCH'},
      {'node':'N4','object_de':'abgeteilte Ansatzportion','created_at':'E073','role':'PORTION_OUTPUT'},
    ]
    write('FOUR_HUNDRED_NINETY_SIXTH_FOUR_OBJECT_STATES.tsv',objects)
    coverage=[{'event_id':r['event_id'],'surface':r['surface'],'manual_item':r['manual_item'],'existing_item':'YES','new_local_value':'NO','reading_de':r['revised_event_reading_de']} for r in trace]
    write('FOUR_HUNDRED_NINETY_SIXTH_COMPLETE_COMPONENT_COVERAGE.tsv',coverage)
    candidates=[
      {'candidate':'A','reading_de':MACRO,'component_fit':6,'object_fit':5,'invented_content_cost':0,'total':11,'decision':'SELECT'},
      {'candidate':'B','reading_de':'PFLANZENAUSZUG ERWAERMEN UND AUFLEGEN','component_fit':2,'object_fit':3,'invented_content_cost':4,'total':1,'decision':'REJECT'},
      {'candidate':'C','reading_de':'PFLANZENPORTION FUER SPAETERE VERWENDUNG VORBEREITEN','component_fit':5,'object_fit':4,'invented_content_cost':2,'total':7,'decision':'RIVAL'},
    ]
    write('FOUR_HUNDRED_NINETY_SIXTH_THREE_H4_READINGS.tsv',candidates)
    revised=[];removed=0
    for r in manual:
      if r['item_id']=='W:H4-S004':removed+=1;continue
      revised.append(dict(r))
    for i,r in enumerate(revised,1):r['manual_order']=str(i)
    write('FOUR_HUNDRED_NINETY_SIXTH_166_ITEM_H4_DECOMPOSED_MANUAL.tsv',revised)
    tm={r['event_id']:r for r in trace};out=[]
    for r in ledger:
      n=dict(r)
      if r['item_id'] in tm:
        x=tm[r['item_id']];n['semantic_layer']='COMPOSED_EXISTING_COMPONENT_CHAIN';n['syntax_item']=x['manual_item'];n['concrete_reading_de']=x['revised_event_reading_de'];n['local_macro']=MACRO;n['macro_phase']=x['macro_phase']
      out.append(n)
    write('FOUR_HUNDRED_NINETY_SIXTH_776_H4_DECOMPOSED_LEDGER.tsv',out)
    (HERE/'FOUR_HUNDRED_NINETY_SIXTH_COMPLETE_H4_S004_READING.md').write_text('# '+MACRO+'\n\nSetze das Sollmaß und setze den bemessenen Posten an der gelernten Zielstelle an. Trage Pflanzenmaterial in diesen Arbeitsgang weiter ein und bilde daraus einen Ansatz. Halte diesen Ansatz als laufenden Posten und teile eine Portion davon ab.\n\nDie Zielstelle ist gelernt oder bildabhängig; die Karten nennen keine Körperstelle und keine bestimmte Anwendung.\n',encoding='utf-8')
    summary={'status':'PASS','statement_id':TARGET,'events':len(trace),'phases':3,'objects':len(objects),'new_local_values':0,'removed_local_whole_forms':removed,'manual_before':len(manual),'manual_after':len(revised),'ledger_groups':len(out),'macro_events_total':sum(r['local_macro']!='NONE' for r in out)}
    (HERE/'FOUR_HUNDRED_NINETY_SIXTH_BUILD_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
