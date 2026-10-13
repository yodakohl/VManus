#!/usr/bin/env python3
"""Reproduce only admitted metadata counts; never rerun historical decoders."""
import csv,hashlib,io,json,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
ROOT=next(p for p in D.parents if (p/'vmanus-exp').is_file())
def read(p):return json.loads(p.read_text())
audit=read(D/'CONSONANTAL_LOCAL_SEARCH_SCOPE_AUDIT_20261013.json')
for item in audit['primaries']:
 assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
expected=read(D/'CONSONANTAL_INPUT_SCOPE_METADATA_20261013.json')
legacy=read(ROOT/'gdt193_result.json')
source=ROOT/'gdt016_group_state_inventory.tsv'
assert hashlib.sha256(source.read_bytes()).hexdigest()==expected['source_sha256']==legacy['inputs'][source.name]
allow=[r['page'] for r in csv.DictReader((ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')]
args=['./vmanus-exp','query-tsv',source.name,'--selector','page']
for page in allow:args+=['--allow',page]
args+=['--columns','locus,page']
p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,check=True)
reader=csv.DictReader(io.StringIO(p.stdout),delimiter='\t');assert reader.fieldnames==['locus','page'];rows=list(reader)
assert all(r['page'] in allow and not r['page'].startswith('f84') for r in rows)
remaining=[r for r in rows if r['locus']!='f102v2.33']
assert len(rows)==expected['current_allowed_rows_before_legacy_exclusion']
assert len(remaining)==expected['current_allowed_rows_after_legacy_exclusion']
assert legacy['counts']['source_rows']==expected['legacy_reported_rows']
assert legacy['counts']['source_rows']-len(remaining)==expected['legacy_rows_outside_current_selectors']
assert p.stderr.strip()==expected['guard_receipt']
for name in ['gdt193_result.json','gdt194_result.json']:
 result=read(ROOT/name);assert result['gates']['all_pass'] is False and result['gates']['best_beats_matched_kt'] is False and result['gates']['best_mapping_stable'] is False
out={'status':'PASS_METADATA_AND_LEGACY_HASHES_ONLY','admitted_group_rows':len(remaining),'legacy_group_rows':legacy['counts']['source_rows'],'difference_group_rows':legacy['counts']['source_rows']-len(remaining),'queried_columns':['locus','page'],'legacy_primaries_unchanged':True,'old_numeric_decisions_unchanged':True,'scope':'Group-record counts, not physical text lines. No decoder/sourcepack run, no nonadmitted row identity or text, no global key or semantic result.'}
(D/'CONSONANTAL_SCOPE_VALIDATION_20261013.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
