#!/usr/bin/env python3
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    records=read('FIVE_HUNDRED_SEVENTY_FIRST_ELEVEN_NATURAL_RECORD_SUMMARIES.tsv');trans=read('FIVE_HUNDRED_SEVENTY_FIRST_ONE_HUNDRED_SIXTEEN_BOUND_TRANSITIONS.tsv')
    checks={
        'records11':len(records)==11 and len({r['record'] for r in records})==11,
        'transitions116':len(trans)==116 and len({r['statement_id'] for r in trans})==116,
        'statement_sum116':sum(int(r['statements']) for r in records)==116,
        'commit_sum89':sum(int(r['committed_cells']) for r in records)==89,
        'five_herbal':sum(r['record_kind']=='OPEN_HERBAL_ARTICLE' for r in records)==5,
        'four_cellular':sum(r['record_kind'].startswith('CELLULAR') for r in records)==4,
        'two_appendices':sum(r['record_kind']=='TECHNICAL_APPENDIX' for r in records)==2,
        'complete_summaries':all(r['natural_start_material_de'].strip() and r['main_transformations_de'].strip() and r['natural_end_product_or_rest_de'].strip() and r['natural_record_summary_de'].strip() for r in records),
        'all_bound':all(r['transition_bound']=='YES' for r in trans),
        'fixed_pages':{r['page'] for r in trans}=={'f10r','f11r','f55v','f56r','f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in trans),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_SEVENTY_FIRST_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
