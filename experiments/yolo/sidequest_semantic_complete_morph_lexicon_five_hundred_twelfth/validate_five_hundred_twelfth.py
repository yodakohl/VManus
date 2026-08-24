#!/usr/bin/env python3
import csv,json
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 l=r('FIVE_HUNDRED_TWELFTH_173_COMPLETE_MORPHOLOGICAL_LEXICON.tsv');e=r('FIVE_HUNDRED_TWELFTH_381_EVENT_MORPHOLOGICAL_READINGS.tsv');s=r('FIVE_HUNDRED_TWELFTH_116_STATEMENT_MORPHOLOGICAL_READINGS.tsv');c=r('FIVE_HUNDRED_TWELFTH_MORPHOLOGY_COUNTS.tsv');n=Counter(x['morphological_class'] for x in l);ne=Counter(x['morphological_class'] for x in e)
 checks={'lexicon173':len(l)==173 and len({x['joint_tuple_id'] for x in l})==173,'events381':len(e)==381 and len({x['event_id'] for x in e})==381,'statements116':len(s)==116 and sum(int(x['events']) for x in s)==381,'full_compositions155':n['FULL_COMPONENT_COMPOSITION']==155,'atomic12':n['ATOMIC_CORE_CARD']==12,'compressed1':n['COMPRESSED_KNOWN_VALUE_SIGN']==1,'whole5':n['MEMORIZED_WHOLE_SIGN']==5,'class_totals_match':all(int(x['card_types'])==n[x['morphological_class']] and int(x['events'])==ne[x['morphological_class']] for x in c),'all_parts_known':all(x['expanded_semantic_parts'] and x['literal_pocket_reading_de'] for x in l),'all_event_cards_bound':all(x['card_no'] for x in e),'no_unknown_words':not any('UNKNOWN' in x['literal_pocket_reading_de'].upper() for x in l),'seal_absent':all(not x['page'].lower().startswith('f84') for x in e)}
 z={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(H/'FIVE_HUNDRED_TWELFTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
