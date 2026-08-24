#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 s=r('FIVE_HUNDRED_FOURTEENTH_TWENTY_TWO_COMPONENT_STRIPS.tsv');e=r('FIVE_HUNDRED_FOURTEENTH_HOST_EXAMPLES.tsv');c=r('FIVE_HUNDRED_FOURTEENTH_381_TEACHING_COVERAGE.tsv')
 checks={'strips22':len(s)==22 and len({x['component_id'] for x in s})==22,'examples_bound':len(e)==sum(int(x['selected_examples']) for x in s),'one_to_three_examples':all(1<=int(x['selected_examples'])<=3 for x in s),'highlighted':all(f"[{x['component_id']}]" in x['highlighted_parse'] for x in e),'no_standalone_claim':all(x['standalone_exact_card']=='NO' for x in s),'coverage381':len(c)==381 and len({x['event_id'] for x in c})==381,'deck99':sum(x['teaching_mode']=='SEVENTEEN_EXACT_CARD_DECK' for x in c)==99,'strips281':sum(x['teaching_mode']=='TWENTY_TWO_COMPONENT_STRIPS' for x in c)==281,'compressed1':sum(x['teaching_mode']=='ONE_COMPRESSED_STAGE_NOTE' for x in c)==1,'seal_absent':all(not x['page'].lower().startswith('f84') for x in e+c)}
 z={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(H/'FIVE_HUNDRED_FOURTEENTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
