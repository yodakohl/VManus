#!/usr/bin/env python3
import csv,json
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 p=r('FIVE_HUNDRED_SEVENTEENTH_ALLOGRAPH_POLICY_COMPARISON.tsv');b=r('FIVE_HUNDRED_SEVENTEENTH_FIFTY_ALLOGRAPH_BLOCKS.tsv');l=r('FIVE_HUNDRED_SEVENTEENTH_381_BLOCK_MASTER_LOG.tsv');d=r('FIVE_HUNDRED_SEVENTEENTH_134_REVISED_CONSCIOUS_DECISIONS.tsv');c=Counter(x['decision_type'] for x in d);sel=next(x for x in p if x['selected']=='YES')
 checks={'policies7':len(p)==7,'selected_one_gap':sel['policy']=='ONE_GAP_LOCAL_BLOCK','blocks50':len(b)==50 and len({x['block_id'] for x in b})==50,'span74_extra7':sum(int(x['span_events']) for x in b)==74 and sum(int(x['extra_rule_events_copied']) for x in b)==7,'log381':len(l)==381 and len({x['event_id'] for x in l})==381,'decisions134':len(d)==134,'decision_types63_21_50':c['SELECT_UNUSUAL_PROGRAM']==63 and c['RESET_VISIBLE_OWNER']==21 and c['ENTER_ALLOGRAPH_BLOCK']==50,'conscious_events110':sum(x['revised_master_mode']=='CONSCIOUS_LOCAL_CHOICE' for x in l)==110,'automatic_events271':sum(x['revised_master_mode']=='AUTOMATIC_FLOW' for x in l)==271,'block_starts50':sum(x['block_start_decision']=='YES' for x in l)==50,'seal_absent':all(not x['page'].lower().startswith('f84') for x in l+d)}
 z={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(H/'FIVE_HUNDRED_SEVENTEENTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
