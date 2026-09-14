from pathlib import Path
import json,csv,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
src=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());loci={'f75v.44','f80r.32','f116r.42'}
ps=[dict(edition=ed,**p) for ed,pp in src.items() for p in pp if loci & {l['locus'] for l in p['lines']}];assert ps==json.loads((D/'PARAGRAPHS.json').read_text()) and len(ps)==6
lex={r['form']:r['hypothesis'] for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')};lex.update(sheedy='Zubereitung A',shey='Zubereitung B')
rs=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));targets=list(csv.DictReader((D/'ALL_SHECKHY.tsv').open(),delimiter='\t'));assert len(rs)==1160 and len(targets)==10
for p in ps:
 flat=[(sid,w) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])]
 for m,v in [('N','Mischung'),('A','vermische')]:
  rows=[r for r in rs if (r['edition'],r['paragraph'],r['model'])==(p['edition'],p['id'],m)]
  assert [(r['at'],r['word']) for r in rows]==flat
  for r in rows:assert r['hypothesis']==(v if r['word']=='sheckhy' else lex.get(r['word'],'⟦'+r['word']+'⟧'))
 assert [r['at'] for r in targets if (r['edition'],r['paragraph'])==(p['edition'],p['id'])]==[sid for sid,w in flat if w=='sheckhy']
v=dict(status='PASS',scope='six complete paragraphs, all target positions and1160alignedgroups',meaning_validated=False,qualitative_priority_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
