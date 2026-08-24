#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 e=r('FIVE_HUNDRED_THIRD_381_EVENT_EXPANDED_TOKENS.tsv');s=r('FIVE_HUNDRED_THIRD_116_STATEMENT_PROGRAMS.tsv');p=r('FIVE_HUNDRED_THIRD_72_PROGRAM_INVENTORY.tsv');q9=r('FIVE_HUNDRED_THIRD_NINE_RECURRENT_PROGRAMS.tsv');t=r('FIVE_HUNDRED_THIRD_TERMINAL_OPERATION_COUNTS.tsv');m=r('FIVE_HUNDRED_THIRD_120_ITEM_STATEMENT_PROGRAM_MANUAL.tsv');l=r('FIVE_HUNDRED_THIRD_776_STATEMENT_PROGRAM_LEDGER.tsv')
 q={'events_381':len(e)==381,'tokens_470':sum(int(x['emitted_token_count']) for x in e)==470,'close_events_89':sum(x['closes_step']=='YES' for x in e)==89,'every_close_emits_two':all(int(x['emitted_token_count'])==2 and x['emitted_procedure_tokens'].endswith('>CLOSE') for x in e if x['closes_step']=='YES'),'statements_116':len(s)==116,'programs_72':len(p)==72,'recurrent_9':len(q9)==9,'recurrent_support_53':sum(int(x['support']) for x in q9)==53,'unique_programs_63':sum(x['status']=='UNIQUE_PROGRAM' for x in p)==63,'herbal_19_all_unique':sum(x['record'].startswith('H') and x['program_status']=='UNIQUE' for x in s)==19,'bio_44_unique':sum(x['record'].startswith('B') and x['program_status']=='UNIQUE' for x in s)==44,'terminal_ops_sum89':sum(int(x['events']) for x in t)==89,'manual_120':len(m)==120,'ledger_776':len(l)==776,'program_rows_381':sum(x['statement_program']!='NONE' for x in l)==381,'sealed_absent':not any('f84' in str(v).lower() for x in e+l for v in x.values())}
 z={'status':'PASS' if all(q.values()) else 'FAIL','checks':q};(H/'FIVE_HUNDRED_THIRD_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in q.items()]
 if not all(q.values()):raise SystemExit(1)
if __name__=='__main__':main()
