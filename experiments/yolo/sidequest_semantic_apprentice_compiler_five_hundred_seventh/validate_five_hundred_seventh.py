#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 e=r('FIVE_HUNDRED_SEVENTH_381_FORWARD_BACKWARD_CARD_TRACES.tsv');s=r('FIVE_HUNDRED_SEVENTH_116_STATEMENT_COMPILER_TRACES.tsv');c=r('FIVE_HUNDRED_SEVENTH_TWELVE_STEP_APPRENTICE_COMPILER.tsv');m=r('FIVE_HUNDRED_SEVENTH_125_ITEM_APPRENTICE_MANUAL.tsv')
 checks={'events381':len(e)==381 and len({x['event_id'] for x in e})==381,'statements116':len(s)==116 and len({x['statement_id'] for x in s})==116,'records11':len({x['record'] for x in s})==11,'tokens470':sum(int(x['emitted_tokens']) for x in s)==470,'owner_resets21':sum(x['owner_reset']=='YES' for x in e)==21,'renderer314plus67':sum(x['renderer_mode']=='RULE' for x in e)==314 and sum(x['renderer_mode']=='COPY_LOCAL_ALLOGRAPH' for x in e)==67,'card_roundtrip':all(x['roundtrip_card']=='YES' for x in e),'closed_terminal':all(x['automaton_after']=='CLOSED' for x in e if 'CLOSE' in x['procedure_tokens']),'twelve_steps':len(c)==12,'manual125':len(m)==125 and sum(x['item_id']=='COMPILER_G01' for x in m)==1,'all_fields_nonempty':all(all(v!='' for v in x.values()) for x in e+s+c),'seal_absent':all(not x['page'].lower().startswith('f84') for x in e)}
 z={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(H/'FIVE_HUNDRED_SEVENTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
