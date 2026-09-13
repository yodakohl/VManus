from pathlib import Path
import json,hashlib,re,collections
D=Path(__file__).resolve().parents[1]
s=json.loads((D/'src/SPEC.json').read_text())
for p,h in s['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors'])
occ=[];counts=collections.Counter();den=collections.Counter();frames=collections.defaultdict(list)
for p in s['sources']:
 d=json.loads(Path(p).read_text())
 for line in d['lines']:
  m=line['metadata'];assert m['page'] in allow and not m['page'].startswith('f84')
  ed=m['edition'];gs=[dict(zip(d['group_columns'],g)) for g in line['groups']];words=[g['ivtff_group_raw'] for g in gs];den[ed]+=len(gs)
  for i,word in enumerate(words):
   if word not in s['forms']:continue
   counts[ed,word]+=1
   good=0<i<len(gs)-1 and all(re.fullmatch('[a-z]+',words[j]) for j in [i-1,i+1])
   if good:good=all(gs[a]['right_separator']==gs[b]['left_separator']=='DEFINITE_SPACE' and int(gs[b]['source_group_index'])==int(gs[a]['source_group_index'])+1 for a,b in [(i-1,i),(i,i+1)])
   r=dict(edition=ed,page=m['page'],leaf=int(re.match(r'f(\d+)',m['page'])[1]),locus=m['locus'],id=gs[i]['source_group_id'],word=word,frame=[words[i-1],words[i+1]] if good else None,raw_line=words)
   occ.append(r)
   if good:frames[ed,*r['frame']].append(r)
matched=[]
for (ed,left,right),rows in sorted(frames.items()):
 present=sorted({r['word'] for r in rows})
 if len(present)<2:continue
 edges=[]
 for a,b in s['edges']:
  if a in present and b in present:edges.append(dict(forms=[a,b],cross_leaf=any(x['leaf']!=y['leaf'] for x in rows if x['word']==a for y in rows if y['word']==b)))
 matched.append(dict(edition=ed,frame=[left,right],forms=present,edges=edges,square=len(present)==4,witnesses=rows))
out=dict(counts={ed:{w:counts[ed,w] for w in s['forms']} for ed in sorted(den)},groups=dict(den),occurrences=len(occ),eligible_frames=sum(r['frame'] is not None for r in occ),matched_frames=len(matched),squares=sum(r['square'] for r in matched),edge_frames=sum(len(r['edges']) for r in matched),cross_leaf_edge_frames=sum(e['cross_leaf'] for r in matched for e in r['edges']),meanings_confirmed=0)
for name,data in [('OCCURRENCES.json',occ),('FRAMES.json',matched),('RESULT.json',out)]: (D/'artifacts'/name).write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(out,indent=2))
