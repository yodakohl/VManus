#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'experiments/yolo/gdt375_comparator_derived_functional_roadmap'
ART=BASE/'artifacts'
def rows(p):
    with p.open(encoding='utf-8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    r=json.loads((ART/'gdt375_result.json').read_text()); reg=rows(ART/'gdt375_ranked_hypothesis_registry.tsv'); x=rows(ART/'gdt375_gdt373_crosswalk.tsv'); d=rows(ART/'gdt375_detector_contract.tsv')
    names=[z['hypothesis_family'] for z in reg]; required={
      'STATE_TRANSITION_FINGERPRINTS','LOCAL_VALENCY_PREDICATE_HEAD','REF_ANAPHORA_ELLIPSIS_RECOVERY','LONG_DISTANCE_CORRELATIVE_PAIRS','NEXT_RESUME_LOCAL_RESET','UNTIL_STATE_GATING','AND_VARIABLE_ARITY_CHAINS','OR_BRANCH_RECONVERGENCE','POLARITY_NEGATION_INVERSE_TRANSITION','COMPOSITIONAL_POINTER_RELATION_PARADIGMS','EXCLUDE_WITHOUT','LIKE_AS_SAME_COMPARISON','FUNCTION_WORD_INFORMATION_BOTTLENECK','SCOPE_LENGTH_HORIZON','LATENT_PROCEDURAL_AUTOMATON'}
    checks={
      'status':r['status']=='COMPARATOR_DERIVED_FUNCTIONAL_FAMILIES_REGISTERED_BEFORE_ORACLE_EVALUATION',
      'counts':(len(reg),len(x),len(d))==(37,15,15),
      'unique':len(names)==len(set(names)),
      'required':required==set(z['new_family'] for z in x)==set(z['hypothesis_family'] for z in d),
      'priorities':[int(z['priority']) for z in reg]==list(range(1,38)),
      'distinct':all(z['distinct_family']=='YES' for z in x),
      'blind':not r['oracle_values_evaluated'] and not r['voynich_scored'],
      'f84':not r['f84_accessed'],
      'hashes':all(sha(ROOT/p)==v for p,v in r['outputs'].items()),
    }
    c=dict(r); expected=c.pop('content_hash'); checks['content_hash']=hashlib.sha256(json.dumps(c,sort_keys=True,separators=(',',':')).encode()).hexdigest()==expected
    out={'schema':'GDT375_VALIDATION_V1','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'checks_passed':sum(checks.values()),'checks_total':len(checks),'result_sha256':sha(ART/'gdt375_result.json')}
    (ART/'gdt375_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status'],f"{out['checks_passed']}/{out['checks_total']}")
    if out['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
