#!/usr/bin/env python3
import csv,json
from pathlib import Path
H=Path(__file__).resolve().parent
def r(n):
 with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 d=r('FIVE_HUNDRED_THIRTEENTH_SEVENTEEN_CARD_DECK.tsv');o=r('FIVE_HUNDRED_THIRTEENTH_99_DECK_OCCURRENCES.tsv');e=r('FIVE_HUNDRED_THIRTEENTH_TWENTY_TWO_EMBEDDED_ONLY_CORE_VALUES.tsv')
 checks={'deck17':len(d)==17 and len({x['card_no'] for x in d})==17,'atomic12_whole5':sum(x['card_kind']=='ATOMIC_CORE_CARD' for x in d)==12 and sum(x['card_kind']=='MEMORIZED_WHOLE_SIGN' for x in d)==5,'occurrences99':len(o)==99 and len({x['event_id'] for x in o})==99,'occurrence_sum':sum(int(x['occurrences']) for x in d)==99,'embedded22':len(e)==22 and len({x['component_id'] for x in e})==22,'all_examples_real':all(x['real_example_event'] and x['real_example_statement'] for x in d),'all_neighbors':all(x['common_left_neighbors'] and x['common_right_neighbors'] for x in d),'all_embedded_have_hosts':all(int(x['host_card_types'])>=1 for x in e),'seal_absent':all(not x['page'].lower().startswith('f84') for x in o)}
 z={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(H/'FIVE_HUNDRED_THIRTEENTH_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');[print(f"{k}\t{'PASS' if v else 'FAIL'}") for k,v in checks.items()]
 if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
