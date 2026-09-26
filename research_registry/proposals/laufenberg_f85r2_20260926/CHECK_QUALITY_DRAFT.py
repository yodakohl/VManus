#!/usr/bin/env python3
"""Independent conservation/hash audit of the frozen authored draft, not meaning."""
import csv, hashlib, json
from collections import Counter
from pathlib import Path
B=Path(__file__).resolve().parent
R=B.parents[2]
P=B/'quality_whole_draft'
receipt=json.loads((P/'FREEZE_RECEIPT.json').read_text())
checks={}
checks['frozen_contents']=all(hashlib.sha256((P/n).read_bytes()).hexdigest()==h for n,h in receipt['content_hashes'].items())
checks['bound_inputs']=all(hashlib.sha256((R/n).read_bytes()).hexdigest()==h for n,h in receipt['input_hashes_at_freeze'].items())
lex=json.loads((P/'LEXICON.json').read_text())
doc=json.loads((P/'ALL_OCCURRENCES.json').read_text())
# Input is the previously guarded, single admitted selector artifact, not a mixed source.
with (R/lex['target_input']).open() as f:
 reader=csv.DictReader(f,delimiter='\t'); fields=reader.fieldnames
 src=[r for r in reader if r['edition']=='ZL3b' and r['block'] in {'N','E','S','W'}]
obs=doc['occurrences']; entries=lex['entries']
checks['source_conservation']= [{k:r[k] for k in fields} for r in obs]==src
raw=Counter(r['ivtff_group_raw'] for r in src)
checks['counts']=len(src)==108 and len(raw)==85 and sum(v==1 for v in raw.values())==73
by_raw={r['raw_form']:r for r in entries}; by_id={r['source_group_id']:r for r in obs}
checks['unique_dictionary']=len(by_raw)==len(entries)==85 and set(by_raw)==set(raw)
checks['all_occurrence_values']=all(all(r[k]==by_raw[r['ivtff_group_raw']][k] for k in ['type_A','value_A','gloss_A','type_B','value_B','gloss_B']) for r in obs)
checks['dictionary_links']=all(e['occurrence_ids']==[r['source_group_id'] for r in obs if r['ivtff_group_raw']==e['raw_form']] for e in entries)
clause_ids=[i for c in doc['clauses'] for i in c['token_ids']]
checks['clause_partition']=clause_ids==[r['source_group_id'] for r in src]
checks['clause_raw_and_roles']=all(c['raw_tokens']==[by_id[i]['ivtff_group_raw'] for i in c['token_ids']] and set(c['token_roles'])==set(c['token_ids']) and all(by_id[i]['clause_id']==c['clause_id'] for i in c['token_ids']) for c in doc['clauses'])
checks['seed_preserved']=all(by_raw[x]['value_A']==y for x,y in {'dar':'HOT','daiin':'MOIST','qodar':'NOT_HOT','qodaiin':'NOT_MOIST'}.items())
checks['only_rival_changes']=set(e['raw_form'] for e in entries if e['value_A']!=e['value_B'])=={'qodar','qodaiin'}
checks['new_binding_count']=sum(e['freedom_cost'] for e in entries)==81
out={'status':'PASS_RECORD_INTEGRITY_ONLY' if all(checks.values()) else 'FAIL_RECORD_INTEGRITY','checks':checks,'counts':{'groups':len(src),'types':len(raw),'hapax_types':sum(v==1 for v in raw.values()),'clauses':len(doc['clauses'])},'not_tested':['semantic truth','historical medical plausibility','independent meaning binding','automatic logical proof','statistical significance','rival selection']}
(B/'QUALITY_DRAFT_INTEGRITY.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
assert all(checks.values())
