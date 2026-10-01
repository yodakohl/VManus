"""Frozen FD literal/argument audit; no independent meaning check."""
import hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[3]
def load(n):return json.loads((P/n).read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
a=load('FD_AUTHOR.json');f=load('FD_FOCUS_PACKET.json');checks=0
assert sha((P/'FD_AUTHOR.json').read_bytes())=='c7b6e7c3073eed97c4d51c6e176de8bf285d7af86446ddf9e1996874f14cebed';checks+=1
for rel,h in a['inputs_sha256'].items():
 data=(P/'FD_ROUTING_INPUT.txt').read_bytes() if rel=='VOYNICH_CURRENT_ROUTE.md' else (R/rel).read_bytes()
 assert sha(data)==h,(rel,'hash');checks+=1
for k in ['frozen73','frozen11_rules','retained_new12']:assert a[k]==f[k];checks+=1
assert len(a['new_atomic_values'])==13 and len(a['new_rules'])==8;checks+=2
maps={b:{**f['frozen73'][b],**{k:v['value'] for k,v in a['new_atomic_values'].items()}} for b in ['G','I']}
assert all(len(m)==86 for m in maps.values());checks+=2
for ed,source in f['editions'].items():
 rows=a['primary_positions'] if ed=='IT2a' else a['alternate_readings'][ed]['positions']
 assert len(rows)==len(source);checks+=1
 for row,original in zip(rows,source):
  for k,v in original.items():assert row[k]==v,(ed,k);checks+=1
  if ed=='IT2a':
   assert row['value_G']==maps['G'][original['ivtff_group_raw']];assert row['value_I']==maps['I'][original['ivtff_group_raw']];checks+=2
   assert row['contribution'] and row['role'] and row['rule_ids'];checks+=1
   assert row['entity'] is not None or row['event'] is not None;checks+=1
positions=a['primary_positions'];assert positions[10]['value_G']==positions[13]['value_G']=='portion';checks+=1
assert positions[8]['entity']=='R' and positions[6]['entity']=='R';checks+=2
assert a['anchor_discharge']['LFCHEDY']['R6_result']=='R' and not a['anchor_discharge']['LFCHEDY']['unknown_barrier'];checks+=2
assert a['anchor_discharge']['QOKAIIN']['not_bare_liquid'];checks+=1
events={e['id']:e for e in a['phrase_graph']['events']}
assert events['E1']['agent']=='P' and events['E1']['theme']=='R';checks+=2
assert events['E2']['theme']=='R' and events['E3']['theme']=='U' and events['E4']['theme']=='V' and events['E4']['medium']=='H';checks+=4
assert a['phrase_graph']['clause_spans']==[[1,5],[6,10],[11,13],[14,17]];checks+=1
pri={x['form']:x['editions']['IT2a'] for x in load('FD_WORD_PRIORS.json')['profiles']}
for k,v in a['formal_priors'].items():
 for field in ['count','pages_with_form','rank','positions','repetition']:assert v[field]==pri[k][field];checks+=1
result={'unit':'FD','status':'LITERAL_AND_LOCAL_ARGUMENT_CHECKS_PASS','checks':checks,'primary_groups':17,'alternative_groups':{'ZL3b':17,'RF1b':18},'new_values':13,'new_rules':8,'all_values_each_branch':86,'meaning_validation':False,'portable_new_grammar_validated':False,'retained_portability_defect':'N6/N7 generic MOISTURE_PROPERTY conditions hardcode DRY/MOIST; no repair','route_hash_source':'frozen navigation snapshot, never a live resume point or scientific input','global_check':'NOT_RUN; historical failures unchanged'}
(P/'FD_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
