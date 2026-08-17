#!/usr/bin/env python3
"""Independent source reconstruction for GDT223 target result."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;RES=R/'gdt223_result.json';OUT=R/'gdt223_validation.json'
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def jac(a,b):return len(a&b)/len(a|b) if a|b else 0
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)});assert v,n
r=json.loads(RES.read_text());saved=r.pop('result_content_sha256');ck('content_hash',saved==csha(r));r['result_content_sha256']=saved
ck('status',r['status']=='MODULE_SET_DIRECTION_HIT_AR_LOCAL_ADDRESS_TRANSFER_FAILED')
for n,h in r['inputs'].items():ck('input_'+n,sha(R/n)==h)
for n,h in r['outputs'].items():ck('output_'+n,sha(R/n)==h)
for n,h in r['documents'].items():ck('document_'+n,sha(R/n)==h)
for n,h in r['implementation'].items():ck('implementation_'+n,sha(R/n)==h)
mods=r['modules'];man=read(R/'gdt223_f82v_assembly_prediction.tsv');ll={x for z in man for x in z['label_loci'].split(',')};pl={x for z in man for x in z['prose_loci'].split(',')}
L=defaultdict(list);P=defaultdict(list);cnt={};labels_no_f84=True
with (R/'gdt012_annotated_core_inventory.tsv').open() as h:
 for z in csv.DictReader(h,delimiter='\t'):
  labels_no_f84=labels_no_f84 and not z['page'].startswith('f84')
  if z['locus'] in ll:L[z['locus']].append(z['token'])
ck('label_source_no_f84',labels_no_f84)
with (R/'gdt016_group_state_inventory.tsv').open() as h:
 for z in csv.DictReader(h,delimiter='\t'):
  if z['page'].startswith('f84'):continue
  if z['locus'] in pl:P[z['locus']].append(z['token']);cnt[z['locus']]=int(z['group_count'])
ck('target_coverage',set(L)==ll and set(P)==pl and all(len(P[x])==cnt[x] for x in pl))
sets={}
for z in man:
 side=z['assembly'][0];lt=[t for l in z['label_loci'].split(',') for t in L[l]];pt=[t for l in z['prose_loci'].split(',') for t in P[l]]
 sets['L'+side]={m for m in mods if any(m in t for t in lt)};sets['P'+side]={m for m in mods if any(m in t for t in pt)}
lead=jac(sets['LT'],sets['PT'])+jac(sets['LB'],sets['PB'])-jac(sets['LT'],sets['PB'])-jac(sets['LB'],sets['PT'])
ck('lead',abs(lead-r['prediction_results']['assignment_lead'])<1e-12 and lead>0)
def mhit(m):
 a=(m in sets['LT'],m in sets['LB']);b=(m in sets['PT'],m in sets['PB']);return a[0]!=a[1] and b[0]!=b[1] and a==b
ck('ar_fail',not mhit('ar') and not r['prediction_results']['ar_discriminates_exactly_one_matching_side'])
ck('dal_postreveal',mhit('dal') and r['prediction_results']['postreveal_dal_discriminates_exactly_one_matching_side'])
ck('dal_only',sum(mhit(m) for m in mods)==1)
ck('freeze_commit',r['freeze_commit']=='dc266ccfdb70e2cb7ba7c8bb681c1c6727f27fc8')
ck('claim_ceiling','translation' not in r['interpretation'].lower() and 'plaintext' not in r['interpretation'].lower())
ck('f84_flags',not any(r['f84'].values()))
v={'schema':'GDT223_TARGET_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'checks':checks,'result_sha256':sha(RES),'validator_sha256':sha(Path(__file__))};v['validation_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(f"PASS {len(checks)}/{len(checks)}")
