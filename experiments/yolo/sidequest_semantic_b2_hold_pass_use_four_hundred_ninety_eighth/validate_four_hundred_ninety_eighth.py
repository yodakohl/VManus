#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 t=r('FOUR_HUNDRED_NINETY_EIGHTH_FOUR_EVENT_HOLD_PASS_USE_TRACE.tsv');o=r('FOUR_HUNDRED_NINETY_EIGHTH_FOUR_OBJECT_STATES.tsv');c=r('FOUR_HUNDRED_NINETY_EIGHTH_THREE_B2_READINGS.tsv');m=r('FOUR_HUNDRED_NINETY_EIGHTH_164_ITEM_B2_DECOMPOSED_MANUAL.tsv');l=r('FOUR_HUNDRED_NINETY_EIGHTH_776_B2_DECOMPOSED_LEDGER.tsv')
 q={'trace_4':len(t)==4,'ids_exact':[x['event_id'] for x in t]==['E185','E186','E187','E188'],'phases_3':len({x['phase'] for x in t})==3,'objects_4':len(o)==4,'one_selected':sum(x['decision']=='SELECT' for x in c)==1,'manual_164':len(m)==164,'whole_removed':not any(x['item_id']=='W:B2-S006' for x in m),'ledger_776':len(l)==776,'macro_events_88':sum(x['local_macro']!='NONE' for x in l)==88,'b2_macro_4':sum(x['local_macro'].startswith('FOLGEPOSTEN AM BECKEN') for x in l)==4,'all_open':all(x['closes_step']=='NO' for x in t),'sealed_absent':not any('f84' in str(v).lower() for x in t+l for v in x.values())}
 z={'status':'PASS' if all(q.values()) else 'FAIL','checks':q};(H/'FOUR_HUNDRED_NINETY_EIGHTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in q.items()]
 if not all(q.values()):raise SystemExit(1)
if __name__=='__main__':main()
