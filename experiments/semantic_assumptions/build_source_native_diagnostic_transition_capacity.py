#!/usr/bin/env python3
"""Build a target-masked diagnostic-group transition capacity panel."""

from __future__ import annotations
import csv,hashlib,json,re
from collections import Counter
from pathlib import Path

BASE=Path(__file__).resolve().parent;RESULTS=BASE/"results";SOURCE=RESULTS/"source_sta_family_consensus_groups.tsv";SOURCE_VALIDATION=RESULTS/"source_sta_family_consensus_validation.json";FAMILY_ATLAS_VALIDATION=RESULTS/"source_native_transition_atlas_validation.json";SPEC=BASE/"SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_CAPACITY_SPEC.md";BUILDER=Path(__file__).resolve();OUT_TSV=RESULTS/"source_native_diagnostic_transition_masked.tsv";OUT_JSON=RESULTS/"source_native_diagnostic_transition_capacity.json";OUT_REPORT=RESULTS/"source_native_diagnostic_transition_capacity_report.md"
FROZEN={SOURCE:"a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",SOURCE_VALIDATION:"fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",FAMILY_ATLAS_VALIDATION:"209510d655c4b81c58f8f5eaec27676a4eee71317e3b485b3a1ce88d975dfd5c",SPEC:"f7db5445659acb097db3262bb2eab2dd9c4b68e2564dca71d6912d195496b1c9"};FIELDS=("unit_id","locus","page","physical_folio","section","currier","kind","symbol_count")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def folio(page):
 match=re.fullmatch(r'(f\d+)[rv]\d*',page)
 if match is None:raise ValueError('page')
 return match.group(1)
def strata(rows,keys):
 counts=Counter(tuple(row[key] for key in keys) for row in rows);movable=[row for row in rows if counts[tuple(row[key] for key in keys)]>=2]
 return {'strata':len(counts),'multi_group_strata':sum(value>=2 for value in counts.values()),'movable_groups':len(movable),'movable_length_ge_2_groups':sum(int(row['symbol_count'])>=2 for row in movable),'movable_noninitial_positions':sum(max(0,int(row['symbol_count'])-1) for row in movable),'movable_physical_folios':len({row['physical_folio'] for row in movable}),'maximum_stratum_size':max(counts.values())}
def main():
 if any(path.exists() for path in (OUT_TSV,OUT_JSON,OUT_REPORT)):raise SystemExit('refusing overwrite')
 for path,expected in FROZEN.items():
  if sha(path)!=expected:raise SystemExit(f'frozen input mismatch: {path.name}')
 if json.loads(SOURCE_VALIDATION.read_text())['status']!='PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION' or json.loads(FAMILY_ATLAS_VALIDATION.read_text())['status']!='PASS_INDEPENDENT_576_PAIR_HELD_FOLIO_RECONSTRUCTION':raise SystemExit('authorization failure')
 with SOURCE.open(encoding='utf-8',newline='') as handle:source=list(csv.DictReader(handle,delimiter='\t'))
 rows=[]
 for row in source:
  if row['strict_zero_alternative']!='1' or row['grammar_scope']!='DIAGNOSTIC_NONPROSE' or not re.fullmatch(r'f\d+[rv]\d*',row['page']):continue
  rows.append({'unit_id':row['consensus_group_id'],'locus':row['locus'],'page':row['page'],'physical_folio':folio(row['page']),'section':row['section'],'currier':row['currier'],'kind':row['kind'],'symbol_count':row['symbol_count']})
 if len(rows)!=1382 or len({row['unit_id'] for row in rows})!=1382:raise ValueError('capacity')
 rows.sort(key=lambda row:row['unit_id']);counts={'groups':len(rows),'physical_folios':len({row['physical_folio'] for row in rows}),'length_ge_2_groups':sum(int(row['symbol_count'])>=2 for row in rows),'noninitial_positions':sum(max(0,int(row['symbol_count'])-1) for row in rows),'currier':dict(sorted(Counter(row['currier'] for row in rows).items())),'section':dict(sorted(Counter(row['section'] for row in rows).items())),'kind':dict(sorted(Counter(row['kind'] for row in rows).items())),'length':{str(key):value for key,value in sorted(Counter(int(row['symbol_count']) for row in rows).items())},'ensembles':{'SECTION_KIND_LENGTH':strata(rows,('section','kind','symbol_count')),'FOLIO_KIND_LENGTH':strata(rows,('physical_folio','kind','symbol_count'))}}
 if counts['physical_folios']!=26 or counts['length_ge_2_groups']!=1302 or counts['noninitial_positions']!=4857 or counts['currier']!={'':991,'A':228,'B':163}:raise ValueError('aggregate')
 with OUT_TSV.open('w',encoding='utf-8',newline='') as handle:writer=csv.DictWriter(handle,fieldnames=FIELDS,delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(rows)
 result={'experiment':'SOURCE_NATIVE_DIAGNOSTIC_TRANSITION_CAPACITY','status':'PASS_TARGET_MASKED_DIAGNOSTIC_TRANSFER_CAPACITY','inputs':{path.name:sha(path) for path in (*FROZEN,BUILDER)},'counts':counts,'tsv_sha256':sha(OUT_TSV),'target_surface_columns_used':[],'target_family_sequences_output':0,'target_member_codes_output':0,'target_scores_computed':0,'english_glosses':0,'decision':'GO_INDEPENDENTLY_VALIDATE_MASKED_CAPACITY','claim_ceiling':'Target-masked capacity for later synthetic calibration only; no wordhood, ownership, label meaning, picture identity, sound, language, cipher, plaintext, or translation follows.'};OUT_JSON.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');OUT_REPORT.write_text(f"""# Diagnostic transition-transfer capacity

Status: **{result['status']}**

The masked panel retains **1,382** strict diagnostic groups on **26** physical
folios. Its **1,302** groups of length at least two supply **4,857** noninitial
positions. `SECTION_KIND_LENGTH` retains 4,780 movable positions; the stricter
`FOLIO_KIND_LENGTH` ensemble retains 4,560.

The output contains metadata and length only: zero family sequences, member
codes, scores, or English glosses. Decision:
**GO_INDEPENDENTLY_VALIDATE_MASKED_CAPACITY**. No wordhood, ownership, label
meaning, picture identity, sound, language, cipher, plaintext, or translation
follows.
""");print(json.dumps({'status':result['status'],'counts':counts,'decision':result['decision']},sort_keys=True))
if __name__=='__main__':main()
