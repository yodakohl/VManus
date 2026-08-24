#!/usr/bin/env python3
import csv,json
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 l=r('FIVE_HUNDRED_SIXTEENTH_381_MASTER_COPY_LOG.tsv');d=r('FIVE_HUNDRED_SIXTEENTH_151_CONSCIOUS_DECISIONS.tsv');h=r('FIVE_HUNDRED_SIXTEENTH_SEVEN_AUTOMATIC_MASTER_HABITS.tsv');s=r('FIVE_HUNDRED_SIXTEENTH_ELEVEN_RECORD_MASTER_LOAD.tsv');c=Counter(x['decision_type'] for x in d)
 checks={'events381':len(l)==381 and len({x['event_id'] for x in l})==381,'decisions151':len(d)==151,'unique_program63':c['SELECT_UNUSUAL_PROGRAM']==63,'owner21':c['RESET_VISIBLE_OWNER']==21,'allograph67':c['COPY_LOCAL_ALLOGRAPH']==67,'conscious_events126':sum(x['master_mode']=='CONSCIOUS_LOCAL_CHOICE' for x in l)==126,'automatic_events255':sum(x['master_mode']=='AUTOMATIC_FLOW' for x in l)==255,'decision_counts_match':sum(int(x['master_conscious_decision_count']) for x in l)==151,'habits7':len(h)==7,'records11':len(s)==11 and sum(int(x['events']) for x in s)==381,'seal_absent':all(not x['page'].lower().startswith('f84') for x in l+d)}
 z={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(H/'FIVE_HUNDRED_SIXTEENTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
