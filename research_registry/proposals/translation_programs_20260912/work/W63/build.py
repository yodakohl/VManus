from pathlib import Path
import json,csv
D=Path(__file__).parent
src=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());loci={'f75v.44','f80r.32','f116r.42'}
ps=[dict(edition=ed,**p) for ed,pp in src.items() for p in pp if loci & {l['locus'] for l in p['lines']}]
lex={r['form']:r for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')};lex.update(sheedy={'hypothesis':'Zubereitung A'},shey={'hypothesis':'Zubereitung B'})
rows=[];targets=[];counts={};md=['# Vollständige direkte Vergleichsabsätze','', 'Alle deutschen Werte hypothetisch; offene Wörter bleiben ⟦…⟧. Keine Argumentbindung durch bloße Wortfolge.','']
for p in ps:
 for l in p['lines']:
  for i,w in enumerate(l['words']):
   if w=='sheckhy':targets.append(dict(edition=p['edition'],paragraph=p['id'],at=l['source_ids'][i],left=l['words'][i-1] if i else 'BOUNDARY',right=l['words'][i+1] if i+1<len(l['words']) else 'BOUNDARY',direct_qokain=i+1<len(l['words']) and l['words'][i+1]=='qokain',full_line=' '.join(l['words'])))
 for model,gloss in [('N','Mischung'),('A','vermische')]:
  total=known=0;md+=['## '+p['edition']+' '+p['id']+' / '+model,'']
  for l in p['lines']:
   out=[]
   for sid,w in zip(l['source_ids'],l['words']):
    v=gloss if w=='sheckhy' else lex[w]['hypothesis'] if w in lex else '⟦'+w+'⟧';known+=w in lex or w=='sheckhy';total+=1
    rows.append(dict(edition=p['edition'],paragraph=p['id'],model=model,at=sid,word=w,hypothesis=v));out.append(v)
   md+=[l['locus']+' `'+ ' '.join(l['words'])+'`','', ' · '.join(out),'']
  counts[p['edition']+'|'+p['id']+'|'+model]=dict(total=total,assumed=known,open=total-known)
for name,rs in [('ALIGNMENT.tsv',rows),('ALL_SHECKHY.tsv',targets)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter='\t');w.writeheader();w.writerows(rs)
(D/'READINGS.md').write_text('\n'.join(md)+'\n');(D/'PARAGRAPHS.json').write_text(json.dumps(ps,indent=2)+'\n')
res=dict(counts=counts,paragraphs=len(ps),target_reading_positions=len(targets),direct_qokain_reading_positions=sum(r['direct_qokain'] for r in targets),alignment_rows=len(rows),selected=None,working_priority="N_CONDITIONAL_MANUAL",meanings_confirmed=0)
(D/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res));print(json.dumps(targets,indent=2))
