#!/usr/bin/env python3
"""Separate independent prediction comparison and full source/state checks."""
import csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
spec=json.loads((E/'src/SPEC.json').read_text());b=json.loads((E/'src/BINDINGS.json').read_text())
assert hashlib.sha256((E/'src/SPEC.json').read_bytes()).hexdigest()==b['spec_sha256']
data={}
for key,x in spec['inputs'].items():
 raw=(ROOT/x['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==x['sha256'];data[key]=json.loads(raw)
p=b['independent_predictions'];raw=(ROOT/p['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==p['sha256'];ind=json.loads(raw)
for path,sha in b['implementation_hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
a=data['author'];t=data['target'];r=json.loads((E/'artifacts/RESULT.json').read_text())
assert len(r['cases'])==len(ind['cases'])==4
canon=lambda x:'P14' if x=='R14' else x
expected={(x['policy'],x['OL13_CHEDY14_scope']):x for x in ind['cases']}
checks=0
for c in r['cases']:
 e=expected[(c['policy'],c['scope'])];g=c['graph'];tr=c['trace'];assert [x['position'] for x in tr]==list(range(1,19));checks+=18
 actual=[(x['child'],x['parent'],x['introduced_id']) for x in g['parents']]
 want=[(canon(x['child']),canon(x['parent']),x['introduced_id']) for x in e['parent_graph']];assert actual==want;checks+=7
 for node,x in e['entities'].items():
  y=g['entities'][canon(node)];assert y['sort']==x['sort'] and y['initial_attributes']==x['initial_attributes'];assert y['parent']==canon(x['parent']);checks+=3
 for y,x in zip(g['events'],e['event_patients']):
  assert y['position']==x['position'] and y['source_id']==x['id'];assert y['patient']==canon(x['patient'])
  assert y['predicate']==x['predicate'].split('/')[0].lower();assert y['current_before']==canon(x['CURRENT_before']) and y['current_after']==canon(x['CURRENT_after']);assert y['writes_current']==x['write_CURRENT'];checks+=7
 for y,x in zip(g['assertions'],e['property_assertions']):
  assert y['position']==x['position'] and y['source_id']==x['id'];assert y['input']==canon(x['evaluated_input']);assert set(y['attributes'])==set(x['asserted_attributes']);assert y['output_inheritance'] is False;checks+=5
 assert len(g['assertions'])==len(e['property_assertions'])==15
 for y,x in zip(g['writes'],e['CURRENT_writes']):
  assert y['position']==x['position'] and y['before']==canon(x['CURRENT_before']) and y['after']==canon(x['CURRENT_after']) and y['parent']==canon(x['parent']);checks+=4
 assert g['final_state']=={'topic':'M2','current':'W18','owner':None};assert next(x for x in g['events'] if x['position']==16)['current_after']=='P15';checks+=2
 # Prefix graph ancestry and qualification consequences, without importing runner.
 for node,x in g['entities'].items():
  if node!='M2':assert x['initial_attributes']==[]
  if x.get('relation')=='proper_portion':assert node in ['P5','P9','P10','P15','P17']
 assert sum(x.get('relation')=='proper_portion' for x in g['entities'].values())==5
 assert g['entities']['P14']['relation']=='retained_part' and g['entities']['W18']['relation']=='working_part';checks+=3
 assert [x['position'] for x in c['f85_trace']]==[1,2,3];assert c['f85_graph']['entities']['C1']['contains']=='M1';assert c['f85_graph']['events'][0]['patient']=='M1';checks+=3
 sha=hashlib.sha256(json.dumps(g,sort_keys=True).encode()).hexdigest();assert sha==c['graph_sha256'];checks+=1
# Scope alternatives are equal in full semantic state, not only a selected event.
for policy in ['TOPIC','CURRENT']:
 cases=[x for x in r['cases'] if x['policy']==policy];assert cases[0]['graph']==cases[1]['graph'];checks+=1
assert r['cases'][0]['graph']!=r['cases'][2]['graph']
assert r['graph_equivalence_groups']==[['TOPIC_SEPARATE','TOPIC_NOMINAL_EVENT'],['CURRENT_SEPARATE','CURRENT_NOMINAL_EVENT']]
assert (r['projected_groups'],r['newly_executed_groups'],r['remaining_unconsumed'],r['whole_contexts_complete'])==(21,10,108,0)
with (E/'artifacts/ALL_POSITIONS.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
assert len(table)==129
rawrows=[(c['context'],x) for c in t['contexts'] for x in c['groups']]
for row,old,(ctx,raw) in zip(table,a['positions'],rawrows):
 assert row['context']==ctx==old['context'] and row['raw_id']==raw['source_group_id']==old['raw_id']
 assert row['raw_surface']==raw['ivtff_group_raw']==old['raw_surface'];assert row['segmentation'].split('+')==old['segmentation'];assert row['original_status']==old['status'];checks+=4
 covered=old['position']<=(18 if ctx.startswith('f80') else 3)
 for c in r['cases']:
  if covered:
   value=json.loads(row[c['id']]);assert value['source_id']==old['raw_id'];assert value['output_sort'] in ['Material','Container']
  else:assert row[c['id']]=='UNBOUND_NOT_CONSUMED'
  checks+=1
 assert old['left_separator']==raw['left_separator'] and old['right_separator']==raw['right_separator'];checks+=2
v={'status':'PASS','checks':checks,'coverage':'Bound inputs/code/predictions, independent fourcase parent/event/property/CURRENT expectations,84prefix records,all129rawgroups and108remainingUNBOUND percase,full semantic scope equality','identifier_normalization':'Opaque retained result R14->P14 only; source/role unchanged','meaning_validated':False,'generic_parser_validated':False,'whole_reading_complete':False,'confirmed_words':0,'independent_confirmation_capacity':0}
(E/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
