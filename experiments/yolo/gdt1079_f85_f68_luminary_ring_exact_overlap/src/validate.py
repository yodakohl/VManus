#!/usr/bin/env python3
"""Independent source-to-result audit for GDT1079."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
D = Path(__file__).resolve().parents[1]
result = json.loads((D/'artifacts/RESULT.json').read_text())
source85 = ROOT/'experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv'
source68 = ROOT/'research_registry/proposals/laufenberg_f85r2_20260926/F68R_PAIRED_OPENINGS_SOURCE_20260927.json'
for name, wanted in result['source_hashes'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == wanted
with source85.open(newline='') as f:
    r85 = list(csv.DictReader(f,delimiter='\t'))
r68 = next(q['rows'] for q in json.loads(source68.read_text())['queries'] if q['id']=='groups')
assert {r['locus'] for r in r68} == {'f68r2.6','f68r2.31'}
assert all(not r['locus'].startswith('f84') for r in r85+r68)
errors=[]
counts={}
for ed in ('ZL3b','IT2a','RF1b'):
    expected={}
    for loc,src in [('f85r2.24',r85),('f68r2.31',r68),('f68r2.6',r68)]:
        source=[r for r in src if r['edition']==ed and r['locus']==loc]
        observed=result['rings'][ed][loc]
        src_tuples=sorted((int(r['source_group_index']),r['ivtff_group_raw'],r['left_separator'],r['right_separator']) for r in source)
        res_tuples=sorted((int(r['source_group_index']),r['ivtff_group_raw'],r['left_separator'],r['right_separator']) for r in observed)
        if src_tuples!=res_tuples: errors.append(ed+' '+loc+' incomplete source rows')
        expected[loc]=set(r['ivtff_group_raw'] for r in source)
        counts[ed+' '+loc]=len(source)
    for other,key in [('f68r2.31','sun'),('f68r2.6','moon')]:
        overlap=expected['f85r2.24'] & expected[other]
        shown=set(result['intersections'][ed][key+'_eligible']) | set(result['intersections'][ed][key+'_raw_ineligible'])
        if overlap!=shown: errors.append(ed+' '+key+' incomplete intersection')
        if overlap: errors.append(ed+' '+key+' expected zero raw overlap; inspect manually')
if result['rare_sun_only'] or result['status']!='NO_RARE_SUN_ONLY_EXACT_BRIDGE':
    errors.append('gate mismatch')
validation={'status':'PASS' if not errors else 'FAIL','errors':errors,'raw_intersection_recomputed':'zero in all six reader/pair cells','ring_group_counts':counts,'limits':'Checks source completeness and zero raw overlap; not image identity, probability, or meaning.'}
(D/'artifacts/VALIDATION.json').write_text(json.dumps(validation,indent=2,sort_keys=True)+'\n')
print(validation['status'])
if errors: raise SystemExit(1)
