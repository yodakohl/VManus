#!/usr/bin/env python3
"""Independent reconstruction of the masked diagnostic transition panel."""

from __future__ import annotations
import csv,hashlib,json,re
from collections import Counter
from copy import deepcopy
from pathlib import Path

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";SOURCE_VALIDATION=RESULTS/"source_sta_family_consensus_validation.json";FAMILY_ATLAS_VALIDATION=RESULTS/"source_native_transition_atlas_validation.json";SPEC=BASE/"SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_CAPACITY_SPEC.md";BUILDER=BASE/"build_source_native_diagnostic_transition_capacity.py";PANEL=RESULTS/"source_native_diagnostic_transition_masked.tsv";PRODUCTION=RESULTS/"source_native_diagnostic_transition_capacity.json";PRODUCTION_REPORT=RESULTS/"source_native_diagnostic_transition_capacity_report.md";OUT=RESULTS/"source_native_diagnostic_transition_capacity_validation.json";REPORT=RESULTS/"source_native_diagnostic_transition_capacity_validation_report.md"
FROZEN={SOURCE:"a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",SOURCE_VALIDATION:"fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",FAMILY_ATLAS_VALIDATION:"209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c",SPEC:"f7db5445659acb097db3262bb2eab2dd9c4b68e2564dca71d6912d195496b1c9",BUILDER:"9d6cf392db5bc08019d4f9fe2f50baf9f35a57786671e78d86e2ae00e3ac1027",PANEL:"7ed9f8186dcb31bd49a446e6b7751dc0bfc0f9d508feb816314fc71105daea02",PRODUCTION:"8b7b17f0c254e719612bc5a10641058a50c169af61e19df2b48379e27b0d448b",PRODUCTION_REPORT:"b16af064a203fe9aae5807555c99af4eba21114688487c007ce95f950053733c"};FIELDS=("unit_id","locus","page","physical_folio","section","currier","kind","symbol_count")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def folio(page):
 match=re.fullmatch(r'(f\d+)[rv]\d*',page)
 if match is None:raise ValueError('page')
 return match.group(1)
def derive(source):
 if len(source)!=26184 or len({row['consensus_group_id'] for row in source})!=26184:raise ValueError('source identity')
 rows=[]
 for row in source:
  if row['strict_zero_alternative']=='1' and row['grammar_scope']=='DIAGNOSTIC_NONPROSE' and re.fullmatch(r'f\d+[rv]\d*',row['page']):rows.append({'unit_id':row['consensus_group_id'],'locus':row['locus'],'page':row['page'],'physical_folio':folio(row['page']),'section':row['section'],'currier':row['currier'],'kind':row['kind'],'symbol_count':row['symbol_count']})
 if len(rows)!=1382 or len({row['unit_id'] for row in rows})!=1382:raise ValueError('capacity')
 return sorted(rows,key=lambda row:row['unit_id'])
def ensemble(rows,keys):
 counts=Counter(tuple(row[key] for key in keys) for row in rows);movable=[row for row in rows if counts[tuple(row[key] for key in keys)]>=2]
 return {'strata':len(counts),'multi_group_strata':sum(value>=2 for value in counts.values()),'movable_groups':len(movable),'movable_length_ge_2_groups':sum(int(row['symbol_count'])>=2 for row in movable),'movable_noninitial_positions':sum(max(0,int(row['symbol_count'])-1) for row in movable),'movable_physical_folios':len({row['physical_folio'] for row in movable}),'maximum_stratum_size':max(counts.values())}
