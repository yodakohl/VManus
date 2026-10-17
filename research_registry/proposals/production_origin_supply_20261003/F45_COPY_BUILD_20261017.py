#!/usr/bin/env python3
"""Finite authored A-block copy alternative, not a Voynich decoder."""
import collections,copy,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=read(D/'F45R_RECORD_SYNTHESIS_DERIVATION_20261015.json');rules=read(D/'F45R_RECORD_SYNTHESIS_RULES_20261015.json')
assert sha(D/'F45R_RECORD_SYNTHESIS_RULES_20261015.json')==parent['rules_sha256']
assert sha(ROOT/rules['source'])==parent['source_sha256']==rules['source_sha256']
assert len(parent['trace'])==86 and parent['summary']['paragraph_groups']==[33,21,32]
records=[];computed={};events={e['id']:e for r in parent['records'] for e in r['field_events']};seen=set();changes=[]
for old in parent['records']:
 name=old['record'];A=[];program=[]
 for row in parent['trace']:
  if row['record']!=name:continue
  if row['kind']=='subject_description':
   item={'descriptor':row['descriptor'],'origin_record':name,'origin_source_ids':[row['id']],'copy_via':[]};A.append(item);program.append({'kind':'LITERAL_A','source_ids':[row['id']],'descriptor':row['descriptor']});continue
  ev=events[row['event']]
  if ev['id'] in seen:continue
  seen.add(ev['id'])
  if ev['roles']!=['dy']:
   program.append({'kind':'UNCHANGED_B','event':copy.deepcopy(ev)});continue
  if ev['kind']=='free_field':
   assert ev['raw']==['kol','dy'] and ev['descriptor']=='kol'
   A.append({'descriptor':'kol','origin_record':name,'origin_source_ids':ev['source_ids'],'copy_via':[]})
   program.append({'kind':'LOCAL_A_FROM_FREE_DY','source_ids':ev['source_ids'],'descriptor':'kol'})
   changes.append({'source_ids':ev['source_ids'],'change':'KOL is now on currentP3A, not an oldDYentityconstraint onP2.'})
  else:
   assert ev['raw'][0] in ('opchaldy','daldy') and ev['kind']=='bound_field'
   candidates=[r['record'] for r in parent['records'] if r['record'] in computed and ev['descriptor'] in r['ordinary_descriptor_set']]
   assert candidates==[ev['anchor_record']]
   source=candidates[0];payload=copy.deepcopy(computed[source]);offset=len(A)
   for item in payload:item['copy_via'].append(ev['source_ids'][0])
   A.extend(payload);program.append({'kind':'COPY_A','source_ids':ev['source_ids'],'source_record':source,'target_record':name,'insertion_offset':offset,'payload_length':len(payload)})
   changes.append({'source_ids':ev['source_ids'],'change':'Replace oldDYsubjectidentity by copied expandedA content.','source_record':source})
 B={k:copy.deepcopy(v) for k,v in old['fields'].items() if k!='dy'}
 computed[name]=copy.deepcopy(A);records.append({'record':name,'subject':old['subject'],'A':A,'A_words':[x['descriptor'] for x in A],'B':B,'program':program,'source_explicit_ordinary':copy.deepcopy(old['ordinary'])})
assert [len(r['A']) for r in records]==[27,44,62]
# Derive facts from new A and unchanged B, never reuse old R1's merged entity facts.
facts=collections.defaultdict(set)
for r in records:
 facts[r['subject']].update(r['A_words'])
 for v in r['B'].values():facts[v['value']].update(v['descriptions'])
assert 'kol' not in facts['P2.subject'] and 'kol' in facts['P3.subject']
assert {'dor','otydal'}<=facts['P2.subject']
assert all('dor' not in r['A_words'] and 'shor' not in r['A_words'] and 'kchol' not in r['A_words'] for r in records)
assert all(r['A_words'].count('chol')==2 and r['A_words'].count('ykeol')==2 for r in records)
coverage=[]
for r in records:
 for event in r['program']:coverage.extend(event['event']['source_ids'] if event['kind']=='UNCHANGED_B' else event['source_ids'])
assert coverage==[r['id'] for r in parent['trace']] and len(set(coverage))==86
oppositions=[{'q_form':q,'base_form':b} for q,b in [('qoky','oky'),('qokaiin','okaiin')] if q in records[2]['A_words'] and b in records[2]['A_words']]
pins=[D/n for n in ['F45_COPY_PLAN_20261017.json','F45_COPY_PROFILES_20261017.json','F45R_RECORD_SYNTHESIS_RULES_20261015.json','F45R_RECORD_SYNTHESIS_DERIVATION_20261015.json','selective_entry_inheritance.json']]+[ROOT/rules['source'],Path(__file__)]
result={'status':'CONDITIONAL_COMPLETE_SOURCE_AUTHORING_NOT_SEMANTIC_SELECTION','original_trace':parent['trace'],'summary':{'original_groups':86,'paragraph_groups':[33,21,32],'expanded_A_lengths':[len(r['A']) for r in records],'literal_A_occurrences':61,'free_DY_local_A_occurrences':1,'copied_A_occurrences':71,'confirmed_words':0},'records':records,'new_subject_and_B_descriptor_constraints':{k:sorted(v) for k,v in sorted(facts.items())},'explicit_changes_from_R1':changes,'conditional_signed_counter':{'status':'ADDITIONAL_COMPLEMENT_AND_FIXED_STATE_CONJUNCTION_CLASHES','pairs_in_P3':oppositions,'limit':'Both complements were separately assumed, not decoded q meanings. This stops only the joint static-copy plus complement account. No hiddenoverwrite/newstate repair is added.'},'limits':['All R1grouping/field/descriptor/prior-anchor assumptions remain unconfirmed. DYnow has a different type from otherfields; threefiniteeventsare expresslychanged.','Copy is proposed for two exact joinedforms, not exported as a universal suffixmeaning. Freekol dy is a paid different construction. Otheroccurrences/reader splits remain counterobligations.','A is an ordered written descriptionblock, not every live property of a physical object. Later B assertions do not rewrite an already copied A.','Repetition/order are retained in copieddata. This alone does not explain the human purpose of every repeated word or establish any lexical meaning.','Fullcopywith explicitoverwrites may beequivalent under othercontracts. No alternative eliminated merelybybetterstory.','The historicalsource903note motivates a possiblearchitecture but supplies no nativewordassignment.','ExpandedA alone does not recover original spelling/provenance uniquely; the original86sourcegroups and taggedprogram are retained.'],'pins':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in pins]}
(D/'F45COPY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result['summary']))
