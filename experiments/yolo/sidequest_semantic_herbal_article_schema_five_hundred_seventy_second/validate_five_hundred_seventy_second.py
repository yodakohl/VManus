#!/usr/bin/env python3
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    slots=read('FIVE_HUNDRED_SEVENTY_SECOND_SIX_HERBAL_ARTICLE_SLOTS.tsv');matrix=read('FIVE_HUNDRED_SEVENTY_SECOND_FIVE_ARTICLE_MATRIX.tsv');statements=read('FIVE_HUNDRED_SEVENTY_SECOND_NINETEEN_STATEMENT_SLOT_MAP.tsv');events=read('FIVE_HUNDRED_SEVENTY_SECOND_ONE_HUNDRED_HERBAL_EVENTS.tsv')
    checks={
        'slots6':len(slots)==6 and len({r['slot'] for r in slots})==6,
        'records5':len(matrix)==5 and {r['record'] for r in matrix}=={'H1','H2','H3','H4','H5'},
        'statements19':len(statements)==19 and len({r['statement_id'] for r in statements})==19,
        'events100':len(events)==100 and len({r['event_id'] for r in events})==100,
        'four_common_two_optional':sum(r['schema_status']=='COMMON_CORE' for r in slots)==4 and sum(r['schema_status']=='OPTIONAL_EXTENSION' for r in slots)==2,
        'common_all_records':all(int(r['records_present'])==5 for r in slots if r['schema_status']=='COMMON_CORE'),
        'all_final_open':all(r['final_committed']=='NO' for r in matrix),
        'bindings_complete':all(r['schema_binding_complete']=='YES' for r in events),
        'fixed_pages':{r['page'] for r in events}=={'f10r','f11r','f55v','f56r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in events),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_SEVENTY_SECOND_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
