from pathlib import Path
import json, hashlib
P=Path(__file__).resolve().parent
root=P.parents[3]
a=json.loads((P/'FG_AUTHOR.json').read_text())
c=json.loads((P/'FG_CONSTRUCTION_CONTRACT.json').read_text())
f=json.loads((P/'FD_FOCUS_PACKET.json').read_text())
checks=0
assert hashlib.sha256((P/'FG_AUTHOR.json').read_bytes()).hexdigest()=='2b09253df85c732ec0ffbccfc0020dbe434918af21c067100c4e35d9cbb2e264'; checks+=1
assert a['contract']==c; checks+=1
assert [x['ivtff_group_raw'] for x in a['primary_positions']]==c['raw_primary'] and len(a['primary_positions'])==17; checks+=1
for edition in ['IT2a','ZL3b','RF1b']:
 original=f['editions'][edition]
 if isinstance(original,dict):
  original=original.get('groups',original.get('raw_groups'))
 observed=a['primary_positions'] if edition=='IT2a' else a['alternate_raw_capacity'][edition]
 assert [{k:x[k] for k in original[0]} for x in observed]==original
 checks+=1
for path,digest in a['inputs_sha256'].items():
 assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest
 checks+=1
assert a['first_unsatisfied']['position']==14 and a['first_unsatisfied']['first_unassigned_whole_position']==16;checks+=1
assert a['identity_policies']['output_difference'].startswith('NONE_ESTABLISHED');checks+=1
result={'status':'BINDING_CONSERVATION_PASS','checks':checks,'meaning_validation':False,'grammar_default_budget_certified':False,'scope':'frozen artifact/input hashes and raw conservation only, not complete composition'}
(P/'FG_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
