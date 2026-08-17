#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(n):
 with (ROOT/n).open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def main():
 r=json.loads((ROOT/'gdt233_result.json').read_text());p=read('gdt233_prefix_manifest.tsv');q=read('gdt233_q13_label_predictions.tsv');c=[]
 strict=[x for x in p if x['selection_status']=='STRICT_TRAINING_SELECTED'];tp=sum(x['predicted_label']=='1' and x['true_label']=='1' for x in q);fp=sum(x['predicted_label']=='1' and x['true_label']=='0' for x in q);fn=sum(x['predicted_label']=='0' and x['true_label']=='1' for x in q);tn=sum(x['predicted_label']=='0' and x['true_label']=='0' for x in q)
 c += [('prefixes14',len(strict)==r['strict_prefixes']==14),('q13_646',len(q)==r['q13_loci']==646),('q13_labels98',sum(x['true_label']=='1' for x in q)==98),('confusion',(tp,fp,fn,tn)==(34,12,64,536)),('baca_not_strict',r['baca_training']['strict_selected'] is False),('baca_q13_5',r['baca_q13']['occurrences']==r['baca_q13']['labels']==5),('no_f84',all(not x['page'].startswith('f84') for x in q)),('no_gloss',all(x['claim_state']=='TRANSFERRED_REGISTER_DECOMPOSITION_NO_GLOSS' for x in q))]
 for kind in ('inputs','outputs','documents','implementation'):
  for n,d in r[kind].items():c.append((f'hash:{n}',sha(n)==d))
 clean=dict(r);stored=clean.pop('content_hash');c.append(('content_hash',stored==hashlib.sha256(json.dumps(clean,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
 c += [(f'f84_{k}_false',v is False) for k,v in r['f84'].items()]
 failed=[n for n,ok in c if not ok];o={'experiment':r['experiment'],'status':'PASS' if not failed else 'FAIL','checks_passed':sum(ok for _,ok in c),'checks_total':len(c),'failed':failed,'result_sha256':sha('gdt233_result.json')};(ROOT/'gdt233_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
 if failed:raise SystemExit('FAIL '+','.join(failed))
 print(f"PASS {o['checks_passed']}/{o['checks_total']}")
if __name__=='__main__':main()
