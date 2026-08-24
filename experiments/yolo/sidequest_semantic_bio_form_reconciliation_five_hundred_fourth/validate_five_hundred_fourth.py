#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 c=r('FIVE_HUNDRED_FOURTH_116_OLD_NEW_FORM_CROSSWALK.tsv');p=r('FIVE_HUNDRED_FOURTH_NINE_SELECTED_BIO_FORM_PROGRAMS.tsv');lo=r('FIVE_HUNDRED_FOURTH_FOUR_OLD_FALSE_RECURRENCES.tsv');ga=r('FIVE_HUNDRED_FOURTH_SIX_NEW_RECURRENCES.tsv');m=r('FIVE_HUNDRED_FOURTH_122_ITEM_RECONCILED_MANUAL.tsv');l=r('FIVE_HUNDRED_FOURTH_776_RECONCILED_FORM_LEDGER.tsv')
 q={'crosswalk_116':len(c)==116,'old_recurrent_51':sum(x['old_form_class']!='LOCAL_FORM' for x in c)==51,'programs_9':len(p)==9,'new_recurrent_53':sum(int(x['support_statements']) for x in p)==53,'lost_4':len(lo)==4,'gained_6':len(ga)==6,'recurrent_overlap_47':sum(x['relation']=='OLD_AND_NEW_RECURRENT' for x in c)==47,'manual_122':len(m)==122,'no_old_form_layer':not any(x['layer']=='L4_BIO_FORM_CARD' for x in m),'nine_new_form_rows':sum(x['layer']=='L4_BIO_PRIMITIVE_PROGRAM' for x in m)==9,'unique_ids':len({x['item_id'] for x in m})==122,'ledger_776':len(l)==776,'bio_program_statement_count':len({x['statement_or_locus'] for x in l if x['bio_form_program']!='NONE'})==53,'sealed_absent':not any('f84' in str(v).lower() for x in c+l for v in x.values())}
 z={'status':'PASS' if all(q.values()) else 'FAIL','checks':q};(H/'FIVE_HUNDRED_FOURTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in q.items()]
 if not all(q.values()):raise SystemExit(1)
if __name__=='__main__':main()
