import csv, hashlib, json
from pathlib import Path
D=Path(__file__).parent
s=json.loads((D/'SPEC.json').read_text())
for p,h in s['hashes'].items(): assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
ctx=json.loads(Path(s['context']).read_text())
effects=json.loads(Path(s['effects']).read_text())['effects']
candidates=json.loads(Path(s['candidate_source']).read_text())['candidates']
rows=[]; evidence=[]
for line in ctx['same_locus_source_lines']:
 ed=line['metadata']['edition']; gs=line['groups']; words=[g['ivtff_group_raw'] for g in gs]
 assert not line['metadata']['page'].startswith('f84')
 state={}; causes=[]; target=s['target'] in words
 if target:
  i=words.index(s['target']); assert i==3 and words[1:3]==['chor','sheey']
  for a,b in zip(gs[:i],gs[1:i+1]):
   assert int(b['source_group_index'])==int(a['source_group_index'])+1
   assert a['right_separator']==b['left_separator']=='DEFINITE_SPACE'
  for j in (0,2):
   effect=effects.get(words[j])
   causes.append(dict(source_id=gs[j]['source_group_id'],raw=words[j],effect=effect,patient=gs[1]['source_group_id'],status='ASSUMED_EFFECT' if effect else 'UNKNOWN_EFFECT'))
   if effect: state[effect['axis']]=effect['value']
 evidence.append(dict(edition=ed,raw_line=' '.join(words),exact_target=target,state=state,causes=causes))
 for name,(axis,value) in candidates.items():
  observed=state.get(axis,'UNKNOWN')
  if not target: status='NO_EXACT_TARGET'
  elif observed=='UNKNOWN': status='UNKNOWN'
  elif observed==value: status='MATCH'
  elif {observed,value} in ({'wet','dry'},{'cold','warm'},{'cold','hot'}): status='CONFLICT'
  else: status='DIFFERENT_NOT_OPPOSED'
  rows.append(dict(edition=ed,candidate=name,axis=axis,predicted=value,modeled_state=observed,status=status,row_status='recorded'))
with (D/'PREDICTIONS.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
priority=[c for c in candidates if all(r['status']=='MATCH' for r in rows if r['candidate']==c and r['edition'] in ('ZL3b','IT2a'))]
result=dict(evidence=evidence,conditional_priority=priority,physical_loci=1,independent_meaning_confirmations=0,unknown_is_not_refutation=True,complete_paragraph_source=s['context'])
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(conditional_priority=priority,predictions=len(rows))))
