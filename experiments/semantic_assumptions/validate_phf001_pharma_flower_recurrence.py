#!/usr/bin/env python3
"""Independent compact validation of PHF001 counts and stored stop."""
import csv,json,re,hashlib
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];B=ROOT/'experiments/semantic_assumptions';R=B/'results'
A=R/'existing_human_label_annotations.tsv';X=R/'existing_human_current_locus_crosswalk.tsv';O=R/'pharma_root_color_native_visual_ownership.tsv';RES=R/'phf001_pharma_flower_recurrence.json';REP=R/'phf001_pharma_flower_recurrence_report.md';OUT=R/'phf001_pharma_flower_recurrence_validation.json';REPORT=R/'phf001_pharma_flower_recurrence_validation_report.md'
def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def st(t):
 a=bool(re.search(r'(?<!\w)flower(?!s|\w)',t.lower()));b=bool(re.search(r'(?<!\w)flowers(?!\w)',t.lower()))
 return 'SINGLE_FLOWER' if a and not b else ('MULTIPLE_FLOWERS' if b and not a else None)
def fol(p):return re.match(r'f\d+',p).group()
ann=read(A);x={r['source_record_id']:r for r in read(X)};old=read(O);checks=[]
rows=[(st(r['comments']),r) for r in ann if r['section']=='pharma' and r['certainty']=='UNHEDGED' and r['object_guess'] in {'plant','root'} and st(r['comments'])]
assert Counter(s for s,r in rows)=={'SINGLE_FLOWER':13,'MULTIPLE_FLOWERS':12};checks.append('human_25_partition')
pri=[(s,r) for s,r in rows if x[r['source_record_id']]['primary_eligible']=='1'];assert Counter(s for s,r in pri)=={'SINGLE_FLOWER':10,'MULTIPLE_FLOWERS':8};checks.append('primary_18_partition')
oldclear={r['source_record_id'] for r in old if r['visual_grade']=='CLEAR_ONE_FRAGMENT_ONE_LABEL_CELL'};new={'STOLFI_BEST_1113','STOLFI_BEST_1474'};owned=[(s,r) for s,r in pri if r['source_record_id'] in oldclear|new]
assert Counter(s for s,r in owned)=={'SINGLE_FLOWER':7,'MULTIPLE_FLOWERS':2};checks.append('owned_9_partition')
assert {s:sorted({fol(r['page']) for q,r in owned if q==s}) for s in ('SINGLE_FLOWER','MULTIPLE_FLOWERS')}=={'SINGLE_FLOWER':['f100','f102','f88','f89'],'MULTIPLE_FLOWERS':['f100','f89']};checks.append('owned_folio_support')
clear=oldclear|new;stable=[]
for k in clear:
 z=x[k];v=[z[e].replace(' ','') for e in ('ZL3b_text','IT2a_text','RF1b_text')]
 if z['all_three_present']=='1' and len(set(v))==1:stable.append((k,v[0]))
c=Counter(v for k,v in stable);assert len(clear)==24 and len(stable)==17 and max(c.values())==1;checks.append('zero_exact_recurrence')
r=json.loads(RES.read_text());assert r['status']=='STOP_NO_TRANSFERABLE_FLOWER_COUNT_AND_ZERO_EXACT_RECURRENCE' and r['counts']['recurrent_complete_literal_types']==0 and r['access']['complete_literal_surfaces_displayed_in_development_diagnostic'];checks.append('stored_stop_and_disclosure')
assert '**None repeats**' in REP.read_text();checks.append('report_ceiling')
result={'experiment':'PHF001_PHARMA_FLOWER_COUNT_AND_EXACT_RECURRENCE_VALIDATION','status':'PASS_7_CHECK_INDEPENDENT_RECONSTRUCTION','check_count':len(checks),'checks':checks,'validated_result_sha256':hashlib.sha256(RES.read_bytes()).hexdigest(),'claim_ceiling':'Validation confirms only the stopped flower-count and zero exact-recurrence screen. It supplies no translation.'}
payload=json.dumps(result,indent=2,sort_keys=True)+'\n';report=f"# PHF001 validation\n\nStatus: **{result['status']}**.\n\nIndependent code reconstructs the 25/18/9 flower panels, folio support, 24 clear cells, 17 all-reading-stable literals, zero recurrence, disclosure, stored stop, and report ceiling. No translation follows.\n"
if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
OUT.write_text(payload);REPORT.write_text(report)
