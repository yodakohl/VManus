#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/'experiments/yolo/gdt377_local_head_signature_transfer';ART=BASE/'artifacts'
def rows(p):
 with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 f=json.loads((ART/'gdt377_comparator_model_freeze.json').read_text());r=json.loads((ART/'gdt377_result.json').read_text());e=rows(ART/'gdt377_event_scores.tsv');a=rows(ART/'gdt377_tuple_candidate_atlas.tsv');n=rows(ART/'gdt377_null.tsv');passed=[x for x in a if x['candidate_gate']=='PASS']
 powered=[x for x in a if int(x['events'])>=12 and int(x['physical_folios'])>=3]
 checks={'freeze':f['status']=='FROZEN_BEFORE_VOYNICH_SCORE','endpoint':f['endpoint']=='PREDICATE_HEAD_WITH_DEPENDENTS','events':len(e)==8448,'tuples':len(a)==1676,'records':r['records']==288,'powered':len(powered)==111,'powered_positive_delta':sum(float(x['mean_structure_minus_nuisance'])>=0 for x in powered)==102,'powered_absolute_fail':not any(float(x['mean_signature_probability'])>=.5 for x in powered),'powered_folio_fail':not any(float(x['folio_fraction_mean_ge_0_5'])>=.75 for x in powered),'no_f84':not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in e),'scores':all(0<=float(x['nuisance_probability'])<=1 and 0<=float(x['cmp_local_head_signature_probability'])<=1 for x in e),'unassigned':all(x['semantic_state']=='UNASSIGNED' for x in e+a),'candidate_count':len(passed)==r['candidate_tuples']==0,'candidate_gate':all(int(x['events'])>=12 and int(x['physical_folios'])>=3 and float(x['mean_signature_probability'])>=.5 and float(x['folio_fraction_mean_ge_0_5'])>=.75 and float(x['mean_structure_minus_nuisance'])>=0 for x in passed),'null':len(n)==1 and int(n[0]['null_worlds'])==4096 and abs(float(n[0]['inclusive_p'])-.003417134489)<1e-12,'f84_flags':not any(r['f84'].values()),'hashes':all(sha(ROOT/p)==v for p,v in r['outputs'].items())}
 c=dict(r);expected=c.pop('content_hash');checks['content_hash']=hashlib.sha256(json.dumps(c,sort_keys=True,separators=(',',':')).encode()).hexdigest()==expected
 out={'schema':'GDT377_VALIDATION_V1','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'checks_passed':sum(checks.values()),'checks_total':len(checks),'result_sha256':sha(ART/'gdt377_result.json')};(ART/'gdt377_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],f"{out['checks_passed']}/{out['checks_total']}")
 if out['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
