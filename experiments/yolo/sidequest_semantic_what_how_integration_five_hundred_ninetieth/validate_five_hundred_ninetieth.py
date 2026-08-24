#!/usr/bin/env python3
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    bridges=read('FIVE_HUNDRED_NINETIETH_SEVENTEEN_CROSS_SECTION_BRIDGES.tsv');phases=read('FIVE_HUNDRED_NINETIETH_PRIMITIVE_PHASE_COMPARISON.tsv');models=read('FIVE_HUNDRED_NINETIETH_TWO_MODEL_SCORECARD.tsv')
    checks={
        'bridges17':len(bridges)==17 and len({r['card_no'] for r in bridges})==17,
        'partition8_9':sum(r['integration_role']=='CONTENT_HANDOFF_CAPABLE' for r in bridges)==8 and sum(r['integration_role']=='SHARED_WORKSHOP_GRAMMAR' for r in bridges)==9,
        'no_pointer':all(r['explicit_cross_record_pointer']=='NO' for r in bridges),
        'phases10':len(phases)==10 and len({r['primitive_phase'] for r in phases})==10,
        'shared9':sum(r['present_both']=='YES' for r in phases)==9,
        'wash_bio_only':next(r for r in phases if r['primitive_phase']=='WASH')['present_both']=='NO',
        'model_total':models[-1]['criterion']=='TOTAL' and int(models[-1]['integrated_what_how_score'])>int(models[-1]['shared_grammar_independent_score']),
        'nonempty':all(r['what_how_reading_de'] for r in bridges) and all(r['workflow_role_de'] for r in phases),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_NINETIETH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
