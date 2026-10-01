"""Literal conservation and full diagnostic replay, no meaning validation."""
import csv, importlib.util, json
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fc_audit',P/'FC_AUDIT.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=m.build();checks=0
for name,value in out.items():assert (P/name).read_text()==value,name;checks+=1
cases=json.loads(out['FC_CASES.json']);result=json.loads(out['FC_RESULT.json']);contexts=json.loads(out['FC_WHOLE_CONTEXTS.json'])
assert len(cases)==542 and len({x['source_group_id'] for x in cases})==542;checks+=2
assert len(contexts['paragraphs'])==258 and sum(len(x['groups']) for x in contexts['paragraphs'])==15662;checks+=2
assert result['outside_resolved_reference_claims']==0 # Flag is no assertion, not a solver result.
assert len([x for x in cases if x['split']!='ORIGINAL_CONSTRUCTION' and x['form']=='dain' and x['status']=='CANDIDATE_LABEL_ONLY'])==8;checks+=2
assert {x['locus'] for x in cases if x['split']!='ORIGINAL_CONSTRUCTION' and x['form']=='dain' and x['status']=='CANDIDATE_LABEL_ONLY'}=={'f5v.2','f47r.3','f47v.9','f81r.10'};checks+=1
for x in cases:
 if x['form']=='lfchedy' and x['split']!='ORIGINAL_CONSTRUCTION':
  assert x['locus']=='f113r.37';assert x['status'] in ('UNKNOWN_OR_BOUNDARY_BLOCKED','NO_PARAGRAPH_CAPACITY');checks+=2
with (P/'FC_ALL_DUTIES.tsv').open() as f:rows=list(csv.DictReader(f,delimiter='\t'))
assert [x['source_group_id'] for x in rows]==[x['source_group_id'] for x in cases];checks+=1
for row,case in zip(rows,cases):
 assert row['observed_status']==case['status'];assert row['hypothetical_value']==case['value'];assert row['reference_resolution']=='NOT_IMPLEMENTED_NO_OUTSIDE_GRAPH_ASSERTED';checks+=3
with (P/'FC_CANDIDATE_TABLE.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
assert len(table)==6;checks+=1
for row in table:
 subset=[x for x in cases if x['edition']==row['edition'] and x['form']==row['form']]
 assert int(row['all_occurrences'])==len(subset);assert int(row['outside_occurrences'])==sum(x['split']!='ORIGINAL_CONSTRUCTION' for x in subset);checks+=2
validation={'unit':'FC','status':'LITERAL_COVERAGE_REPLAY_PASS','checks':checks,'meaning_validation':False,'entity_resolution_implemented':False,'outside_graph_impossibility_claim':False,'global_check':'NOT_RUN; original historical failures remain','regenerated_without_writes':True}
(P/'FC_VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n');print(json.dumps(validation))
