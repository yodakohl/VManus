#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(n):
 with (ROOT/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def main():
 r=json.loads((ROOT/'gdt232_result.json').read_text());census=read('gdt232_baca_occurrence_census.tsv');checks=[]
 checks += [('census19',len(census)==r['baca_occurrences']==19),('labels12',sum(x['kind']=='L' for x in census)==r['baca_labels']==12),('q13_5of5',r['q13_baca']=={'occurrences':5,'labels':5}),('pharma_5of6',r['pharma_baca']=={'occurrences':6,'labels':5}),('no_f84',all(not x['page'].startswith('f84') for x in census)),('all_baca',all(x['family_surface'].startswith('BACA') for x in census))]
 for kind in ('inputs','outputs','documents','implementation'):
  for n,d in r[kind].items():checks.append((f'hash:{n}',sha(n)==d))
 clean=dict(r);stored=clean.pop('content_hash');checks.append(('content_hash',stored==hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
 checks += [(f'f84_{k}_false',v is False) for k,v in r['f84'].items()]
 failed=[n for n,ok in checks if not ok];o={'experiment':r['experiment'],'status':'PASS' if not failed else 'FAIL','checks_passed':sum(ok for _,ok in checks),'checks_total':len(checks),'failed':failed,'result_sha256':sha('gdt232_result.json')};(ROOT/'gdt232_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
 if failed:raise SystemExit('FAIL '+','.join(failed))
 print(f"PASS {o['checks_passed']}/{o['checks_total']}")
if __name__=='__main__':main()
