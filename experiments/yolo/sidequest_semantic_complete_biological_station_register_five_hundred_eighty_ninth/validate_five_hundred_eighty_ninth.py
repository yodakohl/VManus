#!/usr/bin/env python3
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):
    with (HERE/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
    records=read('FIVE_HUNDRED_EIGHTY_NINTH_SIX_BIOLOGICAL_RECORDS.tsv');statements=read('FIVE_HUNDRED_EIGHTY_NINTH_NINETY_SEVEN_STATION_ENTRIES.tsv');events=read('FIVE_HUNDRED_EIGHTY_NINTH_TWO_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv')
    checks={
        'records6':len(records)==6 and {r['record'] for r in records}=={'B1','B2','B3','B4','B5','B6'},
        'statements97':len(statements)==97 and len({r['statement_id'] for r in statements})==97,
        'events281':len(events)==281 and len({r['event_id'] for r in events})==281,
        'event_sums':sum(int(r['events']) for r in records)==281 and sum(int(r['event_total']) for r in statements)==281,
        'close85_open12':sum(r['cell_status']=='CLOSED_CELL' for r in statements)==85 and sum(r['cell_status']=='OPEN_ENTRY' for r in statements)==12,
        'b1_b4_close83':sum(r['cell_status']=='CLOSED_CELL' and r['record'] in {'B1','B2','B3','B4'} for r in statements)==83,
        'types':all((r['record'] in {'B1','B2','B3','B4'})==(r['record_type']=='LOCAL_STATION_CELL_REGISTER') for r in records+statements),
        'no_global_flow':all(r['global_flow_claim']=='NONE' for r in records),
        'bound':all(r['all_source_events_bound']=='YES' for r in statements) and all(r['bound_once']=='YES' for r in events),
        'pages':{r['page'] for r in events}<={'f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in events),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_EIGHTY_NINTH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
