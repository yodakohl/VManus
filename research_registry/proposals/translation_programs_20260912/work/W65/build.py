from pathlib import Path
import json,csv,collections
D=Path(__file__).parent;ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text());rows=[]
for p in ps:
 for l in p['lines']:
  for i,w in enumerate(l['words']):
   if w not in ('okain','solchey'):continue
   rows.append(dict(edition=p['edition'],paragraph=p['id'],at=l['source_ids'][i],word=w,left=l['words'][i-1] if i else 'LINE_START',right=l['words'][i+1] if i+1<len(l['words']) else 'LINE_END',full_line=' '.join(l['words'])))
with (D/'ALL_OCCURRENCES.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
res=dict(counts={ed:{w:sum(r['edition']==ed and r['word']==w for r in rows) for w in ('okain','solchey')} for ed in ('ZL3b','IT2a')},solchey_frames=[r for r in rows if r['word']=='solchey'],qokain_okain=[r for r in rows if r['word']=='okain' and r['left']=='qokain'],meaning_confirmations=0,new_grammar=False)
(D/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
