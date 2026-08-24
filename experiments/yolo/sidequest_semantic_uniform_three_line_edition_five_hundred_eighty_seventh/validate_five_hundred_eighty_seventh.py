#!/usr/bin/env python3
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    rows=read('FIVE_HUNDRED_EIGHTY_SEVENTH_ONE_HUNDRED_SIXTEEN_THREE_LINE_STATEMENTS.tsv');events=read('FIVE_HUNDRED_EIGHTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_INDEX.tsv')
    checks={
        'statements116':len(rows)==116 and len({r['statement_id'] for r in rows})==116,
        'events381':len(events)==381 and len({r['event_id'] for r in events})==381,
        'records11':len({r['record'] for r in rows})==11,
        'partition73_21_10_12':sum(r['formula_mode']=='TAUGHT_MACRO' for r in rows)==73 and sum(r['formula_mode']=='SIMPLE_ONE_EDIT_VARIANT' for r in rows)==21 and sum(r['formula_mode']=='EXTENDED_TWO_EDIT_VARIANT' for r in rows)==10 and sum(r['formula_mode']=='FREE_COMPOSITION' for r in rows)==12,
        'event_sum':sum(int(r['event_count']) for r in rows)==381,
        'three_lines':all(r['visible_cards'] and r['component_parses'] and r['spoken_component_line_de'] and r['complete_owner_filled_instruction_de'] for r in rows),
        'bound':all(r['all_events_bound']=='YES' for r in rows) and all(r['bound_to_complete_instruction']=='YES' for r in events),
        'event_statement_sets':{r['statement_id'] for r in rows}=={r['statement_id'] for r in events},
        'fixed_pages':{r['page'] for r in events}<={'f10r','f11r','f55v','f56r','f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in events),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_EIGHTY_SEVENTH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
