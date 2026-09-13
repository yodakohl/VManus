import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path(__file__).parent;S=json.loads((D/'SPEC.json').read_text());B=Path(S['base'])
def read(p):return list(csv.DictReader(Path(p).open(),delimiter='\t'))
for p,h in S['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
raw=read(S['source']);assert len(raw)==1045 and all(not r['locus'].startswith('f84') for r in raw)
targets=[r for r in raw if r['form']=='ysheol']
def tab(n,rr,cols):
 with (D/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
predictions=[];histories=[];bindings=[]
for stream in S['streams']:
 flat=read(B/(stream+'_SOURCE_FLAT.tsv'));args=read(B/(stream+'_ARGUMENTS.tsv'));events=read(B/(stream+'_EVENTS.tsv'))
 assert [(r['id'],r['form']) for r in flat]==[(r['id'],r['form']) for r in raw]
 for target in targets:
  para=target['paragraph'];ts=[r for r in flat if r['paragraph']==para];i=next(i for i,r in enumerate(ts) if r['id']==target['id']);previous=ts[i-1]
  assert previous['role']=='ACTION'
  for grammar in ['B','J','M']:
   a=next(a for a in args if a['paragraph']==para and a['grammar']==grammar and a['operation']==previous['id'])
   patient=a['patient'];p=next((r for r in ts if r['id']==patient),None)
   eligible=p is not None and int(p['offset'])<int(target['offset'])
   for model in ['D','H']:
    for timing in ['O','I']:
     world='|'.join([stream,grammar,model,timing]);es=[e for e in events if e['paragraph']==para and e['grammar']==grammar and e['model']==model and e['timing']==timing]
     before=[e for e in es if int(e['order'])<int(target['offset'])];after=[e for e in es if int(e['order'])>=int(target['offset'])]
     assert before+after==es
     ae=[e for e in before if e['location']==previous['id'] and e['kind']=='ACTION'];assert len(ae)==1
     obj=ae[0]['object'] if eligible else ''
     prior=[e for e in before if obj and e['object']==obj];later=[e for e in after if obj and e['object']==obj]
     state=json.loads(prior[-1]['after']) if prior else {}
     bindings.append(dict(world=world,target=target['id'],previous_action=previous['id'],patient=patient,patient_form=a['patient_form'],object=obj,rule='RESULT_OF_IMMEDIATELY_PRECEDING_WRITTEN_ACTION',debts=a['debts'],prior_state=json.dumps(state,sort_keys=True),later_events=len(later)))
     for side,ee in [('PRIOR',prior),('LATER',later)]:
      for e in ee:histories.append(dict(world=world,target=target['id'],side=side,**{k:v for k,v in e.items() if k!='row_status'}))
     for name,(axis,value) in S['candidates'].items():
      observed=state.get('PHYSICAL:'+axis)
      if not eligible or not obj:status='MISSING_PATIENT'
      elif observed is None:status='UNKNOWN'
      elif observed==value:status='MATCH'
      elif axis=='moisture' or 'cold' in [observed,value]:status='CONFLICT'
      else:status='DIFFERENT_NOT_OPPOSED'
      predictions.append(dict(world=world,target=target['id'],candidate=name,axis=axis,predicted=value,observed=observed or 'UNKNOWN',status=status,patient=patient,object=obj,state_source=next((e['location'] for e in reversed(prior) if json.loads(e['after']).get('PHYSICAL:'+axis)==observed and json.loads(e['before']).get('PHYSICAL:'+axis)!=observed),'NONE'),state_snapshot_source=prior[-1]['location'] if prior else 'NONE',initial_state_added=False,independent_confirmation_capacity=0))
tab('PREDICTIONS.tsv',predictions,list(predictions[0]));tab('BINDINGS.tsv',bindings,list(bindings[0]));tab('HISTORIES.tsv',histories,list(histories[0]))
summary={k:dict(Counter(r['status'] for r in predictions if r['candidate']==k)) for k in S['candidates']}
md=['# W44 — fünf vollständige Zielabsatz-Lesungen','','Nur ysheol erhält die jeweilige prospektive Zustandsbedeutung. W38 bleibt unverändert; alle anderen 16Absätze siehe dort. Keine bestätigte Übersetzung.','']
gloss=dict(wet='feucht [Momentzustand]',dry='trocken [Momentzustand]',cold='kalt [Momentzustand]',warm='warm [Momentzustand]',hot='heiß [Momentzustand]')
for stream in S['streams']:
 al=read(B/(stream+'_ALIGNMENT.tsv'))
 for para in dict.fromkeys(t['paragraph'] for t in targets):
  md+=['## '+stream+' / '+para,'']
  for line in dict.fromkeys(r['locus'] for r in raw if r['paragraph']==para):
   rr=[r for r in al if r['paragraph']==para and r['locus']==line];md += [line+': `'+ ' '.join(r['raw'] for r in rr)+'`','']
   for candidate in S['candidates']:
    md += [candidate+': '+' · '.join(gloss[candidate] if r['raw']=='ysheol' else ('D:'+r['D']+' / H:'+r['H'] if r['D']!=r['H'] else r['H']) for r in rr),'']
(D/'READING.md').write_text('\n'.join(md)+'\n')
result=dict(groups_searched=len(raw),paragraphs_searched=len({r['paragraph'] for r in raw}),target_occurrences=len(targets),worlds=len(bindings),predictions=len(predictions),status_by_candidate=summary,known_seed_meanings_confirmed=False,independent_confirmation_capacity=0,held_access=False)
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
