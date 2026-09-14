from pathlib import Path
import json,csv
D=Path(__file__).parent
rows=[]
for p in json.loads((D/'PARAGRAPHS.json').read_text()):
 last=None
 for l in p['lines']:
  for i,w in enumerate(l['words']):
   if w not in {'qotaiin','shey','qotchy'}:continue
   r=dict(edition=p['edition'],paragraph=p['id'],at=l['source_ids'][i],word=w,argument=l['words'][i+1] if i+1<len(l['words']) else '',linked_harm=last if w=='qotchy' and last else '',status='HARM' if w!='qotchy' else 'LINKED' if last else 'MISSING_PRIOR_HARM');rows.append(r)
   if w!='qotchy':last=r['at']
with (D/'PARAGRAPH_RELATIONS.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
