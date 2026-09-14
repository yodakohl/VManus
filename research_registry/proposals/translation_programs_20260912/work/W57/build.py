from pathlib import Path
import json,csv
D=Path(__file__).parent
src=json.loads((D.parent/'W56/PARAGRAPHS.json').read_text());paras=[p for p in src if p['page']=='f75v']
lex={r['form']:r for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')}
rows=[];md=['# W57 — vollständige Arbeitsfassungen','', '⟦…⟧ = ungelesen; jede deutsche Glosse ist eine unbestätigte Annahme. Aneinanderreihung bindet keine Argumente.','']
counts={}
for p in paras:
 ed=p['edition'];counts[ed]={}
 for model in ['G','S']:
  known=0;total=0
  md+=['## '+ed+' / '+model,'']
  for l in p['lines']:
   out=[]
   for word,sid in zip(l['words'],l['source_ids']):
    total+=1;r=lex.get(word);gloss=r['hypothesis'] if r else '⟦'+word+'⟧'
    if model=='S' and word=='cheey':gloss='benetze'
    known+=r is not None
    rows.append(dict(edition=ed,model=model,locus=l['locus'],source_id=sid,word=word,hypothesis=gloss,status='UNCONFIRMED_ASSUMPTION' if r else 'OPEN',origin='W57 explicit cheey synonym rival' if model=='S' and word=='cheey' else 'W02 exact whole' if r else 'NO_VALUE'))
    out.append(gloss)
   md+=[l['locus']+' `'+ ' '.join(l['words'])+'`','', ' · '.join(out),'']
  counts[ed][model]=dict(groups=total,assumed=known,open=total-known)
(D/'READINGS.md').write_text('\n'.join(md)+'\n')
with (D/'ALIGNMENT.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
r=dict(counts=counts,changed_form_only='cheey',confirmed_words=[],argument_binding_executed=False,selection=None)
(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
