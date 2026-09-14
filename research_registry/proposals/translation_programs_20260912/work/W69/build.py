from pathlib import Path
import csv,json,collections
D=Path(__file__).parent
ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text())
base={r['form']:r for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')}
actions={'ACTION','ACTION_TYPED','REPEAT_ACTION','REPEAT_COOL','MIX'};qualities={'STATE','QUALITY_VALUE'}
events=[];scopes=[];md=['# W69 vollständige Folge und bedingte Bezüge','','Alle Glossen und Bezüge hypothetisch. Kein Zustandsrechner.','']
for model in ['NRC','AMV']:
 lex={k:dict(v) for k,v in base.items()}
 for w,h,r in [('sheedy','Zubereitung A','MATERIAL'),('shey','Zubereitung B','MATERIAL'),('sheckhy','Mischung' if model=='NRC' else 'vermische','MATERIAL' if model=='NRC' else 'ACTION')]:lex[w]=dict(hypothesis=h,role=r)
 if model=='AMV':lex['ol']=dict(hypothesis='Zubereitungsposten',role='MATERIAL');lex['chey']=dict(hypothesis='nicht',role='NEGATION')
 for p in ps:
  assert not p['page'].startswith('f84')
  flat=[dict(at=sid,word=w,locus=l['locus']) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])]
  pred={i for i,x in enumerate(flat) if lex.get(x['word'],{}).get('role') in actions|qualities}
  neg=collections.Counter();ss=[]
  if model=='AMV':
   for i,x in enumerate(flat):
    if x['word']!='chey':continue
    j=i+1
    while j<len(flat) and flat[j]['word'] not in {'sol','qokal'} and j not in pred:j+=1
    target=j if j<len(flat) and flat[j]['word'] not in {'sol','qokal'} else None
    if target is not None:neg[target]+=1
    ss.append(dict(model=model,edition=p['edition'],paragraph=p['id'],chey=x['at'],target=flat[target]['at'] if target is not None else '',target_word=flat[target]['word'] if target is not None else '',status='TARGET' if target is not None else 'NO_TARGET',intervening=' '.join(y['word'] for y in flat[i+1:j]),stop=flat[j]['word'] if j<len(flat) else 'PARAGRAPH_END'))
  scopes+=ss;last=None;last_i=None
  md+=['## '+model+' / '+p['edition']+' / '+p['id'],'']
  local={}
  for i,x in enumerate(flat):
   role=lex.get(x['word'],{}).get('role')
   if role in {'MATERIAL','MATERIAL_DOSE'}:last=x;last_i=i
   if i not in pred:continue
   r=dict(model=model,edition=p['edition'],paragraph=p['id'],at=x['at'],word=x['word'],hypothesis=lex[x['word']]['hypothesis'],kind='ACTION' if role in actions else 'QUALITY',polarity='NEGATIVE' if neg[i]%2 else 'POSITIVE',patient=last['at'] if last else '',patient_word=last['word'] if last else '',patient_hypothesis=lex[last['word']]['hypothesis'] if last else '',status='LEFT_PATIENT_ASSUMED' if last else 'MISSING_PATIENT',intervening=' '.join(y['word'] for y in flat[last_i+1:i]) if last else '')
   events.append(r);local[x['at']]=r
  for l in p['lines']:
   md += [l['locus']+' `'+ ' '.join(l['words'])+'`','', ' · '.join(lex.get(w,{}).get('hypothesis','⟦'+w+'⟧') for w in l['words']),'']
   for sid in l['source_ids']:
    if sid in local:
     r=local[sid];md += ['- '+sid+': '+r['polarity']+' '+r['hypothesis']+' → '+(r['patient_word']+' / '+r['patient_hypothesis']+' ('+r['patient']+')' if r['patient'] else 'OBJEKT FEHLT')]
   md+=['']
for name,rs in [('EVENTS.tsv',events),('SCOPES.tsv',scopes)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter='\t');w.writeheader();w.writerows(rs)
(D/'READING.md').write_text('\n'.join(md)+'\n')
r=dict(scope_rows=len(scopes),scope_status=dict(collections.Counter(x['status'] for x in scopes)),negative_events=[x for x in events if x['polarity']=='NEGATIVE'],model_counts={m:dict(events=sum(x['model']==m for x in events),missing=sum(x['model']==m and not x['patient'] for x in events)) for m in ['NRC','AMV']},meaning_confirmed=False,state_execution=False,selected=None)
(D/'RESULT.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n');print(json.dumps(r,ensure_ascii=False))
