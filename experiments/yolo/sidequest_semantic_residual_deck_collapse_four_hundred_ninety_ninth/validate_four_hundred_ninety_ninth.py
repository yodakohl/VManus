#!/usr/bin/env python3
import csv,json,collections
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 i=r('FOUR_HUNDRED_NINETY_NINTH_49_REMOVED_LOCAL_ITEMS.tsv');e=r('FOUR_HUNDRED_NINETY_NINTH_204_EVENT_REMAP.tsv');m=r('FOUR_HUNDRED_NINETY_NINTH_116_ITEM_COLLAPSED_MANUAL.tsv');l=r('FOUR_HUNDRED_NINETY_NINTH_776_COLLAPSED_LEDGER.tsv');p=r('FOUR_HUNDRED_NINETY_NINTH_FIVE_RETAINED_PROCEDURE_MACROS.tsv');s=r('FOUR_HUNDRED_NINETY_NINTH_116_ITEM_LAYER_SUMMARY.tsv')
 c=collections.Counter(x['layer'] for x in m)
 q={'removed_49':len(i)==49,'removed_46_x':sum(x['old_type']=='STATEMENT_RESIDUAL' for x in i)==46,'removed_3_r':sum(x['old_type']=='SMALL_RECURRENT_RESIDUAL' for x in i)==3,'remap_204':len(e)==204,'all_remapped':all(x['local_value_removed']=='YES' for x in e),'no_x_r_syntax':not any(x['syntax_item'].startswith(('X:','R0')) for x in l),'manual_116':len(m)==116,'one_clause_g01':sum(x['item_id']=='CLAUSE_G01' for x in m)==1,'unique_item_ids':len({x['item_id'] for x in m})==116,'macros_5':len(p)==5,'macro_event_counts':sorted(int(x['event_count']) for x in p)==[9,9,10,11,19],'local_layers_6':c['L6_REDUCED_LOCAL_DECK']+c['L6_GENERAL_LOCAL_CLAUSE_GRAMMAR']==6,'ledger_776':len(l)==776,'macro_events_88':sum(x['local_macro']!='NONE' for x in l)==88,'layer_sum_116':sum(int(x['items']) for x in s)==116,'sealed_absent':not any('f84' in str(v).lower() for x in e+l for v in x.values())}
 z={'status':'PASS' if all(q.values()) else 'FAIL','checks':q};(H/'FOUR_HUNDRED_NINETY_NINTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in q.items()]
 if not all(q.values()):raise SystemExit(1)
if __name__=='__main__':main()
