#!/usr/bin/env python3
import csv, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(name):
    with (HERE/name).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    statements=read('FIVE_HUNDRED_EIGHTY_SIXTH_TWENTY_TWO_LONG_STATEMENTS.tsv');groups=read('FIVE_HUNDRED_EIGHTY_SIXTH_BREATH_GROUPS.tsv');events=read('FIVE_HUNDRED_EIGHTY_SIXTH_ONE_HUNDRED_FIFTY_SIX_GROUPED_EVENTS.tsv')
    checks={
        'statements22':len(statements)==22 and len({r['statement_id'] for r in statements})==22,
        'partition10_12':sum(r['learning_mode']=='EXTENDED_TWO_EDIT_VARIANT' for r in statements)==10 and sum(r['learning_mode']=='FREE_COMPOSITION' for r in statements)==12,
        'events156':len(events)==156 and len({r['event_id'] for r in events})==156,
        'groups_nonempty':len(groups)>0 and all(1<=int(r['events'])<=4 for r in groups),
        'group_event_sum':sum(int(r['events']) for r in groups)==156,
        'statement_event_sum':sum(int(r['events']) for r in statements)==156,
        'event_group_binding':{r['event_id'] for r in events}=={x for r in groups for x in r['event_ids'].split('|')},
        'complete':all(r['complete']=='YES' for r in statements) and all(r['all_events_retained']=='YES' for r in groups),
        'fixed_pages':{r['page'] for r in events}<={'f10r','f11r','f55v','f56r','f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in events),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_EIGHTY_SIXTH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
