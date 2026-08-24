#!/usr/bin/env python3
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    cards=read('FIVE_HUNDRED_SEVENTY_FOURTH_SEVENTEEN_PORTABLE_CARDS.tsv');events=read('FIVE_HUNDRED_SEVENTY_FOURTH_ONE_HUNDRED_THIRTY_SIX_PORTABLE_EVENTS.tsv');inv=read('FIVE_HUNDRED_SEVENTY_FOURTH_THREE_INVENTORY_CLASSES.tsv')
    checks={
        'cards17':len(cards)==17 and len({r['card_no'] for r in cards})==17,
        'events136':len(events)==136 and len({r['event_id'] for r in events})==136,
        'herbal44_bio92':sum(r['section']=='HERBAL' for r in events)==44 and sum(r['section']=='BIOLOGICAL' for r in events)==92,
        'inventory173':sum(int(r['card_types']) for r in inv)==173,
        'inventory381':sum(int(r['events']) for r in inv)==381,
        'class_counts':{r['inventory_class']:int(r['card_types']) for r in inv}=={'CROSS_SECTION_PORTABLE':17,'HERBAL_LOCAL':49,'BIOLOGICAL_LOCAL':107},
        'atomic_invariant':all(r['atomic_value_changes_by_section']=='NO' and r['only_object_filling_changes']=='YES' for r in cards),
        'event_complete':all(r['portable_reading_complete']=='YES' for r in events),
        'fixed_pages':{r['page'] for r in events}<={'f10r','f11r','f55v','f56r','f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in events),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_SEVENTY_FOURTH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
