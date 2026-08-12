#!/usr/bin/env python3
"""Independent aggregate/null validator for the RTA001 result."""

from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent;R=HERE/'results';P=R/'rta001_result.json';HELD=R/'rta001_heldout_panel_results.tsv';CODE=R/'rta001_operator_codebook.json';ATLAS=R/'rta001_operator_atlas.md';REPORT=R/'rta001_result_report.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def main():
 d=json.loads(P.read_text());checks=[]
 def ck(n,x):checks.append(n);assert x,n
 ck('schema',d['schema_version']=='RTA001_RESULT_V1'); h=rows(HELD);ck('46 panel rows',len(h)==46)
 folios=defaultdict(list)
 for x in h:
  stored=float(x['gain_bits_per_edge']);gain=float(x['baseline_bits_per_edge'])-float(x['operator_bits_per_edge']);ck('row gain',abs(gain-stored)<=1.1e-6);folios[x['physical_folio']].append(stored)
 means={f:sum(v)/len(v) for f,v in folios.items()};ck('nine folios',len(means)==9)
 observed=sum(means.values())/9;ck('primary gain',abs(observed-d['primary']['gain_bits_per_edge'])<2e-6)
 ck('positive folios',sum(v>0 for v in means.values())==d['primary']['positive_folios'])
 null=d['null']['gains_bits_per_edge'];ck('4096 nulls',len(null)==4096 and all(math.isfinite(x) for x in null))
 digest=hashlib.sha256(np.array(null,dtype='<f8').tobytes()).hexdigest();ck('null digest',digest==d['null']['gain_sha256'])
 p=sum(x>=d['primary']['gain_bits_per_edge'] for x in null)/4096;ck('inclusive p',p==d['primary']['inclusive_p_value'])
 ck('null summaries',min(null)==d['null']['minimum'] and max(null)==d['null']['maximum'] and float(np.median(null))==d['null']['median'])
 robust={'positive_folios_at_least_7_of_9':sum(v>0 for v in means.values())>=7,'operator_recurs_on_3_folios_and_is_used_heldout':d['secondary']['recurring_operator_fold_instances']>0,'abstract_representation_positive_without_exact_identity':any(d['secondary']['representation_mean_gains_bits_per_edge'][r]>0 for r in ('construction','root','family'))}
 ck('robustness',d['robustness']==robust)
 status='PASS' if observed>0 and p<=.01 and all(robust.values()) else 'FAIL';ck('status',d['status']==status);ck('decision',(d['decision']=='NO_TRANSFER_AT_REGISTERED_RESOLUTION')==(status=='FAIL'))
 ck('artifact hashes',d['artifacts']=={HELD.name:sha(HELD),CODE.name:sha(CODE),ATLAS.name:sha(ATLAS)})
 code=json.loads(CODE.read_text());ck('codebook status',code['status']==status and len(code['fold_codebooks'])==9)
 for fold in code['fold_codebooks']:
  ck('operator count',len(fold['operators'])==fold['k'])
  for op in fold['operators']:
   ck('anonymous id',op['operator_id'].startswith('OP'));ck('explicit DSL',bool(op['dsl_program']));ck('support',op['training_support']>=1)
 report=REPORT.read_text();ck('report primary',f"{d['primary']['gain_bits_per_edge']:.6f}" in report and f"{p:.6f}" in report);ck('atlas ceiling','no meaning' in ATLAS.read_text())
 print(json.dumps({'status':'PASS','checks':len(checks),'result_sha256':sha(P),'heldout_sha256':sha(HELD)},sort_keys=True))
if __name__=='__main__':main()
