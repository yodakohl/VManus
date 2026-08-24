#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 t=r('FOUR_HUNDRED_NINETY_SEVENTH_SIX_EVENT_RECEIVE_EXIT_TRACE.tsv');b=r('FOUR_HUNDRED_NINETY_SEVENTH_FIVE_BOUNDARY_DECISIONS.tsv');o=r('FOUR_HUNDRED_NINETY_SEVENTH_FIVE_LOCAL_OBJECTS.tsv');c=r('FOUR_HUNDRED_NINETY_SEVENTH_THREE_B4_READINGS.tsv');m=r('FOUR_HUNDRED_NINETY_SEVENTH_165_ITEM_B4_DECOMPOSED_MANUAL.tsv');l=r('FOUR_HUNDRED_NINETY_SEVENTH_776_B4_DECOMPOSED_LEDGER.tsv')
 q={'trace_6':len(t)==6,'ids_exact':[x['event_id'] for x in t]==[f'E{i:03d}' for i in range(352,358)],'stations_2':{x['station'] for x in t}=={'STATION_A','STATION_B'},'boundaries_5':len(b)==5,'one_reset':sum(x['owner']=='RESET_B' for x in b)==1,'no_carry_reset':all(x['material']=='DO_NOT_CARRY' for x in b if x['owner']=='RESET_B'),'objects_5':len(o)==5,'no_object_crosses':all(x['crosses_gap']=='NO' for x in o),'one_selected':sum(x['decision']=='SELECT' for x in c)==1,'manual_165':len(m)==165,'whole_removed':not any(x['item_id']=='W:B4-S015' for x in m),'ledger_776':len(l)==776,'macro_events_84':sum(x['local_macro']!='NONE' for x in l)==84,'b4_macro_6':sum(x['local_macro'].startswith('EMPFANGSPORTION') for x in l)==6,'close_e357':[x['event_id'] for x in t if x['closes_step']=='YES']==['E357'],'sealed_absent':not any('f84' in str(v).lower() for x in t+l for v in x.values())}
 z={'status':'PASS' if all(q.values()) else 'FAIL','checks':q};(H/'FOUR_HUNDRED_NINETY_SEVENTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in q.items()]
 if not all(q.values()):raise SystemExit(1)
if __name__=='__main__':main()
