#!/usr/bin/env python3
import csv,json,subprocess,sys
from pathlib import Path
O=Path(__file__).resolve().parent
def r(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 c=r('PASS921_3X2X2_ACTION_CUBE.tsv');p=r('PASS921_25_MINIMAL_CONTRASTS.tsv');qg=r('PASS921_19_Q_ALLOGRAPHS.tsv');s=json.loads((O/'PASS921_BUILD_SUMMARY.json').read_text());q=[]
 def a(n,x,z):q.append({'name':n,'pass':bool(x),'detail':z})
 a('cube_12',len(c)==12,len(c));a('observed_11',sum(x['status']=='OBSERVED' for x in c)==11,sum(x['status']=='OBSERVED' for x in c));a('one_prediction',sum(x['status']=='PREDICTED_MISSING_CARD' for x in c)==1,[x['component_recipe'] for x in c if x['status']!='OBSERVED']);a('prediction_chekedy',next(x['preferred_surface'] for x in c if x['status']!='OBSERVED')=='chekedy','chekedy')
 a('contrasts_25',len(p)==25,len(p));a('all_contrasts_observed',all(x['both_observed']=='YES' for x in p),sum(x['both_observed']=='YES' for x in p));a('q_19',len(qg)==19,len(qg));a('q_no_meaning_change',all(x['meaning_change']=='NONE' for x in qg),len(qg))
 names=['PASS921_3X2X2_ACTION_CUBE.tsv','PASS921_25_MINIMAL_CONTRASTS.tsv','PASS921_19_Q_ALLOGRAPHS.tsv','PASS921_PREDICTED_MISSING_CARD.md','PASS921_REPORT.md'];text='\n'.join((O/n).read_text(errors='ignore') for n in names);a('sealed_absent','f84' not in text.lower(),'sealed')
 before=s['sha256'];subprocess.run([sys.executable,str(O/'build_nine_hundred_twenty_first.py')],check=True);after=json.loads((O/'PASS921_BUILD_SUMMARY.json').read_text())['sha256'];a('deterministic',before==after,len(after))
 z={'status':'PASS' if all(x['pass'] for x in q) else 'FAIL','checks_passed':sum(x['pass'] for x in q),'checks_total':len(q),'checks':q};(O/'PASS921_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z));raise SystemExit(0 if z['status']=='PASS' else 1)
if __name__=='__main__':main()
