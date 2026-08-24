#!/usr/bin/env python3
import csv,json
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 l=r('FIVE_HUNDRED_FIFTEENTH_381_APPRENTICE_COPY_LOG.tsv');c=r('FIVE_HUNDRED_FIFTEENTH_CORRECTION_CHECKPOINTS.tsv');s=r('FIVE_HUNDRED_FIFTEENTH_ELEVEN_RECORD_COPY_SUMMARY.tsv');n=Counter(x['checkpoint'] for x in c)
 checks={'log381':len(l)==381 and len({x['event_id'] for x in l})==381,'records11':len(s)==11 and sum(int(x['events']) for x in s)==381,'checkpoints196':len(c)==196,'owner21':n['RESET_OWNER']==21,'line19':n['CARRY_ACROSS_LINE']==19,'allograph67':n['COPY_LOCAL_ALLOGRAPH']==67,'terminal89':n['ACTION_THEN_CLOSE']==89,'renderer314_67':sum(x['renderer_action']=='ACCEPT_RULE' for x in l)==314 and sum(x['renderer_action']=='COPY_LOCAL_EXEMPLAR' for x in l)==67,'roundtrip381':all(x['card_roundtrip']=='YES' and x['surface_roundtrip']=='YES' for x in l),'teaching_modes99_281_1':sum(x['teaching_mode']=='SEVENTEEN_EXACT_CARD_DECK' for x in l)==99 and sum(x['teaching_mode']=='TWENTY_TWO_COMPONENT_STRIPS' for x in l)==281 and sum(x['teaching_mode']=='ONE_COMPRESSED_STAGE_NOTE' for x in l)==1,'seal_absent':all(not x['page'].lower().startswith('f84') for x in l)}
 z={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(H/'FIVE_HUNDRED_FIFTEENTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
