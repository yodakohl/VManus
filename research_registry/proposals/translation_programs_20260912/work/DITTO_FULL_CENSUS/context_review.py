"""Retrospective whole-paragraph follow-through; does not infer action counts."""
import hashlib,json
from pathlib import Path
b=Path(__file__).resolve().parent;root=b.parents[4]
prior=json.loads((b/'RESULT.json').read_text());raw=(root/prior['source']).read_bytes()
assert hashlib.sha256(raw).hexdigest()==prior['sha256']
c=json.loads(raw);rows=[];packets={}
cases=[('f23r.7','dar','qokchol'),('f52r.4','dar','oty'),('f77v.22','dar','qokal'),('f82r.19','char','okain'),('f113v.32','char','qokain'),('f78r.18','dar','qokain')]
for ed in ['ZL3b','IT2a']:
 for loc,marker,x in cases:
  ps=[p for p in c[ed] if any(l['locus']==loc for l in p['lines'])];assert len(ps)==1;p=ps[0]
  packets[ed+'|'+p['id']]={'edition':ed,**p}
  flat=[{'locus':l['locus'],'word':w,'source_id':l['source_ids'][j]} for l in p['lines'] for j,w in enumerate(l['words'])]
  ids=[i for i,v in enumerate(flat) if v['locus']==loc and v['word']==marker];assert len(ids)==1;i=ids[0]
  rows.append(dict(edition=ed,locus=loc,marker=marker,x=x,paragraph=p['id'],groups=len(flat),left=flat[i-1],right=flat[i+1],earlier_x=[v for v in flat[:i-1] if v['word']==x],later_x=[v for v in flat[i+2:] if v['word']==x],following_groups=len(flat)-i-2))
out={'kind':'retrospective_context_review','source':prior['source'],'source_sha256':prior['sha256'],'cases':rows,'paragraphs':list(packets.values()),'independent_semantic_confirmation':False,'meaning_assignments':0}
(b/'CONTEXT_REVIEW.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
for r in rows:print(r['edition'],r['locus'],r['groups'],len(r['earlier_x']),len(r['later_x']),r['following_groups'])
