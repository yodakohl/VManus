from pathlib import Path
import csv,json,collections
D=Path(__file__).parent
ps=[p for p in json.loads((D.parent/'W63/PARAGRAPHS.json').read_text()) if p['page']=='f75v']
ev=list(csv.DictReader((D.parent/'W69/EVENTS.tsv').open(),delimiter='\t'))
eff=json.loads((D.parent/'W09/SPEC.json').read_text())['effects'];features=json.loads((D.parent/'W03/SPEC.json').read_text())['features']
initial={f['form']:f['value'] for f in features if f['axis']=='thermal' and f['kind']=='PROCESSED_NOMINAL'}
rows=[];md=['# Vollständiger Absatz und thermische Projektion','','Alle Wortwerte und Objektbezüge hypothetisch. Keine vollständige Zustandsprüfung.','']
for p in ps:
 assert not p['page'].startswith('f84')
 for m in ['NRC','AMV']:
  state={};ee={e['at']:e for e in ev if e['edition']==p['edition'] and e['paragraph']==p['id'] and e['model']==m}
  md+=['## '+p['edition']+' '+m,'']
  for l in p['lines']:
   md += [l['locus']+' `'+ ' '.join(l['words'])+'`','']
   for sid,w in zip(l['source_ids'],l['words']):
    if w in initial:state[sid]=initial[w]
    if sid not in ee:continue
    e=ee[sid];effect=eff.get(w,{});before=state.get(e['patient'],'UNKNOWN');after=before
    status='NOT_A_THERMAL_ACTION'
    if e['kind']=='ACTION' and effect.get('axis')=='thermal':
     status='NEGATIVE_NOT_APPLIED' if e['polarity']=='NEGATIVE' else 'MISSING_PATIENT' if not e['patient'] else 'ASSIGNED'
     if status=='ASSIGNED':after=effect['value'];state[e['patient']]=after
    r=dict(edition=p['edition'],model=m,at=sid,word=w,kind=e['kind'],patient=e['patient'],patient_word=e['patient_word'],polarity=e['polarity'],before=before,after=after,status=status,hot_to_warm=str(status=='ASSIGNED' and before=='hot' and after=='warm'))
    rows.append(r);md+=['- '+sid+' '+w+' → '+(e['patient_word'] or 'OBJEKT FEHLT')+': '+status+' '+before+' → '+after]
   md+=['']
with (D/'TRACE.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
(D/'READING.md').write_text('\n'.join(md)+'\n')
r=dict(predicate_rows=len(rows),status_counts=dict(collections.Counter(x['status'] for x in rows)),hot_to_warm=[x for x in rows if x['hot_to_warm']=='True'],meaning_confirmed=False,physical_validation=False,full_state_replay=False)
(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
