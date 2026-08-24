#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 c=r('FIVE_HUNDRED_FIRST_CROSS_MACRO_NGRAM_CANDIDATES.tsv');o=r('FIVE_HUNDRED_FIRST_SEVEN_SUBROUTINE_OCCURRENCES.tsv');p=r('FIVE_HUNDRED_FIRST_FIVE_SUBROUTINE_COMPRESSED_RECIPES.tsv');a=r('FIVE_HUNDRED_FIRST_SUBROUTINE_COST_ACCOUNT.tsv');m=r('FIVE_HUNDRED_FIRST_120_ITEM_SUBROUTINE_MANUAL.tsv');l=r('FIVE_HUNDRED_FIRST_776_SUBROUTINE_LEDGER.tsv')
 q={'candidate_rows_13':len(c)==13,'selected_3':len({x['subroutine'] for x in o})==3,'calls_7':len(o)==7,'covered_events_18':len({z for x in o for z in x['event_ids'].split('|')})==18,'cross_phase_sub02_2':sum(x['subroutine']=='SUB02' and x['crosses_phase_boundary']=='YES' for x in o)==2,'recipes_5':len(p)==5,'order_preserved':all(x['event_order_preserved']=='YES' for x in p),'compressed_tokens_47':sum(int(x['recipe_tokens_after']) for x in p)==47,'cost_total_55':next(int(x['tokens']) for x in a if x['account']=='selector_paid_total')==55,'gain_3':next(int(x['tokens']) for x in a if x['account']=='selector_paid_gain')==3,'manual_120':len(m)==120,'unique_ids':len({x['item_id'] for x in m})==120,'ledger_776':len(l)==776,'subroutine_event_rows_18':sum(x['procedure_subroutine']!='NONE' for x in l)==18,'sealed_absent':not any('f84' in str(v).lower() for x in o+l for v in x.values())}
 z={'status':'PASS' if all(q.values()) else 'FAIL','checks':q};(H/'FIVE_HUNDRED_FIRST_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in q.items()]
 if not all(q.values()):raise SystemExit(1)
if __name__=='__main__':main()
