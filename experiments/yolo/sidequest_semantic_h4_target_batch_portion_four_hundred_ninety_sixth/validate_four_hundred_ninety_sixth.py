#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def read(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 t=read('FOUR_HUNDRED_NINETY_SIXTH_SIX_EVENT_TARGET_BATCH_TRACE.tsv');c=read('FOUR_HUNDRED_NINETY_SIXTH_COMPLETE_COMPONENT_COVERAGE.tsv');o=read('FOUR_HUNDRED_NINETY_SIXTH_FOUR_OBJECT_STATES.tsv');r=read('FOUR_HUNDRED_NINETY_SIXTH_THREE_H4_READINGS.tsv');m=read('FOUR_HUNDRED_NINETY_SIXTH_166_ITEM_H4_DECOMPOSED_MANUAL.tsv');l=read('FOUR_HUNDRED_NINETY_SIXTH_776_H4_DECOMPOSED_LEDGER.tsv')
 checks={'trace_6':len(t)==6,'ids_exact':[x['event_id'] for x in t]==[f'E{i:03d}' for i in range(68,74)],'phases_3':len({x['macro_phase'] for x in t})==3,'coverage_6':len(c)==6,'all_existing':all(x['existing_item']=='YES' and x['new_local_value']=='NO' for x in c),'objects_4':len(o)==4,'one_selected':sum(x['decision']=='SELECT' for x in r)==1,'manual_166':len(m)==166,'whole_removed':not any(x['item_id']=='W:H4-S004' for x in m),'ledger_776':len(l)==776,'macro_events_78':sum(x['local_macro']!='NONE' for x in l)==78,'h4_macro_6':sum(x['local_macro'].startswith('BEMESSENE PFLANZENPORTION') for x in l)==6,'all_open':all(x['closes_step']=='NO' for x in t),'sealed_absent':not any('f84' in str(v).lower() for x in t+l for v in x.values())}
 result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(H/'FOUR_HUNDRED_NINETY_SIXTH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
 [print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
