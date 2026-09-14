import hashlib,json
from pathlib import Path
from collections import Counter,defaultdict
b=Path(__file__).resolve().parent;root=b.parents[4]
r=json.loads((b/'RESULT.json').read_text());src=(root/r['source']).read_bytes()
assert hashlib.sha256(src).hexdigest()==r['sha256']
assert hashlib.sha256((b/'DECISION.md').read_bytes()).hexdigest()==r['decision_sha256']
a=json.loads((b/'OCCURRENCES.json').read_text());actual={x['source_id']:x for x in a};assert len(actual)==len(a)
expected=set(); sym=set();frames=defaultdict(lambda:defaultdict(list))
for ed,ps in json.loads(src).items():
 if ed not in ['ZL3b','IT2a']:continue
 for p in ps:
  words=[w for l in p['lines'] for w in l['words']];ids=[i for l in p['lines'] for i in l['source_ids']]
  for i,w in enumerate(words):
   if w not in ['char','dar','sar']:continue
   sid=ids[i];expected.add(sid);x=actual[sid];assert (x['word'],x['paragraph'])==(w,p['id'])
   lr=(words[i-1] if i else None,words[i+1] if i+1<len(words) else None)
   assert lr==(x['left'],x['right'])
   if None not in lr:
    frames[ed][lr].append((w,sid))
    if lr[0]==lr[1]:sym.add(sid)
assert expected==set(actual)
assert sym=={x['source_id'] for x in r['symmetric']}
expected_frames={(ed,lr,tuple(sorted(items))) for ed,fs in frames.items() for lr,items in fs.items() if len({w for w,i in items})>1}
reported={(x['edition'],(x['left'],x['right']),tuple(sorted((i['word'],i['source_id']) for i in x['occurrences']))) for x in r['shared_frames']}
assert expected_frames==reported
for key,s in r['stats'].items():
 ed,w=key.split('|');rs=[x for x in a if (x['edition'],x['word'])==(ed,w)]
 assert len(rs)==s['occurrences']
 for flag in ['paragraph_initial','paragraph_final','line_final','symmetric']:assert sum(x[flag] for x in rs)==s[flag]
 assert len({x['leaf'] for x in rs})==s['leaves']
print('PASS: complete occurrence coverage, literal neighbors, all symmetric and shared frames; not meanings')
