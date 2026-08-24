#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 e=r('FIVE_HUNDRED_SECOND_381_EVENT_PRIMITIVE_MAP.tsv');o=r('FIVE_HUNDRED_SECOND_14_GLOBAL_SUBROUTINE_OCCURRENCES.tsv');s=r('FIVE_HUNDRED_SECOND_THREE_SUBROUTINE_STATUS.tsv');m=r('FIVE_HUNDRED_SECOND_120_ITEM_GLOBAL_SUBROUTINE_MANUAL.tsv');l=r('FIVE_HUNDRED_SECOND_776_GLOBAL_SUBROUTINE_LEDGER.tsv');c=r('FIVE_HUNDRED_SECOND_EIGHT_PRIMITIVE_COUNTS.tsv')
 q={'events_381':len(e)==381,'ids_exact':[x['event_id'] for x in e]==[f'E{i:03d}' for i in range(1,382)],'primitive_types_8':len({x['procedure_primitive'] for x in e})==8,'counts_sum381':sum(int(x['events']) for x in c)==381,'calls_14':len(o)==14,'covered_events_33':len({z for x in o for z in x['event_ids'].split('|')})==33,'new_calls_7':sum(x['status']=='NEW_OUTSIDE_FIVE_MACROS' for x in o)==7,'sub_counts':{x['subroutine']:int(x['calls']) for x in s}=={'SUB01':3,'SUB02':2,'SUB03':9},'sub01_general':next(x['classification'] for x in s if x['subroutine']=='SUB01')=='GENERAL_WORKSHOP_ROUTINE','sub02_pair_only':next(x['classification'] for x in s if x['subroutine']=='SUB02')=='FIVE_MACRO_PAIR_ONLY','sub03_general':next(x['classification'] for x in s if x['subroutine']=='SUB03')=='GENERAL_WORKSHOP_ROUTINE','manual_120':len(m)==120,'ledger_776':len(l)==776,'prose_primitive_381':sum(x['procedure_primitive']!='NONE' for x in l)==381,'subroutine_rows_33':sum(x['procedure_subroutine']!='NONE' for x in l)==33,'sealed_absent':not any('f84' in str(v).lower() for x in e+l for v in x.values())}
 z={'status':'PASS' if all(q.values()) else 'FAIL','checks':q};(H/'FIVE_HUNDRED_SECOND_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in q.items()]
 if not all(q.values()):raise SystemExit(1)
if __name__=='__main__':main()
