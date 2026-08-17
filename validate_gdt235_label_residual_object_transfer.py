#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(n):
 with (ROOT/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def main():
 r=json.loads((ROOT/'gdt235_result.json').read_text());i=read('gdt235_label_object_inventory.tsv');s=read('gdt235_object_transfer_summary.tsv');c=[]
 c += [('rows703',len(i)==r['inventory_rows']==703),('folios23',len({x['physical_folio'] for x in i})==r['folios']==23),('summary6',len(s)==6),('no_f84',all(not x['page'].startswith('f84') for x in i)),('no_gloss',all(x['claim_state']=='COARSE_VISIBLE_OBJECT_ENDPOINT_NO_GLOSS' for x in i))]
 hf=r['held_folio'];c += [('raw_delta',abs(hf['RAW_FAMILY']['accuracy_delta']-(-0.234726688103))<1e-12),('residual_delta',abs(hf['STRICT_RESIDUAL']['accuracy_delta']-(-0.238390092879))<1e-12),('prefix_delta',abs(hf['TRANSFERRED_PREFIX']['accuracy_delta']-(-0.204778156997))<1e-12),('q13_all_zero',all(x['feature_correct']==0 for x in r['q13_held_section'].values()))]
 for kind in ('inputs','outputs','documents','implementation'):
  for n,d in r[kind].items():c.append((f'hash:{n}',sha(n)==d))
 clean=dict(r);stored=clean.pop('content_hash');c.append(('content_hash',stored==hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
 c += [(f'f84_{k}_false',v is False) for k,v in r['f84'].items()]
 failed=[n for n,ok in c if not ok];o={'experiment':r['experiment'],'status':'PASS' if not failed else 'FAIL','checks_passed':sum(ok for _,ok in c),'checks_total':len(c),'failed':failed,'result_sha256':sha('gdt235_result.json')};(ROOT/'gdt235_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
 if failed:raise SystemExit('FAIL '+','.join(failed))
 print(f"PASS {o['checks_passed']}/{o['checks_total']}")
if __name__=='__main__':main()
