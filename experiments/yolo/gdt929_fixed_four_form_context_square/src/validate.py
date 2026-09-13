from pathlib import Path
import json,collections,re
D=Path(__file__).resolve().parents[1]
import hashlib
for p,h in json.loads((D/'PREREG_LOCK.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
s=json.loads((D/'src/SPEC.json').read_text());expected=[];groups=collections.Counter()
for p,h in s['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
allow=json.loads(Path(s['allow_source']).read_text())['allowed_selectors']
for p in s['sources']:
 d=json.loads(Path(p).read_text());cols=d['group_columns']
 for line in d['lines']:
  m=line['metadata'];assert m['page'] in allow and not m['page'].startswith('f84')
  g=[dict(zip(cols,x)) for x in line['groups']];w=[x['ivtff_group_raw'] for x in g];groups[m['edition']]+=len(w)
  for i,x in enumerate(g):
   if w[i] not in s['forms']:continue
   frame=None
   if i>0 and i+1<len(g):
    triple=g[i-1:i+2];idx=[int(t['source_group_index']) for t in triple]
    chars=all(t['ivtff_group_raw'].isascii() and t['ivtff_group_raw'].isalpha() and t['ivtff_group_raw'].islower() for t in (triple[0],triple[2]))
    seams=[triple[0]['right_separator'],triple[1]['left_separator'],triple[1]['right_separator'],triple[2]['left_separator']]
    if chars and idx==list(range(idx[0],idx[0]+3)) and set(seams)=={'DEFINITE_SPACE'}:frame=[w[i-1],w[i+1]]
   expected.append(dict(edition=m['edition'],page=m['page'],leaf=int(re.match('f([0-9]+)',m['page'])[1]),locus=m['locus'],id=x['source_group_id'],word=w[i],frame=frame,raw_line=w))
assert expected==json.loads((D/'artifacts/OCCURRENCES.json').read_text())
frames=json.loads((D/'artifacts/FRAMES.json').read_text());keys={(r['edition'],*r['frame']) for r in expected if r['frame']}
want=[]
for ed,l,r in sorted(keys):
 rows=[x for x in expected if x['edition']==ed and x['frame']==[l,r]];forms=sorted({x['word'] for x in rows})
 if len(forms)<2:continue
 edges=[]
 for a,b in s['edges']:
  la={x['leaf'] for x in rows if x['word']==a};lb={x['leaf'] for x in rows if x['word']==b}
  if la and lb:edges.append(dict(forms=[a,b],cross_leaf=len(la|lb)>1))
 want.append(dict(edition=ed,frame=[l,r],forms=forms,edges=edges,square=len(forms)==4,witnesses=rows))
assert frames==want
v=json.loads((D/'artifacts/RESULT.json').read_text());assert v['groups']==dict(groups)
for ed,counts in v['counts'].items():assert counts=={w:sum(x['edition']==ed and x['word']==w for x in expected) for w in s['forms']}
assert v['occurrences']==len(expected) and v['eligible_frames']==sum(x['frame'] is not None for x in expected)
assert v['matched_frames']==len(want) and v['squares']==sum(x['square'] for x in want)
assert v['edge_frames']==sum(len(x['edges']) for x in want) and v['cross_leaf_edge_frames']==sum(e['cross_leaf'] for x in want for e in x['edges'])
out=dict(status='PASS',coverage='independent full occurrence/frame reconstruction; preregistration integrity',meaning_validated=False)
(D/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
