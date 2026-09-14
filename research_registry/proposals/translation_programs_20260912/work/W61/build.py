from pathlib import Path
import json,csv
D=Path(__file__).parent
ps=json.loads((D.parent/'W60/PARAGRAPHS.json').read_text());lex={r['form']:r for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')}
lex.update(sheedy=dict(hypothesis='Zubereitung A',role='MATERIAL'),shey=dict(hypothesis='Zubereitung B',role='MATERIAL'))
md=['# Ganze Absätze in zwei hypothetischen Fassungen','', 'Jede deutsche Glosse unbestätigt; ⟦…⟧ offen. Kein automatischer Argumentbezug aus der Wortfolge.',''];align=[];links=[];counts={}
for p in ps:
 flat=[(sid,w) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])]
 for model,value in [('R','mit'),('V','verwende')]:
  md+=['## '+p['edition']+' '+p['id']+' / '+model,''];known=0
  for l in p['lines']:
   out=[]
   for sid,w in zip(l['source_ids'],l['words']):
    r=lex.get(w);v=value if w=='qolshey' else r['hypothesis'] if r else '⟦'+w+'⟧';known+=bool(r or w=='qolshey')
    align.append(dict(edition=p['edition'],paragraph=p['id'],model=model,at=sid,word=w,hypothesis=v));out.append(v)
   md+=[l['locus']+' `'+ ' '.join(l['words'])+'`','', ' · '.join(out),'']
  counts[p['edition']+'|'+p['id']+'|'+model]=dict(total=len(flat),assumed=known,open=len(flat)-known)
 for i,(sid,w) in enumerate(flat):
  if w!='qolshey':continue
  aa=[j for j in range(i) if flat[j][1] in lex and lex[flat[j][1]]['role'] in ('ACTION','ACTION_TYPED','REPEAT_ACTION')]
  j=aa[-1] if aa else None
  links.append(dict(edition=p['edition'],at=sid,phrase=' '.join(w for _,w in flat[i:i+2]),R_previous_action=flat[j][0] if j is not None else 'MISSING',R_action_word=flat[j][1] if j is not None else 'MISSING',intervening=' '.join(w for _,w in flat[j+1:i]) if j is not None else '',unknown_intervening=sum(w not in lex for _,w in flat[j+1:i]) if j is not None else None,V_object=flat[i+1][0],status='HYPOTHETICAL_UNCONFIRMED_ATTACHMENT'))
(D/'READINGS.md').write_text('\n'.join(md)+'\n')
for name,rs in [('ALIGNMENT.tsv',align),('LINKS.tsv',links)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter='\t');w.writeheader();w.writerows(rs)
(D/'RESULT.json').write_text(json.dumps(dict(counts=counts,meaning_confirmations=0,selected=None,new_form='qolshey',state_validation=False),indent=2)+'\n')
print(json.dumps(links,indent=2));print(json.dumps(counts))
