import hashlib,json
from pathlib import Path
b=Path(__file__).resolve().parent;root=b.parents[4]
r=json.loads((b/'RESULT.json').read_text());raw=(root/r['source']).read_bytes()
assert hashlib.sha256(raw).hexdigest()==r['source_sha256']
assert hashlib.sha256((b/'DECISION.md').read_bytes()).hexdigest()==r['decision_sha256']
rows=json.loads((b/'TRIPLES.json').read_text());got={x['middle_id']:x for x in rows};assert len(rows)==len(got)
expected=set()
for ed,ps in json.loads(raw).items():
 if ed not in ['ZL3b','IT2a']:continue
 for p in ps:
  words=[w for l in p['lines'] for w in l['words']];ids=[i for l in p['lines'] for i in l['source_ids']]
  positions={w:[i for i,v in enumerate(words) if v==w] for w in set(words)}
  for w,pos in positions.items():
   for i in pos:
    if i+2 not in pos or words[i+1]==w:continue
    sid=ids[i+1];expected.add(sid);a=got[sid]
    assert a['x_total']==len(pos) and a['later_x']==sum(j>i+2 for j in pos)
    assert a['terminal']==(pos[-1]==i+2)
assert expected==set(got)
for ed,summary in r['summaries'].items():
 a=[x for x in rows if x['edition']==ed];target_ps={x['paragraph'] for x in a if x['middle'] in ['char','dar','sar']}
 for name,groups in summary.items():
  q=[x for x in a if (x['middle']==name if name in ['char','dar','sar'] else x['middle'] not in ['char','dar','sar'] and (name=='other' or x['paragraph'] in target_ps))]
  for kind,s in groups.items():
   z=[x for x in q if kind=='all' or (x['x_total']==2 if kind=='two_x' else x['x_total']>2)]
   assert s==dict(n=len(z),terminal=sum(x['terminal'] for x in z),paragraphs=len({x['paragraph'] for x in z}))
print('PASS: all triples, source positions and every denominator; no semantic or significance validation')
