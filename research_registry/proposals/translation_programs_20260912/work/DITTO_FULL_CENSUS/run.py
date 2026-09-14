import hashlib,json,itertools
from collections import Counter,defaultdict
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[4]
P=Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json')
corpus=json.loads((R/P).read_text());rows=[];stats={};shared=[]
for ed in ['ZL3b','IT2a']:
 for p in corpus[ed]:
  flat=[(line,j,w) for line in p['lines'] for j,w in enumerate(line['words'])]
  for k,(l,j,w) in enumerate(flat):
   if w not in ['char','dar','sar']:continue
   left=flat[k-1][2] if k else None;right=flat[k+1][2] if k+1<len(flat) else None
   rows.append(dict(edition=ed,paragraph=p['id'],page=p['page'],leaf=p['leaf'],locus=l['locus'],source_id=l['source_ids'][j],word=w,position=j+1,line_words=l['words'],line_anchor_eligible=l['anchor_eligible'],left=left,right=right,left_locus=flat[k-1][0]['locus'] if k else None,right_locus=flat[k+1][0]['locus'] if k+1<len(flat) else None,paragraph_initial=k==0,paragraph_final=k==len(flat)-1,line_final=j==len(l['words'])-1,symmetric=left is not None and right is not None and left==right))
 for w in ['char','dar','sar']:
  a=[r for r in rows if r['edition']==ed and r['word']==w]
  stats[ed+'|'+w]=dict(occurrences=len(a),leaves=len({r['leaf'] for r in a}),paragraph_initial=sum(r['paragraph_initial'] for r in a),paragraph_final=sum(r['paragraph_final'] for r in a),line_final=sum(r['line_final'] for r in a),two_neighbors=sum(r['left'] is not None and r['right'] is not None for r in a),symmetric=sum(r['symmetric'] for r in a))
 frames=defaultdict(list)
 for r in rows:
  if r['edition']==ed and r['left'] is not None and r['right'] is not None:frames[(r['left'],r['right'])].append(r)
 for (l,r),a in sorted(frames.items()):
  if len({x['word'] for x in a})>1:shared.append(dict(edition=ed,left=l,right=r,occurrences=[{k:x[k] for k in ['word','source_id','paragraph']} for x in a]))
result=dict(status='DESCRIPTIVE_ONLY',stats=stats,symmetric=[r for r in rows if r['symmetric']],shared_frames=shared,source=str(P),sha256=hashlib.sha256((R/P).read_bytes()).hexdigest(),decision_sha256=hashlib.sha256((B/'DECISION.md').read_bytes()).hexdigest(),meanings=0,independent_confirmation=False)
(B/'OCCURRENCES.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':'))+'\n')
(B/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
