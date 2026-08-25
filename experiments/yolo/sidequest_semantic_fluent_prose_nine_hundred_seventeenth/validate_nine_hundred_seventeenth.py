#!/usr/bin/env python3
import csv, json, subprocess, sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
def rows(n):
    with (OUT/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
    i=rows('PASS917_1435_FLUENT_INSTRUCTIONS.tsv'); e=rows('PASS917_2010_EVENT_BINDINGS.tsv'); c=rows('PASS917_354_FLUENT_CLAUSES.tsv')
    s=json.loads((OUT/'PASS917_BUILD_SUMMARY.json').read_text()); checks=[]
    def add(n,x,d):checks.append({'name':n,'pass':bool(x),'detail':d})
    add('events_2010',len(e)==2010,len(e));add('event_unique',len({r['event_id'] for r in e})==2010,len({r['event_id'] for r in e}))
    add('instructions_1435',len(i)==1435,len(i));add('instruction_unique',len({r['instruction_id'] for r in i})==1435,len({r['instruction_id'] for r in i}))
    add('clauses_354',len(c)==354,len(c));add('event_sum',sum(int(r['event_count']) for r in i)==2010,sum(int(r['event_count']) for r in i))
    add('multi_387',s['multi_event_instructions']==387,s['multi_event_instructions']);add('max_10',s['max_events_per_instruction']==10,s['max_events_per_instruction'])
    add('pages_12',len(s['pages'])==12,s['pages']);add('all_fluent',all(r['fluent_workshop_de'] for r in i),len(i))
    add('all_clause_fluent',all(r['fluent_clause_de'] for r in c),len(c));add('no_unknown',all('UNKNOWN' not in r['fluent_workshop_de'] for r in i),'none')
    names=['PASS917_1435_FLUENT_INSTRUCTIONS.tsv','PASS917_2010_EVENT_BINDINGS.tsv','PASS917_354_FLUENT_CLAUSES.tsv','PASS917_TWELVE_PAGE_FLUENT_EDITION.md','PASS917_REPORT.md']
    text='\n'.join((OUT/n).read_text(encoding='utf-8',errors='ignore') for n in names)
    add('sealed_absent','f84' not in text.lower(),'sealed')
    before=s['sha256'];subprocess.run([sys.executable,str(OUT/'build_nine_hundred_seventeenth.py')],check=True)
    after=json.loads((OUT/'PASS917_BUILD_SUMMARY.json').read_text())['sha256'];add('deterministic',before==after,len(after))
    result={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','checks_passed':sum(x['pass'] for x in checks),'checks_total':len(checks),'checks':checks}
    (OUT/'PASS917_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
