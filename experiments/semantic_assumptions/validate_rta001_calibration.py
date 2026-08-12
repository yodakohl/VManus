#!/usr/bin/env python3
"""Independent nonimporting validator for RTA001 synthetic calibration."""

from __future__ import annotations
import hashlib,json,math
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent;R=HERE/'results';P=R/'rta001_synthetic_calibration.json';REPORT=R/'rta001_synthetic_calibration_report.md'
REG={'NULL_UNRELATED':32,'TRANSFERRED_K2':8,'TRANSFERRED_K4':8,'TRANSFERRED_K6':8,'TRANSFERRED_K8':8,'LOCAL_ONLY':8,'ONE_PANEL_ONLY':8,'LENGTH_FREQUENCY_CONFOUNDED':8,'TRUE_COMPOSITION':8,'CYCLE_VIOLATION':8,'SYMMETRY_TRANSFERRED':8}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stable(*parts):return int.from_bytes(hashlib.sha256('|'.join(map(str,parts)).encode()).digest()[:8],'little')
def main():
 d=json.loads(P.read_text()); checks=[]
 def ck(n,x):checks.append(n);assert x,n
 ck('schema',d['schema_version']=='RTA001_SYNTHETIC_CALIBRATION_V1')
 ck('registry',d['world_registry']==REG)
 worlds=d['worlds'];ck('world count',len(worlds)==112)
 ck('family counts',Counter(x['family'] for x in worlds)==REG)
 ck('unique family worlds',len({(x['family'],x['world']) for x in worlds})==112)
 for x in worlds:
  ck('seed',x['seed']==stable('RTA001_SYNTHETIC',x['family'],x['world']))
  ck('k',x['selected_k'] in (2,4,6,8))
  ck('recovery finite',math.isfinite(x['assignment_recovery']) and 0<=x['assignment_recovery']<=1)
  ck('gain finite',math.isfinite(x['heldout_gain_bits_per_edge']))
  ck('positive folios range',0<=x['positive_holdout_folios']<=8)
  ck('digest',len(x['model_digest'])==64 and set(x['model_digest'])<=set('0123456789abcdef'))
  cp=x['checkpoint'];ck('checkpoint shape',len(cp['assignments'])==336 and len(cp['assignment_costs_scaled'])==336 and len(cp['medoid_indices'])==x['selected_k'])
  ck('checkpoint seed',cp['restart_seed']>=0 and cp['total_bits_scaled']>=0)
 null=sum(x['heldout_gain_bits_per_edge']>0 for x in worlds if x['family']=='NULL_UNRELATED')
 local=max(x['positive_holdout_folios'] for x in worlds if x['family'] in {'LOCAL_ONLY','ONE_PANEL_ONLY'})
 transfer=sum(x['heldout_gain_bits_per_edge']>0 and x['assignment_recovery']>=.75 for x in worlds if x['family'].startswith('TRANSFERRED_K'))
 true=sum(x['cycle_residual_bits'] for x in worlds if x['family']=='TRUE_COMPOSITION')/8
 bad=sum(x['cycle_residual_bits'] for x in worlds if x['family']=='CYCLE_VIOLATION')/8
 summaries={'null_false_positive_count':null,'max_local_or_one_panel_positive_holdouts':local,'transferred_pass_count':transfer,'true_composition_mean_cycle_residual_bits':true,'cycle_violation_mean_cycle_residual_bits':bad}
 gates={'null_false_positive_at_most_1_of_32':null<=1,'local_or_one_panel_positive_holdouts_at_most_2':local<=2,'transferred_recovery_at_least_28_of_32':transfer>=28,'cycle_residual_strictly_distinguishes_violation':true<bad}
 ck('summary exact',d['summaries']==summaries);ck('gates exact',d['gates']==gates);ck('status exact',d['status']==('PASS' if all(gates.values()) else 'FAIL'))
 bench=d['benchmark'];ck('cpu cuda digest parity',bench['cpu_sha256']==bench['cuda_sha256']);ck('backend threshold',bench['selected_backend']==('CUDA' if bench['cuda_speedup']>=1.25 else 'CPU'))
 for name,digest in d['inputs'].items():
  path=(HERE/name) if (HERE/name).exists() else R/name
  ck('input '+name,path.exists() and sha(path)==digest)
 report=REPORT.read_text();ck('report status',f"Status: **{d['status']}**" in report)
 print(json.dumps({'status':'PASS','checks':len(checks),'calibration_sha256':sha(P),'report_sha256':sha(REPORT)},sort_keys=True))
if __name__=='__main__':main()
