from pathlib import Path
import json,csv,collections,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text());base={r['form']:r['role'] for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')}
events=list(csv.DictReader((D/'EVENTS.tsv').open(),delimiter='\t'));scopes=list(csv.DictReader((D/'SCOPES.tsv').open(),delimiter='\t'));ec=0;sc=0
predroles={'ACTION','ACTION_TYPED','REPEAT_ACTION','REPEAT_COOL','MIX','STATE','QUALITY_VALUE'}
for m in ['NRC','AMV']:
 roles=dict(base,sheedy='MATERIAL',shey='MATERIAL',sheckhy='MATERIAL' if m=='NRC' else 'ACTION')
 if m=='AMV':roles.update(chey='NEGATION',ol='MATERIAL')
 for p in ps:
  assert not p['page'].startswith('f84')
  flat=[(sid,w) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])];positions={a:i for i,(a,w) in enumerate(flat)}
  ee=[x for x in events if x['model']==m and x['edition']==p['edition'] and x['paragraph']==p['id']]
  assert [x['at'] for x in ee]==[a for a,w in flat if roles.get(w) in predroles];ec+=len(ee)
  ss=[x for x in scopes if x['edition']==p['edition'] and x['paragraph']==p['id']] if m=='AMV' else []
  if m=='AMV':assert [x['chey'] for x in ss]==[a for a,w in flat if w=='chey']
  hits=collections.Counter()
  for s in ss:
   i=positions[s['chey']];candidates=[j for j in range(i+1,len(flat)) if flat[j][1] in {'sol','qokal'} or roles.get(flat[j][1]) in predroles];j=candidates[0] if candidates else len(flat)
   target=flat[j][0] if j<len(flat) and flat[j][1] not in {'sol','qokal'} else ''
   assert s['target']==target and s['intervening']==' '.join(w for a,w in flat[i+1:j]);hits[target]+=1;sc+=1
  for e in ee:
   i=positions[e['at']];materials=[a for a,w in flat[:i] if roles.get(w) in {'MATERIAL','MATERIAL_DOSE'}];assert e['patient']==(materials[-1] if materials else '')
   assert e['polarity']==('NEGATIVE' if hits[e['at']]%2 else 'POSITIVE')
assert ec==len(events)==135 and sc==len(scopes)==11
v=dict(status='PASS',all_predicate_events=ec,all_chey_scopes=sc,negative_events=sum(e['polarity']=='NEGATIVE' for e in events),meaning_validated=False,state_execution=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
