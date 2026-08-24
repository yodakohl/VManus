#!/usr/bin/env python3
import csv,json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    audit=read('FIVE_HUNDRED_FIFTY_FIFTH_ELEVEN_CARD_UNIFICATION_AUDIT.tsv');cards=read('FIVE_HUNDRED_FIFTY_FIFTH_ONE_HUNDRED_SEVENTY_THREE_ATOMIC_CARD_DICTIONARY.tsv');events=read('FIVE_HUNDRED_FIFTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_ATOMIC_EVENT_DICTIONARY.tsv');cb={r['card_no']:r for r in cards};targets={r['card_no'] for r in audit}
    checks={
        'audit11':len(audit)==11 and len(targets)==11,
        'cards173':len(cards)==173 and len(cb)==173,
        'events381':len(events)==381 and len({r['event_id'] for r in events})==381,
        'source380':len({r['source_position_id'] for r in events})==380,
        'all_atomic_stable':all(r['atomic_context_stable']=='YES' for r in cards),
        'multi_expansion11':Counter(r['has_multiple_local_expansions'] for r in cards)==Counter({'NO':162,'YES':11}),
        'expansion_events70':sum(r['card_no'] in targets for r in events)==70,
        'card_event_atomic_match':all(r['atomic_card_value_de']==cb[r['card_no']]['atomic_card_value_de'] for r in events),
        'all_defaults':all(r['complete_default_available']=='YES' for r in events),
        'fixed_pages_only':{r['page'] for r in events}=={'f10r','f11r','f55v','f56r','f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in events),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_FIFTY_FIFTH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
