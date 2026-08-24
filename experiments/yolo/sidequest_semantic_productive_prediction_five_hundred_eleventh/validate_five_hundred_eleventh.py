#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 p=r('FIVE_HUNDRED_ELEVENTH_TWELVE_PRODUCTIVE_CARD_PREDICTIONS.tsv');s=r('FIVE_HUNDRED_ELEVENTH_ELEVEN_REVISED_STATEMENTS.tsv');c=r('FIVE_HUNDRED_ELEVENTH_WORD_VERSUS_COMPOSITION_COMPARISON.tsv')
 checks={'predictions12':len(p)==12 and len({x['card_id'] for x in p})==12,'statements11':len(s)==11 and len({x['statement_id'] for x in s})==11,'comparison12':len(c)==12,'herbal7_bio5':sum(x['record'].startswith('H') for x in p)==7 and sum(x['record'].startswith('B') for x in p)==5,'records9':len({x['record'] for x in s})==9,'all_composed':all('+' in x['component_parse'] for x in p),'no_whole_required':all(x['whole_word_required']=='NO' for x in p),'no_new_values':all(x['new_semantic_values_added']=='0' for x in s),'complete_rewrites':all(len(x['complete_revised_statement_de'].split())>=8 for x in s),'seal_absent':all(not x['page'].lower().startswith('f84') for x in p+s)}
 z={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(H/'FIVE_HUNDRED_ELEVENTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
