#!/usr/bin/env python3
import csv,json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    rules=read('FIVE_HUNDRED_FIFTY_SEVENTH_ELEVEN_ALLOGRAPH_RULES.tsv');audit=read('FIVE_HUNDRED_FIFTY_SEVENTH_SEVENTY_FOUR_ALLOGRAPH_EVENT_AUDIT.tsv');steps=read('FIVE_HUNDRED_FIFTY_SEVENTH_REVISED_TRACE_STEPS.tsv');summary=json.loads((HERE/'FIVE_HUNDRED_FIFTY_SEVENTH_BUILD_SUMMARY.json').read_text())
    checks={
        'rules11':len(rules)==11 and len({r['component_parse'] for r in rules})==11,
        'events74':len(audit)==74 and len({r['event_id'] for r in audit})==74,
        'full_rule74':all(r['exact_card_match']=='YES' for r in audit),
        'without_memory71':sum(r['structural_without_local_memory_match']=='YES' for r in audit)==71,
        'rule_types_5_5_1':Counter(r['rule_type'] for r in rules)==Counter({'NEIGHBOR_RULE':5,'RECORD_RULE':5,'LOCAL_LOCUS_MEMORY':1}),
        'rule_event_counts':sum(int(r['events']) for r in rules)==74 and sum(int(r['full_rule_correct']) for r in rules)==74,
        'global381':summary['global_exact_card_with_full_rules']==381,
        'global_without_memory378':summary['global_exact_card_without_local_memory']==378,
        'trace_steps_exact':all(r['renderer_exact_match']=='YES' for r in steps),
        'fixed_pages_only':{r['page'] for r in audit}=={'f10r','f11r','f55v','f56r','f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in audit),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_FIFTY_SEVENTH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
