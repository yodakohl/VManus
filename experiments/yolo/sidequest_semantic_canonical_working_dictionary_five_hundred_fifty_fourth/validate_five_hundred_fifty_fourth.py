#!/usr/bin/env python3
import csv,json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    comp=read('FIVE_HUNDRED_FIFTY_FOURTH_THIRTY_EIGHT_COMPONENT_DICTIONARY.tsv'); rules=read('FIVE_HUNDRED_FIFTY_FOURTH_FIFTY_SIX_ACTION_FRAME_LEXICON.tsv'); cards=read('FIVE_HUNDRED_FIFTY_FOURTH_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv'); events=read('FIVE_HUNDRED_FIFTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_DICTIONARY.tsv'); cb={r['card_no']:r for r in cards}
    checks={
        'components38':len(comp)==38 and len({r['component'] for r in comp})==38,
        'rules56':len(rules)==56 and len({(r['action_component'],r['frame_code']) for r in rules})==56,
        'cards173':len(cards)==173 and len(cb)==173,
        'events381':len(events)==381 and len({r['event_id'] for r in events})==381,
        'source_positions380':len({r['source_position_id'] for r in events})==380,
        'card_counts':Counter(r['card_no'] for r in events)==Counter({r['card_no']:int(r['occurrences']) for r in cards}),
        'action_nonaction128_45':Counter(r['clause_type']=='ACTION_CLAUSE' for r in cards)==Counter({True:128,False:45}),
        'context_sensitive11':Counter(r['context_sensitive'] for r in cards)==Counter({'NO':162,'YES':11}),
        'all_defaults':all(r['complete_default_available']=='YES' for r in cards+events),
        'card_event_parse_match':all(r['component_parse']==cb[r['card_no']]['component_parse'] for r in events),
        'copy_e180_e181':len([r for r in events if r['source_position_id']=='SRC_E180_E181'])==2,
        'fixed_pages_only':{r['page'] for r in events}=={'f10r','f11r','f55v','f56r','f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in events),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_FIFTY_FOURTH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