def summarize(rows):return {'groups':len(rows),'physical_folios':len({row['physical_folio'] for row in rows}),'length_ge_2_groups':sum(int(row['symbol_count'])>=2 for row in rows),'noninitial_positions':sum(max(0,int(row['symbol_count'])-1) for row in rows),'currier':dict(sorted(Counter(row['currier'] for row in rows).items())),'section':dict(sorted(Counter(row['section'] for row in rows).items())),'kind':dict(sorted(Counter(row['kind'] for row in rows).items())),'length':{str(key):value for key,value in sorted(Counter(int(row['symbol_count']) for row in rows).items())},'ensembles':{'SECTION_KIND_LENGTH':ensemble(rows,('section','kind','symbol_count')),'FOLIO_KIND_LENGTH':ensemble(rows,('physical_folio','kind','symbol_count'))}}
def main():
 if OUT.exists() or REPORT.exists():raise SystemExit('refusing overwrite')
 failures=[];checks=0
 def check(condition,name):
  nonlocal checks;checks+=1
  if not condition:failures.append(name)
 for path,expected in FROZEN.items():check(sha(path)==expected,f'hash:{path.name}')
 with SOURCE.open(encoding='utf-8',newline='') as handle:source=list(csv.DictReader(handle,delimiter='\t'))
 rebuilt=derive(source);counts=summarize(rebuilt)
 with PANEL.open(encoding='utf-8',newline='') as handle:reader=csv.DictReader(handle,delimiter='\t');check(tuple(reader.fieldnames or ())==FIELDS,'schema');stored=list(reader)
 check(stored==rebuilt,'rows');check(len({row['unit_id'] for row in stored})==1382,'unique');production=json.loads(PRODUCTION.read_text());check(production['counts']==counts,'counts');check(production['tsv_sha256']==sha(PANEL),'binding');check(production['inputs']=={path.name:sha(path) for path in list(FROZEN)[:5]},'inputs');check(production['status']=='PASS_TARGET_MASKED_DIAGNOSTIC_TRANSFER_CAPACITY' and production['decision']=='GO_INDEPENDENTLY_VALIDATE_MASKED_CAPACITY','decision');check(production['target_surface_columns_used']==[] and production['target_family_sequences_output']==0 and production['target_member_codes_output']==0 and production['target_scores_computed']==0 and production['english_glosses']==0,'ceiling')
 expected_report="""# Diagnostic transition-transfer capacity

Status: **PASS_TARGET_MASKED_DIAGNOSTIC_TRANSFER_CAPACITY**

The masked panel retains **1,382** strict diagnostic groups on **26** physical
folios. Its **1,302** groups of length at least two supply **4,857** noninitial
positions. `SECTION_KIND_LENGTH` retains 4,780 movable positions; the stricter
`FOLIO_KIND_LENGTH` ensemble retains 4,560.

The output contains metadata and length only: zero family sequences, member
codes, scores, or English glosses. Decision:
**GO_INDEPENDENTLY_VALIDATE_MASKED_CAPACITY**. No wordhood, ownership, label
meaning, picture identity, sound, language, cipher, plaintext, or translation
follows.
""";check(PRODUCTION_REPORT.read_text()==expected_report,'report')
 target_index=next(index for index,row in enumerate(source) if row['strict_zero_alternative']=='1' and row['grammar_scope']=='DIAGNOSTIC_NONPROSE' and re.fullmatch(r'f\d+[rv]\d*',row['page']))
 for name,mutation in (('missing',lambda rows:rows.pop(target_index)),('duplicate',lambda rows:rows.append(dict(rows[target_index]))),('scope',lambda rows:rows[target_index].__setitem__('grammar_scope','CONFIRMED_PROSE')),('page',lambda rows:rows[target_index].__setitem__('page','bad'))):
  altered=deepcopy(source);mutation(altered)
  try:derive(altered)
  except ValueError:passed=True
  else:passed=False
  check(passed,'mutation:'+name)
 if failures:raise SystemExit('validation failed: '+failures[0])
 result={'experiment':'SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_CAPACITY_VALIDATION','status':'PASS_INDEPENDENT_TARGET_MASKED_DIAGNOSTIC_CAPACITY_RECONSTRUCTION','checks':checks,'failures':[],'rows':len(rebuilt),'noninitial_positions':counts['noninitial_positions'],'physical_folios':counts['physical_folios'],'ensemble_capacity':counts['ensembles'],'mutations':4,'target_surface_columns_used':[],'target_family_sequences_output':0,'target_scores_computed':0,'english_glosses':0,'inputs':{path.name:sha(path) for path in FROZEN},'claim_ceiling':'Independent target-masked capacity reconstruction only; no wordhood, ownership, label meaning, sound, language, cipher, plaintext, or translation follows.'};OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');REPORT.write_text(f"""# Diagnostic transition capacity validation

Status: **{result['status']}**

A production-free reconstruction matches all **1,382** masked rows, both
rotation-capacity summaries, bindings, report, and four mutations in
**{checks}** checks. It uses and outputs zero family surfaces or member codes.

This validates capacity only and supplies no wordhood, ownership, label
meaning, picture identity, sound, language, cipher, plaintext, or translation.
""");print(json.dumps({'status':result['status'],'checks':checks},sort_keys=True))
if __name__=='__main__':main()
