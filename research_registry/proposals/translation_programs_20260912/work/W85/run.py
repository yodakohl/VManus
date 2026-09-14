from pathlib import Path
import json,csv,hashlib,collections
D=Path(__file__).resolve().parent.relative_to(Path.cwd());S=D.parent/'W84';ps=[p for p in json.loads((S/'PARAGRAPHS.json').read_text()) if p['page'] in {'f15r','f53v'}];lex=json.loads((S/'LEXICON.json').read_text())|json.loads((S/'MODELS.json').read_text())['1'];events=[r for r in csv.DictReader((S/'EVENTS.tsv').open(),delimiter='\t') if r['model']=='1' and (r['edition'],r['paragraph']) in {(p['edition'],p['id']) for p in ps}];out=[];al=[];md=['# Ganze f15r/f53v Arbeitslesungen','Unveränderte W84-Modell1-Hypothese. Offene Wörter in Klammern, keine ergänzten Verben oder Stoffe.'];profiles=[]
for p in ps:
 flat=[(w,at) for l in p['lines'] for w,at in zip(l['words'],l['source_ids'])];idx={at:i for i,(w,at) in enumerate(flat)};cut=next(i for i,(w,at) in enumerate(flat) if w=='cthy');ev=[r for r in events if r['edition']==p['edition'] and r['paragraph']==p['id']];heads=[dict(word=w,at=at,index=i) for i,(w,at) in enumerate(flat) if lex.get(w,{}).get('kind')=='MATERIAL'];pe=[]
 for r in ev:
  q=r|dict(phase='before_cthy' if idx[r['at']]<cut else 'from_cthy',intervening_groups=idx[r['at']]-idx[r['carrier']]-1 if r['carrier'] else '')
  out.append(q);pe.append(q)
 profiles.append(dict(edition=p['edition'],paragraph=p['id'],groups=len(flat),first_cthy=flat[cut][1],material_mentions=heads,cthy_mentions=sum(w=='cthy' for w,at in flat),phases={phase:dict(counts=dict(collections.Counter(r['kind'] for r in pe if r['phase']==phase)),ordered=[dict(word=r['word'],kind=r['kind'],carrier=r['carrier_word'],input=r['input']) for r in pe if r['phase']==phase]) for phase in ['before_cthy','from_cthy']},max_intervening=max((r['intervening_groups'] for r in pe if r['kind'] in {'VALUE','QUALITY'} and r['intervening_groups']!=''),default=None)))
 md+=['\n## '+p['edition']+' '+p['id']]
 for l in p['lines']:
  gg=[]
  for w,at in zip(l['words'],l['source_ids']):
   v={'dair':'A','dain':'B','daiin':'C'}.get(w);g='Masse '+v+'·Uₚ' if v else lex.get(w,{}).get('meaning','⟦'+w+'⟧');gg.append(g);al.append(dict(edition=p['edition'],paragraph=p['id'],at=at,word=w,gloss=g))
  md+=['\n'+l['locus']+' `'+ ' '.join(l['words'])+'`','\n'+' · '.join(gg)]
for name,rows in [('ALIGNMENT.tsv',al),('EVENTS.tsv',out)]:
 with (D/name).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');wr.writeheader();wr.writerows(rows)
(D/'READING.md').write_text('\n'.join(md)+'\n');(D/'PROFILES.json').write_text(json.dumps(profiles,ensure_ascii=False,indent=2)+'\n');(D/'PARAGRAPHS.json').write_text(json.dumps(ps,ensure_ascii=False,separators=(',',':'))+'\n');(D/'SOURCE_HASHES.json').write_text(json.dumps({str(S/n):hashlib.sha256((S/n).read_bytes()).hexdigest() for n in ['PARAGRAPHS.json','LEXICON.json','MODELS.json','EVENTS.tsv']},indent=2)+'\n')
print(json.dumps([dict(edition=p['edition'],paragraph=p['paragraph'],groups=p['groups'],cthy=p['cthy_mentions'],heads=[h['word'] for h in p['material_mentions']],max_intervening=p['max_intervening'],phases={k:v['counts'] for k,v in p['phases'].items()}) for p in profiles]))
