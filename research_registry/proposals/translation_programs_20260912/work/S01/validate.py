import csv,json,hashlib
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[4]
def read(n):return list(csv.DictReader((H/n).open(),delimiter='\t'))
manifest=json.loads((H/'SOURCE.json').read_text())
for f in manifest['files']:assert hashlib.sha256((R/f['path']).read_bytes()).hexdigest()==f['sha256']
lines=list(csv.DictReader((R/manifest['files'][0]['path']).open(),delimiter='\t'));raw=[]
for line in lines:
 assert line['page']=='f83r'
 raw += [(line['record_id'],line['locus'],line['locus']+':'+str(n),w) for n,w in enumerate(line['zl3b_line'].split(),1)]
assert len(raw)==341 and len(lines)==51
N={'shedy','lchedy','qokeey','shckhedy'};ops={'qokeedy','qokedy'}
keys=['record','locus','at','word'];assert [tuple(x[k] for k in keys) for x in read('INPUT.tsv')]==raw
index={x[2]:i for i,x in enumerate(raw)}
def prev(i):return next((j for j in range(i-1,-1,-1) if raw[j][0]==raw[i][0] and raw[j][3] in N),None)
def following(i):
 stop=next((j for j in range(i+1,len(raw)) if raw[j][0]!=raw[i][0] or raw[j][3] in ops),len(raw))
 return [j for j in range(i+1,stop) if raw[j][3] in N]
def pos(i):return raw[i][2] if i is not None else 'NONE'
splits={i:(prev(i),following(i)[:2]) for i,x in enumerate(raw) if x[3]=='qokeedy'}
heats={i:prev(i) for i,x in enumerate(raw) if x[3]=='chedy'}
observations={i:prev(i) for i,x in enumerate(raw) if x[3]=='sheey'}
claims={i:next(iter(following(i)),None) for i,x in enumerate(raw) if x[3]=='qokedy'}
assert len(splits)==6 and len(heats)==14 and len(observations)==1 and len(claims)==13
for row,(i,(p,cs)) in zip(read('SPLITS.tsv'),splits.items()):
 assert row['at']==pos(i) and row['input']==pos(p) and row['children']==(','.join(pos(c) for c in cs) or 'NONE')
 assert row['status']==('COMPLETE' if p is not None and len(cs)==2 else 'MISSING_ROLES')
summary={}
for v in ['F','L','U']:
 a=read('ALIGNMENT_'+v+'.tsv');assert [tuple(x[k] for k in keys) for x in a]==raw
 for row in a:assert row['word']+' → '+row['render'] in (H/('READING_'+v+'.md')).read_text()
 expected=[];obsrows=read('OBSERVATIONS_'+v+'.tsv')
 for row,(o,p) in zip(obsrows,observations.items()):
  licenses=[]
  for s,(parent,children) in splits.items():
   if parent is None or len(children)!=2 or children[-1]>=o or raw[s][0]!=raw[o][0]:continue
   chosen=children[0] if v=='F' else children[1] if v=='L' else None
   if p==chosen and not any(chosen<h<o and hp==p for h,hp in heats.items()):licenses.append((s,parent))
  assert row['sample_splits']==(','.join(pos(s) for s,p in licenses) or 'NONE')
  assert row['parent_mentions']==(','.join(pos(p) for s,p in licenses) or 'NONE')
 for i,target in claims.items():
  direct=[];sample=[]
  for o,p in observations.items():
   if o>=i or raw[o][0]!=raw[i][0] or target is None or p is None:continue
   if raw[p][3]==raw[target][3] and not any(o<h<i and hp==p for h,hp in heats.items()):direct.append(o)
   for s,(parent,children) in splits.items():
    if v=='U' or parent is None or len(children)!=2 or children[-1]>=o or raw[s][0]!=raw[o][0]:continue
    chosen=children[0] if v=='F' else children[1]
    if chosen!=p or raw[parent][3]!=raw[target][3]:continue
    if any(p<h<o and hp==p for h,hp in heats.items()):continue
    if any(o<h<i and hp in {p,parent} for h,hp in heats.items()):continue
    sample.append((o,s,parent))
  status='MISSING_TARGET' if target is None else 'SUPPORTED_DIRECT' if direct else 'SUPPORTED_SAMPLE' if sample else 'UNSUPPORTED'
  expected.append((pos(i),pos(target),status,','.join(pos(o) for o,s,p in sample) or 'NONE'))
 actual=read('CLAIMS_'+v+'.tsv');assert [(r['at'],r['target'],r['status'],r['sample_observations']) for r in actual]==expected
 summary[v]={'claims':dict(Counter(x['status'] for x in actual)),'observations':dict(Counter(x['status'] for x in obsrows))}
res=json.loads((H/'RESULT.json').read_text());assert res['variants']==summary
assert res['hypothetical_positions']==65 and res['open_positions']==276
assert [(x['at'],x['target']) for x in read('CLAIMS_L.tsv') if x['status']=='SUPPORTED_SAMPLE']==[('f83r.28:4','f83r.28:5')]
out={'status':'PASS','groups_per_reading':341,'readings':3,'claim_rows':39,'split_rows':6,'heat_rows':14,'observation_rows':3,'supported_parent_inference':'L f83r.28:4 only','scope':'independent bounded-source consequences, not semantic truth or global mass balance'}
(H/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
