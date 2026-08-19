#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/'experiments/yolo/gdt376_corema_hidden_function_oracle';ART=BASE/'artifacts'
def rows(p):
 with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 d=json.loads((ART/'gdt376_design_freeze.json').read_text());r=json.loads((ART/'gdt376_result.json').read_text());o=rows(ART/'gdt376_observation_layer.tsv');s=rows(ART/'gdt376_oracle_endpoint_summary.tsv');f=rows(ART/'gdt376_fold_scores.tsv');t=rows(ART/'gdt376_transfer_gate.tsv')
 forbidden={'role','annotation_flags','parent_instruction_ordinal','concept_id','editor_english_label'}
 checks={
 'design':d['status']=='FROZEN_BEFORE_HELD_ORACLE_EVALUATION','rows':len(o)==27568,'observable':sum(x['observable_surface']=='1' for x in o)==27349,
 'observation_blind':not(forbidden&set(o[0])),'collections':sorted({x['collection_id'] for x in o})==['b4','b6','br1','bs1','gr1','w1'],
 'summary':len(s)==11,'folds':len(f)==11*6*5,'transfer':len(t)==15,'unassigned':all(x['semantic_gloss']=='UNASSIGNED' for x in t),
 'promotion_exact':set(r['promoted_endpoints'])=={x['target'] for x in s if x['promoted']=='YES'},'transfer_exact':set(r['transferable_families'])=={x['hypothesis_family'] for x in t if x['transfer_to_voynich']=='YES'},
 'no_voynich':not r['voynich_scored'],'f84':not r['f84_accessed'],'hashes':all(sha(ROOT/p)==v for p,v in r['outputs'].items()),
 }
 c=dict(r);expected=c.pop('content_hash');checks['content_hash']=hashlib.sha256(json.dumps(c,sort_keys=True,separators=(',',':')).encode()).hexdigest()==expected
 out={'schema':'GDT376_VALIDATION_V1','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'checks_passed':sum(checks.values()),'checks_total':len(checks),'result_sha256':sha(ART/'gdt376_result.json')}
 (ART/'gdt376_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],f"{out['checks_passed']}/{out['checks_total']}")
 if out['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
