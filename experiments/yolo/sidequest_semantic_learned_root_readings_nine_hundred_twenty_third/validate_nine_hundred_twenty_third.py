#!/usr/bin/env python3
import csv,json,subprocess,sys
from pathlib import Path
O=Path(__file__).resolve().parent
def r(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 o=r('PASS923_141_ROOT_OCCURRENCES.tsv');d=r('PASS923_10_LEARNED_ROOT_DECISIONS.tsv');s=json.loads((O/'PASS923_BUILD_SUMMARY.json').read_text());q=[]
 def a(n,x,z):q.append({'name':n,'pass':bool(x),'detail':z})
 a('occurrences_141',len(o)==141,len(o));a('event_unique',len({x['event_id'] for x in o})==141,len({x['event_id'] for x in o}));a('roots_10',len(d)==10,len(d));a('roots_unique',len({x['root'] for x in d})==10,len({x['root'] for x in d}));a('three_revisions',sum(x['decision'].startswith('REVISE') for x in d)==3,[x['root'] for x in d if x['decision'].startswith('REVISE')]);a('all_contexts',all(x['complete_context_de'] for x in o),len(o));a('all_expansions',all(x['register_expansion_de'] for x in o),len(o))
 names=['PASS923_141_ROOT_OCCURRENCES.tsv','PASS923_10_LEARNED_ROOT_DECISIONS.tsv','PASS923_COMPLETE_ROOT_CONTEXTS.md','PASS923_REPORT.md'];text='\n'.join((O/n).read_text(errors='ignore') for n in names);a('sealed_absent','f84' not in text.lower(),'sealed')
 before=s['sha256'];subprocess.run([sys.executable,str(O/'build_nine_hundred_twenty_third.py')],check=True);after=json.loads((O/'PASS923_BUILD_SUMMARY.json').read_text())['sha256'];a('deterministic',before==after,len(after))
 z={'status':'PASS' if all(x['pass'] for x in q) else 'FAIL','checks_passed':sum(x['pass'] for x in q),'checks_total':len(q),'checks':q};(O/'PASS923_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z));raise SystemExit(0 if z['status']=='PASS' else 1)
if __name__=='__main__':main()
