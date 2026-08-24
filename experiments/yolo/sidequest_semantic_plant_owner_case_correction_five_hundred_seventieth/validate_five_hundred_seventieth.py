#!/usr/bin/env python3
import csv,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(name):
    with (HERE/name).open(encoding='utf-8',newline='') as handle:return list(csv.DictReader(handle,delimiter='\t'))
def main():
    events=read('FIVE_HUNDRED_SEVENTIETH_THREE_HUNDRED_EIGHTY_ONE_CORRECTED_EVENTS.tsv')
    statements=read('FIVE_HUNDRED_SEVENTIETH_ONE_HUNDRED_SIXTEEN_CORRECTED_STATEMENTS.tsv')
    profiles=read('FIVE_HUNDRED_SEVENTIETH_EIGHT_CORRECTED_PROFILES.tsv')
    transitions=read('FIVE_HUNDRED_SEVENTIETH_ONE_HUNDRED_SIXTEEN_CORRECTED_TRANSITIONS.tsv')
    records=read('FIVE_HUNDRED_SEVENTIETH_ELEVEN_CORRECTED_RECORD_FLOWS.tsv')
    checks={
        'events381':len(events)==381 and len({r['event_id'] for r in events})==381,
        'statements116':len(statements)==116 and len({r['statement_id'] for r in statements})==116,
        'profiles8':len(profiles)==8 and sum(int(r['events']) for r in profiles)==381,
        'transitions116':len(transitions)==116 and all(r['transition_complete']=='YES' for r in transitions),
        'records11':len(records)==11,
        'h3_events17_corrected':sum(r['owner_class_changed']=='YES' for r in events)==17 and all(r['corrected_owner_object_class']=='PLANT_MATERIAL' for r in events if r['record']=='H3'),
        'h3_statements4_corrected':sum(r['owner_class_changed']=='YES' for r in statements)==4 and all(r['corrected_owner_object_class']=='PLANT_MATERIAL' for r in statements if r['record']=='H3'),
        'h3_start_plant':next(r['start_object'] for r in records if r['record']=='H3')=='PICTURED_PLANT_MATTER',
        'other_events_unchanged':sum(r['previous_owner_object_class']==r['corrected_owner_object_class'] for r in events)==364,
        'fixed_pages':{r['page'] for r in events}=={'f10r','f11r','f55v','f56r','f81v','f82r','f83r'},
        'seal_absent':all(not r['page'].lower().startswith('f84') for r in events),
    }
    result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'FIVE_HUNDRED_SEVENTIETH_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for k,v in checks.items():print(f"{k}\t{'PASS' if v else 'FAIL'}")
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
