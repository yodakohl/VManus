#!/usr/bin/env python3
import csv,json,subprocess,sys
from pathlib import Path
O=Path(__file__).resolve().parent
def r(n):
 with (O/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 e=r('PASS919_863_EVENT_SECOND_READING.tsv');l=r('PASS919_144_LOCUS_SECOND_READING.tsv');s=json.loads((O/'PASS919_BUILD_SUMMARY.json').read_text());q=[]
 def a(n,x,z):q.append({'name':n,'pass':bool(x),'detail':z})
 a('events_863',len(e)==863,len(e));a('event_unique',len({x['event_id'] for x in e})==863,len({x['event_id'] for x in e}));a('loci_144',len(l)==144,len(l));a('locus_event_sum',sum(int(x['events']) for x in l)==863,sum(int(x['events']) for x in l))
 a('prose_619',s['channels'].get('WORKSHOP_PROSE')==619,s['channels']);a('labels_244',s['channels'].get('OWNER_ADDRESS_LABEL')==244,s['channels']);a('pages',s['pages']=={'f13r':77,'f75r':418,'f70v1':86,'f70v2':132,'f88r':150},s['pages'])
 a('all_read',all(x['second_reading_de'] for x in e),len(e));a('ring_recast',all(x['transfer_decision']=='RING_TEXT_RECAST_AS_ADDRESS' for x in e if x['usage_class']=='RING_TEXT'),sum(x['usage_class']=='RING_TEXT' for x in e))
 names=['PASS919_863_EVENT_SECOND_READING.tsv','PASS919_144_LOCUS_SECOND_READING.tsv','PASS919_FOUR_PAGE_COMPLETE_EDITION.md','PASS919_REPORT.md'];text='\n'.join((O/n).read_text(errors='ignore') for n in names);a('sealed_absent','f84' not in text.lower(),'sealed')
 before=s['sha256'];subprocess.run([sys.executable,str(O/'build_nine_hundred_nineteenth.py')],check=True);after=json.loads((O/'PASS919_BUILD_SUMMARY.json').read_text())['sha256'];a('deterministic',before==after,len(after))
 z={'status':'PASS' if all(x['pass'] for x in q) else 'FAIL','checks_passed':sum(x['pass'] for x in q),'checks_total':len(q),'checks':q};(O/'PASS919_VALIDATION.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z));raise SystemExit(0 if z['status']=='PASS' else 1)
if __name__=='__main__':main()
