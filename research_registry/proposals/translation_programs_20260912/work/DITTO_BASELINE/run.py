import hashlib,json
from pathlib import Path
from collections import Counter
b=Path(__file__).resolve().parent;root=b.parents[4]
p=Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json');raw=(root/p).read_bytes();c=json.loads(raw);rows=[];summaries={}
for ed in ['ZL3b','IT2a']:
 for para in c[ed]:
  a=[(w,l['locus'],l['source_ids'][j]) for l in para['lines'] for j,w in enumerate(l['words'])];counts=Counter(v[0] for v in a)
  for i in range(len(a)-2):
   x,m,y=a[i][0],a[i+1][0],a[i+2][0]
   if x!=y or x==m:continue
   rows.append(dict(edition=ed,paragraph=para['id'],leaf=para['leaf'],x=x,middle=m,start_id=a[i][2],middle_id=a[i+1][2],end_id=a[i+2][2],loci=[a[j][1] for j in range(i,i+3)],x_total=counts[x],later_x=sum(v[0]==x for v in a[i+3:]),terminal=not any(v[0]==x for v in a[i+3:]),remaining_groups=len(a)-i-3))
 rs=[r for r in rows if r['edition']==ed];tps={r['paragraph'] for r in rs if r['middle'] in ['char','dar','sar']}
 groups={w:[r for r in rs if r['middle']==w] for w in ['char','dar','sar']}
 groups['other']=[r for r in rs if r['middle'] not in ['char','dar','sar']]
 groups['other_in_target_paragraphs']=[r for r in groups['other'] if r['paragraph'] in tps]
 summaries[ed]={}
 for name,rr in groups.items():
  summaries[ed][name]={s:dict(n=len(ss),terminal=sum(r['terminal'] for r in ss),paragraphs=len({r['paragraph'] for r in ss})) for s,ss in [('all',rr),('two_x',[r for r in rr if r['x_total']==2]),('more_x',[r for r in rr if r['x_total']>2])]}
result=dict(status='DESCRIPTIVE_BASELINE_NO_SIGNIFICANCE',summaries=summaries,source=str(p),source_sha256=hashlib.sha256(raw).hexdigest(),decision_sha256=hashlib.sha256((b/'DECISION.md').read_bytes()).hexdigest(),independent_confirmation=False,meanings=0)
(b/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');(b/'TRIPLES.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':'))+'\n');print(json.dumps(summaries,indent=2))
