import csv,json,hashlib
from pathlib import Path
D=Path(__file__).parent;S=json.loads((D/'SPEC.json').read_text());B=Path(S['base'])
read=lambda p:list(csv.DictReader(Path(p).open(),delimiter='\t'))
for p,h in S['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
raw=read(S['source']);pp=read(D/'PREDICTIONS.tsv');bb=read(D/'BINDINGS.tsv');hh=read(D/'HISTORIES.tsv')
targets=[r for r in raw if r['form']=='ysheol'];assert len(raw)==1045 and len(targets)==1
assert len(bb)==24 and len(pp)==120
checks=0
for b in bb:
 stream,g,m,t=b['world'].split('|');target=next(r for r in targets if r['id']==b['target'])
 es=[e for e in read(B/(stream+'_EVENTS.tsv')) if (e['paragraph'],e['grammar'],e['model'],e['timing'])==(target['paragraph'],g,m,t)]
 ar=read(B/(stream+'_ARGUMENTS.tsv'));a=next(a for a in ar if a['grammar']==g and a['operation']==b['previous_action'])
 assert a['patient']==b['patient']=='f21r.12:2' and a['patient_form']=='chor'
 assert a['operation']=='f21r.12:3' and a['form']=='sheey'
 ae=next(e for e in es if e['location']==a['operation'] and e['kind']=='ACTION')
 assert ae['object']==b['object'] and int(ae['order'])<int(target['offset'])
 relevant=[e for e in es if e['object']==b['object']]
 expected_prior=[e for e in relevant if int(e['order'])<int(target['offset'])];expected_later=[e for e in relevant if int(e['order'])>=int(target['offset'])]
 for side,expected in [('PRIOR',expected_prior),('LATER',expected_later)]:
  actual=[e for e in hh if e['world']==b['world'] and e['side']==side]
  assert [{k:e[k] for k in es[0]} for e in actual]==expected
 state={};origin={}
 # Reconstruct axis value changes rather than trusting the final snapshot.
 for e in expected_prior:
  before=json.loads(e['before']);after=json.loads(e['after'])
  for key,value in after.items():
   if before.get(key)!=value:state[key]=value;origin[key]=e['location']
 assert all(state[k]==v for k,v in json.loads(b['prior_state']).items())
 for p in [p for p in pp if p['world']==b['world']]:
  axis,value=S['candidates'][p['candidate']];obs=state.get('PHYSICAL:'+axis)
  assert p['observed']==obs and p['state_source']==origin['PHYSICAL:'+axis]
  forbidden={frozenset(['wet','dry']),frozenset(['cold','warm']),frozenset(['cold','hot'])}
  status='MATCH' if obs==value else ('CONFLICT' if frozenset([obs,value]) in forbidden else 'DIFFERENT_NOT_OPPOSED')
  assert p['status']==status;checks+=1
 assert int(b['later_events'])==len(expected_later)
text=(D/'READING.md').read_text()
for line in dict.fromkeys(r['locus'] for r in raw if r['paragraph']==targets[0]['paragraph']):assert line+': `'+ ' '.join(r['form'] for r in raw if r['locus']==line)+'`' in text
result=dict(status='PASS',bound_files=len(S['hashes']),groups_searched=len(raw),target_occurrences=len(targets),worlds=len(bb),prediction_checks=checks,history_rows=len(hh),independent_meaning_validation=False)
(D/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
