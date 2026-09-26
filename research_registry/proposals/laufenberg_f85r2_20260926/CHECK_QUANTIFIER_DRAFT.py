#!/usr/bin/env python3
"""Check frozen 558 accounting. This is not a semantic parser or verifier."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
B=Path(__file__).resolve().parent
ROOT=B.parents[2]
D=B/'quantifier_whole_draft'
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(name,ok):
    assert ok,name
    checks.append(name)
f=read(D/'FREEZE_RECEIPT.json')
ck('all seven frozen content hashes',all(sha(D/p)==h for p,h in f['content_hashes'].items()))
ck('all five frozen input hashes',all(sha(ROOT/p)==h for p,h in f['input_hashes_at_freeze'].items()))
L=read(D/'LEXICON.json');A=read(D/'ALL_OCCURRENCES.json');G=read(D/'ALTERNATE_GAPS.json')
with (ROOT/L['target_input']).open() as handle:
    source=list(csv.DictReader(handle,delimiter='\t'))
ck('owned source is only f85r2',all(x['locus'].startswith('f85r2.') for x in source))
z=[x for x in source if x['edition']=='ZL3b']
fields=list(z[0])
ck('156 full raw rows preserved',len(z)==156 and [{k:r[k] for k in fields} for r in A['occurrences']]==z)
entries={x['raw_form']:x for x in L['entries']}
ck('115 types exactly cover ZL',len(entries)==115 and set(entries)=={x['ivtff_group_raw'] for x in z})
ck('one type/value/gloss per repeated raw form',all(all(r[k]==entries[r['ivtff_group_raw']][k] for k in ['type','value','gloss']) for r in A['occurrences']))
raw=read(B/'ideas/28_common_membership_regimen_quantifiers.json')['design']['assignments']
ck('all seven seeds unchanged',L['fixed_seed_assignments']==raw and all(entries[k]['raw_seed_record']==v for k,v in raw.items()))
byid={r['source_group_id']:r for r in z}
ids=[x for c in A['clauses'] for x in c['token_ids']]
ck('29 clauses account for each group once',len(A['clauses'])==29 and Counter(ids)==Counter(byid.keys()))
ck('clause literal forms match source',all(c['raw_forms']==[byid[i]['ivtff_group_raw'] for i in c['token_ids']] for c in A['clauses']))
for ed,n in [('IT2a',157),('RF1b',160)]:
    alt=[r for line in G['lines'] if line['edition']==ed for r in line['native_rows']]
    ck(ed+' native rows conserved',len(alt)==n and alt==[r for r in source if r['edition']==ed])
C=Counter(x['ivtff_group_raw'] for x in z)
counts={'ZL_groups':len(z),'ZL_types':len(C),'hapax_types':sum(v==1 for v in C.values()),'seed_values':len(raw),'new_values':sum(x['new_binding_cost'] for x in entries.values()),'clauses':len(A['clauses']),'clauses_with_unresolved':sum(bool(c['unresolved']) for c in A['clauses'])}
ck('declared incomplete semantic closure retained',A['complete_semantic_parse_claim'] is False and read(D/'SOURCE_COVERAGE.json')['all_eight_obligations_semantically_completed'] is False)
out={'status':'PASS_RECORD_INTEGRITY_ONLY','checks':checks,'counts':counts,'not_validated':['word meanings','source entailment','grammar or scope truth','independent target preference']}
(B/'QUANTIFIER_DRAFT_INTEGRITY.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
