from pathlib import Path
import json,csv,collections
D=Path(__file__).parent
ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text());events=list(csv.DictReader((D.parent/'W69/EVENTS.tsv').open(),delimiter='\t'));fx=json.loads((D.parent/'W09/SPEC.json').read_text())['effects'];features={f['form']:f for f in json.loads((D.parent/'W03/SPEC.json').read_text())['features'] if f['kind']=='STANDALONE'}
rows=[];md=['# Alle Absätze und ausgeschriebenen Qualitätsbezüge','','Wortwerte, Polarität und Materialbezüge hypothetisch.','']
for p in ps:
 flat=[(sid,w) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])];pos={sid:i for i,(sid,w) in enumerate(flat)}
 for m in ['NRC','AMV']:
  es=[e for e in events if e['edition']==p['edition'] and e['paragraph']==p['id'] and e['model']==m];qr=[]
  for e in es:
   if e['kind']!='QUALITY':continue
   f=features.get(e['word']);actions=[a for a in es if a['kind']=='ACTION' and a['polarity']=='POSITIVE' and a['patient'] and a['patient']==e['patient'] and fx.get(a['word'],{}).get('axis')=='thermal'];before=[a for a in actions if pos[a['at']]<pos[e['at']]];after=[a for a in actions if pos[a['at']]>pos[e['at']]];a=before[-1] if before else None;b=after[0] if after else None
   status='NO_STANDALONE_FEATURE' if not f else 'NONTHERMAL_FEATURE' if f['axis']!='thermal' else 'MISSING_PATIENT' if not e['patient'] else 'NO_PRIOR_THERMAL_ACTION' if not a else 'WRITTEN_ENDPOINT_CANDIDATE'
   relation='NOT_COMPARED'
   if status=='WRITTEN_ENDPOINT_CANDIDATE':relation=('SAME_VALUE' if fx[a['word']]['value']==f['value'] else 'DIFFERENT_VALUE') if e['polarity']=='POSITIVE' else ('EXCLUDES_ASSIGNED_VALUE' if fx[a['word']]['value']==f['value'] else 'DIFFERENT_VALUE_NEGATED')
   r=dict(model=m,edition=p['edition'],paragraph=p['id'],at=e['at'],word=e['word'],polarity=e['polarity'],patient=e['patient'],patient_word=e['patient_word'],axis=f['axis'] if f else '',value=f['value'] if f else '',status=status,prior_action=a['at'] if a else '',prior_word=a['word'] if a else '',prior_value=fx[a['word']]['value'] if a else '',next_action=b['at'] if b else '',next_word=b['word'] if b else '',relation=relation,intervening_before=' '.join(w for sid,w in flat[pos[a['at']]+1:pos[e['at']]]) if a else '',intervening_after=' '.join(w for sid,w in flat[pos[e['at']]+1:pos[b['at']]]) if b else '')
   rows.append(r);qr.append(r)
  md+=['## '+p['edition']+' '+m+' '+p['id'],'']
  for l in p['lines']:
   md += [l['locus']+' `'+ ' '.join(l['words'])+'`','']
   for r in qr:
    if r['at'] in l['source_ids']:md+=['- '+r['at']+' '+r['word']+': '+r['status']+'; '+r['polarity']+' '+r['value']+'; Material '+(r['patient'] or 'FEHLT')+'; vorher '+(r['prior_action'] or 'keine thermische Aktion an dieser Nennung')+'; danach '+(r['next_action'] or 'keine thermische Aktion an dieser Nennung')]
   md+=['']
with (D/'QUALITIES.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
(D/'READING.md').write_text('\n'.join(md)+'\n');r=dict(quality_rows=len(rows),statuses=dict(collections.Counter(x['status'] for x in rows)),endpoint_candidates=sum(x['status']=='WRITTEN_ENDPOINT_CANDIDATE' for x in rows),meaning_confirmed=False)
(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));print(json.dumps([x for x in rows if x['axis']=='thermal'],ensure_ascii=False))
