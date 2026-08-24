#!/usr/bin/env python3
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    slots=read('FIVE_HUNDRED_SEVENTY_THIRD_SIX_BIOLOGICAL_CELL_SLOTS.tsv');matrix=read('FIVE_HUNDRED_SEVENTY_THIRD_FOUR_RECORD_MATRIX.tsv');cells=read('FIVE_HUNDRED_SEVENTY_THIRD_NINETY_THREE_CELL_MAP.tsv');events=read('FIVE_HUNDRED_SEVENTY_THIRD_TWO_HUNDRED_SIXTY_ONE_EVENTS.tsv')
    checks={
        'slots6':len(slots)==6 and len({r['slot'] for r in slots})==6,
        'records4':len(matrix)==4 and {r['record'] for r in matrix}=={'B1','B2','B3','B4'},
        'cells93':len(cells)==93 and len({r['statement_id'] for r in cells})==93,
        'events261':len(events)==261 and len({r['event_id'] for r in events})==261,
        'all_records_all_slots':all(all(r[f'bs{i}']=='USED' for i in range(1,7)) for r in matrix),
        'owner93':sum('BS1' in r['cell_slots'].split('|') for r in cells)==93,
        'operation88':sum('BS5' in r['cell_slots'].split('|') for r in cells)==88,
        'close83':sum('BS6' in r['cell_slots'].split('|') for r in cells)==83,
        'bindings_complete':all(r['schema_binding_complete']=='YES' for r in events),
        'fixed_pages':{r['page'] for r in events}=={'f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in events),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_SEVENTY_THIRD_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
