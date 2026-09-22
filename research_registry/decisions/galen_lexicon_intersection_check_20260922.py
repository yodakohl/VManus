"""Rebuild the full 67/59 lexical intersection, without manuscript data or semantic scoring."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
inputs=['research_registry/proposals/raw_galen_2442_target_development_20260921.json','research_registry/proposals/raw_galen_2443_specific_transfer_extension_20260921.json','research_registry/proposals/raw_galen_2444_comparison_epistemic_target_20260921.json','research_registry/proposals/raw_galen_2445_frozen38_extension_20260921.json']
a,b,c,d=[json.loads((ROOT/p).read_text()) for p in inputs]
A={x['form']:dict(x) for x in a['lexicon']+b['new_lexicon']}
change=b['explicit_new_branch_before_any_semantic_test']['changed_entry']
for k in ['value','type','denotation']:A[change['form']][k]=change['new_'+k]
B={x['form']:dict(x) for x in d['frozen_parent_lexicon']+d['new_lexicon']}
assert len(A)==67 and len(B)==59
shared=sorted(A.keys()&B.keys());assert len(shared)==13
rows=[{'form':w,'A':{k:A[w][k] for k in ['value','type','denotation']},'B':{k:B[w][k] for k in ['value','type','denotation']},'literal_fields_identical':all(A[w][k]==B[w][k] for k in ['value','type','denotation'])} for w in shared]
report=ROOT/'research_registry/decisions/galen_1029_501_complete_lexicon_intersection_20260922.md'
t=report.read_text()
assert set(shared)==set(line.split('`')[1] for line in t.splitlines() if line.startswith('| `') and '<br>' in line)
for row in rows:
 for side in ['A','B']:
  for field in ['value','type','denotation']:assert row[side][field].replace('|','\\|') in t,(row['form'],side,field)
print(json.dumps({'status':'PASS_LITERAL_EXTRACTION_AND_ALL_78_FIELDS','inputs':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},'a_types':len(A),'b_types':len(B),'intersection':len(shared),'union':len(A.keys()|B.keys()),'literal_identical':sum(r['literal_fields_identical'] for r in rows),'rows':rows,'semantic_contradictions_verified_by_code':False,'semantic_reasoning':'See complete manually reviewed table; literal mismatch alone is not semantic contradiction.'},indent=2,ensure_ascii=False))
