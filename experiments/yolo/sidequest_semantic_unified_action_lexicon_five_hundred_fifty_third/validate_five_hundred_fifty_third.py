#!/usr/bin/env python3
import csv, json
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
def read(name):
    with (HERE/name).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def main():
    rules=read("FIVE_HUNDRED_FIFTY_THIRD_UNIFIED_ACTION_FRAME_LEXICON.tsv"); actions=read("FIVE_HUNDRED_FIFTY_THIRD_TWO_HUNDRED_SEVENTY_ONE_ACTION_OCCURRENCES.tsv"); clauses=read("FIVE_HUNDRED_FIFTY_THIRD_TWO_HUNDRED_FORTY_ONE_REVISED_BUNDLES.tsv"); instructions=read("FIVE_HUNDRED_FIFTY_THIRD_NINETY_SEVEN_REVISED_INSTRUCTIONS.tsv"); articles=read("FIVE_HUNDRED_FIFTY_THIRD_ELEVEN_REVISED_ARTICLES.tsv")
    expected=Counter({'OK':79,'CHD':48,'L':27,'SH':25,'K':21,'CH':16,'SHED':15,'T':10,'CHK':7,'SOLK':7,'R':6,'LSH':3,'P':3,'CFH':1,'S':1,'LD':1,'TALAM':1})
    checks={
        'components17':len({r['action_component'] for r in rules})==17,
        'rules56':len(rules)==56 and len({(r['action_component'],r['frame_code']) for r in rules})==56,
        'actions271':len(actions)==271 and Counter(r['action_component'] for r in actions)==expected,
        'rule_coverage':Counter((r['action_component'],r['frame_code']) for r in actions)==Counter({(r['action_component'],r['frame_code']):int(r['occurrences']) for r in rules}),
        'clauses241':len(clauses)==241 and len({r['clause_id'] for r in clauses})==241,
        'instructions97':len(instructions)==97 and len({r['instruction_id'] for r in instructions})==97,
        'articles11':len(articles)==11 and len({r['record'] for r in articles})==11,
        'visible381':len({e for r in clauses for e in r['visible_event_ids'].split('|')})==381,
        'source380':len({s for r in clauses for s in r['source_position_ids'].split('|')})==380,
        'components_unchanged':all(r['component_values_changed']=='NO' for r in actions+clauses),
        'record_ends8_3':Counter(r['record_final_status'] for r in articles)==Counter({'RECORD_FINAL_OPEN':8,'COMMITTED_CLOSE':3}),
        'fixed_pages_only':{r['page'] for r in actions}=={'f10r','f11r','f55v','f56r','f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in actions),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_FIFTY_THIRD_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
