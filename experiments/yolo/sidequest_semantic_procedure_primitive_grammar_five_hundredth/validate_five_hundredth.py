#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 p=r('FIVE_HUNDREDTH_EIGHT_PROCEDURE_PRIMITIVES.tsv');e=r('FIVE_HUNDREDTH_58_EVENT_PRIMITIVE_MAP.tsv');h=r('FIVE_HUNDREDTH_15_PHASE_RECIPES.tsv');c=r('FIVE_HUNDREDTH_FIVE_COMPACT_MACRO_RECIPES.tsv');m=r('FIVE_HUNDREDTH_117_ITEM_PROCEDURE_GRAMMAR_MANUAL.tsv');l=r('FIVE_HUNDREDTH_776_PROCEDURE_PRIMITIVE_LEDGER.tsv');s=r('FIVE_HUNDREDTH_PRIMITIVE_CROSS_MACRO_SUPPORT.tsv')
 q={'primitives_8':len(p)==8,'events_58':len(e)==58,'event_ids_unique':len({x['event_id'] for x in e})==58,'all_mapped':all(x['procedure_primitive']!='NONE' for x in e),'phases_15':len(h)==15,'macros_5':len(c)==5,'macro_counts':sorted(int(x['events']) for x in c)==[9,9,10,11,19],'all_keep_order':all(x['retain_order_recipe']=='YES' for x in c),'manual_117':len(m)==117,'one_proc_rule':sum(x['item_id']=='PROC_G01' for x in m)==1,'unique_manual_ids':len({x['item_id'] for x in m})==117,'ledger_776':len(l)==776,'mapped_58_in_ledger':sum(x['procedure_primitive']!='NONE' for x in l)==58,'all_shared_by_two':all(x['shared_by_at_least_two']=='YES' for x in s),'macro_events_total_88':sum(x['local_macro']!='NONE' for x in l)==88,'sealed_absent':not any('f84' in str(v).lower() for x in e+l for v in x.values())}
 z={'status':'PASS' if all(q.values()) else 'FAIL','checks':q};(H/'FIVE_HUNDREDTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in q.items()]
 if not all(q.values()):raise SystemExit(1)
if __name__=='__main__':main()
