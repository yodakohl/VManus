#!/usr/bin/env python3
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    manual=read('FIVE_HUNDRED_FIFTY_SIXTH_FOURTEEN_RULE_APPRENTICE_MANUAL.tsv'); inv=read('FIVE_HUNDRED_FIFTY_SIXTH_ONE_HUNDRED_SIXTY_TWO_PARSE_INVENTORY.tsv'); norms=read('FIVE_HUNDRED_FIFTY_SIXTH_ELEVEN_ALLOGRAPH_NORMALIZATIONS.tsv'); steps=read('FIVE_HUNDRED_FIFTY_SIXTH_REPRESENTATIVE_TRACE_STEPS.tsv'); traces=read('FIVE_HUNDRED_FIFTY_SIXTH_FOURTEEN_ROUNDTRIP_TRACES.tsv'); summary=json.loads((HERE/'FIVE_HUNDRED_FIFTY_SIXTH_BUILD_SUMMARY.json').read_text())
    checks={
        'manual14':len(manual)==14 and len({r['rule_no'] for r in manual})==14,
        'parse_inventory162':len(inv)==162 and len({r['component_parse'] for r in inv})==162,
        'ambiguous11':sum(r['exact_card_requires_allograph_choice']=='YES' for r in inv)==11,
        'ambiguous_atomic_agreement':all(r['atomic_value_agreement']=='YES' for r in inv if r['exact_card_requires_allograph_choice']=='YES'),
        'normalizations11':len(norms)==11 and all(r['semantic_allograph']=='YES' for r in norms),
        'cards173':sum(int(r['candidate_card_count']) for r in inv)==173,
        'traces14':len(traces)==14 and len({r['trace_no'] for r in traces})==14,
        'all_records':{r['record'] for r in traces}=={'H1','H2','H3','H4','H5','B1','B2','B3','B4','B5','B6'},
        'trace_steps_partition':sum(int(r['source_steps']) for r in traces)==len(steps),
        'semantic_roundtrip':all(r['semantic_roundtrip']=='PASS' and r['master_card_prose_used']=='NO' for r in traces+steps),
        'global_events381':summary['semantic_atomic_roundtrip_events']==381,
        'ambiguous_22_74':summary['ambiguous_cards']==22 and summary['ambiguous_visible_events']==74,
        'unique_events307':summary['unique_card_visible_events']==307,
        'fixed_pages_only':{r['page'] for r in traces}=={'f10r','f11r','f55v','f56r','f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in traces),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_FIFTY_SIXTH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
