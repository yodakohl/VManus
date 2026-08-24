#!/usr/bin/env python3
import csv,json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    led=read('FIVE_HUNDRED_FIFTY_EIGHTH_THREE_HUNDRED_EIGHTY_ONE_SURFACE_RENDERER_LEDGER.tsv');ctx=read('FIVE_HUNDRED_FIFTY_EIGHTH_FOUR_CONTEXT_WRAPPER_RULES.tsv');res=read('FIVE_HUNDRED_FIFTY_EIGHTH_FIFTY_NINE_RESIDUAL_LOCAL_ASSIGNMENTS.tsv');multi=read('FIVE_HUNDRED_FIFTY_EIGHTH_THIRTY_FOUR_MULTI_SURFACE_CARDS.tsv');sources=Counter(r['wrapper_assignment_source'] for r in led)
    checks={
        'events381':len(led)==381 and len({r['event_id'] for r in led})==381,
        'multi_cards34':len(multi)==34 and len({r['card_no'] for r in multi})==34,
        'multi_events202':sum(int(r['visible_events']) for r in multi)==202,
        'context_rules4':len(ctx)==4 and sum(int(r['events']) for r in ctx)==8,
        'residual59':len(res)==59 and len({r['event_id'] for r in res})==59,
        'residual_modes34':len({r['residual_locus_mode'] for r in res})==34,
        'sources314_8_59':sources==Counter({'GLOBAL_RULE_RENDERER':314,'AUTOMATIC_CONTEXT_RULE':8,'RESIDUAL_LOCUS_TABLE':59}),
        'surface_roundtrip381':all(r['surface_roundtrip']=='YES' for r in led),
        'no_free_choice':all(r['free_renderer_choice']=='NO' for r in led) and all(r['free_choice']=='NO' for r in res),
        'fixed_pages_only':{r['page'] for r in led}=={'f10r','f11r','f55v','f56r','f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in led),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_FIFTY_EIGHTH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
