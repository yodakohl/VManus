#!/usr/bin/env python3
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    cards=read('FIVE_HUNDRED_SEVENTY_FIFTH_ONE_HUNDRED_FIFTY_SIX_LOCAL_CARDS.tsv');events=read('FIVE_HUNDRED_SEVENTY_FIFTH_TWO_HUNDRED_FORTY_FIVE_LOCAL_EVENTS.tsv');special=read('FIVE_HUNDRED_SEVENTY_FIFTH_SEVEN_SPECIALIST_CARDS.tsv');summary=read('FIVE_HUNDRED_SEVENTY_FIFTH_SECTION_SUMMARY.tsv')
    checks={
        'cards156':len(cards)==156 and len({r['card_no'] for r in cards})==156,
        'events245':len(events)==245 and len({r['event_id'] for r in events})==245,
        'partition34_115_7':sum(r['section_local_partition']=='LOCAL_RECURRENT_COMPOSITION' for r in cards)==34 and sum(r['section_local_partition']=='LOCAL_SINGLETON_COMPOSITION' for r in cards)==115 and sum(r['section_local_partition']=='LOCAL_SPECIALIST_WHOLE_OR_ATOM' for r in cards)==7,
        'recurrent_events123':sum(int(r['occurrences']) for r in cards if r['section_local_partition']=='LOCAL_RECURRENT_COMPOSITION')==123,
        'component_generated149':sum(r['semantic_learning_rule']=='GENERATE_FROM_COMPONENTS' for r in cards)==149,
        'specialist7':len(special)==7 and len({r['card_no'] for r in special})==7,
        'all_events_complete':all(r['event_reading_complete']=='YES' for r in events),
        'section_counts':{r['section']:int(r['local_cards']) for r in summary if r['section']!='BOTH_LOCAL'}=={'HERBAL':49,'BIOLOGICAL':107},
        'fixed_pages':{r['page'] for r in events}<={'f10r','f11r','f55v','f56r','f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in events),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_SEVENTY_FIFTH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
