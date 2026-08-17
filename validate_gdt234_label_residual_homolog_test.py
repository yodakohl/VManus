#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(n):
 with (ROOT/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def main():
 r=json.loads((ROOT/'gdt234_result.json').read_text());p=read('gdt234_residual_homolog_pairs.tsv');s=read('gdt234_special_pairs.tsv');c=[]
 changed=[x for x in p if x['prefix_a']!='NONE' or x['prefix_b']!='NONE'];non=[x for x in changed if x['prefix_a']!='NONE' and x['prefix_b']!='NONE' and x['both_residual_nonempty']=='1']
 c += [('pairs391',len(p)==r['pairs']==391),('changed157',len(changed)==r['changed_pairs']==157),('nonempty13',len(non)==r['both_nonempty_pairs']==13),('changed_counts',(r['changed_summary']['improved'],r['changed_summary']['degraded'],r['changed_summary']['unchanged'])==(18,129,10)),('nonempty_counts',(r['nonempty_summary']['improved'],r['nonempty_summary']['degraded'],r['nonempty_summary']['unchanged'])==(2,9,2)),('special4',len(s)==4),('no_f84',all(not x['page'].startswith('f84') for x in p)),('no_gloss',all(x['claim_state']=='REGISTER_RESIDUAL_MECHANISM_DIAGNOSTIC_NO_GLOSS' for x in p))]
 for kind in ('inputs','outputs','documents','implementation'):
  for n,d in r[kind].items():c.append((f'hash:{n}',sha(n)==d))
 clean=dict(r);stored=clean.pop('content_hash');c.append(('content_hash',stored==hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
 c += [(f'f84_{k}_false',v is False) for k,v in r['f84'].items()]
 failed=[n for n,ok in c if not ok];o={'experiment':r['experiment'],'status':'PASS' if not failed else 'FAIL','checks_passed':sum(ok for _,ok in c),'checks_total':len(c),'failed':failed,'result_sha256':sha('gdt234_result.json')};(ROOT/'gdt234_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
 if failed:raise SystemExit('FAIL '+','.join(failed))
 print(f"PASS {o['checks_passed']}/{o['checks_total']}")
if __name__=='__main__':main()
