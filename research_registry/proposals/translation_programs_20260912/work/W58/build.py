from pathlib import Path
import csv,json
D=Path(__file__).parent
ps=[p for p in json.loads((D.parent/'W56/PARAGRAPHS.json').read_text()) if p['page']=='f75v']
lex={r['form']:r for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')}
lex.update(sheedy=dict(hypothesis='Zubereitung A',role='MATERIAL'),shey=dict(hypothesis='Zubereitung B',role='MATERIAL'))
rows=[];events=[];md=['# W58 — alle Quellgruppen, neue Rollen explizit','', 'Alle deutschen Werte sind Hypothesen; ⟦…⟧ offen. patient ist nur der unter der festen Linksregel angesetzte Gegenstand.',''];counts={}
for p in ps:
 for model in ['G','S']:
  ed=p['edition'];last=None;lastid=None;known=0;total=0;md+=['## '+ed+' / '+model,'']
  for l in p['lines']:
   out=[]
   for word,sid in zip(l['words'],l['source_ids']):
    total+=1;r=lex.get(word);gloss=r['hypothesis'] if r else '⟦'+word+'⟧';known+=r is not None
    if model=='S' and word=='cheey':gloss='benetze'
    if r and r['role'] in ['MATERIAL','MATERIAL_DOSE']:last=word;lastid=sid
    if r and r['role'] in ['ACTION','ACTION_TYPED']:
     events.append(dict(edition=ed,model=model,at=sid,word=word,action=gloss,patient=last or 'MISSING',patient_at=lastid or 'MISSING',patient_gloss=lex[last]['hypothesis'] if last else 'MISSING'))
     gloss+=' [Objekt='+ (lex[last]['hypothesis'] if last else 'OFFEN')+']'
    rows.append(dict(edition=ed,model=model,at=sid,word=word,gloss=gloss,status='ASSUMPTION' if r else 'OPEN'));out.append(gloss)
   md+=[l['locus']+' `'+ ' '.join(l['words'])+'`','', ' · '.join(out),'']
  counts[ed+'_'+model]=dict(groups=total,assumed=known,open=total-known)
for name,data in [('ALIGNMENT.tsv',rows),('ACTIONS.tsv',events)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]),delimiter='\t');w.writeheader();w.writerows(data)
(D/'READINGS.md').write_text('\n'.join(md)+'\n')
res=dict(counts=counts,actions=len(events),new_assumed_forms=['sheedy','shey'],selected_model=None,meaning_confirmations=0,state_engine=False)
(D/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
for r in events:
 if r['edition']=='IT2a' and r['model']=='G':print(r)
