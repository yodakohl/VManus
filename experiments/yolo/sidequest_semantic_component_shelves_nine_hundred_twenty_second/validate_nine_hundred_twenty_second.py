#!/usr/bin/env python3
import csv,json,subprocess,sys
from collections import Counter
from pathlib import Path
O=Path(__file__).resolve().parent
def r(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 x=r('PASS922_56_COMPONENT_SHELVES.tsv');s=json.loads((O/'PASS922_BUILD_SUMMARY.json').read_text());q=[];c=Counter(z['shelf'] for z in x)
 def a(n,v,d):q.append({'name':n,'pass':bool(v),'detail':d})
 a('components_56',len(x)==56,len(x));a('unique',len({z['component'] for z in x})==56,len({z['component'] for z in x}));a('productive_30',c['PRODUCTIVE_CONTRAST_CORE']==30,c);a('learned_10',c['LEARNED_WORKSHOP_ROOT']==10,c);a('address_5',c['FORMAL_ADDRESS_SIGN']==5,c);a('local_11',c['LOCAL_WRITING_SIGN']==11,c);a('all_defaults',all(z['fixed_default_de'] for z in x),len(x))
 names=['PASS922_56_COMPONENT_SHELVES.tsv','PASS922_10_LEARNED_ROOTS.tsv','PASS922_30_PRODUCTIVE_CORES.tsv','PASS922_16_ADDRESS_AND_LOCAL_SIGNS.tsv','PASS922_REPORT.md'];text='\n'.join((O/n).read_text(errors='ignore') for n in names);a('sealed_absent','f84' not in text.lower(),'sealed')
 before=s['sha256'];subprocess.run([sys.executable,str(O/'build_nine_hundred_twenty_second.py')],check=True);after=json.loads((O/'PASS922_BUILD_SUMMARY.json').read_text())['sha256'];a('deterministic',before==after,len(after))
 z={'status':'PASS' if all(v['pass'] for v in q) else 'FAIL','checks_passed':sum(v['pass'] for v in q),'checks_total':len(q),'checks':q};(O/'PASS922_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z));raise SystemExit(0 if z['status']=='PASS' else 1)
if __name__=='__main__':main()
