from pathlib import Path
import csv,json,itertools
D=Path(__file__).parent
ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text())
lex={r['form']:r['hypothesis'] for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')}
lex.update(sheedy='Zubereitung A',shey='Zubereitung B')
rows=[];targets=[];models=[];md=['# Acht vollständige hypothetische Interlinearentwürfe','', 'Keine ausgeführte Syntax oder Negationsbindung. Punkte trennen Wortglossen, keine Sätze. Alle Werte unbestätigt.','']
for s,o,c in itertools.product('NA','RM','CV'):
 model=s+o+c;gl=dict(lex,sheckhy='Mischung' if s=='N' else 'vermische',ol='mit' if o=='R' else 'Zubereitungsposten',chey='prüfe' if c=='C' else 'nicht [Bereich offen]')
 models.append(dict(model=model,sheckhy=gl['sheckhy'],ol=gl['ol'],chey=gl['chey']))
 for p in ps:
  assert not p['page'].startswith('f84')
  md+=['## '+model+' / '+p['edition']+' / '+p['id'],'']
  for line in p['lines']:
   out=[]
   for i,(sid,w) in enumerate(zip(line['source_ids'],line['words'])):
    v=gl.get(w,'⟦'+w+'⟧');out.append(v)
    rows.append(dict(model=model,edition=p['edition'],paragraph=p['id'],at=sid,word=w,hypothesis=v))
    if w=='sheckhy':
     ws=line['words'][max(0,i-1):i+2]
     targets.append(dict(model=model,edition=p['edition'],at=sid,raw=' '.join(ws),hypothesis=' · '.join(gl.get(x,'⟦'+x+'⟧') for x in ws)))
   md += [line['locus']+' `'+ ' '.join(line['words'])+'`','', ' · '.join(out),'']
for name,data in [('CANDIDATES.tsv',models),('ALIGNMENT.tsv',rows),('TARGETS.tsv',targets)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]),delimiter='\t');w.writeheader();w.writerows(data)
(D/'READINGS.md').write_text('\n'.join(md)+'\n')
(D/'RESULT.json').write_text(json.dumps(dict(models=8,paragraph_readings=len(ps),physical_target_loci=5,target_rows=len(targets),alignment_rows=len(rows),selected=None,scope_execution=False,meaning_confirmed=False,independent_confirmation_capacity=0),indent=2)+'\n')
