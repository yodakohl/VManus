#!/usr/bin/env python3
import csv,json,subprocess,sys
from collections import Counter
from pathlib import Path
O=Path(__file__).resolve().parent
def r(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 e=r('PASS924_2511_CURRENT_EVENT_LEDGER.tsv');d=r('PASS924_1384_CURRENT_CARD_DICTIONARY.tsv');l=r('PASS924_464_CURRENT_LOCUS_EDITION.tsv');i=r('PASS924_1435_CURRENT_PROSE_INSTRUCTIONS.tsv');c=r('PASS924_354_CURRENT_CLAUSES.tsv');co=r('PASS924_56_CURRENT_COMPONENTS.tsv');v=r('PASS924_17_CURRENT_VERBS.tsv');p=r('PASS924_44_CURRENT_PHRASES.tsv');s=json.loads((O/'PASS924_BUILD_SUMMARY.json').read_text());q=[]
 def a(n,x,z):q.append({'name':n,'pass':bool(x),'detail':z})
 for n,x,k in [('events',e,2511),('dictionary',d,1384),('loci',l,464),('instructions',i,1435),('clauses',c,354),('components',co,56),('verbs',v,17),('phrases',p,44)]:a(n+'_'+str(k),len(x)==k,len(x))
 a('event_unique',len({x['event_id'] for x in e})==2511,len({x['event_id'] for x in e}));a('dict_unique',len({x['dictionary_entry_id'] for x in d})==1384,len({x['dictionary_entry_id'] for x in d}));a('locus_sum',sum(int(x['events']) for x in l)==2511,sum(int(x['events']) for x in l));a('channels',Counter(x['current_channel'] for x in e)==Counter({'WORKSHOP_PROSE':2010,'OWNER_ADDRESS_OR_DIAGRAM':501}),Counter(x['current_channel'] for x in e));a('pages_14_15',s['physical_pages']==14 and s['source_pages']==15,(s['physical_pages'],s['source_pages']))
 a('revisions_propagated',all('rückführ' not in x['current_reading_de'].lower() and 'stoffteil' not in x['current_reading_de'].lower() and 'pressen' not in x['current_reading_de'].lower() for x in e),'clean')
 names=['PASS924_2511_CURRENT_EVENT_LEDGER.tsv','PASS924_1384_CURRENT_CARD_DICTIONARY.tsv','PASS924_464_CURRENT_LOCUS_EDITION.tsv','PASS924_1435_CURRENT_PROSE_INSTRUCTIONS.tsv','PASS924_354_CURRENT_CLAUSES.tsv','PASS924_56_CURRENT_COMPONENTS.tsv','PASS924_17_CURRENT_VERBS.tsv','PASS924_44_CURRENT_PHRASES.tsv','PASS924_FOURTEEN_PAGE_CURRENT_EDITION.md','PASS924_COMPACT_SCRIBAL_HANDBOOK.md','PASS924_REPORT.md'];text='\n'.join((O/n).read_text(errors='ignore') for n in names);a('sealed_absent','f84' not in text.lower(),'sealed')
 before=s['sha256'];subprocess.run([sys.executable,str(O/'build_nine_hundred_twenty_fourth.py')],check=True);after=json.loads((O/'PASS924_BUILD_SUMMARY.json').read_text())['sha256'];a('deterministic',before==after,len(after))
 z={'status':'PASS' if all(x['pass'] for x in q) else 'FAIL','checks_passed':sum(x['pass'] for x in q),'checks_total':len(q),'checks':q};(O/'PASS924_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z));raise SystemExit(0 if z['status']=='PASS' else 1)
if __name__=='__main__':main()
