#!/usr/bin/env python3
import csv,json,subprocess,sys
from pathlib import Path
O=Path(__file__).resolve().parent
def r(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 d=r('PASS918_17_VERB_DECK.tsv');i=r('PASS918_1435_REVISED_INSTRUCTIONS.tsv');c=r('PASS918_354_REVISED_CLAUSES.tsv');s=json.loads((O/'PASS918_BUILD_SUMMARY.json').read_text());q=[]
 def a(n,x,z):q.append({'name':n,'pass':bool(x),'detail':z})
 a('verbs_17',len(d)==17,len(d));a('unique_stems',len({x['stem'] for x in d})==17,len({x['stem'] for x in d}));a('unique_defaults',len({x['fixed_verb_de'] for x in d})==17,len({x['fixed_verb_de'] for x in d}))
 a('instructions_1435',len(i)==1435,len(i));a('clauses_354',len(c)==354,len(c));a('all_instruction_readings',all(x['revised_fluent_de'] for x in i),len(i));a('all_clause_readings',all(x['revised_fluent_clause_de'] for x in c),len(c))
 a('no_old_bearbeiten_pruefen',all('bearbeiten oder markieren' not in x['revised_fluent_de'] and 'prüfen oder' not in x['revised_fluent_de'] for x in i),'clean')
 names=['PASS918_17_VERB_DECK.tsv','PASS918_1435_REVISED_INSTRUCTIONS.tsv','PASS918_354_REVISED_CLAUSES.tsv','PASS918_TWELVE_PAGE_REVISED_EDITION.md','PASS918_REPORT.md'];text='\n'.join((O/n).read_text(errors='ignore') for n in names);a('sealed_absent','f84' not in text.lower(),'sealed')
 before=s['sha256'];subprocess.run([sys.executable,str(O/'build_nine_hundred_eighteenth.py')],check=True);after=json.loads((O/'PASS918_BUILD_SUMMARY.json').read_text())['sha256'];a('deterministic',before==after,len(after))
 z={'status':'PASS' if all(x['pass'] for x in q) else 'FAIL','checks_passed':sum(x['pass'] for x in q),'checks_total':len(q),'checks':q};(O/'PASS918_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z));raise SystemExit(0 if z['status']=='PASS' else 1)
if __name__=='__main__':main()
