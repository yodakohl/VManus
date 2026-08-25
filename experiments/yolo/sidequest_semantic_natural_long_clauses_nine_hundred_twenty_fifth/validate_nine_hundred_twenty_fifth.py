#!/usr/bin/env python3
import csv,json,subprocess,sys
from pathlib import Path
O=Path(__file__).resolve().parent
def r(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 c=r('PASS925_30_NATURAL_CLAUSES.tsv');p=r('PASS925_PHASES.tsv');e=r('PASS925_856_EVENT_BINDINGS.tsv');s=json.loads((O/'PASS925_BUILD_SUMMARY.json').read_text());q=[]
 def a(n,x,z):q.append({'name':n,'pass':bool(x),'detail':z})
 a('clauses_30',len(c)==30,len(c));a('events_856',len(e)==856,len(e));a('events_unique',len({x['event_id'] for x in e})==856,len({x['event_id'] for x in e}));a('phases',len(p)==s['phases'],len(p));a('phase_unique',len({x['phase_id'] for x in p})==len(p),len(p));a('all_natural',all(x['natural_paragraph_de'] for x in c),len(c));a('binding_clauses',set(x['clause_id'] for x in e)==set(x['clause_id'] for x in c),len(set(x['clause_id'] for x in e)))
 names=['PASS925_30_NATURAL_CLAUSES.tsv','PASS925_PHASES.tsv','PASS925_856_EVENT_BINDINGS.tsv','PASS925_NATURAL_LONG_CLAUSE_EDITION.md','PASS925_REPORT.md'];text='\n'.join((O/n).read_text(errors='ignore') for n in names);a('sealed_absent','f84' not in text.lower(),'sealed')
 before=s['sha256'];subprocess.run([sys.executable,str(O/'build_nine_hundred_twenty_fifth.py')],check=True);after=json.loads((O/'PASS925_BUILD_SUMMARY.json').read_text())['sha256'];a('deterministic',before==after,len(after))
 z={'status':'PASS' if all(x['pass'] for x in q) else 'FAIL','checks_passed':sum(x['pass'] for x in q),'checks_total':len(q),'checks':q};(O/'PASS925_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z));raise SystemExit(0 if z['status']=='PASS' else 1)
if __name__=='__main__':main()
