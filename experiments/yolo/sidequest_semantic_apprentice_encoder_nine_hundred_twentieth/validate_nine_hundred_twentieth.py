#!/usr/bin/env python3
import csv,json,subprocess,sys
from pathlib import Path
O=Path(__file__).resolve().parent
def r(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 p=r('PASS920_44_PHRASE_ENCODER.tsv');m=r('PASS920_24_APPRENTICE_MESSAGES.tsv');s=json.loads((O/'PASS920_BUILD_SUMMARY.json').read_text());q=[]
 def a(n,x,z):q.append({'name':n,'pass':bool(x),'detail':z})
 a('phrases_44',len(p)==44,len(p));a('macros_unique',len({x['macro_id'] for x in p})==44,len({x['macro_id'] for x in p}));a('messages_24',len(m)==24,len(m));a('messages_unique',len({x['message_id'] for x in m})==24,len({x['message_id'] for x in m}));a('all_observed',all(x['all_cards_observed']=='YES' for x in m),len(m));a('all_roundtrip',all(x['roundtrip_reading_de'] for x in m),len(m));a('q_pairs',s['q_entry_pairs']==19,s['q_entry_pairs'])
 names=['PASS920_44_PHRASE_ENCODER.tsv','PASS920_24_APPRENTICE_MESSAGES.tsv','PASS920_APPRENTICE_MANUAL.md','PASS920_REPORT.md'];text='\n'.join((O/n).read_text(errors='ignore') for n in names);a('sealed_absent','f84' not in text.lower(),'sealed')
 before=s['sha256'];subprocess.run([sys.executable,str(O/'build_nine_hundred_twentieth.py')],check=True);after=json.loads((O/'PASS920_BUILD_SUMMARY.json').read_text())['sha256'];a('deterministic',before==after,len(after))
 z={'status':'PASS' if all(x['pass'] for x in q) else 'FAIL','checks_passed':sum(x['pass'] for x in q),'checks_total':len(q),'checks':q};(O/'PASS920_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z));raise SystemExit(0 if z['status']=='PASS' else 1)
if __name__=='__main__':main()
