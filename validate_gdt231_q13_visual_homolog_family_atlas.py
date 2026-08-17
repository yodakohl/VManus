#!/usr/bin/env python3
"""Integrity validator for GDT231 outputs."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(n):
 with (ROOT/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def main():
 r=json.loads((ROOT/'gdt231_result.json').read_text());p=read('gdt231_visual_homolog_pair_atlas.tsv');t=read('gdt231_target_tests.tsv');c=[]
 c += [('pairs_391',len(p)==r['pair_rows']==391),('no_f84',all(not x['page'].startswith('f84') for x in p)),('claim_state',all(x['claim_state']=='EXPLORATORY_VISUAL_HOMOLOG_FORMAL_SIMILARITY_NO_GLOSS' for x in p))]
 w=next(x for x in p if {x['locus_a'],x['locus_b']}=={'f82r.35','f82r.38'});c += [('waterfall_families',{w['family_expression_a'],w['family_expression_b']}=={'BACAB','BACACA'}),('waterfall_prefix',int(w['leading_common_family_length'])==4)]
 pool=r['pool_counterexample'];c += [('pool_prefix_zero',pool['leading_common_family_length']==0),('tests_four',len(t)==4)]
 for kind in ('inputs','outputs','documents','implementation'):
  for n,d in r[kind].items():c.append((f'hash:{n}',sha(n)==d))
 clean=dict(r);stored=clean.pop('content_hash');c.append(('content_hash',stored==hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
 c += [(f'f84_{k}_false',v is False) for k,v in r['f84'].items()]
 failed=[n for n,ok in c if not ok];o={'experiment':r['experiment'],'status':'PASS' if not failed else 'FAIL','checks_passed':sum(ok for _,ok in c),'checks_total':len(c),'failed':failed,'result_sha256':sha('gdt231_result.json')};(ROOT/'gdt231_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
 if failed:raise SystemExit('FAIL '+','.join(failed))
 print(f"PASS {o['checks_passed']}/{o['checks_total']}")
if __name__=='__main__':main()
