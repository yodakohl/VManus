"""Post-result proof presentation only: existing certificate parents and counts."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
import json,gzip
D=Path(__file__).resolve().parents[1];A=D/'artifacts';S=json.loads((D/'src/SPEC.json').read_text());source=json.loads(gzip.decompress(Path(S['source']).read_bytes()))
out={'purpose':'Post-result presentation; no new selection, fit, independent confirmation or meanings. Counts refer only to the immutable strict-interior panel.','created_utc':datetime.now(timezone.utc).isoformat(),'readers':{}}
for reader,rows in source.items():
 C=json.loads(gzip.decompress((A/f'CERTIFICATE_{reader}.json.gz').read_bytes()));N=C['nodes'];s=C['summary'];index={tuple(n['word']):i for i,n in enumerate(N)};by=defaultdict(list)
 for r in rows:by[tuple(r['units'])].append(r)
 def evidence(i):
  needed=set()
  def visit(j):
   if j in needed:return
   for p in N[j]['parents'] or []:visit(p)
   needed.add(j)
  visit(i);steps=[]
  for j in sorted(needed):
   n=N[j];w=tuple(n['word']);p=n['parents'];x={'node':j,'units':list(w),'display':''.join(w),'parents':p}
   if p is None:
    occ=by[w];x.update(panel_count=len(occ),pages=sorted({z['page'] for z in occ}),first_occurrence=occ[0])
   else:x['equation']={'complete_prefix':N[p[0]]['word'],'complete_larger':N[p[1]]['word'],'complete_remainder':n['word']}
   steps.append(x)
  return {'target_node':i,'steps':steps,'smallest_leaf_form_count':min(z['panel_count'] for z in steps if z['parents'] is None)}
 forced={g:evidence(index[(g,)]) for g in s['F']};branches={}
 for g,h in s['heads'].items():
  if h['bound'] is None:continue
  branches[g]={}
  for b in s['second_signs'][g]:
   candidates=[w for w in index if len(w)>1 and w[:2]==(g,b)];w=min(candidates,key=lambda w:(len(w),w));branches[g][b]=evidence(index[w])
 out['readers'][reader]={'forced_singletons':forced,'long_code_head_branches':branches,'selection':'Use retained parent certificate. Choose shortest then lexical quotient for each already determined head/second branch; do not maximize or remove support after seeing rarity.'}
(A/'PROOF_EXAMPLES.json').write_text(json.dumps(out,indent=2)+'\n')
print({r:{'forced_examples':len(v['forced_singletons']),'long_head_examples':{g:len(x) for g,x in v['long_code_head_branches'].items()},'singleton_proofs_using_one_token_form':sum(x['smallest_leaf_form_count']==1 for x in v['forced_singletons'].values())}for r,v in out['readers'].items()})
